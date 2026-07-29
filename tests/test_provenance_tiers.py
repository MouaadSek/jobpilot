"""Three kinds of token, three different burdens of proof."""

from __future__ import annotations

import copy

import pytest

from jobpilot.facts import load_fact_bank
from jobpilot.tailoring import (
    OfferContext,
    SourcedBullet,
    TailoringError,
    TailoringPlan,
    pick_variant,
    tailor_cv_html,
    validate_provenance,
)
from tests.test_fact_id_resolution import TEMPLATE_PATH
from tests.test_tailoring_provenance import _payload

# A real fact about incident volumes: it names no tool, no standard and no
# category, so anything accepted alongside it was accepted by another tier.
CITED = "experience.concentrix.incidents"


@pytest.fixture
def bank():
    return load_fact_bank()


def _check(text: str, bank, *, cited: str = CITED) -> None:
    validate_provenance([SourcedBullet(text=text, sources=(cited,))], bank)


def test_the_cited_fact_names_none_of_the_tokens_under_test(bank) -> None:
    """Otherwise these tests would pass through the attribution tier."""

    evidence = bank.claims[CITED].text
    for token in ("SIEM", "SOC", "API", "Wazuh", "Terraform", "EDR"):
        assert token not in evidence


# ----- tier 3: vocabulary asserts nothing and is free -----


@pytest.mark.parametrize(
    "text",
    (
        "Supervision SIEM des alertes de sécurité au quotidien.",
        "Analyste SOC en environnement industriel.",
        "Consommation d'une API REST pour l'automatisation.",
        "Qualification des alertes EDR et XDR remontées.",
        "Application des exigences RGPD sur les flux internes.",
        "Contribution au cadrage DevSecOps de la chaîne de production.",
    ),
)
def test_a_category_word_is_allowed_without_any_fact_naming_it(
    bank,
    text: str,
) -> None:
    """The bank names products; no bank-wide rule could ever reach a category."""

    _check(text, bank)


def test_the_observed_failure_no_longer_fails(bank) -> None:
    """'unsupported proper noun siem' was the whole reason for this redesign."""

    _check("Supervision SIEM et réponse aux incidents.", bank)


def test_vocabulary_does_not_license_the_product_behind_the_category(bank) -> None:
    """SIEM is free; the SIEM you claim to have run is not."""

    with pytest.raises(TailoringError, match="unsupported capability 'QRadar'"):
        _check("Supervision du SIEM QRadar au quotidien.", bank)


# ----- tier 2: capability claims are judged against the whole bank -----


@pytest.mark.parametrize(
    "text",
    (
        "Détection d'intrusions avec Wazuh sur le périmètre serveur.",
        "Provisioning d'infrastructure avec Terraform.",
        "Analyse des risques selon la méthode EBIOS RM.",
        "Recherche de vulnérabilités avec Burp Suite.",
        "Corrélation des journaux via Splunk.",
    ),
)
def test_a_tool_in_the_bank_is_allowed_from_any_cited_fact(bank, text: str) -> None:
    _check(text, bank)


@pytest.mark.parametrize(
    "text",
    (
        "Analyse des alertes avec CrowdStrike.",
        "Supervision via Datadog sur l'ensemble du parc.",
        "Orchestration des réponses dans Cortex XSOAR.",
    ),
)
def test_a_tool_absent_from_the_bank_is_refused(bank, text: str) -> None:
    with pytest.raises(TailoringError, match="unsupported capability"):
        _check(text, bank)


def test_the_refusal_names_the_token_as_written(bank) -> None:
    """The reader has to be able to search for it, or add it to the config."""

    with pytest.raises(TailoringError, match="unsupported capability 'CrowdStrike'"):
        _check("Analyse des alertes avec CrowdStrike.", bank)


@pytest.mark.parametrize(
    "text",
    (
        "Cadrage des exigences ISO 27001 sur le périmètre applicatif.",
        "Feuille de route NIS2 pour la mise en conformité.",
        "Certification AZ-900 à l'appui de la trajectoire cloud.",
    ),
)
def test_designations_in_the_bank_are_still_accepted(bank, text: str) -> None:
    """Task 26's handling survives as the digit-shaped corner of tier 2."""

    _check(text, bank)


@pytest.mark.parametrize(
    "text",
    (
        "Analyse de risques selon ISO 31000.",
        "Certification AZ-104 obtenue.",
    ),
)
def test_designations_absent_from_the_bank_are_still_refused(bank, text: str) -> None:
    with pytest.raises(TailoringError, match="unsupported designation"):
        _check(text, bank)


