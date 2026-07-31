"""Every CV and letter ever generated, retrievable.

The case this exists for: an employer calls back six weeks later and the exact
CV that was sent has to be produced. Task 34 already archives the previous
generation on every regenerate, into
``output/applications/<id>/archive/<UTC stamp>/``, so the history is on disk
already — this reads it back rather than adding storage or a table.

An archived generation is read-only. Nothing here transitions anything, and
there is deliberately no route from an archive back to ``ready``: restoring an
old generation would mean the database and the artefacts disagreed about which
documents the application actually holds.
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from jobpilot.apply_flow import ARCHIVE_DIR_NAME
from jobpilot.logging_conf import get_logger

log = get_logger("library")

#: The documents worth listing. Intermediate HTML is on disk but nobody sends it.
LIBRARY_ARTIFACTS: tuple[str, ...] = ("cv.pdf", "motivation_letter.pdf")

#: ISO 8601 basic format, as written by ``apply_flow.archive_artifacts``. Task 34
#: used basic rather than extended because the extended form's colons are not
#: legal in a Windows filename.
ARCHIVE_STAMP_RE = re.compile(r"^\d{8}T\d{6}Z(?:-\d+)?$")


def is_archive_stamp(value: str) -> bool:
    """Whether ``value`` is a stamp this application itself wrote."""

    return bool(ARCHIVE_STAMP_RE.fullmatch(value))


def _stamp_to_iso(stamp: str) -> str | None:
    """Read a directory stamp back as an ISO timestamp, for display."""

    base = stamp.split("-", 1)[0]
    try:
        moment = datetime.strptime(base, "%Y%m%dT%H%M%SZ").replace(tzinfo=UTC)
    except ValueError:
        return None
    return moment.isoformat()


@dataclass(frozen=True, slots=True)
class Generation:
    """One set of documents: either the live one or an archived one."""

    artifacts: tuple[str, ...]
    generated_at: str | None
    stamp: str | None = None

    @property
    def is_archived(self) -> bool:
        return self.stamp is not None

    def as_dict(self) -> dict[str, Any]:
        return {
            "artifacts": list(self.artifacts),
            "generated_at": self.generated_at,
            "stamp": self.stamp,
            "is_archived": self.is_archived,
        }


@dataclass(frozen=True, slots=True)
class LibraryEntry:
    """One application and every generation of its documents."""

    application_id: int
    company: str | None
    title: str | None
    status: str
    variant: str | None
    apply_route: str | None
    current: Generation | None
    archives: tuple[Generation, ...]

    @property
    def generations(self) -> int:
        return len(self.archives) + (1 if self.current else 0)

    def as_dict(self) -> dict[str, Any]:
        return {
            "application_id": self.application_id,
            "company": self.company,
            "title": self.title,
            "status": self.status,
            "variant": self.variant,
            "apply_route": self.apply_route,
            "current": self.current.as_dict() if self.current else None,
            "archives": [archive.as_dict() for archive in self.archives],
            "generations": self.generations,
        }


def _mtime_iso(path: Path) -> str | None:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, tz=UTC).isoformat()
    except OSError:  # pragma: no cover - the file was listed a moment ago
        return None


def _read_generation(directory: Path, *, stamp: str | None) -> Generation | None:
    """The documents present in one directory, or None if it holds none."""

    present = tuple(
        name for name in LIBRARY_ARTIFACTS if (directory / name).is_file()
    )
    if not present:
        return None
    generated_at = (
        _stamp_to_iso(stamp) if stamp else _mtime_iso(directory / present[0])
    )
    return Generation(artifacts=present, generated_at=generated_at, stamp=stamp)


def _archives_for(application_dir: Path) -> tuple[Generation, ...]:
    """Archived generations, newest first.

    A directory whose name is not a stamp this application wrote is ignored
    rather than guessed at: the archive tree is only ever written by
    ``archive_artifacts``, so anything else in there did not come from JobPilot.
    """

    archive_root = application_dir / ARCHIVE_DIR_NAME
    if not archive_root.is_dir():
        return ()
    found: list[Generation] = []
    for child in sorted(archive_root.iterdir(), reverse=True):
        if not child.is_dir():
            continue
        if not is_archive_stamp(child.name):
            log.debug("ignoring unrecognised archive directory %s", child)
            continue
        generation = _read_generation(child, stamp=child.name)
        if generation is not None:
            found.append(generation)
    return tuple(found)


def _variant_used(db: sqlite3.Connection, application_id: int) -> str | None:
    """Which CV variant this application's documents were built from."""

    from jobpilot.review import variant_decision

    decision = variant_decision(db, application_id)
    if not decision:
        return None
    return decision.get("document_variant") or decision.get("variant")


def library_entries(
    db: sqlite3.Connection,
    output_root: Path,
    *,
    search: str | None = None,
) -> tuple[LibraryEntry, ...]:
    """Every application that has generated documents, newest generation first.

    Applications with no artefacts on disk are left out entirely: this is a
    library of documents, not another list of applications.
    """

    clause = ""
    params: list[Any] = []
    if search and search.strip():
        clause = " AND lower(COALESCE(c.name, '')) LIKE ?"
        params.append(f"%{search.strip().lower()}%")

    rows = db.execute(
        "SELECT a.id, a.status, a.apply_route, o.title, "
        "       COALESCE(c.name, c2.name) AS company "
        "FROM applications a "
        "LEFT JOIN offers o ON o.id = a.offer_id "
        "LEFT JOIN companies c ON c.id = o.company_id "
        "LEFT JOIN companies c2 ON c2.id = a.company_id "
        f"WHERE a.kind = 'offer'{clause} "
        "ORDER BY a.id DESC",
        params,
    ).fetchall()

    root = Path(output_root)
    entries: list[LibraryEntry] = []
    for row in rows:
        application_dir = root / str(row["id"])
        if not application_dir.is_dir():
            continue
        current = _read_generation(application_dir, stamp=None)
        archives = _archives_for(application_dir)
        if current is None and not archives:
            continue
        entries.append(
            LibraryEntry(
                application_id=int(row["id"]),
                company=row["company"],
                title=row["title"],
                status=row["status"],
                variant=_variant_used(db, int(row["id"])),
                apply_route=row["apply_route"],
                current=current,
                archives=archives,
            )
        )
    return tuple(entries)
