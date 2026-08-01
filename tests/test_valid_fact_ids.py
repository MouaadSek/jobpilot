"""Task 37 item 1: tell the advisor the set of ids is closed.

`skill.rules.sigma` exists nowhere in the bank. The offer asked for Sigma
detection rules, the advisor wanted to claim them, and it built a plausible id
by analogy with the real `skill.*` ids it had been shown.

Every real id was already in the prompt — nested under six different keys. What
was missing was any statement that the set is closed, and any instruction about
what to do when the offer asks for something the bank does not have. Omission is
the right answer there, and nothing said so.

The guard that refused the invented id was correct and is untouched.
"""

from __future__ import annotations

import dataclasses
import json
import re
from pathlib import Path

import pytest

from jobpilot.facts import load_fact_bank
from jobpilot.tailoring import (
    _advisor_fact_context,
    _advisor_prompt,
    extract_template_context,
    pick_variant,
    valid_fact_ids,
)
from tests.test_selection_tailoring import TEMPLATE_PATH, _offer


@pytest.fixture
def context():
    offer = _offer()
    selection = pick_variant(offer.description, title=offer.title)
    template = extract_template_context(TEMPLATE_PATH.read_text(encoding="utf-8"))
    return offer, selection, template


@pytest.fixture
def facts(context):
    _, selection, template = context
    return _advisor_fact_context(selection, template, load_fact_bank())


def _nested_ids(facts) -> set[str]:
    """Every id reachable in the nested context, gathered independently."""

    found: set[str] = set()
    for section in ("experience", "projects"):
        for entry in facts[section]:
            found.update(fact["id"] for fact in entry["facts"])
    for section in ("education", "certifications", "languages", "verified_skills"):
        found.update(entry["id"] for entry in facts[section])
    return found


# ----- the array is exactly the context, no more and no less -----


def test_the_flat_array_and_the_nested_context_hold_the_same_ids(facts) -> None:
    """The closed set the prompt declares must be the set the prompt showed."""

    assert set(valid_fact_ids(facts)) == _nested_ids(facts)


def test_the_array_has_no_duplicates(facts) -> None:
    ids = valid_fact_ids(facts)

    assert len(ids) == len(set(ids))
    assert ids  # and it is not vacuously empty


def _context_for(bank):
    offer = _offer()
    selection = pick_variant(offer.description, title=offer.title)
    template = extract_template_context(TEMPLATE_PATH.read_text(encoding="utf-8"))
    return _advisor_fact_context(selection, template, bank)


def test_a_needs_review_fact_never_reaches_the_array() -> None:
    """The real bank happens to hold none, so one is planted: the point is that
    the filter excludes it, not that today's bank is clean."""

    bank = load_fact_bank()
    entry = bank.experience[0]
    marked = dataclasses.replace(entry.facts[0], needs_review=True)
    planted = dataclasses.replace(
        bank,
        experience=(dataclasses.replace(entry, facts=(marked, *entry.facts[1:])),
                    *bank.experience[1:]),
    )

    ids = set(valid_fact_ids(_context_for(planted)))

    assert marked.id not in ids
    assert entry.facts[1].id in ids  # its siblings are unaffected


def test_an_unverified_skill_never_reaches_the_array() -> None:
    bank = load_fact_bank()
    skill = bank.skills[0]
    planted = dataclasses.replace(
        bank,
        skills=(dataclasses.replace(skill, verified=False), *bank.skills[1:]),
    )

    assert skill.id not in set(valid_fact_ids(_context_for(planted)))


def test_the_invented_id_that_started_this_is_not_in_the_bank() -> None:
    """Task 37 must not have quietly added Sigma to make the failure go away."""

    bank = load_fact_bank()

    assert "skill.rules.sigma" not in bank.claims


def test_the_array_survives_a_context_missing_sections() -> None:
    """Defensive: a template with no projects must not raise here."""

    assert valid_fact_ids({}) == ()
    assert valid_fact_ids({"experience": [{"facts": []}]}) == ()


# ----- the prompt states the rule -----


def test_the_prompt_carries_the_flat_array_before_the_output_shape(context) -> None:
    offer, selection, template = context

    prompt = _advisor_prompt(offer, selection, template)

    assert "<valid_fact_ids>" in prompt
    assert prompt.index("<valid_fact_ids>") < prompt.index("Return exactly this shape:")


def test_the_prompt_array_matches_the_context_exactly(context, facts) -> None:
    offer, selection, template = context

    prompt = _advisor_prompt(offer, selection, template)
    block = re.search(r"<valid_fact_ids>\n(.*?)\n</valid_fact_ids>", prompt, re.DOTALL)

    assert block is not None
    assert set(json.loads(block.group(1))) == _nested_ids(facts)


def test_the_prompt_says_the_set_is_closed(context) -> None:
    offer, selection, template = context

    prompt = _advisor_prompt(offer, selection, template)

    assert "COMPLETE and CLOSED set" in prompt
    assert "must appear in it verbatim" in prompt


def test_the_prompt_forbids_building_an_id_by_analogy(context) -> None:
    """The exact mechanism that produced skill.rules.sigma."""

    offer, selection, template = context

    prompt = _advisor_prompt(offer, selection, template)

    assert "derive an id by analogy" in prompt
    assert "however plausible it looks" in prompt


def test_the_prompt_says_omission_is_the_right_answer(context) -> None:
    """The clause that was missing entirely: the model was trying to be helpful
    about Sigma and had never been told that leaving it out is correct."""

    offer, selection, template = context

    prompt = _advisor_prompt(offer, selection, template)

    assert "OMIT it" in prompt
    assert "Omission is the correct answer, not approximation" in prompt


def test_the_prompt_still_refuses_paraphrase_and_selection_rules(context) -> None:
    """Item 1 adds rules; it must not have displaced the existing ones."""

    offer, selection, template = context

    prompt = _advisor_prompt(offer, selection, template)

    assert "You SELECT the CV's experience bullets" in prompt
    assert "paraphrase, shorten, translate, or re-punctuate" in prompt
    assert "Copy every fact id verbatim" in prompt


def test_every_id_in_the_prompt_array_is_a_real_bank_claim(context) -> None:
    offer, selection, template = context
    bank = load_fact_bank()

    prompt = _advisor_prompt(offer, selection, template)
    block = re.search(r"<valid_fact_ids>\n(.*?)\n</valid_fact_ids>", prompt, re.DOTALL)
    ids = json.loads(block.group(1))

    assert ids
    for fact_id in ids:
        assert fact_id in bank.claims, fact_id


def test_the_fact_bank_file_is_untouched_by_this_task() -> None:
    """Out of scope: adding Sigma, or any skill, is a deliberate edit Mouaad
    makes, not something a task infers from a job posting."""

    bank_path = Path(__file__).resolve().parents[1] / "config" / "fact_bank.yaml"
    text = bank_path.read_text(encoding="utf-8")

    assert "sigma" not in text.casefold() or "règles sigma" in text.casefold()
