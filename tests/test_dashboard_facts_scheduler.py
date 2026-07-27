"""Read-only fact bank page and honest scheduler reporting on the queue page."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from jobpilot.apply_flow import APPLICATION_LOCK
from jobpilot.dashboard import create_app, database_connection
from jobpilot.scheduler import HEARTBEAT_FILENAME, daemon_status, write_heartbeat

FIXTURE_BANK = """
version: 1
source_documents: ["skill/SKILL.md"]
source_templates: ["Mouaad_Sekkouri_-_SOC__Alternance.html"]
experience:
  - id: exp_concentrix
    employer: Concentrix
    role: Support Réseau et Sécurité
    dates: 2021 - 2023
    location: Lille
    facts:
      - id: exp_concentrix_incidents
        text: 1500 incidents traités, 85% résolus au premier contact
      - id: exp_concentrix_mttr
        text: MTTR réduit de 20%
        needs_review: true
projects:
  - id: proj_siem
    title: Lab SIEM maison
    stack: ["Wazuh", "Docker"]
    source_templates: ["Mouaad_Sekkouri_-_SOC__Alternance.html"]
    facts:
      - id: proj_siem_detection
        text: Règles de détection sur 12 cas d'usage MITRE ATT&CK
education:
  - id: edu_m1
    diploma: M1 Cybersécurité
    institution: Supinfo
    dates: 2025 - 2026
    location: Lille
certifications:
  - id: cert_az900
    name: AZ-900
    obtained: "2025"
languages:
  - id: lang_en
    name: Anglais
    level: C1 Courant
skills:
  - id: skill_azure
    name: Azure
    verified: true
  - id: skill_terraform
    name: Terraform
    verified: false
locked:
  name: Mouaad Sekkouri
  email: mouaadsekkourii@gmail.com
  phone: "+33 7 51 13 54 25"
  linkedin: linkedin.com/in/sekkouri
  diplomas: ["M1 Cybersécurité"]
  employer_names: ["Concentrix"]
  certification_names: ["AZ-900"]
  dates: ["2021 - 2023"]
