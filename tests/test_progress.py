"""Task 36 item 6: live progress for the slow operations.

Generation, regeneration and apply all run *inside* the request, holding
APPLICATION_LOCK for their whole duration. That is why the registry is in memory
rather than in SQLite and why /progress touches no database: a progress row in
the database could not be read until the thing it describes had finished.
"""

from __future__ import annotations

import re
import sqlite3
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from jobpilot.apply_flow import APPLICATION_LOCK
from jobpilot.dashboard import create_app, database_connection
from jobpilot.progress import (
    MIN_POLL_INTERVAL_MS,
    REGISTRY,
    ProgressRegistry,
    refresh_operation,
    track,
)
from tests.test_dashboard import _offer_application
from tests.test_tailoring import _Advisor, _Toolchain

_ROOT = Path(__file__).resolve().parents[1] / "src" / "jobpilot"
# Item 7 split the single template into a shell, a script partial and a
# stylesheet. These snapshots follow the markup to the file that now owns it.
SHELL = _ROOT / "templates" / "base.html"
SCRIPT = _ROOT / "templates" / "partials" / "console.js.html"
STYLESHEET = _ROOT / "static" / "console.css"


@pytest.fixture(autouse=True)
def _clean_registry() -> Iterator[None]:
    REGISTRY.clear()
    yield
    REGISTRY.clear()


@contextmanager
def _client(
    db: sqlite3.Connection, tmp_path: Path, *, toolchain: object | None = None
) -> Iterator[TestClient]:
    app = create_app(
        advisor=_Advisor(),
        toolchain=toolchain or _Toolchain(),
        output_root=tmp_path,
    )

    def connection() -> Iterator[sqlite3.Connection]:
        with APPLICATION_LOCK:
            yield db

    app.dependency_overrides[database_connection] = connection
    with TestClient(app) as client:
        yield client


# ----- the registry -----


def test_an_operation_is_visible_while_it_runs() -> None:
    registry = ProgressRegistry()

    with track("k", "Génération", step="Analyse", registry=registry):
        (running,) = registry.snapshot()
        assert running["label"] == "Génération"
        assert running["step"] == "Analyse"
        assert running["running"] is True
        assert running["error"] is None

    (finished,) = registry.snapshot()
    assert finished["running"] is False
    assert finished["step"] == "Terminé"


def test_advancing_reports_which_step_and_how_far() -> None:
    registry = ProgressRegistry()

    with track("k", "Actualisation", total=6, registry=registry) as progress:
        progress.advance("france_travail", done=3)
        (snapshot,) = registry.snapshot()

    assert snapshot["step"] == "france_travail"
    assert snapshot["done"] == 3
    assert snapshot["total"] == 6


def test_a_failure_closes_the_operation_and_keeps_its_message() -> None:
    """A failure that never cleared its progress would leave the page claiming
    work was still happening forever."""

    registry = ProgressRegistry()

    with pytest.raises(RuntimeError), track("k", "Génération", registry=registry):
        raise RuntimeError("orphan quality gate failed")

    (snapshot,) = registry.snapshot()
    assert snapshot["running"] is False
    assert snapshot["step"] == "Échec"
    assert snapshot["error"] == "orphan quality gate failed"


def test_elapsed_time_is_reported() -> None:
    registry = ProgressRegistry()
    registry.start("k", "Génération")

    later = datetime.now(UTC) + timedelta(seconds=42)
    (snapshot,) = registry.snapshot(now=later)

    assert snapshot["elapsed_seconds"] >= 42.0


def test_a_finished_operation_is_eventually_pruned() -> None:
    """It stays briefly so a poll landing just after completion sees the
    outcome, then goes: an operation that is not running has no progress."""

    registry = ProgressRegistry()
    with track("k", "Génération", registry=registry):
        pass

    assert len(registry.snapshot()) == 1
    assert registry.snapshot(now=datetime.now(UTC) + timedelta(minutes=5)) == []


def test_advancing_an_unknown_or_finished_operation_is_ignored() -> None:
    registry = ProgressRegistry()
    registry.advance("nope", step="x")
    with track("k", "Génération", registry=registry):
        pass
    registry.advance("k", step="too late")

    assert registry.snapshot()[0]["step"] == "Terminé"


def test_two_operations_are_tracked_independently() -> None:
    registry = ProgressRegistry()

    with track("generate:1", "Un", registry=registry):
        with track("generate:2", "Deux", registry=registry):
            assert len(registry.snapshot()) == 2


# ----- refresh, in the same shape -----


def test_a_refresh_snapshot_becomes_a_per_source_operation() -> None:
    operation = refresh_operation(
        {
            "running": True,
            "stage": "ingesting",
            "started_at": datetime.now(UTC).isoformat(),
            "finished_at": None,
            "error": None,
            "sources": [
                {"name": "france_travail", "state": "done"},
                {"name": "labonnealternance", "state": "running"},
                {"name": "wttj", "state": "pending"},
            ],
        }
    )

    assert operation is not None
    assert operation["label"] == "Actualisation des offres"
    assert operation["step"] == "labonnealternance 1/3"
    assert operation["total"] == 3
    assert operation["running"] is True


