"""Task 36 item 1: the skim list for below-threshold offers.

Task 35 established why this page exists: alert-sourced offers cannot be scored
(~120-character descriptions, 176 of 235 bank skills scoring zero against them)
and cannot be enriched without scraping, which constitution rule 11 forbids. So
they get read quickly by a human instead of scored better by a machine.
"""

from __future__ import annotations

import hashlib
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from jobpilot.apply_flow import APPLICATION_LOCK
from jobpilot.dashboard import create_app, database_connection
from jobpilot.skim import (
    SkimError,
    available_sources,
    ignore_offer,
    promote_offer,
    skim_offers,
)
from jobpilot.state import current_status

THRESHOLD = 0.35


def _days_ago(days: int) -> str:
    """A posting date relative to now.

    Task 41 gave the lists a staleness filter with a default of seven days, so a
    hard-coded fixture date silently ages past it and the test starts failing on
    a calendar rather than on a change. Relative dates cannot rot that way.
    """

    return (datetime.now(UTC) - timedelta(days=days)).isoformat()


def _offer(
    db: sqlite3.Connection,
    *,
    suffix: str,
    score: float,
    hard_pass: int = 1,
    source: str = "linkedin_alert",
    posted_at: str | None = None,
    title: str = "Alternance Cybersécurité",
    city: str = "Lille",
) -> int:
    source_id = db.execute("SELECT id FROM sources WHERE name = ?", (source,)).fetchone()[
        "id"
    ]
    company_id = db.execute(
        "INSERT INTO companies (name, city) VALUES (?, 'Lille')", (f"Acme {suffix}",)
    ).lastrowid
    digest = hashlib.sha256(f"skim-{suffix}".encode()).hexdigest()
    offer_id = db.execute(
        "INSERT INTO offers (source_id, company_id, external_id, url, title, "
        "description, contract_type, city, posted_at, content_hash) "
        "VALUES (?, ?, ?, ?, ?, 'Description courte.', 'alternance', ?, ?, ?)",
        (
            source_id, company_id, f"offer-{suffix}",
            f"https://example.test/jobs/{suffix}", title, city,
            posted_at if posted_at is not None else _days_ago(1), digest,
        ),
    ).lastrowid
    db.execute(
        "INSERT INTO match_scores (offer_id, hard_filter_pass, hard_filter_reason, "
        "semantic_score, keyword_score, bonus_score, final_score, scored_at) "
        "VALUES (?, ?, ?, 0.2, 0.0, 0.1, ?, '2026-07-20T09:00:00+00:00')",
        (offer_id, hard_pass, None if hard_pass else "location=lyon/unknown", score),
    )
    db.commit()
    return int(offer_id)


def _events(db: sqlite3.Connection, application_id: int) -> list[str]:
    return [
        row["event"]
        for row in db.execute(
            "SELECT event FROM events WHERE application_id = ? ORDER BY id",
            (application_id,),
        )
    ]


@contextmanager
def _client(db: sqlite3.Connection, tmp_path: Path) -> Iterator[TestClient]:
    app = create_app(output_root=tmp_path)

    def connection() -> Iterator[sqlite3.Connection]:
        with APPLICATION_LOCK:
            yield db

    app.dependency_overrides[database_connection] = connection
    with TestClient(app) as client:
        yield client


# ----- who belongs on the list -----


def test_only_below_threshold_filter_passers_are_listed(db: sqlite3.Connection) -> None:
    below = _offer(db, suffix="below", score=0.12)
    _offer(db, suffix="above", score=0.61)
    _offer(db, suffix="rejected", score=0.05, hard_pass=0)

    page = skim_offers(db, threshold=THRESHOLD)

    assert [row["offer_id"] for row in page.rows] == [below]
    assert page.total == 1


def test_an_offer_that_failed_the_hard_filter_never_appears(
    db: sqlite3.Connection,
) -> None:
    """It was rejected on contract, location or duration. Skimming cannot help."""

    _offer(db, suffix="rejected", score=0.01, hard_pass=0)

    assert skim_offers(db, threshold=THRESHOLD).rows == ()
    assert skim_offers(db, threshold=THRESHOLD, include_ignored=True).rows == ()


