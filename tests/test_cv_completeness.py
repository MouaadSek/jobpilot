"""Structural completeness floor for AI-generated CVs (Task 22).

Selection freedom covers which bullets represent an employer and how they read,
never whether the employer appears at all.
"""

from __future__ import annotations

import copy
import hashlib
import sqlite3
from pathlib import Path
from typing import Any

import pytest

from jobpilot.apply_flow import ApplicationGenerationError, approve_application
from jobpilot.config import PROJECT_ROOT
from jobpilot.facts import load_fact_bank
from jobpilot.profile import CvProfile, load_cv_profile
from jobpilot.state import current_status
from jobpilot.tailoring import (
    _TECH_ROW_RE,
    TailoringError,
    TailoringPlan,
    _extract_first,
    document_variant_label,
    extract_template_context,
    pick_variant,
    resolve_header_location,
    tailor_cv_html,
)
from tests.test_tailoring import _Toolchain
from tests.test_tailoring_provenance import TEMPLATE_PATH, _offer, _payload

TEMPLATES_DIR = PROJECT_ROOT / "skill" / "assets" / "cv-templates"
GRC_TEMPLATE_PATH = TEMPLATES_DIR / "Mouaad_Sekkouri_-_GRC__Alternance.html"


def _render(payload: dict[str, Any]) -> str:
    offer = _offer()
    selection = pick_variant(offer.description, title=offer.title)
    plan = TailoringPlan.from_mapping(payload, offer=offer, selection=selection)
    return tailor_cv_html(
        TEMPLATE_PATH.read_text(encoding="utf-8"),
        plan,
        selection,
        offer_description=offer.description,
        fact_bank=load_fact_bank(),
        offer=offer,
    )


def _without_employer(experience_id: str) -> dict[str, Any]:
    payload = copy.deepcopy(_payload())
    payload["experience_content"] = [
        entry
        for entry in payload["experience_content"]
        if entry["experience_id"] != experience_id
    ]
    return payload


@pytest.mark.parametrize(
    ("experience_id", "employer"),
    [
        ("experience.baifall_dream", "Baïfall Dream"),
        ("experience.testronic", "Testronic"),
    ],
)
def test_omitting_any_employer_is_rejected(experience_id: str, employer: str) -> None:
    with pytest.raises(TailoringError, match=f"missing employer.*{employer}"):
        _render(_without_employer(experience_id))


def test_employers_out_of_chronological_order_are_rejected() -> None:
    payload = copy.deepcopy(_payload())
    entries = payload["experience_content"]
    entries[0], entries[1] = entries[1], entries[0]

    with pytest.raises(TailoringError, match="reverse-chronological"):
        _render(payload)


def test_recent_employer_below_the_bullet_minimum_is_rejected() -> None:
    payload = copy.deepcopy(_payload())
    payload["experience_content"][0]["bullets"] = payload["experience_content"][0][
        "bullets"
    ][:1]

    with pytest.raises(TailoringError, match="Baïfall Dream needs at least 2"):
        _render(payload)


def test_older_employer_keeps_its_single_bullet_minimum() -> None:
    payload = copy.deepcopy(_payload())
    payload["experience_content"][3]["bullets"] = []

    with pytest.raises(TailoringError, match="bullets.*non-empty"):
        _render(payload)


@pytest.mark.parametrize("count", [2, 4])
def test_project_count_other_than_three_is_rejected(count: int) -> None:
    payload = copy.deepcopy(_payload())
    projects = payload["project_content"]
    if count == 2:
        payload["project_content"] = projects[:2]
    else:
        extra = copy.deepcopy(projects[0])
        extra["project_id"] = "project.soc.alternance.1"
        payload["project_content"] = [*projects, extra]

    with pytest.raises(TailoringError, match="exactly 3 projects|duplicate project"):
        _render(payload)


def test_three_projects_are_accepted() -> None:
    tailored = _render(copy.deepcopy(_payload()))

    assert tailored.count('<div class="project-item">') == 3


