"""LinkedIn / Indeed job-alert ingestion by parsing the alert emails (Gmail IMAP).

We do NOT scrape LinkedIn or Indeed (constitution). Instead we read the job-alert
emails they send, extract (title, company, location, original link + job id), and
ingest them as offers under the `linkedin_alert` / `indeed_alert` sources. Dedup
is primarily on (source_id, external_id) via the job id in the link, so repeated
alerts collapse to one row.

Mail is selected by SENDER DOMAIN (see the constants block below), not by exact
address: the providers rotate local parts freely.

Alerts carry a title, company and location but effectively no description, and
matcher.py (frozen) builds its matching text from title + description. Records
whose parsed description is thin therefore get one synthesised from the alert's
own fields before they are yielded — see jobpilot.descriptions.

The HTML parsers are tolerant and covered by fixture tests; their selectors should
be confirmed against a real forwarded alert (title/link/job-id are reliable;
company/location are best-effort from the alert layout).
"""

from __future__ import annotations

import email
import imaplib
import re
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from email.message import Message
from email.utils import parseaddr
from html import unescape
from html.parser import HTMLParser
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

from jobpilot.config import Settings
from jobpilot.descriptions import enrich_offer
from jobpilot.logging_conf import get_logger
from jobpilot.models import OfferRecord
from jobpilot.sources.base import Source

log = get_logger("email_alerts")


class EmailAlertError(RuntimeError):
    """A redacted IMAP or alert-processing failure safe for CLI/log display."""


# ---- provider sender domains (single source of truth) ----
#
# Job alerts arrive from a moving set of local parts (alert@, noreply@,
# donotreply@, invitetoapply@, jobalerts-noreply@, and others the providers add
# without notice), so an exact-address allowlist silently drops real alerts:
# `ingest --source indeed_alert` reported emails_scanned=0 against a mailbox
# full of them. We therefore allowlist DOMAINS and accept any address whose
# domain equals one of these or is a subdomain of one.
#
# Matching is on domain boundaries, never substrings, so lookalikes such as
# indeed.evil.com, notlinkedin.com or alert@indeed.com.evil.net are rejected.
# Subdomains are covered implicitly: fr.indeed.com and e.linkedin.com match via
# indeed.com / linkedin.com and need no entry of their own.
LINKEDIN_DOMAINS: tuple[str, ...] = (
    "linkedin.com",  # incl. e.linkedin.com, el.linkedin.com, bounce.linkedin.com
    "linkedinmail.com",  # alternate notification domain; harmless when unused
)
INDEED_DOMAINS: tuple[str, ...] = (
    "indeed.com",  # incl. fr.indeed.com and the other country subdomains
    "indeedemail.com",  # Indeed's bulk-mail domain, not a subdomain of indeed.com
)

_TAG_RE = re.compile(r"<[^>]+>")


def sender_domain(from_header: str | None) -> str:
    """Return the lowercased domain of the address in a `From` header.

    Parses the RFC 5322 address, so a spoofed display name ("Indeed"
    <alerts@evil.com>) is ignored. Returns "" when no domain can be read.
    """
    _, address = parseaddr(from_header or "")
    _, at, domain = address.rpartition("@")
    if not at:
        return ""
    return domain.strip().strip(".").casefold()


def sender_allowed(from_header: str | None, domains: Sequence[str]) -> bool:
    """True when the From address sits on one of `domains` or a subdomain of it."""
    domain = sender_domain(from_header)
    if not domain:
        return False
    return any(
        domain == allowed or domain.endswith(f".{allowed}")
        for allowed in (d.casefold().strip(".") for d in domains)
    )


def _strip_tags(html: str) -> str:
    return " ".join(unescape(_TAG_RE.sub(" ", html)).split())


# ---- IMAP transport (injectable for tests) ----


