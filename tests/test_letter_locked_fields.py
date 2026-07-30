"""A letter is prose about a career; a CV is slots the renderer fills."""

from __future__ import annotations

import copy

import pytest

from jobpilot.facts import load_fact_bank
from jobpilot.tailoring import (
    OfferContext,
    TailoringError,
    TailoringPlan,
    pick_variant,
    tailor_cv_html,
)
from tests.test_fact_id_resolution import TEMPLATE_PATH
from tests.test_tailoring_provenance import _payload

EDUCATION = "education.supinfo.m1_cybersecurity"


@pytest.fixture
def bank():
    return load_fact_bank()


def _offer() -> OfferContext:
    return OfferContext(
        title="Analyste SOC (H/F) - Paris",
        company="Acme",
        description="Analyser les alertes SIEM et répondre aux incidents dès septembre 2026.",
        contract_type="alternance",
        duration_months=12,
        city="Paris",
        source="france_travail",
        url="https://example.test/jobs/31",
    )


def _render(payload: dict) -> str:
    offer = _offer()
    selection = pick_variant(offer.description, title=offer.title)
    return tailor_cv_html(
        TEMPLATE_PATH.read_text(encoding="utf-8"),
        TailoringPlan.from_mapping(payload, offer=offer, selection=selection),
        selection,
        offer_description=offer.description,
        offer=offer,
    )


def _letter(text: str, *, sources: tuple[str, ...] = (EDUCATION,)) -> dict:
    payload = copy.deepcopy(_payload())
    payload["letter_paragraphs"][0]["text"] = text
    payload["letter_paragraphs"][0]["sources"] = list(sources)
    return payload


# ----- the sentence this task exists for -----


def test_the_letter_may_describe_the_current_stage_by_name() -> None:
    """The blocked sentence: a letter that cannot say where you work is not a letter."""

    payload = _letter(
        "Mon stage actuel chez Baïfall Dream me permet de cadrer et développer "
        "une plateforme d'e-facturation.",
        sources=("experience.baifall.conception.et.developpement.de.la.plateforme",),
    )

    assert _render(payload)


@pytest.mark.parametrize(
    ("text", "sources"),
    (
        (
            "Mon passage chez Concentrix m'a formé au support réseau et sécurité.",
            ("experience.concentrix.incidents",),
        ),
        (
            "Ma formation à Supinfo Lille structure cette trajectoire.",
            (EDUCATION,),
        ),
        (
            "La certification Microsoft AZ-900 - Azure Fundamentals confirme "
            "mon orientation cloud.",
            ("certification.microsoft.az900",),
        ),
        (
            "Mon Bachelor Génie Informatique m'a donné les bases du développement.",
            ("education.vistula.bachelor_computer_engineering",),
        ),
    ),
)
def test_the_letter_may_name_his_own_employers_schools_and_certifications(
    text: str,
    sources: tuple[str, ...],
) -> None:
    assert _render(_letter(text, sources=sources))


def test_the_letter_may_use_a_date_the_bank_records() -> None:
    payload = _letter(
        "Depuis juillet 2026, je conçois une plateforme de facturation électronique.",
        sources=("experience.baifall.conception.et.developpement.de.la.plateforme",),
    )

    assert _render(payload)


# ----- what the letter still may not do -----


def test_an_employer_the_bank_never_records_is_still_refused() -> None:
    """Naming a real-sounding employer he never had is a fabrication, not prose."""

    payload = _letter("Mon passage chez Capgemini m'a formé à l'audit.")

    with pytest.raises(TailoringError, match="unsupported capability 'Capgemini'"):
        _render(payload)


@pytest.mark.parametrize(
    "field",
    ("email", "phone", "linkedin", "name"),
)
def test_a_contact_field_in_the_letter_body_is_refused(bank, field: str) -> None:
    """The renderer injects the address block; the body repeating it is a bug."""

    value = getattr(bank.locked, field)
    payload = _letter(f"Vous pouvez me joindre : {value}.")

    with pytest.raises(TailoringError, match="contact field the header carries"):
        _render(payload)


def test_a_date_the_bank_never_records_is_refused() -> None:
    payload = _letter("Depuis 2014, je travaille dans la sécurité des systèmes.")

    with pytest.raises(TailoringError, match="unsupported number '2014'"):
        _render(payload)


def test_the_bank_really_lacks_that_year(bank) -> None:
    """Otherwise the test above would prove nothing about scope."""

    from jobpilot.tailoring import whole_bank_scope

    scope = whole_bank_scope(bank)
    assert "2014" not in scope.numbers
    assert "2026" in scope.numbers  # a date the bank does record


# ----- the CV keeps the whole rule -----


@pytest.mark.parametrize(
    "phrase",
    (
        "sécurité chez Concentrix",
        "conformité pour Baïfall Dream",
        "sécurité et Microsoft AZ-900 - Azure Fundamentals",
    ),
)
def test_the_domain_phrase_may_not_name_a_locked_field(phrase: str) -> None:
    payload = copy.deepcopy(_payload())
    payload["profile_domain_phrase"] = phrase

    with pytest.raises(TailoringError, match="locked field"):
        _render(payload)


def test_cv_bullets_are_unaffected_because_they_are_verbatim(bank) -> None:
    """The bank's own text names nothing it should not; selection is the check."""

    tailored = _render(copy.deepcopy(_payload()))

    assert bank.claims["experience.concentrix.incidents"].text in tailored
