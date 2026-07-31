"""Task 36 item 3: read the CV before downloading it.

Reading is the step that decides whether an application is sent, so it happens
on the page. Preview and download are separate actions over the same guarded
path: only the Content-Disposition differs.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from jobpilot.apply_flow import APPLICATION_LOCK
from jobpilot.dashboard import create_app, database_connection
from jobpilot.state import transition
from tests.test_dashboard import _offer_application


@contextmanager
def _client(db: sqlite3.Connection, tmp_path: Path) -> Iterator[TestClient]:
    app = create_app(output_root=tmp_path)

    def connection() -> Iterator[sqlite3.Connection]:
        with APPLICATION_LOCK:
            yield db

    app.dependency_overrides[database_connection] = connection
    with TestClient(app) as client:
        yield client


def _ready_with_artifacts(db: sqlite3.Connection, tmp_path: Path, company: str) -> int:
    with APPLICATION_LOCK:
        application_id = _offer_application(
            db, title="Analyste SOC", score=0.9, suffix=f"pv-{company[:6]}"
        )
        db.execute(
            "UPDATE companies SET name = ? WHERE id = ("
            " SELECT company_id FROM offers WHERE id = ("
            "  SELECT offer_id FROM applications WHERE id = ?))",
            (company, application_id),
        )
        db.execute(
            "INSERT INTO profile (id, full_name, target_roles, hard_skills, certs, "
            "languages, locations_ok, contract_wanted) "
            "VALUES (1, 'Mouaad Sekkouri', '[]', '[]', '[]', '{}', '[]', '[]')"
        )
        transition(db, application_id, "generating")
        transition(db, application_id, "ready")
    directory = tmp_path / str(application_id)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "cv.pdf").write_bytes(b"%PDF-cv")
    (directory / "motivation_letter.pdf").write_bytes(b"%PDF-lm")
    return application_id


def test_preview_is_inline_and_download_is_an_attachment(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    """Separate actions, same bytes, same guarded path."""

    application_id = _ready_with_artifacts(dashboard_db, tmp_path, "Advens")

    with _client(dashboard_db, tmp_path) as client:
        preview = client.get(f"/files/{application_id}/cv.pdf")
        download = client.get(f"/files/{application_id}/cv.pdf?download=1")

    assert preview.headers["content-disposition"].startswith("inline")
    assert download.headers["content-disposition"].startswith("attachment")
    assert preview.content == download.content == b"%PDF-cv"
    # Even the preview carries the readable name, for "save as" from the viewer.
    assert "Advens_CV_Mouaad_Sekkouri.pdf" in preview.headers["content-disposition"]


def test_the_detail_page_offers_preview_and_download_separately(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    application_id = _ready_with_artifacts(dashboard_db, tmp_path, "Advens")

    with _client(dashboard_db, tmp_path) as client:
        page = client.get(f"/application/{application_id}")

    assert "Prévisualiser" in page.text
    assert "Télécharger" in page.text
    assert f'src="/files/{application_id}/cv.pdf"' in page.text
    assert f'href="/files/{application_id}/cv.pdf?download=1"' in page.text
    assert "déclenche aucun envoi" in page.text


def test_preview_neither_sends_nor_transitions(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    application_id = _ready_with_artifacts(dashboard_db, tmp_path, "Advens")
    before = dashboard_db.execute(
        "SELECT count(*) AS n FROM events WHERE application_id = ?", (application_id,)
    ).fetchone()["n"]

    with _client(dashboard_db, tmp_path) as client:
        client.get(f"/files/{application_id}/cv.pdf")
        client.get(f"/files/{application_id}/motivation_letter.pdf")

    after = dashboard_db.execute(
        "SELECT status, applied_at FROM applications WHERE id = ?", (application_id,)
    ).fetchone()
    events = dashboard_db.execute(
        "SELECT count(*) AS n FROM events WHERE application_id = ?", (application_id,)
    ).fetchone()["n"]
    assert after["status"] == "ready"
    assert after["applied_at"] is None
    assert events == before


@pytest.mark.parametrize(
    "name",
    ["../../../etc/passwd", "..%2Fsecret", "secret.pdf", "archive", "/etc/passwd"],
)
def test_the_traversal_guard_still_holds_for_both_dispositions(
    dashboard_db: sqlite3.Connection, tmp_path: Path, name: str
) -> None:
    """Task 34 pinned this. Naming the download must not have widened it."""

    application_id = _ready_with_artifacts(dashboard_db, tmp_path, "Advens")

    with _client(dashboard_db, tmp_path) as client:
        preview = client.get(f"/files/{application_id}/{name}")
        download = client.get(f"/files/{application_id}/{name}?download=1")

    assert preview.status_code in (400, 404)
    assert download.status_code in (400, 404)


def test_an_artifact_of_a_non_ready_application_is_still_refused(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    application_id = _ready_with_artifacts(dashboard_db, tmp_path, "Advens")
    with APPLICATION_LOCK:
        transition(dashboard_db, application_id, "queued")

    with _client(dashboard_db, tmp_path) as client:
        assert client.get(f"/files/{application_id}/cv.pdf").status_code == 404
