"""WTTJ inline application stays human-approved and dry-run by default."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

import pytest

from jobpilot.apply_assist import (
    ApplicantProfile,
    WTTJAdapter,
    WTTJApplyError,
    launch_wttj_application,
)
from jobpilot.config import Settings
from jobpilot.state import current_status

FIXTURES = Path(__file__).parent / "fixtures" / "apply_assist"
WTTJ_URL = (
    "https://www.welcometothejungle.com/fr/companies/acme/jobs/"
    "analyste-soc_paris"
)
APPLICANT = ApplicantProfile(
    full_name="Mouaad Sekkouri",
    email="mouaad@example.test",
    phone="+33 7 51 13 54 25",
    linkedin_url="https://www.linkedin.com/in/sekkouri",
)


class _FakeLocator:
    def __init__(self, selector: str, page: _FakePage) -> None:
        self.selector = selector
        self.page = page

    @property
    def first(self) -> _FakeLocator:
        return self

    def count(self) -> int:
        if self.selector in WTTJAdapter.confirmation_selectors:
            return int(
                self.page.confirmation_ready
                or self.page.preexisting_confirmation_visible
                or self.page.preexisting_confirmation_hidden
            )
        return 1

    def is_visible(self) -> bool:
        if self.selector in WTTJAdapter.confirmation_selectors:
            return self.page.confirmation_ready or self.page.preexisting_confirmation_visible
        return self.count() > 0

    def fill(self, value: str) -> None:
        self.page.actions.append(("fill", self.selector, value))

    def set_input_files(self, files: str) -> None:
        self.page.actions.append(("upload", self.selector, files))

    def click(self) -> None:
        self.page.actions.append(("click", self.selector, ""))
        self.page.submitted = True
        if self.page.confirmation_ready:
            self.page.url = "https://www.welcometothejungle.com/fr/applications/confirmation"


class _FakePage:
    def __init__(
        self,
        html: str,
        *,
        confirm_after_submit: bool = True,
        confirmation_delay_ticks: int = 0,
        preexisting_confirmation_visible: bool = False,
        preexisting_confirmation_hidden: bool = False,
    ) -> None:
        self.html = html
        self.confirm_after_submit = confirm_after_submit
        self.confirmation_delay_ticks = confirmation_delay_ticks
        self.preexisting_confirmation_visible = preexisting_confirmation_visible
        self.preexisting_confirmation_hidden = preexisting_confirmation_hidden
        self.wait_ticks = 0
        self.submitted = False
        self.url = WTTJ_URL
        self.actions: list[tuple[str, str, str]] = []
        self.screenshots: list[Path] = []

    @property
    def confirmation_ready(self) -> bool:
        return (
            self.submitted
            and self.confirm_after_submit
            and self.wait_ticks >= self.confirmation_delay_ticks
        )

    def content(self) -> str:
        return self.html

    def locator(self, selector: str) -> _FakeLocator:
        return _FakeLocator(selector, self)

    def screenshot(self, *, path: str, full_page: bool) -> None:
        assert full_page is True
        screenshot = Path(path)
        screenshot.write_bytes(b"fake-png:" + self.html.encode("utf-8"))
        self.screenshots.append(screenshot)

    def wait_for_timeout(self, timeout: float) -> None:
        assert timeout > 0
        self.wait_ticks += 1
        if self.confirmation_ready:
            self.url = "https://www.welcometothejungle.com/fr/applications/confirmation"


class _FakeLauncher:
    def __init__(self, page: _FakePage) -> None:
        self.page = page
        self.urls: list[str] = []

    def open_page(self, url: str) -> _FakePage:
        self.urls.append(url)
        return self.page


def _settings(tmp_path: Path, *, live: bool) -> Settings:
    return Settings(
        db_path=Path(":memory:"),
        log_dir=tmp_path / "logs",
        config_dir=Path("config"),
        schema_path=Path("schema.sql"),
        migrations_dir=Path("migrations"),
        embed_model="x",
        queue_threshold=0.6,
        ft_client_id=None,
        ft_client_secret=None,
        ft_token_url="",
        ft_search_url="",
        ft_scope="",
        ft_published_since=31,
        lba_api_key=None,
        lba_search_url="",
        lba_caller_email=None,
        gmail_address=None,
        gmail_app_password=None,
        email_alert_since_days=7,
        wttj_app_id="APP",
        wttj_api_key=None,
        wttj_index="idx",
        applicant_full_name=APPLICANT.full_name,
        applicant_email=APPLICANT.email,
        applicant_phone=APPLICANT.phone,
        applicant_linkedin_url=APPLICANT.linkedin_url,
        wttj_auto_submit_enabled=live,
    )


def _ready_wttj_application(
    db: sqlite3.Connection,
    output_root: Path,
    *,
    suffix: str,
    status: str = "ready",
) -> int:
    source_id = db.execute("SELECT id FROM sources WHERE name = 'wttj'").fetchone()["id"]
    company_id = db.execute(
        "INSERT INTO companies (name, city) VALUES ('Acme', 'Paris')"
    ).lastrowid
    digest = hashlib.sha256(f"wttj-apply-{suffix}".encode()).hexdigest()
    offer_id = db.execute(
        "INSERT INTO offers (source_id, company_id, external_id, url, title, "
        "description, contract_type, city, content_hash) "
        "VALUES (?, ?, 'wttj-42', ?, 'Analyste SOC', 'desc', "
        "'alternance', 'Paris', ?)",
        (source_id, company_id, WTTJ_URL, digest),
    ).lastrowid
    application_id = int(
        db.execute(
            "INSERT INTO applications (offer_id, company_id, kind, status) "
            "VALUES (?, ?, 'offer', ?)",
            (offer_id, company_id, status),
        ).lastrowid
    )
    artifact_dir = output_root / str(application_id)
    artifact_dir.mkdir(parents=True)
    cv_path = artifact_dir / "cv.pdf"
    letter_path = artifact_dir / "motivation_letter.pdf"
    cv_path.write_bytes(b"%PDF-cv")
    letter_path.write_bytes(b"%PDF-letter")
    db.execute(
        "UPDATE applications SET cv_pdf_path = ?, letter_pdf_path = ? WHERE id = ?",
        (str(cv_path), str(letter_path), application_id),
    )
    db.commit()
    return application_id


def _events(db: sqlite3.Connection, application_id: int) -> list[sqlite3.Row]:
    return db.execute(
        "SELECT event, detail FROM events WHERE application_id = ? ORDER BY id",
        (application_id,),
    ).fetchall()


@pytest.mark.parametrize(
    "fixture_name",
    ["wttj_standard.html", "wttj_split_name.html", "wttj_required_letter.html"],
)
def test_wttj_adapter_maps_all_saved_form_variants(
    fixture_name: str,
    tmp_path: Path,
) -> None:
    html = (FIXTURES / fixture_name).read_text(encoding="utf-8")
    cv_path = tmp_path / "cv.pdf"
    letter_path = tmp_path / "motivation_letter.pdf"
    cv_path.write_bytes(b"%PDF-cv")
    letter_path.write_bytes(b"%PDF-letter")
    adapter = WTTJAdapter()

    plan = adapter.build_plan(html, APPLICANT, cv_path, letter_path)
    adapter.validate_pre_submit(
        html,
        plan,
        expected_external_id="wttj-42",
        expected_title="Analyste SOC",
    )

    assert {action.field for action in plan.fills} >= {"email"}
    assert {action.field for action in plan.uploads} >= {"cv"}



def test_wttj_actions_are_scoped_to_the_identified_application_form(
    tmp_path: Path,
) -> None:
    application_html = (FIXTURES / "wttj_standard.html").read_text(encoding="utf-8")
    html = (
        '<form id="newsletter"><input name="email" required>'
        '<button type="submit">Subscribe</button></form>'
        + application_html
    )
    cv_path = tmp_path / "cv.pdf"
    letter_path = tmp_path / "motivation_letter.pdf"
    cv_path.write_bytes(b"%PDF-cv")
    letter_path.write_bytes(b"%PDF-letter")
    adapter = WTTJAdapter()
    page = _FakePage(html)

    plan = adapter.build_plan(html, APPLICANT, cv_path, letter_path)
    adapter.validate_pre_submit(
        html,
        plan,
        expected_external_id="wttj-42",
        expected_title="Analyste SOC",
    )
    adapter.apply_plan(page, plan)
    adapter.submit(page, plan)

    assert plan.scope is not None
    assert all(selector.startswith(plan.scope) for _, selector, _ in page.actions)



def test_wttj_form_can_use_page_data_offer_identity(tmp_path: Path) -> None:
    html = (FIXTURES / "wttj_standard.html").read_text(encoding="utf-8")
    html = html.replace(
        '        <input type="hidden" name="offer_id" value="wttj-42" required>\n',
        "",
    )
    cv_path = tmp_path / "cv.pdf"
    letter_path = tmp_path / "motivation_letter.pdf"
    cv_path.write_bytes(b"%PDF-cv")
    letter_path.write_bytes(b"%PDF-letter")
    adapter = WTTJAdapter()
    page = _FakePage(html)

    plan = adapter.build_plan(html, APPLICANT, cv_path, letter_path)
    adapter.validate_pre_submit(
        html,
        plan,
        expected_external_id="wttj-42",
        expected_title="Analyste SOC",
    )
    adapter.apply_plan(page, plan)

    assert plan.scope is not None
    assert "form:has(" in plan.scope


@pytest.mark.parametrize(
    "fixture_name",
    ["wttj_standard.html", "wttj_split_name.html", "wttj_required_letter.html"],
)
def test_dry_run_fills_uploads_and_screenshots_but_never_submits(
    db: sqlite3.Connection,
    tmp_path: Path,
    fixture_name: str,
) -> None:
    application_id = _ready_wttj_application(
        db, tmp_path, suffix=f"dry-{fixture_name}"
    )
    page = _FakePage((FIXTURES / fixture_name).read_text(encoding="utf-8"))

    result = launch_wttj_application(
        db,
        application_id,
        output_root=tmp_path,
        settings=_settings(tmp_path, live=False),
        launcher=_FakeLauncher(page),
        opener=lambda _: pytest.fail("safe dry-run must not need fallback"),
        via="dashboard",
    )

    assert result.outcome == "apply_dry_run"
    assert result.screenshot_path == tmp_path / str(application_id) / "wttj_apply.png"
    assert result.screenshot_path.is_file()
    assert {kind for kind, _, _ in page.actions} == {"fill", "upload"}
    assert current_status(db, application_id) == "ready"
    assert [row["event"] for row in _events(db, application_id)] == [
        "human_approved",
        "apply_dry_run",
    ]


def test_live_mode_submits_only_after_assertions_and_transitions(
    db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    application_id = _ready_wttj_application(db, tmp_path, suffix="live")
    page = _FakePage((FIXTURES / "wttj_standard.html").read_text(encoding="utf-8"))

    result = launch_wttj_application(
        db,
        application_id,
        output_root=tmp_path,
        settings=_settings(tmp_path, live=True),
        launcher=_FakeLauncher(page),
        opener=lambda _: pytest.fail("confirmed submission must not use fallback"),
        via="dashboard",
    )

    assert result.outcome == "application_submitted"
    assert [kind for kind, _, _ in page.actions].count("click") == 1
    assert current_status(db, application_id) == "applied"
    events = _events(db, application_id)
    assert [row["event"] for row in events] == [
        "human_approved",
        "application_submitted",
        "status_change",
    ]
    assert json.loads(events[-1]["detail"])["to"] == "applied"



def test_live_mode_waits_for_delayed_confirmation(
    db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    application_id = _ready_wttj_application(db, tmp_path, suffix="delayed")
    page = _FakePage(
        (FIXTURES / "wttj_standard.html").read_text(encoding="utf-8"),
        confirmation_delay_ticks=2,
    )

    result = launch_wttj_application(
        db,
        application_id,
        output_root=tmp_path,
        settings=_settings(tmp_path, live=True),
        launcher=_FakeLauncher(page),
        via="dashboard",
    )

    assert result.outcome == "application_submitted"
    assert page.wait_ticks >= 2
    assert current_status(db, application_id) == "applied"


@pytest.mark.parametrize(
    ("mutation", "expected_reason"),
    [
        ("captcha", "captcha_detected"),
        ("password", "password_detected"),
        ("account", "account_required"),
        ("missing_field", "required_field_unmapped"),
        ("missing_select", "required_field_unmapped"),
        ("id_mismatch", "offer_mismatch"),
        ("missing_cv", "missing_cv"),
        ("missing_letter", "missing_letter"),
    ],
)
def test_abort_conditions_never_submit_and_leave_state_ready(
    db: sqlite3.Connection,
    tmp_path: Path,
    mutation: str,
    expected_reason: str,
) -> None:
    application_id = _ready_wttj_application(
        db, tmp_path, suffix=f"blocked-{mutation}"
    )
    fixture = "wttj_required_letter.html" if mutation == "missing_letter" else "wttj_standard.html"
    html = (FIXTURES / fixture).read_text(encoding="utf-8")
    if mutation == "captcha":
        html = html.replace("</form>", '<div class="g-recaptcha"></div></form>')
    elif mutation == "password":
        html = html.replace(
            "</form>",
            '<input type="password" name="password" required></form>',
        )
    elif mutation == "account":
        html = html.replace(
            "</form>",
            "<label><input type='checkbox' name='create_account'>"
            "Créer un compte</label></form>",
        )
    elif mutation == "missing_field":
        html = html.replace(
            "</form>",
            '<input type="text" name="portfolio" required></form>',
        )
    elif mutation == "missing_select":
        html = html.replace(
            "</form>",
            '<select name="availability" required>'
            '<option value="">Choisir</option></select></form>',
        )
    elif mutation == "id_mismatch":
        html = html.replace('value="wttj-42"', 'value="wttj-other"')
    elif mutation == "missing_cv":
        (tmp_path / str(application_id) / "cv.pdf").unlink()
    elif mutation == "missing_letter":
        (tmp_path / str(application_id) / "motivation_letter.pdf").unlink()
    page = _FakePage(html)
    launcher = _FakeLauncher(page)
    opened: list[str] = []

    result = launch_wttj_application(
        db,
        application_id,
        output_root=tmp_path,
        settings=_settings(tmp_path, live=True),
        launcher=launcher,
        opener=lambda url: opened.append(url) or True,
        via="dashboard",
    )

    assert result.outcome == "apply_blocked"
    assert result.reason == expected_reason
    assert not any(kind == "click" for kind, _, _ in page.actions)
    assert current_status(db, application_id) == "ready"
    assert opened == [WTTJ_URL]
    blocked = _events(db, application_id)[-1]
    assert blocked["event"] == "apply_blocked"
    assert json.loads(blocked["detail"])["reason"] == expected_reason


def test_unconfirmed_submission_is_prominent_and_does_not_transition(
    db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    application_id = _ready_wttj_application(db, tmp_path, suffix="unconfirmed")
    page = _FakePage(
        (FIXTURES / "wttj_standard.html").read_text(encoding="utf-8"),
        confirm_after_submit=False,
    )

    result = launch_wttj_application(
        db,
        application_id,
        output_root=tmp_path,
        settings=_settings(tmp_path, live=True),
        launcher=_FakeLauncher(page),
        opener=lambda _: True,
        via="dashboard",
    )

    assert result.outcome == "submit_unconfirmed"
    assert current_status(db, application_id) == "ready"
    assert _events(db, application_id)[-1]["event"] == "submit_unconfirmed"

    with pytest.raises(WTTJApplyError, match="previous WTTJ submission"):
        launch_wttj_application(
            db,
            application_id,
            output_root=tmp_path,
            settings=_settings(tmp_path, live=True),
            launcher=_FakeLauncher(page),
            via="dashboard",
        )
    assert [kind for kind, _, _ in page.actions].count("click") == 1


def test_success_in_job_slug_is_not_submission_confirmation(
    db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    application_id = _ready_wttj_application(db, tmp_path, suffix="success-slug")
    page = _FakePage(
        (FIXTURES / "wttj_standard.html").read_text(encoding="utf-8"),
        confirm_after_submit=False,
    )
    page.url = (
        "https://www.welcometothejungle.com/fr/companies/acme/jobs/"
        "customer-success-manager_paris"
    )

    result = launch_wttj_application(
        db,
        application_id,
        output_root=tmp_path,
        settings=_settings(tmp_path, live=True),
        launcher=_FakeLauncher(page),
        via="dashboard",
    )

    assert result.outcome == "submit_unconfirmed"
    assert current_status(db, application_id) == "ready"


@pytest.mark.parametrize(
    ("preexisting_visible", "preexisting_hidden"),
    ((True, False), (False, True)),
)
def test_preexisting_confirmation_marker_does_not_confirm_submission(
    db: sqlite3.Connection,
    tmp_path: Path,
    preexisting_visible: bool,
    preexisting_hidden: bool,
) -> None:
    application_id = _ready_wttj_application(
        db,
        tmp_path,
        suffix=f"preexisting-{preexisting_visible}-{preexisting_hidden}",
    )
    page = _FakePage(
        (FIXTURES / "wttj_standard.html").read_text(encoding="utf-8"),
        confirm_after_submit=False,
        preexisting_confirmation_visible=preexisting_visible,
        preexisting_confirmation_hidden=preexisting_hidden,
    )

    result = launch_wttj_application(
        db,
        application_id,
        output_root=tmp_path,
        settings=_settings(tmp_path, live=True),
        launcher=_FakeLauncher(page),
        via="dashboard",
    )

    assert result.outcome == "submit_unconfirmed"
    assert current_status(db, application_id) == "ready"


def test_wrong_state_is_a_clean_domain_error(
    db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    application_id = _ready_wttj_application(
        db, tmp_path, suffix="queued", status="queued"
    )

    with pytest.raises(WTTJApplyError, match="ready"):
        launch_wttj_application(
            db,
            application_id,
            output_root=tmp_path,
            settings=_settings(tmp_path, live=False),
            launcher=_FakeLauncher(
                _FakePage(
                    (FIXTURES / "wttj_standard.html").read_text(encoding="utf-8")
                )
            ),
            via="dashboard",
        )
