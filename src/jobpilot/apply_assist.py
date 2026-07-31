"""Best-effort ATS prefill and human-approved WTTJ inline applications.

The generic ATS path intentionally has no click helpers: it fills known fields,
uploads local documents, and leaves submission to the human. WTTJ is the one
explicit exception. Its adapter may click the submit control only after a fresh
dashboard approval, pre-submit assertions, and the disabled-by-default
``WTTJ_AUTO_SUBMIT_ENABLED`` gate. Any blocker leaves state unchanged and opens
the ordinary offer URL for the human.
"""

from __future__ import annotations

import re
import sqlite3
import webbrowser
from collections.abc import Callable
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Literal, Protocol
from urllib.parse import urlparse

from jobpilot.clipboard import copy_text
from jobpilot.config import Settings, get_settings
from jobpilot.logging_conf import get_logger
from jobpilot.state import log_event, transition

log = get_logger("apply_assist")


class ApplyAssistError(RuntimeError):
    """Raised for an ineligible application or an incomplete assist setup."""


class SelectorError(ApplyAssistError):
    """Raised when an adapter cannot safely map a required field."""


class WTTJApplyError(ApplyAssistError):
    """Raised when a WTTJ application is missing or not eligible."""


class WTTJApplyBlocked(WTTJApplyError):
    """A safe, auditable pre-submit abort with a stable machine reason."""

    def __init__(self, reason: str, message: str) -> None:
        super().__init__(message)
        self.reason = reason


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
    scope: str | None = None


@dataclass(frozen=True)
class AssistResult:
    """Auditable result of a single manual prefill launch request."""

    outcome: Literal["prefill_launched", "apply_url_opened"]
    adapter: str | None
    fallback_reason: str | None = None


@dataclass(frozen=True)
class WTTJApplyResult:
    """Auditable outcome of one approved WTTJ dashboard action."""

    outcome: Literal[
        "apply_dry_run",
        "application_submitted",
        "apply_blocked",
        "submit_unconfirmed",
    ]
    screenshot_path: Path | None = None
    reason: str | None = None


@dataclass(frozen=True)
class _ConfirmationBaseline:
    url: str
    visible_selectors: frozenset[str]


class _Locator(Protocol):
    @property
    def first(self) -> _Locator: ...

    def count(self) -> int: ...

    def is_visible(self) -> bool: ...

    def fill(self, value: str) -> None: ...

    def set_input_files(self, files: str) -> None: ...

    def click(self) -> None: ...


class _Page(Protocol):
    url: str

    def content(self) -> str: ...

    def locator(self, selector: str) -> _Locator: ...

    def screenshot(self, *, path: str, full_page: bool) -> None: ...

    def wait_for_timeout(self, timeout: float) -> None: ...


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
        if tag not in {"input", "select", "textarea"}:
            return
        attributes = {
            key.lower(): value if value is not None else ""
            for key, value in attrs
        }
        self.controls.append(_Control(tag=tag.lower(), attributes=attributes))


def _controls_from_html(html: str) -> tuple[_Control, ...]:
    parser = _ControlParser()
    parser.feed(html)
    parser.close()
    return tuple(parser.controls)


@dataclass(frozen=True)
class _Form:
    attributes: dict[str, str]
    controls: tuple[_Control, ...]


