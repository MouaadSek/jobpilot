"""Re-running ingest must never duplicate rows (constitution idempotency rule)."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator

from jobpilot.ingest import ingest_source
from jobpilot.models import OfferRecord
from jobpilot.sources.base import Source


class FakeSource(Source):
    name = "france_travail"

    def __init__(self, offers: list[OfferRecord]) -> None:
        self._offers = offers

    def fetch_offers(self) -> Iterator[OfferRecord]:
        yield from self._offers


def _sample() -> list[OfferRecord]:
    return [
        OfferRecord(external_id="1", url="https://x/1", title="Alternance SOC",
                    company_name="ACME", description="azure").normalized(),
        OfferRecord(external_id="2", url="https://x/2", title="Stage Pentest",
                    company_name="ACME", description="python").normalized(),
    ]


def test_first_run_inserts_all(db: sqlite3.Connection) -> None:
    res = ingest_source(db, FakeSource(_sample()))
    assert res.inserted == 2
    assert res.duplicates == 0
    assert db.execute("SELECT count(*) AS n FROM offers").fetchone()["n"] == 2


def test_second_run_inserts_nothing(db: sqlite3.Connection) -> None:
    ingest_source(db, FakeSource(_sample()))
    res = ingest_source(db, FakeSource(_sample()))
    assert res.inserted == 0
    assert res.duplicates == 2
    assert db.execute("SELECT count(*) AS n FROM offers").fetchone()["n"] == 2


def test_company_deduped_across_offers_and_runs(db: sqlite3.Connection) -> None:
    ingest_source(db, FakeSource(_sample()))
    ingest_source(db, FakeSource(_sample()))
    # Both offers share company ACME -> exactly one company row.
    assert db.execute("SELECT count(*) AS n FROM companies").fetchone()["n"] == 1


def test_last_run_at_updated(db: sqlite3.Connection) -> None:
    ingest_source(db, FakeSource(_sample()))
    row = db.execute(
        "SELECT last_run_at FROM sources WHERE name = 'france_travail'"
    ).fetchone()
    assert row["last_run_at"] is not None
