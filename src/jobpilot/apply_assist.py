"""Best-effort ATS form prefill that always leaves final submission to a human.

The module intentionally has no click helpers. It fills only known applicant
fields and uploads local documents, then leaves a visible Playwright browser
open for the human to review, submit, or abandon. ATS markup changes often, so
all mapping or Playwright failures safely fall back to the URL in the default
browser instead of interrupting the dashboard.
"""

from __future__ import annotations

import sqlite3
import webbrowser
from collections.abc import Callable
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Literal, Protocol
from urllib.parse import urlparse

from jobpilot.config import Settings, get_settings
from jobpilot.logging_conf import get_logger
from jobpilot.state import log_event

log = get_logger("apply_assist")


class ApplyAssistError(RuntimeError):
    """Raised for an ineligible application or an incomplete assist setup."""


class SelectorError(ApplyAssistError):
    """Raised when an adapter cannot safely map a required field."""


@dataclass(frozen=True)
class ApplicantProfile:
    """The non-secret contact values entered into an ATS form."""

    full_name: str
    email: str
    phone: str
    linkedin_url: str

    @classmethod
    def from_settings(cls, settings: Settings) -> ApplicantProfile:
        values = {
            "APPLICANT_FULL_NAME": settings.applicant_full_name,
            "APPLICANT_EMAIL": settings.applicant_email,
            "APPLICANT_PHONE": settings.applicant_phone,
            "APPLICANT_LINKEDIN_URL": settings.applicant_linkedin_url,
        }
        missing = [name for name, value in values.items() if not value]
        if missing:
            raise ApplyAssistError(
                "ATS prefill needs " + ", ".join(missing) + " in .env"
            )
        return cls(
            full_name=values["APPLICANT_FULL_NAME"] or "",
            email=values["APPLICANT_EMAIL"] or "",
            phone=values["APPLICANT_PHONE"] or "",
            linkedin_url=values["APPLICANT_LINKEDIN_URL"] or "",
        )

    @property
    def first_name(self) -> str:
        return self.full_name.split(maxsplit=1)[0]

    @property
    def last_name(self) -> str:
        parts = self.full_name.split(maxsplit=1)
        return parts[1] if len(parts) > 1 else ""


@dataclass(frozen=True)
class FillAction:
    """One safe text-field fill in a selected ATS form."""

    field: str
    selector: str
    value: str


@dataclass(frozen=True)
class UploadAction:
    """One safe local-file upload; never a form submit action."""

    field: str
    selector: str
    path: Path


@dataclass(frozen=True)
class PrefillPlan:
    """The actions selected from a page's current HTML fixture/markup."""

    fills: tuple[FillAction, ...]
    uploads: tuple[UploadAction, ...]


@dataclass(frozen=True)
class AssistResult:
    """Auditable result of a single manual prefill launch request."""

    outcome: Literal["prefill_launched", "apply_url_opened"]
    adapter: str | None
    fallback_reason: str | None = None


class _Locator(Protocol):
    @property
    def first(self) -> _Locator: ...

    def count(self) -> int: ...

    def fill(self, value: str) -> None: ...

    def set_input_files(self, files: str) -> None: ...


class _Page(Protocol):
    def content(self) -> str: ...

    def locator(self, selector: str) -> _Locator: ...


class BrowserLauncher(Protocol):
    """A launch seam: production opens Playwright, tests supply a stub page."""

    def open_page(self, url: str) -> _Page: ...


_ACTIVE_BROWSERS: list[object] = []


class VisibleBrowserLauncher:
    """Launch Playwright visibly and retain it until the human closes it."""

    def open_page(self, url: str) -> _Page:
        # Imported lazily so fixture tests need neither a browser nor Playwright.
        from playwright.sync_api import sync_playwright

        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
        # Keep the owning objects reachable after this request returns. Closing the
        # visible browser is the human's explicit end to their review session.
        _ACTIVE_BROWSERS.extend((playwright, browser))
        page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        return page


