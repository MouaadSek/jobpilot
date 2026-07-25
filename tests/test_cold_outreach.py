"""Cold outreach dispatch rails and two-step dashboard workflow."""

from __future__ import annotations

import dataclasses
import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from email.message import EmailMessage

import pytest
from fastapi.testclient import TestClient

from jobpilot.apply_flow import APPLICATION_LOCK
from jobpilot.config import get_settings
from jobpilot.contacts import (
    MAX_PER_DAY,
    OPT_OUT_LINE,
    requires_personal_confirmation,
    suppress_email,
)
from jobpilot.dashboard import create_app, database_connection
from jobpilot.mailer import (
    ColdSendDisabled,
    MailerError,
    SendBlocked,
    prepare_cold_email,
    send_cold_email,
    sends_today,
)
from jobpilot.state import current_status, log_event

NOW = datetime(2026, 7, 25, 8, 0, tzinfo=UTC)


def _settings(*, enabled: bool) -> object:
    return dataclasses.replace(
        get_settings(),
        smtp_username="mouaad@sender.example",
        smtp_password="smtp-test-secret",
        smtp_from_name="Mouaad Sekkouri",
        cold_send_enabled=enabled,
    )


def _cold_draft(
    db: sqlite3.Connection,
    *,
    recipient: str = "recrutement@acme.example",
    status: str = "generating",
    approved: bool = True,
    subject: str = "Candidature spontanée — Analyste SOC",
) -> tuple[int, int]:
    company_id = db.execute(
        "INSERT INTO companies (name) VALUES ('Acme Cyber')"
    ).lastrowid
    application_id = int(
        db.execute(
            "INSERT INTO applications "
            "(company_id, kind, status, contact_email, contact_name) "
            "VALUES (?, 'cold', ?, ?, 'Jean Dupont')",
            (company_id, status, recipient),
        ).lastrowid
    )
    if approved:
        log_event(
            db,
            application_id,
            "human_approved",
            {"via": "test"},
        )
    queue_id = int(
        db.execute(
            "INSERT INTO email_queue "
            "(application_id, to_email, subject, body, scheduled_at, kind) "
            "VALUES (?, ?, ?, 'Bonjour Jean,\\n\\nMessage de test.', ?, 'initial')",
            (application_id, recipient, subject, NOW.isoformat()),
        ).lastrowid
    )
    db.commit()
    return application_id, queue_id


class _Sender:
    def __init__(
        self,
        *,
        message_id: str = "<cold-test@example>",
        error: Exception | None = None,
    ) -> None:
        self.message_id = message_id
        self.error = error
        self.sent: EmailMessage | None = None

    def send(self, message: EmailMessage) -> str:
        self.sent = message
        if self.error is not None:
            raise self.error
        return self.message_id


def _event_rows(
    db: sqlite3.Connection,
    application_id: int,
) -> list[sqlite3.Row]:
    return db.execute(
        "SELECT event, detail FROM events WHERE application_id = ? ORDER BY id",
        (application_id,),
    ).fetchall()


def test_cold_send_flag_defaults_to_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from jobpilot import config

    monkeypatch.delenv("COLD_SEND_ENABLED", raising=False)
    config.get_settings.cache_clear()
    try:
        assert config.get_settings().cold_send_enabled is False
    finally:
        config.get_settings.cache_clear()


def test_cold_send_disabled_blocks_smtp_and_logs_safe_failure(
    db: sqlite3.Connection,
) -> None:
    application_id, queue_id = _cold_draft(db)
    sender = _Sender()

    prep = prepare_cold_email(db, queue_id, now=NOW)
    assert prep.blocked_reason is None
    with pytest.raises(ColdSendDisabled, match="cold sending is disabled"):
        send_cold_email(
            db,
            queue_id,
            sender=sender,
            settings=_settings(enabled=False),
            now=NOW,
        )

    assert sender.sent is None
    assert current_status(db, application_id) == "generating"
    failure = _event_rows(db, application_id)[-1]
    assert failure["event"] == "cold_send_failed"
    detail = json.loads(failure["detail"])
    assert detail["recipient"] == "recrutement@acme.example"
    assert detail["subject"] == prep.subject


