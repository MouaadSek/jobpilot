"""Task 42: recency is first-class, and the age it reports is honest.

France Travail offers were aging out in the queue before they were reached: the
review list was ordered by score, so a three-week-old 0.72 sat above a
one-day-old 0.61 and stayed there. Ordering, colouring and hiding all now come
from jobpilot.freshness, and these tests cover the two things about it that are
easy to get quietly wrong.

**The fallback is a lower bound, not a date.** 408 of 669 offers carry no
posted_at — LinkedIn and Indeed arrive as email alerts. They fall back to
scraped_at, which is always *after* the real posting date, so the age computed
from it understates how old the offer is. It is therefore marked and never
coloured fresh.

**The stored formats disagree.** France Travail writes ...Z, WTTJ writes
...+02:00, scraped_at writes ...+00:00. Text ordering across those is not
instant ordering.
"""

from __future__ import annotations

import hashlib
import sqlite3
from datetime import UTC, datetime, timedelta

import pytest

from jobpilot.freshness import (
    AMBER_DAYS,
    FRESH_DAYS,
    NOT_STALE_SQL,
    PUBLISHED_COLUMNS_SQL,
    RECENT_ORDER_SQL,
    age_in_days,
    describe,
    drop_stale,
    stale_cutoff,
)

NOW = datetime(2026, 8, 4, 12, 0, tzinfo=UTC)


def _at(days: int, *, hours: int = 0) -> str:
    return (NOW - timedelta(days=days, hours=hours)).isoformat()


def _offer(
    db: sqlite3.Connection,
    *,
    suffix: str,
    posted_at: str | None,
    scraped_at: str | None = None,
) -> int:
    source_id = db.execute(
        "SELECT id FROM sources WHERE name = 'france_travail'"
    ).fetchone()["id"]
    digest = hashlib.sha256(f"fresh-{suffix}".encode()).hexdigest()
    return int(
        db.execute(
            "INSERT INTO offers (source_id, external_id, url, title, description, "
            "contract_type, city, posted_at, scraped_at, content_hash) "
            "VALUES (?, ?, ?, ?, 'Description.', 'alternance', 'Lille', ?, ?, ?)",
            (
                source_id,
                f"offer-{suffix}",
                f"https://example.test/jobs/{suffix}",
                f"Offre {suffix}",
                posted_at,
                scraped_at or _at(0),
                digest,
            ),
        ).lastrowid
    )


# ----- parsing the formats that are actually stored -----


@pytest.mark.parametrize(
    ("stored", "days"),
    (
        ("2026-08-01T12:00:00.000Z", 3),  # France Travail
        ("2026-08-01T14:00:00.000+02:00", 3),  # WTTJ: same instant, other zone
        ("2026-08-01T12:00:00.000000+00:00", 3),  # scraped_at
        ("2026-08-01T12:00:00", 3),  # naive: read as UTC rather than rejected
    ),
)
def test_every_stored_timestamp_shape_parses_to_the_same_age(
    stored: str, days: int
) -> None:
    assert age_in_days(stored, now=NOW) == days


@pytest.mark.parametrize("stored", (None, "", "   ", "bientôt", 12345))
def test_an_unusable_value_is_no_age_rather_than_a_wrong_one(stored: object) -> None:
    assert age_in_days(stored, now=NOW) is None


def test_a_future_date_is_today_and_not_a_negative_age() -> None:
    """Some postings state an availability date rather than a posting date."""

    assert age_in_days(_at(-30), now=NOW) == 0


# ----- the bands -----


@pytest.mark.parametrize(
    ("days", "tone"),
    (
        (0, "fresh"),
        (FRESH_DAYS - 1, "fresh"),
        (FRESH_DAYS, "amber"),
        (AMBER_DAYS, "amber"),
        (AMBER_DAYS + 1, "old"),
    ),
)
def test_the_colour_bands_are_where_they_are_documented(days: int, tone: str) -> None:
    assert describe(_at(days), now=NOW).tone == tone


@pytest.mark.parametrize(
    ("days", "label"),
    ((0, "aujourd'hui"), (1, "hier"), (3, "il y a 3 j")),
)
def test_the_label_is_relative_and_not_a_raw_date(days: int, label: str) -> None:
    assert describe(_at(days), now=NOW).label == label


def test_an_unknown_date_says_so_and_is_never_hidden() -> None:
    """The filter hides what is provably old, not what is merely unlabelled."""

    freshness = describe(None, now=NOW)

    assert freshness.days is None
    assert freshness.tone == "unknown"
    assert freshness.label == "date inconnue"
    assert freshness.stale is False


