"""The skim list: offers that passed the hard filter but scored below threshold.

Task 35 measured why this page has to exist. Alert-sourced offers are
structurally unscoreable — ~141 of 189 filter-passers were LinkedIn/Indeed
alerts carrying ~120-character descriptions, and 176 of 235 verified bank skills
score exactly zero against that corpus. Their descriptions cannot be enriched
either: fetching the posting behind an alert is scraping, which constitution
rule 11 forbids.

So they are a discovery channel, not a scoring channel, and the answer is a
human skimming path rather than a better score. LinkedIn and Indeed are where
most French alternance volume actually is; discarding them would be worse than
reading them quickly.

Read-only queries plus the two writes the page needs. The web layer owns none of
this (constitution), and every status change goes through ``state.transition``.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from jobpilot.config import get_settings
from jobpilot.freshness import (
    NOT_STALE_SQL,
    PUBLISHED_COLUMNS_SQL,
    RECENT_ORDER_SQL,
    annotate,
    max_offer_age_days,
    stale_cutoff,
)
from jobpilot.logging_conf import get_logger
from jobpilot.state import current_status, log_event, transition

log = get_logger("skim")

#: Rows per page. The list is ~180 offers today and only grows.
PAGE_SIZE = 50

#: Sorts the page offers. Newest first is the default: a skim is triage, and a
#: stale offer is usually already filled.
#:
#: "recent" used to order on o.posted_at alone, which put every alert-sourced
#: offer — 408 of 669 rows, none of which carry one — in a single NULL block at
#: the bottom regardless of when it arrived. It now orders on the same fallback
#: the age column shows.
SORTS: dict[str, str] = {
    "recent": f"{RECENT_ORDER_SQL}, o.id DESC",
    "score": f"m.final_score DESC, {RECENT_ORDER_SQL}, o.id DESC",
}
DEFAULT_SORT = "recent"

#: An application in one of these states has left the skim list for good: it is
#: either in the review flow proper or deliberately dismissed.
_HANDLED_STATUSES = ("queued", "generating", "ready", "applied", "skipped")


class SkimError(ValueError):
    """Raised when an offer cannot be promoted or ignored from the skim list."""


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(frozen=True, slots=True)
class SkimPage:
    """One page of skimmable offers, plus what the pager needs to render."""

    rows: tuple[dict[str, Any], ...]
    total: int
    page: int
    pages: int
    sort: str
    source: str | None
    include_ignored: bool
    include_stale: bool = False
    hidden_stale: int = 0
    max_age_days: int = 0

    @property
    def has_previous(self) -> bool:
        return self.page > 1

    @property
    def has_next(self) -> bool:
        return self.page < self.pages


def available_sources(db: sqlite3.Connection, *, threshold: float | None = None) -> list[str]:
    """Sources that actually have skimmable offers, for the filter control."""

    bar = _threshold(threshold)
    rows = db.execute(
        "SELECT DISTINCT s.name AS name "
        "FROM offers o "
        "JOIN match_scores m ON m.offer_id = o.id "
        "JOIN sources s ON s.id = o.source_id "
        "WHERE m.hard_filter_pass = 1 AND m.final_score < ? "
        "ORDER BY s.name",
        (bar,),
    ).fetchall()
    return [row["name"] for row in rows]


def _threshold(threshold: float | None) -> float:
    return get_settings().queue_threshold if threshold is None else threshold


def skim_offers(
    db: sqlite3.Connection,
    *,
    source: str | None = None,
    include_ignored: bool = False,
    include_stale: bool = False,
    sort: str = DEFAULT_SORT,
    page: int = 1,
    per_page: int = PAGE_SIZE,
    threshold: float | None = None,
    max_age_days: int | None = None,
    now: datetime | None = None,
) -> SkimPage:
    """Offers that passed the hard filter and scored below the queue threshold.

    An offer that failed the hard filter is never listed: it was rejected on
    contract, location or duration, and no amount of skimming changes that.

    The staleness filter is applied in SQL rather than to the fetched page: this
    list is paginated, and a page trimmed after the fact would report a total
    and a page count that describe rows the reader cannot see.
    """

    bar = _threshold(threshold)
    order = SORTS.get(sort, SORTS[DEFAULT_SORT])
    sort = sort if sort in SORTS else DEFAULT_SORT
    limit_days = max_offer_age_days(max_age_days)

    where = ["m.hard_filter_pass = 1", "m.final_score < ?"]
    params: list[Any] = [bar]
    if source:
        where.append("s.name = ?")
        params.append(source)
    if not include_ignored:
        # Anything already promoted or dismissed has left the skim list.
        placeholders = ", ".join("?" for _ in _HANDLED_STATUSES)
        where.append(
            f"(a.id IS NULL OR a.status NOT IN ({placeholders}))"
        )
        params.extend(_HANDLED_STATUSES)
    clause = " AND ".join(where)

    joins = (
        "FROM offers o "
        "JOIN match_scores m ON m.offer_id = o.id "
        "LEFT JOIN sources s ON s.id = o.source_id "
        "LEFT JOIN companies c ON c.id = o.company_id "
        "LEFT JOIN applications a ON a.offer_id = o.id "
    )
    total = int(
        db.execute(f"SELECT count(*) AS n {joins} WHERE {clause}", params).fetchone()["n"]
    )

    visible_clause, visible_params = clause, list(params)
    hidden = 0
    if not include_stale:
        visible_clause = f"{clause} AND {NOT_STALE_SQL}"
        visible_params = [*params, stale_cutoff(limit_days, now=now)]
        visible_total = int(
            db.execute(
                f"SELECT count(*) AS n {joins} WHERE {visible_clause}", visible_params
            ).fetchone()["n"]
        )
        hidden = total - visible_total
        total = visible_total

    per_page = max(1, per_page)
    pages = max(1, -(-total // per_page))
    page = min(max(1, page), pages)

    rows = db.execute(
        "SELECT o.id AS offer_id, o.title, o.city, o.url, o.posted_at, "
        f"       {PUBLISHED_COLUMNS_SQL}, "
        "       o.contract_type, m.final_score AS score, "
        "       c.name AS company, s.name AS source, "
        "       a.id AS application_id, a.status AS application_status "
        f"{joins} WHERE {visible_clause} ORDER BY {order} LIMIT ? OFFSET ?",
        [*visible_params, per_page, (page - 1) * per_page],
    ).fetchall()

    return SkimPage(
        rows=tuple(
            annotate(
                [dict(row) for row in rows], max_age_days=limit_days, now=now
            )
        ),
        total=total,
        page=page,
        pages=pages,
        sort=sort,
        source=source,
        include_ignored=include_ignored,
        include_stale=include_stale,
        hidden_stale=hidden,
        max_age_days=limit_days,
    )


def _skimmable_offer(
    db: sqlite3.Connection, offer_id: int, *, threshold: float | None = None
) -> sqlite3.Row:
    """The offer row, if it is genuinely one this page may act on."""

    row = db.execute(
        "SELECT o.id, o.company_id, m.hard_filter_pass, m.final_score, "
        "       a.id AS application_id, a.status AS application_status "
        "FROM offers o "
        "JOIN match_scores m ON m.offer_id = o.id "
        "LEFT JOIN applications a ON a.offer_id = o.id "
        "WHERE o.id = ?",
        (offer_id,),
    ).fetchone()
    if row is None:
        raise SkimError(f"no scored offer with id={offer_id}")
    if not row["hard_filter_pass"]:
        raise SkimError(
            "this offer was rejected by the hard filter and is not skimmable"
        )
    if row["final_score"] is not None and row["final_score"] >= _threshold(threshold):
        raise SkimError("this offer is already above the queue threshold")
    return row


def _create_application(db: sqlite3.Connection, row: sqlite3.Row, *, via: str) -> int:
    """Create the offer's application row in 'queued'.

    matcher.score_new_offers owns the only other place an offer application is
    born, and it is frozen, so this cannot call into it. The insert is kept here
    rather than in the web layer, and it writes an event so a row that appeared
    outside the scoring pass is still explicable months later.
    """

    cursor = db.execute(
        "INSERT OR IGNORE INTO applications (offer_id, company_id, kind, status, "
        "last_event_at) VALUES (?, ?, 'offer', 'queued', ?)",
        (row["id"], row["company_id"], _utc_now()),
    )
    if cursor.rowcount:
        application_id = int(cursor.lastrowid)
    else:  # pragma: no cover - only reachable on a concurrent insert
        application_id = int(
            db.execute(
                "SELECT id FROM applications WHERE offer_id = ?", (row["id"],)
            ).fetchone()["id"]
        )
    log_event(
        db,
        application_id,
        "queued_from_skim",
        {"via": via, "offer_id": row["id"]},
    )
    return application_id


def promote_offer(
    db: sqlite3.Connection,
    offer_id: int,
    *,
    via: str = "dashboard skim",
    threshold: float | None = None,
) -> int:
    """Put a below-threshold offer into the normal review flow. Returns its id."""

    row = _skimmable_offer(db, offer_id, threshold=threshold)
    if row["application_id"] is None:
        application_id = _create_application(db, row, via=via)
        log.info("promoted offer %d from the skim list", offer_id)
        return application_id

    application_id = int(row["application_id"])
    status = current_status(db, application_id)
    if status == "queued":
        return application_id  # already where the caller wants it
    transition(db, application_id, "queued", detail={"via": via})
    return application_id


def ignore_offer(
    db: sqlite3.Connection,
    offer_id: int,
    *,
    via: str = "dashboard skim",
    threshold: float | None = None,
) -> int:
    """Dismiss a skimmed offer so it stops reappearing. Returns its id.

    Persisted as a real 'skipped' application rather than a client-side hide, so
    the decision survives a reload and shows up in the event history like every
    other decision the operator makes.
    """

    row = _skimmable_offer(db, offer_id, threshold=threshold)
    application_id = (
        int(row["application_id"])
        if row["application_id"] is not None
        else _create_application(db, row, via=via)
    )
    if current_status(db, application_id) == "skipped":
        return application_id
    transition(db, application_id, "skipped", detail={"via": via})
    log.info("ignored offer %d from the skim list", offer_id)
    return application_id
