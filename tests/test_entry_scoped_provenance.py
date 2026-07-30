"""A claim is judged by the entry it sits under, not by which fact was cited."""

from __future__ import annotations

import copy

import pytest

from jobpilot.facts import load_fact_bank
from jobpilot.tailoring import (
    OfferContext,
    SourcedBullet,
    TailoringError,
    TailoringPlan,
    entry_scope,
    pick_variant,
    tailor_cv_html,
    validate_plan_provenance,
    validate_provenance,
    whole_bank_scope,
)
from tests.test_fact_id_resolution import TEMPLATE_PATH
from tests.test_tailoring_provenance import _payload

CONCENTRIX = "experience.concentrix"
TESTRONIC = "experience.testronic"

# Concentrix has five facts. Two of them carry « 1 500+ »; the other three do
# not. Under the old rule the same true sentence passed or failed depending on
# which one the model happened to cite.
CONCENTRIX_FACTS = (
    "experience.concentrix.incidents",
    "experience.concentrix.resolution_time",
    "experience.concentrix.incidents.2",
    "experience.concentrix.resolution_time.2",
    "experience.concentrix.resolution_time.3",
)


@pytest.fixture
def bank():
    return load_fact_bank()


def _check(text: str, bank, *, cited: tuple[str, ...], entry: str) -> None:
    validate_provenance(
        [SourcedBullet(text=text, sources=cited)],
        bank,
        scope=entry_scope(bank, entry),
    )


def _facts(bank, entry_id: str):
    """The facts of one entry, whichever section it lives in."""

    for entry in (*bank.experience, *bank.projects):
        if entry.id == entry_id:
            return entry.facts
    raise AssertionError(f"no such entry: {entry_id}")


def _in_bank_corpus(bank, token: str) -> bool:
    return token.casefold() in whole_bank_scope(bank).normalized


# ----- the reproduction this task exists for -----


def test_only_two_of_the_five_concentrix_facts_carry_the_figure(bank) -> None:
    """The premise: citation choice, not truth, decided the old outcome."""

    carriers = [
        fact_id for fact_id in CONCENTRIX_FACTS if "1 500+" in bank.claims[fact_id].text
    ]

    assert len(carriers) == 2
    assert len(CONCENTRIX_FACTS) == 5


@pytest.mark.parametrize("cited", CONCENTRIX_FACTS)
def test_a_true_claim_passes_whichever_concentrix_fact_is_cited(
    bank,
    cited: str,
) -> None:
    """« Triage de 1 500+ incidents » is true of Concentrix. That is the test."""

    _check(
        "Triage de 1 500+ incidents réseau au premier niveau.",
        bank,
        cited=(cited,),
        entry=CONCENTRIX,
    )


def test_a_bullet_may_synthesise_across_the_entrys_facts(bank) -> None:
    """Good bullets draw on more than one fact; that is not a citation error."""

    _check(
        "Triage de 1 500+ incidents avec réduction du délai moyen de 20 %.",
        bank,
        cited=("experience.concentrix.incidents",),
        entry=CONCENTRIX,
    )


# ----- misattribution across entries is still refused -----


def test_another_employers_figure_is_refused_under_this_entry(bank) -> None:
    """Baïfall's 93 measures are not Concentrix's, whatever is cited."""

    assert "93" in whole_bank_scope(bank).numbers  # it is real, just not here

    with pytest.raises(
        TailoringError,
        match="unsupported number '93' for entry 'Concentrix'",
    ):
        _check(
            "Autoévaluation de 93 mesures de sécurité.",
            bank,
            cited=CONCENTRIX_FACTS[:1],
            entry=CONCENTRIX,
        )


def test_a_neighbouring_employers_volume_is_refused(bank) -> None:
    """Lionbridge handled 200 000+ items; Testronic did not."""

    with pytest.raises(
        TailoringError,
        match="unsupported number '200 000\\+' for entry 'Testronic'",
    ):
        _check(
            "Traitement de 200 000+ éléments localisés.",
            bank,
            cited=("experience.testronic.detection.de.90.anomalies.critiques",),
            entry=TESTRONIC,
        )


def test_naming_a_different_employer_inside_an_entry_is_refused(bank) -> None:
    with pytest.raises(
        TailoringError,
        match="unsupported organisation 'Baïfall Dream' for entry 'Concentrix'",
    ):
        _check(
            "Coordination avec les équipes de Baïfall Dream sur les incidents.",
            bank,
            cited=CONCENTRIX_FACTS[:1],
            entry=CONCENTRIX,
        )