# ----- the inferred date -----


def test_an_inferred_date_is_marked_and_never_shown_as_fresh() -> None:
    """scraped_at is always after the real posting date, so this age understates
    it. Colouring it green would be claiming something we cannot know."""

    real = describe(_at(2), now=NOW)
    inferred = describe(_at(2), inferred=True, now=NOW)

    assert real.tone == "fresh"
    assert inferred.tone != "fresh"
    assert inferred.inferred is True
    assert inferred.label == "vue il y a 2 j"


def test_an_inferred_date_past_the_threshold_is_still_stale() -> None:
    """A lower bound that already exceeds the limit is proof of age, even though
    staying under it is not proof of freshness."""

    assert describe(_at(30), inferred=True, max_age_days=7, now=NOW).stale is True
    assert describe(_at(3), inferred=True, max_age_days=7, now=NOW).stale is False


# ----- the SQL filter and the Python one must agree -----


@pytest.mark.parametrize("days", range(0, 12))
def test_the_sql_cutoff_hides_exactly_what_describe_calls_stale(
    db: sqlite3.Connection, days: int
) -> None:
    """Two implementations of one rule; this is what keeps them one rule."""

    offer_id = _offer(db, suffix=f"cut{days}", posted_at=_at(days))
    db.commit()

    row = db.execute(
        f"SELECT {PUBLISHED_COLUMNS_SQL} FROM offers o WHERE o.id = ?", (offer_id,)
    ).fetchone()
    python_says_stale = describe(
        row["published_at"], max_age_days=7, now=NOW
    ).stale
    sql_keeps_it = (
        db.execute(
            f"SELECT count(*) AS n FROM offers o WHERE o.id = ? AND {NOT_STALE_SQL}",
            (offer_id, stale_cutoff(7, now=NOW)),
        ).fetchone()["n"]
        == 1
    )

    assert python_says_stale is not sql_keeps_it


# ----- ordering -----


def test_recency_ordering_compares_instants_and_not_text(
    db: sqlite3.Connection,
) -> None:
    """The trap: '+02:00' sorts by its local wall clock, so plain text ordering
    puts an offer posted at 00:30 in Paris above one posted an hour later in UTC.
    """

    earlier = _offer(db, suffix="paris", posted_at="2026-08-01T01:30:00.000+02:00")
    later = _offer(db, suffix="utc", posted_at="2026-08-01T00:00:00.000Z")
    db.commit()

    ordered = [
        row["id"]
        for row in db.execute(f"SELECT o.id FROM offers o ORDER BY {RECENT_ORDER_SQL}")
    ]

    # 01:30+02:00 is 23:30 the previous day in UTC, so it is the older of the two.
    assert ordered == [later, earlier]


def test_an_offer_without_posted_at_orders_on_when_it_was_first_seen(
    db: sqlite3.Connection,
) -> None:
    """The alert sources are 408 of 669 rows. Ordering on posted_at alone put
    every one of them in a single NULL block at the bottom."""

    alert = _offer(db, suffix="alert", posted_at=None, scraped_at=_at(1))
    dated = _offer(db, suffix="dated", posted_at=_at(10))
    db.commit()

    ordered = [
        row["id"]
        for row in db.execute(f"SELECT o.id FROM offers o ORDER BY {RECENT_ORDER_SQL}")
    ]

    assert ordered == [alert, dated]


def test_an_unparseable_date_sorts_last_rather_than_first(
    db: sqlite3.Connection,
) -> None:
    fresh = _offer(db, suffix="fresh", posted_at=_at(1))
    broken = _offer(db, suffix="broken", posted_at="bientôt")
    db.commit()

    ordered = [
        row["id"]
        for row in db.execute(f"SELECT o.id FROM offers o ORDER BY {RECENT_ORDER_SQL}")
    ]

    assert ordered == [fresh, broken]


# ----- hiding is not deleting -----


def test_drop_stale_reports_what_it_hid_and_leaves_the_rows_alone() -> None:
    rows = [
        {"id": 1, "published_at": _at(1), "published_inferred": 0},
        {"id": 2, "published_at": _at(40), "published_inferred": 0},
    ]
    from jobpilot.freshness import annotate

    annotated = annotate(rows, max_age_days=7, now=NOW)
    kept, hidden = drop_stale(annotated, include_stale=False)
    shown, none_hidden = drop_stale(annotated, include_stale=True)

    assert [row["id"] for row in kept] == [1]
    assert hidden == 1
    assert [row["id"] for row in shown] == [1, 2]
    assert none_hidden == 0