def test_the_newest_offer_comes_first_and_score_sorting_is_available(
    db: sqlite3.Connection,
) -> None:
    old_high = _offer(db, suffix="old", score=0.30, posted_at=_days_ago(60))
    new_low = _offer(db, suffix="new", score=0.05, posted_at=_days_ago(1))

    # include_stale: this test is about the ordering, and the 60-day offer is
    # hidden by the staleness filter otherwise.
    assert [
        r["offer_id"]
        for r in skim_offers(db, threshold=THRESHOLD, include_stale=True).rows
    ] == [new_low, old_high]
    assert [
        r["offer_id"]
        for r in skim_offers(
            db, sort="score", threshold=THRESHOLD, include_stale=True
        ).rows
    ] == [old_high, new_low]


def test_an_unknown_sort_falls_back_rather_than_erroring(db: sqlite3.Connection) -> None:
    _offer(db, suffix="a", score=0.1)

    page = skim_offers(db, sort="'; DROP TABLE offers; --", threshold=THRESHOLD)

    assert page.sort == "recent"
    assert page.total == 1


def test_filtering_by_source(db: sqlite3.Connection) -> None:
    linked = _offer(db, suffix="li", score=0.1, source="linkedin_alert")
    _offer(db, suffix="ft", score=0.1, source="france_travail")

    page = skim_offers(db, source="linkedin_alert", threshold=THRESHOLD)

    assert [row["offer_id"] for row in page.rows] == [linked]
    assert set(available_sources(db, threshold=THRESHOLD)) == {
        "linkedin_alert", "france_travail",
    }


def test_pagination_slices_and_clamps(db: sqlite3.Connection) -> None:
    for index in range(7):
        _offer(db, suffix=f"p{index}", score=0.1)

    first = skim_offers(db, per_page=3, threshold=THRESHOLD)
    last = skim_offers(db, per_page=3, page=99, threshold=THRESHOLD)

    assert first.total == 7 and first.pages == 3 and len(first.rows) == 3
    assert first.has_next and not first.has_previous
    assert last.page == 3 and len(last.rows) == 1
    assert last.has_previous and not last.has_next


# ----- promoting -----


def test_promoting_creates_a_queued_application_and_says_where_it_came_from(
    db: sqlite3.Connection,
) -> None:
    offer_id = _offer(db, suffix="promote", score=0.12)

    application_id = promote_offer(db, offer_id, threshold=THRESHOLD)

    assert current_status(db, application_id) == "queued"
    row = db.execute(
        "SELECT offer_id, kind FROM applications WHERE id = ?", (application_id,)
    ).fetchone()
    assert row["offer_id"] == offer_id
    assert row["kind"] == "offer"
    assert _events(db, application_id) == ["queued_from_skim"]
    # And it leaves the skim list, because it is now in the review flow.
    assert skim_offers(db, threshold=THRESHOLD).rows == ()


def test_promoting_twice_is_idempotent(db: sqlite3.Connection) -> None:
    offer_id = _offer(db, suffix="twice", score=0.12)

    first = promote_offer(db, offer_id, threshold=THRESHOLD)
    second = promote_offer(db, offer_id, threshold=THRESHOLD)

    assert first == second
    assert db.execute("SELECT count(*) AS n FROM applications").fetchone()["n"] == 1
    assert _events(db, first) == ["queued_from_skim"]


def test_an_offer_above_threshold_cannot_be_promoted_from_here(
    db: sqlite3.Connection,
) -> None:
    offer_id = _offer(db, suffix="high", score=0.9)

    with pytest.raises(SkimError, match="above the queue threshold"):
        promote_offer(db, offer_id, threshold=THRESHOLD)


def test_a_hard_filter_reject_cannot_be_promoted(db: sqlite3.Connection) -> None:
    offer_id = _offer(db, suffix="rej", score=0.01, hard_pass=0)

    with pytest.raises(SkimError, match="hard filter"):
        promote_offer(db, offer_id, threshold=THRESHOLD)


def test_an_unknown_offer_is_refused(db: sqlite3.Connection) -> None:
    with pytest.raises(SkimError, match="no scored offer"):
        promote_offer(db, 4242, threshold=THRESHOLD)


# ----- ignoring -----


