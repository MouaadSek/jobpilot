"""CV variant routing, 5+1 zone tailoring, and generation orchestration."""

from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

import pytest

from jobpilot.state import current_status
from jobpilot.tailoring import (
    TailoringError,
    TailoringPlan,
    extract_template_context,
    generate_application,
    pick_variant,
    tailor_cv_html,
)

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "skill" / "assets" / "cv-templates"


@pytest.mark.parametrize(
    ("missions", "slug", "template_name"),
    [
        (
            "Superviser le SOC, analyser les alertes SIEM et répondre aux incidents.",
            "soc",
            "Mouaad_Sekkouri_-_SOC__Alternance.html",
        ),
        (
            "Réaliser des pentests, de l'exploitation et des exercices red team.",
            "pentest",
            "Mouaad_Sekkouri_-_Pentest__Alternance.html",
        ),
        (
            "Conduire des audits ISO 27001 et des analyses de risques EBIOS RM.",
            "grc",
            "Mouaad_Sekkouri_-_GRC__Alternance.html",
        ),
        (
            "Administrer l'IAM, Active Directory et la gouvernance des identités.",
            "iam",
            "Mouaad_Sekkouri_-_IAM__Alternance.html",
        ),
        (
            "Sécuriser le SDLC avec SAST, DAST et les contrôles OWASP.",
            "appsec",
            "Mouaad_Sekkouri_-_AppSec__Alternance.html",
        ),
        (
            "Durcir Azure et AWS selon les CIS Benchmarks et la sécurité cloud.",
            "cloudsec",
            "Mouaad_Sekkouri_-CloudSec__Alternance.html",
        ),
        (
            "Intégrer la sécurité aux pipelines CI/CD et aux pratiques DevOps.",
            "devsecops",
            "Mouaad_Sekkouri_-_DevSecOps__Alternance.html",
        ),
        (
            "Piloter un projet cyber, coordonner les équipes et tenir le planning.",
            "chef-de-projet-it",
            "Mouaad_Sekkouri_-_Chef_de_Projet_IT__Alternance.html",
        ),
        (
            "Conseiller les métiers dans leur transformation digitale et SI.",
            "consultant-it",
            "Mouaad_Sekkouri_-_Consultant_IT__Alternance.html",
        ),
        (
            "Administrer les infrastructures, systèmes, réseaux et leur sécurité.",
            "infra-cloud",
            "Mouaad_Sekkouri_-_Infrastructure_Cloud__Alternance.html",
        ),
        (
            "Concevoir des réseaux télécoms, du routing BGP et du switching Cisco.",
            "reseaux-telecoms",
            "Mouaad_Sekkouri_-_Reseaux_Telecoms__Alternance.html",
        ),
        (
            "Développer des APIs REST backend en Python et Java.",
            "backend-dev",
            "Mouaad_Sekkouri_-_Backend_Dev__Alternance.html",
        ),
        (
            "Développer une application full-stack avec React côté front et Node côté back.",
            "fullstack-dev",
            "Mouaad_Sekkouri_-_Fullstack_Dev__Alternance.html",
        ),
        (
            "Automatiser le CI/CD, la fiabilité SRE et le monitoring Kubernetes.",
            "devops-sre",
            "Mouaad_Sekkouri_-_DevOps_SRE__Alternance.html",
        ),
        (
            "Assurer le support helpdesk N1/N2 et l'administration système.",
            "support-it",
            "Mouaad_Sekkouri_-_Support_IT_Sysadmin__Alternance.html",
        ),
        (
            "Construire des pipelines ETL, un data warehouse et des rapports BI.",
            "data-bi",
            "Mouaad_Sekkouri_-_Data_Engineering_BI__Alternance.html",
        ),
        (
            "Développer des modèles de machine learning et d'intelligence artificielle.",
            "ia-ml",
            "Mouaad_Sekkouri_-_IA_Machine_Learning__Alternance.html",
        ),
        (
            "Automatiser les tests QA avec Selenium et piloter la recette.",
            "qa-testing",
            "Mouaad_Sekkouri_-_QA_Testing__Alternance.html",
        ),
        (
            "Participer à la sécurité informatique et aux activités SSI générales.",
            "cybersecurite",
            "Mouaad_Sekkouri_-_Cybersecurite__Alternance.html",
        ),
    ],
)
def test_picker_routes_missions_to_all_alternance_variants(
    missions: str,
    slug: str,
    template_name: str,
) -> None:
    selected = pick_variant(missions, title="Alternant ingénieur", contract_type="alternance")

    assert selected.slug == slug
    assert selected.template_name == template_name
    assert selected.adapted_for_stage is False