def test_enabled_cold_send_appends_footer_marks_sent_and_transitions(
    db: sqlite3.Connection,
) -> None:
    application_id, queue_id = _cold_draft(db)
    sender = _Sender()

    message_id = send_cold_email(
        db,
        queue_id,
        body="Bonjour Jean,\n\nJe souhaite échanger avec vous.",
        sender=sender,
        settings=_settings(enabled=True),
        now=NOW,
    )

    assert message_id == "<cold-test@example>"
    assert sender.sent is not None
    assert OPT_OUT_LINE in sender.sent.get_content()
    stored = db.execute(
        "SELECT sent_at, body, subject FROM email_queue WHERE id = ?",
        (queue_id,),
    ).fetchone()
    assert stored["sent_at"] == NOW.isoformat()
    assert OPT_OUT_LINE in stored["body"]
    assert current_status(db, application_id) == "applied"
    events = _event_rows(db, application_id)
    assert [row["event"] for row in events][-3:] == [
        "status_change",
        "status_change",
        "cold_mail_sent",
    ]
    sent_detail = json.loads(events[-1]["detail"])
    assert sent_detail["recipient"] == "recrutement@acme.example"
    assert sent_detail["subject"] == stored["subject"]


def test_suppression_is_rechecked_at_cold_send_time(
    db: sqlite3.Connection,
) -> None:
    application_id, queue_id = _cold_draft(db, recipient="rh@acme.example")
    suppress_email(db, "rh@acme.example", "asked to stop")
    sender = _Sender()

    assert "suppression" in (prepare_cold_email(db, queue_id, now=NOW).blocked_reason or "")
    with pytest.raises(SendBlocked, match="suppression"):
        send_cold_email(
            db,
            queue_id,
            sender=sender,
            settings=_settings(enabled=True),
            now=NOW,
        )

    assert sender.sent is None
    assert current_status(db, application_id) == "generating"
    assert _event_rows(db, application_id)[-1]["event"] == "cold_send_failed"


def test_personal_looking_professional_address_needs_extra_confirmation(
    db: sqlite3.Connection,
) -> None:
    application_id, queue_id = _cold_draft(
        db,
        recipient="jean.dupont@acme.example",
    )
    sender = _Sender()

    assert requires_personal_confirmation("recrutement@acme.example") is False
    assert requires_personal_confirmation("jean.dupont@acme.example") is True
    with pytest.raises(SendBlocked, match="personal-address confirmation"):
        send_cold_email(
            db,
            queue_id,
            sender=sender,
            settings=_settings(enabled=True),
            now=NOW,
        )
    assert sender.sent is None

    send_cold_email(
        db,
        queue_id,
        personal_address_confirmed=True,
        sender=sender,
        settings=_settings(enabled=True),
        now=NOW,
    )
    assert sender.sent is not None
    assert current_status(db, application_id) == "applied"


def test_shared_daily_cap_counts_application_and_cold_email_sends(
    db: sqlite3.Connection,
) -> None:
    prior_app, prior_queue = _cold_draft(
        db,
        recipient="rh@prior.example",
        status="applied",
    )
    db.execute(
        "UPDATE email_queue SET sent_at = ? WHERE id = ?",
        (NOW.isoformat(), prior_queue),
    )
    for _ in range(MAX_PER_DAY - 1):
        db.execute(
            "INSERT INTO events (application_id, event, detail, created_at) "
            "VALUES (?, 'application_sent', '{}', ?)",
            (prior_app, NOW.isoformat()),
        )
    db.commit()
    application_id, queue_id = _cold_draft(
        db,
        recipient="rh@next.example",
    )

    assert sends_today(db, NOW) == MAX_PER_DAY
    prep = prepare_cold_email(db, queue_id, now=NOW)
    assert prep.blocked_reason == f"daily send cap reached ({MAX_PER_DAY} emails today)"
    with pytest.raises(SendBlocked, match="daily send cap"):
        send_cold_email(
            db,
            queue_id,
            sender=_Sender(),
            settings=_settings(enabled=True),
            now=NOW,
        )
    assert current_status(db, application_id) == "generating"


def test_cold_send_stagger_reports_exact_retry_time(
    db: sqlite3.Connection,
) -> None:
    _, prior_queue = _cold_draft(
        db,
        recipient="rh@prior.example",
        status="applied",
    )
    db.execute(
        "UPDATE email_queue SET sent_at = ? WHERE id = ?",
        (NOW.isoformat(), prior_queue),
    )
    db.commit()
    _, queue_id = _cold_draft(db, recipient="rh@next.example")
    too_soon = NOW + timedelta(minutes=3)

    prep = prepare_cold_email(db, queue_id, now=too_soon)
    assert prep.blocked_reason == "cold-send stagger active; retry at 08:04 UTC"
    with pytest.raises(SendBlocked, match="retry at 08:04"):
        send_cold_email(
            db,
            queue_id,
            sender=_Sender(),
            settings=_settings(enabled=True),
            now=too_soon,
        )


def test_cold_send_requires_recorded_human_approval(
    db: sqlite3.Connection,
) -> None:
    _, queue_id = _cold_draft(db, approved=False)
    sender = _Sender()

    with pytest.raises(SendBlocked, match="human approval"):
        send_cold_email(
            db,
            queue_id,
            sender=sender,
            settings=_settings(enabled=True),
            now=NOW,
        )

    assert sender.sent is None


