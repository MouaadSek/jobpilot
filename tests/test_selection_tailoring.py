"""The advisor selects; the renderer inserts the bank's wording unchanged."""

from __future__ import annotations

import copy
import json
import re
import sqlite3
from pathlib import Path

import pytest

from jobpilot.apply_flow import ApplicationGenerationError, approve_application
from jobpilot.facts import load_fact_bank
from jobpilot.state import current_status
from jobpilot.tailoring import (
    OfferContext,
    TailoringError,
    TailoringPlan,
    extract_template_context,
    pick_variant,
    tailor_cv_html,
)
from tests.test_fact_id_resolution import TEMPLATE_PATH
from tests.test_tailoring_provenance import _payload, _queued_application

CONCENTRIX = "experience.concentrix"


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
        url="https://example.test/jobs/30",
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


def _bullets(tailored: str, employer: str) -> list[str]:
    """The rendered <li> texts under one employer, decoded back to plain text."""

    block = re.search(
        rf'<span class="company-name">{re.escape(employer)}</span>.*?</ul>',
        tailored,
        re.DOTALL,
    )
    assert block is not None, f"{employer} block not rendered"
    import html as html_module

    return [
        html_module.unescape(re.sub(r"<[^>]+>", "", raw)).strip()
        for raw in re.findall(r"<li>(.*?)</li>", block.group(0), re.DOTALL)
    ]


# ----- 30.1 the CV's text is the bank's text -----


def test_a_rendered_bullet_is_byte_identical_to_its_fact(bank) -> None:
    """No paraphrase, no reflow: the hand-tuned line fit survives generation."""

    payload = copy.deepcopy(_payload())
    selected = [
        "experience.concentrix.incidents",
        "experience.concentrix.resolution_time.2",
    ]
    payload["experience_content"][1]["fact_ids"] = selected

    rendered = _bullets(_render(payload), "Concentrix")

    assert rendered == [bank.claims[fact_id].text for fact_id in selected]


def test_the_selection_order_is_the_rendered_order(bank) -> None:
    payload = copy.deepcopy(_payload())
    reversed_selection = [
        "experience.concentrix.resolution_time",
        "experience.concentrix.incidents",
    ]
    payload["experience_content"][1]["fact_ids"] = reversed_selection

    rendered = _bullets(_render(payload), "Concentrix")

    assert rendered == [bank.claims[fact_id].text for fact_id in reversed_selection]


def test_a_project_description_is_its_facts_text(bank) -> None:
    tailored = _render(copy.deepcopy(_payload()))

    for project in _payload()["project_content"]:
        assert bank.claims[project["fact_id"]].text in tailored


def test_the_baifall_variant_bullets_are_selectable_verbatim(bank) -> None:
    """The pre-written variants from the skill asset, used as the asset intends."""

    variants = (
        "experience.baifall.cadrage.reglementaire.immatriculation.dgfip.certification",
        "experience.baifall.specification.d.une.architecture.secure.by.design",
        "experience.baifall.analyse.des.exigences.d.hebergement.localisation.ue",
    )
    for variant in variants:
        payload = copy.deepcopy(_payload())
        payload["experience_content"][0]["fact_ids"] = [
            "experience.baifall.redaction.du.cahier.des.charges.d.une",
            variant,
        ]

        assert bank.claims[variant].text in _bullets(_render(payload), "Baïfall Dream")


def test_the_advisor_cannot_send_bullet_text_at_all(bank) -> None:
    """The contract has no field for prose, so a writing advisor fails loudly."""

    payload = copy.deepcopy(_payload())
    payload["experience_content"][1]["bullets"] = [
        {"text": "Du texte inventé.", "sources": ["experience.concentrix.incidents"]}
    ]

    with pytest.raises(TailoringError, match="unknown fields.*bullets"):
        _render(payload)


def test_a_justification_is_accepted_and_never_rendered(bank) -> None:
    payload = copy.deepcopy(_payload())
    payload["experience_content"][1]["justification"] = "Choix ciblé sur le SOC."

    tailored = _render(payload)

    assert "Choix ciblé sur le SOC" not in tailored


# ----- 30.1 the completeness floor now applies to selections -----


def test_every_employer_is_still_mandatory() -> None:
    payload = copy.deepcopy(_payload())
    del payload["experience_content"][2]

    with pytest.raises(TailoringError, match="missing employer.*Lionbridge"):
        _render(payload)


def test_reverse_chronological_order_is_still_enforced() -> None:
    payload = copy.deepcopy(_payload())
    payload["experience_content"][1], payload["experience_content"][2] = (
        payload["experience_content"][2],
        payload["experience_content"][1],
    )

    with pytest.raises(TailoringError, match="reverse-chronological"):
        _render(payload)


