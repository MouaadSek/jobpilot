"""What the dashboard is doing right now, readable while it does it.

``RefreshRunner`` already had the shape: mutate an in-memory snapshot behind its
own lock, and expose it through an endpoint that touches no database so polling
never waits on the work it is reporting. This generalises that to the other slow
operations — generation, regeneration and apply — which run *inside* the request
under ``APPLICATION_LOCK``.

That is why the registry is in memory and lock-guarded rather than in SQLite: a
generation holds the writer lock for its whole duration, so a progress row in
the database could not be read until the thing it describes had already
finished.

Nothing here is durable. A restart loses it, which is correct: an operation that
is no longer running has no progress to report.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from typing import Any

from jobpilot.logging_conf import get_logger

log = get_logger("progress")

#: Minimum poll interval the page is allowed to use, in milliseconds. The spec
#: is "no faster than 1 Hz"; the client also stops entirely while hidden.
MIN_POLL_INTERVAL_MS = 1000

#: How long a finished operation stays readable, so a poll that lands just after
#: completion still sees the outcome rather than an empty registry.
RETAIN_FINISHED_SECONDS = 30.0


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(frozen=True, slots=True)
class Operation:
    """One slow thing, and how far along it is."""

    key: str
    label: str
    step: str
    done: int = 0
    total: int = 0
    started_at: str = ""
    finished_at: str | None = None
    error: str | None = None

    @property
    def running(self) -> bool:
        return self.finished_at is None

    def elapsed_seconds(self, *, now: datetime | None = None) -> float:
        started = datetime.fromisoformat(self.started_at)
        end = (
            datetime.fromisoformat(self.finished_at)
            if self.finished_at
            else (now or datetime.now(UTC))
        )
        return max(0.0, (end - started).total_seconds())

    def as_dict(self, *, now: datetime | None = None) -> dict[str, Any]:
        return {
            "key": self.key,
            "label": self.label,
            "step": self.step,
            "done": self.done,
            "total": self.total,
            "running": self.running,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "error": self.error,
            "elapsed_seconds": round(self.elapsed_seconds(now=now), 1),
        }


class ProgressRegistry:
    """Every operation currently worth reporting, keyed by a stable string."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._operations: dict[str, Operation] = {}

    def start(self, key: str, label: str, *, step: str = "", total: int = 0) -> Operation:
        operation = Operation(
            key=key, label=label, step=step, total=total, started_at=_utc_now()
        )
        with self._lock:
            self._operations[key] = operation
        return operation

    def advance(
        self,
        key: str,
        *,
        step: str | None = None,
        done: int | None = None,
        total: int | None = None,
    ) -> None:
        """Update a running operation. A key that is not running is ignored."""

        with self._lock:
            current = self._operations.get(key)
            if current is None or not current.running:
                return
            changes: dict[str, Any] = {}
            if step is not None:
                changes["step"] = step
            if done is not None:
                changes["done"] = done
            if total is not None:
                changes["total"] = total
            self._operations[key] = replace(current, **changes)

    def finish(self, key: str, *, step: str = "", error: str | None = None) -> None:
        """Close an operation. The first outcome recorded wins.

        A handled failure calls this, and then the surrounding ``with`` block
        exits normally and calls it again with "Terminé". Without the guard the
        generic completion would overwrite the specific failure and the operator
        would be told a rejected generation had succeeded.
        """

        with self._lock:
            current = self._operations.get(key)
            if current is None or not current.running:
                return
            self._operations[key] = replace(
                current,
                step=step or current.step,
                finished_at=_utc_now(),
                error=error,
            )

    def get(self, key: str) -> Operation | None:
        with self._lock:
            return self._operations.get(key)

    def _prune(self, now: datetime) -> None:
        stale = [
            key
            for key, operation in self._operations.items()
            if not operation.running
            and operation.elapsed_seconds(now=now) is not None
            and (now - datetime.fromisoformat(operation.finished_at or "")).total_seconds()
            > RETAIN_FINISHED_SECONDS
        ]
        for key in stale:
            del self._operations[key]

    def snapshot(self, *, now: datetime | None = None) -> list[dict[str, Any]]:
        """Everything running, plus anything that finished very recently."""

        moment = now or datetime.now(UTC)
        with self._lock:
            self._prune(moment)
            operations = list(self._operations.values())
        return [operation.as_dict(now=moment) for operation in operations]

    def clear(self) -> None:
        with self._lock:
            self._operations.clear()


#: One registry per process. The dashboard is single-user and loopback-only.
REGISTRY = ProgressRegistry()


class track:  # noqa: N801 - used as a context manager, reads as a verb
    """Report one operation for as long as it runs, however it ends.

    ``with track("generate:12", "Génération des documents"):`` publishes the
    operation, and the ``finally`` clause guarantees it is closed out — a
    failure that never cleared its progress would leave the page claiming work
    was still happening forever.
    """

    def __init__(
        self,
        key: str,
        label: str,
        *,
        step: str = "",
        total: int = 0,
        registry: ProgressRegistry | None = None,
    ) -> None:
        self.key = key
        self._registry = registry or REGISTRY
        self._registry.start(key, label, step=step, total=total)

    def advance(
        self, step: str | None = None, *, done: int | None = None, total: int | None = None
    ) -> None:
        self._registry.advance(self.key, step=step, done=done, total=total)

    def fail(self, message: str) -> None:
        """Record a failure the caller handled rather than raised.

        The dashboard catches generation errors and renders them, so nothing
        propagates out of the ``with`` block; without this, a rejected
        generation would be reported to the operator as having succeeded.
        """

        self._registry.finish(self.key, step="Échec", error=message)

    def __enter__(self) -> track:
        return self

    def __exit__(self, exc_type: object, exc: BaseException | None, tb: object) -> None:
        if exc is None:
            self._registry.finish(self.key, step="Terminé")
            return
        # The message is the operator's, not a stack trace: Task 34 established
        # that the validator's own words are what the human needs to see.
        self._registry.finish(self.key, step="Échec", error=str(exc) or type(exc).__name__)


def refresh_operation(status: dict[str, Any]) -> dict[str, Any] | None:
    """Present a RefreshRunner snapshot in the same shape as everything else.

    Refresh keeps its own richer per-source status endpoint; this is the summary
    line, so one poll can drive the whole page.
    """

    if not status.get("started_at"):
        return None
    sources = status.get("sources") or []
    done = sum(1 for source in sources if source.get("state") in {"done", "skipped", "failed"})
    running = next(
        (source["name"] for source in sources if source.get("state") == "running"), None
    )
    stage = status.get("stage") or "idle"
    step = f"{running} {done}/{len(sources)}" if running else stage
    operation = Operation(
        key="refresh",
        label="Actualisation des offres",
        step=step,
        done=done,
        total=len(sources),
        started_at=status["started_at"],
        finished_at=status.get("finished_at") if not status.get("running") else None,
        error=status.get("error"),
    )
    return operation.as_dict()
