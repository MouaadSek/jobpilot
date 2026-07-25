"""Read-only queries shared by review surfaces."""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from jobpilot.state import LEGAL

# All statuses the state machine knows about, derived from its transition table.
_ALL_STATUSES = set(LEGAL) | {nxt for nexts in LEGAL.values() for nxt in nexts}
# Dashboard navigation tabs, in funnel order, restricted to statuses that exist
# in state.py. "applied" is the recorded state for a sent/submitted application.
TAB_STATUSES: tuple[str, ...] = tuple(
    status
    for status in ("queued", "generating", "ready", "applied", "skipped")
    if status in _ALL_STATUSES
)


def applications_by_status(
    db: sqlite3.Connection,
    status: str,
) -> list[dict[str, Any]]:
    """Return offer applications in one status, in stable descending score order."""

    rows = db.execute(
        "SELECT a.id, m.final_score AS score, o.title, o.city, "
        "       o.contract_type, o.url, o.posted_at, "
        "       c.name AS company, s.name AS source "
        "FROM applications a "
        "JOIN offers o ON o.id = a.offer_id "
        "LEFT JOIN match_scores m ON m.offer_id = o.id "
        "LEFT JOIN companies c ON c.id = o.company_id "
        "LEFT JOIN sources s ON s.id = o.source_id "
        "WHERE a.status = ? "
        "ORDER BY m.final_score IS NULL, m.final_score DESC, a.id",
        (status,),
    ).fetchall()
    return [dict(row) for row in rows]


def queued_applications(db: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return the review queue (queued offers) in stable descending score order."""

    return applications_by_status(db, "queued")


def outreach_drafts(db: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return unsent cold drafts that may still be reviewed or retried."""

    rows = db.execute(
        "SELECT q.id AS queue_id, q.application_id, q.to_email, q.subject, "
        "       q.scheduled_at, a.status, a.contact_name, "
        "       c.name AS company "
        "FROM email_queue q "
        "JOIN applications a ON a.id = q.application_id "
        "LEFT JOIN companies c ON c.id = a.company_id "
        "WHERE a.kind = 'cold' AND q.sent_at IS NULL "
        "  AND a.status IN ('queued', 'generating', 'ready') "
        "ORDER BY q.scheduled_at, q.id"
    ).fetchall()
    return [dict(row) for row in rows]


def status_tabs(db: sqlite3.Connection, active: str) -> list[dict[str, Any]]:
    """Navigation tabs with per-status counts for offer applications."""

    counts = {
        row["status"]: row["n"]
        for row in db.execute(
            "SELECT status, count(*) AS n FROM applications "
            "WHERE kind = 'offer' GROUP BY status"
        ).fetchall()
    }
    return [
        {"status": status, "count": counts.get(status, 0), "active": status == active}
        for status in TAB_STATUSES
    ]


def status_counts(db: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return application counts using the same grouping as ``jobpilot stats``."""

    rows = db.execute(
        "SELECT status, count(*) AS n FROM applications "
        "GROUP BY status ORDER BY n DESC"
    ).fetchall()
    return [dict(row) for row in rows]


def application_detail(
    db: sqlite3.Connection,
    application_id: int,
) -> dict[str, Any] | None:
    """Return an application with offer, company, and stored score data."""

    row = db.execute(
        "SELECT a.id, a.kind, a.status, a.cv_pdf_path, a.letter_pdf_path, "
        "       a.last_event_at, o.title, o.description, o.city, "
        "       o.contract_type, o.url, o.posted_at, o.remote_policy, "
        "       o.contact_email, "
        "       c.name AS company, s.name AS source, "
        "       m.hard_filter_pass, m.hard_filter_reason, "
        "       m.semantic_score, m.keyword_score, m.bonus_score, "
        "       m.final_score, v.label AS variant_label, v.slug AS variant_slug "
        "FROM applications a "
        "LEFT JOIN offers o ON o.id = a.offer_id "
        "LEFT JOIN companies c ON c.id = COALESCE(o.company_id, a.company_id) "
        "LEFT JOIN sources s ON s.id = o.source_id "
        "LEFT JOIN match_scores m ON m.offer_id = o.id "
        "LEFT JOIN cv_variants v ON v.id = m.best_cv_variant_id "
        "WHERE a.id = ?",
        (application_id,),
    ).fetchone()
    return dict(row) if row is not None else None


def event_history(
    db: sqlite3.Connection,
    application_id: int,
) -> list[dict[str, Any]]:
    """Return event history with safe, readable JSON detail."""

    rows = db.execute(
        "SELECT event, detail, created_at FROM events "
        "WHERE application_id = ? ORDER BY id",
        (application_id,),
    ).fetchall()
    history: list[dict[str, Any]] = []
    for row in rows:
        detail = row["detail"] or "{}"
        try:
            parsed = json.loads(detail)
            rendered = json.dumps(parsed, ensure_ascii=False, sort_keys=True)
        except (TypeError, json.JSONDecodeError):
            rendered = str(detail)
        history.append(
            {
                "event": row["event"],
                "detail": rendered,
                "created_at": row["created_at"],
            }
        )
    return history
