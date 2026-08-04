"""Read-only queries shared by review surfaces."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Any

from jobpilot.freshness import (
    PUBLISHED_COLUMNS_SQL,
    RECENT_ORDER_SQL,
    Freshness,
    annotate,
    describe,
    drop_stale,
)
from jobpilot.state import LEGAL
from jobpilot.vocabulary import TokenTier, parse_rejections

# All statuses the state machine knows about, derived from its transition table.
_ALL_STATUSES = set(LEGAL) | {nxt for nexts in LEGAL.values() for nxt in nexts}
# Dashboard navigation tabs, in funnel order, restricted to statuses that exist
# in state.py. "applied" is the recorded state for a sent/submitted application.
TAB_STATUSES: tuple[str, ...] = tuple(
    status
    for status in ("queued", "generating", "ready", "applied", "skipped")
    if status in _ALL_STATUSES
)


#: How the review lists may be ordered. Recency is the default because an offer
#: that scores 0.72 and closed last week is worth less than one that scores 0.61
#: and opened yesterday — the queue was ordered by score, and offers aged out of
#: usefulness before they were reached. Score is still available and still shown
#: as a column; it stopped being the ordering, not the information.
SORTS: dict[str, str] = {
    "recent": f"{RECENT_ORDER_SQL}, m.final_score IS NULL, m.final_score DESC, a.id",
    "score": f"m.final_score IS NULL, m.final_score DESC, {RECENT_ORDER_SQL}, a.id",
}
DEFAULT_SORT = "recent"


def applications_by_status(
    db: sqlite3.Connection,
    status: str,
    *,
    sort: str = DEFAULT_SORT,
    include_stale: bool = False,
    max_age_days: int | None = None,
    now: datetime | None = None,
) -> tuple[list[dict[str, Any]], int]:
    """Offer applications in one status, newest first, with their age.

    Returns the visible rows and how many were hidden for being older than the
    staleness threshold. Hidden is all it is: no status changes, no writes.
    """

    order = SORTS.get(sort, SORTS[DEFAULT_SORT])
    rows = db.execute(
        "SELECT a.id, m.final_score AS score, o.title, o.city, "
        "       o.contract_type, o.url, o.posted_at, "
        f"       {PUBLISHED_COLUMNS_SQL}, "
        "       c.name AS company, s.name AS source "
        "FROM applications a "
        "JOIN offers o ON o.id = a.offer_id "
        "LEFT JOIN match_scores m ON m.offer_id = o.id "
        "LEFT JOIN companies c ON c.id = o.company_id "
        "LEFT JOIN sources s ON s.id = o.source_id "
        "WHERE a.status = ? "
        f"ORDER BY {order}",
        (status,),
    ).fetchall()
    annotated = annotate(
        [dict(row) for row in rows], max_age_days=max_age_days, now=now
    )
    return drop_stale(annotated, include_stale=include_stale)


def queued_applications(db: sqlite3.Connection) -> list[dict[str, Any]]:
    """The review queue (queued offers), newest first, staleness filter off.

    The plain list, for callers with no page to render — ``jobpilot review`` and
    the tests. Surfaces that can offer a toggle call applications_by_status.
    """

    rows, _hidden = applications_by_status(db, "queued", include_stale=True)
    return rows


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
        "       m.final_score, v.label AS variant_label, v.slug AS variant_slug, "
        f"       {PUBLISHED_COLUMNS_SQL} "
        "FROM applications a "
        "LEFT JOIN offers o ON o.id = a.offer_id "
        "LEFT JOIN companies c ON c.id = COALESCE(o.company_id, a.company_id) "
        "LEFT JOIN sources s ON s.id = o.source_id "
        "LEFT JOIN match_scores m ON m.offer_id = o.id "
        "LEFT JOIN cv_variants v ON v.id = m.best_cv_variant_id "
        "WHERE a.id = ?",
        (application_id,),
    ).fetchone()
    if row is None:
        return None
    return annotate([dict(row)])[0]


def offer_freshness(
    db: sqlite3.Connection,
    application_id: int,
    *,
    max_age_days: int | None = None,
    now: datetime | None = None,
) -> Freshness | None:
    """How old the offer behind one application is. None if it has no offer.

    Read on its own rather than off application_detail so the approve path can
    ask the question before it does any work — a generation costs an API call
    and about twenty seconds, and a closed posting is the one case where that is
    certainly wasted.
    """

    row = db.execute(
        f"SELECT {PUBLISHED_COLUMNS_SQL} "
        "FROM applications a JOIN offers o ON o.id = a.offer_id WHERE a.id = ?",
        (application_id,),
    ).fetchone()
    if row is None:
        return None
    return describe(
        row["published_at"],
        inferred=bool(row["published_inferred"]),
        max_age_days=max_age_days,
        now=now,
    )


#: Written by tailoring.generate_application onto the ready status_change event.
_DECISION_FIELDS = (
    "variant",
    "routing_variant",
    "document_variant",
    "variant_selected_by",
    "routing_justification",
    "routing_runner_up",
    "routing_fallback_reason",
)


def variant_decision(
    db: sqlite3.Connection,
    application_id: int,
) -> dict[str, Any] | None:
    """Return how the CV variant was chosen, from the audit event that recorded it.

    The events table is already the record of the decision, so reading it back
    keeps the detail page truthful without duplicating the fields onto
    ``applications``.
    """

    rows = db.execute(
        "SELECT detail FROM events WHERE application_id = ? AND event = 'status_change' "
        "ORDER BY id DESC",
        (application_id,),
    ).fetchall()
    for row in rows:
        try:
            parsed = json.loads(row["detail"] or "{}")
        except (TypeError, json.JSONDecodeError):
            continue
        if not isinstance(parsed, dict) or parsed.get("to") != "ready":
            continue
        decision = {
            field: parsed[field] for field in _DECISION_FIELDS if parsed.get(field)
        }
        if not decision:
            return None
        # Written as a boolean by the generator; older events predate it, and a
        # missing value must not be rendered as agreement.
        decision["agreed"] = parsed.get("routing_agreed")
        return decision
    return None


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


def vocabulary_misses(
    db: sqlite3.Connection,
    *,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Return capability-tier tokens that have tripped generations, by frequency.

    Only the tier a config edit can fix is reported. A refused quantity or a
    refused employer name is a real fabrication and no vocabulary file should
    ever excuse one, so those stay out of this list even though they are logged
    the same way.
    """

    rows = db.execute(
        "SELECT application_id, detail, created_at FROM events "
        "WHERE event = 'generation_failed' ORDER BY id DESC",
    ).fetchall()
    misses: dict[str, dict[str, Any]] = {}
    for row in rows:
        try:
            parsed = json.loads(row["detail"] or "{}")
        except (TypeError, json.JSONDecodeError):
            continue
        if not isinstance(parsed, dict):
            continue
        messages = [str(parsed.get("error") or "")]
        attempts = parsed.get("attempts")
        if isinstance(attempts, list):
            messages.extend(str(attempt) for attempt in attempts)
        for rejection in parse_rejections(messages):
            if rejection.tier is not TokenTier.CAPABILITY:
                continue
            miss = misses.setdefault(
                rejection.token,
                {
                    "token": rejection.token,
                    "kind": rejection.kind,
                    "count": 0,
                    "entries": [],
                    "applications": [],
                    "last_seen": row["created_at"],
                },
            )
            miss["count"] += 1
            # Which entries could not support it: the same token refused under
            # one employer and accepted elsewhere is a scope problem, not a
            # vocabulary one.
            scope = rejection.entry or "whole bank"
            if scope not in miss["entries"]:
                miss["entries"].append(scope)
            if row["application_id"] not in miss["applications"]:
                miss["applications"].append(row["application_id"])
    ordered = sorted(
        misses.values(),
        key=lambda miss: (-miss["count"], miss["token"]),
    )
    return ordered[:limit]


