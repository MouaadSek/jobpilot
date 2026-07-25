"""LinkedIn / Indeed alert parsing + IMAP-backed Source (with injected transport)."""

from __future__ import annotations

import email
import sqlite3
from dataclasses import replace
from email.message import EmailMessage
from pathlib import Path
from typing import Any

import pytest

from jobpilot.config import MissingCredentialError, Settings
from jobpilot.ingest import ingest_source
from jobpilot.sources.email_alerts import (
    EmailAlertError,
    GmailIMAP,
    IndeedAlertSource,
    LinkedInAlertSource,
    clean_job_url,
    html_of,
    parse_indeed,
    parse_linkedin,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "email_alerts"

LINKEDIN_HTML = """
<html><body>
  <table>
    <tr><td><a href="https://www.linkedin.com/comm/jobs/view/3812345678/?trk=eml">
      Alternance Analyste SOC - ACME Cyber - Lille, Hauts-de-France</a></td></tr>
    <tr><td><a href="https://www.linkedin.com/comm/jobs/view/3899999999/?trk=eml">
      Ingénieur Cybersécurité - SecuCorp - Paris</a></td></tr>
    <tr><td><a href="https://www.linkedin.com/comm/jobs/view/3812345678/?trk=dup">
      Alternance Analyste SOC - ACME Cyber - Lille</a></td></tr>
    <tr><td><a href="https://www.linkedin.com/feed/">Unsubscribe</a></td></tr>
  </table>
</body></html>
"""

INDEED_HTML = """
<html><body>
  <a href="https://fr.indeed.com/rc/clk?jk=a1b2c3d4e5f60718&from=ja">
    Stage Pentest - RedTeam SAS - Villeneuve-d'Ascq (59)</a>
  <a href="https://fr.indeed.com/pagead/clk?jk=ffee00112233aabb">
    Alternance DevSecOps - CloudCorp - Paris (75)</a>
  <a href="https://fr.indeed.com/">Manage alerts</a>
</body></html>
"""


def _settings(gmail: bool = True) -> Settings:
    return Settings(
        db_path=Path(":memory:"),
        log_dir=Path("logs"),
        config_dir=Path("config"),
        schema_path=Path("schema.sql"),
        migrations_dir=Path("migrations"),
        embed_model="x",
        queue_threshold=0.35,
        ft_client_id=None,
        ft_client_secret=None,
        ft_token_url="",
        ft_search_url="",
        ft_scope="",
        ft_published_since=31,
        lba_api_key=None,
        lba_search_url="",
        lba_caller_email=None,
        gmail_address="me@gmail.com" if gmail else None,
        gmail_app_password="pw" if gmail else None,
        email_alert_since_days=7,
        wttj_app_id="APP",
        wttj_api_key=None,
        wttj_index="idx",
    )


def _msg(html: str) -> EmailMessage:
    m = EmailMessage()
    m["From"] = "jobalerts-noreply@linkedin.com"
    m["Subject"] = "Your job alert"
    m.set_content("plain fallback")
    m.add_alternative(html, subtype="html")
    return m


def _fixture_message(name: str):
    with (FIXTURE_DIR / name).open("rb") as fixture:
        return email.message_from_binary_file(fixture)


class _FakeIMAP:
    def __init__(self, messages) -> None:
        self._messages = messages

    def fetch_from(self, senders, since_days):
        return self._messages


# ---- parsing ----


def test_parse_linkedin_extracts_and_dedups() -> None:
    recs = parse_linkedin(LINKEDIN_HTML)
    assert [r.external_id for r in recs] == ["3812345678", "3899999999"]  # deduped
    first = recs[0]
    assert first.title == "Alternance Analyste SOC"
    assert first.company_name == "ACME Cyber"
    assert first.city == "Lille, Hauts-de-France"
    assert "jobs/view/3812345678" in first.url


def test_parse_indeed_extracts_jk_ids() -> None:
    recs = parse_indeed(INDEED_HTML)
    assert {r.external_id for r in recs} == {"a1b2c3d4e5f60718", "ffee00112233aabb"}
    soc = next(r for r in recs if r.external_id.startswith("a1b2"))
    assert soc.title == "Stage Pentest"
    assert soc.company_name == "RedTeam SAS"


def test_parse_ignores_non_job_links() -> None:
    # Unsubscribe/manage links must not become offers.
    assert all("jobs/view" in r.url for r in parse_linkedin(LINKEDIN_HTML))
    assert all("jk=" in r.url for r in parse_indeed(INDEED_HTML))


def test_html_of_prefers_html_part() -> None:
    assert "jobs/view" in html_of(_msg(LINKEDIN_HTML))


# ---- Source ----


def test_linkedin_source_yields_offers() -> None:
    src = LinkedInAlertSource(_settings(), imap=_FakeIMAP([_msg(LINKEDIN_HTML)]))
    recs = list(src.fetch_offers())
    assert len(recs) == 2
    assert all(r.contract_type == "unknown" for r in recs)


def test_source_dedups_across_messages() -> None:
    src = LinkedInAlertSource(
        _settings(), imap=_FakeIMAP([_msg(LINKEDIN_HTML), _msg(LINKEDIN_HTML)])
    )
    assert len(list(src.fetch_offers())) == 2  # same ids across two emails


def test_indeed_source() -> None:
    src = IndeedAlertSource(_settings(), imap=_FakeIMAP([_msg(INDEED_HTML)]))
    assert len(list(src.fetch_offers())) == 2


def test_missing_gmail_credentials_raises() -> None:
    with pytest.raises(MissingCredentialError):
        LinkedInAlertSource(_settings(gmail=False))


def test_real_linkedin_fixture_extracts_separate_card_fields_and_cleans_url() -> None:
    records = parse_linkedin(html_of(_fixture_message("linkedin_alert.eml")))

    assert len(records) == 2
    first = records[0]
    assert first.title == "Alternance Analyste SOC"
    assert first.company_name == "ACME Cyber"
    assert first.city == "Lille, Hauts-de-France"
    assert first.description == (
        "Surveillez les alertes SIEM et participez à la réponse aux incidents."
    )
    assert first.url == "https://www.linkedin.com/jobs/view/3812345678"


def test_real_indeed_fixture_extracts_separate_card_fields_and_cleans_url() -> None:
    records = parse_indeed(html_of(_fixture_message("indeed_alert.eml")))

    assert len(records) == 2
    first = records[0]
    assert first.title == "Stage Pentest"
    assert first.company_name == "RedTeam SAS"
    assert first.city == "Villeneuve-d'Ascq (59)"
    assert first.description == (
        "Testez des applications web et rédigez les rapports de vulnérabilité."
    )
    assert first.url == "https://fr.indeed.com/viewjob?jk=a1b2c3d4e5f60718"


@pytest.mark.parametrize(
    ("provider", "url", "expected"),
    [
        (
            "linkedin",
            "https://www.linkedin.com/comm/jobs/view/42/?trk=mail&utm_source=alert",
            "https://www.linkedin.com/jobs/view/42",
        ),
        (
            "indeed",
            "https://fr.indeed.com/rc/clk?jk=abcd1234&from=ja&utm_campaign=mail",
            "https://fr.indeed.com/viewjob?jk=abcd1234",
        ),
    ],
)
def test_clean_job_url_removes_tracking_parameters(
    provider: str,
    url: str,
    expected: str,
) -> None:
    assert clean_job_url(url, provider) == expected


def test_malformed_alert_is_warned_and_does_not_abort_valid_email(
    caplog: pytest.LogCaptureFixture,
) -> None:
    source = LinkedInAlertSource(
        _settings(),
        imap=_FakeIMAP(
            [
                _fixture_message("malformed_alert.eml"),
                _fixture_message("linkedin_alert.eml"),
            ]
        ),
    )

    with caplog.at_level("INFO"):
        records = list(source.fetch_offers())

    assert len(records) == 2
    assert "skipping malformed linkedin alert" in caplog.text.lower()
    assert "emails_scanned=2" in caplog.text
    assert "entries_found=2" in caplog.text


def test_repeated_fixture_alert_ingestion_is_idempotent(
    db: sqlite3.Connection,
) -> None:
    message = _fixture_message("linkedin_alert.eml")
    first = ingest_source(
        db,
        LinkedInAlertSource(_settings(), imap=_FakeIMAP([message])),
    )
    second = ingest_source(
        db,
        LinkedInAlertSource(
            _settings(),
            imap=_FakeIMAP([_fixture_message("linkedin_alert.eml")]),
        ),
    )

    assert first.inserted == 2
    assert second.inserted == 0
    assert second.duplicates == 2
    assert db.execute("SELECT count(*) AS n FROM offers").fetchone()["n"] == 2


def test_imap_transport_uses_configured_readonly_folder_and_body_peek(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw_message = (FIXTURE_DIR / "linkedin_alert.eml").read_bytes()
    calls: dict[str, Any] = {}

    class FakeConnection:
        def login(self, address: str, password: str) -> tuple[str, list[bytes]]:
            calls["login"] = (address, password)
            return "OK", []

        def select(
            self,
            folder: str,
            readonly: bool = False,
        ) -> tuple[str, list[bytes]]:
            calls["select"] = (folder, readonly)
            return "OK", []

        def search(self, *criteria: str) -> tuple[str, list[bytes]]:
            calls["search"] = criteria
            return "OK", [b"1"]

        def fetch(self, number: bytes, query: str):
            calls["fetch"] = (number, query)
            return "OK", [(b"1", raw_message)]

        def logout(self) -> tuple[str, list[bytes]]:
            calls["logout"] = True
            return "BYE", []

    def imap_factory(host: str, port: int) -> FakeConnection:
        calls["endpoint"] = (host, port)
        return FakeConnection()

    monkeypatch.setattr(
        "jobpilot.sources.email_alerts.imaplib.IMAP4_SSL",
        imap_factory,
    )
    transport = GmailIMAP(
        "mouaad@example.com",
        "app-password",
        host="imap.example.com",
        port=1993,
        folder="Alerts",
    )

    messages = transport.fetch_from(["jobalerts-noreply@linkedin.com"], 7)

    assert len(messages) == 1
    assert calls["endpoint"] == ("imap.example.com", 1993)
    assert calls["select"] == ("Alerts", True)
    assert calls["fetch"] == (b"1", "(BODY.PEEK[])")
    assert "SINCE" in calls["search"]
    assert calls["logout"] is True


def test_imap_failure_redacts_gmail_app_password(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "gmail-app-password-secret"
    settings = replace(_settings(), gmail_app_password=secret)

    class RejectingConnection:
        def login(self, address: str, password: str) -> None:
            raise RuntimeError(f"login rejected password={password}")

        def logout(self) -> None:
            return None

    monkeypatch.setattr(
        "jobpilot.sources.email_alerts.imaplib.IMAP4_SSL",
        lambda host, port: RejectingConnection(),
    )
    source = LinkedInAlertSource(settings)

    with pytest.raises(EmailAlertError) as caught:
        list(source.fetch_offers())

    assert secret not in str(caught.value)
    assert "[REDACTED]" in str(caught.value)


def test_imap_connection_settings_use_existing_gmail_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from jobpilot import config

    monkeypatch.setenv("GMAIL_ADDRESS", "alerts@example.com")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "existing-app-password")
    monkeypatch.setenv("IMAP_HOST", "imap.example.com")
    monkeypatch.setenv("IMAP_PORT", "1993")
    monkeypatch.setenv("IMAP_FOLDER", "Job Alerts")
    monkeypatch.setenv("EMAIL_ALERT_SINCE_DAYS", "9")
    config.get_settings.cache_clear()
    try:
        settings = config.get_settings()
        assert settings.gmail_address == "alerts@example.com"
        assert settings.gmail_app_password == "existing-app-password"
        assert settings.imap_host == "imap.example.com"
        assert settings.imap_port == 1993
        assert settings.imap_folder == "Job Alerts"
        assert settings.email_alert_since_days == 9
    finally:
        config.get_settings.cache_clear()