class _FormParser(HTMLParser):
    """Collect controls by form so automation never targets the wrong form."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.forms: list[_Form] = []
        self._attributes: dict[str, str] | None = None
        self._controls: list[_Control] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        tag = tag.casefold()
        attributes = {
            key.casefold(): value if value is not None else ""
            for key, value in attrs
        }
        if tag == "form":
            if self._attributes is None:
                self._attributes = attributes
                self._controls = []
            return
        if self._attributes is not None and tag in {"input", "select", "textarea"}:
            self._controls.append(_Control(tag=tag, attributes=attributes))

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() != "form" or self._attributes is None:
            return
        self.forms.append(_Form(self._attributes, tuple(self._controls)))
        self._attributes = None
        self._controls = []


def _forms_from_html(html: str) -> tuple[_Form, ...]:
    parser = _FormParser()
    parser.feed(html)
    parser.close()
    return tuple(parser.forms)


def _selector_matches(control: _Control, selector: str) -> bool:
    """Match the deliberately simple tag[attr=value] selectors used below."""

    if "[" not in selector or not selector.endswith("]"):
        return False
    tag, raw_attribute = selector[:-1].split("[", maxsplit=1)
    if control.tag != tag:
        return False
    if "*=" in raw_attribute:
        attribute, value = raw_attribute.split("*=", maxsplit=1)
        actual = control.attributes.get(attribute.lower(), "").lower()
        return value.strip("'\"").lower() in actual
    if "=" not in raw_attribute:
        return False
    attribute, value = raw_attribute.split("=", maxsplit=1)
    actual = control.attributes.get(attribute.lower(), "").lower()
    return actual == value.strip("'\"").lower()


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


def _css_attribute_value(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _scoped_selector(scope: str | None, selector: str) -> str:
    return f"{scope} {selector}" if scope else selector


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
        return self._build_plan(
            _controls_from_html(html), applicant, cv_path, letter_path
        )

    def _build_plan(
        self,
        controls: tuple[_Control, ...],
        applicant: ApplicantProfile,
        cv_path: Path,
        letter_path: Path | None,
    ) -> PrefillPlan:
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
            selector = _scoped_selector(plan.scope, action.selector)
            locator = page.locator(selector)
            if locator.count() == 0:
                raise SelectorError(f"{self.name}: {action.field} field disappeared")
            locator.first.fill(action.value)
        for action in plan.uploads:
            selector = _scoped_selector(plan.scope, action.selector)
            locator = page.locator(selector)
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


_TITLE_RE = re.compile(
    r"<[^>]*data-testid=[\"']job-title[\"'][^>]*>(.*?)</[^>]+>",
    re.IGNORECASE | re.DOTALL,
)
_TAG_RE = re.compile(r"<[^>]+>")


def _identity(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", unescape(value).casefold()))


def _page_offer_identity(html: str) -> tuple[str, str]:
    controls = _controls_from_html(html)
    offer_control = next(
        (
            control
            for control in controls
            if control.attributes.get("name", "").casefold() == "offer_id"
        ),
        None,
    )
    offer_id = offer_control.attributes.get("value", "") if offer_control else ""
    if not offer_id:
        match = re.search(r"data-offer-id=[\"']([^\"']+)", html, re.IGNORECASE)
        offer_id = match.group(1) if match else ""
    title_match = _TITLE_RE.search(html)
    title = (
        unescape(_TAG_RE.sub("", title_match.group(1))).strip()
        if title_match
        else ""
    )
    return offer_id.strip(), title


def _wttj_application_form(
    html: str,
    cv_selectors: tuple[str, ...],
) -> tuple[_Form, str, str, bool]:
    forms_with_cv: list[tuple[_Form, str, str]] = []
    for form in _forms_from_html(html):
        cv_selector = _first_matching_selector(form.controls, cv_selectors)
        if cv_selector is None:
            continue
        offer_control = next(
            (
                control
                for control in form.controls
                if control.attributes.get("name", "").casefold() == "offer_id"
            ),
            None,
        )
        offer_id = offer_control.attributes.get("value", "").strip() if offer_control else ""
        forms_with_cv.append((form, offer_id, cv_selector))

    identified = [candidate for candidate in forms_with_cv if candidate[1]]
    if len(identified) == 1:
        form, offer_id, cv_selector = identified[0]
        return form, offer_id, cv_selector, True
    if not identified and len(forms_with_cv) == 1:
        form, _, cv_selector = forms_with_cv[0]
        page_offer_id, _ = _page_offer_identity(html)
        if page_offer_id:
            return form, page_offer_id, cv_selector, False
    raise WTTJApplyBlocked(
        "application_form_ambiguous",
        "exactly one WTTJ application form must be identifiable",
    )


class WTTJAdapter(_BaseAdapter):
    """WTTJ inline form adapter with explicit pre-submit assertions."""

    name = "wttj"
    name_fields = (
        ("first_name", ("input[name='first_name']",), "first_name"),
        ("last_name", ("input[name='last_name']",), "last_name"),
        (
            "name",
            ("input[name='full_name']", "input[name='name']"),
            "full_name",
        ),
    )
    email_selectors = (
        "input[name='email']",
        "input[name='candidate_email']",
        "input[type='email']",
    )
    phone_selectors = (
        "input[name='phone']",
        "input[name='candidate_phone']",
        "input[name='phone_number']",
        "input[type='tel']",
    )
    linkedin_selectors = (
        "input[name*='linkedin']",
        "input[id*='linkedin']",
    )
    cv_selectors = (
        "input[name*='resume']",
        "input[name='cv']",
        "input[id='cv']",
    )
    letter_selectors = (
        "input[name*='cover_letter']",
        "input[name*='motivation_letter']",
        "input[name*='letter']",
    )
    submit_selectors = (
        "button[data-testid='submit-application']",
        "button.submit-application",
        "button[type='submit']",
        "input[type='submit']",
    )
    confirmation_selectors = (
        "[data-testid='application-success']",
        ".application-success",
        "[data-status='submitted']",
    )

    def matches(self, url: str) -> bool:
        hostname = (urlparse(url).hostname or "").casefold()
        return hostname == "welcometothejungle.com" or hostname.endswith(
            ".welcometothejungle.com"
        )

    def build_plan(
        self,
        html: str,
        applicant: ApplicantProfile,
        cv_path: Path,
        letter_path: Path | None,
    ) -> PrefillPlan:
        form, offer_id, cv_selector, has_offer_control = _wttj_application_form(
            html, self.cv_selectors
        )
        letter_selector = _first_matching_selector(
            form.controls, self.letter_selectors
        )
        if letter_selector is not None and letter_path is None:
            raise WTTJApplyBlocked(
                "missing_letter",
                "motivation_letter.pdf is required because the WTTJ form has a letter field",
            )
        plan = self._build_plan(form.controls, applicant, cv_path, letter_path)
        scope = (
            "form:has(input[name='offer_id'][value="
            f"{_css_attribute_value(offer_id)}])"
            if has_offer_control
            else f"form:has({cv_selector})"
        )
        return PrefillPlan(plan.fills, plan.uploads, scope=scope)

    def validate_pre_submit(
        self,
        html: str,
        plan: PrefillPlan,
        *,
        expected_external_id: str,
        expected_title: str,
    ) -> None:
        normalized_html = html.casefold()
        if any(
            marker in normalized_html
            for marker in (
                "captcha",
                "g-recaptcha",
                "hcaptcha",
                "data-sitekey",
                "cloudflare challenge",
                "are you human",
            )
        ):
            raise WTTJApplyBlocked("captcha_detected", "CAPTCHA or bot check detected")
        form, offer_id, _, _ = _wttj_application_form(html, self.cv_selectors)
        controls = form.controls
        if any(
            control.attributes.get("type", "").casefold() == "password"
            for control in controls
        ):
            raise WTTJApplyBlocked("password_detected", "password field detected")
        account_markers = (
            "create_account",
            "create-account",
            "create account",
            "créer un compte",
            "creer un compte",
            "account required",
            "sign up",
            "inscription obligatoire",
        )
        if any(marker in normalized_html for marker in account_markers):
            raise WTTJApplyBlocked("account_required", "account creation is required")

        _, title = _page_offer_identity(html)
        if (
            not offer_id
            or not title
            or offer_id != expected_external_id
            or _identity(title) != _identity(expected_title)
        ):
            raise WTTJApplyBlocked(
                "offer_mismatch",
                "the WTTJ page does not match the selected application",
            )

        mapped_fills = tuple(plan.fills)
        mapped_uploads = tuple(plan.uploads)
        for control in controls:
            if "required" not in control.attributes:
                continue
            control_type = control.attributes.get("type", "text").casefold()
            if control_type == "hidden":
                if not control.attributes.get("value", "").strip():
                    raise WTTJApplyBlocked(
                        "required_field_unmapped", "a required hidden field is empty"
                    )
                continue
            if control_type in {"checkbox", "radio"}:
                if "checked" not in control.attributes:
                    raise WTTJApplyBlocked(
                        "required_field_unmapped",
                        "a required choice needs manual review",
                    )
                continue
            if control_type == "file":
                mapped = next(
                    (
                        action
                        for action in mapped_uploads
                        if _selector_matches(control, action.selector)
                    ),
                    None,
                )
                valid = (
                    mapped is not None
                    and mapped.path.is_file()
                    and mapped.path.stat().st_size > 0
                )
            else:
                mapped = next(
                    (
                        action
                        for action in mapped_fills
                        if _selector_matches(control, action.selector)
                    ),
                    None,
                )
                valid = mapped is not None and bool(mapped.value.strip())
            if not valid:
                field = control.attributes.get("name", control.tag)
                raise WTTJApplyBlocked(
                    "required_field_unmapped",
                    f"required WTTJ field is not safely mapped: {field}",
                )

    def _assert_scope_unique(self, page: _Page, plan: PrefillPlan) -> None:
        if plan.scope is None or page.locator(plan.scope).count() != 1:
            raise WTTJApplyBlocked(
                "application_form_changed",
                "the identified WTTJ application form changed before submission",
            )

    def apply_plan(self, page: _Page, plan: PrefillPlan) -> None:
        self._assert_scope_unique(page, plan)
        super().apply_plan(page, plan)

    def submit(self, page: _Page, plan: PrefillPlan) -> None:
        self._assert_scope_unique(page, plan)
        for selector in self.submit_selectors:
            scoped = _scoped_selector(plan.scope, selector)
            locator = page.locator(scoped)
            if locator.count() == 1:
                locator.first.click()
                return
        raise WTTJApplyBlocked("submit_missing", "WTTJ submit control not found")

    def confirmation_baseline(self, page: _Page) -> _ConfirmationBaseline:
        visible = frozenset(
            selector
            for selector in self.confirmation_selectors
            if page.locator(selector).count()
            and page.locator(selector).first.is_visible()
        )
        return _ConfirmationBaseline(url=page.url, visible_selectors=visible)

    def _confirmation_present(
        self,
        page: _Page,
        baseline: _ConfirmationBaseline,
    ) -> bool:
        path_segments = {
            segment
            for segment in urlparse(page.url).path.casefold().split("/")
            if segment
        }
        if page.url != baseline.url and path_segments.intersection(
            {"confirmation", "confirmed", "merci", "application-success"}
        ):
            return True
        for selector in self.confirmation_selectors:
            locator = page.locator(selector)
            if (
                selector not in baseline.visible_selectors
                and locator.count()
                and locator.first.is_visible()
            ):
                return True
        return False

    def submission_confirmed(
        self,
        page: _Page,
        baseline: _ConfirmationBaseline,
        *,
        timeout_ms: int = 5_000,
    ) -> bool:
        poll_ms = 100
        attempts = max(1, timeout_ms // poll_ms)
        for attempt in range(attempts + 1):
            if self._confirmation_present(page, baseline):
                return True
            if attempt < attempts:
                page.wait_for_timeout(poll_ms)
        return False


ADAPTERS: tuple[ApplyAdapter, ...] = (
    LeverAdapter(),
    GreenhouseAdapter(),
    SmartRecruitersAdapter(),
    WTTJAdapter(),
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


def _application_for_wttj(
    db: sqlite3.Connection,
    application_id: int,
) -> sqlite3.Row:
    row = db.execute(
        "SELECT a.status, o.external_id, o.url, o.title, s.name AS source, "
        "(SELECT e.event FROM events e WHERE e.application_id = a.id "
        " ORDER BY e.id DESC LIMIT 1) AS latest_event "
        "FROM applications a "
        "JOIN offers o ON o.id = a.offer_id "
        "JOIN sources s ON s.id = o.source_id "
        "WHERE a.id = ?",
        (application_id,),
    ).fetchone()
    if row is None:
        raise WTTJApplyError(f"no application with id={application_id}")
    if row["status"] != "ready":
        raise WTTJApplyError("application must be in 'ready' state for WTTJ apply")
    if row["source"] != "wttj" or not row["url"]:
        raise WTTJApplyError("application is not an eligible WTTJ offer")
    if row["latest_event"] == "submit_unconfirmed":
        raise WTTJApplyError(
            "previous WTTJ submission is unconfirmed; verify it manually before retrying"
        )
    return row


def _open_for_human(
    application_id: int,
    url: str,
    opener: Callable[[str], bool],
) -> bool:
    try:
        return bool(opener(url))
    except Exception as exc:  # platform-owned browser integration
        log.warning(
            "WTTJ browser fallback failed for application %d: %s",
            application_id,
            exc,
        )
        return False


def launch_wttj_application(
    db: sqlite3.Connection,
    application_id: int,
    *,
    output_root: Path | None = None,
    settings: Settings | None = None,
    launcher: BrowserLauncher | None = None,
    opener: Callable[[str], bool] = webbrowser.open,
    via: str = "dashboard",
) -> WTTJApplyResult:
    """Fill a WTTJ inline form and submit only behind the explicit live gate."""

    row = _application_for_wttj(db, application_id)
    configured = settings or get_settings()
    live = configured.wttj_auto_submit_enabled
    mode = "live" if live else "dry-run"
    url = str(row["url"])
    log_event(
        db,
        application_id,
        "human_approved",
        {"via": via, "action": "wttj_apply", "mode": mode},
    )
    try:
        applicant = ApplicantProfile.from_settings(configured)
        application_dir = Path(output_root or configured.output_dir) / str(application_id)
        application_dir.mkdir(parents=True, exist_ok=True)
        cv_path = application_dir / "cv.pdf"
        if not cv_path.is_file() or cv_path.stat().st_size == 0:
            raise WTTJApplyBlocked("missing_cv", "generated cv.pdf is missing or empty")
        letter_path = application_dir / "motivation_letter.pdf"
        if not letter_path.is_file() or letter_path.stat().st_size == 0:
            letter_path = None

        adapter = WTTJAdapter()
        page = (launcher or VisibleBrowserLauncher()).open_page(url)
        html = page.content()
        plan = adapter.build_plan(html, applicant, cv_path, letter_path)
        adapter.validate_pre_submit(
            html,
            plan,
            expected_external_id=str(row["external_id"] or ""),
            expected_title=str(row["title"] or ""),
        )
        adapter.apply_plan(page, plan)
        screenshot_path = application_dir / "wttj_apply.png"
        page.screenshot(path=str(screenshot_path), full_page=True)

        if not live:
            log_event(
                db,
                application_id,
                "apply_dry_run",
                {"via": via, "screenshot": str(screenshot_path)},
            )
            return WTTJApplyResult(
                "apply_dry_run", screenshot_path=screenshot_path
            )

        confirmation_baseline = adapter.confirmation_baseline(page)
        adapter.submit(page, plan)
        if not adapter.submission_confirmed(page, confirmation_baseline):
            log_event(
                db,
                application_id,
                "submit_unconfirmed",
                {"via": via, "screenshot": str(screenshot_path)},
            )
            return WTTJApplyResult(
                "submit_unconfirmed",
                screenshot_path=screenshot_path,
                reason="submission confirmation was not detected",
            )

        log_event(
            db,
            application_id,
            "application_submitted",
            {"via": via, "adapter": adapter.name, "screenshot": str(screenshot_path)},
        )
        transition(
            db,
            application_id,
            "applied",
            detail={"via": via, "adapter": adapter.name},
        )
        return WTTJApplyResult(
            "application_submitted", screenshot_path=screenshot_path
        )
    except WTTJApplyBlocked as exc:
        opened = _open_for_human(application_id, url, opener)
        log_event(
            db,
            application_id,
            "apply_blocked",
            {"via": via, "reason": exc.reason, "opened": opened},
        )
        return WTTJApplyResult("apply_blocked", reason=exc.reason)
    except Exception as exc:
        detail = configured.redact(str(exc))
        log.warning("WTTJ apply failed for application %d: %s", application_id, detail)
        opened = _open_for_human(application_id, url, opener)
        log_event(
            db,
            application_id,
            "apply_blocked",
            {"via": via, "reason": "automation_error", "opened": opened},
        )
        return WTTJApplyResult("apply_blocked", reason="automation_error")


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


class _TextParser(HTMLParser):
    """Strip a generated letter's markup down to what a human would paste."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self._parts.append(data)

    def handle_startendtag(self, tag: str, attrs: object) -> None:
        if tag == "br":
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"p", "div", "li", "br"}:
            self._parts.append("\n\n")

    @property
    def text(self) -> str:
        joined = "".join(self._parts)
        lines = [line.strip() for line in joined.splitlines()]
        return "\n".join(line for line in lines if line).strip()


