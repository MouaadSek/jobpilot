"""Task 41 item 6: a source that has stopped answering must not read as healthy.

Before this, sources.last_run_at was the whole record of ingestion. It ticks
forward on every cycle whatever the cycle did, so WTTJ returning nothing for a
week looked exactly like WTTJ working: a fresh timestamp, and « inconnu (non
enregistré) » in the Résultat column. The only evidence was in logs/.

migration 009 keeps one row per source per run. These tests cover what that row
has to be true about — including on the failure path, where the ingest is rolled
back and the row must not claim the offers it did not keep.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient

from jobpilot.dashboard import create_app, database_connection
from jobpilot.db import source_id
from jobpilot.ingest import ingest_source, record_run
from jobpilot.models import OfferRecord
from jobpilot.scheduler import DEAD_AFTER_FAILURES, scheduler_status, source_runs
from jobpilot.sources.base import Source


class _Fake(Source):
    """A source that yields what it is given, or raises when told to."""

    name = "france_travail"

    def __init__(self, offers: list[OfferRecord], raises: Exception | None = None) -> None:
        self._offers = offers
        self._raises = raises

    def fetch_offers(self) -> Iterator[OfferRecord]:
        yield from self._offers
        if self._raises is not None:
            raise self._raises


def _offer(external_id: str) -> OfferRecord:
    # The title varies with the id: offers are deduped on a content hash as well
    # as on (source_id, external_id), so two identically worded postings are one
    # offer however they are numbered.
    return OfferRecord(
        external_id=external_id,
        url=f"https://example.test/o/{external_id}",
        title=f"Alternance SOC {external_id}",
        description="SIEM, Wazuh, détection",
        company_name="Acme",
        contract_type="alternance",
        city="Lille",
    )


def _rows(db: sqlite3.Connection) -> list[sqlite3.Row]:
    return db.execute(
        "SELECT * FROM source_runs ORDER BY id"
    ).fetchall()


def _fail(db: sqlite3.Connection, name: str = "france_travail", times: int = 1) -> None:
    for index in range(times):
        with pytest.raises(RuntimeError):
            ingest_source(db, _Fake([], raises=RuntimeError(f"HTTP 503 #{index}")))


# ----- the row itself -----


def test_a_successful_run_records_what_it_did(db: sqlite3.Connection) -> None:
    ingest_source(db, _Fake([_offer("a"), _offer("b")]))

    (row,) = _rows(db)

    assert row["fetched"] == 2
    assert row["inserted"] == 2
    assert row["duplicates"] == 0
    assert row["companies_created"] == 1
    assert row["error"] is None
    assert row["started_at"] <= row["finished_at"]


def test_a_second_identical_run_records_duplicates_and_not_inserts(
    db: sqlite3.Connection,
) -> None:
    """Idempotency is a constitution rule; the record has to show it holding."""

    ingest_source(db, _Fake([_offer("a")]))
    ingest_source(db, _Fake([_offer("a")]))

    first, second = _rows(db)

    assert (first["inserted"], first["duplicates"]) == (1, 0)
    assert (second["inserted"], second["duplicates"]) == (0, 1)


def test_a_failed_run_is_recorded_and_claims_nothing_it_rolled_back(
    db: sqlite3.Connection,
) -> None:
    """The row survives the rollback; the inserts do not, so it must say zero."""

    with pytest.raises(RuntimeError):
        ingest_source(db, _Fake([_offer("a")], raises=RuntimeError("HTTP 503")))

    (row,) = _rows(db)
    offers = db.execute("SELECT COUNT(*) AS n FROM offers").fetchone()["n"]

    assert offers == 0
    assert row["inserted"] == 0
    assert row["duplicates"] == 0
    assert row["companies_created"] == 0
    # fetched is kept: the API really did return that record before it broke.
    assert row["fetched"] == 1
    assert "RuntimeError: HTTP 503" in row["error"]


def test_a_failed_run_does_not_move_the_sources_timestamp(
    db: sqlite3.Connection,
) -> None:
    """The timestamp that looked healthy for a week is the one being fixed."""

    _fail(db)

    row = db.execute(
        "SELECT last_run_at FROM sources WHERE name = 'france_travail'"
    ).fetchone()

    assert row["last_run_at"] is None


def test_a_long_error_is_truncated_rather_than_flooding_the_table(
    db: sqlite3.Connection,
) -> None:
    with pytest.raises(RuntimeError):
        ingest_source(db, _Fake([], raises=RuntimeError("x" * 5000)))

    (row,) = _rows(db)

    assert len(row["error"]) <= 240


# ----- the streak -----


def test_a_source_is_not_dead_after_one_failure(db: sqlite3.Connection) -> None:
    _fail(db, times=1)

    entry = next(s for s in source_runs(db) if s["name"] == "france_travail")

    assert entry["consecutive_failures"] == 1
    assert entry["dead"] is False


def test_a_source_that_fails_its_last_n_runs_is_marked_dead(
    db: sqlite3.Connection,
) -> None:
    _fail(db, times=DEAD_AFTER_FAILURES)

    entry = next(s for s in source_runs(db) if s["name"] == "france_travail")

    assert entry["consecutive_failures"] == DEAD_AFTER_FAILURES
    assert entry["dead"] is True
    assert entry["last_run"]["error"]


def test_one_success_resets_the_streak(db: sqlite3.Connection) -> None:
    """« Muette » means still failing, not "failed at some point"."""

    _fail(db, times=DEAD_AFTER_FAILURES)
    ingest_source(db, _Fake([_offer("a")]))

    entry = next(s for s in source_runs(db) if s["name"] == "france_travail")

    assert entry["consecutive_failures"] == 0
    assert entry["dead"] is False


def test_a_run_returning_nothing_is_not_a_failure(db: sqlite3.Connection) -> None:
    """A source can legitimately have nothing new; that is not an error."""

    for _ in range(DEAD_AFTER_FAILURES + 1):
        ingest_source(db, _Fake([]))

    entry = next(s for s in source_runs(db) if s["name"] == "france_travail")

    assert entry["dead"] is False
    assert entry["last_run"]["fetched"] == 0
    assert entry["last_run"]["error"] is None


def test_the_last_run_at_shown_is_the_last_attempt_not_the_last_success(
    db: sqlite3.Connection,
) -> None:
    """A dead source with a stale date and no explanation is the old bug."""

    ingest_source(db, _Fake([_offer("a")]))
    _fail(db, times=1)

    entry = next(s for s in source_runs(db) if s["name"] == "france_travail")
    rows = _rows(db)

    assert entry["last_run_at"] == rows[-1]["started_at"]
    assert entry["last_run"]["error"]


def test_a_source_with_no_history_reports_nothing_rather_than_guessing(
    db: sqlite3.Connection,
) -> None:
    entry = next(s for s in source_runs(db) if s["name"] == "labonnealternance")

    assert entry["last_run"] is None
    assert entry["consecutive_failures"] == 0
    assert entry["dead"] is False


def test_record_run_does_not_commit_on_its_own(db: sqlite3.Connection) -> None:
    """It is called inside the caller's transaction, on both paths."""

    sid = source_id(db, "wttj")
    record_run(db, sid, started_at="2026-08-01T00:00:00+00:00", result=None)
    db.rollback()

    assert _rows(db) == []


