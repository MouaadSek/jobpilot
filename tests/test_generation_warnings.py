"""Task 39 item 2: a degraded document must not look like a clean one.

Warnings ship before the funnel that produces most of them, deliberately: the
whole risk of "recoverable degrades instead of aborting" is that a compromise
becomes invisible, and Mouaad reads every CV before sending. If the degradation
is on the page, the review still catches it.
"""

from __future__ import annotations

import sqlite3

import pytest

from jobpilot.generation_warnings import (
    GenerationWarning,
    clear_warnings,
    record_warnings,
    warning_gates_by_application,
    warnings_for,
)
from tests.test_tailoring_retry import _queued_application


@pytest.fixture
def application(db: sqlite3.Connection) -> int:
    return _queued_application(db, suffix="warnings")


def _warning(gate: str = "check_orphan_lines") -> GenerationWarning:
    return GenerationWarning(
        gate=gate,
        message="ORPHAN REGRESSIONS: 1 [.profile#0] last=11.0% width",
        degraded="profil : phrase du modèle restaurée",
    )


def test_a_recorded_warning_reads_back_whole(db, application) -> None:
    record_warnings(db, application, [_warning(), _warning("resolve_fact_id")])

    stored = warnings_for(db, application)

    assert [w.gate for w in stored] == ["check_orphan_lines", "resolve_fact_id"]
    assert stored[0].message.startswith("ORPHAN REGRESSIONS")
    assert stored[0].degraded


def test_regeneration_replaces_warnings_rather_than_accumulating(db, application) -> None:
    """The previous run's compromises say nothing about the document on disk."""

    record_warnings(db, application, [_warning(), _warning("resolve_fact_id")])
    clear_warnings(db, application)

    assert warnings_for(db, application) == ()

    record_warnings(db, application, [_warning("_validate_profile_candidate")])

    assert [w.gate for w in warnings_for(db, application)] == [
        "_validate_profile_candidate"
    ]


def test_never_generated_is_distinguishable_from_generated_cleanly(db, application) -> None:
    """NULL is not '[]', and the detail page reads them differently."""

    raw = db.execute(
        "SELECT generation_warnings FROM applications WHERE id = ?", (application,)
    ).fetchone()[0]
    assert raw is None

    clear_warnings(db, application)
    raw = db.execute(
        "SELECT generation_warnings FROM applications WHERE id = ?", (application,)
    ).fetchone()[0]
    assert raw == "[]"
    assert warnings_for(db, application) == ()


def test_the_marker_index_skips_clean_and_ungenerated_applications(db) -> None:
    clean = _queued_application(db, suffix="clean")
    degraded = _queued_application(db, suffix="degraded")
    _queued_application(db, suffix="never-run")
    clear_warnings(db, clean)
    record_warnings(db, degraded, [_warning()])

    marks = warning_gates_by_application(db)

    assert marks == {degraded: ("check_orphan_lines",)}


def test_an_unreadable_payload_is_treated_as_no_warnings(db, application) -> None:
    """A corrupt column must not take the detail page down with it."""

    db.execute(
        "UPDATE applications SET generation_warnings = ? WHERE id = ?",
        ("{not json", application),
    )

    assert warnings_for(db, application) == ()
    assert warning_gates_by_application(db) == {}


def test_a_missing_application_has_no_warnings(db) -> None:
    assert warnings_for(db, 9999) == ()


# ----- the wiring: a real generation that degraded -----


def test_an_advisory_orphan_is_recorded_on_the_application(db, tmp_path) -> None:
    """It did not block, so the only thing standing between it and invisibility
    is this record."""

    from tests.test_selection_tailoring import _approve
    from tests.test_tailoring import _Toolchain

    outcome = _approve(db, tmp_path, _Toolchain(fail_orphans=True, orphan_selector="li"))

    stored = warnings_for(db, outcome.application_id)

    assert [w.gate for w in stored] == ["check_orphan_lines"]
    assert "ORPHAN REGRESSIONS" in stored[0].message
    assert "Vérifier la mise en page" in stored[0].degraded


def test_a_clean_generation_records_an_empty_set_not_null(db, tmp_path) -> None:
    """« rien à signaler » is a claim worth being able to make."""

    from tests.test_selection_tailoring import _approve
    from tests.test_tailoring import _Toolchain

    outcome = _approve(db, tmp_path, _Toolchain())

    raw = db.execute(
        "SELECT generation_warnings FROM applications WHERE id = ?",
        (outcome.application_id,),
    ).fetchone()[0]

    assert raw == "[]"
    assert warnings_for(db, outcome.application_id) == ()


def test_the_library_and_tracker_mark_a_degraded_application(db, tmp_path) -> None:
    from jobpilot.tracker import tracker_rows
    from tests.test_selection_tailoring import _approve
    from tests.test_tailoring import _Toolchain

    degraded = _approve(db, tmp_path, _Toolchain(fail_orphans=True, orphan_selector="li"))

    rows = {row["application_id"]: row for row in tracker_rows(db)}

    assert rows[degraded.application_id]["warning_gates"] == ["check_orphan_lines"]


def test_the_detail_page_shows_the_warning_in_amber(dashboard_db, tmp_path) -> None:
    """Amber, not red: the document is usable, it just needs a look."""

    from collections.abc import Iterator

    from fastapi.testclient import TestClient

    from jobpilot.apply_flow import APPLICATION_LOCK, approve_application
    from jobpilot.dashboard import create_app, database_connection
    from tests.test_selection_tailoring import _SelectingAdvisor
    from tests.test_tailoring import _Toolchain

    with APPLICATION_LOCK:
        application_id = _queued_application(dashboard_db, suffix="warn-visible")
    approve_application(
        dashboard_db,
        application_id,
        via="test",
        advisor=_SelectingAdvisor(),
        toolchain=_Toolchain(fail_orphans=True, orphan_selector="li"),
        output_root=tmp_path,
    )

    app = create_app(output_root=tmp_path)

    def connection() -> Iterator[sqlite3.Connection]:
        with APPLICATION_LOCK:
            yield dashboard_db

    app.dependency_overrides[database_connection] = connection
    with TestClient(app) as client:
        page = client.get(f"/application/{application_id}")

    assert 'class="warn"' in page.text
    assert 'role="status"' in page.text
    assert "check_orphan_lines" in page.text
    assert "1 avertissement" in page.text