def test_picker_uses_missions_instead_of_generic_title() -> None:
    selected = pick_variant(
        "Analyser les alertes SIEM, qualifier les incidents et améliorer la détection.",
        title="Ingénieur cybersécurité",
        contract_type="alternance",
    )

    assert selected.slug == "soc"


def test_picker_applies_consultant_title_hard_rule() -> None:
    selected = pick_variant(
        "Développer des APIs Python et des microservices.",
        title="Consultant technique junior",
        contract_type="alternance",
    )

    assert selected.slug == "consultant-it"


@pytest.mark.parametrize(
    ("title", "missions", "expected"),
    [
        (
            "Chef de projet cybersécurité",
            "Coordination des équipes, planning, budget et reporting projet.",
            "chef-de-projet-it",
        ),
        (
            "Ingénieur sécurité",
            "Gouvernance IAM, Active Directory, SSO et gestion des accès.",
            "iam",
        ),
        (
            "DevOps",
            "Durcir les pipelines CI/CD avec SAST et contrôles de sécurité.",
            "devsecops",
        ),
        (
            "Administrateur sécurité",
            "Administration des infrastructures Linux, réseau et virtualisation.",
            "infra-cloud",
        ),
    ],
)
def test_picker_applies_routing_shortcuts(
    title: str,
    missions: str,
    expected: str,
) -> None:
    assert pick_variant(missions, title=title).slug == expected


def test_picker_uses_dedicated_stage_templates_when_available() -> None:
    cyber = pick_variant(
        "Contribuer aux activités générales de sécurité informatique.",
        title="Stagiaire cybersécurité",
        contract_type="stage",
    )
    consultant = pick_variant(
        "Accompagner la transformation du SI.",
        title="Consultant IT stagiaire",
        contract_type="stage",
    )

    assert cyber.slug == "cybersecurite-stage"
    assert cyber.template_name == "Mouaad_Sekkouri_-_Cybersecurite__Stage.html"
    assert cyber.adapted_for_stage is False
    assert consultant.slug == "consultant-it-stage"
    assert consultant.template_name == "Mouaad_Sekkouri_-_Consultant_IT__Stage.html"


def test_picker_marks_stage_without_dedicated_template_for_adaptation() -> None:
    selected = pick_variant(
        "Superviser un SIEM et répondre aux incidents de sécurité.",
        title="Analyste SOC",
        contract_type="stage",
    )

    assert selected.slug == "soc"
    assert selected.template_name == "Mouaad_Sekkouri_-_SOC__Alternance.html"
    assert selected.adapted_for_stage is True


def _plan_for(template_html: str, **overrides: object) -> TailoringPlan:
    context = extract_template_context(template_html)
    values: dict[str, object] = {
        "job_title": "Analyste SOC - Alternance M2 dès Septembre 2026",
        "profile_domain_phrase": "détection proactive des menaces",
        "tech_order": tuple(reversed(context.tech_categories)),
        "tech_keywords": {},
        "project_order": tuple(reversed(context.project_titles)),
        "location_region": "Île-de-France",
        "letter_body_html": (
            "<p>Madame, Monsieur,</p>"
            "<p>Votre mission SOC correspond à mon projet professionnel.</p>"
            "<p>Mon expérience en sécurité réseau répond à vos besoins.</p>"
            "<p>Mes projets de détection apportent une base concrète.</p>"
            "<p>Mon AZ-900 et mon M1 renforcent cette trajectoire.</p>"
            "<p>Je suis disponible pour douze mois dès septembre 2026.</p>"
            "<p>Cordialement,<br/>Mouaad Sekkouri</p>"
        ),
        "rationale": "Priorité donnée à la détection et à la réponse aux incidents.",
    }
    values.update(overrides)
    return TailoringPlan(**values)