def letter_plain_text(output_root: Path, application_id: int) -> str:
    """The generated letter as plain text, or '' when it was never generated."""

    path = Path(output_root) / str(application_id) / "letter_body.html"
    if not path.is_file():
        return ""
    parser = _TextParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser.text


def open_manually(
    db: sqlite3.Connection,
    application_id: int,
    url: str | None,
    *,
    output_root: Path | None = None,
    settings: Settings | None = None,
    opener: Callable[[str], bool] = webbrowser.open,
    copier: Callable[[str], bool] = copy_text,
    via: str = "dashboard",
) -> tuple[bool, bool]:
    """The manual_open route: open the offer, copy the letter, submit nothing.

    A legitimate terminal route rather than a degradation, so it records what it
    managed to do — a browser that would not open and a clipboard that would not
    take the letter are both things the human needs told, not hidden.
    """

    configured = settings or get_settings()
    opened = False
    if url:
        try:
            opened = bool(opener(url))
        except Exception as exc:  # browser integration is platform-owned
            log.warning(
                "manual open failed for application %d: %s", application_id, exc
            )
    letter = letter_plain_text(
        Path(output_root or configured.output_dir), application_id
    )
    copied = bool(letter) and bool(copier(letter))
    log_event(
        db,
        application_id,
        "apply_url_opened",
        {"via": via, "route": "manual_open", "opened": opened, "letter_copied": copied},
    )
    return opened, copied


#: Attributes that could carry what a human typed. Form learning never sees them.
_VALUE_BEARING_ATTRIBUTES = frozenset({"value", "placeholder", "checked", "selected"})


def observable_controls(html: str) -> tuple[dict[str, str], ...]:
    """Every fillable control's *shape*, for form learning. Never its contents.

    ``value``, ``placeholder`` and the checked/selected flags are stripped here
    rather than at the caller, so there is exactly one place where "we do not
    read what the human typed" is enforced.
    """

    return tuple(
        {
            "tag": control.tag,
            **{
                key: value
                for key, value in control.attributes.items()
                if key not in _VALUE_BEARING_ATTRIBUTES
            },
        }
        for control in _controls_from_html(html)
    )


def selector_matches_html(html: str, selector: str) -> bool:
    """Whether a stored selector still finds a control on the current page."""

    return any(
        _selector_matches(control, selector) for control in _controls_from_html(html)
    )