def test_a_recent_employer_needs_two_selected_facts() -> None:
    payload = copy.deepcopy(_payload())
    payload["experience_content"][1]["fact_ids"] = ["experience.concentrix.incidents"]

    with pytest.raises(TailoringError, match="Concentrix needs at least 2"):
        _render(payload)


def _project(index: int) -> dict[str, str]:
    return {
        "project_id": f"project.soc.alternance.{index}",
        "fact_id": f"project.soc.alternance.{index}.outcome",
    }


@pytest.mark.parametrize("count", (2, 4))
def test_exactly_three_projects_are_still_required(count: int) -> None:
    payload = copy.deepcopy(_payload())
    payload["project_content"] = [_project(index) for index in (1, 2, 3)][:count]
    if count == 4:
        # A fourth real project, so the count is what fails, not a duplicate.
        payload["project_content"] = [_project(index) for index in (1, 2, 3)] + [
            {
                "project_id": "project.cybersecurite.alternance.1",
                "fact_id": "project.cybersecurite.alternance.1.outcome",
            }
        ]

    with pytest.raises(TailoringError, match="exactly 3 projects|do not belong"):
        _render(payload)


def test_selecting_the_same_fact_twice_is_rejected() -> None:
    payload = copy.deepcopy(_payload())
    payload["experience_content"][1]["fact_ids"] = [
        "experience.concentrix.incidents",
        "experience.concentrix.incidents",
    ]

    with pytest.raises(TailoringError, match="selects the same fact twice"):
        _render(payload)


# ----- 30.1 a selection must belong to its entry -----


def test_a_fact_from_another_employer_is_rejected() -> None:
    payload = copy.deepcopy(_payload())
    payload["experience_content"][1]["fact_ids"] = [
        "experience.concentrix.incidents",
        "experience.baifall.cadrage.complet.du.projet.benchmark",
    ]

    with pytest.raises(TailoringError, match="does not belong to entry"):
        _render(payload)


def test_a_skill_fact_is_not_an_experience_bullet() -> None:
    """Only the entry's own facts, so a skill id cannot become a bullet."""

    payload = copy.deepcopy(_payload())
    payload["experience_content"][1]["fact_ids"] = [
        "experience.concentrix.incidents",
        "skill.wazuh",
    ]

    with pytest.raises(TailoringError, match="does not belong to entry"):
        _render(payload)


def test_a_project_fact_from_another_project_is_rejected() -> None:
    payload = copy.deepcopy(_payload())
    payload["project_content"][0]["fact_id"] = "project.soc.alternance.3.outcome"

    with pytest.raises(TailoringError, match="does not belong to entry"):
        _render(payload)


def test_an_unresolvable_selection_is_rejected() -> None:
    payload = copy.deepcopy(_payload())
    payload["experience_content"][1]["fact_ids"] = [
        "experience.concentrix.incidents",
        "experience.concentrix.nowhere",
    ]

    with pytest.raises(TailoringError, match="unknown fact id"):
        _render(payload)


def test_a_prefix_less_selection_still_resolves(bank) -> None:
    """Task 25's tolerance survives: ids are normalised before they are judged."""

    payload = copy.deepcopy(_payload())
    payload["experience_content"][1]["fact_ids"] = [
        "concentrix.incidents",
        "concentrix.resolution_time",
    ]

    rendered = _bullets(_render(payload), "Concentrix")

    assert rendered[0] == bank.claims["experience.concentrix.incidents"].text


# ----- 30.2 what the advisor still writes -----


def test_the_domain_phrase_is_still_written_and_bounded() -> None:
    payload = copy.deepcopy(_payload())
    payload["profile_domain_phrase"] = "détection"

    with pytest.raises(TailoringError, match="3 to 7 words"):
        _render(payload)


def test_the_profile_stays_within_fifteen_characters_of_the_template() -> None:
    payload = copy.deepcopy(_payload())
    payload["profile_domain_phrase"] = (
        "détection proactive des menaces avancées et gouvernance"
    )

    with pytest.raises(TailoringError, match="within 15 characters"):
        _render(payload)


def test_a_fabricated_tool_in_the_domain_phrase_is_refused() -> None:
    """The phrase is short, but it is still generated, so the tiers still read it."""

    payload = copy.deepcopy(_payload())
    payload["profile_domain_phrase"] = "détection avancée via CrowdStrike"

    with pytest.raises(TailoringError, match="unsupported capability 'CrowdStrike'"):
        _render(payload)


def test_a_fabricated_figure_in_the_domain_phrase_is_refused() -> None:
    payload = copy.deepcopy(_payload())
    payload["profile_domain_phrase"] = "détection sur 15 000 incidents"

    with pytest.raises(TailoringError, match="unsupported number '15 000'"):
        _render(payload)


