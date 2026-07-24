"""The single authorized writer of applications.status.

Every status transition MUST go through transition(): it validates legality and
appends to the events audit table. No other module issues UPDATE ... status.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime

from jobpilot.logging_conf import get_logger

log = get_logger("state")

# Legal transitions. Keys are current status; values the set of allowed next states.
LEGAL: dict[str, set[str]] = {
    "queued": {"skipped", "generating"},
    "skipped": set(),  # terminal
    "generating": {"ready", "queued"},  # generation can fail back to queued
    "ready": {"applied", "queued"},
    "applied": {"followup_1", "replied", "interview", "rejected", "ghosted"},
    "followup_1": {"followup_2", "replied", "interview", "rejected", "ghosted"},
    "followup_2": {"replied", "interview", "rejected", "ghosted"},
    "replied": {"interview", "rejected"},
    "interview": {"offer_received", "rejected"},
    "offer_received": set(),  # terminal
    "rejected": set(),  # terminal
    "ghosted": {"replied"},  # a ghost can still resurface
}


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


class IllegalTransition(ValueError):
    """Raised when a status change is not permitted by the state machine."""


def current_status(db: sqlite3.Connection, application_id: int) -> str:
    row = db.execute(
        "SELECT status FROM applications WHERE id = ?", (application_id,)
    ).fetchone()
    if row is None:
        raise ValueError(f"no application with id={application_id}")
    return row["status"]


def log_event(
    db: sqlite3.Connection,
    application_id: int,
    event: str,
    detail: dict | None = None,
    *,
    commit: bool = True,
) -> None:
    """Append an audit event. Used for status_change, human_approved, email_sent, etc."""
    db.execute(
        "INSERT INTO events (application_id, event, detail, created_at) "
        "VALUES (?, ?, ?, ?)",
        (application_id, event, json.dumps(detail or {}, ensure_ascii=False),
         _utc_now()),
    )
    if commit:
        db.commit()


def transition(
    db: sqlite3.Connection,
    application_id: int,
    to_status: str,
    *,
    detail: dict | None = None,
) -> str:
    """Move an application to to_status if legal; log a status_change event.

    Returns the new status. Raises IllegalTransition otherwise. Idempotent for
    a no-op (same status) is *not* allowed unless the machine permits a self-loop,
    which none currently do — callers should check current_status if needed.
    """
    frm = current_status(db, application_id)
    allowed = LEGAL.get(frm, set())
    if to_status not in allowed:
        raise IllegalTransition(
            f"application {application_id}: {frm} -> {to_status} not allowed "
            f"(legal: {sorted(allowed) or 'none, terminal'})"
        )

    now = _utc_now()
    db.execute(
        "UPDATE applications SET status = ?, last_event_at = ? WHERE id = ?",
        (to_status, now, application_id),
    )
    payload = {"from": frm, "to": to_status, **(detail or {})}
    log_event(db, application_id, "status_change", payload, commit=False)
    db.commit()
    log.info("application %d: %s -> %s", application_id, frm, to_status)
    return to_status
