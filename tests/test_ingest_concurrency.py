"""Task 41 follow-up: the write lock is not held across the network.

Task 41 put WAL and a busy timeout on the connection, which stops the daemon and
the dashboard blocking each other's *reads*. It did not fix the writer:
ingest_source opened its transaction at the first insert and committed at the
end, so the transaction was held across ``fetch_offers`` — a paginated HTTP walk
with per-domain rate limiting in it. Under WAL there is exactly one writer, so a
dashboard generation starting mid-cycle waited for the whole walk and then
failed with "database is locked" after db.BUSY_TIMEOUT_MS.

The fix is to drain the source into memory first and open the transaction after,
rather than committing per page — that keeps ingest_source's all-or-nothing
commit, which the constitution's idempotency rule is written against.

These tests use a real database file rather than the in-memory fixture the
constitution asks for, because the property under test is two connections
contending for one file's write lock and ``:memory:`` gives each connection its
own database. It is the one thing in-memory cannot express.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest

from jobpilot.db import connect, init_db
from jobpilot.ingest import ingest_source
from jobpilot.models import OfferRecord
from jobpilot.sources.base import Source

#: Short on purpose. The real timeout is 30 s; if the lock were still held
#: across the fetch this makes the test fail in a fifth of a second instead of
#: hanging for thirty.
PROBE_TIMEOUT_MS = 200


def _offer(external_id: str) -> OfferRecord:
    return OfferRecord(
        external_id=external_id,
        url=f"https://example.test/o/{external_id}",
        title=f"Alternance SOC {external_id}",
        description="SIEM, Wazuh, détection",
        company_name=f"Acme {external_id}",
        contract_type="alternance",
        city="Lille",
    )


@pytest.fixture
def live_db(tmp_path: Path) -> Iterator[sqlite3.Connection]:
    """A real file, so a second connection contends for the same write lock."""

    conn = init_db(tmp_path / "jobpilot.db")
    yield conn
    conn.close()


class _Observed(Source):
    """A source that runs a callback between yields, as the network would."""

    name = "france_travail"

    def __init__(
        self,
        offers: list[OfferRecord],
        between: object,
        raises: Exception | None = None,
    ) -> None:
        self._offers = offers
        self._between = between
        self._raises = raises

    def fetch_offers(self) -> Iterator[OfferRecord]:
        for offer in self._offers:
            self._between()  # what the dashboard is doing meanwhile
            yield offer
        if self._raises is not None:
            raise self._raises


def test_a_second_writer_is_not_blocked_while_the_source_is_fetching(
    live_db: sqlite3.Connection, tmp_path: Path
) -> None:
    """The bug, reproduced: this is the dashboard generating mid-cycle."""

    dashboard = connect(tmp_path / "jobpilot.db")
    dashboard.execute(f"PRAGMA busy_timeout = {PROBE_TIMEOUT_MS}")
    blocked: list[str] = []
    open_transactions: list[bool] = []

    def probe() -> None:
        open_transactions.append(live_db.in_transaction)
        try:
            dashboard.execute("INSERT INTO companies (name) VALUES ('Probe')")
            dashboard.commit()
        except sqlite3.OperationalError as exc:  # pragma: no cover - the old bug
            blocked.append(str(exc))
            dashboard.rollback()

    try:
        ingest_source(live_db, _Observed([_offer("a"), _offer("b")], probe))
    finally:
        dashboard.close()

    assert blocked == []
    # The direct statement of the property: no transaction was open at any point
    # during the fetch, so there was no lock for the other writer to wait on.
    assert open_transactions == [False, False]


def test_the_ingest_still_commits_all_or_nothing(
    live_db: sqlite3.Connection,
) -> None:
    """Draining buys the lock back without giving up atomicity — which is what
    committing per page would have cost, and what idempotency is written on.

    A regression guard rather than a test of the fix: this passed before the
    change too, which is exactly the point of keeping it.
    """

    def noop() -> None:
        return None

    with pytest.raises(RuntimeError):
        ingest_source(
            live_db,
            _Observed([_offer("a"), _offer("b")], noop, raises=RuntimeError("HTTP 503")),
        )

    offers = live_db.execute("SELECT count(*) AS n FROM offers").fetchone()["n"]
    companies = live_db.execute("SELECT count(*) AS n FROM companies").fetchone()["n"]

    assert offers == 0
    assert companies == 0


def test_a_walk_that_dies_midway_still_reports_what_arrived(
    live_db: sqlite3.Connection,
) -> None:
    """fetched is counted as records arrive, not from len(), so the failed
    source_runs row distinguishes "returned nothing" from "died on page three".

    The reason _drain accumulates in a loop instead of calling list(): with
    list() a walk that raised would report zero fetched, losing the one piece of
    evidence that separates a dead source from a broken one.
    """

    def noop() -> None:
        return None

    with pytest.raises(RuntimeError):
        ingest_source(
            live_db,
            _Observed([_offer("a"), _offer("b")], noop, raises=RuntimeError("HTTP 503")),
        )

    row = live_db.execute("SELECT fetched, inserted, error FROM source_runs").fetchone()

    assert row["fetched"] == 2
    assert row["inserted"] == 0
    assert "HTTP 503" in row["error"]


def test_nothing_is_written_before_the_source_has_finished_talking(
    live_db: sqlite3.Connection, tmp_path: Path
) -> None:
    """A reader mid-cycle never sees a half-ingested set.

    This holds under WAL either way — an uncommitted row is invisible to another
    connection whether or not the writer drained first — so it does not
    discriminate the fix. It is here because it is the property the dashboard
    actually depends on while the daemon runs, and it would be worth knowing if
    a later change to the commit boundary broke it.
    """

    reader = connect(tmp_path / "jobpilot.db")
    seen: list[int] = []

    def probe() -> None:
        seen.append(reader.execute("SELECT count(*) AS n FROM offers").fetchone()["n"])

    try:
        ingest_source(live_db, _Observed([_offer("a"), _offer("b")], probe))
        after = reader.execute("SELECT count(*) AS n FROM offers").fetchone()["n"]
    finally:
        reader.close()

    assert seen == [0, 0]
    assert after == 2
