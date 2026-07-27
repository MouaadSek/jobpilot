"""Dashboard-triggered refresh: single flight, honest per-source results."""

from __future__ import annotations

import sqlite3
import threading
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path

from fastapi.testclient import TestClient

from jobpilot.apply_flow import APPLICATION_LOCK
from jobpilot.config import MissingCredentialError
from jobpilot.dashboard import create_app, database_connection
from jobpilot.models import OfferRecord
from jobpilot.refresh import RefreshRunner
from jobpilot.sources.base import Source


class _FakeSource(Source):
    """A source that yields fixed records; no network, no rate limiting needed."""

    def __init__(self, name: str, offers: list[OfferRecord]) -> None:
        self.name = name
        self._offers = offers
        self.gate: threading.Event | None = None

    def fetch_offers(self) -> Iterator[OfferRecord]:
        if self.gate is not None:
            self.gate.wait(timeout=5)
        yield from self._offers


def _offer(suffix: str) -> OfferRecord:
    return OfferRecord(
        external_id=f"ext-{suffix}",
        url=f"https://example.test/jobs/{suffix}",
        title=f"Analyste SOC {suffix}",
        company_name="Acme",
        description="Surveillance SIEM, detection d'incidents et reponse.",
        contract_type="alternance",
        city="Lille",
    ).normalized()


def _runner(
    db: sqlite3.Connection,
    *,
    sources: dict[str, _FakeSource | Exception],
    score_pass: Callable[[sqlite3.Connection, object], int] | None = None,
    model_loader: Callable[[], object] | None = None,
) -> RefreshRunner:
    @contextmanager
    def factory() -> Iterator[sqlite3.Connection]:
        yield db

    def builder(name: str) -> Source:
        built = sources[name]
        if isinstance(built, Exception):
            raise built
        return built

    return RefreshRunner(
        connection_factory=factory,
        source_names=lambda: list(sources),
        source_builder=builder,
        model_loader=model_loader or (lambda: (lambda text: [0.1, 0.2, 0.3])),
        score_pass=score_pass or (lambda db, embed_fn: 0),
    )


@contextmanager
def _client(db: sqlite3.Connection, runner: RefreshRunner) -> Iterator[TestClient]:
    app = create_app(output_root=Path("unused"), refresh_runner=runner)

    def in_memory_connection() -> Iterator[sqlite3.Connection]:
        with APPLICATION_LOCK:
            yield db

    app.dependency_overrides[database_connection] = in_memory_connection
    with TestClient(app) as client:
        yield client


def test_second_refresh_returns_conflict_and_never_runs_in_parallel(
    dashboard_db: sqlite3.Connection,
) -> None:
    gate = threading.Event()
    blocked = _FakeSource("france_travail", [_offer("single-flight")])
    blocked.gate = gate
    runs: list[int] = []

    def counting_score(db: sqlite3.Connection, embed_fn: object) -> int:
        runs.append(len(runs) + 1)
        return 0

    runner = _runner(
        dashboard_db,
        sources={"france_travail": blocked},
        score_pass=counting_score,
    )

    with _client(dashboard_db, runner) as client:
        first = client.post("/refresh")
        second = client.post("/refresh")
        gate.set()
        assert runner.wait(timeout=5)
        third = client.post("/refresh")
        assert runner.wait(timeout=5)

    assert first.status_code == 202
    assert first.json()["running"] is True
    assert second.status_code == 409
    assert "already running" in second.json()["detail"]
    # The conflicting POST started nothing: only the two accepted runs scored.
    assert third.status_code == 202
    assert len(runs) == 2


def test_failing_source_does_not_hide_the_others_results(
    dashboard_db: sqlite3.Connection,
) -> None:
    class _Exploding(_FakeSource):
        def fetch_offers(self) -> Iterator[OfferRecord]:
            raise RuntimeError("upstream returned 503")
            yield  # pragma: no cover - generator marker

    runner = _runner(
        dashboard_db,
        sources={
            "france_travail": _FakeSource("france_travail", [_offer("ok-1")]),
            "wttj": _Exploding("wttj", []),
            "linkedin_alert": MissingCredentialError("Gmail IMAP credentials missing"),
        },
    )

    with _client(dashboard_db, runner) as client:
        assert client.post("/refresh").status_code == 202
        assert runner.wait(timeout=5)
        status = client.get("/refresh/status").json()

    by_name = {source["name"]: source for source in status["sources"]}
    assert by_name["france_travail"]["state"] == "done"
    assert by_name["france_travail"]["fetched"] == 1
    assert by_name["france_travail"]["inserted"] == 1
    assert by_name["france_travail"]["duplicates"] == 0
    assert by_name["wttj"]["state"] == "failed"
    assert "503" in by_name["wttj"]["message"]
    assert by_name["linkedin_alert"]["state"] == "skipped"
    assert "credentials missing" in by_name["linkedin_alert"]["message"]
    assert status["running"] is False
    assert status["error"] is None