def _category_skills(source: str) -> list[tuple[str, list[str]]]:
    """Every shipped category line with its raw, non-deduplicated tool list."""

    rows: list[tuple[str, list[str]]] = []
    for row in _TECH_ROW_RE.findall(source):
        category = _extract_first(
            r'<div class="tech-category">(.*?)</div>', row, "tech category"
        )
        skills = _extract_first(r'<div class="tech-list">(.*?)</div>', row, "tech list")
        rows.append((category, [item.strip() for item in skills.split(",") if item.strip()]))
    return rows


def test_no_shipped_template_repeats_a_tool_across_skill_categories() -> None:
    for template_path in sorted(TEMPLATES_DIR.glob("*.html")):
        seen: dict[str, str] = {}
        for category, skills in _category_skills(
            template_path.read_text(encoding="utf-8")
        ):
            for skill in skills:
                key = skill.casefold()
                assert key not in seen, (
                    f"{template_path.name}: {skill} in both {seen[key]} and {category}"
                )
                seen[key] = category


def test_duplicate_tool_across_categories_is_rejected() -> None:
    source = TEMPLATE_PATH.read_text(encoding="utf-8")
    borrowed = _category_skills(source)[0][1][0]
    # Re-list the first category's tool under the second one.
    head, _, tail = source.partition('<div class="tech-list">')
    second_head, marker, second_tail = tail.partition('<div class="tech-list">')
    duplicated = (
        head
        + '<div class="tech-list">'
        + second_head
        + marker
        + f"{borrowed}, "
        + second_tail
    )
    offer = _offer()
    selection = pick_variant(offer.description, title=offer.title)
    plan = TailoringPlan.from_mapping(
        copy.deepcopy(_payload()),
        offer=offer,
        selection=selection,
    )

    with pytest.raises(TailoringError, match="duplicate tool across skill categories"):
        tailor_cv_html(
            duplicated,
            plan,
            selection,
            offer_description=offer.description,
            fact_bank=load_fact_bank(),
            offer=offer,
        )


def test_header_location_prefers_the_offer_region_then_the_profile() -> None:
    profile = CvProfile(city="Lille", region="Hauts-de-France")

    assert resolve_header_location("Paris", profile) == "Île-de-France"
    assert resolve_header_location("Bordeaux", profile) == "Hauts-de-France"
    assert resolve_header_location("", profile) == "Hauts-de-France"
    assert load_cv_profile().city


def test_model_supplied_location_is_ignored_and_never_a_bare_country() -> None:
    payload = copy.deepcopy(_payload())
    payload["location_region"] = "Provence-Alpes-Côte d'Azur"

    tailored = _render(payload)

    assert "Provence" not in tailored
    # The offer is in Paris, so the renderer injects that region, not the model's.
    assert extract_template_context(tailored).location_region == "Île-de-France"


def _queued_application(
    db: sqlite3.Connection,
    *,
    city: str = "Paris",
    external_id: str = "task-22",
) -> int:
    source_id = db.execute(
        "SELECT id FROM sources WHERE name = 'france_travail'"
    ).fetchone()["id"]
    company_id = db.execute("INSERT INTO companies (name) VALUES ('Acme')").lastrowid
    digest = hashlib.sha256(external_id.encode()).hexdigest()
    offer_id = db.execute(
        "INSERT INTO offers (source_id, company_id, external_id, url, title, "
        "description, contract_type, duration_months, city, content_hash) "
        "VALUES (?, ?, ?, 'https://example.test/task-22', "
        "'Analyste SOC', 'SIEM dès septembre 2026', 'alternance', 12, ?, ?)",
        (source_id, company_id, external_id, city, digest),
    ).lastrowid
    application_id = db.execute(
        "INSERT INTO applications (offer_id, company_id, kind, status) "
        "VALUES (?, ?, 'offer', 'queued')",
        (offer_id, company_id),
    ).lastrowid
    db.commit()
    return int(application_id)


