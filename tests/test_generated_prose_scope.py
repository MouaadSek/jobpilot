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

Task 38 widened that second one from the town to the whole parsed offer. Three
further generations died on `unsupported capability 'Ikivia'` / `'AXA'` /
`'Capgemini'`, and « le poste d'Analyste Cybersécurité SecOps » was the next in
line: one class of failure, not four bugs, so the bounded field set is admitted
at once. The prompt rule that told the model not to repeat the company went with
it — naming the employer is what a motivation letter does, the model did it
anyway, and only the scope was ever protecting anything.
"""

from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import replace
from pathlib import Path

import pytest

from jobpilot.facts import load_fact_bank
from jobpilot.review import invention_report
from jobpilot.tailoring import (
    MAX_SECTION_FACT_IDS,
    OfferContext,
    SourcedBullet,
    TailoringError,
    UnsupportedNumberError,
    _advisor_prompt,
    _normalized_number,
    _valid_fact_ids_block,
    _validate_selection,
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


# ----- the offer's own identity: 'Cergy', then 'Ikivia', 'AXA', 'Capgemini' -----


def _posting(
    *,
    company: str = "Ikivia",
    title: str = "Analyste Cybersécurité SecOps",
    city: str = "Cergy",
    company_known: bool = True,
) -> OfferContext:
    """A parsed offer, which is the only thing letter_scope ever admits."""

    return OfferContext(
        title=title,
        company=company,
        description="Rejoignez notre équipe.",
        contract_type="alternance",
        duration_months=12,
        city=city,
        source="france_travail",
        url="https://example.test/jobs/38",
        company_known=company_known,
    )


def _letter(text: str, bank) -> SourcedBullet:
    return SourcedBullet(text=text, sources=(next(iter(bank.claims)),))


@pytest.mark.parametrize(
    "sentence",
    (
        "Je serais ravi de rejoindre votre équipe à Cergy.",
        "Votre annonce Ikivia a retenu toute mon attention.",
        "Le poste d'Analyste Cybersécurité SecOps que vous proposez m'intéresse.",
    ),
)
def test_the_offers_own_identity_is_nameable_in_the_letter(bank, sentence) -> None:
    """Saying who the letter is addressed to claims nothing about the candidate."""

    bullet = _letter(sentence, bank)

    with pytest.raises(TailoringError):
        validate_provenance([bullet], bank, scope=whole_bank_scope(bank))

    validate_provenance([bullet], bank, scope=letter_scope(bank, offer=_posting()))


def test_a_postcode_in_a_parsed_field_never_becomes_a_claimable_quantity(bank) -> None:
    """The first narrow limit that keeps this from being a hole."""

    base = whole_bank_scope(bank)
    widened = letter_scope(bank, offer=_posting(city="Cergy 95000"))

    assert widened.numbers == base.numbers
    with pytest.raises(UnsupportedNumberError):
        validate_provenance(
            [_letter("Traitement de 95000 incidents.", bank)], bank, scope=widened
        )


def test_the_offers_prose_is_not_admitted_only_its_parsed_fields(bank) -> None:
    """The second narrow limit: a posting is untrusted input."""

    offer = _posting()
    offer = replace(
        offer, description="Notre SOC est outillé avec Splunk Enterprise Security."
    )

    with pytest.raises(TailoringError, match="unsupported capability"):
        validate_provenance(
            [_letter("Supervision via Splunk Enterprise Security.", bank)],
            bank,
            scope=letter_scope(bank, offer=offer),
        )


def test_a_capability_the_bank_never_records_is_still_refused(bank) -> None:
    """Widening for the offer's identity must not widen for tools."""

    bullet = _letter("Mission réalisée avec CrowdStrike Falcon.", bank)

    with pytest.raises(TailoringError, match="unsupported capability"):
        validate_provenance(
            [bullet], bank, scope=letter_scope(bank, offer=_posting())
        )


def test_naming_the_employer_is_not_claiming_to_have_worked_there(bank) -> None:
    """The letter may address Ikivia; the CV may not grow an Ikivia experience.

    Attribution on the CV is a different check from the letter's token tiers,
    and it is the one that holds the line here: a selected fact must belong to a
    real entry of the bank, so no widening of the letter's scope can invent an
    employer for the candidate.
    """

    scope = letter_scope(bank, offer=_posting())
    assert "ikivia" in scope.normalized

    borrowed = next(iter(bank.experience)).facts[0].id
    with pytest.raises(TailoringError, match="does not belong to entry"):
        _validate_selection([borrowed], (), bank, entry_id="experience.ikivia")

    with pytest.raises(TailoringError, match="unknown fact id"):
        _validate_selection(
            ["experience.ikivia.supervision"], (), bank, entry_id="experience.ikivia"
        )


def test_an_absent_offer_leaves_the_scope_exactly_as_it_was(bank) -> None:
    base = whole_bank_scope(bank)
    blank = _posting(company="", title="", city="")
    blank = replace(blank, contract_type="")

    for offer in (None, blank, replace(blank, city="95000")):
        widened = letter_scope(bank, offer=offer)
        assert widened.normalized == base.normalized
        assert widened.numbers == base.numbers


def test_an_unnamed_company_admits_nothing(bank) -> None:
    """« votre entreprise » has no name to admit, so the field stays out."""

    widened = letter_scope(
        bank, offer=_posting(company="Ikivia", company_known=False)
    )

    assert "ikivia" not in widened.normalized


def test_the_domain_phrase_is_not_widened_for_the_offer(bank) -> None:
    """It describes an orientation and has no business naming a city or a firm."""

    from jobpilot.tailoring import validate_generated_phrase

    with pytest.raises(TailoringError, match="Cergy"):
        validate_generated_phrase("sécurité opérationnelle à Cergy", bank)

    with pytest.raises(TailoringError, match="Ikivia"):
        validate_generated_phrase("sécurité opérationnelle chez Ikivia", bank)


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
