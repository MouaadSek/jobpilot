"""Letter quality: French elision and the 'Entreprise' placeholder rejection."""

from __future__ import annotations

import pytest

from jobpilot.tailoring import (
    OfferContext,
    TailoringError,
    _default_letter,
    _validate_letter_body,
    french_de_elision,
)


@pytest.mark.parametrize(
    ("noun", "expected"),
    [
        ("Expert", "d'Expert"),
        ("Ingénieur", "d'Ingénieur"),
        ("Analyste", "d'Analyste"),
        ("Administrateur", "d'Administrateur"),
        ("École", "d'École"),  # accented capital vowel elides
        ("Étudiant", "d'Étudiant"),
        ("Hôte", "d'Hôte"),  # mute h elides
        ("Consultant", "de Consultant"),  # consonant keeps « de »
        ("Développeur", "de Développeur"),
        ("Technicien", "de Technicien"),
    ],
)
def test_french_de_elision(noun: str, expected: str) -> None:
    assert french_de_elision(noun) == expected


def test_french_de_elision_handles_leading_whitespace_and_empty() -> None:
    assert french_de_elision("  Ingénieur") == "d'Ingénieur"
    assert french_de_elision("") == "de"


def _letter(second_paragraph: str) -> str:
    return (
        "<p>Madame, Monsieur,</p>"
        f"<p>{second_paragraph}</p>"
        "<p>Mes deux ans en sécurité répondent à vos besoins.</p>"
        "<p>Mes projets démontrent une pratique concrète.</p>"
        "<p>Mon AZ-900 et mon M1 renforcent cette trajectoire.</p>"
        "<p>Je suis disponible dès septembre 2026.</p>"
        "<p>Je serais heureux d'échanger sur ma contribution.</p>"
        "<p>Cordialement,<br/>Mouaad Sekkouri</p>"
    )


def test_validator_rejects_entreprise_placeholder() -> None:
    body = _letter("Je souhaite rejoindre Entreprise pour ce poste.")
    with pytest.raises(TailoringError, match="Entreprise"):
        _validate_letter_body(body)


def test_validator_accepts_votre_entreprise_lowercase() -> None:
    body = _letter("Je souhaite rejoindre votre entreprise pour ce poste.")
    _validate_letter_body(body)  # must not raise


def test_validator_rejects_missing_elision_before_vowel() -> None:
    body = _letter("Je vise le poste de Ingénieur sécurité chez vous.")
    with pytest.raises(TailoringError, match="elide"):
        _validate_letter_body(body)


def test_validator_accepts_correct_elision() -> None:
    body = _letter("Je vise le poste d'Ingénieur sécurité chez vous.")
    _validate_letter_body(body)  # must not raise


def test_validator_accepts_de_before_consonant() -> None:
    body = _letter("Je vise le poste de Consultant sécurité chez vous.")
    _validate_letter_body(body)  # must not raise


def _offer(*, company: str, company_known: bool, title: str) -> OfferContext:
    return OfferContext(
        title=title,
        company=company,
        company_known=company_known,
        description="",
        contract_type="alternance",
        duration_months=12,
        city="Lille",
        url="https://example.test/1",
        source="france_travail",
    )


def test_default_letter_uses_votre_entreprise_when_company_unknown() -> None:
    body = _default_letter(
        _offer(company="votre entreprise", company_known=False, title="Analyste SOC")
    )
    assert "votre entreprise" in body
    _validate_letter_body(body)  # placeholder rule must pass


def test_default_letter_elides_poste_before_vowel() -> None:
    body = _default_letter(
        _offer(company="Acme", company_known=True, title="Ingénieur sécurité")
    )
    assert "le poste d'Ingénieur sécurité" in body
    _validate_letter_body(body)
