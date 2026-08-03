"""Task 39 item 3: one funnel, three outcomes.

152 raise sites all meant "abort", so a fabricated metric and a short last line
had identical consequences. Seven consecutive generation failures had seven
distinct causes and not one of them caught a fabrication.

The rule these are decided by: a gate may abort only if (a) it guards something
a reader cannot catch, or (b) the document would be unusable and no degradation
exists. Mouaad reads every CV before sending.

Nothing here weakens a provenance check. What changes is only what happens after
a gate fires.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from jobpilot.facts import load_fact_bank
from jobpilot.generation_warnings import warnings_for
from jobpilot.tailoring import (
    SourcedBullet,
    TailoringError,
    Tier,
    UnknownFactIdError,
    _validate_letter_body,
    _validate_selection,
    _validate_skill_categories,
    tier_for,
    validate_provenance,
    whole_bank_scope,
)


@pytest.fixture
def bank():
    return load_fact_bank()


def _raised(call) -> TailoringError:
    with pytest.raises(TailoringError) as excinfo:
        call()
    return excinfo.value


# ----- every gate says what it costs -----


def test_a_provenance_refusal_is_fatal(bank) -> None:
    """The reader cannot check that a claim traces to the bank. Nobody can."""

    bullet = SourcedBullet(
        text="Certifié CISSP depuis 2024.", sources=(next(iter(bank.claims)),)
    )

    exc = _raised(
        lambda: validate_provenance([bullet], bank, scope=whole_bank_scope(bank))
    )

    assert exc.tier is Tier.FATAL
    assert tier_for(exc, position="letter_paragraphs") is Tier.FATAL


def test_a_recoverable_gate_with_no_degradation_escalates_to_fatal(
    db: sqlite3.Connection, tmp_path: Path
) -> None:
    """An invented figure is recoverable — the retry is handed the real ones —
    but nothing structural can be dropped to fix a sentence, so an exhausted
    retry still aborts. Recoverable is not a licence to ship."""

    from jobpilot.apply_flow import ApplicationGenerationError, approve_application
    from jobpilot.state import current_status
    from jobpilot.tailoring import TailoringPlan, UnsupportedNumberError
    from tests.test_tailoring import _Toolchain
    from tests.test_tailoring_retry import _payload, _queued_application

    assert UnsupportedNumberError("1 500", "x").tier is Tier.RECOVERABLE

    class _InventsANumberForever:
        accepts_correction = True

        def advise(self, offer, selection, template, *, correction=None):
            payload = _payload()
            payload["letter_paragraphs"][0]["text"] = (
                "Traitement de 1 500 incidents pour votre équipe."
            )
            return TailoringPlan.from_mapping(
                payload, offer=offer, selection=selection
            )

    application_id = _queued_application(db, suffix="tier-no-degradation")

    with pytest.raises(ApplicationGenerationError, match="1 500"):
        approve_application(
            db,
            application_id,
            via="test",
            advisor=_InventsANumberForever(),
            toolchain=_Toolchain(),
            output_root=tmp_path,
        )

    assert current_status(db, application_id) == "queued"


def test_the_innermost_gate_is_the_one_reported(bank) -> None:
    """validate_provenance delegates; the capability tier is what actually fired."""

    bullet = SourcedBullet(
        text="Mission réalisée avec CrowdStrike Falcon.",
        sources=(next(iter(bank.claims)),),
    )

    exc = _raised(
        lambda: validate_provenance([bullet], bank, scope=whole_bank_scope(bank))
    )

    assert exc.gate == "_reject_unsupported_capabilities"
    assert exc.tier is Tier.FATAL


def test_selection_attribution_is_fatal(bank) -> None:
    """The one gate stopping a CV experience entry at the offer's employer."""

    borrowed = next(iter(bank.experience)).facts[0].id

    exc = _raised(
        lambda: _validate_selection([borrowed], (), bank, entry_id="experience.ikivia")
    )

    assert exc.gate == "_validate_selection"
    assert exc.tier is Tier.FATAL


def test_the_letter_shape_is_recoverable() -> None:
    exc = _raised(lambda: _validate_letter_body("<p>Une seule phrase.</p>"))

    assert exc.gate == "_validate_letter_body"
    assert exc.tier is Tier.RECOVERABLE


def test_a_duplicate_tool_is_advisory() -> None:
    source = (
        '<div class="tech-row"><div class="tech-category">A</div>'
        '<div class="tech-list">Wazuh</div></div>\n'
        '<div class="tech-row"><div class="tech-category">B</div>'
        '<div class="tech-list">Wazuh</div></div>\n'
    )

    exc = _raised(lambda: _validate_skill_categories(source))

    assert exc.tier is Tier.ADVISORY


