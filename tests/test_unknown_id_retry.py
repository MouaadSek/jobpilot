"""Task 37 item 2: give the unknown-id retry something to work with.

An unknown fact id is the cheapest failure to recover from and the most common,
so it gets two retries where other validator rejections get one. Provider errors
are still never retried, and nothing here accepts an invented id — the extra
attempt only buys the model another chance to pick a real one.
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

import pytest

from jobpilot.apply_flow import ApplicationGenerationError, approve_application
from jobpilot.facts import load_fact_bank
from jobpilot.state import current_status
from jobpilot.tailoring import (
    _MAX_ADVISOR_RETRIES,
    _MAX_UNKNOWN_ID_RETRIES,
    MAX_SECTION_FACT_IDS,
    TailoringError,
    TailoringPlan,
    UnknownFactIdError,
    _offered_fact_ids,
    _valid_fact_ids_block,
    extract_template_context,
    pick_variant,
)
from tests.test_selection_tailoring import TEMPLATE_PATH, _offer
from tests.test_tailoring import _Toolchain
from tests.test_tailoring_retry import _payload, _queued_application


@pytest.fixture
def rendered():
    offer = _offer()
    selection = pick_variant(offer.description, title=offer.title)
    template = extract_template_context(TEMPLATE_PATH.read_text(encoding="utf-8"))
    return offer, selection, template, load_fact_bank()


# ----- what the rejection hands back -----


def test_an_invented_skill_id_is_told_the_whole_skill_section(rendered) -> None:
    """The case that started this: skill.rules.sigma resolves to no entry, so
    the sibling-id path from Task 35 has nothing — the section listing is what
    the retry actually reads."""

    offer, selection, template, bank = rendered
    exc = UnknownFactIdError("skill.rules.sigma", section="skills")

    block = _valid_fact_ids_block(exc, selection, template, bank)

    offered = _offered_fact_ids("skills", selection, template, bank)
    assert offered
    for fact_id in offered[:MAX_SECTION_FACT_IDS]:
        assert fact_id in block
    assert 'section="skills"' in block
    # And it never smuggles in the id that was refused.
    assert "skill.rules.sigma" not in block


def test_a_long_section_is_capped_and_says_so(rendered) -> None:
    """A rejection that buries the answer in a wall of ids is no more useful
    than one that omits it."""

    offer, selection, template, bank = rendered
    many = tuple(f"skill.filler.{index}" for index in range(MAX_SECTION_FACT_IDS + 12))

    import jobpilot.tailoring as tailoring

    original = tailoring._offered_fact_ids
    tailoring._offered_fact_ids = lambda *a, **k: many
    try:
        block = _valid_fact_ids_block(
            UnknownFactIdError("skill.nope", section="skills"),
            selection, template, bank,
        )
    finally:
        tailoring._offered_fact_ids = original

    assert block.count("skill.filler.") == MAX_SECTION_FACT_IDS
    assert "and 12 more not shown" in block


def test_a_short_section_is_not_annotated_as_truncated(rendered) -> None:
    offer, selection, template, bank = rendered

    block = _valid_fact_ids_block(
        UnknownFactIdError("certification.nope", section="certifications"),
        selection, template, bank,
    )

    assert "more not shown" not in block


def test_a_non_citation_rejection_gets_no_id_block(rendered) -> None:
    offer, selection, template, bank = rendered

    assert _valid_fact_ids_block(
        TailoringError("page count gate failed"), selection, template, bank
    ) == ""


# ----- the budget -----


def test_an_unknown_id_gets_more_attempts_than_other_rejections() -> None:
    assert _MAX_UNKNOWN_ID_RETRIES == 2
    assert _MAX_ADVISOR_RETRIES == 1
    assert _MAX_UNKNOWN_ID_RETRIES > _MAX_ADVISOR_RETRIES


class _InventsThenRecovers:
    """Cites an id that exists nowhere, for a chosen number of attempts."""

    accepts_correction = True

    def __init__(self, *, failures: int) -> None:
        self.failures = failures
        self.corrections: list[str | None] = []

    @property
    def call_count(self) -> int:
        return len(self.corrections)

    def advise(self, offer, selection, template, *, correction: str | None = None):
        self.corrections.append(correction)
        payload = _payload()
        if self.call_count <= self.failures:
            payload["skill_order"] = ["skill.rules.sigma", *payload["skill_order"]]
        return TailoringPlan.from_mapping(payload, offer=offer, selection=selection)


def test_an_invented_id_recovers_on_the_second_retry(
    db: sqlite3.Connection, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """One retry was not enough for this failure. Two is."""

    application_id = _queued_application(db, suffix="invent-recovers")
    advisor = _InventsThenRecovers(failures=2)

    with caplog.at_level(logging.DEBUG, logger="jobpilot.tailoring"):
        approve_application(
            db, application_id, via="test",
            advisor=advisor, toolchain=_Toolchain(), output_root=tmp_path,
        )

    assert current_status(db, application_id) == "ready"
    assert advisor.call_count == 3  # first attempt plus two retries
    assert advisor.corrections[0] is None
    # Both retries were told which ids are real.
    for correction in advisor.corrections[1:]:
        assert "skill.rules.sigma" in correction
        assert 'section="skills"' in correction


def test_the_extra_attempt_is_not_lent_to_other_rejections(
    db: sqlite3.Connection, tmp_path: Path
) -> None:
    """A non-citation rejection keeps exactly the count it had."""

    from tests.test_tailoring_retry import _RecordingAdvisor

    application_id = _queued_application(db, suffix="other-rejection")
    advisor = _RecordingAdvisor(failures=2)

    with pytest.raises(ApplicationGenerationError):
        approve_application(
            db, application_id, via="test",
            advisor=advisor, toolchain=_Toolchain(), output_root=tmp_path,
        )

    assert advisor.call_count == 2  # first attempt plus one retry, as before
    assert current_status(db, application_id) == "queued"


def test_an_invented_id_that_never_recovers_still_fails(
    db: sqlite3.Connection, tmp_path: Path
) -> None:
    """The extra attempt buys another chance at a real id, not acceptance of a
    fabricated one. The guard is unchanged."""

    application_id = _queued_application(db, suffix="invent-forever")
    advisor = _InventsThenRecovers(failures=99)

    with pytest.raises(ApplicationGenerationError) as excinfo:
        approve_application(
            db, application_id, via="test",
            advisor=advisor, toolchain=_Toolchain(), output_root=tmp_path,
        )

    assert advisor.call_count == 3
    assert "skill.rules.sigma" in str(excinfo.value)
    assert current_status(db, application_id) == "queued"
    # And it is still recorded as a failure, not quietly downgraded.
    assert db.execute(
        "SELECT count(*) AS n FROM events WHERE application_id = ? "
        "AND event = 'generation_failed'",
        (application_id,),
    ).fetchone()["n"] == 1


def test_an_interactive_advisor_is_still_never_retried(
    db: sqlite3.Connection, tmp_path: Path
) -> None:
    from tests.test_tailoring_retry import _InteractiveShapedAdvisor

    application_id = _queued_application(db, suffix="interactive-unknown")
    advisor = _InteractiveShapedAdvisor()

    with pytest.raises(ApplicationGenerationError):
        approve_application(
            db, application_id, via="test",
            advisor=advisor, toolchain=_Toolchain(), output_root=tmp_path,
        )

    assert advisor.call_count == 1
