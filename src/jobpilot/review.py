"""Read-only queries shared by review surfaces."""

from __future__ import annotations

import json
import sqlite3
from typing import Any


def queued_applications(db: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return the review queue in stable descending score order."""

    rows = db.execute(
        "SELECT a.id, m.final_score AS score, o.title, o.city, "
        "       o.contract_type, o.url, o.posted_at, "
        "       c.name AS company, s.name AS source "
        "FROM applications a "
        "JOIN offers o ON o.id = a.offer_id "
        "LEFT JOIN match_scores m ON m.offer_id = o.id "
        "LEFT JOIN companies c ON c.id = o.company_id "
        "LEFT JOIN sources s ON s.id = o.source_id "
        "WHERE a.status = 'queued' "
        "ORDER BY m.final_score IS NULL, m.final_score DESC, a.id"
    ).fetchall()
    return [dict(row) for row in rows]


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
