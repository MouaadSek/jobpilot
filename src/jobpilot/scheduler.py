"""Background daemon: run ingest + score on a fixed interval (default 3h).

The daemon is platform-neutral. macOS launchd and Windows Task Scheduler
helpers in ``deploy/`` keep it alive; all real work stays in ingest/scoring.
"""

from __future__ import annotations

import sqlite3

from apscheduler.schedulers.blocking import BlockingScheduler

from jobpilot.config import MissingCredentialError, get_settings
from jobpilot.db import connect
from jobpilot.ingest import ingest_source
from jobpilot.logging_conf import get_logger
from jobpilot.scoring import score
from jobpilot.sources.registry import build_source, enabled_sources

log = get_logger("scheduler")


def run_cycle() -> None:
    """One ingest-all + score pass. Sources with missing creds are skipped."""
    conn: sqlite3.Connection = connect()
    try:
        for name in enabled_sources():
            try:
                src = build_source(name)
            except MissingCredentialError as exc:
                log.info("skip %s: %s", name, exc)
                continue
            try:
                ingest_source(conn, src)
            except Exception:  # one bad source must not kill the cycle
                log.exception("ingest failed for %s", name)
        try:
            score(conn)
        except Exception:
            log.exception("scoring failed")
    finally:
        conn.close()


def run_daemon(interval_hours: float = 3.0) -> None:
    settings = get_settings()
    log.info("starting daemon: cycle every %sh, db=%s", interval_hours,
             settings.db_path)
    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(
        run_cycle, "interval", hours=interval_hours,
        id="ingest_score", max_instances=1, coalesce=True,
    )
    run_cycle()  # run once immediately on startup
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        log.info("daemon stopped")
