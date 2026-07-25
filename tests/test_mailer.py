"""Application email sending: rails, transitions, and events (mocked SMTP)."""

from __future__ import annotations

import dataclasses
import hashlib
import json
import sqlite3
from datetime import UTC, datetime
from email.message import EmailMessage
from pathlib import Path

import pytest

from jobpilot.config import get_settings
from jobpilot.contacts import MAX_PER_DAY, suppress_email
from jobpilot.mailer import (
    MailerError,
    SendBlocked,
    mark_application_sent,
    prepare_application_email,
    send_application_email,
    sends_today,
)
from jobpilot.state import current_status


def _settings_with_smtp():
    return dataclasses.replace(
        get_settings(),
        smtp_username="me@sender.example",
        smtp_password="app-secret-pw",
        smtp_from_name="Mouaad Sekkouri",
    )


def _ready_app(
    db: sqlite3.Connection,
    output_root: Path,
    *,
    contact_email: str | None = "recrutement@acme.example",
    title: str = "Analyste SOC",
    with_files: bool = True,
) -> int:
    source_id = db.execute(
        "SELECT id FROM sources WHERE name = 'france_travail'"
    ).fetchone()["id"]
    company_id = db.execute(
        "INSERT INTO companies (name, city) VALUES ('Acme', 'Paris')"
    ).lastrowid
    digest = hashlib.sha256(f"mailer-{title}-{contact_email}".encode()).hexdigest()
    offer_id = db.execute(
        "INSERT INTO offers (source_id, company_id, external_id, url, title, "
        "description, contract_type, city, content_hash, contact_email) "
        "VALUES (?, ?, ?, ?, ?, 'desc', 'alternance', 'Paris', ?, ?)",
        (source_id, company_id, f"ext-{digest[:8]}",
         "https://example.test/1", title, digest, contact_email),
    ).lastrowid
    application_id = int(
        db.execute(
            "INSERT INTO applications (offer_id, company_id, kind, status) "
            "VALUES (?, ?, 'offer', 'ready')",
            (offer_id, company_id),
        ).lastrowid
    )
    db.commit()
    if with_files:
        app_dir = output_root / str(application_id)
        app_dir.mkdir(parents=True, exist_ok=True)
        (app_dir / "cv.pdf").write_bytes(b"%PDF-cv")
        (app_dir / "motivation_letter.pdf").write_bytes(b"%PDF-letter")
    return application_id


class _Sender:
    def __init__(self, *, message_id: str = "<abc@test>", error: Exception | None = None):
        self.message_id = message_id
        self.error = error
        self.sent: EmailMessage | None = None

    def send(self, message: EmailMessage) -> str:
        self.sent = message
        if self.error is not None:
            raise self.error
        return self.message_id


def _events(db: sqlite3.Connection, application_id: int) -> list[str]:
    return [
        row["event"]
        for row in db.execute(
            "SELECT event FROM events WHERE application_id = ? ORDER BY id",
            (application_id,),
        ).fetchall()
    ]


def test_successful_send_transitions_ready_to_applied_and_logs_event(
    db: sqlite3.Connection, tmp_path: Path
) -> None:
    app_id = _ready_app(db, tmp_path)
    sender = _Sender(message_id="<msg-1@test>")

    message_id = send_application_email(
        db, app_id, sender=sender, output_root=tmp_path,
        settings=_settings_with_smtp(),
    )

    assert message_id == "<msg-1@test>"
    assert current_status(db, app_id) == "applied"
    assert _events(db, app_id) == ["status_change", "application_sent"]
    sent_detail = json.loads(
        db.execute(
            "SELECT detail FROM events WHERE application_id = ? "
            "AND event = 'application_sent'",
            (app_id,),
        ).fetchone()["detail"]
    )
    assert sent_detail["recipient"] == "recrutement@acme.example"
    assert sent_detail["message_id"] == "<msg-1@test>"
    assert "Candidature" in sent_detail["subject"]
    # Two PDF attachments were attached to the outgoing message.
    assert sender.sent is not None
    filenames = {part.get_filename() for part in sender.sent.iter_attachments()}
    assert filenames == {"cv.pdf", "motivation_letter.pdf"}
    assert sends_today(db) == 1


def test_smtp_failure_keeps_ready_and_logs_send_failed(
    db: sqlite3.Connection, tmp_path: Path
) -> None:
    app_id = _ready_app(db, tmp_path)
    sender = _Sender(error=OSError("connection refused for app-secret-pw"))

    with pytest.raises(MailerError) as exc_info:
        send_application_email(
            db, app_id, sender=sender, output_root=tmp_path,
            settings=_settings_with_smtp(),
        )

    # Password must be redacted from the surfaced error.
    assert "app-secret-pw" not in str(exc_info.value)
    assert current_status(db, app_id) == "ready"
    assert _events(db, app_id) == ["send_failed"]
    assert sends_today(db) == 0


def test_daily_cap_refuses_send(db: sqlite3.Connection, tmp_path: Path) -> None:
    app_id = _ready_app(db, tmp_path)
    now = datetime.now(UTC).isoformat()
    for _ in range(MAX_PER_DAY):
        db.execute(
            "INSERT INTO events (application_id, event, detail, created_at) "
            "VALUES (?, 'application_sent', '{}', ?)",
            (app_id, now),
        )
    db.commit()

    assert prepare_application_email(
        db, app_id, output_root=tmp_path
    ).blocked_reason is not None
    with pytest.raises(SendBlocked, match="cap"):
        send_application_email(
            db, app_id, sender=_Sender(), output_root=tmp_path,
            settings=_settings_with_smtp(),
        )
    assert current_status(db, app_id) == "ready"


def test_suppression_refuses_send(db: sqlite3.Connection, tmp_path: Path) -> None:
    app_id = _ready_app(db, tmp_path, contact_email="rh@blocked.example")
    suppress_email(db, "rh@blocked.example", "opted out")

    prep = prepare_application_email(db, app_id, output_root=tmp_path)
    assert prep.blocked_reason is not None and "suppression" in prep.blocked_reason
    with pytest.raises(SendBlocked, match="suppression"):
        send_application_email(
            db, app_id, sender=_Sender(), output_root=tmp_path,
            settings=_settings_with_smtp(),
        )
    assert current_status(db, app_id) == "ready"


def test_mark_sent_records_manual_application_sent_without_counting(
    db: sqlite3.Connection, tmp_path: Path
) -> None:
    app_id = _ready_app(db, tmp_path, contact_email=None)

    mark_application_sent(db, app_id)

    assert current_status(db, app_id) == "applied"
    assert _events(db, app_id) == ["status_change", "application_sent"]
    detail = json.loads(
        db.execute(
            "SELECT detail FROM events WHERE application_id = ? "
            "AND event = 'application_sent'",
            (app_id,),
        ).fetchone()["detail"]
    )
    assert detail == {"via": "manual"}
    # A manual mark does not dispatch an email, so it must not consume the cap.
    assert sends_today(db) == 0


def test_send_requires_ready_state(db: sqlite3.Connection, tmp_path: Path) -> None:
    app_id = _ready_app(db, tmp_path)
    mark_application_sent(db, app_id)  # now 'applied'
    with pytest.raises(MailerError, match="ready"):
        send_application_email(
            db, app_id, sender=_Sender(), output_root=tmp_path,
            settings=_settings_with_smtp(),
        )
