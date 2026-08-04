"""Task 42: what the four lists do with recency, end to end.

tests/test_freshness.py covers the rule. This covers the four surfaces that have
to apply it the same way — the review queue, the skim list, the tracker and the
detail page — plus the one place it stops something happening: approving an
offer old enough that generating for it is probably a wasted API call.
"""

from __future__ import annotations

import hashlib
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from jobpilot.apply_flow import APPLICATION_LOCK
from jobpilot.dashboard import create_app, database_connection
from jobpilot.review import applications_by_status, offer_freshness
from jobpilot.skim import skim_offers
from jobpilot.tracker import COLUMNS, tracker_rows

THRESHOLD = 0.35


def _days_ago(days: int) -> str:
    return (datetime.now(UTC) - timedelta(days=days)).isoformat()


def _offer_application(
    db: sqlite3.Connection,
    *,
    suffix: str,
    title: str = "Alternance SOC",
    score: float = 0.8,
    status: str | None = "queued",
    days_old: int | None = 1,
    source: str = "france_travail",
) -> int:
    """One scored offer, with an application unless ``status`` is None.

    ``status=None`` leaves the offer skimmable: the skim list only shows offers
    that have not been promoted or dismissed. ``days_old=None`` means the offer
    carries no posted_at at all, like every LinkedIn and Indeed alert.
    """

    source_id = db.execute(
        "SELECT id FROM sources WHERE name = ?", (source,)
    ).fetchone()["id"]
    company_id = db.execute(
        "INSERT INTO companies (name, city) VALUES (?, 'Lille')", (f"Acme {suffix}",)
    ).lastrowid
    digest = hashlib.sha256(f"recency-{suffix}".encode()).hexdigest()
    offer_id = db.execute(
        "INSERT INTO offers (source_id, company_id, external_id, url, title, "
        "description, contract_type, city, posted_at, scraped_at, content_hash) "
        "VALUES (?, ?, ?, ?, ?, 'Description complète.', 'alternance', 'Lille', "
        "?, ?, ?)",
        (
            source_id,
            company_id,
            f"offer-{suffix}",
            f"https://example.test/jobs/{suffix}",
            title,
            _days_ago(days_old) if days_old is not None else None,
            _days_ago(days_old if days_old is not None else 1),
            digest,
        ),
    ).lastrowid
    db.execute(
        "INSERT INTO match_scores (offer_id, hard_filter_pass, hard_filter_reason, "
        "semantic_score, keyword_score, bonus_score, final_score, scored_at) "
        "VALUES (?, 1, 'ok', 0.2, 0.0, 0.1, ?, ?)",
        (offer_id, score, _days_ago(0)),
    )
    if status is None:
        return int(offer_id)
    return int(
        db.execute(
            "INSERT INTO applications (offer_id, company_id, kind, status, "
            "last_event_at) VALUES (?, ?, 'offer', ?, ?)",
            (offer_id, company_id, status, _days_ago(0)),
        ).lastrowid
    )


@contextmanager
def _client(conn: sqlite3.Connection) -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[database_connection] = lambda: conn
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


# ----- the review queue -----


def test_the_queue_is_ordered_by_recency_and_not_by_score(
    db: sqlite3.Connection,
) -> None:
    """The bug: a three-week 0.72 sat above a one-day 0.61 and stayed there."""

    old_high = _offer_application(db, suffix="oh", score=0.90, days_old=5)
    new_low = _offer_application(db, suffix="nl", score=0.40, days_old=1)
    db.commit()

    rows, _hidden = applications_by_status(db, "queued")

    assert [row["id"] for row in rows] == [new_low, old_high]


def test_score_first_is_still_available_as_a_toggle(db: sqlite3.Connection) -> None:
    old_high = _offer_application(db, suffix="oh", score=0.90, days_old=5)
    new_low = _offer_application(db, suffix="nl", score=0.40, days_old=1)
    db.commit()

    rows, _hidden = applications_by_status(db, "queued", sort="score")

    assert [row["id"] for row in rows] == [old_high, new_low]


