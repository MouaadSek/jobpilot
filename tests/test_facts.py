"""Fact-bank loading, review CLI, and deterministic role-title cleaning."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from jobpilot.cli import app
from jobpilot.facts import build_cv_title, load_fact_bank, normalise_role_title

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "skill" / "assets" / "cv-templates"


def test_fact_bank_covers_every_cv_template_and_has_unique_claim_ids() -> None:
    bank = load_fact_bank()
    template_names = {path.name for path in TEMPLATES.glob("*.html")}

    assert set(bank.source_templates) == template_names
    assert set(bank.source_documents) == {"skill/SKILL.md", "skill/assets/stage-baifall-dream.md"}
    assert len(bank.experience) == 4
    assert len(bank.projects) >= 21
    assert len(bank.education) == 2
    assert len(bank.certifications) == 1
    assert len(bank.languages) == 4
    assert bank.skills
    assert len(bank.claims) == len(set(bank.claims))


def test_fact_bank_locks_identity_and_all_model_immutable_values() -> None:
    bank = load_fact_bank()

    assert bank.locked.name == "Mouaad Sekkouri"
    assert bank.locked.email == "mouaadsekkourii@gmail.com"
    assert bank.locked.phone == "+33 7 51 13 54 25"
    assert bank.locked.linkedin == "linkedin.com/in/sekkouri"
    assert set(bank.locked.employer_names) == {
        "Baïfall Dream",
        "Concentrix",
        "Lionbridge",
        "Testronic",
    }
    assert bank.locked.certification_names == ("Microsoft AZ-900 - Azure Fundamentals",)
    assert all(entry.dates in bank.locked.dates for entry in bank.experience)
    assert all(entry.diploma in bank.locked.diplomas for entry in bank.education)


def test_every_skill_is_explicitly_verified_or_unverified() -> None:
    bank = load_fact_bank()

    assert {skill.verified for skill in bank.skills} <= {True, False}
    assert all(skill.needs_review for skill in bank.skills if not skill.verified)


def test_facts_cli_prints_reviewable_sections() -> None:
    result = CliRunner().invoke(app, ["facts"])

    assert result.exit_code == 0
    assert "EXPÉRIENCE" in result.stdout
    assert "PROJETS" in result.stdout
    assert "FORMATION" in result.stdout
    assert "CERTIFICATIONS" in result.stdout
    assert "LANGUES" in result.stdout
    assert "COMPÉTENCES" in result.stdout
    assert "VERROUILLÉ" in result.stdout
    assert "experience.concentrix.incidents" in result.stdout


@pytest.mark.parametrize(
    ("raw_title", "expected"),
    [
        ("Expert / Experte en cybersécurité (H/F)", "Expert en cybersécurité"),
        ("Ingénieur(e) Sécurité Cloud F/H", "Ingénieur Sécurité Cloud"),
        ("Analyste SOC (H/F/X) - Paris (75)", "Analyste SOC"),
        ("Alternance - Consultant Cybersécurité H/F - Lille", "Consultant Cybersécurité"),
        ("Stage Pentest (M/F) | Puteaux (92)", "Pentest"),
        ("Développeur·se Backend Python - Réf. DEV-2026-42", "Développeur Backend Python"),
        (
            "Administrateur/Administratrice Systèmes et Réseaux",
            "Administrateur Systèmes et Réseaux",
        ),
        ("[REF 38192] Ingénieur DevSecOps - Île-de-France", "Ingénieur DevSecOps"),
        ("URGENT : Analyste Cybersécurité - 59", "Analyste Cybersécurité"),
        ("Nouveau ! Chef de Projet IT (F/H) à Roubaix", "Chef de Projet IT"),
        ("APPRENTISSAGE – Data Engineer H/F – Courbevoie", "Data Engineer"),
        ("Stagiaire QA / Testeur logiciel (H/F) - Lyon 69", "QA / Testeur logiciel"),
        ("Rejoignez-nous : Consultant IAM (H/F/NB)", "Consultant IAM"),
        ("Offre n° 2026-001 - Technicien Support N1/N2 - Paris", "Technicien Support N1/N2"),
        ("Cloud Security Engineer (m/f/d) - Remote France", "Cloud Security Engineer"),
        ("Alternant(e) Infrastructure & Cloud - Département 92", "Infrastructure & Cloud"),
        ("Analyste SOC H/F @ ACME - Saint-Denis", "Analyste SOC"),
        ("CDI - Responsable Sécurité SI (F/H) – 75008 Paris", "Responsable Sécurité SI"),
    ],
)
def test_normalise_role_title_handles_real_world_shapes(
    raw_title: str,
    expected: str,
) -> None:
    assert normalise_role_title(raw_title) == expected


def test_build_cv_title_uses_clean_role_and_contract_specific_suffix() -> None:
    assert (
        build_cv_title(
            "Alternance - Ingénieur(e) cybersécurité (H/F) - Paris",
            contract_type="alternance",
            start_date="septembre 2026",
        )
        == "Ingénieur cybersécurité - Alternance M2 dès septembre 2026"
    )
    assert (
        build_cv_title(
            "Stage Analyste SOC F/H - Lille",
            contract_type="stage",
            duration_months=6,
            start_date="janvier 2027",
        )
        == "Analyste SOC - Stage 6 mois dès janvier 2027"
    )