# ----- what the queue page says -----


@contextmanager
def _client(conn: sqlite3.Connection) -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[database_connection] = lambda: conn
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_the_queue_page_shows_the_last_result(
    dashboard_db: sqlite3.Connection,
) -> None:
    ingest_source(dashboard_db, _Fake([_offer("a"), _offer("b")]))
    ingest_source(dashboard_db, _Fake([_offer("a"), _offer("b"), _offer("c")]))

    with _client(dashboard_db) as client:
        page = client.get("/")

    assert "reçues" in page.text
    assert "nouvelles" in page.text
    assert "déjà connues" in page.text
    assert "inconnu (aucun cycle enregistré)" in page.text  # the other sources


def test_the_queue_page_marks_a_dead_source(
    dashboard_db: sqlite3.Connection,
) -> None:
    """Visible without reading logs/ — the whole point of the row."""

    _fail(dashboard_db, times=DEAD_AFTER_FAILURES)

    with _client(dashboard_db) as client:
        page = client.get("/")

    assert "muette" in page.text
    assert "run-dead" in page.text
    assert "HTTP 503" in page.text


def test_the_status_payload_carries_the_threshold_it_used(
    db: sqlite3.Connection,
) -> None:
    """The page explains « muette » with the same number the code applied."""

    assert scheduler_status(db)["dead_after_failures"] == DEAD_AFTER_FAILURES