@pytest.mark.parametrize(
    ("text", "message"),
    (
        ("Résolution de 15 000 incidents au premier contact.", "unsupported number"),
        ("Taux de 98 % de résolution au premier contact.", "unsupported number"),
        ("Analyse des alertes avec CrowdStrike.", "unsupported capability"),
        ("Analyse de risques selon ISO 31000.", "unsupported designation"),
    ),
)
def test_fabrication_is_refused_in_every_scope(bank, text: str, message: str) -> None:
    """Nothing in the bank supports these, so no scope can accept them."""

    with pytest.raises(TailoringError, match=message):
        _check(text, bank, cited=CONCENTRIX_FACTS[:1], entry=CONCENTRIX)
    with pytest.raises(TailoringError, match=message):
        validate_provenance(
            [SourcedBullet(text=text, sources=CONCENTRIX_FACTS[:1])],
            bank,
            scope=whole_bank_scope(bank),
        )


def test_the_letter_scope_is_genuinely_looser_and_that_is_deliberate(bank) -> None:
    """« 5 ans » is refused under an employer and allowed in a career summary.

    A small figure that exists somewhere in the bank passes the whole-bank
    scope. That is the stated cost of letting the letter summarise a career:
    attribution there means "the bank knows this number", not "this employer
    produced it". Anything absent from the bank is still refused everywhere,
    which is what the test above pins.
    """

    text = "5 ans d'expérience sur le périmètre sécurité."

    with pytest.raises(TailoringError, match="unsupported number '5'"):
        _check(text, bank, cited=CONCENTRIX_FACTS[:1], entry=CONCENTRIX)

    validate_provenance(
        [SourcedBullet(text=text, sources=CONCENTRIX_FACTS[:1])],
        bank,
        scope=whole_bank_scope(bank),
    )


# ----- capability claims are scoped to the entry too, which is a tightening -----


#: Tools the candidate genuinely has, learned on personal projects. Task 27 let
#: them appear anywhere, including under a support desk that never used them.
PROJECT_TOOLS = (
    ("ELK", "project.soc.alternance.1"),
    ("Terraform", "project.devops.sre.alternance.2"),
    ("Kubernetes", "project.devsecops.alternance.2"),
)


@pytest.mark.parametrize(("tool", "owner"), PROJECT_TOOLS)
def test_a_projects_tool_is_refused_under_an_employer_that_never_used_it(
    bank,
    tool: str,
    owner: str,
) -> None:
    """Truthful, and stricter than Task 27: the tool is real, the context is not."""

    assert _in_bank_corpus(bank, tool)  # the candidate does have it

    with pytest.raises(
        TailoringError,
        match=f"unsupported capability '{tool}' for entry 'Concentrix'",
    ):
        _check(
            f"Supervision de l'infrastructure avec {tool}.",
            bank,
            cited=CONCENTRIX_FACTS[:1],
            entry=CONCENTRIX,
        )


@pytest.mark.parametrize(("tool", "owner"), PROJECT_TOOLS)
def test_the_same_tool_passes_under_the_entry_that_owns_it(
    bank,
    tool: str,
    owner: str,
) -> None:
    _check(
        f"Mise en oeuvre de {tool} sur le périmètre du projet.",
        bank,
        cited=(_facts(bank, owner)[0].id,),
        entry=owner,
    )


def test_a_standard_is_refused_under_an_entry_that_does_not_carry_it(bank) -> None:
    """ISO 27001 is in the bank, and not in a network support desk's facts."""

    with pytest.raises(
        TailoringError,
        match="unsupported designation 'ISO 27001' for entry 'Concentrix'",
    ):
        _check(
            "Cadrage des exigences ISO 27001 sur le périmètre.",
            bank,
            cited=CONCENTRIX_FACTS[:1],
            entry=CONCENTRIX,
        )


def test_the_same_standard_passes_under_the_project_that_carries_it(bank) -> None:
    project = "project.grc.alternance.2"
    _check(
        "Cadrage des exigences ISO 27001 sur le périmètre.",
        bank,
        cited=(_facts(bank, project)[0].id,),
        entry=project,
    )


def test_a_tool_the_entry_does_use_is_still_accepted(bank) -> None:
    """Concentrix escalated through Salesforce, so its bullets may say so."""

    _check(
        "Escalade des incidents via Salesforce selon la criticité.",
        bank,
        cited=("experience.concentrix.resolution_time",),
        entry=CONCENTRIX,
    )


def test_category_words_stay_free_under_the_tighter_scope(bank) -> None:
    """Tier 3 is untouched: the tightening is about products, not vocabulary."""

    _check(
        "Supervision SIEM et qualification des alertes SOC via une API REST.",
        bank,
        cited=CONCENTRIX_FACTS[:1],
        entry=CONCENTRIX,
    )


# ----- the entry comes from the plan, and must exist -----


def test_an_unknown_entry_is_an_error_not_a_silent_whole_bank_scope(bank) -> None:
    with pytest.raises(TailoringError, match="unknown entry for provenance scope"):
        entry_scope(bank, "experience.nowhere")


def test_the_scope_of_an_experience_is_named_after_its_employer(bank) -> None:
    scope = entry_scope(bank, CONCENTRIX)

    assert scope.label == "Concentrix"
    assert scope.entry_id == CONCENTRIX
    assert scope.is_entry is True


