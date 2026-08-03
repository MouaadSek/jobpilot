"""Task 40: the domain phrase is found by its own marker, not by its neighbours.

_PROFILE_DOMAIN_RE used to anchor on what FOLLOWED the phrase — "<strong>Alternance"
or "Recherche un <strong>stage". The stage adaptation replaces exactly that region
with the offer's own contract phrase, so on a stage-adapted CV the anchor stopped
existing and every later read raised "template profile domain phrase not found".
That aborted every stage-adapted generation; app 26 was the reproduction.

The fix is the coupling, not the symptom: the phrase carries a marker we emit
ourselves, so extraction cannot be broken by rewriting the prose around it.
"""

from __future__ import annotations

import dataclasses
import re
from pathlib import Path

import pytest

from jobpilot.facts import load_fact_bank
from jobpilot.tailoring import (
    _PROFILE_DOMAIN_RE,
    OfferContext,
    TailoringPlan,
    _extract_profile_domain,
    _restore_template_profile_domain,
    extract_template_context,
    tailor_cv_html,
    variant_for_slug,
)
from tests.test_tailoring_retry import _payload

TEMPLATES = sorted(
    (Path(__file__).resolve().parents[1] / "skill" / "assets" / "cv-templates").glob(
        "*.html"
    )
)


def _profile_of(source: str) -> str:
    return source.split('<section class="profile">')[1].split("</section>")[0]


def _stage_plan(selection):
    offer = OfferContext(
        title="Stagiaire SOC",
        company="Acme",
        description="SIEM dès septembre 2026",
        contract_type="stage",
        duration_months=6,
        city="Paris",
        url="https://example.test/jobs/40",
        source="france_travail",
    )
    payload = _payload()
    payload["profile_contract_phrase"] = "Stage de 6 mois dès septembre 2026"
    return offer, TailoringPlan.from_mapping(payload, offer=offer, selection=selection)


def test_every_template_carries_the_marker_exactly_once() -> None:
    assert TEMPLATES, "no templates found"

    for path in TEMPLATES:
        source = path.read_text(encoding="utf-8")
        assert len(_PROFILE_DOMAIN_RE.findall(source)) == 1, path.name


@pytest.mark.parametrize("path", TEMPLATES, ids=lambda p: p.stem[:28])
def test_every_template_still_extracts_its_domain_phrase(path: Path) -> None:
    phrase = _extract_profile_domain(path.read_text(encoding="utf-8"))

    assert phrase.strip()
    assert "<" not in phrase


def test_a_stage_adapted_cv_can_still_be_re_read() -> None:
    """The bug. This raised "template profile domain phrase not found"."""

    selection = variant_for_slug("soc", contract_type="stage")
    assert selection.adapted_for_stage, "fixture must exercise the adaptation path"
    original = (TEMPLATES[0].parent / selection.template_name).read_text(
        encoding="utf-8"
    )
    offer, plan = _stage_plan(selection)

    tailored = tailor_cv_html(
        original,
        plan,
        selection,
        offer_description=offer.description,
        fact_bank=load_fact_bank(),
        offer=offer,
    )

    # The contract sentence the old anchor depended on is gone by now.
    assert "Alternance de" not in _profile_of(tailored)
    assert _extract_profile_domain(tailored) == plan.profile_domain_phrase
    assert extract_template_context(tailored).profile_domain_phrase


def test_extraction_survives_an_arbitrary_contract_sentence() -> None:
    """Not just the wordings we ship: any of them, including ones nobody wrote yet."""

    source = (TEMPLATES[0].parent / "Mouaad_Sekkouri_-_SOC__Alternance.html").read_text(
        encoding="utf-8"
    )
    profile = _profile_of(source)

    for replacement in (
        "<strong>Stage de 6 mois dès juin 2027</strong>.",
        "<strong>Contrat pro dès mars</strong>. Rythme : <strong>3/1</strong>.",
        "Disponible immédiatement.",
        "",
    ):
        mutated = source.replace(
            profile,
            re.sub(
                r"(</span>\.).*$",
                lambda m, r=replacement: f"{m.group(1)} {r}",
                profile,
                flags=re.DOTALL,
            ),
        )

        assert _extract_profile_domain(mutated) == "détection et réponse aux incidents"


def test_both_rewrites_keep_the_marker() -> None:
    """A rewrite that dropped it would break the next read instead of this one."""

    selection = variant_for_slug("soc", contract_type="alternance")
    original = (TEMPLATES[0].parent / selection.template_name).read_text(
        encoding="utf-8"
    )
    offer, plan = _stage_plan(selection)
    # Outside stage adaptation the contract text is immutable, so this plan
    # exercises the domain rewrite alone.
    plan = dataclasses.replace(plan, profile_contract_phrase=None)

    tailored = tailor_cv_html(
        original,
        plan,
        selection,
        offer_description=offer.description,
        fact_bank=load_fact_bank(),
        offer=offer,
    )
    restored = _restore_template_profile_domain(
        tailored, "sécurité opérationnelle", selection=selection
    )

    assert len(_PROFILE_DOMAIN_RE.findall(tailored)) == 1
    assert len(_PROFILE_DOMAIN_RE.findall(restored)) == 1
    assert _extract_profile_domain(restored) == "sécurité opérationnelle"


def test_the_marker_adds_no_visible_text() -> None:
    """The ±15-character layout budget must not shift under it."""

    from jobpilot.tailoring import _plain

    source = (TEMPLATES[0].parent / "Mouaad_Sekkouri_-_SOC__Alternance.html").read_text(
        encoding="utf-8"
    )
    profile = _profile_of(source)

    assert "profile-domain" not in _plain(profile)
