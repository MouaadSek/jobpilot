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


#: How long a writer waits for the lock before raising "database is locked".
#: The daemon and the dashboard are two processes on one file now, so a blocked
#: writer is a normal event rather than a bug, and failing instantly on it would
#: be. Thirty seconds covers every write either process makes on its own; it
#: does not cover a writer that holds its transaction open across the network —
#: see the note on ``ingest_source``.
BUSY_TIMEOUT_MS = 30_000


def connect(db_path: Path | str | None = None) -> sqlite3.Connection:
    """Open a connection with Row factory, foreign keys, WAL, and a busy timeout.

    matcher.py relies on sqlite3.Row access (offer["title"]); keep it here.

    WAL is what makes two processes on this file workable at all: under the
    default rollback journal a single dashboard read blocks the daemon's writes
    and vice versa. Under WAL, readers never block the writer and the writer
    never blocks readers, so the dashboard stays answerable through a whole
    ingest cycle. It is a property of the database file, not of the connection,
    so setting it here is a one-time conversion that every later connection
    inherits; re-issuing it is a no-op.
    """
    path = Path(db_path) if db_path else get_settings().db_path
    if path != Path(":memory:"):
        path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute(f"PRAGMA busy_timeout = {BUSY_TIMEOUT_MS}")
    # An in-memory database has no file to journal and reports back "memory";
    # asking is harmless, so the call is not special-cased, only the check is.
    mode = conn.execute("PRAGMA journal_mode = WAL").fetchone()
    if path != Path(":memory:") and mode is not None and mode[0].lower() != "wal":
        # A refused conversion means the file is on a filesystem that cannot do
        # WAL (a network share). Two writers on that file is not safe, and the
        # daemon would find out by corrupting nothing and losing everything.
        log.warning(
            "WAL unavailable on %s (journal_mode=%s); concurrent daemon and "
            "dashboard writes are not safe on this filesystem",
            path,
            mode[0],
        )
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