def test_refresh_scores_after_ingest_and_the_queue_shows_new_offers(
    dashboard_db: sqlite3.Connection,
) -> None:
    seen: list[int] = []

    def score_pass(db: sqlite3.Connection, embed_fn: object) -> int:
        rows = db.execute(
            "SELECT o.id, o.company_id FROM offers o "
            "LEFT JOIN applications a ON a.offer_id = o.id WHERE a.id IS NULL"
        ).fetchall()
        seen.append(len(rows))
        for row in rows:
            db.execute(
                "INSERT INTO applications (offer_id, company_id, kind, status) "
                "VALUES (?, ?, 'offer', 'queued')",
                (row["id"], row["company_id"]),
            )
        db.commit()
        return len(rows)

    runner = _runner(
        dashboard_db,
        sources={
            "france_travail": _FakeSource(
                "france_travail", [_offer("queued-a"), _offer("queued-b")]
            )
        },
        score_pass=score_pass,
    )

    with _client(dashboard_db, runner) as client:
        assert client.post("/refresh").status_code == 202
        assert runner.wait(timeout=5)
        status = client.get("/refresh/status").json()
        queue = client.get("/")

    # Scoring ran after ingest: it saw both freshly inserted offers.
    assert seen == [2]
    assert status["queued"] == 2
    assert status["stage"] == "done"
    assert "Analyste SOC queued-a" in queue.text
    assert "Analyste SOC queued-b" in queue.text


def test_repeated_refresh_is_idempotent_and_reports_duplicates(
    dashboard_db: sqlite3.Connection,
) -> None:
    source = _FakeSource("france_travail", [_offer("idempotent")])
    runner = _runner(dashboard_db, sources={"france_travail": source})

    with _client(dashboard_db, runner) as client:
        client.post("/refresh")
        assert runner.wait(timeout=5)
        client.post("/refresh")
        assert runner.wait(timeout=5)
        status = client.get("/refresh/status").json()

    assert status["sources"][0]["inserted"] == 0
    assert status["sources"][0]["duplicates"] == 1
    assert dashboard_db.execute("SELECT count(*) AS n FROM offers").fetchone()["n"] == 1


def test_queue_page_renders_the_refresh_control_and_current_state(
    dashboard_db: sqlite3.Connection,
) -> None:
    runner = _runner(
        dashboard_db,
        sources={"france_travail": _FakeSource("france_travail", [])},
    )

    with _client(dashboard_db, runner) as client:
        page = client.get("/")

    assert page.status_code == 200
    assert 'id="refresh-button"' in page.text
    assert "Actualiser les offres" in page.text
    assert "/refresh/status" in page.text


def test_model_load_is_reported_as_its_own_stage_before_scoring(
    dashboard_db: sqlite3.Connection,
) -> None:
    """The first refresh is slow because of the model; say so instead of hanging."""

    observed: list[str] = []

    def model_loader() -> object:
        observed.append(runner.status().stage)
        return object()

    def score_pass(db: sqlite3.Connection, embed_fn: object) -> int:
        observed.append(runner.status().stage)
        return 0

    runner = _runner(
        dashboard_db, sources={}, score_pass=score_pass, model_loader=model_loader
    )
    runner.start()

    assert runner.wait(timeout=5)
    assert observed == ["loading_model", "scoring"]


def test_scoring_failure_is_surfaced_and_does_not_wedge_the_runner(
    dashboard_db: sqlite3.Connection,
) -> None:
    def failing_score(db: sqlite3.Connection, embed_fn: object) -> int:
        raise RuntimeError("embedding backend unavailable")

    runner = _runner(
        dashboard_db,
        sources={"france_travail": _FakeSource("france_travail", [_offer("score-fail")])},
        score_pass=failing_score,
    )

    with _client(dashboard_db, runner) as client:
        assert client.post("/refresh").status_code == 202
        assert runner.wait(timeout=5)
        status = client.get("/refresh/status").json()
        again = client.post("/refresh")

    assert status["running"] is False
    assert "embedding backend unavailable" in status["error"]
    assert status["sources"][0]["state"] == "done"
    assert again.status_code == 202  # a failed run releases the single flight
