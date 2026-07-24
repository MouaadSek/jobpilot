"""Local dashboard coverage over the existing application state machine."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from jobpilot.apply_flow import APPLICATION_LOCK
from jobpilot.dashboard import create_app, database_connection
from jobpilot.state import current_status
from tests.test_tailoring import _Advisor, _Toolchain


def _offer_application(
    db: sqlite3.Connection,
    *,
    title: str,
    score: float,
    status: str = "queued",
    suffix: str,
) -> int:
    source_id = db.execute(
        "SELECT id FROM sources WHERE name = 'france_travail'"
    ).fetchone()["id"]
    company_id = db.execute(
        "INSERT INTO companies (name, city) VALUES ('Acme', 'Paris')"
    ).lastrowid
    description = f"Description complète pour {title}: SIEM, alertes et incidents."
    digest = hashlib.sha256(f"dashboard-{suffix}".encode()).hexdigest()
    offer_id = db.execute(
        "INSERT INTO offers (source_id, company_id, external_id, url, title, "
        "description, contract_type, duration_months, city, remote_policy, "
        "posted_at, content_hash) VALUES (?, ?, ?, ?, ?, ?, 'alternance', 12, "
        "'Paris', 'hybrid', '2026-07-20T08:00:00+00:00', ?)",
        (
            source_id,
            company_id,
            f"offer-{suffix}",
            f"https://example.test/jobs/{suffix}",
            title,
            description,
            digest,
        ),
    ).lastrowid
    db.execute(
        "INSERT INTO match_scores (offer_id, hard_filter_pass, semantic_score, "
        "keyword_score, bonus_score, final_score, scored_at) "
        "VALUES (?, 1, 0.81, 0.72, 0.05, ?, '2026-07-20T09:00:00+00:00')",
        (offer_id, score),
    )
    application_id = db.execute(
        "INSERT INTO applications (offer_id, company_id, kind, status) "
        "VALUES (?, ?, 'offer', ?)",
        (offer_id, company_id, status),
    ).lastrowid
    db.commit()
    return int(application_id)


@contextmanager
def _client(
    db: sqlite3.Connection,
    output_root: Path,
    *,
    toolchain: _Toolchain | None = None,
) -> Iterator[TestClient]:
    app = create_app(
        advisor=_Advisor(),
        toolchain=toolchain or _Toolchain(),
        output_root=output_root,
    )

    def in_memory_connection() -> Iterator[sqlite3.Connection]:
        with APPLICATION_LOCK:
            yield db

    app.dependency_overrides[database_connection] = in_memory_connection
    with TestClient(app) as client:
        yield client


def _events(db: sqlite3.Connection, application_id: int) -> list[sqlite3.Row]:
    return db.execute(
        "SELECT event, detail FROM events WHERE application_id = ? ORDER BY id",
        (application_id,),
    ).fetchall()


def test_queue_page_lists_queued_applications_by_descending_score(
    dashboard_db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    with APPLICATION_LOCK:
        lower_id = _offer_application(
            dashboard_db,
            title="Analyste junior",
            score=0.61,
            suffix="lower",
        )
        higher_id = _offer_application(
            dashboard_db,
            title="Analyste SOC confirmé",
            score=0.94,
            suffix="higher",
        )
        _offer_application(
            dashboard_db,
            title="Application ignorée",
            score=0.99,
            status="skipped",
            suffix="skipped",
        )

    with _client(dashboard_db, tmp_path) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert response.text.index("Analyste SOC confirmé") < response.text.index(
        "Analyste junior"
    )
    assert f"/application/{higher_id}" in response.text
    assert f"/application/{lower_id}" in response.text
    assert "Application ignorée" not in response.text
    assert "queued" in response.text


def test_approve_uses_shared_flow_and_finishes_ready_with_artifacts(
    dashboard_db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    with APPLICATION_LOCK:
        application_id = _offer_application(
            dashboard_db,
            title="Analyste SOC",
            score=0.91,
            suffix="approve",
        )

    with _client(dashboard_db, tmp_path) as client:
        response = client.post(
            f"/application/{application_id}/approve",
            follow_redirects=False,
        )
        detail = client.get(f"/application/{application_id}")

    assert response.status_code == 303
    assert response.headers["location"] == f"/application/{application_id}"
    assert detail.status_code == 200
    assert current_status(dashboard_db, application_id) == "ready"
    stored = dashboard_db.execute(
        "SELECT cv_pdf_path, letter_pdf_path FROM applications WHERE id = ?",
        (application_id,),
    ).fetchone()
    assert Path(stored["cv_pdf_path"]).is_file()
    assert Path(stored["letter_pdf_path"]).is_file()
    assert (tmp_path / str(application_id) / "tracker.tsv").is_file()
    assert f"/files/{application_id}/cv.pdf" in detail.text
    assert f"/files/{application_id}/motivation_letter.pdf" in detail.text
    assert "Tracker row" in detail.text

    events = _events(dashboard_db, application_id)
    assert [row["event"] for row in events] == [
        "human_approved",
        "status_change",
        "status_change",
    ]
    assert json.loads(events[0]["detail"]) == {"via": "dashboard"}
    assert json.loads(events[1]["detail"]) == {
        "from": "queued",
        "to": "generating",
    }
    ready_detail = json.loads(events[2]["detail"])
    assert ready_detail["from"] == "generating"
    assert ready_detail["to"] == "ready"


def test_approve_failure_returns_to_queue_and_clears_partial_artifacts(
    dashboard_db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    with APPLICATION_LOCK:
        application_id = _offer_application(
            dashboard_db,
            title="Analyste SOC",
            score=0.88,
            suffix="failure",
        )

    with _client(
        dashboard_db,
        tmp_path,
        toolchain=_Toolchain(fail_orphans=True),
    ) as client:
        response = client.post(f"/application/{application_id}/approve")

    assert response.status_code == 422
    assert "orphan quality gate failed" in response.text
    assert current_status(dashboard_db, application_id) == "queued"
    stored = dashboard_db.execute(
        "SELECT cv_pdf_path, letter_pdf_path FROM applications WHERE id = ?",
        (application_id,),
    ).fetchone()
    assert stored["cv_pdf_path"] is None
    assert stored["letter_pdf_path"] is None
    application_dir = tmp_path / str(application_id)
    assert application_dir.is_dir()
    assert list(application_dir.iterdir()) == []
    assert [row["event"] for row in _events(dashboard_db, application_id)] == [
        "human_approved",
        "status_change",
        "status_change",
        "generation_failed",
    ]


def test_skip_transitions_through_state_machine(
    dashboard_db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    with APPLICATION_LOCK:
        application_id = _offer_application(
            dashboard_db,
            title="Poste à ignorer",
            score=0.52,
            suffix="skip",
        )

    with _client(dashboard_db, tmp_path) as client:
        response = client.post(
            f"/application/{application_id}/skip",
            follow_redirects=False,
        )

    assert response.status_code == 303
    assert current_status(dashboard_db, application_id) == "skipped"
    events = _events(dashboard_db, application_id)
    assert [row["event"] for row in events] == ["status_change"]
    assert json.loads(events[0]["detail"]) == {
        "from": "queued",
        "to": "skipped",
        "via": "dashboard",
    }


@pytest.mark.parametrize(
    "unsafe_name",
    (
        "..%2fcv.pdf",
        "%2fetc%2fpasswd",
        "unknown.pdf",
    ),
)
def test_file_endpoint_rejects_traversal_absolute_and_unknown_names(
    dashboard_db: sqlite3.Connection,
    tmp_path: Path,
    unsafe_name: str,
) -> None:
    with APPLICATION_LOCK:
        application_id = _offer_application(
            dashboard_db,
            title="Analyste SOC",
            score=0.84,
            status="ready",
            suffix=f"files-{unsafe_name}",
        )
    artifact_dir = tmp_path / str(application_id)
    artifact_dir.mkdir(parents=True)
    (artifact_dir / "cv.pdf").write_bytes(b"%PDF-safe")

    with _client(dashboard_db, tmp_path) as client:
        allowed = client.get(f"/files/{application_id}/cv.pdf")
        rejected = client.get(f"/files/{application_id}/{unsafe_name}")

    assert allowed.status_code == 200
    assert allowed.content == b"%PDF-safe"
    assert rejected.status_code in {400, 404}


def test_approve_wrong_state_returns_clean_conflict(
    dashboard_db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    with APPLICATION_LOCK:
        application_id = _offer_application(
            dashboard_db,
            title="Déjà ignorée",
            score=0.75,
            status="skipped",
            suffix="conflict",
        )

    with _client(dashboard_db, tmp_path) as client:
        response = client.post(f"/application/{application_id}/approve")

    assert response.status_code == 409
    assert "not in &#39;queued&#39; state" in response.text
    assert current_status(dashboard_db, application_id) == "skipped"
    assert _events(dashboard_db, application_id) == []
