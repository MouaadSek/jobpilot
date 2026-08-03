"""Task 40 amendment: bullets had a floor and no ceiling.

_validate_experience_completeness checked len(fact_ids) < minimum and nothing
checked the other direction, so a generation selected 9 of Baïfall's 11 facts
into a block every template lays out with 2 or 3 rows. That is not a cosmetic
overflow: it crowds the other three employers out and a CV showing one entry's
whole fact bank is not a tailored CV. The page count caught it only sometimes,
which is why it looked intermittent.

The ceiling is the template's own row count, not a constant — the Backend and
Fullstack templates deliberately give the current employer 2.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from jobpilot.facts import load_fact_bank
from jobpilot.generation_warnings import GenerationWarning
from jobpilot.tailoring import (
    _OLDER_EMPLOYER_MIN_BULLETS,
    _RECENT_EMPLOYER_COUNT,
    _RECENT_EMPLOYER_MIN_BULLETS,
    TailoringError,
    TailoringPlan,
    _cap_experience_selection,
    _experience_bullet_capacity,
    _normalize,
    _reverse_chronological_experiences,
    _validate_experience_completeness,
    extract_template_context,
    pick_variant,
    tailor_cv_html,
)
from tests.test_selection_tailoring import _offer
from tests.test_tailoring_retry import _payload

TEMPLATES = Path(__file__).resolve().parents[1] / "skill" / "assets" / "cv-templates"
SOC = TEMPLATES / "Mouaad_Sekkouri_-_SOC__Alternance.html"
#: Deliberately two rows for the current employer, per the amendment.
TWO_ROW = TEMPLATES / "Mouaad_Sekkouri_-_Backend_Dev__Alternance.html"


@pytest.fixture
def bank():
    return load_fact_bank()


def _plan(bank, *, facts_for_first: int) -> TailoringPlan:
    """A plan whose most recent employer selects `facts_for_first` of its facts."""

    offer = _offer()
    selection = pick_variant(offer.description, title=offer.title)
    payload = _payload()
    first = _reverse_chronological_experiences(bank)[0]
    available = [fact.id for fact in first.facts][:facts_for_first]
    assert len(available) == facts_for_first, "fact bank has fewer facts than asked"
    for chosen in payload["experience_content"]:
        if chosen["experience_id"] == first.id:
            chosen["fact_ids"] = available
    return TailoringPlan.from_mapping(payload, offer=offer, selection=selection)


def test_the_capacity_comes_from_the_template_not_a_constant() -> None:
    soc = _experience_bullet_capacity(SOC.read_text(encoding="utf-8"))
    two_row = _experience_bullet_capacity(TWO_ROW.read_text(encoding="utf-8"))

    assert soc[_normalize("Baïfall Dream")] == 3
    assert two_row[_normalize("Baïfall Dream")] == 2
    assert soc[_normalize("Lionbridge")] == 1


def test_every_template_gives_every_employer_room_for_its_floor(bank) -> None:
    """If a template ever dropped below the floor, truncating would be illegal."""

    order = [entry.id for entry in _reverse_chronological_experiences(bank)]
    employer_of = {entry.id: entry.employer for entry in bank.experience}

    for path in sorted(TEMPLATES.glob("*.html")):
        capacity = _experience_bullet_capacity(path.read_text(encoding="utf-8"))
        for position, entry_id in enumerate(order):
            rows = capacity.get(_normalize(employer_of[entry_id]))
            if rows is None:
                continue
            floor = (
                _RECENT_EMPLOYER_MIN_BULLETS
                if position < _RECENT_EMPLOYER_COUNT
                else _OLDER_EMPLOYER_MIN_BULLETS
            )
            assert rows >= floor, f"{path.name}: {employer_of[entry_id]}"


def test_over_selection_is_truncated_with_a_warning(bank) -> None:
    """The reproduction: nine facts into three rows."""

    plan = _plan(bank, facts_for_first=9)
    warnings: list[GenerationWarning] = []

    capped = _cap_experience_selection(
        plan, SOC.read_text(encoding="utf-8"), bank=bank, warnings=warnings
    )

    first = capped.experience_content[0]
    assert len(first.fact_ids) == 3
    # Kept in the advisor's own order, because the plan carries no ranking.
    assert first.fact_ids == plan.experience_content[0].fact_ids[:3]
    assert [w.gate for w in warnings] == ["_cap_experience_selection"]
    assert "9 faits" in warnings[0].message
    assert "classement" in warnings[0].degraded


def test_a_two_row_template_caps_at_two(bank) -> None:
    plan = _plan(bank, facts_for_first=9)

    capped = _cap_experience_selection(
        plan, TWO_ROW.read_text(encoding="utf-8"), bank=bank, warnings=[]
    )

    assert len(capped.experience_content[0].fact_ids) == 2


def test_a_selection_within_the_ceiling_is_untouched(bank) -> None:
    plan = _plan(bank, facts_for_first=3)

    capped = _cap_experience_selection(
        plan, SOC.read_text(encoding="utf-8"), bank=bank, warnings=[]
    )

    assert capped is plan


def test_under_selection_still_fails_the_floor(bank) -> None:
    """The ceiling does not soften the other direction."""

    plan = _plan(bank, facts_for_first=1)

    with pytest.raises(TailoringError, match="needs at least"):
        _validate_experience_completeness(plan, bank)


def test_truncation_never_takes_an_entry_below_its_floor(bank) -> None:
    """Floor beats ceiling; a template row count under it cannot make a bad CV."""

    plan = _plan(bank, facts_for_first=9)
    starved = re.sub(r"<li>.*?</li>", "", SOC.read_text(encoding="utf-8"), count=99,
                     flags=re.DOTALL)

    capped = _cap_experience_selection(plan, starved, bank=bank, warnings=[])

    _validate_experience_completeness(capped, bank)


def test_the_rendered_cv_carries_only_the_capped_bullets(bank) -> None:
    """End to end: the renderer inserts what survived, not what was asked for."""

    offer = _offer()
    selection = pick_variant(offer.description, title=offer.title)
    plan = _plan(bank, facts_for_first=9)
    warnings: list[GenerationWarning] = []

    tailored = tailor_cv_html(
        SOC.read_text(encoding="utf-8"),
        plan,
        selection,
        offer_description=offer.description,
        fact_bank=bank,
        offer=offer,
        warnings=warnings,
    )

    block = re.search(
        r'<div class="experience-item">.*?</ul>', tailored, re.DOTALL
    )
    assert block is not None
    assert len(re.findall(r"<li>", block.group(0))) == 3
    assert [w.gate for w in warnings] == ["_cap_experience_selection"]


def test_the_prompt_states_the_ceiling() -> None:
    """The model had never been told there was one."""

    from jobpilot.tailoring import _advisor_prompt

    offer = _offer()
    selection = pick_variant(offer.description, title=offer.title)
    template = extract_template_context(SOC.read_text(encoding="utf-8"))

    prompt = _advisor_prompt(offer, selection, template)

    assert "Baïfall Dream = 3" in prompt
    assert "Lionbridge = 1" in prompt
    assert "Each employer also has a MAXIMUM" in prompt
    assert prompt.index("MAXIMUM") > prompt.index("at least 2 selected facts")
