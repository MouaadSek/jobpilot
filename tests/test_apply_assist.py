"""ATS prefill adapters use saved markup only; browser launch is fully stubbed."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

import pytest

from jobpilot.apply_assist import (
    ApplicantProfile,
    ApplyAdapter,
    GreenhouseAdapter,
    LeverAdapter,
    SmartRecruitersAdapter,
    launch_application_assist,
)
from jobpilot.config import Settings
from jobpilot.state import current_status

FIXTURES = Path(__file__).parent / "fixtures" / "apply_assist"
APPLICANT = ApplicantProfile(
    full_name="Mouaad Sekkouri",
    email="mouaad@example.test",
    phone="+33 7 51 13 54 25",
    linkedin_url="https://www.linkedin.com/in/sekkouri",
)


@pytest.mark.parametrize(
    ("adapter", "fixture", "expected_name_fields"),
    [
        (LeverAdapter(), "lever.html", {"name": "Mouaad Sekkouri"}),
        (
            GreenhouseAdapter(),
            "greenhouse.html",
            {"first_name": "Mouaad", "last_name": "Sekkouri"},
        ),
        (
            SmartRecruitersAdapter(),
            "smartrecruiters.html",
            {"first_name": "Mouaad", "last_name": "Sekkouri"},
        ),
    ],
)
def test_adapter_maps_saved_html_fixture(
    adapter: ApplyAdapter,
    fixture: str,
    expected_name_fields: dict[str, str],
    tmp_path: Path,
) -> None:
    """Each adapter maps real-shaped static markup without a network request."""

    html = (FIXTURES / fixture).read_text(encoding="utf-8")
    cv_path = tmp_path / "cv.pdf"
    letter_path = tmp_path / "motivation_letter.pdf"
    plan = adapter.build_plan(html, APPLICANT, cv_path, letter_path)

    fills = {action.field: action.value for action in plan.fills}
    assert {name: fills[name] for name in expected_name_fields} == expected_name_fields
    assert fills["email"] == APPLICANT.email
    assert fills["phone"] == APPLICANT.phone
    assert fills["linkedin"] == APPLICANT.linkedin_url
    assert [(action.field, action.path) for action in plan.uploads] == [
        ("cv", cv_path),
        ("letter", letter_path),
    ]


class _FakeLocator:
    def __init__(self, selector: str, page: _FakePage) -> None:
        self.selector = selector
        self.page = page

    @property
    def first(self) -> _FakeLocator:
        return self

    def count(self) -> int:
        return 1

    def fill(self, value: str) -> None:
        self.page.fills.append((self.selector, value))

    def set_input_files(self, files: str) -> None:
        self.page.uploads.append((self.selector, files))


class _FakePage:
    def __init__(self, html: str) -> None:
        self.html = html
        self.fills: list[tuple[str, str]] = []
        self.uploads: list[tuple[str, str]] = []
        self.clicks: list[str] = []

    def content(self) -> str:
        return self.html

    def locator(self, selector: str) -> _FakeLocator:
        return _FakeLocator(selector, self)


class _FakeLauncher:
    def __init__(self, page: _FakePage) -> None:
        self.page = page
        self.urls: list[str] = []

    def open_page(self, url: str) -> _FakePage:
        self.urls.append(url)
        return self.page


def _settings(tmp_path: Path) -> Settings:
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
    )


def _ready_ats_application(
    db: sqlite3.Connection,
    output_root: Path,
    *,
    url: str,
) -> int:
    source_id = db.execute("SELECT id FROM sources WHERE name = 'ats'").fetchone()["id"]
    company_id = db.execute(
        "INSERT INTO companies (name, city) VALUES ('Acme', 'Lille')"
    ).lastrowid
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
    offer_id = db.execute(
        "INSERT INTO offers (source_id, company_id, external_id, url, title, "
        "description, contract_type, city, content_hash) "
        "VALUES (?, ?, ?, ?, 'Analyste SOC', 'desc', 'alternance', 'Lille', ?)",
        (source_id, company_id, digest[:12], url, digest),
    ).lastrowid
    application_id = int(
        db.execute(
            "INSERT INTO applications (offer_id, company_id, kind, status) "
            "VALUES (?, ?, 'offer', 'ready')",
            (offer_id, company_id),
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


def test_prefill_uses_stubbed_browser_logs_event_and_never_submits(
    db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    application_id = _ready_ats_application(
        db, tmp_path, url="https://jobs.lever.co/acme/analyste-soc"
    )
    page = _FakePage((FIXTURES / "lever.html").read_text(encoding="utf-8"))
    launcher = _FakeLauncher(page)

    result = launch_application_assist(
        db,
        application_id,
        output_root=tmp_path,
        settings=_settings(tmp_path),
        launcher=launcher,
        opener=lambda _: pytest.fail("fallback must not be used"),
    )

    assert result.outcome == "prefill_launched"
    assert launcher.urls == ["https://jobs.lever.co/acme/analyste-soc"]
    assert ("input[name='name']", APPLICANT.full_name) in page.fills
    assert len(page.uploads) == 2
    assert page.clicks == []
    assert current_status(db, application_id) == "ready"
    event = db.execute(
        "SELECT event, detail FROM events WHERE application_id = ?", (application_id,)
    ).fetchone()
    assert event["event"] == "prefill_launched"
    assert json.loads(event["detail"]) == {"adapter": "lever"}


def test_unknown_ats_opens_default_browser_and_logs_fallback_event(
    db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    url = "https://careers.example.test/jobs/42"
    application_id = _ready_ats_application(db, tmp_path, url=url)
    opened: list[str] = []

    result = launch_application_assist(
        db,
        application_id,
        output_root=tmp_path,
        settings=_settings(tmp_path),
        opener=lambda opened_url: opened.append(opened_url) or True,
    )

    assert result.outcome == "apply_url_opened"
    assert result.fallback_reason == "unknown_ats"
    assert opened == [url]
    assert current_status(db, application_id) == "ready"
    event = db.execute(
        "SELECT event, detail FROM events WHERE application_id = ?", (application_id,)
    ).fetchone()
    assert event["event"] == "apply_url_opened"
    assert json.loads(event["detail"]) == {"reason": "unknown_ats", "opened": True}


def test_adapter_failure_degrades_to_default_browser(
    db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    url = "https://jobs.lever.co/acme/changed-form"
    application_id = _ready_ats_application(db, tmp_path, url=url)
    launcher = _FakeLauncher(_FakePage("<input name='email'>"))
    opened: list[str] = []

    result = launch_application_assist(
        db,
        application_id,
        output_root=tmp_path,
        settings=_settings(tmp_path),
        launcher=launcher,
        opener=lambda opened_url: opened.append(opened_url) or True,
    )

    assert result.outcome == "apply_url_opened"
    assert result.fallback_reason == "lever_prefill_failed"
    assert opened == [url]
    assert current_status(db, application_id) == "ready"