def test_the_whole_bank_scope_blames_nobody(bank) -> None:
    scope = whole_bank_scope(bank)

    assert scope.is_entry is False
    assert scope.entry_label is None


def test_a_project_scope_covers_its_own_stack_and_facts(bank) -> None:
    scope = entry_scope(bank, "project.soc.alternance.1")

    assert "elk" in scope.normalized
    assert scope.label


def test_dates_are_not_part_of_an_entrys_numbers(bank) -> None:
    """A year is renderer-owned; a scope is about what was done, not when."""

    scope = entry_scope(bank, CONCENTRIX)

    assert "2021" not in scope.numbers
    assert "2023" not in scope.numbers


# ----- sections with no entry are judged against the whole bank -----


def test_a_letter_paragraph_may_summarise_the_whole_career(bank) -> None:
    validate_provenance(
        [
            SourcedBullet(
                text=(
                    "Mon parcours couvre la résolution de 1 500+ incidents et la "
                    "détection de 90+ anomalies critiques."
                ),
                sources=("experience.concentrix.incidents",),
            )
        ],
        bank,
        scope=whole_bank_scope(bank),
    )


def test_a_fabricated_number_in_the_letter_still_fails(bank) -> None:
    with pytest.raises(
        TailoringError,
        match="unsupported number '15 000' for the whole bank",
    ):
        validate_provenance(
            [
                SourcedBullet(
                    text="Mon parcours couvre 15 000 incidents traités.",
                    sources=("experience.concentrix.incidents",),
                )
            ],
            bank,
            scope=whole_bank_scope(bank),
        )


# ----- citations remain required, and must still resolve -----


def test_a_bullet_with_no_citation_is_still_rejected(bank) -> None:
    """Citations stopped being the boundary; they did not stop being required."""

    with pytest.raises(TailoringError, match="must cite at least one fact id"):
        validate_provenance(
            [SourcedBullet(text="Triage de 1 500+ incidents.", sources=())],
            bank,
            scope=entry_scope(bank, CONCENTRIX),
        )


def test_a_citation_that_does_not_resolve_is_still_rejected(bank) -> None:
    with pytest.raises(TailoringError, match="unknown fact id"):
        _check(
            "Triage de 1 500+ incidents.",
            bank,
            cited=("experience.nowhere.at.all",),
            entry=CONCENTRIX,
        )


def test_a_review_pending_citation_is_still_rejected(bank) -> None:
    import dataclasses

    from jobpilot.facts import FactClaim

    claims = dict(bank.claims)
    claims["experience.concentrix.draft"] = FactClaim(
        id="experience.concentrix.draft",
        text="Brouillon non relu",
        section="experience",
        needs_review=True,
    )
    widened = dataclasses.replace(bank, claims=claims)

    with pytest.raises(TailoringError, match="requires review"):
        _check(
            "Triage de 1 500+ incidents.",
            bank=widened,
            cited=("experience.concentrix.draft",),
            entry=CONCENTRIX,
        )


# ----- the plan decides the entry, never the text -----


def _offer() -> OfferContext:
    return OfferContext(
        title="Analyste SOC (H/F) - Paris",
        company="Acme",
        description="Analyser les alertes SIEM et répondre aux incidents dès septembre 2026.",
        contract_type="alternance",
        duration_months=12,
        city="Paris",
        source="france_travail",
        url="https://example.test/jobs/28",
    )


def _plan(payload: dict) -> TailoringPlan:
    offer = _offer()
    return TailoringPlan.from_mapping(
        payload,
        offer=offer,
        selection=pick_variant(offer.description, title=offer.title),
    )


def test_the_plan_path_judges_each_bullet_against_its_own_employer(bank) -> None:
    """Filed under Concentrix, so judged as Concentrix, whatever it cites."""

    payload = copy.deepcopy(_payload())
    payload["experience_content"][1]["bullets"][0]["text"] = (
        "Triage de 1 500+ incidents réseau au premier niveau."
    )
    payload["experience_content"][1]["bullets"][0]["sources"] = [
        "experience.concentrix.resolution_time"  # the fact WITHOUT the figure
    ]

    validate_plan_provenance(_plan(payload), bank)


def test_the_plan_path_refuses_a_figure_borrowed_from_another_employer(bank) -> None:
    payload = copy.deepcopy(_payload())
    payload["experience_content"][1]["bullets"][0]["text"] = (
        "Traitement de 200 000+ éléments avec 85 % de résolution au premier contact."
    )

    with pytest.raises(TailoringError, match="for entry 'Concentrix'"):
        validate_plan_provenance(_plan(payload), bank)


def test_the_committed_reference_payload_still_generates(bank) -> None:
    """Entry scoping must not have broken the known-good plan."""

    offer = _offer()
    selection = pick_variant(offer.description, title=offer.title)

    tailored = tailor_cv_html(
        TEMPLATE_PATH.read_text(encoding="utf-8"),
        _plan(copy.deepcopy(_payload())),
        selection,
        offer_description=offer.description,
        offer=offer,
    )

    assert tailored
