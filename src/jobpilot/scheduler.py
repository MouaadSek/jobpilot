"""Background daemon: run ingest + score on a fixed interval (default 3h).

The daemon is platform-neutral. macOS launchd and Windows Task Scheduler
helpers in ``deploy/`` keep it alive; all real work stays in ingest/scoring.

Each completed cycle writes a heartbeat file so the dashboard can report whether
the daemon is alive from a recorded fact rather than a guess.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from jobpilot.config import MissingCredentialError, Settings, get_settings
from jobpilot.db import connect
from jobpilot.ingest import ingest_source
from jobpilot.logging_conf import get_logger
from jobpilot.sources.registry import build_source, enabled_sources

log = get_logger("scheduler")

HEARTBEAT_FILENAME = "scheduler.heartbeat"
# A daemon that has missed two whole cycles is not merely late.
STALE_CYCLE_FACTOR = 2


def _utc_now() -> datetime:
    return datetime.now(UTC)


def heartbeat_path(settings: Settings | None = None) -> Path:
    return (settings or get_settings()).log_dir / HEARTBEAT_FILENAME


def write_heartbeat(interval_hours: float | None = None) -> None:
    """Record that a cycle completed. Never fatal: a daemon must not die on this."""

    path = heartbeat_path()
    payload = {"at": _utc_now().isoformat(), "interval_hours": interval_hours}
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")
    except OSError:
        log.warning("could not write scheduler heartbeat to %s", path)


@dataclass(frozen=True, slots=True)
class DaemonStatus:
    """What can honestly be said about the daemon, and nothing more."""

    state: str  # "actif" | "inactif" | "inconnu"
    last_beat_at: str | None
    interval_hours: float | None
    detail: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "last_beat_at": self.last_beat_at,
            "interval_hours": self.interval_hours,
            "detail": self.detail,
        }


def daemon_status(settings: Settings | None = None) -> DaemonStatus:
    """Report daemon liveness from the heartbeat file, or admit it is unknown."""

    path = heartbeat_path(settings)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return DaemonStatus(
            state="inconnu",
            last_beat_at=None,
            interval_hours=None,
            detail=(
                "Aucun battement enregistré. Lancez `jobpilot daemon` (ou le "
                "service launchd) pour que son activité devienne visible ici."
            ),
        )

    raw_beat = payload.get("at") if isinstance(payload, dict) else None
    interval = payload.get("interval_hours") if isinstance(payload, dict) else None
    try:
        beat = datetime.fromisoformat(str(raw_beat))
    except (TypeError, ValueError):
        return DaemonStatus(
            state="inconnu",
            last_beat_at=None,
            interval_hours=None,
            detail="Battement illisible ; l'activité du démon est indéterminable.",
        )
    if beat.tzinfo is None:
        beat = beat.replace(tzinfo=UTC)
    interval_hours = float(interval) if isinstance(interval, int | float) else None

    age_hours = (_utc_now() - beat).total_seconds() / 3600
    if interval_hours is None:
        return DaemonStatus(
            state="inconnu",
            last_beat_at=beat.isoformat(),
            interval_hours=None,
            detail=(
                "Intervalle du démon inconnu : impossible de dire si ce "
                "battement est récent."
            ),
        )
    if age_hours <= interval_hours * STALE_CYCLE_FACTOR:
        return DaemonStatus(
            state="actif",
            last_beat_at=beat.isoformat(),
            interval_hours=interval_hours,
            detail=(
                f"Dernier cycle il y a {age_hours:.1f} h "
                f"(intervalle {interval_hours:g} h)."
            ),
        )
    return DaemonStatus(
        state="inactif",
        last_beat_at=beat.isoformat(),
        interval_hours=interval_hours,
        detail=(
            f"Dernier cycle il y a {age_hours:.1f} h, soit plus de "
            f"{STALE_CYCLE_FACTOR} intervalles de {interval_hours:g} h."
        ),
    )


#: How many consecutive failed runs make a source dead rather than unlucky.
#: One failure is a timeout; three in a row, at a six-hour interval, is close to
#: a day of a source returning nothing — which is how WTTJ went unnoticed.
DEAD_AFTER_FAILURES = 3

#: How far back to look when counting that streak. Only the leading runs matter,
#: so there is nothing to gain from reading past the threshold.
_STREAK_WINDOW = DEAD_AFTER_FAILURES


def _last_runs(db: sqlite3.Connection, source_id: int) -> list[sqlite3.Row]:
    return db.execute(
        "SELECT started_at, fetched, inserted, duplicates, companies_created, error "
        "FROM source_runs WHERE source_id = ? ORDER BY id DESC LIMIT ?",
        (source_id, _STREAK_WINDOW),
    ).fetchall()


def _consecutive_failures(runs: list[sqlite3.Row]) -> int:
    """Leading failures only: one success resets the streak."""

    streak = 0
    for run in runs:
        if run["error"] is None:
            break
        streak += 1
    return streak


def source_runs(
    db: sqlite3.Connection,
    settings: Settings | None = None,
) -> list[dict[str, Any]]:
    """Last recorded run per enabled source, with what that run actually did.

    ``last_run_at`` on its own could not distinguish a source that ingested
    forty offers from one that raised on every request, because a failing source
    kept a fresh timestamp either way. The history in source_runs can, so it is
    preferred here; sources.last_run_at remains the fallback for the runs that
    predate the table.
    """

    rows = {
        row["name"]: row
        for row in db.execute("SELECT id, name, last_run_at FROM sources").fetchall()
    }
    report: list[dict[str, Any]] = []
    for name in enabled_sources(settings):
        row = rows.get(name)
        if row is None:
            report.append(
                {
                    "name": name,
                    "last_run_at": None,
                    "last_run": None,
                    "consecutive_failures": 0,
                    "dead": False,
                }
            )
            continue
        runs = _last_runs(db, row["id"])
        latest = runs[0] if runs else None
        failures = _consecutive_failures(runs)
        report.append(
            {
                "name": name,
                "last_run_at": (latest["started_at"] if latest else row["last_run_at"]),
                "last_run": dict(latest) if latest else None,
                "consecutive_failures": failures,
                "dead": failures >= DEAD_AFTER_FAILURES,
            }
        )
    return report


def scheduler_status(
    db: sqlite3.Connection,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Everything the queue page shows about scheduled ingestion."""

    return {
        "sources": source_runs(db, settings),
        "daemon": daemon_status(settings).as_dict(),
        "dead_after_failures": DEAD_AFTER_FAILURES,
    }


def run_cycle(interval_hours: float | None = None) -> None:
    """One ingest-all + score pass. Sources with missing creds are skipped."""
    from jobpilot.scoring import score  # lazy: pulls in the embedding model

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
    write_heartbeat(interval_hours)


def run_daemon(interval_hours: float = 3.0) -> None:
    from apscheduler.schedulers.blocking import BlockingScheduler

    settings = get_settings()
    log.info("starting daemon: cycle every %sh, db=%s", interval_hours,
             settings.db_path)
    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(
        run_cycle, "interval", hours=interval_hours, args=(interval_hours,),
        id="ingest_score", max_instances=1, coalesce=True,
    )
    run_cycle(interval_hours)  # run once immediately on startup
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        log.info("daemon stopped")