def test_tailoring_changes_only_the_allowed_zones_and_swaps_zone_6() -> None:
    template_path = TEMPLATES / "Mouaad_Sekkouri_-_SOC__Alternance.html"
    original = template_path.read_text(encoding="utf-8")
    before = extract_template_context(original)
    plan = _plan_for(original)
    selection = pick_variant("SIEM et réponse aux incidents", title="Analyste SOC")

    tailored = tailor_cv_html(
        original,
        plan,
        selection,
        offer_description="Audit ISO 27001, conformité et appui au RSSI.",
    )
    after = extract_template_context(tailored)

    assert after.job_title == plan.job_title
    assert after.profile_domain_phrase == plan.profile_domain_phrase
    assert after.tech_categories == tuple(reversed(before.tech_categories))
    assert after.project_titles == tuple(reversed(before.project_titles))
    assert after.location_region == "Île-de-France"
    assert "Cadrage réglementaire" in tailored
    assert "95 exigences" in tailored
    assert "Conception et développement de la plateforme" in tailored
    assert "#7bd3e9" in tailored
    assert "C1 Courant" in tailored
    assert "Démarrage anticipé" not in tailored
    assert tailored.count("\n") == original.count("\n")


def test_tailoring_preserves_entity_encoding() -> None:
    template_path = TEMPLATES / "Mouaad_Sekkouri_-_GRC__Alternance.html"
    original = template_path.read_text(encoding="utf-8")
    plan = _plan_for(
        original,
        job_title="Chargé de conformité - Alternance M2 dès Septembre 2026",
        profile_domain_phrase="gouvernance des risques numériques",
        location_region="Île-de-France",
    )
    selection = pick_variant("Audit ISO 27001 et conformité", title="Chargé GRC")

    tailored = tailor_cv_html(
        original,
        plan,
        selection,
        offer_description="Audit ISO 27001 et conformité.",
    )

    assert "Charg&eacute; de conformit&eacute;" in tailored
    assert "gouvernance des risques num&eacute;riques" in tailored
    assert "Île-de-France" not in tailored
    assert "&Icirc;le-de-France" in tailored


@pytest.mark.parametrize(
    "phrase",
    [
        "SOC",
        # 8 words: past the bound even for French.
        "validation et vérification des systèmes embarqués pour l'aéronautique civile",
    ],
)
def test_tailoring_rejects_profile_phrase_outside_three_to_seven_words(phrase: str) -> None:
    original = (TEMPLATES / "Mouaad_Sekkouri_-_SOC__Alternance.html").read_text(encoding="utf-8")
    plan = _plan_for(original, profile_domain_phrase=phrase)
    selection = pick_variant("SIEM", title="Analyste SOC")

    with pytest.raises(TailoringError, match="3 to 7 words"):
        tailor_cv_html(original, plan, selection, offer_description="SIEM")


def test_tailoring_accepts_a_six_word_french_domain_phrase() -> None:
    """The V&V case: a natural French phrase needs more room than five words."""

    original = (TEMPLATES / "Mouaad_Sekkouri_-_SOC__Alternance.html").read_text(encoding="utf-8")
    plan = _plan_for(
        original,
        profile_domain_phrase="validation et vérification des systèmes embarqués",
    )
    selection = pick_variant("SIEM", title="Analyste SOC")

    tailored = tailor_cv_html(original, plan, selection, offer_description="SIEM")

    assert "validation et vérification des systèmes embarqués" in tailored


class _Advisor:
    def advise(self, offer, selection, template):
        return TailoringPlan(
            job_title="Analyste SOC - Alternance M2 dès Septembre 2026",
            profile_domain_phrase="détection proactive des menaces",
            tech_order=template.tech_categories,
            tech_keywords={},
            project_order=template.project_titles,
            location_region="Île-de-France",
            letter_body_html=(
                "<p>Madame, Monsieur,</p>"
                "<p>Je souhaite rejoindre votre équipe SOC.</p>"
                "<p>Mon expérience répond à vos missions.</p>"
                "<p>Mes projets démontrent ma pratique.</p>"
                "<p>Je prépare un M1 et détiens AZ-900.</p>"
                "<p>Je suis disponible dès septembre 2026.</p>"
                "<p>Cordialement,<br/>Mouaad Sekkouri</p>"
            ),
            rationale="Missions centrées sur le SIEM.",
        )


