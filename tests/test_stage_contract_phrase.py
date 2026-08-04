"""Task 44 item 1: the stage contract line is renderer-owned.

A real generation (COMCYBER, application 37) shipped « Stage de [offer duration]
mois dès [offer start date] » into a PDF. The prompt had told the model the
phrase must be *exactly* that string, and it complied literally. No gate could
object: as a contract line it is well formed, every word is supported, the
layout fits. Only the brackets were wrong and nothing was looking at them.

Duration and start date are parsed offer fields, so the renderer builds the
sentence — the move Task 38 already made for the job title and the header
location. The model is no longer asked for the field at all.

This file was tests/test_stage_contract_fallback.py under Task 40, when the
built phrase was a degradation behind a model-supplied one. It is the only path
now, so the tests that covered preserving a valid candidate are gone with the
candidate.
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
    _renderer_contract_phrase,
    _stage_contract_phrase,
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


def test_the_phrase_uses_the_offers_duration_when_it_has_one() -> None:
    assert _stage_contract_phrase(_offer(duration=6)) == "Stage de 6 mois dès mars 2027"


def test_a_missing_duration_falls_back_to_the_template_wording() -> None:
    """Never a placeholder. The sentence says what he is looking for, so the
    templates' own wording is true of an offer that states no duration — which
    is all three of the stage offers in the queue."""

    assert _stage_contract_phrase(_offer(duration=None)) == (
        f"Stage de {_STAGE_DEFAULT_DURATION} dès mars 2027"
    )


@pytest.mark.parametrize("duration", (None, 3, 6, 12))
def test_the_built_phrase_always_passes_the_rule_for_the_field(duration) -> None:
    _validate_stage_contract_phrase(_stage_contract_phrase(_offer(duration=duration)))


@pytest.mark.parametrize("duration", (None, 3, 6, 12))
def test_the_built_phrase_never_contains_a_bracket(duration) -> None:
    """The whole point of the task, asserted on the field that shipped one."""

    phrase = _stage_contract_phrase(_offer(duration=duration))

    assert "[" not in phrase and "]" not in phrase


def test_the_gate_is_recoverable_and_names_itself() -> None:
    with pytest.raises(TailoringError) as excinfo:
        _validate_stage_contract_phrase(None)

    assert excinfo.value.gate == "_validate_stage_contract_phrase"
    assert excinfo.value.tier is Tier.RECOVERABLE


def test_the_renderer_owns_the_field_on_an_adapted_stage() -> None:
    selection = variant_for_slug("soc", contract_type="stage")
    assert selection.adapted_for_stage

    assert _renderer_contract_phrase(selection, _offer(duration=4)) == (
        "Stage de 4 mois dès mars 2027"
    )


def test_nothing_is_written_outside_stage_adaptation() -> None:
    """The contract line is the template's own on an alternance CV. That was a
    rule the model could break and be rejected for; it is now a fact."""

    selection = variant_for_slug("soc", contract_type="alternance")
    assert not selection.adapted_for_stage

    assert _renderer_contract_phrase(selection, _offer(duration=6)) is None


def test_a_stage_generation_overwrites_a_placeholder_phrase_from_the_model(
    db, tmp_path
) -> None:
    """End to end, on the exact string that reached application 37's PDF.

    The advisor here returns what the old prompt asked for, brackets and all.
    Before this task that string passed every gate and rendered. Now it is
    discarded before it can be validated, because the field is not the model's
    to write.
    """

    import hashlib

    from jobpilot.apply_flow import approve_application
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

    class _ReturnsThePlaceholder:
        accepts_correction = True

        def advise(self, offer, selection, template, *, correction=None):
            assert selection.adapted_for_stage, "fixture must adapt an alternance CV"
            payload = _payload()
            payload["profile_contract_phrase"] = (
                "Stage de [offer duration] mois dès [offer start date]"
            )
            return TailoringPlan.from_mapping(
                payload, offer=offer, selection=selection
            )

    approve_application(
        db,
        application_id,
        via="test",
        advisor=_ReturnsThePlaceholder(),
        toolchain=_Toolchain(),
        output_root=tmp_path,
    )

    assert current_status(db, application_id) == "ready"
    cv = (tmp_path / str(application_id) / "tailored_cv.html").read_text(
        encoding="utf-8"
    )
    assert "[offer duration]" not in cv
    assert "[offer start date]" not in cv
    assert f"Stage de {_STAGE_DEFAULT_DURATION} dès septembre 2026" in cv


def test_the_prompt_no_longer_asks_for_the_phrase_at_all() -> None:
    """Fixing the instruction's wording would have left the model writing a
    field the renderer can derive. The instruction is gone instead."""

    from jobpilot.tailoring import _advisor_prompt, extract_template_context

    selection = variant_for_slug("soc", contract_type="stage")
    template_path = next(TEMPLATES.glob("*Cybersecurite__Alternance.html"))
    template = extract_template_context(template_path.read_text(encoding="utf-8"))

    prompt = _advisor_prompt(_offer(duration=None), selection, template)

    assert "[offer duration]" not in prompt
    assert "[offer start date]" not in prompt
    assert "profile_contract_phrase must be null" in prompt
