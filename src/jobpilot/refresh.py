"""Background ingest + score refresh triggered from the dashboard.

The web layer owns no ingest or scoring logic: this runner calls exactly the
functions ``jobpilot ingest`` and ``jobpilot score`` call. It only adds the
single-flight guard and the progress snapshot the page polls.

SQLite has one writer, so every database step is taken under the shared
``APPLICATION_LOCK``; the status snapshot lives in memory behind its own lock so
polling never waits on the running refresh.
"""

from __future__ import annotations

import sqlite3
import threading
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from typing import Any

from jobpilot.apply_flow import APPLICATION_LOCK
from jobpilot.config import MissingCredentialError, get_settings
from jobpilot.db import connect
from jobpilot.ingest import IngestResult, ingest_source
from jobpilot.logging_conf import get_logger
from jobpilot.sources.base import Source
from jobpilot.sources.registry import build_source, enabled_sources

log = get_logger("refresh")

# Vocabulary the page renders; kept here so the template and tests agree.
SOURCE_STATES: tuple[str, ...] = ("pending", "running", "done", "skipped", "failed")
STAGES: tuple[str, ...] = ("idle", "ingesting", "loading_model", "scoring", "done")


class RefreshAlreadyRunning(RuntimeError):
    """Raised when a second refresh is requested while one is still running."""


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(frozen=True, slots=True)
class SourceProgress:
    """One source's outcome, kept even when the source failed or was skipped."""

    name: str
    state: str
    fetched: int = 0
    inserted: int = 0
    duplicates: int = 0
    message: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "state": self.state,
            "fetched": self.fetched,
            "inserted": self.inserted,
            "duplicates": self.duplicates,
            "message": self.message,
        }


@dataclass(frozen=True, slots=True)
class RefreshStatus:
    """Immutable snapshot handed to the status endpoint."""

    running: bool = False
    stage: str = "idle"
    sources: tuple[SourceProgress, ...] = ()
    queued: int | None = None
    error: str | None = None
    started_at: str | None = None
    finished_at: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "running": self.running,
            "stage": self.stage,
            "sources": [source.as_dict() for source in self.sources],
            "queued": self.queued,
            "error": self.error,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }


@contextmanager
def _production_connection() -> Iterator[sqlite3.Connection]:
    """One dedicated connection per refresh; the request's own is long gone."""

    connection = connect()
    try:
        yield connection
    finally:
        connection.close()


def _default_model_loader() -> Any:
    """Load the embedding model. Lazy exactly as the CLI's `score` path is."""

    from jobpilot.embeddings import get_embed_fn  # heavy: torch + transformers

    return get_embed_fn()


def _default_score_pass(db: sqlite3.Connection, embed_fn: Any) -> int:
    """Score exactly as ``jobpilot score`` does, with the model already loaded."""

    from jobpilot.scoring import score

    return score(db, embed_fn)


ConnectionFactory = Callable[[], Any]


class RefreshRunner:
    """Single-flight ingest + score pass driven from the dashboard."""

    def __init__(
        self,
        *,
        connection_factory: ConnectionFactory | None = None,
        source_names: Callable[[], list[str]] | None = None,
        source_builder: Callable[[str], Source] | None = None,
        ingest: Callable[[sqlite3.Connection, Source], IngestResult] | None = None,
        model_loader: Callable[[], Any] | None = None,
        score_pass: Callable[[sqlite3.Connection, Any], int] | None = None,
    ) -> None:
        self._connection_factory = connection_factory or _production_connection
        self._source_names = source_names or enabled_sources
        self._source_builder = source_builder or build_source
        self._ingest = ingest or ingest_source
        self._model_loader = model_loader or _default_model_loader
        self._score_pass = score_pass or _default_score_pass
        self._lock = threading.Lock()
        self._status = RefreshStatus()
        self._done = threading.Event()
        self._done.set()

    # ----- status -----

    def status(self) -> RefreshStatus:
        with self._lock:
            return self._status

    def wait(self, timeout: float | None = None) -> bool:
        """Block until the running refresh finishes. Tests use this, not sleeps."""

        return self._done.wait(timeout)

    def _update(self, **changes: Any) -> None:
        with self._lock:
            self._status = replace(self._status, **changes)

    def _set_source(self, progress: SourceProgress) -> None:
        with self._lock:
            self._status = replace(
                self._status,
                sources=tuple(
                    progress if item.name == progress.name else item
                    for item in self._status.sources
                ),
            )

    # ----- control -----

    def start(self) -> RefreshStatus:
        """Claim the single flight and hand the work to a background thread."""

        names = list(self._source_names())
        with self._lock:
            if self._status.running:
                raise RefreshAlreadyRunning("a refresh is already running")
            self._status = RefreshStatus(
                running=True,
                stage="ingesting",
                sources=tuple(
                    SourceProgress(name=name, state="pending") for name in names
                ),
                started_at=_utc_now(),
            )
            self._done = done = threading.Event()
            snapshot = self._status
        thread = threading.Thread(
            target=self._run,
            args=(names, done),
            name="jobpilot-refresh",
            daemon=True,
        )
        thread.start()
        return snapshot

    # ----- worker -----

    def _run(self, names: list[str], done: threading.Event) -> None:
        try:
            with self._connection_factory() as db:
                self._ingest_all(db, names)
                self._score(db)
        except Exception as exc:  # a runner crash must surface, not vanish
            log.exception("refresh failed")
            self._update(error=get_settings().redact(str(exc)))
        finally:
            self._update(
                running=False,
                stage="done",
                finished_at=_utc_now(),
            )
            done.set()

    def _ingest_all(self, db: sqlite3.Connection, names: list[str]) -> None:
        for name in names:
            self._set_source(SourceProgress(name=name, state="running"))
            try:
                source = self._source_builder(name)
            except MissingCredentialError as exc:
                self._set_source(
                    SourceProgress(
                        name=name,
                        state="skipped",
                        message=get_settings().redact(str(exc)),
                    )
                )
                continue
            try:
                # One writer at a time; released between sources so the page
                # and the approval flow are not blocked for the whole run.
                with APPLICATION_LOCK:
                    result = self._ingest(db, source)
            except Exception as exc:  # one bad source must not hide the others
                log.exception("ingest failed for %s", name)
                self._set_source(
                    SourceProgress(
                        name=name,
                        state="failed",
                        message=get_settings().redact(str(exc)),
                    )
                )
                continue
            self._set_source(
                SourceProgress(
                    name=name,
                    state="done",
                    fetched=result.fetched,
                    inserted=result.inserted,
                    duplicates=result.duplicates,
                )
            )

    def _score(self, db: sqlite3.Connection) -> None:
        # The model load touches no database, so it stays outside the writer lock
        # even though it is the slowest part of a first refresh.
        self._update(stage="loading_model")
        try:
            embed_fn = self._model_loader()
            self._update(stage="scoring")
            with APPLICATION_LOCK:
                queued = self._score_pass(db, embed_fn)
        except Exception as exc:
            log.exception("scoring failed")
            self._update(error=get_settings().redact(str(exc)))
            return
        self._update(queued=queued)