def test_a_refresh_that_never_started_is_not_an_operation() -> None:
    assert refresh_operation({"running": False, "started_at": None}) is None


# ----- the endpoint -----


def test_the_progress_endpoint_reports_nothing_when_idle(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    with _client(dashboard_db, tmp_path) as client:
        body = client.get("/progress").json()

    assert body["operations"] == []
    assert body["poll_interval_ms"] == MIN_POLL_INTERVAL_MS >= 1000


def test_generation_is_visible_from_another_request_while_it_runs(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    """The point of the whole item: the writer lock is held, and /progress still
    answers."""

    with APPLICATION_LOCK:
        application_id = _offer_application(
            dashboard_db, title="Analyste SOC", score=0.9, suffix="prog"
        )

    in_generation = threading.Event()
    may_finish = threading.Event()
    seen: dict[str, object] = {}

    class _BlockingToolchain(_Toolchain):
        def generate_cv_pdf(self, tailored_path: Path, output_path: Path) -> None:
            in_generation.set()
            assert may_finish.wait(10)
            super().generate_cv_pdf(tailored_path, output_path)

    app = create_app(
        advisor=_Advisor(), toolchain=_BlockingToolchain(), output_root=tmp_path
    )

    def connection() -> Iterator[sqlite3.Connection]:
        yield dashboard_db  # no APPLICATION_LOCK: the endpoint takes it itself

    app.dependency_overrides[database_connection] = connection

    with TestClient(app) as client:
        worker = threading.Thread(
            target=lambda: client.post(f"/application/{application_id}/approve")
        )
        worker.start()
        assert in_generation.wait(10)
        seen["body"] = client.get("/progress").json()
        may_finish.set()
        worker.join(20)

    operations = seen["body"]["operations"]  # type: ignore[index]
    assert len(operations) == 1
    assert operations[0]["key"] == f"generate:{application_id}"
    assert operations[0]["running"] is True
    assert "Rédaction" in operations[0]["step"]
    assert operations[0]["elapsed_seconds"] >= 0


def test_a_generation_failure_is_reported_in_the_interface_voice(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    """Task 34's rule: the validator's own message, verbatim, not 'Error: 500'."""

    with APPLICATION_LOCK:
        application_id = _offer_application(
            dashboard_db, title="Analyste SOC", score=0.9, suffix="prog-fail"
        )

    with _client(
        dashboard_db, tmp_path, toolchain=_Toolchain(fail_validate=True)
    ) as client:
        response = client.post(f"/application/{application_id}/approve")
        body = client.get("/progress").json()

    assert response.status_code == 422
    assert "validate_cv.py failed" in response.text
    (operation,) = body["operations"]
    assert operation["running"] is False
    assert operation["step"] == "Échec"
    assert "validate_cv.py failed" in operation["error"]


def test_the_progress_endpoint_touches_no_database(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    """It must answer while a generation holds the writer lock."""

    app = create_app(output_root=tmp_path)

    def refuse() -> Iterator[sqlite3.Connection]:
        raise AssertionError("/progress must not open a database connection")
        yield  # pragma: no cover

    app.dependency_overrides[database_connection] = refuse

    with TestClient(app) as client:
        assert client.get("/progress").status_code == 200


# ----- the page contract -----


def test_no_polling_loop_is_faster_than_one_hertz() -> None:
    markup = SCRIPT.read_text(encoding="utf-8")

    intervals = [int(value) for value in re.findall(r"setInterval\([^,]+,\s*(\d+)", markup)]

    assert intervals, "expected at least one polling loop"
    assert all(value >= 1000 for value in intervals), intervals


def test_every_polling_loop_stops_when_the_page_is_hidden() -> None:
    markup = SCRIPT.read_text(encoding="utf-8")

    assert markup.count("visibilitychange") >= 2
    assert markup.count("document.hidden") >= 2


def test_buttons_that_start_work_are_disabled_with_a_label() -> None:
    markup = SCRIPT.read_text(encoding="utf-8")

    assert "button.disabled = true" in markup
    assert "button.dataset.label" in markup
    assert 'form.classList.add("busy")' in markup


def test_the_progress_region_is_a_live_region() -> None:
    markup = SHELL.read_text(encoding="utf-8")

    assert 'id="progress-region"' in markup
    assert 'role="status"' in markup
    assert 'aria-live="polite"' in markup


def test_a_failed_poll_says_what_to_do_rather_than_a_status_code() -> None:
    markup = SCRIPT.read_text(encoding="utf-8")

    assert "Suivi de progression indisponible" in markup
    assert "Rechargez la page" in markup
    assert "Le travail en cours continue" in markup


def test_the_spinner_respects_reduced_motion() -> None:
    """The token system disables motion wholesale rather than per-animation."""

    styles = STYLESHEET.read_text(encoding="utf-8")

    assert "prefers-reduced-motion" in styles
    assert "animation-duration: 0.001ms !important" in styles
    assert "transition-duration: 0.001ms !important" in styles
