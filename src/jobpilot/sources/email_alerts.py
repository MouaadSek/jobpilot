"""LinkedIn / Indeed job-alert ingestion by parsing the alert emails (Gmail IMAP).

We do NOT scrape LinkedIn or Indeed (constitution). Instead we read the job-alert
emails they send, extract (title, company, location, original link + job id), and
ingest them as offers under the `linkedin_alert` / `indeed_alert` sources. Dedup
is primarily on (source_id, external_id) via the job id in the link, so repeated
alerts collapse to one row.

The HTML parsers are tolerant and covered by fixture tests; their selectors should
be confirmed against a real forwarded alert (title/link/job-id are reliable;
company/location are best-effort from the alert layout).
"""

from __future__ import annotations

import email
import imaplib
import re
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from email.message import Message
from html import unescape
from html.parser import HTMLParser

from jobpilot.config import Settings
from jobpilot.logging_conf import get_logger
from jobpilot.models import OfferRecord
from jobpilot.sources.base import Source

log = get_logger("email_alerts")

LINKEDIN_SENDERS = [
    "jobalerts-noreply@linkedin.com", "jobs-noreply@linkedin.com",
    "jobs-listings@linkedin.com",
]
INDEED_SENDERS = [
    "alert@indeed.com", "noreply@indeed.com", "donotreply@indeed.com",
    "invitetoapply@indeed.com",
]

_TAG_RE = re.compile(r"<[^>]+>")


def _strip_tags(html: str) -> str:
    return " ".join(unescape(_TAG_RE.sub(" ", html)).split())


# ---- IMAP transport (injectable for tests) ----

class GmailIMAP:
    """Minimal read-only Gmail IMAP client."""

    def __init__(self, address: str, app_password: str,
                 host: str = "imap.gmail.com") -> None:
        self._address = address
        self._password = app_password
        self._host = host

    def fetch_from(self, senders: list[str], since_days: int) -> list[Message]:
        since = (datetime.now(UTC) - timedelta(days=since_days)).strftime("%d-%b-%Y")
        conn = imaplib.IMAP4_SSL(self._host)
        try:
            conn.login(self._address, self._password)
            conn.select("INBOX", readonly=True)
            messages: list[Message] = []
            for sender in senders:
                typ, data = conn.search(None, "FROM", f'"{sender}"', "SINCE", since)
                if typ != "OK" or not data or not data[0]:
                    continue
                for num in data[0].split():
                    typ, msg_data = conn.fetch(num, "(RFC822)")
                    if typ != "OK" or not msg_data or not msg_data[0]:
                        continue
                    raw = msg_data[0][1]
                    messages.append(email.message_from_bytes(raw))
            return messages
        finally:
            try:
                conn.logout()
            except Exception:  # best-effort close
                log.debug("IMAP logout failed", exc_info=True)


def html_of(msg: Message) -> str:
    """Return the best HTML (or plain-text) body of an email message."""
    html_parts: list[str] = []
    text_parts: list[str] = []
    for part in msg.walk() if msg.is_multipart() else [msg]:
        ctype = part.get_content_type()
        if ctype not in ("text/html", "text/plain"):
            continue
        payload = part.get_payload(decode=True)
        if payload is None:
            continue
        charset = part.get_content_charset() or "utf-8"
        try:
            decoded = payload.decode(charset, errors="replace")
        except LookupError:
            decoded = payload.decode("utf-8", errors="replace")
        (html_parts if ctype == "text/html" else text_parts).append(decoded)
    return "\n".join(html_parts) if html_parts else "\n".join(text_parts)


# ---- anchor extraction ----

class _AnchorParser(HTMLParser):
    """Collects (href, inner_text) for every <a> tag."""

    def __init__(self) -> None:
        super().__init__()
        self.anchors: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._href is not None:
            self.anchors.append((self._href, " ".join(" ".join(self._text).split())))
            self._href = None
            self._text = []


def _anchors(html: str) -> list[tuple[str, str]]:
    p = _AnchorParser()
    p.feed(html)
    return p.anchors


# ---- provider parsers (pure, fixture-tested) ----

_LINKEDIN_ID_RE = re.compile(r"/jobs/view/(\d+)")
_INDEED_JK_RE = re.compile(r"[?&]jk=([0-9a-f]+)")


def parse_linkedin(html: str) -> list[OfferRecord]:
    """Extract jobs from a LinkedIn job-alert email."""
    out: list[OfferRecord] = []
    seen: set[str] = set()
    for href, text in _anchors(html):
        m = _LINKEDIN_ID_RE.search(href)
        if not m or not text:
            continue
        job_id = m.group(1)
        if job_id in seen:
            continue
        seen.add(job_id)
        title, company, city = _split_card(text)
        out.append(OfferRecord(
            external_id=job_id, url=unescape(href), title=title,
            company_name=company, city=city, contract_type="unknown",
        ).normalized())
    return out


def parse_indeed(html: str) -> list[OfferRecord]:
    """Extract jobs from an Indeed job-alert email."""
    out: list[OfferRecord] = []
    seen: set[str] = set()
    for href, text in _anchors(html):
        m = _INDEED_JK_RE.search(href)
        if not m or not text:
            continue
        jk = m.group(1)
        if jk in seen:
            continue
        seen.add(jk)
        title, company, city = _split_card(text)
        out.append(OfferRecord(
            external_id=jk, url=unescape(href), title=title,
            company_name=company, city=city, contract_type="unknown",
        ).normalized())
    return out


def _split_card(text: str) -> tuple[str, str | None, str | None]:
    """Best-effort split of "Title - Company - Location" style anchor text.

    Alert anchors sometimes pack title/company/location separated by '-', '·' or
    '|'. Title is always the first segment; company/location follow if present.
    """
    parts = [p.strip() for p in re.split(r"\s[-–·|]\s", text) if p.strip()]
    title = parts[0] if parts else text
    company = parts[1] if len(parts) > 1 else None
    city = parts[2] if len(parts) > 2 else None
    return title, company, city


# ---- Source implementations ----

class _EmailAlertSource(Source):
    senders: list[str] = []

    def __init__(self, settings: Settings, *, imap: GmailIMAP | None = None,
                 since_days: int | None = None) -> None:
        address, password = settings.require_gmail_credentials()
        self._imap = imap or GmailIMAP(address, password)
        self._since_days = (
            since_days if since_days is not None else settings.email_alert_since_days
        )

    def _parse(self, html: str) -> list[OfferRecord]:  # overridden
        raise NotImplementedError

    def fetch_offers(self) -> Iterator[OfferRecord]:
        seen: set[str] = set()
        for msg in self._imap.fetch_from(self.senders, self._since_days):
            for rec in self._parse(html_of(msg)):
                key = rec.external_id or rec.hash
                if key in seen:
                    continue
                seen.add(key)
                yield rec


class LinkedInAlertSource(_EmailAlertSource):
    name = "linkedin_alert"
    senders = LINKEDIN_SENDERS

    def _parse(self, html: str) -> list[OfferRecord]:
        return parse_linkedin(html)


class IndeedAlertSource(_EmailAlertSource):
    name = "indeed_alert"
    senders = INDEED_SENDERS

    def _parse(self, html: str) -> list[OfferRecord]:
        return parse_indeed(html)
