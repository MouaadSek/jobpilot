"""LinkedIn / Indeed alert parsing + IMAP-backed Source (with injected transport)."""

from __future__ import annotations

from email.message import EmailMessage
from pathlib import Path

import pytest

from jobpilot.config import MissingCredentialError, Settings
from jobpilot.sources.email_alerts import (
    IndeedAlertSource,
    LinkedInAlertSource,
    html_of,
    parse_indeed,
    parse_linkedin,
)

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
        db_path=Path(":memory:"), log_dir=Path("logs"), config_dir=Path("config"),
        schema_path=Path("schema.sql"), migrations_dir=Path("migrations"),
        embed_model="x", queue_threshold=0.35, ft_client_id=None,
        ft_client_secret=None, ft_token_url="", ft_search_url="", ft_scope="",
        ft_published_since=31, lba_api_key=None, lba_search_url="",
        lba_caller_email=None,
        gmail_address="me@gmail.com" if gmail else None,
        gmail_app_password="pw" if gmail else None,
        email_alert_since_days=7,
        wttj_app_id="APP", wttj_api_key=None, wttj_index="idx",
    )


def _msg(html: str) -> EmailMessage:
    m = EmailMessage()
    m["From"] = "jobalerts-noreply@linkedin.com"
    m["Subject"] = "Your job alert"
    m.set_content("plain fallback")
    m.add_alternative(html, subtype="html")
    return m


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