def test_smtp_failure_is_redacted_and_retryable(
    db: sqlite3.Connection,
) -> None:
    application_id, queue_id = _cold_draft(db)
    sender = _Sender(error=OSError("failed with smtp-test-secret"))

    with pytest.raises(MailerError) as exc_info:
        send_cold_email(
            db,
            queue_id,
            sender=sender,
            settings=_settings(enabled=True),
            now=NOW,
        )

    assert "smtp-test-secret" not in str(exc_info.value)
    assert current_status(db, application_id) == "ready"
    assert _event_rows(db, application_id)[-1]["event"] == "cold_send_failed"
    assert db.execute(
        "SELECT sent_at FROM email_queue WHERE id = ?",
        (queue_id,),
    ).fetchone()["sent_at"] is None


@contextmanager
def _dashboard_client(
    db: sqlite3.Connection,
    *,
    sender: _Sender | None = None,
) -> Iterator[TestClient]:
    app = create_app(sender=sender)

    def in_memory_connection() -> Iterator[sqlite3.Connection]:
        with APPLICATION_LOCK:
            yield db

    app.dependency_overrides[database_connection] = in_memory_connection
    with TestClient(app) as client:
        yield client


def _configure_dashboard(
    monkeypatch: pytest.MonkeyPatch,
    *,
    enabled: bool,
) -> None:
    from jobpilot import config

    monkeypatch.setenv("SMTP_USERNAME", "mouaad@sender.example")
    monkeypatch.setenv("SMTP_PASSWORD", "smtp-test-secret")
    monkeypatch.setenv("COLD_SEND_ENABLED", "true" if enabled else "false")
    config.get_settings.cache_clear()


def test_dashboard_outreach_tab_lists_drafts_and_opens_confirmation(
    dashboard_db: sqlite3.Connection,
) -> None:
    _, queue_id = _cold_draft(
        dashboard_db,
        status="queued",
        approved=False,
    )

    with _dashboard_client(dashboard_db) as client:
        queue_page = client.get("/")
        outreach = client.get("/outreach")
        confirmation = client.get(f"/outreach/{queue_id}")

    assert 'href="/outreach"' in queue_page.text
    assert outreach.status_code == 200
    assert "recrutement@acme.example" in outreach.text
    assert f'href="/outreach/{queue_id}"' in outreach.text
    assert confirmation.status_code == 200
    assert 'name="body"' in confirmation.text
    assert OPT_OUT_LINE in confirmation.text
    assert f'action="/outreach/{queue_id}/send"' in confirmation.text
    assert "Confirmer et envoyer" in confirmation.text


def test_dashboard_flag_off_records_approval_but_never_calls_smtp(
    dashboard_db: sqlite3.Connection,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    application_id, queue_id = _cold_draft(
        dashboard_db,
        status="queued",
        approved=False,
    )
    sender = _Sender()
    _configure_dashboard(monkeypatch, enabled=False)
    try:
        with _dashboard_client(dashboard_db, sender=sender) as client:
            response = client.post(
                f"/outreach/{queue_id}/send",
                data={"body": "Bonjour Jean"},
            )
    finally:
        get_settings.cache_clear()

    assert response.status_code == 409
    assert "cold sending is disabled" in response.text
    assert sender.sent is None
    assert current_status(dashboard_db, application_id) == "generating"
    assert [row["event"] for row in _event_rows(dashboard_db, application_id)] == [
        "human_approved",
        "status_change",
        "cold_send_failed",
    ]


def test_dashboard_personal_address_checkbox_gates_then_allows_send(
    dashboard_db: sqlite3.Connection,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    application_id, queue_id = _cold_draft(
        dashboard_db,
        recipient="jean.dupont@acme.example",
        status="queued",
        approved=False,
    )
    sender = _Sender()
    _configure_dashboard(monkeypatch, enabled=True)
    try:
        with _dashboard_client(dashboard_db, sender=sender) as client:
            confirmation = client.get(f"/outreach/{queue_id}")
            blocked = client.post(
                f"/outreach/{queue_id}/send",
                data={"body": "Bonjour Jean"},
            )
            sent = client.post(
                f"/outreach/{queue_id}/send",
                data={
                    "body": "Bonjour Jean",
                    "personal_address_confirmed": "1",
                },
                follow_redirects=False,
            )
    finally:
        get_settings.cache_clear()

    assert 'name="personal_address_confirmed"' in confirmation.text
    assert blocked.status_code == 409
    assert "personal-address confirmation" in blocked.text
    assert sent.status_code == 303
    assert sent.headers["location"] == "/outreach"
    assert sender.sent is not None
    assert OPT_OUT_LINE in sender.sent.get_content()
    assert current_status(dashboard_db, application_id) == "applied"
