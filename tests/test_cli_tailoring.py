"""CLI coverage for offer document generation and cold-application approval."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

from typer.testing import CliRunner

from jobpilot import cli
from jobpilot.state import current_status, transition


class _ConnectionProxy:
    """Keep the shared in-memory fixture open after the CLI closes its handle."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def __getattr__(self, name: str):
        return getattr(self._connection, name)

    def close(self) -> None:
        pass


def _application(db: sqlite3.Connection, kind: str = "offer") -> int:
    application_id = db.execute(
        "INSERT INTO applications (kind, status) VALUES (?, 'queued')",
        (kind,),
    ).lastrowid
    db.commit()
    return int(application_id)


def _tailoring_module(generate_application, error_type: type[Exception]) -> ModuleType:
    module = ModuleType("jobpilot.tailoring")
    module.generate_application = generate_application
    module.TailoringError = error_type
    return module


def test_apply_offer_generates_and_reports_outputs(
    db: sqlite3.Connection,
    monkeypatch,
    tmp_path: Path,
) -> None:
    application_id = _application(db)
    proxy = _ConnectionProxy(db)
    monkeypatch.setattr(cli, "connect", lambda: proxy)

    class FakeTailoringError(RuntimeError):
        pass

    tracker_row = "\t".join(["value"] * 18)
    result = SimpleNamespace(
        selection=SimpleNamespace(label="SOC Analyst", slug="soc"),
        rationale="Missions centred on SIEM and incident response.",
        cv_html_path=tmp_path / "cv.html",
        cv_pdf_path=tmp_path / "cv.pdf",
        letter_body_path=tmp_path / "letter.html",
        letter_pdf_path=tmp_path / "letter.pdf",
        tracker_path=tmp_path / "tracker.tsv",
        tracker_row=tracker_row,
    )

    def generate_application(connection, received_id: int):
        assert connection is proxy
        assert received_id == application_id
        assert current_status(connection, received_id) == "generating"
        transition(connection, received_id, "ready")
        return result

    monkeypatch.setitem(
        sys.modules,
        "jobpilot.tailoring",
        _tailoring_module(generate_application, FakeTailoringError),
    )

    completed = CliRunner().invoke(cli.app, ["apply", str(application_id)])

    assert completed.exit_code == 0, completed.output
    assert current_status(db, application_id) == "ready"
    assert "approved -> generating" in completed.output
    assert "CV variant: SOC Analyst (soc)" in completed.output
    assert f"CV PDF: {result.cv_pdf_path}" in completed.output
    assert f"Motivation letter PDF: {result.letter_pdf_path}" in completed.output
    assert f"Tracker: {result.tracker_path}" in completed.output
    assert tracker_row in completed.output
    assert "ready for human review" in completed.output
    approval_count = db.execute(
        "SELECT count(*) AS n FROM events "
        "WHERE application_id = ? AND event = 'human_approved'",
        (application_id,),
    ).fetchone()["n"]
    assert approval_count == 1


def test_apply_failure_reports_queued_for_retry(
    db: sqlite3.Connection,
    monkeypatch,
) -> None:
    application_id = _application(db)
    proxy = _ConnectionProxy(db)
    monkeypatch.setattr(cli, "connect", lambda: proxy)

    class FakeTailoringError(RuntimeError):
        pass

    def generate_application(connection, received_id: int):
        transition(connection, received_id, "queued")
        raise FakeTailoringError("quality gate failed")

    monkeypatch.setitem(
        sys.modules,
        "jobpilot.tailoring",
        _tailoring_module(generate_application, FakeTailoringError),
    )

    completed = CliRunner().invoke(cli.app, ["apply", str(application_id)])

    assert completed.exit_code == 1
    assert current_status(db, application_id) == "queued"
    assert "generation failed" in completed.output
    assert "returned to queued" in completed.output
    assert "quality gate failed" in completed.output


def test_apply_cold_preserves_approval_only_behavior(
    db: sqlite3.Connection,
    monkeypatch,
) -> None:
    application_id = _application(db, kind="cold")
    monkeypatch.setattr(cli, "connect", lambda: _ConnectionProxy(db))
    # Any attempted tailoring import would fail because the required names are absent.
    monkeypatch.setitem(sys.modules, "jobpilot.tailoring", ModuleType("jobpilot.tailoring"))

    completed = CliRunner().invoke(cli.app, ["apply", str(application_id)])

    assert completed.exit_code == 0, completed.output
    assert current_status(db, application_id) == "generating"
    assert completed.output.strip() == (
        f"application {application_id}: approved -> generating"
    )
    approval_count = db.execute(
        "SELECT count(*) AS n FROM events "
        "WHERE application_id = ? AND event = 'human_approved'",
        (application_id,),
    ).fetchone()["n"]
    assert approval_count == 1