def invention_report(db: sqlite3.Connection) -> dict[str, Any]:
    """How often the advisor cites an id that does not exist, and whether it recovers.

    Task 37 exists because of two hard generation failures, the second caused by
    `skill.rules.sigma` — an id the model built by analogy. Prevention (item 1)
    and recovery (item 2) are both guesses until this counts them, so the events
    are read back rather than the logs: "did item 1 work?" has to be answerable
    after ten generations without anyone re-reading a log file by hand.

    A rejection is one `fact_id_rejected` event. A recovery is a generation that
    emitted `fact_id_recovered`, which only happens when a retry produced a
    valid plan after an invented id. A citation that was dropped instead
    (item 3) is counted separately: it is not a recovery.
    """

    rejections = [
        json.loads(row["detail"] or "{}")
        for row in db.execute(
            "SELECT detail FROM events WHERE event = 'fact_id_rejected' ORDER BY id"
        )
    ]
    recovered_events = [
        json.loads(row["detail"] or "{}")
        for row in db.execute(
            "SELECT detail FROM events WHERE event = 'fact_id_recovered' ORDER BY id"
        )
    ]
    dropped = [
        json.loads(row["detail"] or "{}")
        for row in db.execute(
            "SELECT detail FROM events WHERE event = 'citation_dropped' ORDER BY id"
        )
    ]
    generations = int(
        db.execute(
            "SELECT count(*) AS n FROM events WHERE event = 'status_change' "
            "AND detail LIKE '%\"to\": \"generating\"%'"
        ).fetchone()["n"]
    )

    recovered_ids: set[str] = set()
    for event in recovered_events:
        recovered_ids.update(event.get("fact_ids") or ())
    dropped_ids = {event.get("fact_id") for event in dropped if event.get("fact_id")}

    by_section: dict[str, dict[str, Any]] = {}
    for rejection in rejections:
        section = rejection.get("section") or "unknown"
        bucket = by_section.setdefault(
            section, {"section": section, "rejections": 0, "ids": {}, "had_similar": 0}
        )
        bucket["rejections"] += 1
        bucket["had_similar"] += 1 if rejection.get("had_similar") else 0
        fact_id = rejection.get("fact_id") or "?"
        bucket["ids"][fact_id] = bucket["ids"].get(fact_id, 0) + 1

    # Numbers are the same failure shape in a different place: prose rather than
    # a citation slot. Same report, separate category, so it is visible which
    # kind dominates rather than the two averaging each other out.
    number_events = [
        json.loads(row["detail"] or "{}")
        for row in db.execute(
            "SELECT detail FROM events WHERE event = 'number_rejected' ORDER BY id"
        )
    ]
    number_counts: dict[str, int] = {}
    for event in number_events:
        value = event.get("number") or "?"
        number_counts[value] = number_counts.get(value, 0) + 1

    distinct = {rejection.get("fact_id") for rejection in rejections}
    distinct.discard(None)
    return {
        "numbers": {
            "rejections": len(number_events),
            "distinct": len(number_counts),
            "ids": sorted(
                number_counts.items(), key=lambda item: (-item[1], item[0])
            ),
        },
        "generations": generations,
        "rejections": len(rejections),
        "distinct_ids": len(distinct),
        "recovered_ids": len(recovered_ids & distinct),
        "dropped_ids": len(dropped_ids & distinct),
        "unrecovered_ids": len(distinct - recovered_ids - dropped_ids),
        "recovery_rate": (
            len(recovered_ids & distinct) / len(distinct) if distinct else None
        ),
        "invention_rate": (len(distinct) / generations if generations else None),
        "by_section": sorted(
            (
                {
                    "section": bucket["section"],
                    "rejections": bucket["rejections"],
                    "distinct_ids": len(bucket["ids"]),
                    "had_similar": bucket["had_similar"],
                    "ids": sorted(
                        bucket["ids"].items(), key=lambda item: (-item[1], item[0])
                    ),
                }
                for bucket in by_section.values()
            ),
            key=lambda bucket: (-bucket["rejections"], bucket["section"]),
        ),
    }