@dataclass(frozen=True)
class _Control:
    tag: str
    attributes: dict[str, str]


class _ControlParser(HTMLParser):
    """Tiny standard-library parser sufficient to test our simple CSS selectors."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.controls: list[_Control] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        if tag not in {"input", "textarea"}:
            return
        attributes = {
            key.lower(): value.lower() if value is not None else ""
            for key, value in attrs
        }
        self.controls.append(_Control(tag=tag.lower(), attributes=attributes))


def _controls_from_html(html: str) -> tuple[_Control, ...]:
    parser = _ControlParser()
    parser.feed(html)
    parser.close()
    return tuple(parser.controls)


def _selector_matches(control: _Control, selector: str) -> bool:
    """Match the deliberately simple tag[attr=value] selectors used below."""

    if "[" not in selector or not selector.endswith("]"):
        return False
    tag, raw_attribute = selector[:-1].split("[", maxsplit=1)
    if control.tag != tag:
        return False
    if "*=" in raw_attribute:
        attribute, value = raw_attribute.split("*=", maxsplit=1)
        actual = control.attributes.get(attribute.lower(), "")
        return value.strip("'\"").lower() in actual
    if "=" not in raw_attribute:
        return False
    attribute, value = raw_attribute.split("=", maxsplit=1)
    return control.attributes.get(attribute.lower()) == value.strip("'\"").lower()


def _first_matching_selector(
    controls: tuple[_Control, ...],
    selectors: tuple[str, ...],
) -> str | None:
    return next(
        (
            selector
            for selector in selectors
            if any(_selector_matches(control, selector) for control in controls)
        ),
        None,
    )


class ApplyAdapter(Protocol):
    """Common adapter interface for a best-effort ATS prefill."""

    name: str

    def matches(self, url: str) -> bool: ...

    def build_plan(
        self,
        html: str,
        applicant: ApplicantProfile,
        cv_path: Path,
        letter_path: Path | None,
    ) -> PrefillPlan: ...

    def apply_plan(self, page: _Page, plan: PrefillPlan) -> None: ...


class _BaseAdapter:
    """Shared plan building and non-submitting form interaction."""

    name = "base"
    name_fields: tuple[tuple[str, tuple[str, ...], str], ...] = ()
    email_selectors: tuple[str, ...] = ()
    phone_selectors: tuple[str, ...] = ()
    linkedin_selectors: tuple[str, ...] = ()
    cv_selectors: tuple[str, ...] = ()
    letter_selectors: tuple[str, ...] = ()

    def matches(self, url: str) -> bool:
        return False

    def build_plan(
        self,
        html: str,
        applicant: ApplicantProfile,
        cv_path: Path,
        letter_path: Path | None,
    ) -> PrefillPlan:
        controls = _controls_from_html(html)
        fills = self._fill_actions(controls, applicant)
        cv_selector = _first_matching_selector(controls, self.cv_selectors)
        if cv_selector is None:
            raise SelectorError(f"{self.name}: CV upload selector not found")

        uploads = [UploadAction("cv", cv_selector, cv_path)]
        if letter_path is not None:
            letter_selector = _first_matching_selector(controls, self.letter_selectors)
            if letter_selector is not None:
                uploads.append(UploadAction("letter", letter_selector, letter_path))
        return PrefillPlan(fills=tuple(fills), uploads=tuple(uploads))

    def _fill_actions(
        self,
        controls: tuple[_Control, ...],
        applicant: ApplicantProfile,
    ) -> list[FillAction]:
        fills: list[FillAction] = []
        for field, selectors, profile_attribute in self.name_fields:
            selector = _first_matching_selector(controls, selectors)
            if selector is not None:
                fills.append(FillAction(field, selector, getattr(applicant, profile_attribute)))
        if not fills:
            raise SelectorError(f"{self.name}: name selector not found")

        email_selector = _first_matching_selector(controls, self.email_selectors)
        if email_selector is None:
            raise SelectorError(f"{self.name}: email selector not found")
        fills.append(FillAction("email", email_selector, applicant.email))

        for field, selectors, value in (
            ("phone", self.phone_selectors, applicant.phone),
            ("linkedin", self.linkedin_selectors, applicant.linkedin_url),
        ):
            selector = _first_matching_selector(controls, selectors)
            if selector is not None:
                fills.append(FillAction(field, selector, value))
        return fills

    def apply_plan(self, page: _Page, plan: PrefillPlan) -> None:
        for action in plan.fills:
            locator = page.locator(action.selector)
            if locator.count() == 0:
                raise SelectorError(f"{self.name}: {action.field} field disappeared")
            locator.first.fill(action.value)
        for action in plan.uploads:
            locator = page.locator(action.selector)
            if locator.count() == 0:
                raise SelectorError(f"{self.name}: {action.field} upload disappeared")
            locator.first.set_input_files(str(action.path))
        # Deliberately no submit, apply, send, CAPTCHA, password, or account action.


class LeverAdapter(_BaseAdapter):
    name = "lever"

    # BEST-EFFORT SELECTORS: Lever's public form markup changes over time. A
    # missing/failed selector is intentionally handled by the browser fallback.
    name_fields = (("name", ("input[name='name']", "input[name='full_name']"), "full_name"),)
    email_selectors = ("input[name='email']", "input[type='email']")
    phone_selectors = ("input[name='phone']", "input[type='tel']")
    linkedin_selectors = (
        "input[name*='linkedin']",
        "input[name*='linkedin_url']",
    )
    cv_selectors = (
        "input[name*='resume']",
        "input[name*='cv']",
        "input[type='file']",
    )
    letter_selectors = ("input[name*='cover']", "input[name*='letter']")

    def matches(self, url: str) -> bool:
        return "lever.co" in (urlparse(url).hostname or "").lower()


class GreenhouseAdapter(_BaseAdapter):
    name = "greenhouse"

    # BEST-EFFORT SELECTORS: Greenhouse boards expose several form versions.
    # Any selector rot or fill error opens the ordinary application URL instead.
    name_fields = (
        ("first_name", ("input[id='first_name']", "input[name='first_name']"), "first_name"),
        ("last_name", ("input[id='last_name']", "input[name='last_name']"), "last_name"),
        ("name", ("input[name='name']", "input[name='full_name']"), "full_name"),
    )
    email_selectors = ("input[id='email']", "input[name='email']", "input[type='email']")
    phone_selectors = ("input[id='phone']", "input[name='phone']", "input[type='tel']")
    linkedin_selectors = ("input[name*='linkedin']", "input[id*='linkedin']")
    cv_selectors = (
        "input[id='resume']",
        "input[name*='resume']",
        "input[type='file']",
    )
    letter_selectors = ("input[id*='cover']", "input[name*='cover']")

    def matches(self, url: str) -> bool:
        return "greenhouse.io" in (urlparse(url).hostname or "").lower()


class SmartRecruitersAdapter(_BaseAdapter):
    name = "smartrecruiters"

    # BEST-EFFORT SELECTORS: SmartRecruiters changes generated field names
    # regularly. Failure always falls back; this adapter never submits a form.
    name_fields = (
        ("first_name", ("input[name='firstName']", "input[name='first_name']"), "first_name"),
        ("last_name", ("input[name='lastName']", "input[name='last_name']"), "last_name"),
        ("name", ("input[name='name']", "input[name='full_name']"), "full_name"),
    )
    email_selectors = ("input[name='email']", "input[type='email']")
    phone_selectors = ("input[name='phone']", "input[name='phoneNumber']", "input[type='tel']")
    linkedin_selectors = ("input[name*='linkedin']", "input[id*='linkedin']")
    cv_selectors = (
        "input[name*='resume']",
        "input[name*='cv']",
        "input[type='file']",
    )
    letter_selectors = ("input[name*='cover']", "input[name*='letter']")

    def matches(self, url: str) -> bool:
        return "smartrecruiters.com" in (urlparse(url).hostname or "").lower()


ADAPTERS: tuple[ApplyAdapter, ...] = (
    LeverAdapter(),
    GreenhouseAdapter(),
    SmartRecruitersAdapter(),
)


def adapter_for_url(url: str) -> ApplyAdapter | None:
    """Return the owning ATS adapter, if the saved offer URL is recognized."""

    return next((adapter for adapter in ADAPTERS if adapter.matches(url)), None)


def _application_for_assist(
    db: sqlite3.Connection,
    application_id: int,
) -> sqlite3.Row:
    row = db.execute(
        "SELECT a.status, a.cv_pdf_path, a.letter_pdf_path, o.url, s.name AS source "
        "FROM applications a "
        "JOIN offers o ON o.id = a.offer_id "
        "JOIN sources s ON s.id = o.source_id "
        "WHERE a.id = ?",
        (application_id,),
    ).fetchone()
    if row is None:
        raise ApplyAssistError(f"no application with id={application_id}")
    if row["status"] != "ready":
        raise ApplyAssistError("application must be in 'ready' state for ATS prefill")
    if row["source"] != "ats" or not row["url"]:
        raise ApplyAssistError("application is not an ATS offer with an apply URL")
    return row


def _fallback(
    db: sqlite3.Connection,
    application_id: int,
    url: str,
    *,
    reason: str,
    opener: Callable[[str], bool] = webbrowser.open,
) -> AssistResult:
    """Attempt the ordinary browser URL and record the safe degradation."""

    opened = False
    try:
        opened = bool(opener(url))
    except Exception as exc:  # browser integration is platform-owned and optional
        log.warning("default browser fallback failed for application %d: %s", application_id, exc)
    log_event(
        db,
        application_id,
        "apply_url_opened",
        {"reason": reason, "opened": opened},
    )
    return AssistResult("apply_url_opened", adapter=None, fallback_reason=reason)


def launch_application_assist(
    db: sqlite3.Connection,
    application_id: int,
    *,
    output_root: Path | None = None,
    settings: Settings | None = None,
    launcher: BrowserLauncher | None = None,
    opener: Callable[[str], bool] = webbrowser.open,
) -> AssistResult:
    """Open and prefill an ATS form, never submitting it on the user's behalf."""

    row = _application_for_assist(db, application_id)
    url = str(row["url"])
    adapter = adapter_for_url(url)
    if adapter is None:
        return _fallback(db, application_id, url, reason="unknown_ats", opener=opener)

    configured = settings or get_settings()
    # Missing applicant configuration is an actionable setup issue, not an ATS
    # adapter failure. Surface it to the local dashboard rather than pretending
    # an unfilled browser page is a successful degradation.
    applicant = ApplicantProfile.from_settings(configured)
    try:
        root = Path(output_root or configured.output_dir)
        cv_path = Path(row["cv_pdf_path"] or root / str(application_id) / "cv.pdf")
        if not cv_path.is_file():
            raise ApplyAssistError("generated cv.pdf is unavailable")
        stored_letter = row["letter_pdf_path"]
        letter_path = (
            Path(stored_letter)
            if stored_letter
            else root / str(application_id) / "motivation_letter.pdf"
        )
        if not letter_path.is_file():
            letter_path = None

        page = (launcher or VisibleBrowserLauncher()).open_page(url)
        plan = adapter.build_plan(page.content(), applicant, cv_path, letter_path)
        adapter.apply_plan(page, plan)
    except Exception as exc:  # any adapter/browser failure must degrade safely
        log.warning(
            "ATS prefill failed for application %d via %s: %s",
            application_id,
            adapter.name,
            exc,
        )
        return _fallback(
            db,
            application_id,
            url,
            reason=f"{adapter.name}_prefill_failed",
            opener=opener,
        )

    log_event(db, application_id, "prefill_launched", {"adapter": adapter.name})
    return AssistResult("prefill_launched", adapter=adapter.name)