def test_a_category_word_in_the_domain_phrase_is_free() -> None:
    payload = copy.deepcopy(_payload())
    payload["profile_domain_phrase"] = "supervision SIEM et réponse à incident"

    assert _render(payload)


def test_the_letter_is_still_free_generation(bank) -> None:
    payload = copy.deepcopy(_payload())
    payload["letter_paragraphs"][0]["text"] = (
        "Votre poste rejoint précisément mon projet de spécialisation en sécurité."
    )

    assert _render(payload)


# ----- 30.3 tech rows are reordered, never invented -----


def test_tech_reordering_never_adds_or_drops_a_tool() -> None:
    original = TEMPLATE_PATH.read_text(encoding="utf-8")
    payload = copy.deepcopy(_payload())
    payload["skill_order"] = ["skill.wazuh", "skill.python"]

    tailored = _render(payload)

    def tools(source: str) -> set[str]:
        return {
            value.strip()
            for row in re.findall(r'<div class="tech-list">(.*?)</div>', source)
            for value in re.sub(r"<[^>]+>", "", row).split(",")
            if value.strip()
        }

    assert tools(tailored) == tools(original)


def test_an_unknown_category_cannot_be_introduced() -> None:
    payload = copy.deepcopy(_payload())
    payload["tech_order"] = [*payload["tech_order"], "Quantique"]

    with pytest.raises(TailoringError):
        _render(payload)


# ----- 30.5 the orphan gate splits, the page count does not -----


class _SelectingAdvisor:
    """Returns the reference selection payload, unchanged."""

    def advise(self, offer, selection, template):
        return TailoringPlan.from_mapping(
            _payload(),
            offer=offer,
            selection=selection,
        )


def _approve(db: sqlite3.Connection, tmp_path: Path, toolchain) -> object:
    return approve_application(
        db,
        _queued_application(db),
        via="test selection tailoring",
        advisor=_SelectingAdvisor(),
        toolchain=toolchain,
        output_root=tmp_path,
    )


def test_an_orphan_in_verbatim_content_warns_and_is_recorded(
    db: sqlite3.Connection,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The asset file calls these false positives outside a full render."""

    from tests.test_tailoring import _Toolchain

    with caplog.at_level("WARNING", logger="jobpilot.tailoring"):
        outcome = _approve(
            db,
            tmp_path,
            _Toolchain(fail_orphans=True, orphan_selector="li"),
        )

    assert outcome.generation is not None
    assert current_status(db, outcome.application_id) == "ready"
    assert "orphan warning on verbatim content" in caplog.text
    detail = db.execute(
        "SELECT detail FROM events WHERE application_id = ? AND event = 'status_change' "
        "ORDER BY id DESC LIMIT 1",
        (outcome.application_id,),
    ).fetchone()["detail"]
    assert "orphan_warning" in json.loads(detail)


def test_an_orphan_in_the_generated_profile_still_fails(
    db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    from tests.test_tailoring import _Toolchain

    with pytest.raises(ApplicationGenerationError, match="orphan"):
        _approve(
            db,
            tmp_path,
            _Toolchain(fail_orphans=True, orphan_selector=".profile"),
        )


def test_a_clean_generation_records_no_orphan_warning(
    db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    from tests.test_tailoring import _Toolchain

    outcome = _approve(db, tmp_path, _Toolchain())

    detail = db.execute(
        "SELECT detail FROM events WHERE application_id = ? AND event = 'status_change' "
        "ORDER BY id DESC LIMIT 1",
        (outcome.application_id,),
    ).fetchone()["detail"]
    parsed = json.loads(detail)
    assert "orphan_warning" not in parsed
    assert parsed["selection_justifications"]["Concentrix"]


def test_the_page_count_remains_a_hard_gate(
    db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    """The reliable control, per the asset file, so it never becomes advisory."""

    from tests.test_tailoring import _Toolchain

    class _TooLong(_Toolchain):
        def verify_page_count(self, pdf_path: Path) -> None:
            raise TailoringError("page count gate failed: 2 pages")

    with pytest.raises(ApplicationGenerationError, match="page count"):
        _approve(db, tmp_path, _TooLong())


def test_the_prompt_asks_for_selections_not_prose() -> None:
    from jobpilot.tailoring import _advisor_prompt

    offer = _offer()
    selection = pick_variant(offer.description, title=offer.title)
    prompt = _advisor_prompt(
        offer,
        selection,
        extract_template_context(TEMPLATE_PATH.read_text(encoding="utf-8")),
    )

    assert '"fact_ids"' in prompt
    assert "You SELECT the CV's experience bullets" in prompt
    assert "paraphrase, shorten, translate, or re-punctuate" in prompt
    assert '"bullets"' not in prompt