def test_every_row_carries_its_age(db: sqlite3.Connection) -> None:
    _offer_application(db, suffix="a", days_old=3)
    db.commit()

    rows, _hidden = applications_by_status(db, "queued")

    assert rows[0]["freshness"]["label"] == "il y a 3 j"
    assert rows[0]["freshness"]["tone"] == "fresh"


def test_the_stale_filter_is_on_by_default_and_hides_rather_than_skips(
    db: sqlite3.Connection,
) -> None:
    fresh = _offer_application(db, suffix="f", days_old=2)
    stale = _offer_application(db, suffix="s", days_old=30)
    db.commit()

    default_rows, hidden = applications_by_status(db, "queued")
    all_rows, none_hidden = applications_by_status(db, "queued", include_stale=True)
    statuses = {
        row["id"]: row["status"]
        for row in db.execute("SELECT id, status FROM applications")
    }

    assert [row["id"] for row in default_rows] == [fresh]
    assert hidden == 1
    assert {row["id"] for row in all_rows} == {fresh, stale}
    assert none_hidden == 0
    # Hidden is all it is: nothing was skipped, nothing was deleted.
    assert statuses == {fresh: "queued", stale: "queued"}


def test_an_offer_with_no_posted_at_falls_back_and_says_so(
    db: sqlite3.Connection,
) -> None:
    """LinkedIn and Indeed alerts carry no date at all — 408 of 669 offers."""

    _offer_application(db, suffix="alert", days_old=None, source="linkedin_alert")
    db.commit()

    rows, _hidden = applications_by_status(db, "queued")
    freshness = rows[0]["freshness"]

    assert freshness["inferred"] is True
    assert freshness["label"].startswith("vue ")
    assert freshness["tone"] != "fresh"


# ----- the skim list -----


def test_the_skim_list_hides_stale_offers_and_still_counts_correctly(
    db: sqlite3.Connection,
) -> None:
    """Filtered in SQL: a page trimmed afterwards would report a total and a
    page count describing rows the reader cannot see."""

    _offer_application(db, suffix="sf", score=0.10, days_old=2, status=None)
    _offer_application(db, suffix="ss", score=0.10, days_old=30, status=None)
    db.commit()

    default_page = skim_offers(db, threshold=THRESHOLD)
    full_page = skim_offers(db, threshold=THRESHOLD, include_stale=True)

    assert default_page.total == 1
    assert len(default_page.rows) == 1
    assert default_page.hidden_stale == 1
    assert full_page.total == 2
    assert full_page.hidden_stale == 0


def test_the_skim_rows_carry_their_age(db: sqlite3.Connection) -> None:
    _offer_application(db, suffix="sk", score=0.10, days_old=1, status=None)
    db.commit()

    page = skim_offers(db, threshold=THRESHOLD)

    assert page.rows[0]["freshness"]["label"] == "hier"


# ----- the tracker -----


def test_the_tracker_defaults_to_the_newest_offer_first(
    db: sqlite3.Connection,
) -> None:
    old = _offer_application(db, suffix="to", days_old=20, status="applied")
    new = _offer_application(db, suffix="tn", days_old=1, status="applied")
    db.commit()

    rows = tracker_rows(db)

    assert [row["application_id"] for row in rows] == [new, old]


def test_the_tracker_shows_everything_by_default_and_can_hide_the_old(
    db: sqlite3.Connection,
) -> None:
    """It answers "where does everything stand"; an answer that quietly omits
    two thirds of the history is not one."""

    _offer_application(db, suffix="ta", days_old=1, status="applied")
    _offer_application(db, suffix="tb", days_old=40, status="applied")
    db.commit()

    assert len(tracker_rows(db)) == 2
    assert len(tracker_rows(db, include_stale=False)) == 1


def test_the_tracker_exports_the_age_it_displays(db: sqlite3.Connection) -> None:
    _offer_application(db, suffix="tc", days_old=3, status="applied")
    db.commit()

    row = tracker_rows(db)[0]
    keys = [key for key, _ in COLUMNS]

    assert "published" in keys
    assert row["published"] == "il y a 3 j"


# ----- the queue page -----


