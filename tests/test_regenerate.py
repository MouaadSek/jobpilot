"""Task 34.A: the dashboard's Régénérer button.

The button re-runs the *existing* generation path; nothing here should be able
to pass if the tailoring behaviour itself changed. What is new and therefore
what is tested: the ready -> queued entry point, the per-application single
flight, and the archive that makes generation N diffable against N+1.
"""

from __future__ import annotations

import re
import sqlite3
import threading
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from jobpilot.apply_flow import (
    APPLICATION_LOCK,
    ARCHIVE_DIR_NAME,
    GenerationInFlight,
    generation_single_flight,
)
from jobpilot.dashboard import create_app, database_connection
from jobpilot.state import current_status, transition
from tests.test_dashboard import _client, _events, _offer_application
from tests.test_tailoring import _Advisor, _Toolchain

SRC_ROOT = Path(__file__).resolve().parents[1] / "src" / "jobpilot"


def _ready(db: sqlite3.Connection, tmp_path: Path, suffix: str) -> int:
    """Drive one application to 'ready' the normal way, so artefacts exist."""

    with APPLICATION_LOCK:
        application_id = _offer_application(
            db, title="Analyste SOC", score=0.9, suffix=suffix
        )
    with _client(db, tmp_path) as client:
        assert client.post(f"/application/{application_id}/approve").status_code == 200
    assert current_status(db, application_id) == "ready"
    return application_id


def _artifact_names(directory: Path) -> set[str]:
    return {path.name for path in directory.iterdir() if path.is_file()}


def _archives(output_root: Path, application_id: int) -> list[Path]:
    archive_root = output_root / str(application_id) / ARCHIVE_DIR_NAME
    if not archive_root.is_dir():
        return []
    return sorted(path for path in archive_root.iterdir() if path.is_dir())


# ----- the round trip -----