class _Toolchain:
    def __init__(self, *, fail_orphans: bool = False) -> None:
        self.calls: list[str] = []
        self.fail_orphans = fail_orphans

    def validate_cv(
        self,
        tailored_path: Path,
        original_path: Path,
        *,
        compare_original: bool,
    ) -> None:
        self.calls.append("validate")
        assert tailored_path.exists()
        assert original_path.exists()
        assert compare_original is True

    def check_orphan_lines(self, tailored_path: Path, original_path: Path) -> None:
        self.calls.append("orphans")
        assert original_path.exists()
        if self.fail_orphans:
            raise TailoringError("orphan quality gate failed")

    def generate_cv_pdf(self, tailored_path: Path, output_path: Path) -> None:
        self.calls.append("cv")
        output_path.write_bytes(b"%PDF-cv")

    def generate_letter_pdf(
        self,
        cv_path: Path,
        body_path: Path,
        output_path: Path,
        *,
        company: str,
        location: str,
        date: str,
    ) -> None:
        self.calls.append("letter")
        assert company == "Acme"
        assert location == "Paris"
        assert date
        assert body_path.exists()
        output_path.write_bytes(b"%PDF-letter")

    def verify_page_count(self, pdf_path: Path) -> None:
        self.calls.append(f"verify:{pdf_path.stem}")

    def format_tracker_row(self, **fields: str) -> str:
        self.calls.append("tracker")
        assert fields["entreprise"] == "Acme"
        assert fields["cv"] == "CV SOC Analyst"
        return "\t".join([""] * 18)


def _application(db: sqlite3.Connection) -> int:
    source_id = db.execute("SELECT id FROM sources WHERE name='france_travail'").fetchone()["id"]
    company_id = db.execute("INSERT INTO companies (name) VALUES ('Acme')").lastrowid
    description = "Analyser les alertes SIEM et répondre aux incidents."
    digest = hashlib.sha256(b"tailoring-test").hexdigest()
    offer_id = db.execute(
        "INSERT INTO offers (source_id, company_id, external_id, url, title, "
        "description, contract_type, duration_months, city, remote_policy, "
        "content_hash) VALUES (?, ?, 'offer-1', 'https://example.test/job', "
        "'Analyste SOC', ?, 'alternance', 12, 'Paris', 'hybrid', ?)",
        (source_id, company_id, description, digest),
    ).lastrowid
    application_id = db.execute(
        "INSERT INTO applications (offer_id, company_id, kind, status) "
        "VALUES (?, ?, 'offer', 'generating')",
        (offer_id, company_id),
    ).lastrowid
    db.commit()
    return int(application_id)


def test_generation_runs_quality_gates_before_pdfs_and_moves_to_ready(
    db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    application_id = _application(db)
    toolchain = _Toolchain()

    result = generate_application(
        db,
        application_id,
        advisor=_Advisor(),
        toolchain=toolchain,
        output_root=tmp_path,
    )

    assert toolchain.calls == [
        "validate",
        "orphans",
        "cv",
        "verify:cv",
        "letter",
        "verify:motivation_letter",
        "tracker",
    ]
    assert current_status(db, application_id) == "ready"
    assert result.cv_pdf_path.exists()
    assert result.letter_pdf_path.exists()
    assert result.tracker_path.read_text(encoding="utf-8").count("\t") == 17
    stored = db.execute(
        "SELECT cv_pdf_path, letter_pdf_path FROM applications WHERE id=?",
        (application_id,),
    ).fetchone()
    assert stored["cv_pdf_path"] == str(result.cv_pdf_path)
    assert stored["letter_pdf_path"] == str(result.letter_pdf_path)


def test_generation_failure_returns_application_to_queue(
    db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    application_id = _application(db)

    with pytest.raises(TailoringError, match="orphan quality gate failed"):
        generate_application(
            db,
            application_id,
            advisor=_Advisor(),
            toolchain=_Toolchain(fail_orphans=True),
            output_root=tmp_path,
        )

    assert current_status(db, application_id) == "queued"
    application_dir = tmp_path / str(application_id)
    assert application_dir.exists()
    assert list(application_dir.iterdir()) == []
    stored = db.execute(
        "SELECT cv_pdf_path, letter_pdf_path FROM applications WHERE id=?",
        (application_id,),
    ).fetchone()
    assert stored["cv_pdf_path"] is None
    assert stored["letter_pdf_path"] is None
    event = db.execute(
        "SELECT event, detail FROM events WHERE application_id=? ORDER BY id DESC LIMIT 1",
        (application_id,),
    ).fetchone()
    assert event["event"] == "generation_failed"
    assert "orphan quality gate failed" in event["detail"]
