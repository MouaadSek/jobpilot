"""Offer recency: one definition of "how old is this posting", used everywhere.

The queue was ordered by score, so a France Travail offer posted three weeks ago
could sit above one posted yesterday and stay there until it was worked down to
— by which time the posting was closed. Ordering, display and filtering all need
the same answer to "when was this published", and they need it to be the same
answer, so it lives here rather than in three list builders.

Two things this module is careful about.

**The date is not always there.** 408 of 669 offers have no ``posted_at`` at
all: LinkedIn and Indeed arrive as email alerts, which carry a title, a link and
almost nothing else. Those fall back to ``offers.scraped_at``, the moment
JobPilot first saw the row — but the two are not interchangeable. An offer is
always seen *after* it is posted, so an age computed from ``scraped_at`` is a
**lower bound**: the offer is at least that old and possibly much older. It is
therefore labelled as inferred, never coloured fresh, and never hidden on the
strength of a bound that could be wrong in the safe direction only.

**The stored formats disagree.** France Travail writes ``...Z``, WTTJ writes
``...+02:00``, ``scraped_at`` writes ``...+00:00``. Comparing those as text is
not comparing instants — a ``+02:00`` timestamp sorts by its local wall clock —
so ordering normalises through SQLite's ``strftime`` rather than trusting that
ISO text sorts chronologically. It does, but only once every value is in the
same zone.

Nothing here touches scoring. Whether freshness should influence ``final_score``
is a separate decision and matcher.py is frozen (constitution).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from jobpilot.config import get_settings

#: The publication instant to use, in SQL: the offer's own date when it has one,
#: otherwise the moment we first saw it. Assumes the offers table is aliased
#: ``o``, which every list builder already does.
PUBLISHED_AT_SQL = "COALESCE(NULLIF(o.posted_at, ''), o.scraped_at)"

#: True when the value above came from scraped_at, i.e. is a lower bound.
PUBLISHED_INFERRED_SQL = "(o.posted_at IS NULL OR o.posted_at = '')"

#: The same value normalised to UTC for ordering.
#:
#: NULL when SQLite cannot parse it, deliberately. Falling back to the raw text
#: was tried and is worse: 'bientôt' compares greater than any '2026-...' under
#: DESC, so an unreadable date sorted to the top of every list. NULL lets the
#: ``IS NULL`` term in RECENT_ORDER_SQL put it at the bottom where it belongs.
PUBLISHED_SORT_SQL = f"strftime('%Y-%m-%dT%H:%M:%fZ', {PUBLISHED_AT_SQL})"

#: The recency ordering itself, newest first, with rows carrying no usable date
#: at the end rather than silently at the top.
RECENT_ORDER_SQL = f"{PUBLISHED_SORT_SQL} IS NULL, {PUBLISHED_SORT_SQL} DESC"

#: The columns a list has to select for :func:`describe` to have anything to
#: read. Kept next to the expressions so the two cannot drift.
PUBLISHED_COLUMNS_SQL = (
    f"{PUBLISHED_AT_SQL} AS published_at, "
    f"{PUBLISHED_INFERRED_SQL} AS published_inferred"
)

#: Colour bands, in days. Deliberately *not* the same knob as the staleness
#: filter: the filter is a personal rule that can be relaxed offer by offer,
#: whereas these three bands are how the column reads at a glance and should not
#: move when the rule does.
FRESH_DAYS = 7
AMBER_DAYS = 14


@dataclass(frozen=True, slots=True)
class Freshness:
    """How old one offer is, and how sure we are of that."""

    published_at: str | None
    inferred: bool
    days: int | None
    label: str
    tone: str  # "fresh" | "amber" | "old" | "inferred" | "unknown"
    stale: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "published_at": self.published_at,
            "inferred": self.inferred,
            "days": self.days,
            "label": self.label,
            "tone": self.tone,
            "stale": self.stale,
        }


def max_offer_age_days(override: int | None = None) -> int:
    return get_settings().max_offer_age_days if override is None else override


def _parse(raw: Any) -> datetime | None:
    if not isinstance(raw, str) or not raw.strip():
        return None
    text = raw.strip()
    # datetime.fromisoformat gained "Z" support only in 3.11; be explicit rather
    # than depending on the interpreter's minor version.
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        moment = datetime.fromisoformat(text)
    except ValueError:
        return None
    return moment if moment.tzinfo else moment.replace(tzinfo=UTC)


def age_in_days(raw: Any, *, now: datetime | None = None) -> int | None:
    """Whole days between ``raw`` and now, or None if it is not a date.

    Negative ages are clamped to zero: a source that publishes with a future
    timestamp is stating an availability date, not a posting older than today.
    """

    moment = _parse(raw)
    if moment is None:
        return None
    delta = (now or datetime.now(UTC)) - moment
    return max(0, delta.days)


def _label(days: int | None, *, inferred: bool) -> str:
    if days is None:
        return "date inconnue"
    if inferred:
        # "vue" and not "publiée": this is when JobPilot saw it, which is the
        # only thing an email alert tells us.
        return "vue aujourd'hui" if days == 0 else f"vue il y a {days} j"
    if days == 0:
        return "aujourd'hui"
    if days == 1:
        return "hier"
    return f"il y a {days} j"


def _tone(days: int | None, *, inferred: bool) -> str:
    if days is None:
        return "unknown"
    if inferred:
        # Never green. The real posting date is at or before this one, so an
        # inferred four days could be a real three weeks.
        return "inferred" if days < AMBER_DAYS else "old"
    if days < FRESH_DAYS:
        return "fresh"
    if days <= AMBER_DAYS:
        return "amber"
    return "old"


def describe(
    published_at: Any,
    *,
    inferred: bool = False,
    max_age_days: int | None = None,
    now: datetime | None = None,
) -> Freshness:
    """Everything a list needs to show, and to decide whether to show it."""

    days = age_in_days(published_at, now=now)
    limit = max_offer_age_days(max_age_days)
    # An unknown date is never hidden: nothing is known about it, and the filter
    # is meant to hide what is provably old rather than what is merely unlabelled.
    # An inferred date can be: it is a lower bound, so exceeding the limit is
    # proof of age even though staying under it is not proof of freshness.
    stale = days is not None and days > limit
    return Freshness(
        published_at=published_at if isinstance(published_at, str) else None,
        inferred=inferred,
        days=days,
        label=_label(days, inferred=inferred),
        tone=_tone(days, inferred=inferred),
        stale=stale,
    )


def stale_cutoff(
    max_age_days: int | None = None,
    *,
    now: datetime | None = None,
) -> str:
    """The instant a row must be at or after to survive the staleness filter.

    For SQL filtering, which paginated lists need — they cannot count a page
    they have already trimmed in Python. Formatted to match PUBLISHED_SORT_SQL
    so the comparison is text against text in one zone.

    :func:`describe` calls a row stale when its whole-day age *exceeds* the
    limit, i.e. once it is at least ``limit + 1`` days old, so the cutoff is
    that same boundary and the comparison against it is strict — a row landing
    exactly on it is ``limit + 1`` days old and therefore stale.
    tests/test_freshness.py pins the two against each other, day by day, rather
    than trusting the arithmetic here to stay in step.
    """

    moment = (now or datetime.now(UTC)) - timedelta(days=max_offer_age_days(max_age_days) + 1)
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


#: The SQL predicate for "not hidden by the staleness filter". Takes the cutoff
#: as a bound parameter. A row with no parseable date is kept, matching
#: :func:`describe`: the filter hides what is provably old, not what is
#: unlabelled.
NOT_STALE_SQL = f"({PUBLISHED_SORT_SQL} IS NULL OR {PUBLISHED_SORT_SQL} > ?)"


def annotate(
    rows: list[dict[str, Any]],
    *,
    max_age_days: int | None = None,
    now: datetime | None = None,
) -> list[dict[str, Any]]:
    """Attach a ``freshness`` mapping to every row that selected the columns."""

    for row in rows:
        row["freshness"] = describe(
            row.get("published_at"),
            inferred=bool(row.get("published_inferred")),
            max_age_days=max_age_days,
            now=now,
        ).as_dict()
    return rows


def drop_stale(
    rows: list[dict[str, Any]],
    *,
    include_stale: bool = False,
) -> tuple[list[dict[str, Any]], int]:
    """Filter annotated rows, returning what is kept and how many were hidden.

    Hidden, not skipped and not deleted: the count comes back so the page can
    offer to show them again. Nothing here writes.
    """

    if include_stale:
        return rows, 0
    kept = [row for row in rows if not row["freshness"]["stale"]]
    return kept, len(rows) - len(kept)
