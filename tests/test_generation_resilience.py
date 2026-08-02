"""Systemic recovery at the generated-prose and document-layout boundaries."""

from __future__ import annotations

import copy
import json
import sqlite3
from pathlib import Path

import pytest

from jobpilot.apply_flow import approve_application
from jobpilot.facts import load_fact_bank
from jobpilot.state import current_status
from jobpilot.tailoring import (
    OfferContext,
    TailoringError,
    TailoringPlan,
    _advisor_prompt,
    _resolve_profile_phrase,
    _restore_template_profile_domain,
    extract_template_context,
    pick_variant,
    validate_plan_provenance,
    variant_for_slug,
)
from jobpilot.variant_catalogue import default_catalogue
from tests.test_fact_id_resolution import TEMPLATE_PATH
from tests.test_selection_tailoring import _SelectingAdvisor
from tests.test_tailoring import _Toolchain
from tests.test_tailoring_provenance import _payload, _queued_application


def _offer(*, title: str = "Analyst N2", company: str = "Thales") -> OfferContext:
    return OfferContext(
        title=title,
        company=company,
        description=(
            "Analyser les alertes SIEM et accompagner le support dès septembre 2026."
        ),
        contract_type="alternance",
        duration_months=12,
        city="Paris",
        source="france_travail",
        url="https://example.test/jobs/resilience",
    )


def _selection_and_template():
    offer = _offer(title="Analyste SOC")
    selection = pick_variant(offer.description, title=offer.title)
    template = extract_template_context(TEMPLATE_PATH.read_text(encoding="utf-8"))
    return selection, template


def test_a_valid_custom_profile_phrase_is_preserved_exactly() -> None:
    selection, template = _selection_and_template()
    candidate = "supervision SIEM et réponse à incident"

    phrase, reason = _resolve_profile_phrase(
        candidate,
        selection=selection,
        template=template,
        bank=load_fact_bank(),
    )

    assert phrase == candidate
    assert reason is None


@pytest.mark.parametrize(
    "candidate",
    (
        "sécurité orientée Analyst",
        "réseaux et support N2",
        "détection",
    ),
)
def test_an_invalid_profile_phrase_uses_the_variant_fallback(candidate: str) -> None:
    selection, template = _selection_and_template()

    phrase, reason = _resolve_profile_phrase(
        candidate,
        selection=selection,
        template=template,
        bank=load_fact_bank(),
    )

    assert phrase == "détection proactive des menaces"
    assert reason


def test_offer_identity_is_renderer_owned_without_losing_evidence() -> None:
    offer = _offer()
    payload = copy.deepcopy(_payload())
    evidence = [paragraph["text"] for paragraph in payload["letter_paragraphs"]]
    plan = TailoringPlan.from_mapping(
        payload,
        offer=offer,
        selection=pick_variant(offer.description, title=offer.title),
    )

    assert "Thales" in plan.letter_body_html
    assert "Analyst N2" in plan.letter_body_html
    assert all(text in plan.letter_body_html for text in evidence)
    validate_plan_provenance(plan, load_fact_bank(), offer_location=offer.city)


def test_an_unsupported_candidate_claim_remains_a_hard_failure() -> None:
    offer = _offer()
    payload = copy.deepcopy(_payload())
    payload["letter_paragraphs"][0]["text"] = (
        "J'ai utilisé CrowdStrike pour superviser les alertes."
    )
    plan = TailoringPlan.from_mapping(
        payload,
        offer=offer,
        selection=pick_variant(offer.description, title=offer.title),
    )

    with pytest.raises(TailoringError, match="unsupported capability 'CrowdStrike'"):
        validate_plan_provenance(plan, load_fact_bank(), offer_location=offer.city)


def test_model_prose_dashes_are_canonicalized_before_validation() -> None:
    offer = _offer(title="Analyste SOC — N2")
    payload = copy.deepcopy(_payload())
    payload["profile_domain_phrase"] = "supervision SIEM — réponse à incident"
    payload["rationale"] = "SIEM — réponse aux incidents"
    payload["letter_paragraphs"][0]["text"] = (
        "Cette mission – centrée sur le SOC – correspond à mon projet."
    )

    plan = TailoringPlan.from_mapping(
        payload,
        offer=offer,
        selection=pick_variant(offer.description, title=offer.title),
    )

    assert "—" not in plan.job_title
    assert "—" not in plan.profile_domain_phrase
    assert "—" not in plan.rationale
    assert "—" not in plan.letter_body_html
    assert "–" not in plan.letter_body_html
    assert " - " in plan.letter_paragraphs[0].text


def test_prompt_keeps_offer_identity_out_of_model_evidence() -> None:
    offer = _offer()
    selection = pick_variant(offer.description, title=offer.title)
    prompt = _advisor_prompt(
        offer,
        selection,
        extract_template_context(TEMPLATE_PATH.read_text(encoding="utf-8")),
    )

    assert "Do not repeat the company name, job title, or location" in prompt
    assert "renderer injects the offer identity" in prompt


@pytest.mark.parametrize(
    "slug",
    tuple(entry.slug for entry in default_catalogue().entries),
)
def test_layout_fallback_restores_each_trusted_template_phrase(slug: str) -> None:
    selection = variant_for_slug(slug, contract_type="alternance")
    original = (TEMPLATE_PATH.parent / selection.template_name).read_text(
        encoding="utf-8"
    )
    expected = extract_template_context(original).profile_domain_phrase
    changed = _restore_template_profile_domain(
        original,
        "sécurité des systèmes numériques",
        selection=selection,
    )

    restored = _restore_template_profile_domain(
        changed,
        expected,
        selection=selection,
    )

    assert extract_template_context(restored).profile_domain_phrase == expected


class _OneShotProfileOrphan(_Toolchain):
    """A profile-only layout regression that disappears with template wording."""

    def __init__(self) -> None:
        super().__init__()
        self.orphan_checks = 0

    def check_orphan_lines(self, tailored_path: Path, original_path: Path) -> None:
        self.calls.append("orphans")
        self.orphan_checks += 1
        if self.orphan_checks == 1:
            raise TailoringError(
                "orphan quality gate failed: ORPHAN REGRESSIONS: 1\n"
                "  [.profile#0] 2 lines, last=18.0% width"
            )


def test_profile_orphan_recovers_with_template_wording(
    db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    toolchain = _OneShotProfileOrphan()
    application_id = _queued_application(db)

    outcome = approve_application(
        db,
        application_id,
        via="test generation resilience",
        advisor=_SelectingAdvisor(),
        toolchain=toolchain,
        output_root=tmp_path,
    )

    assert outcome.generation is not None
    assert toolchain.orphan_checks == 2
    assert current_status(db, application_id) == "ready"
    final_context = extract_template_context(
        outcome.generation.cv_html_path.read_text(encoding="utf-8")
    )
    original_context = extract_template_context(
        TEMPLATE_PATH.read_text(encoding="utf-8")
    )
    assert final_context.profile_domain_phrase == original_context.profile_domain_phrase
    detail = db.execute(
        "SELECT detail FROM events WHERE application_id = ? AND event = 'status_change' "
        "ORDER BY id DESC LIMIT 1",
        (application_id,),
    ).fetchone()["detail"]
    assert json.loads(detail)["profile_layout_fallback"] is True
