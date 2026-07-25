"""Send a ready application by email, after explicit human confirmation.

Two-step by construction: :func:`prepare_application_email` builds exactly what
would be sent (recipient, subject, editable body, attachments) and reports any
rail that blocks it; :func:`send_application_email` performs the SMTP send and,
only on success, records the state transition and the ``application_sent`` event.

Rails are shared with cold mail (constitution): the global >=25 sends/day counter
(applications + cold mail combined) and the suppression list are checked before
every send. No stagger is needed for a human-clicked single send.
"""

from __future__ import annotations

import json
import smtplib
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from email.message import EmailMessage
from email.utils import formataddr, make_msgid
from pathlib import Path
from typing import Protocol

from jobpilot.config import Settings, get_settings
from jobpilot.contacts import MAX_PER_DAY, is_suppressed
from jobpilot.logging_conf import get_logger
from jobpilot.state import current_status, log_event, transition
from jobpilot.tailoring import french_de_elision

log = get_logger("mailer")

CV_ATTACHMENT = "cv.pdf"
LETTER_ATTACHMENT = "motivation_letter.pdf"


class MailerError(RuntimeError):
    """A send could not be attempted or completed (redacted for display)."""


class SendBlocked(MailerError):
    """A rail (suppression list or daily cap) refuses the send. Not a failure."""


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


class EmailSender(Protocol):
    """Transmits a built message and returns its Message-ID."""

    def send(self, message: EmailMessage) -> str: ...


@dataclass(frozen=True)
class SmtpSender:
    """Default STARTTLS SMTP sender built from settings."""

    host: str
    port: int
    username: str
    password: str

    def send(self, message: EmailMessage) -> str:
        with smtplib.SMTP(self.host, self.port, timeout=30) as smtp:
            smtp.starttls()
            smtp.login(self.username, self.password)
            smtp.send_message(message)
        return message["Message-ID"]


def build_sender(settings: Settings | None = None) -> SmtpSender:
    settings = settings or get_settings()
    host, port, username, password, _ = settings.require_smtp_credentials()
    return SmtpSender(host=host, port=port, username=username, password=password)


@dataclass(frozen=True)
class EmailPreparation:
    """Everything a confirmation step needs to show before sending."""

    application_id: int
    recipient: str
    subject: str
    body: str
    attachments: tuple[Path, ...]
    blocked_reason: str | None  # None means the rails allow the send


def sends_today(db: sqlite3.Connection, now: datetime | None = None) -> int:
    """Combined application + cold-mail sends recorded for today (UTC)."""

    day = (now or datetime.now(UTC)).date().isoformat()
    cold = db.execute(
        "SELECT count(*) AS n FROM email_queue "
        "WHERE sent_at IS NOT NULL AND substr(sent_at, 1, 10) = ?",
        (day,),
    ).fetchone()["n"]
    rows = db.execute(
        "SELECT detail FROM events WHERE event = 'application_sent' "
        "AND substr(created_at, 1, 10) = ?",
        (day,),
    ).fetchall()
    emails = 0
    for row in rows:
        try:
            detail = json.loads(row["detail"] or "{}")
        except (TypeError, json.JSONDecodeError):
            detail = {}
        # A manual "mark as sent" does not dispatch an email, so it does not count.
        if detail.get("via") != "manual":
            emails += 1
    return cold + emails


def daily_cap_reached(db: sqlite3.Connection, now: datetime | None = None) -> bool:
    return sends_today(db, now) >= MAX_PER_DAY


def _load_ready_offer_application(
    db: sqlite3.Connection, application_id: int
) -> sqlite3.Row:
    row = db.execute(
        "SELECT a.id, a.kind, a.status, o.title, o.contact_email "
        "FROM applications a LEFT JOIN offers o ON o.id = a.offer_id "
        "WHERE a.id = ?",
        (application_id,),
    ).fetchone()
    if row is None:
        raise MailerError(f"no application with id={application_id}")
    if row["kind"] != "offer":
        raise MailerError("email sending is only available for offer applications")
    return row


def _subject(title: str | None, from_name: str) -> str:
    return f"Candidature — {title or 'votre offre'} — {from_name}"


def _default_body(title: str | None, from_name: str) -> str:
    poste = f"le poste {french_de_elision(title)}" if title else "votre offre"
    return (
        "Madame, Monsieur,\n\n"
        f"Je vous adresse ma candidature pour {poste}. Vous trouverez ci-joint "
        "mon CV ainsi que ma lettre de motivation, qui détaillent mon parcours "
        "et ma motivation.\n\n"
        "Je me tiens à votre disposition pour un échange à votre convenance.\n\n"
        f"Cordialement,\n{from_name}"
    )


