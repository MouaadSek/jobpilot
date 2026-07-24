"""State machine transition tests: legality + event auditing."""

from __future__ import annotations

import sqlite3

import pytest

from jobpilot.state import IllegalTransition, current_status, log_event, transition


def _app(db: sqlite3.Connection, status: str = "queued") -> int:
    # An application needs no offer for this test; kind must satisfy the CHECK.
    cur = db.execute(
        "INSERT INTO applications (kind, status) VALUES ('cold', ?)", (status,)
    )
    db.commit()
    return int(cur.lastrowid)


def test_legal_transition_updates_and_logs(db: sqlite3.Connection) -> None:
    app_id = _app(db, "queued")
    transition(db, app_id, "generating")
    assert current_status(db, app_id) == "generating"

    ev = db.execute(
        "SELECT event, detail FROM events WHERE application_id = ?", (app_id,)
    ).fetchone()
    assert ev["event"] == "status_change"
    assert '"from": "queued"' in ev["detail"]
    assert '"to": "generating"' in ev["detail"]


def test_illegal_transition_raises_and_no_change(db: sqlite3.Connection) -> None:
    app_id = _app(db, "queued")
    with pytest.raises(IllegalTransition):
        transition(db, app_id, "applied")  # not reachable from queued
    assert current_status(db, app_id) == "queued"
    n = db.execute(
        "SELECT count(*) AS n FROM events WHERE application_id = ?", (app_id,)
    ).fetchone()["n"]
    assert n == 0


def test_terminal_state_has_no_exits(db: sqlite3.Connection) -> None:
    app_id = _app(db, "rejected")
    with pytest.raises(IllegalTransition):
        transition(db, app_id, "interview")


def test_full_happy_path(db: sqlite3.Connection) -> None:
    app_id = _app(db, "queued")
    for nxt in ["generating", "ready", "applied", "followup_1", "replied",
                "interview", "offer_received"]:
        transition(db, app_id, nxt)
    assert current_status(db, app_id) == "offer_received"


def test_human_approved_event_recorded(db: sqlite3.Connection) -> None:
    """Constitution: no send/submit without a prior human_approved event."""
    app_id = _app(db, "ready")
    log_event(db, app_id, "human_approved", {"by": "cli"})
    ev = db.execute(
        "SELECT event FROM events WHERE application_id = ? AND event = 'human_approved'",
        (app_id,),
    ).fetchone()
    assert ev is not None