"""


@contextmanager
def _client(
    db: sqlite3.Connection,
    *,
    fact_bank_path: Path | None = None,
) -> Iterator[TestClient]:
    app = create_app(output_root=Path("unused"), fact_bank_path=fact_bank_path)

    def in_memory_connection() -> Iterator[sqlite3.Connection]:
        with APPLICATION_LOCK:
            yield db

    app.dependency_overrides[database_connection] = in_memory_connection
    with TestClient(app) as client:
        yield client


@pytest.fixture
def fixture_bank(tmp_path: Path) -> Path:
    path = tmp_path / "fact_bank.yaml"
    path.write_text(FIXTURE_BANK, encoding="utf-8")
    return path


def test_facts_page_renders_every_section_of_the_bank(
    dashboard_db: sqlite3.Connection,
    fixture_bank: Path,
) -> None:
    with _client(dashboard_db, fact_bank_path=fixture_bank) as client:
        page = client.get("/facts")

    assert page.status_code == 200
    for heading in (
        "Expérience",
        "Projets",
        "Formation",
        "Certifications",
        "Langues",
        "Compétences",
        "Verrouillé",
    ):
        assert heading in page.text
    # Experience entries carry their claims, exactly as `jobpilot facts` prints.
    assert "Concentrix" in page.text
    assert "exp_concentrix_incidents" in page.text
    assert "1500 incidents traités" in page.text
    assert "exp_concentrix_mttr" in page.text
    assert "[à revoir]" in page.text
    assert "Lab SIEM maison" in page.text
    assert "M1 Cybersécurité" in page.text
    assert "AZ-900" in page.text
    assert "C1 Courant" in page.text


def test_facts_page_shows_verified_flags_and_locked_identity(
    dashboard_db: sqlite3.Connection,
    fixture_bank: Path,
) -> None:
    with _client(dashboard_db, fact_bank_path=fixture_bank) as client:
        page = client.get("/facts")

    assert "vérifiée" in page.text
    assert "non vérifiée" in page.text
    assert "mouaadsekkourii@gmail.com" in page.text
    assert "linkedin.com/in/sekkouri" in page.text


def test_facts_page_is_read_only_and_linked_from_the_header(
    dashboard_db: sqlite3.Connection,
    fixture_bank: Path,
) -> None:
    with _client(dashboard_db, fact_bank_path=fixture_bank) as client:
        page = client.get("/facts")
        queue = client.get("/")

    assert 'href="/facts"' in queue.text
    # No editing in this task: nothing on the page submits anything.
    assert "<form" not in page.text
    assert "<textarea" not in page.text


def test_malformed_fact_bank_is_reported_not_swallowed(
    dashboard_db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    broken = tmp_path / "broken.yaml"
    broken.write_text("version: 0\n", encoding="utf-8")

    with _client(dashboard_db, fact_bank_path=broken) as client:
        page = client.get("/facts")

    assert page.status_code == 500
    assert 'role="alert"' in page.text
    assert "version" in page.text


def test_queue_page_lists_last_run_per_enabled_source(
    dashboard_db: sqlite3.Connection,
) -> None:
    dashboard_db.execute(
        "UPDATE sources SET last_run_at = ? WHERE name = 'france_travail'",
        ("2026-07-26T06:00:00+00:00",),
    )
    dashboard_db.commit()

    with _client(dashboard_db) as client:
        page = client.get("/")

    assert "Planification" in page.text
    assert "france_travail" in page.text
    assert "2026-07-26T06:00:00+00:00" in page.text
    # A source that never ran says so rather than showing a blank cell.
    assert "jamais" in page.text
    # The database keeps no per-cycle outcome, and the page does not invent one.
    assert "inconnu (non enregistré)" in page.text


def test_daemon_state_is_unknown_without_a_recorded_heartbeat(
    dashboard_db: sqlite3.Connection,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from jobpilot import scheduler

    monkeypatch.setattr(
        scheduler, "heartbeat_path", lambda settings=None: tmp_path / "absent"
    )

    with _client(dashboard_db) as client:
        page = client.get("/")

    assert "inconnu" in page.text
    assert "Aucun battement enregistré" in page.text


@pytest.mark.parametrize(
    ("age_hours", "expected"),
    ((0.5, "actif"), (10.0, "inactif")),
)
def test_daemon_state_follows_the_recorded_heartbeat_age(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    age_hours: float,
    expected: str,
) -> None:
    from jobpilot import scheduler

    beat = tmp_path / HEARTBEAT_FILENAME
    beat.write_text(
        json.dumps(
            {
                "at": (
                    datetime.now(UTC) - timedelta(hours=age_hours)
                ).isoformat(),
                "interval_hours": 3.0,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(scheduler, "heartbeat_path", lambda settings=None: beat)

    status = daemon_status()

    assert status.state == expected
    assert status.interval_hours == 3.0


def test_unreadable_heartbeat_never_claims_the_daemon_is_alive(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from jobpilot import scheduler

    beat = tmp_path / HEARTBEAT_FILENAME
    beat.write_text("not json at all", encoding="utf-8")
    monkeypatch.setattr(scheduler, "heartbeat_path", lambda settings=None: beat)

    assert daemon_status().state == "inconnu"


def test_write_heartbeat_records_the_cycle_interval(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from jobpilot import scheduler

    beat = tmp_path / "logs" / HEARTBEAT_FILENAME
    monkeypatch.setattr(scheduler, "heartbeat_path", lambda settings=None: beat)

    write_heartbeat(3.0)

    payload = json.loads(beat.read_text(encoding="utf-8"))
    assert payload["interval_hours"] == 3.0
    assert datetime.fromisoformat(payload["at"]).tzinfo is not None