def test_ignoring_persists_as_a_skipped_application(db: sqlite3.Connection) -> None:
    """Persisted, not hidden client-side: the decision has to survive a reload."""

    offer_id = _offer(db, suffix="ignore", score=0.12)

    application_id = ignore_offer(db, offer_id, threshold=THRESHOLD)

    assert current_status(db, application_id) == "skipped"
    assert _events(db, application_id) == ["queued_from_skim", "status_change"]
    assert skim_offers(db, threshold=THRESHOLD).rows == ()


def test_an_ignored_offer_is_visible_again_only_on_request(
    db: sqlite3.Connection,
) -> None:
    offer_id = _offer(db, suffix="shown", score=0.12)
    ignore_offer(db, offer_id, threshold=THRESHOLD)

    hidden = skim_offers(db, threshold=THRESHOLD)
    shown = skim_offers(db, include_ignored=True, threshold=THRESHOLD)

    assert hidden.rows == ()
    assert [row["offer_id"] for row in shown.rows] == [offer_id]
    assert shown.rows[0]["application_status"] == "skipped"


def test_ignoring_twice_is_idempotent(db: sqlite3.Connection) -> None:
    offer_id = _offer(db, suffix="twice-ignore", score=0.12)

    first = ignore_offer(db, offer_id, threshold=THRESHOLD)
    second = ignore_offer(db, offer_id, threshold=THRESHOLD)

    assert first == second
    assert current_status(db, first) == "skipped"


def test_ignoring_an_already_queued_offer_goes_through_the_state_machine(
    db: sqlite3.Connection,
) -> None:
    offer_id = _offer(db, suffix="queued-then-ignored", score=0.12)
    application_id = promote_offer(db, offer_id, threshold=THRESHOLD)

    ignore_offer(db, offer_id, threshold=THRESHOLD)

    assert current_status(db, application_id) == "skipped"
    assert _events(db, application_id) == ["queued_from_skim", "status_change"]


# ----- the page -----


def test_the_page_lists_offers_and_offers_both_actions(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    with APPLICATION_LOCK:
        offer_id = _offer(dashboard_db, suffix="page", score=0.12)

    with _client(dashboard_db, tmp_path) as client:
        page = client.get("/skim")

    assert page.status_code == 200
    assert "Alternance Cybersécurité" in page.text
    assert f"/skim/{offer_id}/queue" in page.text
    assert f"/skim/{offer_id}/ignore" in page.text
    assert "Mettre en file" in page.text


def test_the_page_is_reachable_from_the_navigation(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    with _client(dashboard_db, tmp_path) as client:
        assert 'href="/skim"' in client.get("/").text


def test_posting_queue_promotes_and_returns_to_the_same_slice(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    with APPLICATION_LOCK:
        offer_id = _offer(dashboard_db, suffix="post-queue", score=0.12)

    with _client(dashboard_db, tmp_path) as client:
        response = client.post(
            f"/skim/{offer_id}/queue?page=1&sort=score&source=linkedin_alert",
            follow_redirects=False,
        )

    assert response.status_code == 303
    location = response.headers["location"]
    assert location.startswith("/skim?")
    assert "sort=score" in location and "source=linkedin_alert" in location
    application_id = dashboard_db.execute(
        "SELECT id FROM applications WHERE offer_id = ?", (offer_id,)
    ).fetchone()["id"]
    assert current_status(dashboard_db, application_id) == "queued"


def test_posting_ignore_persists_across_a_reload(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    with APPLICATION_LOCK:
        offer_id = _offer(dashboard_db, suffix="post-ignore", score=0.12)

    with _client(dashboard_db, tmp_path) as client:
        client.post(f"/skim/{offer_id}/ignore")
        reloaded = client.get("/skim")

    assert "Alternance Cybersécurité" not in reloaded.text
    application_id = dashboard_db.execute(
        "SELECT id FROM applications WHERE offer_id = ?", (offer_id,)
    ).fetchone()["id"]
    assert current_status(dashboard_db, application_id) == "skipped"


def test_an_invalid_action_reports_instead_of_500ing(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    with APPLICATION_LOCK:
        offer_id = _offer(dashboard_db, suffix="invalid", score=0.9)

    with _client(dashboard_db, tmp_path) as client:
        response = client.post(f"/skim/{offer_id}/queue")

    assert response.status_code == 200
    assert "seuil" in response.text or "threshold" in response.text


def test_the_empty_state_says_what_to_do_next(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    with _client(dashboard_db, tmp_path) as client:
        page = client.get("/skim")

    assert "Actualiser les offres" in page.text