def test_an_unverified_skill_is_refused_even_though_it_is_in_the_bank(bank) -> None:
    """Presence in the bank is necessary for tier 2, never sufficient."""

    import dataclasses

    from jobpilot.facts import SkillFact

    unverified = SkillFact(
        id="skill.qradar",
        name="QRadar",
        verified=False,
        needs_review=True,
    )
    widened = dataclasses.replace(bank, skills=bank.skills + (unverified,))

    with pytest.raises(TailoringError, match="unverified skill"):
        _check("Supervision du SIEM QRadar au quotidien.", widened)


# ----- tier 1: attribution never yields to the tiers below -----


@pytest.mark.parametrize(
    "text",
    (
        "Résolution de 15 000 incidents au premier contact.",
        "Taux de 98 % de résolution au premier contact.",
        "5 ans d'expérience sur le périmètre sécurité.",
    ),
)
def test_a_fabricated_quantity_is_refused(bank, text: str) -> None:
    with pytest.raises(TailoringError, match="unsupported number"):
        _check(text, bank)


def test_a_quantity_carried_by_another_fact_is_still_refused(bank) -> None:
    """Bank-wide tolerance is for capabilities, never for measurements."""

    others = " ".join(claim.text for key, claim in bank.claims.items() if key != CITED)
    assert "93" in others  # "93 mesures ISO 27001:2022" lives on another fact

    with pytest.raises(TailoringError, match="unsupported number '93'"):
        _check("Autoévaluation de 93 mesures de sécurité.", bank)


def test_a_designation_does_not_smuggle_in_a_neighbouring_quantity(bank) -> None:
    """Span-limited exemptions only, exactly as Task 26 established."""

    with pytest.raises(TailoringError, match="unsupported number '42'"):
        _check("Mise en conformité ISO 27001 sur 42 applications.", bank)


def test_a_bullet_may_not_name_an_employer_its_facts_do_not_name(bank) -> None:
    """The anti-misattribution guarantee: whose incidents were they?"""

    with pytest.raises(TailoringError, match="unsupported organisation 'Lionbridge'"):
        _check("Traitement des incidents pour Lionbridge.", bank)


def test_an_organisation_is_not_rescued_by_being_in_the_bank(bank) -> None:
    """Lionbridge is a real employer; that is why naming it here is a lie."""

    corpus = " ".join(claim.text for claim in bank.claims.values())
    assert "Lionbridge" in corpus or any(
        entry.employer == "Lionbridge" for entry in bank.experience
    )

    with pytest.raises(TailoringError, match="unsupported organisation"):
        _check("Traitement des incidents pour Lionbridge.", bank)


def test_a_school_the_cited_fact_does_not_name_is_refused(bank) -> None:
    with pytest.raises(TailoringError, match="unsupported organisation 'Supinfo'"):
        _check("Formation suivie à Supinfo en parallèle du poste.", bank)


def test_the_cited_facts_own_quantities_are_still_accepted(bank) -> None:
    _check(
        "Résolution de 1 500+ incidents avec 85 % de résolution au premier contact.",
        bank,
    )


# ----- the offer is untrusted input, not a source of vocabulary -----


def _offer(description: str) -> OfferContext:
    return OfferContext(
        title="Analyste SOC (H/F) - Paris",
        company="Acme",
        description=description,
        contract_type="alternance",
        duration_months=12,
        city="Paris",
        source="france_travail",
        url="https://example.test/jobs/27",
    )


def _tailor(payload: dict, offer: OfferContext) -> str:
    selection = pick_variant(offer.description, title=offer.title)
    return tailor_cv_html(
        TEMPLATE_PATH.read_text(encoding="utf-8"),
        TailoringPlan.from_mapping(payload, offer=offer, selection=selection),
        selection,
        offer_description=offer.description,
        offer=offer,
    )


def test_a_tool_named_by_the_offer_is_still_refused() -> None:
    """A posting that asks for CrowdStrike does not mean the candidate has it."""

    payload = copy.deepcopy(_payload())
    payload["letter_paragraphs"][0]["text"] = (
        "Mon expérience de supervision couvre CrowdStrike au quotidien."
    )
    payload["letter_paragraphs"][0]["sources"] = ["experience.concentrix.incidents"]
    offer = _offer(
        "Vous supervisez les alertes CrowdStrike du SOC dès septembre 2026. "
        "CrowdStrike est le socle de détection de l'équipe."
    )

    with pytest.raises(TailoringError, match="unsupported capability 'CrowdStrike'"):
        _tailor(payload, offer)


def test_a_category_word_survives_the_full_generation_path() -> None:
    payload = copy.deepcopy(_payload())
    payload["letter_paragraphs"][0]["text"] = (
        "Mon quotidien mêle supervision SIEM, analyse SOC et automatisation via API."
    )
    payload["letter_paragraphs"][0]["sources"] = ["experience.concentrix.incidents"]

    tailored = _tailor(
        payload,
        _offer("Analyser les alertes SIEM et répondre aux incidents dès septembre 2026."),
    )

    assert tailored