class _IncompleteAdvisor:
    """Drops the current stage, exactly as the observed failure did."""

    def advise(self, offer, selection, template):  # noqa: ANN001, ANN201
        return TailoringPlan.from_mapping(
            _without_employer("experience.baifall_dream"),
            offer=offer,
            selection=selection,
        )


def test_incomplete_cv_rolls_the_application_back_to_queued(
    db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    application_id = _queued_application(db)

    with pytest.raises(ApplicationGenerationError, match="missing employer"):
        approve_application(
            db,
            application_id,
            via="test completeness",
            advisor=_IncompleteAdvisor(),
            toolchain=_Toolchain(),
            output_root=tmp_path,
        )

    assert current_status(db, application_id) == "queued"
    event = db.execute(
        "SELECT event, detail FROM events WHERE application_id = ? ORDER BY id DESC LIMIT 1",
        (application_id,),
    ).fetchone()
    assert event["event"] == "generation_failed"
    assert "missing employer" in event["detail"]


class _CompleteAdvisor:
    def advise(self, offer, selection, template):  # noqa: ANN001, ANN201
        return TailoringPlan.from_mapping(
            copy.deepcopy(_payload()),
            offer=offer,
            selection=selection,
        )


class _RecordingToolchain(_Toolchain):
    def __init__(self) -> None:
        super().__init__()
        self.tracker_fields: dict[str, str] = {}

    def generate_letter_pdf(self, cv_path, body_path, output_path, **kwargs) -> None:  # noqa: ANN001, ANN003
        self.calls.append("letter")
        output_path.write_bytes(b"%PDF-letter")

    def format_tracker_row(self, **fields: str) -> str:
        self.calls.append("tracker")
        self.tracker_fields = dict(fields)
        return "\t".join([""] * 18)


def test_generated_cv_is_complete_and_locally_located(
    db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    application_id = _queued_application(db, city="Bordeaux", external_id="task-22-loc")
    toolchain = _RecordingToolchain()

    outcome = approve_application(
        db,
        application_id,
        via="test completeness",
        advisor=_CompleteAdvisor(),
        toolchain=toolchain,
        output_root=tmp_path,
    )

    assert outcome.generation is not None
    tailored = outcome.generation.cv_html_path.read_text(encoding="utf-8")
    for employer in ("Baïfall Dream", "Concentrix", "Lionbridge", "Testronic"):
        assert employer in tailored
    assert tailored.count('<div class="project-item">') == 3
    assert extract_template_context(tailored).location_region == "Hauts-de-France"
    assert toolchain.tracker_fields["localisation"] == "Hauts-de-France"


def test_tracker_describes_the_generated_document_not_the_routing_guess(
    db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    bank = load_fact_bank()
    grc_html = GRC_TEMPLATE_PATH.read_text(encoding="utf-8")

    # Routing guessed one variant; the document that exists is a GRC CV.
    assert (
        document_variant_label(grc_html, bank, fallback="Chef de Projet IT") == "GRC"
    )

    application_id = _queued_application(db, external_id="task-22-tracker")
    toolchain = _RecordingToolchain()
    outcome = approve_application(
        db,
        application_id,
        via="test tracker",
        advisor=_CompleteAdvisor(),
        toolchain=toolchain,
        output_root=tmp_path,
    )

    assert outcome.generation is not None
    tailored = outcome.generation.cv_html_path.read_text(encoding="utf-8")
    final_projects = extract_template_context(tailored).project_titles
    assert toolchain.tracker_fields["projets"] == ", ".join(final_projects)
    assert toolchain.tracker_fields["cv"] == "CV " + document_variant_label(
        tailored,
        bank,
        fallback="unused",
    )

    detail = db.execute(
        "SELECT detail FROM events WHERE application_id = ? AND event = 'status_change' "
        "ORDER BY id DESC LIMIT 1",
        (application_id,),
    ).fetchone()
    assert "routing_variant" in detail["detail"]