class GmailIMAP:
    """Minimal read-only Gmail IMAP client."""

    def __init__(
        self,
        address: str,
        app_password: str,
        host: str = "imap.gmail.com",
        port: int = 993,
        folder: str = "INBOX",
        redact: Callable[[str], str] | None = None,
    ) -> None:
        self._address = address
        self._password = app_password
        self._host = host
        self._port = port
        self._folder = folder
        self._redact = redact or (lambda text: text)

    def fetch_from(self, domains: Sequence[str], since_days: int) -> list[Message]:
        """Fetch recent mail sent from `domains` (or any of their subdomains).

        The IMAP `FROM` search is a substring match on the header, which both
        over-matches (notlinkedin.com contains linkedin.com) and cannot express
        "or a subdomain of", so every candidate is re-checked locally against
        `sender_allowed` before it is returned.
        """
        since = (datetime.now(UTC) - timedelta(days=since_days)).strftime("%d-%b-%Y")
        conn: imaplib.IMAP4_SSL | None = None
        try:
            conn = imaplib.IMAP4_SSL(self._host, self._port)
            conn.login(self._address, self._password)
            status, _ = conn.select(self._folder, readonly=True)
            if status != "OK":
                raise EmailAlertError(f"cannot select IMAP folder {self._folder!r}")
            messages: list[Message] = []
            fetched_ids: set[bytes] = set()
            for domain in domains:
                typ, data = conn.search(None, "FROM", f'"{domain}"', "SINCE", since)
                if typ != "OK" or not data or not data[0]:
                    continue
                for num in data[0].split():
                    if num in fetched_ids:
                        continue
                    fetched_ids.add(num)
                    typ, msg_data = conn.fetch(num, "(BODY.PEEK[])")
                    if typ != "OK" or not msg_data or not msg_data[0]:
                        continue
                    raw = next(
                        (
                            item[1]
                            for item in msg_data
                            if isinstance(item, tuple)
                            and len(item) > 1
                            and isinstance(item[1], bytes)
                        ),
                        None,
                    )
                    if raw is None:
                        log.warning("IMAP message %r had no RFC822 payload", num)
                        continue
                    msg = email.message_from_bytes(raw)
                    if not sender_allowed(msg.get("From"), domains):
                        log.debug(
                            "ignoring IMAP message %r: sender domain %r not allowed",
                            num,
                            sender_domain(msg.get("From")),
                        )
                        continue
                    messages.append(msg)
            return messages
        except EmailAlertError:
            raise
        except Exception as exc:
            detail = self._redact(str(exc))
            raise EmailAlertError(f"IMAP alert fetch failed: {detail}") from exc
        finally:
            if conn is not None:
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


@dataclass
class _AlertAnchor:
    href: str
    text: str
    context: tuple[str, ...] = ()


@dataclass
class _TextContainer:
    tag: str
    chunks: list[str]
    anchors: list[_AlertAnchor]


class _AnchorParser(HTMLParser):
    """Collect anchors plus nearby table/list-card text without dependencies."""

    def __init__(self) -> None:
        super().__init__()
        self.anchors: list[_AlertAnchor] = []
        self._href: str | None = None
        self._text: list[str] = []
        self._containers: list[_TextContainer] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"td", "tr", "li", "article"}:
            self._containers.append(_TextContainer(tag, [], []))
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_data(self, data: str) -> None:
        cleaned = " ".join(data.split())
        if cleaned:
            for container in self._containers:
                container.chunks.append(cleaned)
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._href is not None:
            anchor = _AlertAnchor(
                self._href,
                " ".join(" ".join(self._text).split()),
            )
            self.anchors.append(anchor)
            for container in self._containers:
                container.anchors.append(anchor)
            self._href = None
            self._text = []
        if tag in {"td", "tr", "li", "article"}:
            self._close_container(tag)

    def finish(self) -> None:
        while self._containers:
            self._close_container(self._containers[-1].tag)

    def _close_container(self, tag: str) -> None:
        for index in range(len(self._containers) - 1, -1, -1):
            if self._containers[index].tag != tag:
                continue
            container = self._containers.pop(index)
            context = tuple(container.chunks)
            if len(context) > 1:
                for anchor in container.anchors:
                    if not anchor.context:
                        anchor.context = context
            return


def _anchors(html: str) -> list[_AlertAnchor]:
    p = _AnchorParser()
    p.feed(html)
    p.finish()
    return p.anchors


# ---- provider parsers (pure, fixture-tested) ----

_LINKEDIN_ID_RE = re.compile(r"/jobs/view/(\d+)")
_INDEED_JK_RE = re.compile(r"[?&]jk=([0-9a-f]+)")
_CTA_TEXT = {
    "apply",
    "postuler",
    "see job",
    "view job",
    "voir l'offre",
    "voir le poste",
}


def clean_job_url(url: str, provider: str) -> str:
    """Return a stable detail URL with email/tracking parameters removed."""

    raw = unescape(url).strip()
    if provider == "linkedin":
        match = _LINKEDIN_ID_RE.search(raw)
        if match:
            return f"https://www.linkedin.com/jobs/view/{match.group(1)}"
    if provider == "indeed":
        query = parse_qs(urlsplit(raw).query)
        job_keys = query.get("jk")
        if job_keys and job_keys[0]:
            return "https://fr.indeed.com/viewjob?" + urlencode({"jk": job_keys[0]})

    parsed = urlsplit(raw)
    kept = []
    for key, values in parse_qs(parsed.query, keep_blank_values=True).items():
        normalized = key.casefold()
        if normalized.startswith("utm_") or normalized in {
            "trk",
            "trackingid",
            "refid",
            "midtoken",
            "from",
            "tk",
            "advn",
        }:
            continue
        kept.extend((key, value) for value in values)
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(kept), parsed.fragment))