def test_an_unclassified_error_is_fatal() -> None:
    """The safety property of the whole task: forgetting to classify a gate
    keeps today's behaviour rather than inventing a degradation nobody
    designed."""

    plain = TailoringError("something nobody labelled")

    assert plain.gate == ""
    assert plain.tier is Tier.FATAL
    assert tier_for(plain, position="anywhere") is Tier.FATAL


def test_tier_is_a_property_of_gate_and_position() -> None:
    """The same capability refusal is fatal in the letter and recoverable in the
    profile phrase, because only one of them has somewhere safe to fall back
    to."""

    exc = TailoringError("unsupported capability 'Splunk'")
    exc.gate = "_reject_unsupported_capabilities"

    assert tier_for(exc, position="letter_paragraphs") is Tier.FATAL
    assert tier_for(exc, position="profile_domain_phrase") is Tier.RECOVERABLE


def test_an_unknown_fact_id_is_recoverable_wherever_it_is_raised(bank) -> None:
    """It is droppable because of what it IS, not because of which gate noticed.

    _validate_sourced_plan is fatal and raises this too. The error class keeps
    its own tier, so the citation is still recoverable there.
    """

    from jobpilot.tailoring import TailoringPlan, _validate_sourced_plan, pick_variant
    from tests.test_selection_tailoring import _offer
    from tests.test_tailoring_retry import _payload

    assert UnknownFactIdError("skill.rules.sigma").tier is Tier.RECOVERABLE

    offer = _offer()
    selection = pick_variant(offer.description, title=offer.title)
    payload = _payload()
    payload["skill_order"] = ["skill.rules.sigma", *payload["skill_order"]]
    plan = TailoringPlan.from_mapping(payload, offer=offer, selection=selection)

    exc = _raised(
        lambda: _validate_sourced_plan(plan, bank, selection=selection, offer=offer)
    )

    assert exc.gate == "_validate_sourced_plan"
    assert exc.tier is Tier.RECOVERABLE


# ----- the three outcomes, end to end -----


def test_an_advisory_gate_never_blocks(db: sqlite3.Connection, tmp_path: Path) -> None:
    from tests.test_selection_tailoring import _approve
    from tests.test_tailoring import _Toolchain

    outcome = _approve(db, tmp_path, _Toolchain(fail_orphans=True, orphan_selector="li"))

    assert outcome.generation is not None
    assert [w.gate for w in warnings_for(db, outcome.application_id)] == [
        "check_orphan_lines"
    ]


def test_a_fatal_gate_still_aborts(db: sqlite3.Connection, tmp_path: Path) -> None:
    """Nothing is weakened: a fabrication ends the run exactly as before."""

    from jobpilot.apply_flow import ApplicationGenerationError, approve_application
    from jobpilot.state import current_status
    from jobpilot.tailoring import TailoringPlan
    from tests.test_tailoring import _Toolchain
    from tests.test_tailoring_retry import _payload, _queued_application

    class _Fabricates:
        accepts_correction = True

        def advise(self, offer, selection, template, *, correction=None):
            payload = _payload()
            payload["letter_paragraphs"][0]["text"] = (
                "J'ai utilisé CrowdStrike Falcon pour superviser les alertes."
            )
            return TailoringPlan.from_mapping(
                payload, offer=offer, selection=selection
            )

    application_id = _queued_application(db, suffix="tier-fatal")

    with pytest.raises(ApplicationGenerationError, match="CrowdStrike"):
        approve_application(
            db,
            application_id,
            via="test",
            advisor=_Fabricates(),
            toolchain=_Toolchain(),
            output_root=tmp_path,
        )

    assert current_status(db, application_id) == "queued"


def test_the_profile_fallback_survives_its_own_fallback_failing() -> None:
    """The unwrapped second call that killed the Capgemini generation.

    A degradation whose output is validated by the gate it is escaping from has
    no third option, so the hand-reviewed template phrase is the floor.
    """

    from jobpilot.tailoring import (
        _resolve_profile_phrase,
        extract_template_context,
        pick_variant,
    )
    from tests.test_selection_tailoring import TEMPLATE_PATH, _offer

    offer = _offer()
    selection = pick_variant(offer.description, title=offer.title)
    template = extract_template_context(TEMPLATE_PATH.read_text(encoding="utf-8"))

    phrase, reason = _resolve_profile_phrase(
        "supervision avec Splunk Enterprise Security et CrowdStrike Falcon",
        selection=selection,
        template=template,
        bank=load_fact_bank(),
    )

    assert reason
    assert phrase