def test_the_queue_page_shows_the_age_column_and_the_toggle(
    dashboard_db: sqlite3.Connection,
) -> None:
    _offer_application(dashboard_db, suffix="p1", days_old=3)
    dashboard_db.commit()

    with _client(dashboard_db) as client:
        page = client.get("/")

    assert "Publiée" in page.text
    assert "il y a 3 j" in page.text
    assert "is-fresh" in page.text
    assert "include_stale" in page.text


def test_the_queue_page_says_how_many_it_hid(
    dashboard_db: sqlite3.Connection,
) -> None:
    _offer_application(dashboard_db, suffix="p2", days_old=1)
    _offer_application(dashboard_db, suffix="p3", days_old=40)
    dashboard_db.commit()

    with _client(dashboard_db) as client:
        default_view = client.get("/")
        full_view = client.get("/?include_stale=1")

    assert "1 offre(s) masquée(s)" in default_view.text
    assert "masquées, pas écartées" in default_view.text
    assert "il y a 40 j" in full_view.text


# ----- generating for a stale offer -----


def test_approving_a_stale_offer_warns_instead_of_generating(
    dashboard_db: sqlite3.Connection,
) -> None:
    """Generation is an API call and ~20 seconds. A closed posting spends both
    for nothing, so the click asks first."""

    with APPLICATION_LOCK:
        application_id = _offer_application(
            dashboard_db, suffix="stale-gen", days_old=30
        )
    dashboard_db.commit()

    with _client(dashboard_db) as client:
        response = client.post(f"/application/{application_id}/approve")

    status = dashboard_db.execute(
        "SELECT status FROM applications WHERE id = ?", (application_id,)
    ).fetchone()["status"]

    assert response.status_code == 409
    assert "il y a 30 j" in response.text
    assert "Générer quand même" in response.text
    # Nothing was generated and nothing moved.
    assert status == "queued"


def test_the_gate_lets_a_fresh_offer_straight_through(
    dashboard_db: sqlite3.Connection,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The warning must not stand between him and the offers he actually wants.

    approve_application is stubbed rather than run: the question here is whether
    the route reaches the generator, and a real generation costs the twenty
    seconds this whole feature exists to stop wasting.
    """

    from jobpilot import dashboard

    with APPLICATION_LOCK:
        application_id = _offer_application(
            dashboard_db, suffix="fresh-gen", days_old=1
        )
    dashboard_db.commit()
    reached: list[int] = []
    monkeypatch.setattr(
        dashboard,
        "approve_application",
        lambda db, app_id, **kwargs: reached.append(app_id),
    )

    with _client(dashboard_db) as client:
        response = client.post(f"/application/{application_id}/approve")

    assert offer_freshness(dashboard_db, application_id).stale is False
    assert reached == [application_id]
    assert "Générer quand même" not in response.text


@pytest.mark.parametrize("days_old", (None, 30))
def test_the_confirmation_lets_the_generation_through(
    dashboard_db: sqlite3.Connection,
    monkeypatch: pytest.MonkeyPatch,
    days_old: int | None,
) -> None:
    """A warning and not a refusal: an old posting is often still open, and he
    is the one who can tell."""

    from jobpilot import dashboard

    with APPLICATION_LOCK:
        application_id = _offer_application(
            dashboard_db, suffix=f"confirm-{days_old}", days_old=days_old
        )
    dashboard_db.commit()
    reached: list[int] = []
    monkeypatch.setattr(
        dashboard,
        "approve_application",
        lambda db, app_id, **kwargs: reached.append(app_id),
    )

    with _client(dashboard_db) as client:
        response = client.post(
            f"/application/{application_id}/approve?confirm_stale=1"
        )

    assert reached == [application_id]
    assert "Générer quand même" not in response.text


def test_an_offer_with_no_date_is_never_stopped_on_a_guess(
    dashboard_db: sqlite3.Connection,
) -> None:
    """An inferred age under the threshold is not proof of freshness, but it is
    not proof of staleness either, and refusing on it would block the alert
    sources entirely."""

    with APPLICATION_LOCK:
        application_id = _offer_application(
            dashboard_db, suffix="undated", days_old=None, source="indeed_alert"
        )
    dashboard_db.commit()

    freshness = offer_freshness(dashboard_db, application_id)

    assert freshness.inferred is True
    assert freshness.stale is False
