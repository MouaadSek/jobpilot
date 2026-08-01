"""Task 37 amendment: generated prose, not just fact ids.

Two more failures, same shape as skill.rules.sigma — the model filling a gap
plausibly — but in prose rather than in a citation slot:

* `unsupported number '1 500'`. The bank writes "1 500+"; the letter wrote
  "1 500". Dropping the trailing + makes it a different normalised figure, so
  this was a near-miss rather than a fabrication, and the prompt has to say
  "copy it exactly, including any + or %" and not merely "use ours".
* `unsupported capability 'Cergy'`. Cergy is a commune. The capability tier
  judges every proper noun as a capability claim, which is right for a tool and
  wrong for a place — and no amount of fact-bank curation would ever have fixed
  it, because a bank of the candidate's career cannot contain the employer's
  town.
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

import pytest

from jobpilot.facts import load_fact_bank
from jobpilot.review import invention_report
from jobpilot.tailoring import (
    MAX_SECTION_FACT_IDS,
    SourcedBullet,
    TailoringError,
    UnsupportedNumberError,
    _advisor_prompt,
    _normalized_number,
    _valid_fact_ids_block,
    allowed_numbers,
    extract_template_context,
    letter_scope,
    pick_variant,
    validate_provenance,
    whole_bank_scope,
)
from tests.test_selection_tailoring import TEMPLATE_PATH, _offer


@pytest.fixture
def bank():
    return load_fact_bank()


@pytest.fixture
def rendered():
    offer = _offer()
    selection = pick_variant(offer.description, title=offer.title)
    template = extract_template_context(TEMPLATE_PATH.read_text(encoding="utf-8"))
    return offer, selection, template


# ----- numbers: the closed set -----


def test_the_allowed_numbers_come_from_the_same_text_the_validator_uses(bank) -> None:
    """A prompt that offered a number the validator then refused would be worse
    than offering none."""

    scope = whole_bank_scope(bank)

    for surface in allowed_numbers(bank):
        assert _normalized_number(surface) in scope.numbers


def test_the_bank_writes_the_figure_with_its_plus(bank) -> None:
    """The actual cause: "1 500+" is supported, "1 500" is a different figure."""

    numbers = allowed_numbers(bank)

    assert any(_normalized_number(n) == "1500+" for n in numbers)
    assert not any(_normalized_number(n) == "1500" for n in numbers)


def test_the_prompt_carries_the_closed_number_set(rendered) -> None:
    offer, selection, template = rendered

    prompt = _advisor_prompt(offer, selection, template)
    block = re.search(r"<valid_numbers>\n(.*?)\n</valid_numbers>", prompt, re.DOTALL)

    assert block is not None
    assert set(json.loads(block.group(1))) == set(allowed_numbers(load_fact_bank()))
    assert prompt.index("<valid_numbers>") < prompt.index("Return exactly this shape:")


def test_the_prompt_forbids_introducing_a_figure(rendered) -> None:
    offer, selection, template = rendered

    prompt = _advisor_prompt(offer, selection, template)

    assert "COMPLETE and CLOSED set of figures" in prompt
    assert "figure, percentage, duration, headcount or date" in prompt


def test_the_prompt_says_to_copy_the_figure_exactly(rendered) -> None:
    """Listing the numbers is not enough on its own: the failure was a dropped +."""

    offer, selection, template = rendered

    prompt = _advisor_prompt(offer, selection, template)

    assert "including any trailing + or %" in prompt
    assert '"1 500+" and "1 500" are different figures' in prompt


def test_the_prompt_says_to_write_the_sentence_without_a_number(rendered) -> None:
    offer, selection, template = rendered

    prompt = _advisor_prompt(offer, selection, template)

    assert "write the sentence WITHOUT a number" in prompt
    assert "Do not round, do not approximate" in prompt


# ----- numbers: rejection and recovery -----


def test_an_unsupported_number_raises_the_specific_class(bank) -> None:
    bullet = SourcedBullet(
        text="Traitement de 1 500 incidents.",
        sources=(next(iter(bank.claims)),),
    )

    with pytest.raises(UnsupportedNumberError) as excinfo:
        validate_provenance([bullet], bank, scope=whole_bank_scope(bank))

    assert excinfo.value.number == "1 500"
    assert "unsupported number" in str(excinfo.value)


def test_the_retry_is_handed_the_figures_it_may_use(rendered, bank) -> None:
    offer, selection, template = rendered

    block = _valid_fact_ids_block(
        UnsupportedNumberError("1 500", "unsupported number '1 500' for the whole bank"),
        selection, template, bank,
    )

    assert "<valid_numbers>" in block
    for surface in allowed_numbers(bank)[:MAX_SECTION_FACT_IDS]:
        assert surface in block
    assert "including any trailing + or %" in block
    assert "rewrite the sentence with no number at all" in block


def test_a_plain_rejection_still_gets_no_block(rendered, bank) -> None:
    offer, selection, template = rendered

    assert _valid_fact_ids_block(
        TailoringError("page count gate failed"), selection, template, bank
    ) == ""


# ----- places: the root cause of "unsupported capability 'Cergy'" -----


def test_the_offers_own_town_is_nameable_in_the_letter(bank) -> None:
    """It claims nothing about the candidate; it says where the job is."""

    bullet = SourcedBullet(
        text="Je serais ravi de rejoindre votre équipe à Cergy.",
        sources=(next(iter(bank.claims)),),
    )

    with pytest.raises(TailoringError, match="Cergy"):
        validate_provenance([bullet], bank, scope=whole_bank_scope(bank))

    validate_provenance([bullet], bank, scope=letter_scope(bank, location="Cergy"))


def test_a_postcode_in_the_city_field_never_becomes_a_claimable_quantity(bank) -> None:
    """The narrow limit that keeps this from being a hole."""

    base = whole_bank_scope(bank)
    widened = letter_scope(bank, location="Cergy 95000")

    assert widened.numbers == base.numbers
    bullet = SourcedBullet(
        text="Traitement de 95000 incidents.", sources=(next(iter(bank.claims)),)
    )
    with pytest.raises(UnsupportedNumberError):
        validate_provenance([bullet], bank, scope=widened)


def test_a_capability_the_bank_never_records_is_still_refused(bank) -> None:
    """Widening for places must not widen for tools."""

    bullet = SourcedBullet(
        text="Mission réalisée avec Splunk Enterprise Security.",
        sources=(next(iter(bank.claims)),),
    )

    with pytest.raises(TailoringError, match="unsupported capability"):
        validate_provenance(
            [bullet], bank, scope=letter_scope(bank, location="Cergy")
        )


def test_an_absent_location_leaves_the_scope_exactly_as_it_was(bank) -> None:
    base = whole_bank_scope(bank)

    for location in (None, "", "   ", "95000"):
        widened = letter_scope(bank, location=location)
        assert widened.normalized == base.normalized
        assert widened.numbers == base.numbers


def test_the_domain_phrase_is_not_widened_for_places(bank) -> None:
    """It describes an orientation and has no business naming a city."""

    from jobpilot.tailoring import validate_generated_phrase

    with pytest.raises(TailoringError, match="Cergy"):
        validate_generated_phrase("sécurité opérationnelle à Cergy", bank)


# ----- counting, same report, separate category -----


def test_a_rejected_number_is_counted_separately_from_an_invented_id(
    db: sqlite3.Connection, tmp_path: Path
) -> None:
    from jobpilot.apply_flow import approve_application
    from jobpilot.tailoring import TailoringPlan
    from tests.test_tailoring import _Toolchain
    from tests.test_tailoring_retry import _payload, _queued_application

    class _InventsANumber:
        accepts_correction = True

        def __init__(self) -> None:
            self.corrections: list[str | None] = []

        def advise(self, offer, selection, template, *, correction=None):
            self.corrections.append(correction)
            payload = _payload()
            if len(self.corrections) == 1:
                payload["letter_paragraphs"][0]["text"] = (
                    "Traitement de 1 500 incidents pour votre équipe."
                )
            return TailoringPlan.from_mapping(
                payload, offer=offer, selection=selection
            )

    application_id = _queued_application(db, suffix="number-count")
    approve_application(
        db, application_id, via="test",
        advisor=_InventsANumber(), toolchain=_Toolchain(), output_root=tmp_path,
    )

    report = invention_report(db)

    assert report["numbers"]["rejections"] == 1
    assert report["numbers"]["distinct"] == 1
    assert report["numbers"]["ids"][0][0] == "1 500"
    # And it did not inflate the invented-id count.
    assert report["rejections"] == 0
