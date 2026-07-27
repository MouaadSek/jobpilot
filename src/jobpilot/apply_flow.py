"""Shared human-approval and document-generation application flow."""

from __future__ import annotations

import importlib
import sqlite3
import threading
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jobpilot.state import current_status, log_event, transition

# SQLite is single-user here, and a dashboard double-click must not start two
# generations. RLock also lets the TestClient's shared in-memory connection use
# this exact lock in its dependency override.
APPLICATION_LOCK = threading.RLock()


class ApplicationNotFoundError(LookupError):
    """Raised when an approval targets an unknown application."""


class ApplicationNotQueuedError(RuntimeError):
    """Raised when an approval targets an application outside the review queue."""


class ApplicationGenerationError(RuntimeError):
    """A redacted generation failure suitable for CLI and dashboard display."""


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
