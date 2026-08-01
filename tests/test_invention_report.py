"""Task 37 item 4: count invention, so the other three items are not guesswork.

Prevention (item 1) and recovery (item 2) are both hypotheses until something
counts whether the advisor still cites ids that do not exist, and whether the
retries get it back. The events table is the record; this reads it.
"""

from __future__ import annotations

import dataclasses
import sqlite3
from pathlib import Path

import pytest
from typer.testing import CliRunner

from jobpilot.apply_flow import ApplicationGenerationError, approve_application
from jobpilot.config import get_settings
from jobpilot.review import invention_report
from jobpilot.tailoring import TailoringPlan
from tests.test_tailoring import _Toolchain
from tests.test_tailoring_retry import _payload, _queued_application


class _Invents:
    """Cites an id that exists nowhere, for a chosen number of attempts."""

    accepts_correction = True

    def __init__(self, *, failures: int, fact_id: str = "skill.rules.sigma") -> None:
        self.failures = failures
        self.fact_id = fact_id
        self.corrections: list[str | None] = []

    @property
    def call_count(self) -> int:
        return len(self.corrections)

    def advise(self, offer, selection, template, *, correction: str | None = None):
        self.corrections.append(correction)
        payload = _payload()
        if self.call_count <= self.failures:
            payload["skill_order"] = [self.fact_id, *payload["skill_order"]]
        return TailoringPlan.from_mapping(payload, offer=offer, selection=selection)


# ----- an empty history reads as empty, not as an error -----


def test_a_database_with_no_generations_reports_nothing(
    db: sqlite3.Connection,
) -> None:
    report = invention_report(db)

    assert report["rejections"] == 0
    assert report["distinct_ids"] == 0
    assert report["recovery_rate"] is None
    assert report["invention_rate"] is None
    assert report["by_section"] == []


def test_a_clean_generation_records_no_invention(
    db: sqlite3.Connection, tmp_path: Path
) -> None:
    from tests.test_tailoring_retry import _RecordingAdvisor

    application_id = _queued_application(db, suffix="clean")
    approve_application(
        db, application_id, via="test",
        advisor=_RecordingAdvisor(failures=0), toolchain=_Toolchain(),
        output_root=tmp_path,
    )

    report = invention_report(db)

    assert report["generations"] == 1
    assert report["rejections"] == 0
    assert report["invention_rate"] == 0.0


# ----- what a rejection records -----


def test_a_rejection_records_the_id_section_and_attempt(
    db: sqlite3.Connection, tmp_path: Path
) -> None:
    application_id = _queued_application(db, suffix="rejected")
    approve_application(
        db, application_id, via="test",
        advisor=_Invents(failures=1), toolchain=_Toolchain(), output_root=tmp_path,
    )

    report = invention_report(db)

    assert report["rejections"] == 1
    assert report["distinct_ids"] == 1
    (section,) = report["by_section"]
    assert section["section"] == "skills"
    assert section["ids"] == [("skill.rules.sigma", 1)]
    # skill.rules.sigma resolves to no near entry: that is the case item 1 targets.
    assert section["had_similar"] == 0


def test_a_recovered_invention_is_counted_as_recovered(
    db: sqlite3.Connection, tmp_path: Path
) -> None:
    application_id = _queued_application(db, suffix="recovered")
    approve_application(
        db, application_id, via="test",
        advisor=_Invents(failures=1), toolchain=_Toolchain(), output_root=tmp_path,
    )

    report = invention_report(db)

    assert report["recovered_ids"] == 1
    assert report["unrecovered_ids"] == 0
    assert report["recovery_rate"] == 1.0


def test_an_invention_that_never_recovers_is_counted_as_unresolved(
    db: sqlite3.Connection, tmp_path: Path
) -> None:
    application_id = _queued_application(db, suffix="never")

    with pytest.raises(ApplicationGenerationError):
        approve_application(
            db, application_id, via="test",
            advisor=_Invents(failures=99), toolchain=_Toolchain(),
            output_root=tmp_path,
        )

    report = invention_report(db)

    assert report["rejections"] == 3  # the first attempt and both retries
    assert report["distinct_ids"] == 1
    assert report["recovered_ids"] == 0
    assert report["unrecovered_ids"] == 1
    assert report["recovery_rate"] == 0.0


def test_a_dropped_citation_is_not_counted_as_a_recovery(
    db: sqlite3.Connection, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Item 3 degrades the CV; that is a different outcome from getting it right."""

    from jobpilot import tailoring

    monkeypatch.setattr(
        tailoring, "get_settings",
        lambda: dataclasses.replace(
            get_settings(), tailoring_drop_unknown_citations=True
        ),
    )
    application_id = _queued_application(db, suffix="dropped")
    approve_application(
        db, application_id, via="test",
        advisor=_Invents(failures=99), toolchain=_Toolchain(), output_root=tmp_path,
    )

    report = invention_report(db)

    assert report["dropped_ids"] == 1
    assert report["recovered_ids"] == 0
    assert report["unrecovered_ids"] == 0


def test_rates_are_computed_across_several_generations(
    db: sqlite3.Connection, tmp_path: Path
) -> None:
    """The question item 4 exists to answer, after more than one run."""

    from tests.test_tailoring_retry import _RecordingAdvisor

    for index in range(3):
        approve_application(
            db, _queued_application(db, suffix=f"clean{index}"), via="test",
            advisor=_RecordingAdvisor(failures=0), toolchain=_Toolchain(),
            output_root=tmp_path,
        )
    approve_application(
        db, _queued_application(db, suffix="dirty"), via="test",
        advisor=_Invents(failures=1), toolchain=_Toolchain(), output_root=tmp_path,
    )

    report = invention_report(db)

    assert report["generations"] == 4
    assert report["distinct_ids"] == 1
    assert report["invention_rate"] == pytest.approx(0.25)
    assert report["recovery_rate"] == 1.0


def test_sections_are_reported_separately(
    db: sqlite3.Connection, tmp_path: Path
) -> None:
    for suffix, fact_id in (("s1", "skill.rules.sigma"), ("s2", "skill.autre.chose")):
        approve_application(
            db, _queued_application(db, suffix=suffix), via="test",
            advisor=_Invents(failures=1, fact_id=fact_id), toolchain=_Toolchain(),
            output_root=tmp_path,
        )

    report = invention_report(db)

    (section,) = report["by_section"]
    assert section["section"] == "skills"
    assert section["rejections"] == 2
    assert section["distinct_ids"] == 2


# ----- the command -----


def test_the_command_reports_an_empty_history_plainly(
    db: sqlite3.Connection, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from jobpilot import cli

    monkeypatch.setattr(cli, "connect", lambda: db)
    result = CliRunner().invoke(cli.app, ["invention-report"])

    assert result.exit_code == 0
    assert "no invented fact ids recorded" in result.output


def test_the_command_summarises_by_section_and_rate(
    db: sqlite3.Connection, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from jobpilot import cli

    approve_application(
        db, _queued_application(db, suffix="cmd"), via="test",
        advisor=_Invents(failures=1), toolchain=_Toolchain(), output_root=tmp_path,
    )
    monkeypatch.setattr(cli, "connect", lambda: db)

    result = CliRunner().invoke(cli.app, ["invention-report"])

    assert result.exit_code == 0
    assert "skill.rules.sigma" in result.output
    assert "recovery rate" in result.output
    assert "invention rate" in result.output
    assert "skills" in result.output
