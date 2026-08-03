"""Task 40: the stage contract line has a degradation now.

_validate_plan's stage-contract check was recoverable with nothing to fall back
to, so under Task 39's rule it escalated to fatal. It killed applications 25 and
28 outright, four times between them, and none of the three stage offers in the
queue states a duration for the retry to copy.

The fallback is built rather than guessed: the offer's duration when it has one,
the templates' own wording when it does not — the profile's contract line says
what the candidate is looking for, not what the posting offers.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from jobpilot.tailoring import (
    _STAGE_DEFAULT_DURATION,
    OfferContext,
    TailoringError,
    Tier,
    _resolve_stage_contract_phrase,
    _stage_contract_fallback,
    _validate_stage_contract_phrase,
    variant_for_slug,
)

TEMPLATES = Path(__file__).resolve().parents[1] / "skill" / "assets" / "cv-templates"


def _offer(*, duration: int | None, description: str = "SIEM dès mars 2027"):
    return OfferContext(
        title="Stage Cybersécurité",
        company="Acme",
        description=description,
        contract_type="stage",
        duration_months=duration,
        city="Paris",
        url="https://example.test/jobs/40",
        source="france_travail",
    )


def test_the_default_duration_is_what_the_stage_templates_say() -> None:
    """Pinned to the file, so the constant cannot drift away from the CV."""

    stage_templates = sorted(TEMPLATES.glob("*Stage*.html"))
    assert stage_templates, "no dedicated stage templates found"

    for path in stage_templates:
        profile = path.read_text(encoding="utf-8").split('<section class="profile">')[1]
        text = re.sub(r"&agrave;", "à", profile.split("</section>")[0])
        assert f"stage de {_STAGE_DEFAULT_DURATION}" in text, path.name


def test_the_fallback_uses_the_offers_duration_when_it_has_one() -> None:
    assert _stage_contract_fallback(_offer(duration=6)) == (
        "Stage de 6 mois dès mars 2027"
    )


def test_the_fallback_falls_back_to_the_template_wording_without_one() -> None:
    """All three stage offers in the queue are this case."""

    assert _stage_contract_fallback(_offer(duration=None)) == (
        f"Stage de {_STAGE_DEFAULT_DURATION} dès mars 2027"
    )


@pytest.mark.parametrize("duration", (None, 3, 6, 12))
def test_the_fallback_always_passes_the_rule_it_is_replacing(duration) -> None:
    """A degradation that fails the same gate is not a degradation."""

    _validate_stage_contract_phrase(_stage_contract_fallback(_offer(duration=duration)))


def test_the_gate_is_recoverable_and_names_itself() -> None:
    with pytest.raises(TailoringError) as excinfo:
        _validate_stage_contract_phrase(None)

    assert excinfo.value.gate == "_validate_stage_contract_phrase"
    assert excinfo.value.tier is Tier.RECOVERABLE


@pytest.mark.parametrize(
    "rejected",
    (None, "", "Stage", "Alternance de 12 mois dès septembre 2026", "6 mois"),
)
def test_a_rejected_phrase_is_replaced_not_kept(rejected) -> None:
    selection = variant_for_slug("soc", contract_type="stage")
    assert selection.adapted_for_stage

    resolved, reason = _resolve_stage_contract_phrase(
        rejected, selection=selection, offer=_offer(duration=None)
    )

    assert reason
    assert resolved != rejected
    _validate_stage_contract_phrase(resolved)


def test_a_valid_phrase_is_left_exactly_alone() -> None:
    selection = variant_for_slug("soc", contract_type="stage")

    resolved, reason = _resolve_stage_contract_phrase(
        "Stage de 4 mois dès janvier 2027",
        selection=selection,
        offer=_offer(duration=None),
    )

    assert resolved == "Stage de 4 mois dès janvier 2027"
    assert reason is None


def test_a_stage_generation_completes_when_the_model_omits_the_phrase(
    db, tmp_path
) -> None:
    """End to end, on the failure that killed applications 25 and 28.

    The live re-runs did not exercise this — the model supplied a valid phrase
    that time — so the degradation is proven here instead of assumed.
    """

    import hashlib

    from jobpilot.apply_flow import approve_application
    from jobpilot.generation_warnings import warnings_for
    from jobpilot.state import current_status
    from jobpilot.tailoring import TailoringPlan
    from tests.test_tailoring import _Toolchain
    from tests.test_tailoring_retry import _payload

    source_id = db.execute(
        "SELECT id FROM sources WHERE name = 'france_travail'"
    ).fetchone()["id"]
    company_id = db.execute("INSERT INTO companies (name) VALUES ('Acme')").lastrowid
    offer_id = db.execute(
        "INSERT INTO offers (source_id, company_id, external_id, url, title, "
        "description, contract_type, duration_months, city, content_hash) "
        "VALUES (?, ?, 'stage-40', 'https://example.test/40', "
        "'Stagiaire SOC', 'Analyser les alertes SIEM dès septembre 2026', "
        "'stage', NULL, 'Paris', ?)",
        (source_id, company_id, hashlib.sha256(b"stage-40").hexdigest()),
    ).lastrowid
    application_id = db.execute(
        "INSERT INTO applications (offer_id, company_id, kind, status) "
        "VALUES (?, ?, 'offer', 'queued')",
        (offer_id, company_id),
    ).lastrowid
    db.commit()

    class _OmitsTheContractPhrase:
        accepts_correction = True

        def advise(self, offer, selection, template, *, correction=None):
            assert selection.adapted_for_stage, "fixture must adapt an alternance CV"
            payload = _payload()
            payload["profile_contract_phrase"] = None
            return TailoringPlan.from_mapping(
                payload, offer=offer, selection=selection
            )

    approve_application(
        db,
        application_id,
        via="test",
        advisor=_OmitsTheContractPhrase(),
        toolchain=_Toolchain(),
        output_root=tmp_path,
    )

    assert current_status(db, application_id) == "ready"
    gates = [w.gate for w in warnings_for(db, application_id)]
    assert "_validate_stage_contract_phrase" in gates
    cv = (tmp_path / str(application_id) / "tailored_cv.html").read_text(
        encoding="utf-8"
    )
    assert f"Stage de {_STAGE_DEFAULT_DURATION} dès septembre 2026" in cv


def test_nothing_happens_outside_stage_adaptation() -> None:
    """The contract line is immutable on an alternance CV; that rule is untouched."""

    selection = variant_for_slug("soc", contract_type="alternance")
    assert not selection.adapted_for_stage

    resolved, reason = _resolve_stage_contract_phrase(
        None, selection=selection, offer=_offer(duration=None)
    )

    assert resolved is None
    assert reason is None
