"""Task 36 item 4: the document library, archives included.

The case: an employer calls back six weeks later and the exact CV that was sent
has to be produced. Task 34 already archives every replaced generation to
output/applications/<id>/archive/<stamp>/, so this reads that history back
rather than adding storage.

Archives are read-only. There is deliberately no route from one back to 'ready':
restoring an old generation would leave the database and the artefacts
disagreeing about which documents the application actually holds.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from jobpilot.apply_flow import APPLICATION_LOCK, ARCHIVE_DIR_NAME
from jobpilot.dashboard import create_app, database_connection
from jobpilot.library import is_archive_stamp, library_entries
from jobpilot.state import transition
from tests.test_dashboard import _offer_application

STAMP_A = "20260701T101500Z"
STAMP_B = "20260715T093000Z"


@contextmanager
def _client(db: sqlite3.Connection, tmp_path: Path) -> Iterator[TestClient]:
    app = create_app(output_root=tmp_path)

    def connection() -> Iterator[sqlite3.Connection]:
        with APPLICATION_LOCK:
            yield db

    app.dependency_overrides[database_connection] = connection
    with TestClient(app) as client:
        yield client


def _generated(
    db: sqlite3.Connection,
    tmp_path: Path,
    *,
    company: str = "Advens",
    suffix: str = "lib",
    archives: tuple[str, ...] = (),
    current: bool = True,
    status: str = "ready",
) -> int:
    with APPLICATION_LOCK:
        application_id = _offer_application(
            db, title="Analyste SOC", score=0.9, suffix=suffix
        )
        db.execute(
            "UPDATE companies SET name = ? WHERE id = ("
            " SELECT company_id FROM offers WHERE id = ("
            "  SELECT offer_id FROM applications WHERE id = ?))",
            (company, application_id),
        )
        transition(db, application_id, "generating")
        transition(db, application_id, "ready")
        if status == "applied":
            transition(db, application_id, "applied")
        db.commit()

    directory = tmp_path / str(application_id)
    directory.mkdir(parents=True, exist_ok=True)
    if current:
        (directory / "cv.pdf").write_bytes(b"%PDF-current-cv")
        (directory / "motivation_letter.pdf").write_bytes(b"%PDF-current-lm")
    for stamp in archives:
        archive = directory / ARCHIVE_DIR_NAME / stamp
        archive.mkdir(parents=True, exist_ok=True)
        (archive / "cv.pdf").write_bytes(f"%PDF-{stamp}".encode())
        (archive / "motivation_letter.pdf").write_bytes(f"%PDF-lm-{stamp}".encode())
    return application_id


# ----- what the library contains -----


def test_an_application_with_no_artefacts_is_not_listed(
    db: sqlite3.Connection, tmp_path: Path
) -> None:
    """A library of documents, not another list of applications."""

    _generated(db, tmp_path, suffix="none", current=False)

    assert library_entries(db, tmp_path) == ()


def test_the_current_generation_is_listed_with_its_metadata(
    db: sqlite3.Connection, tmp_path: Path
) -> None:
    application_id = _generated(db, tmp_path, company="Advens", suffix="meta")

    (entry,) = library_entries(db, tmp_path)

    assert entry.application_id == application_id
    assert entry.company == "Advens"
    assert entry.title == "Analyste SOC"
    assert entry.status == "ready"
    assert entry.current is not None
    assert entry.current.artifacts == ("cv.pdf", "motivation_letter.pdf")
    assert entry.current.generated_at is not None
    assert entry.current.is_archived is False
    assert entry.archives == ()
    assert entry.generations == 1


def test_archived_generations_are_surfaced_newest_first(
    db: sqlite3.Connection, tmp_path: Path
) -> None:
    _generated(db, tmp_path, suffix="arch", archives=(STAMP_A, STAMP_B))

    (entry,) = library_entries(db, tmp_path)

    assert [archive.stamp for archive in entry.archives] == [STAMP_B, STAMP_A]
    assert all(archive.is_archived for archive in entry.archives)
    assert entry.generations == 3


def test_an_archive_stamp_is_read_back_as_a_date(
    db: sqlite3.Connection, tmp_path: Path
) -> None:
    _generated(db, tmp_path, suffix="stampdate", archives=(STAMP_A,))

    (entry,) = library_entries(db, tmp_path)

    assert entry.archives[0].generated_at is not None
    assert entry.archives[0].generated_at.startswith("2026-07-01T10:15:00")


def test_archives_survive_the_application_moving_on(
    db: sqlite3.Connection, tmp_path: Path
) -> None:
    """The interview case is six weeks after sending, so 'applied' must list."""

    _generated(db, tmp_path, suffix="applied", archives=(STAMP_A,), status="applied")

    (entry,) = library_entries(db, tmp_path)

    assert entry.status == "applied"
    assert entry.current is not None
    assert len(entry.archives) == 1


def test_an_application_with_only_archives_still_appears(
    db: sqlite3.Connection, tmp_path: Path
) -> None:
    _generated(db, tmp_path, suffix="onlyarch", current=False, archives=(STAMP_A,))

    (entry,) = library_entries(db, tmp_path)

    assert entry.current is None
    assert len(entry.archives) == 1


def test_a_directory_that_is_not_a_stamp_is_ignored_not_guessed_at(
    db: sqlite3.Connection, tmp_path: Path
) -> None:
    application_id = _generated(db, tmp_path, suffix="junk", archives=(STAMP_A,))
    stray = tmp_path / str(application_id) / ARCHIVE_DIR_NAME / "notes"
    stray.mkdir(parents=True)
    (stray / "cv.pdf").write_bytes(b"%PDF-stray")

    (entry,) = library_entries(db, tmp_path)

    assert [archive.stamp for archive in entry.archives] == [STAMP_A]


@pytest.mark.parametrize(
    "stamp", ["20260701T101500Z", "20260701T101500Z-2", "20260715T093000Z-11"]
)
def test_real_stamps_are_recognised(stamp: str) -> None:
    assert is_archive_stamp(stamp) is True


@pytest.mark.parametrize(
    "stamp",
    ["..", ".", "notes", "2026-07-01T10:15:00Z", "", "../../etc", "20260701T101500"],
)
def test_anything_else_is_not_a_stamp(stamp: str) -> None:
    assert is_archive_stamp(stamp) is False


def test_search_matches_the_company_name(db: sqlite3.Connection, tmp_path: Path) -> None:
    _generated(db, tmp_path, company="Advens", suffix="s1")
    _generated(db, tmp_path, company="Thales", suffix="s2")

    assert [e.company for e in library_entries(db, tmp_path, search="adv")] == ["Advens"]
    assert [e.company for e in library_entries(db, tmp_path, search="THALES")] == [
        "Thales"
    ]
    assert library_entries(db, tmp_path, search="capgemini") == ()
    assert len(library_entries(db, tmp_path, search="  ")) == 2


# ----- the page -----


def test_the_page_groups_by_application_and_collapses_archives(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    application_id = _generated(
        dashboard_db, tmp_path, suffix="page", archives=(STAMP_A, STAMP_B)
    )

    with _client(dashboard_db, tmp_path) as client:
        page = client.get("/library")

    assert page.status_code == 200
    assert "Advens" in page.text
    assert "Version actuelle" in page.text
    # Archives sit behind a disclosure rather than filling the page.
    assert "<details" in page.text
    assert "2 version(s) précédente(s)" in page.text
    assert f"/files/{application_id}/archive/{STAMP_B}/cv.pdf" in page.text


def test_the_page_is_reachable_from_the_navigation(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    with _client(dashboard_db, tmp_path) as client:
        assert 'href="/library"' in client.get("/").text


def test_the_page_offers_preview_and_download_for_both_generations(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    application_id = _generated(dashboard_db, tmp_path, suffix="both", archives=(STAMP_A,))

    with _client(dashboard_db, tmp_path) as client:
        page = client.get("/library")

    assert f'href="/files/{application_id}/cv.pdf"' in page.text
    assert f'href="/files/{application_id}/cv.pdf?download=1"' in page.text
    assert f'href="/files/{application_id}/archive/{STAMP_A}/cv.pdf"' in page.text
    assert (
        f'href="/files/{application_id}/archive/{STAMP_A}/cv.pdf?download=1"' in page.text
    )


def test_the_empty_state_says_what_to_do_next(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    with _client(dashboard_db, tmp_path) as client:
        page = client.get("/library")

    assert "Approuvez une candidature" in page.text


def test_search_narrows_the_page(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    _generated(dashboard_db, tmp_path, company="Advens", suffix="q1")
    _generated(dashboard_db, tmp_path, company="Thales", suffix="q2")

    with _client(dashboard_db, tmp_path) as client:
        page = client.get("/library?q=advens")

    assert "Advens" in page.text
    assert "Thales" not in page.text


# ----- serving archives -----


def test_an_archived_document_is_served_with_the_employer_name(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    application_id = _generated(dashboard_db, tmp_path, suffix="serve", archives=(STAMP_A,))

    with _client(dashboard_db, tmp_path) as client:
        preview = client.get(f"/files/{application_id}/archive/{STAMP_A}/cv.pdf")
        download = client.get(
            f"/files/{application_id}/archive/{STAMP_A}/cv.pdf?download=1"
        )

    assert preview.status_code == 200
    assert preview.content == f"%PDF-{STAMP_A}".encode()
    assert preview.headers["content-disposition"].startswith("inline")
    assert download.headers["content-disposition"].startswith("attachment")
    assert "Advens_CV" in download.headers["content-disposition"]


def test_an_archive_is_served_even_once_the_application_is_applied(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    application_id = _generated(
        dashboard_db, tmp_path, suffix="applied-serve", archives=(STAMP_A,),
        status="applied",
    )

    with _client(dashboard_db, tmp_path) as client:
        response = client.get(f"/files/{application_id}/archive/{STAMP_A}/cv.pdf")

    assert response.status_code == 200


@pytest.mark.parametrize(
    ("stamp", "name"),
    [
        ("..", "cv.pdf"),
        ("../..", "cv.pdf"),
        ("notes", "cv.pdf"),
        ("20260701T101500Z/../..", "cv.pdf"),
        (STAMP_A, "../../../cv.pdf"),
        (STAMP_A, "../cv.pdf"),
        (STAMP_A, "secret.pdf"),
        (STAMP_A, "/etc/passwd"),
        ("%2e%2e", "cv.pdf"),
        ("", "cv.pdf"),
    ],
)
def test_the_archive_guard_refuses_traversal(
    tmp_path: Path, stamp: str, name: str
) -> None:
    """Tested on the guard rather than over HTTP, because an HTTP client
    normalises "archive/../cv.pdf" into "/files/<id>/cv.pdf" before routing —
    which lands on the live guard and serves the application's own current CV,
    so a request-level test would be asserting the wrong thing entirely.

    This is a second, narrower guard rather than a relaxation of the live one.
    """

    from fastapi import HTTPException

    from jobpilot.dashboard import _safe_archive_path

    with pytest.raises(HTTPException) as excinfo:
        _safe_archive_path(tmp_path, 1, stamp, name)

    assert excinfo.value.status_code in (400, 404)


def test_the_archive_guard_cannot_reach_outside_the_application(
    tmp_path: Path,
) -> None:
    """The property that actually matters: no input reads another file."""

    from fastapi import HTTPException

    from jobpilot.dashboard import _safe_archive_path

    secret = tmp_path / "secret.pdf"
    secret.write_bytes(b"%PDF-not-yours")
    other = tmp_path / "2" / ARCHIVE_DIR_NAME / STAMP_A
    other.mkdir(parents=True)
    (other / "cv.pdf").write_bytes(b"%PDF-other-application")

    for stamp, name in ((f"../../{STAMP_A}", "cv.pdf"), ("..", "secret.pdf")):
        with pytest.raises(HTTPException):
            _safe_archive_path(tmp_path, 1, stamp, name)


def test_the_archive_route_refuses_an_unknown_directory(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    application_id = _generated(dashboard_db, tmp_path, suffix="guard", archives=(STAMP_A,))

    with _client(dashboard_db, tmp_path) as client:
        assert client.get(
            f"/files/{application_id}/archive/notes/cv.pdf"
        ).status_code == 404
        assert client.get(
            f"/files/{application_id}/archive/{STAMP_A}/secret.pdf"
        ).status_code == 404
        assert client.get(
            f"/files/{application_id}/archive/20991231T000000Z/cv.pdf"
        ).status_code == 404


def test_an_archive_cannot_be_restored_from_the_library(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    """Read-only by construction: no route accepts a POST here."""

    application_id = _generated(dashboard_db, tmp_path, suffix="ro", archives=(STAMP_A,))

    with _client(dashboard_db, tmp_path) as client:
        page = client.get("/library")
        posted = client.post(f"/files/{application_id}/archive/{STAMP_A}/cv.pdf")

    assert "<form method=\"post\"" not in page.text
    assert posted.status_code == 405
