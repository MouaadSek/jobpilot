"""The tracker: every application, one table, read-only.

Deliberately not a Google Sheets sync. That needs OAuth and a connector and is
its own task if it is ever wanted; a table that is already true is worth more
than a copy of it somewhere else that might not be.

Read-only in the strict sense: nothing here writes, transitions or sends. It is
the one surface that answers "where does everything stand" without offering a
way to change it by accident.
"""

from __future__ import annotations

import csv
import io
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from jobpilot.generation_warnings import warning_gates_by_application
from jobpilot.logging_conf import get_logger

log = get_logger("tracker")

#: Columns, in the order they are shown and exported. The CSV is the visible
#: table, so the two cannot drift.
COLUMNS: tuple[tuple[str, str], ...] = (
    ("company", "Entreprise"),
    ("title", "Intitulé"),
    ("source", "Source"),
    ("score", "Score"),
    ("status", "Statut"),
    ("applied_at", "Envoyée le"),
    ("apply_route", "Voie"),
    ("variant", "CV"),
)

SORTS: dict[str, str] = {
    "recent": "a.last_event_at IS NULL, a.last_event_at DESC, a.id DESC",
    "company": "lower(COALESCE(c.name, c2.name, '')), a.id DESC",
    "score": "m.final_score IS NULL, m.final_score DESC, a.id DESC",
    "status": "a.status, a.id DESC",
    "applied": "a.applied_at IS NULL, a.applied_at DESC, a.id DESC",
}
DEFAULT_SORT = "recent"


@dataclass(frozen=True, slots=True)
class TrackerCounts:
    """The four numbers worth seeing before the table itself."""

    sent_this_week: int
    sent_total: int
    ready: int
    queued: int

    def as_dict(self) -> dict[str, int]:
        return {
            "sent_this_week": self.sent_this_week,
            "sent_total": self.sent_total,
            "ready": self.ready,
            "queued": self.queued,
        }


def _week_start(now: datetime | None = None) -> str:
    """Monday 00:00 UTC of the current week, as ISO text.

    Compared as text against applications.applied_at, which the constitution
    requires to be UTC ISO 8601 — so lexicographic order is chronological order.
    """

    moment = now or datetime.now(UTC)
    monday = (moment - timedelta(days=moment.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return monday.isoformat()


def counts(db: sqlite3.Connection, *, now: datetime | None = None) -> TrackerCounts:
    row = db.execute(
        "SELECT "
        " sum(applied_at IS NOT NULL AND applied_at >= ?) AS sent_this_week, "
        " sum(applied_at IS NOT NULL) AS sent_total, "
        " sum(status = 'ready') AS ready, "
        " sum(status = 'queued') AS queued "
        "FROM applications WHERE kind = 'offer'",
        (_week_start(now),),
    ).fetchone()
    return TrackerCounts(
        sent_this_week=int(row["sent_this_week"] or 0),
        sent_total=int(row["sent_total"] or 0),
        ready=int(row["ready"] or 0),
        queued=int(row["queued"] or 0),
    )


def tracker_rows(
    db: sqlite3.Connection,
    *,
    status: str | None = None,
    sort: str = DEFAULT_SORT,
) -> tuple[dict[str, Any], ...]:
    """Every offer application, optionally narrowed to one status."""

    order = SORTS.get(sort, SORTS[DEFAULT_SORT])
    clause = ""
    params: list[Any] = []
    if status:
        clause = " AND a.status = ?"
        params.append(status)

    rows = db.execute(
        "SELECT a.id AS application_id, a.status, a.applied_at, a.apply_route, "
        "       o.title, o.url, m.final_score AS score, "
        "       COALESCE(c.name, c2.name) AS company, s.name AS source, "
        "       v.label AS variant "
        "FROM applications a "
        "LEFT JOIN offers o ON o.id = a.offer_id "
        "LEFT JOIN sources s ON s.id = o.source_id "
        "LEFT JOIN companies c ON c.id = o.company_id "
        "LEFT JOIN companies c2 ON c2.id = a.company_id "
        "LEFT JOIN match_scores m ON m.offer_id = o.id "
        "LEFT JOIN cv_variants v ON v.id = m.best_cv_variant_id "
        f"WHERE a.kind = 'offer'{clause} ORDER BY {order}",
        params,
    ).fetchall()
    # A degraded generation has to be identifiable from the list, not only from
    # the detail page nobody opens for an application they think is fine.
    warning_marks = warning_gates_by_application(db)
    enriched = []
    for row in rows:
        entry = dict(row)
        entry["warning_gates"] = list(warning_marks.get(int(row["application_id"]), ()))
        enriched.append(entry)
    return tuple(enriched)


def statuses(db: sqlite3.Connection) -> list[str]:
    """Statuses that actually occur, so the filter offers no dead options."""

    return [
        row["status"]
        for row in db.execute(
            "SELECT DISTINCT status FROM applications WHERE kind = 'offer' "
            "ORDER BY status"
        )
    ]


def to_csv(rows: tuple[dict[str, Any], ...]) -> str:
    """Export exactly the visible rows, in the visible column order."""

    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow([label for _, label in COLUMNS])
    for row in rows:
        writer.writerow(
            ["" if row.get(key) is None else row.get(key) for key, _ in COLUMNS]
        )
    return buffer.getvalue()