def prepare_application_email(
    db: sqlite3.Connection,
    application_id: int,
    *,
    output_root: Path | None = None,
    settings: Settings | None = None,
    now: datetime | None = None,
) -> EmailPreparation:
    """Build the exact email and report the first blocking rail, if any."""

    settings = settings or get_settings()
    from_name = settings.smtp_from_name
    row = _load_ready_offer_application(db, application_id)
    recipient = (row["contact_email"] or "").strip()
    root = Path(output_root or settings.output_dir) / str(application_id)
    attachments = (root / CV_ATTACHMENT, root / LETTER_ATTACHMENT)

    blocked: str | None = None
    if not recipient:
        blocked = "no contact email on this offer"
    elif is_suppressed(db, recipient):
        blocked = f"{recipient} is on the suppression list"
    elif daily_cap_reached(db, now):
        blocked = f"daily send cap reached ({MAX_PER_DAY} emails today)"

    return EmailPreparation(
        application_id=application_id,
        recipient=recipient,
        subject=_subject(row["title"], from_name),
        body=_default_body(row["title"], from_name),
        attachments=attachments,
        blocked_reason=blocked,
    )


def _build_message(
    settings: Settings,
    *,
    recipient: str,
    subject: str,
    body: str,
    attachments: tuple[Path, ...],
) -> EmailMessage:
    _, _, username, _, from_name = settings.require_smtp_credentials()
    message = EmailMessage()
    message["From"] = formataddr((from_name, username))
    message["To"] = recipient
    message["Subject"] = subject
    message["Message-ID"] = make_msgid()
    message.set_content(body)
    for path in attachments:
        message.add_attachment(
            path.read_bytes(),
            maintype="application",
            subtype="pdf",
            filename=path.name,
        )
    return message


def send_application_email(
    db: sqlite3.Connection,
    application_id: int,
    *,
    body: str | None = None,
    sender: EmailSender | None = None,
    output_root: Path | None = None,
    settings: Settings | None = None,
    now: datetime | None = None,
) -> str:
    """Send the application by email, then transition ready -> applied.

    Returns the Message-ID. Raises :class:`SendBlocked` (rails) before any send,
    or :class:`MailerError` (redacted) if the SMTP send fails, in which case the
    application stays ``ready`` and a ``send_failed`` event is logged.
    """

    settings = settings or get_settings()
    if current_status(db, application_id) != "ready":
        raise MailerError("application must be in 'ready' state to send")
    prep = prepare_application_email(
        db, application_id, output_root=output_root, settings=settings, now=now
    )
    if prep.blocked_reason:
        raise SendBlocked(prep.blocked_reason)
    for path in prep.attachments:
        if not path.is_file():
            raise MailerError(f"missing attachment: {path.name}")

    chosen_sender = sender or build_sender(settings)
    message = _build_message(
        settings,
        recipient=prep.recipient,
        subject=prep.subject,
        body=body if body is not None else prep.body,
        attachments=prep.attachments,
    )
    try:
        message_id = chosen_sender.send(message)
    except Exception as exc:
        detail = settings.redact(str(exc))
        log_event(
            db,
            application_id,
            "send_failed",
            {"recipient": prep.recipient, "error": detail},
        )
        log.warning("application %d send failed", application_id)
        raise MailerError(f"email send failed: {detail}") from exc

    transition(db, application_id, "applied", detail={"channel": "email"})
    db.execute(
        "UPDATE applications SET applied_at = ? WHERE id = ?",
        (_utc_now(), application_id),
    )
    db.commit()
    log_event(
        db,
        application_id,
        "application_sent",
        {
            "recipient": prep.recipient,
            "subject": prep.subject,
            "message_id": message_id,
        },
    )
    log.info("application %d sent to %s", application_id, prep.recipient)
    return message_id


def mark_application_sent(db: sqlite3.Connection, application_id: int) -> None:
    """Manual fallback: record an externally-submitted application as sent."""

    if current_status(db, application_id) != "ready":
        raise MailerError("application must be in 'ready' state to mark as sent")
    transition(db, application_id, "applied", detail={"via": "manual"})
    db.execute(
        "UPDATE applications SET applied_at = ? WHERE id = ?",
        (_utc_now(), application_id),
    )
    db.commit()
    log_event(db, application_id, "application_sent", {"via": "manual"})
    log.info("application %d marked sent (manual)", application_id)