def parse_linkedin(html: str) -> list[OfferRecord]:
    """Extract jobs from a LinkedIn job-alert email."""
    out: list[OfferRecord] = []
    seen: set[str] = set()
    for anchor in _anchors(html):
        match = _LINKEDIN_ID_RE.search(anchor.href)
        if not match or not anchor.text:
            continue
        job_id = match.group(1)
        if job_id in seen:
            continue
        seen.add(job_id)
        title, company, city, description = _card_fields(anchor)
        out.append(
            OfferRecord(
                external_id=job_id,
                url=clean_job_url(anchor.href, "linkedin"),
                title=title,
                company_name=company,
                city=city,
                description=description,
                contract_type="unknown",
            ).normalized()
        )
    return out


def parse_indeed(html: str) -> list[OfferRecord]:
    """Extract jobs from an Indeed job-alert email."""
    out: list[OfferRecord] = []
    seen: set[str] = set()
    for anchor in _anchors(html):
        match = _INDEED_JK_RE.search(anchor.href)
        if not match or not anchor.text:
            continue
        jk = match.group(1)
        if jk in seen:
            continue
        seen.add(jk)
        title, company, city, description = _card_fields(anchor)
        out.append(
            OfferRecord(
                external_id=jk,
                url=clean_job_url(anchor.href, "indeed"),
                title=title,
                company_name=company,
                city=city,
                description=description,
                contract_type="unknown",
            ).normalized()
        )
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


def _card_fields(
    anchor: _AlertAnchor,
) -> tuple[str, str | None, str | None, str | None]:
    title, company, city = _split_card(anchor.text)
    details: list[str] = []
    for chunk in anchor.context:
        cleaned = " ".join(chunk.split())
        if (
            not cleaned
            or cleaned == anchor.text
            or cleaned.casefold() in _CTA_TEXT
            or cleaned in details
        ):
            continue
        details.append(cleaned)
    if company is None and details:
        company = details.pop(0)
    if city is None and details:
        city = details.pop(0)
    description = " ".join(details) if details else None
    return title, company, city, description


# ---- Source implementations ----


class _EmailAlertSource(Source):
    sender_domains: tuple[str, ...] = ()
    provider = "unknown"

    def __init__(
        self,
        settings: Settings,
        *,
        imap: GmailIMAP | None = None,
        since_days: int | None = None,
    ) -> None:
        address, password = settings.require_gmail_credentials()
        self._settings = settings
        self._imap = imap or GmailIMAP(
            address,
            password,
            host=settings.imap_host,
            port=settings.imap_port,
            folder=settings.imap_folder,
            redact=settings.redact,
        )
        self._since_days = since_days if since_days is not None else settings.email_alert_since_days
        self._min_description_chars = settings.alert_min_description_chars

    def _parse(self, html: str) -> list[OfferRecord]:  # overridden
        raise NotImplementedError

    def fetch_offers(self) -> Iterator[OfferRecord]:
        try:
            messages = self._imap.fetch_from(self.sender_domains, self._since_days)
        except EmailAlertError:
            raise
        except Exception as exc:
            detail = self._settings.redact(str(exc))
            raise EmailAlertError(f"IMAP alert fetch failed: {detail}") from exc

        emails_scanned = 0
        entries_found = 0
        seen: set[str] = set()
        for msg in messages:
            emails_scanned += 1
            try:
                records = self._parse(html_of(msg))
            except Exception as exc:
                log.warning(
                    "skipping malformed %s alert: %s",
                    self.provider,
                    self._settings.redact(str(exc)),
                )
                continue
            if not records:
                # Expected, not exceptional: domain matching also lets through
                # non-job mail from the provider ("Terms of Service Updates"),
                # which simply yields nothing. Warn and move on.
                log.warning(
                    "skipping %s email with no job entries",
                    self.provider,
                )
                continue
            entries_found += len(records)
            for rec in records:
                # Synthesise before the key/hash is read: the stored row, its
                # content_hash and the text matcher.py embeds must all agree.
                enrich_offer(rec, self._min_description_chars)
                key = rec.external_id or rec.hash
                if key in seen:
                    continue
                seen.add(key)
                yield rec
        log.info(
            "email alerts provider=%s emails_scanned=%d entries_found=%d unique_entries=%d",
            self.provider,
            emails_scanned,
            entries_found,
            len(seen),
        )


class LinkedInAlertSource(_EmailAlertSource):
    name = "linkedin_alert"
    provider = "linkedin"
    sender_domains = LINKEDIN_DOMAINS

    def _parse(self, html: str) -> list[OfferRecord]:
        return parse_linkedin(html)


class IndeedAlertSource(_EmailAlertSource):
    name = "indeed_alert"
    provider = "indeed"
    sender_domains = INDEED_DOMAINS

    def _parse(self, html: str) -> list[OfferRecord]:
        return parse_indeed(html)
