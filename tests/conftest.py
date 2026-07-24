"""Shared pytest fixtures. All DB tests use in-memory SQLite (constitution rule)."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest

from jobpilot.db import apply_schema, run_migrations, seed_sources

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema.sql"
MIGRATIONS_DIR = ROOT / "migrations"


@pytest.fixture
def db() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    apply_schema(conn, SCHEMA_PATH)
    run_migrations(conn, MIGRATIONS_DIR)  # parity with init_db (adds profile.headline)
    seed_sources(conn)
    yield conn
    conn.close()


@pytest.fixture
def seeded_profile(db: sqlite3.Connection) -> sqlite3.Connection:
    """Insert the singleton profile row with a small deterministic embedding."""
    db.execute(
        "INSERT INTO profile (id, full_name, target_roles, hard_skills, certs, "
        "languages, locations_ok, contract_wanted, min_duration_months, embedding) "
        "VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            "Test User",
            json.dumps(["SOC Analyst", "Cloud Security", "DevSecOps"]),
            json.dumps(["azure", "sentinel", "kql", "docker", "k8s", "python"]),
            json.dumps(["AZ-900"]),
            json.dumps({"fr": "C2", "en": "C1"}),
            json.dumps(["Lille", "Paris", "remote"]),
            json.dumps(["alternance", "stage"]),
            6,
            json.dumps([0.1, 0.2, 0.3, 0.4]),
        ),
    )
    db.commit()
    return db


@pytest.fixture
def dashboard_db() -> Iterator[sqlite3.Connection]:
    """Thread-capable in-memory DB for synchronous FastAPI TestClient requests."""

    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    apply_schema(conn, SCHEMA_PATH)
    run_migrations(conn, MIGRATIONS_DIR)
    seed_sources(conn)
    yield conn
    conn.close()
