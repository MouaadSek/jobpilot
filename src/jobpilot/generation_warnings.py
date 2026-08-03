"""What a generation had to degrade, recorded where the reviewer will see it.

Task 39 moves generation from "any gate aborts" to three outcomes: fatal aborts,
recoverable degrades, advisory warns. The degradations are the dangerous half —
a document that silently lost a citation looks exactly like one that never
needed to. So every degradation writes a warning here, and the warning names the
gate, what it said, and what was done instead.

Warnings belong to the current generation only. They are replaced wholesale when
an application is regenerated, never appended to: the previous run's compromises
say nothing about the document now on disk.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from dataclasses import asdict, dataclass
from typing import Any

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class GenerationWarning:
    """One thing the reviewer is being asked to check by eye."""

    #: The gate that fired, by function name, so it is greppable in this repo.
    gate: str
    #: What the gate said, verbatim. Truncated only by the display layer.
    message: str
    #: What was done instead. Never empty — a warning with no consequence is
    #: noise, and an abort is not a warning.
    degraded: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


def _decode(raw: str | None) -> tuple[GenerationWarning, ...]:
    if not raw:
        return ()
    try:
        payload = json.loads(raw)
    except (TypeError, ValueError):
        log.warning("unreadable generation_warnings payload, treating as empty")
        return ()
    if not isinstance(payload, list):
        return ()
    warnings: list[GenerationWarning] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        warnings.append(
            GenerationWarning(
                gate=str(item.get("gate", "")),
                message=str(item.get("message", "")),
                degraded=str(item.get("degraded", "")),
            )
        )
    return tuple(warnings)


def record_warnings(
    db: sqlite3.Connection,
    application_id: int,
    warnings: list[GenerationWarning] | tuple[GenerationWarning, ...],
) -> None:
    """Replace this application's warnings with the ones from this run."""

    payload = json.dumps(
        [warning.as_dict() for warning in warnings], ensure_ascii=False
    )
    db.execute(
        "UPDATE applications SET generation_warnings = ? WHERE id = ?",
        (payload, application_id),
    )


def clear_warnings(db: sqlite3.Connection, application_id: int) -> None:
    """Drop the previous run's warnings at the start of a new generation.

    Cleared to '[]' rather than NULL: the run has begun, so "nothing yet" is a
    real answer, while NULL still means "generated before warnings existed".
    """

    db.execute(
        "UPDATE applications SET generation_warnings = '[]' WHERE id = ?",
        (application_id,),
    )


def warnings_for(
    db: sqlite3.Connection, application_id: int
) -> tuple[GenerationWarning, ...]:
    """Every warning the current generation of this application carries."""

    row = db.execute(
        "SELECT generation_warnings FROM applications WHERE id = ?",
        (application_id,),
    ).fetchone()
    if row is None:
        return ()
    return _decode(row[0])


def warning_gates_by_application(db: sqlite3.Connection) -> dict[int, tuple[str, ...]]:
    """Gate names per application, for the library and tracker markers.

    One query rather than one per row: both callers render whole lists, and a
    marker is not worth an N+1.
    """

    marks: dict[int, tuple[str, ...]] = {}
    for row in db.execute(
        "SELECT id, generation_warnings FROM applications "
        "WHERE generation_warnings IS NOT NULL AND generation_warnings != '[]'"
    ):
        gates = tuple(warning.gate for warning in _decode(row[1]))
        if gates:
            marks[int(row[0])] = gates
    return marks


def as_dicts(
    warnings: tuple[GenerationWarning, ...] | list[GenerationWarning],
) -> list[dict[str, Any]]:
    """Template-facing shape."""

    return [warning.as_dict() for warning in warnings]
