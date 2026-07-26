"""Database connection factory, schema application, and migration runner."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from jobpilot.config import get_settings
from jobpilot.logging_conf import get_logger

log = get_logger("db")

# Sources seeded on init-db so ingestion has stable source_ids to reference.
_SEED_SOURCES: tuple[tuple[str, str, int], ...] = (
    # (name, kind, run_interval_min)
    ("france_travail", "api", 180),
    ("labonnealternance", "api", 360),
    ("ats", "api", 360),
    ("linkedin_alert", "api", 360),
    ("indeed_alert", "api", 360),
    ("wttj", "api", 360),
)


def connect(db_path: Path | str | None = None) -> sqlite3.Connection:
    """Open a connection with Row factory and foreign keys enabled.

    matcher.py relies on sqlite3.Row access (offer["title"]); keep it here.
    """
    path = Path(db_path) if db_path else get_settings().db_path
    if path != Path(":memory:"):
        path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def apply_schema(conn: sqlite3.Connection, schema_path: Path | None = None) -> None:
    """Apply schema.sql. Idempotent: uses CREATE TABLE ... only, so we guard reruns."""
    path = schema_path or get_settings().schema_path
    sql = path.read_text(encoding="utf-8")
    # schema.sql uses plain CREATE TABLE; skip if already initialized.
    existing = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='offers'"
    ).fetchone()
    if existing:
        log.info("schema already present, skipping apply_schema")
        return
    conn.executescript(sql)
    conn.commit()
    log.info("applied schema from %s", path)


def run_migrations(conn: sqlite3.Connection, migrations_dir: Path | None = None) -> int:
    """Apply numbered .sql migrations not yet recorded. Returns count applied.

    schema.sql is the base; anything altering it lives here as NNN_name.sql.
    """
    mig_dir = migrations_dir or get_settings().migrations_dir
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations ("
        "  filename TEXT PRIMARY KEY,"
        "  applied_at TEXT NOT NULL DEFAULT (datetime('now'))"
        ")"
    )
    conn.commit()
    if not mig_dir.exists():
        return 0

    applied = {
        r["filename"]
        for r in conn.execute("SELECT filename FROM schema_migrations")
    }
    count = 0
    for f in sorted(mig_dir.glob("*.sql")):
        if f.name in applied:
            continue
        log.info("applying migration %s", f.name)
        conn.executescript(f.read_text(encoding="utf-8"))
        conn.execute(
            "INSERT INTO schema_migrations (filename) VALUES (?)", (f.name,)
        )
        conn.commit()
        count += 1
    return count


def seed_sources(conn: sqlite3.Connection) -> None:
    """Ensure the sources rows exist. Idempotent via INSERT OR IGNORE on unique name."""
    for name, kind, interval in _SEED_SOURCES:
        conn.execute(
            "INSERT OR IGNORE INTO sources (name, kind, run_interval_min) "
            "VALUES (?, ?, ?)",
            (name, kind, interval),
        )
    conn.commit()


def source_id(conn: sqlite3.Connection, name: str) -> int:
    row = conn.execute("SELECT id FROM sources WHERE name = ?", (name,)).fetchone()
    if row is None:
        raise ValueError(f"unknown source '{name}'; run init-db first")
    return row["id"]


def init_db(db_path: Path | str | None = None) -> sqlite3.Connection:
    """Full initialization: schema + migrations + source seeding."""
    conn = connect(db_path)
    apply_schema(conn)
    run_migrations(conn)
    seed_sources(conn)
    return conn
