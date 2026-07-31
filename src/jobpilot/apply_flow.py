"""Shared human-approval and document-generation application flow."""

from __future__ import annotations

import importlib
import sqlite3
import threading
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from jobpilot.logging_conf import get_logger
from jobpilot.state import current_status, log_event, transition

log = get_logger("apply_flow")

# SQLite is single-user here, and a dashboard double-click must not start two
# generations. RLock also lets the TestClient's shared in-memory connection use
# this exact lock in its dependency override.
APPLICATION_LOCK = threading.RLock()

#: Where a regeneration puts the run it is about to replace.
ARCHIVE_DIR_NAME = "archive"

# Which applications are generating right now. Same single-flight discipline as
# RefreshRunner's: one lock guards the claim, the check and the claim happen in
# one critical section, and a second caller is refused rather than queued
# behind the first. Keyed per application id so two different applications can
# generate concurrently.
_GENERATING: set[int] = set()
_GENERATING_LOCK = threading.Lock()


class ApplicationNotFoundError(LookupError):
    """Raised when an approval targets an unknown application."""


class ApplicationNotQueuedError(RuntimeError):
    """Raised when an approval targets an application outside the review queue."""


class ApplicationGenerationError(RuntimeError):
    """A redacted generation failure suitable for CLI and dashboard display."""


class GenerationInFlight(RuntimeError):
    """Raised when a generation is already running for this application."""


class InteractiveAdvisorRequired(RuntimeError):
    """Raised when only the terminal advisor is available to a headless caller.

    The dashboard has no terminal to prompt on: without this the request would
    hang forever while a hidden console waited for keyboard input.
    """


@dataclass(frozen=True)
class ApplyOutcome:
    """The result shared by the CLI and dashboard approval surfaces."""

    application_id: int
    is_cold_application: bool
    generation: Any | None


@contextmanager
def generation_single_flight(application_id: int) -> Iterator[None]:
    """Claim the one generation slot for ``application_id``, or refuse.

    Taken *before* ``APPLICATION_LOCK``, which is the whole point: a second
    click that waited on the writer lock would be admitted the moment the first
    generation released it, find the application ready again, and start a
    second run. Refusing up front is what makes a double click a no-op.
    """

    with _GENERATING_LOCK:
        if application_id in _GENERATING:
            raise GenerationInFlight(
                "Une génération est déjà en cours pour cette candidature."
            )
        _GENERATING.add(application_id)
    try:
        yield
    finally:
        with _GENERATING_LOCK:
            _GENERATING.discard(application_id)


def archive_artifacts(output_root: Path, application_id: int) -> Path | None:
    """Move an application's current artefacts aside; return where they went.

    Diffing generation N against N+1 is the entire point of regenerating, so
    the previous run is moved rather than overwritten. Nothing in the
    application ever reads these directories back — they exist for a human with
    a diff tool — and they live under ``output/``, which is gitignored.

    The stamp is ISO 8601 *basic* format. The extended format's colons are not
    legal in a Windows filename and CI runs Windows.
    """

    application_dir = Path(output_root) / str(application_id)
    if not application_dir.is_dir():
        return None
    artifacts = sorted(path for path in application_dir.iterdir() if path.is_file())
    if not artifacts:
        return None

    archive_root = application_dir / ARCHIVE_DIR_NAME
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    destination = archive_root / stamp
    # Two regenerations inside the same second would otherwise land on the same
    # directory, and an archive that overwrites an archive helps nobody.
    attempt = 1
    while destination.exists():
        attempt += 1
        destination = archive_root / f"{stamp}-{attempt}"
    destination.mkdir(parents=True)

    for artifact in artifacts:
        artifact.replace(destination / artifact.name)
    log.info(
        "application %d: archived %d artefact(s) to %s",
        application_id,
        len(artifacts),
        destination,
    )
    return destination


def approve_application(
    db: sqlite3.Connection,
    application_id: int,
    *,
    via: str,
    on_generating: Callable[[], None] | None = None,
    advisor: Any | None = None,
    toolchain: Any | None = None,
    output_root: Path | None = None,
    templates_dir: Path | None = None,
    allow_interactive_advisor: bool = True,
) -> ApplyOutcome:
    """Record human approval, transition, and generate through one shared path.

    ``allow_interactive_advisor=False`` refuses the approval outright when the
    configured advisor would prompt on a terminal. The refusal happens before any
    event is written, so the audit trail never shows an approval that did nothing.
    """

    try:
        status = current_status(db, application_id)
    except ValueError as exc:
        raise ApplicationNotFoundError(str(exc)) from exc
    if status != "queued":
        raise ApplicationNotQueuedError("application is not in 'queued' state")

    row = db.execute(
        "SELECT kind FROM applications WHERE id = ?",
        (application_id,),
    ).fetchone()
    if row is None:
        raise ApplicationNotFoundError(f"no application with id={application_id}")
    is_cold_application = row["kind"] == "cold"

    # Keep cold outreach independent from the optional CV/LLM toolchain.
    tailoring = None
    if not is_cold_application:
        tailoring = importlib.import_module("jobpilot.tailoring")
        # Check before anything is recorded: no status change and no
        # human_approved event for an approval that cannot proceed.
        if not allow_interactive_advisor and advisor is None:
            try:
                provider = tailoring.resolve_provider()
            except tailoring.TailoringError as exc:
                raise ApplicationGenerationError(str(exc)) from exc
            if provider == "interactive":
                raise InteractiveAdvisorRequired(
                    "Le tailoring automatique nécessite une clé API "
                    "(OPENAI_API_KEY ou ANTHROPIC_API_KEY dans .env). Le mode "
                    "interactif reste disponible via `jobpilot apply`."
                )

    # Constitution: nothing is sent/submitted without recorded human approval.
    log_event(db, application_id, "human_approved", {"via": via})
    transition(db, application_id, "generating")
    if on_generating is not None:
        on_generating()

    if is_cold_application:
        return ApplyOutcome(application_id, True, None)

    generation_options: dict[str, Any] = {}
    if advisor is not None:
        generation_options["advisor"] = advisor
    if toolchain is not None:
        generation_options["toolchain"] = toolchain
    if output_root is not None:
        generation_options["output_root"] = output_root
    if templates_dir is not None:
        generation_options["templates_dir"] = templates_dir

    assert tailoring is not None
    try:
        generation = tailoring.generate_application(
            db,
            application_id,
            **generation_options,
        )
    except tailoring.TailoringError as exc:
        raise ApplicationGenerationError(str(exc)) from exc
    return ApplyOutcome(application_id, False, generation)