def test_regenerate_round_trips_ready_queued_generating_ready(
    dashboard_db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    application_id = _ready(dashboard_db, tmp_path, "regen-roundtrip")
    before = len(_events(dashboard_db, application_id))

    with _client(dashboard_db, tmp_path) as client:
        response = client.post(
            f"/application/{application_id}/regenerate",
            follow_redirects=False,
        )

    assert response.status_code == 303
    assert response.headers["location"] == f"/application/{application_id}"
    assert current_status(dashboard_db, application_id) == "ready"

    new_events = _events(dashboard_db, application_id)[before:]
    assert [row["event"] for row in new_events] == [
        "status_change",  # ready -> queued
        "human_approved",  # the constitution's approval, recorded again
        "status_change",  # queued -> generating
        "status_change",  # generating -> ready
    ]
    assert '"from": "ready", "to": "queued"' in new_events[0]["detail"]
    assert "dashboard regenerate" in new_events[0]["detail"]
    assert "dashboard regenerate" in new_events[1]["detail"]


def test_the_button_is_offered_on_a_ready_application(
    dashboard_db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    application_id = _ready(dashboard_db, tmp_path, "regen-button")

    with _client(dashboard_db, tmp_path) as client:
        ready_page = client.get(f"/application/{application_id}").text
        transition(dashboard_db, application_id, "queued", detail={"via": "test"})
        queued_page = client.get(f"/application/{application_id}").text

    assert f"/application/{application_id}/regenerate" in ready_page
    assert "Régénérer" in ready_page
    assert 'data-label="Génération"' in ready_page
    assert f"/application/{application_id}/regenerate" not in queued_page


# ----- archiving -----


def test_previous_artefacts_are_moved_into_a_timestamped_archive(
    dashboard_db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    """Overwriting would destroy the evidence the button exists to produce."""

    application_id = _ready(dashboard_db, tmp_path, "regen-archive")
    application_dir = tmp_path / str(application_id)
    first_generation = _artifact_names(application_dir)
    assert "cv.pdf" in first_generation
    (application_dir / "cv.pdf").write_bytes(b"%PDF-generation-one")

    with _client(dashboard_db, tmp_path) as client:
        client.post(f"/application/{application_id}/regenerate")

    archives = _archives(tmp_path, application_id)
    assert len(archives) == 1
    assert _artifact_names(archives[0]) == first_generation
    assert (archives[0] / "cv.pdf").read_bytes() == b"%PDF-generation-one"
    # The live directory holds generation two, not the archived bytes.
    assert (application_dir / "cv.pdf").read_bytes() != b"%PDF-generation-one"
    assert _artifact_names(application_dir) == first_generation


def test_two_regenerations_produce_two_distinct_archives(
    dashboard_db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    """Back-to-back clicks land in the same UTC second; neither may be lost."""

    application_id = _ready(dashboard_db, tmp_path, "regen-twice")

    with _client(dashboard_db, tmp_path) as client:
        client.post(f"/application/{application_id}/regenerate")
        client.post(f"/application/{application_id}/regenerate")

    archives = _archives(tmp_path, application_id)
    assert len(archives) == 2
    assert all(_artifact_names(path) for path in archives)


def test_archive_directory_names_are_legal_on_windows(
    dashboard_db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    """ISO 8601 basic format: the extended form's colons are illegal on NTFS."""

    application_id = _ready(dashboard_db, tmp_path, "regen-winsafe")

    with _client(dashboard_db, tmp_path) as client:
        client.post(f"/application/{application_id}/regenerate")

    (archive,) = _archives(tmp_path, application_id)
    assert re.fullmatch(r"\d{8}T\d{6}Z(-\d+)?", archive.name)


def test_archives_are_not_reachable_through_the_file_endpoint(
    dashboard_db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    """Archives are for a human with a diff tool, never for the application."""

    application_id = _ready(dashboard_db, tmp_path, "regen-noserve")

    with _client(dashboard_db, tmp_path) as client:
        client.post(f"/application/{application_id}/regenerate")
        (archive,) = _archives(tmp_path, application_id)
        response = client.get(f"/files/{application_id}/{ARCHIVE_DIR_NAME}")
        nested = client.get(
            f"/files/{application_id}/{ARCHIVE_DIR_NAME}/{archive.name}/cv.pdf"
        )

    assert response.status_code == 404
    assert nested.status_code == 404


# ----- refusals -----


@pytest.mark.parametrize("status", ["queued", "skipped", "applied"])
def test_regenerate_on_a_non_ready_application_conflicts(
    dashboard_db: sqlite3.Connection,
    tmp_path: Path,
    status: str,
) -> None:
    with APPLICATION_LOCK:
        application_id = _offer_application(
            dashboard_db,
            title="Pas prête",
            score=0.7,
            status=status,
            suffix=f"regen-{status}",
        )

    with _client(dashboard_db, tmp_path) as client:
        response = client.post(f"/application/{application_id}/regenerate")

    assert response.status_code == 409
    assert "ready" in response.text
    assert current_status(dashboard_db, application_id) == status
    assert _events(dashboard_db, application_id) == []
    assert not (tmp_path / str(application_id)).exists()


def test_regenerate_on_an_unknown_application_is_a_404(
    dashboard_db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    with _client(dashboard_db, tmp_path) as client:
        response = client.post("/application/4242/regenerate")

    assert response.status_code == 404


def test_generation_failure_leaves_queued_and_surfaces_the_validator_message(
    dashboard_db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    """A silent failure here would be worse than having no button at all."""

    application_id = _ready(dashboard_db, tmp_path, "regen-failure")
    application_dir = tmp_path / str(application_id)
    first_generation = _artifact_names(application_dir)

    with _client(
        dashboard_db, tmp_path, toolchain=_Toolchain(fail_orphans=True)
    ) as client:
        response = client.post(f"/application/{application_id}/regenerate")

    assert response.status_code == 422
    assert "orphan quality gate failed" in response.text
    assert current_status(dashboard_db, application_id) == "queued"
    assert "queued" in response.text

    # The failed run cleaned up after itself; the previous run survives.
    assert _artifact_names(application_dir) == set()
    (archive,) = _archives(tmp_path, application_id)
    assert _artifact_names(archive) == first_generation


# ----- single flight -----


def test_a_second_click_does_not_start_a_second_generation(
    dashboard_db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    """The double-click race has found real bugs in this repo before."""

    application_id = _ready(dashboard_db, tmp_path, "regen-race")

    in_generation = threading.Event()
    may_finish = threading.Event()
    generations = 0
    counter_lock = threading.Lock()

    class _BlockingToolchain(_Toolchain):
        def generate_cv_pdf(self, tailored_path: Path, output_path: Path) -> None:
            nonlocal generations
            with counter_lock:
                generations += 1
            in_generation.set()
            # Held open so the second request is guaranteed to arrive mid-flight.
            assert may_finish.wait(10)
            super().generate_cv_pdf(tailored_path, output_path)

    app = create_app(
        advisor=_Advisor(),
        toolchain=_BlockingToolchain(),
        output_root=tmp_path,
    )

    # Unlike the shared helper this override does not hold APPLICATION_LOCK, so
    # the second request reaches the single-flight guard instead of queueing on
    # the writer lock. That is exactly the ordering the endpoint relies on.
    def shared_connection() -> Iterator[sqlite3.Connection]:
        yield dashboard_db

    app.dependency_overrides[database_connection] = shared_connection

    first: dict[str, int] = {}
    with TestClient(app) as client:

        def regenerate() -> None:
            first["status"] = client.post(
                f"/application/{application_id}/regenerate",
                follow_redirects=False,
            ).status_code

        worker = threading.Thread(target=regenerate)
        worker.start()
        assert in_generation.wait(10)
        second = client.post(f"/application/{application_id}/regenerate")
        may_finish.set()
        worker.join(20)

    assert not worker.is_alive()
    assert first["status"] == 303
    assert second.status_code == 409
    assert "déjà en cours" in second.json()["detail"]
    assert generations == 1
    assert current_status(dashboard_db, application_id) == "ready"
    assert len(_archives(tmp_path, application_id)) == 1


def test_the_flight_is_keyed_per_application() -> None:
    """Two applications must be able to regenerate at the same time."""

    with generation_single_flight(1):
        with generation_single_flight(2):
            with pytest.raises(GenerationInFlight):
                with generation_single_flight(1):
                    pass


def test_the_flight_is_released_after_a_failure() -> None:
    """A crashed generation must not lock the application out forever."""

    with pytest.raises(RuntimeError, match="boom"), generation_single_flight(7):
        raise RuntimeError("boom")

    with generation_single_flight(7):
        pass


# ----- the constitution rule this endpoint could most easily break -----


def test_no_module_updates_application_status_outside_the_state_machine() -> None:
    """state.transition() is the single authorized writer of applications.status.

    Spelled as a grep because the rule is about text that must not exist, and
    the web layer is the surface most likely to reach for a direct UPDATE.
    """

    offenders = []
    for path in sorted(SRC_ROOT.rglob("*.py")):
        if path.name == "state.py":
            continue
        source = path.read_text(encoding="utf-8")
        if re.search(r"UPDATE\s+applications\s+SET\s+status", source, re.IGNORECASE):
            offenders.append(path.relative_to(SRC_ROOT).as_posix())

    assert offenders == []


def test_templates_post_status_changes_only_to_known_endpoints() -> None:
    """The dashboard template must not invent a status-writing route."""

    template = (SRC_ROOT / "templates" / "dashboard.html").read_text(encoding="utf-8")
    posted = set(re.findall(r'action="(/application/\{\{[^"]+\}\}/[a-z-]+)"', template))
    endpoints = {action.rsplit("/", 1)[-1] for action in posted}

    assert endpoints <= {
        "approve",
        "skip",
        "regenerate",
        "mark-sent",
        "prefill",
        "send",
    }
