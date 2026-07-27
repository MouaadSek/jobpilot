"""A standard's digits name a thing; a metric's digits measure one."""

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

# A real fact with numbers of its own but no standard in it, so an accepted
# designation can only have come from elsewhere in the bank.
CITED = "experience.concentrix.incidents"


@pytest.fixture
def bank():
    return load_fact_bank()


def _check(text: str, bank, *, cited: str = CITED) -> None:
    validate_provenance([SourcedBullet(text=text, sources=(cited,))], bank)


def test_the_cited_fact_really_lacks_the_designations_under_test(bank) -> None:
    """Otherwise these tests would pass through the ordinary metric rule."""

    evidence = bank.claims[CITED].text
    for token in ("ISO", "27001", "NIS2", "AZ-900", "802.1X", "CVSS", "OWASP"):
        assert token not in evidence


# ----- designations are bank-wide vocabulary -----


@pytest.mark.parametrize(
    "text",
    (
        "Cadrage des exigences ISO 27001 sur le périmètre applicatif.",
        "Application des contrôles ISO 27002 sur le périmètre.",
        "Autoévaluation ISO 27001:2022 des mesures en place.",
        "Feuille de route NIS2 pour la mise en conformité.",
        "Exigences RGPD art. 32 appliquées aux flux sensibles.",
        "Certification AZ-900 à l'appui de la trajectoire cloud.",
        "Déploiement du 802.1X sur les accès réseau.",
        "Scoring CVSS v3 des vulnérabilités remontées.",
        "Campagne de tests selon OWASP Top 10.",
        "Cadre ITIL v4 appliqué au suivi des incidents.",
        "Escalade L2/L3 selon la criticité.",
    ),
)
def test_a_designation_in_the_bank_is_accepted_from_any_cited_fact(
    bank,
    text: str,
) -> None:
    _check(text, bank)


@pytest.mark.parametrize(
    "text",
    (
        "Analyse de risques selon ISO 31000.",  # no fact mentions ISO 31000
        "Analyse de risques selon ISO 27005.",  # only 27001/27002 are in the bank
        "Certification AZ-104 obtenue.",  # only AZ-900 is in the bank
        "Durcissement selon le guide ANSSI-BP-028.",  # ANSSI is nowhere in the bank
    ),
)
def test_a_designation_absent_from_the_bank_is_rejected(bank, text: str) -> None:
    """Looking like a standard is not evidence of holding one."""

    with pytest.raises(TailoringError, match="unsupported designation"):
        _check(text, bank)


def test_the_rejection_names_the_designation_not_the_bare_digits(bank) -> None:
    with pytest.raises(TailoringError, match="unsupported designation 'ISO 31000'"):
        _check("Analyse de risques selon ISO 31000.", bank)


def test_acceptance_as_a_designation_is_logged_with_token_and_pattern(
    bank,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Over-permissiveness has to be auditable after the fact."""

    with caplog.at_level("DEBUG", logger="jobpilot.tailoring"):
        _check("Cadrage des exigences ISO 27001 sur le périmètre.", bank)

    logged = "\n".join(record.getMessage() for record in caplog.records)
    assert "accepted designation" in logged
    assert "ISO 27001" in logged
    assert "iso" in logged  # the pattern name that matched
    assert "not as a metric" in logged


# ----- quantitative claims are unchanged -----


@pytest.mark.parametrize(
    "text",
    (
        "Résolution de 15 000 incidents au premier contact.",
        "Taux de 98 % de résolution au premier contact.",
        "5 ans d'expérience sur le périmètre sécurité.",
        "Réduction du délai moyen de résolution de 45 %.",
        "Supervision de 3 VMs de production.",
        "Cadrage mené sur 8 mois.",
    ),
)
def test_a_fabricated_metric_is_still_rejected(bank, text: str) -> None:
    """The anti-fabrication guarantee is not weakened by designation handling."""

    with pytest.raises(TailoringError, match="unsupported number"):
        _check(text, bank)


def test_a_metric_is_rejected_even_when_another_fact_carries_that_number(
    bank,
) -> None:
    """Bank-wide tolerance is for designations only, never for quantities."""

    others = " ".join(
        claim.text for key, claim in bank.claims.items() if key != CITED
    )
    assert "93" in others  # "93 mesures ISO 27001:2022" lives on another fact

    with pytest.raises(TailoringError, match="unsupported number '93'"):
        _check("Autoévaluation de 93 mesures de sécurité.", bank)


def test_the_cited_facts_own_numbers_are_still_accepted(bank) -> None:
    _check(
        "Résolution de 1 500+ incidents avec 85 % de résolution au premier contact.",
        bank,
    )


def test_a_designation_does_not_smuggle_in_a_neighbouring_metric(bank) -> None:
    """Only the designation's own span is exempt from the cited-fact rule."""

    with pytest.raises(TailoringError, match="unsupported number '42'"):
        _check("Mise en conformité ISO 27001 sur 42 applications.", bank)


# ----- the full generation path -----


def test_the_observed_failure_no_longer_fails_a_generation() -> None:
    """'unsupported number 27001' was rejecting real, bank-backed vocabulary."""

    payload = copy.deepcopy(_payload())
    payload["letter_paragraphs"][0]["text"] = (
        "Ma formation couvre les exigences ISO 27001 et la feuille de route NIS2."
    )
    payload["letter_paragraphs"][0]["sources"] = ["education.supinfo.m1_cybersecurity"]
    offer = OfferContext(
        title="Analyste SOC (H/F) - Paris",
        company="Acme",
        description="Analyser les alertes SIEM et répondre aux incidents dès septembre 2026.",
        contract_type="alternance",
        duration_months=12,
        city="Paris",
        source="france_travail",
        url="https://example.test/jobs/26",
    )
    selection = pick_variant(offer.description, title=offer.title)

    tailored = tailor_cv_html(
        TEMPLATE_PATH.read_text(encoding="utf-8"),
        TailoringPlan.from_mapping(payload, offer=offer, selection=selection),
        selection,
        offer_description=offer.description,
        offer=offer,
    )

    assert tailored
