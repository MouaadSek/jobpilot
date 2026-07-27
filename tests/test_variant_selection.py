"""The advisor chooses the CV; the keyword router is only a sanity check."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

import pytest
import respx

from jobpilot.apply_flow import approve_application
from jobpilot.config import PROJECT_ROOT
from jobpilot.state import current_status
from jobpilot.tailoring import (
    InteractiveTailoringAdvisor,
    OfferContext,
    OpenAITailoringAdvisor,
    TailoringPlan,
    VariantChoice,
    _interactive_structured_payload,
    pick_variant,
    resolve_variant,
)
from jobpilot.variant_catalogue import default_catalogue

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "offers"
VILLENEUVE_MISSIONS = (FIXTURES / "villeneuve_dascq_ingenieur_cyber.txt").read_text(
    encoding="utf-8"
)
VILLENEUVE_TITLE = "Ingénieur cyber sécurité (H/F)"
TEMPLATE_ROOT = PROJECT_ROOT / "skill" / "assets" / "cv-templates"
OPENAI_URL = "https://api.openai.com/v1/chat/completions"


def _offer(
    *,
    title: str = "Analyste SOC (H/F)",
    description: str = "Analyser les alertes SIEM et répondre aux incidents dès septembre 2026.",
    contract_type: str = "alternance",
    duration_months: int | None = 12,
) -> OfferContext:
    return OfferContext(
        title=title,
        company="Acme",
        description=description,
        contract_type=contract_type,
        duration_months=duration_months,
        city="Villeneuve-d'Ascq",
        source="france_travail",
        url="https://example.test/jobs/24",
    )


class _Toolchain:
    """Records the gates without pinning them to one offer or one variant."""

    def __init__(self) -> None:
        self.calls: list[str] = []
        self.tracker_fields: dict[str, str] = {}

    def validate_cv(self, tailored_path, original_path, *, compare_original) -> None:
        self.calls.append("validate")
        assert tailored_path.exists()
        assert original_path.exists()

    def check_orphan_lines(self, tailored_path, original_path) -> None:
        self.calls.append("orphans")

    def generate_cv_pdf(self, tailored_path, output_path) -> None:
        self.calls.append("cv")
        output_path.write_bytes(b"%PDF-cv")

    def generate_letter_pdf(
        self, cv_path, body_path, output_path, *, company, location, date
    ) -> None:
        self.calls.append("letter")
        output_path.write_bytes(b"%PDF-letter")

    def verify_page_count(self, pdf_path) -> None:
        self.calls.append(f"verify:{pdf_path.stem}")

    def format_tracker_row(self, **fields: str) -> str:
        self.calls.append("tracker")
        self.tracker_fields = dict(fields)
        return "\t".join([""] * 18)


class _SelectingAdvisor:
    """API-shaped advisor: answers selection, then tailors whatever was chosen.

    Selection answers are validated exactly as the real advisors validate them,
    so an invented slug raises inside ``select_variant`` and rides the retry path.
    """

    accepts_correction = True

    def __init__(
        self,
        *answers: dict[str, Any] | Exception,
        runner_up: str = "cybersecurite",
    ) -> None:
        self.answers = list(answers)
        self.runner_up = runner_up
        self.selection_corrections: list[str | None] = []
        self.tailored_slugs: list[str] = []

    def select_variant(self, offer, catalogue, *, correction: str | None = None):
        index = min(len(self.selection_corrections), len(self.answers) - 1)
        self.selection_corrections.append(correction)
        answer = self.answers[index]
        if isinstance(answer, Exception):
            raise answer
        return VariantChoice.from_mapping(answer, catalogue=catalogue)

    def advise(self, offer, selection, template, *, correction: str | None = None):
        self.tailored_slugs.append(selection.slug)
        return TailoringPlan.from_mapping(
            _interactive_structured_payload(offer, selection, template),
            offer=offer,
            selection=selection,
        )


def _answer(slug: str, *, runner_up: str = "cybersecurite") -> dict[str, Any]:
    return {
        "slug": slug,
        "runner_up": runner_up if runner_up != slug else "soc",
        "justification": f"Les missions décrivent surtout du {slug}.",
    }


def _queued_application(
    db: sqlite3.Connection,
    *,
    suffix: str,
    title: str,
    description: str,
    contract_type: str = "alternance",
) -> int:
    source_id = db.execute(
        "SELECT id FROM sources WHERE name = 'france_travail'"
    ).fetchone()["id"]
    company_id = db.execute("INSERT INTO companies (name) VALUES ('Acme')").lastrowid
    digest = hashlib.sha256(f"selection-{suffix}".encode()).hexdigest()
    offer_id = db.execute(
        "INSERT INTO offers (source_id, company_id, external_id, url, title, "
        "description, contract_type, duration_months, city, content_hash) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, 12, 'Villeneuve-d''Ascq', ?)",
        (
            source_id,
            company_id,
            f"offer-{suffix}",
            f"https://example.test/jobs/{suffix}",
            title,
            description,
            contract_type,
            digest,
        ),
    ).lastrowid
    application_id = db.execute(
        "INSERT INTO applications (offer_id, company_id, kind, status) "
        "VALUES (?, ?, 'offer', 'queued')",
        (offer_id, company_id),
    ).lastrowid
    db.commit()
    return int(application_id)


def _ready_detail(db: sqlite3.Connection, application_id: int) -> dict[str, Any]:
    rows = db.execute(
        "SELECT detail FROM events WHERE application_id = ? AND event = 'status_change' "
        "ORDER BY id DESC",
        (application_id,),
    ).fetchall()
    for row in rows:
        parsed = json.loads(row["detail"])
        if parsed.get("to") == "ready":
            return parsed
    raise AssertionError("no ready status_change event")


def _decision(advisor: Any, offer: OfferContext) -> Any:
    return resolve_variant(
        advisor,
        offer=offer,
        application_id=1,
        template_root=TEMPLATE_ROOT,
    )


# ----- the regression this task exists for -----


def test_keyword_router_still_misroutes_the_villeneuve_offer() -> None:
    """The bug, pinned: one « pilotage » outweighs twenty technical signals."""

    keyword = pick_variant(
        VILLENEUVE_MISSIONS, title=VILLENEUVE_TITLE, contract_type="alternance"
    )

    assert keyword.slug == "chef-de-projet-it"


def test_advisor_pick_beats_the_keyword_misroute_on_the_real_offer(
    db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    application_id = _queued_application(
        db,
        suffix="villeneuve",
        title=VILLENEUVE_TITLE,
        description=VILLENEUVE_MISSIONS,
    )
    # The answer a real gpt-5.4-mini call returned for this exact offer.
    advisor = _SelectingAdvisor(
        {
            "slug": "grc",
            "runner_up": "cybersecurite",
            "justification": (
                "Les missions portent surtout sur la gouvernance sécurité, "
                "l'analyse de risques EBIOS RM, les exigences PSSI, les audits "
                "et les KPI de conformité."
            ),
        }
    )
    toolchain = _Toolchain()

    outcome = approve_application(
        db,
        application_id,
        via="test selection",
        advisor=advisor,
        toolchain=toolchain,
        output_root=tmp_path,
    )

    result = outcome.generation
    assert result is not None
    assert result.selection.slug == "grc"
    assert result.selection.slug != "chef-de-projet-it"
    # The document really was tailored from the selected template, and the
    # tracker names the CV that was produced.
    assert advisor.tailored_slugs == ["grc"]
    assert result.selection.template_name == "Mouaad_Sekkouri_-_GRC__Alternance.html"
    assert toolchain.tracker_fields["cv"] == "CV GRC"
    assert current_status(db, application_id) == "ready"

    decision = result.decision
    assert decision is not None
    assert decision.chosen_by == "advisor"
    assert decision.keyword_slug == "chef-de-projet-it"
    assert decision.agreed is False
    assert decision.runner_up == "cybersecurite"
    assert "EBIOS RM" in decision.justification


def test_disagreement_is_recorded_in_the_event_detail_and_logged(
    db: sqlite3.Connection,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    application_id = _queued_application(
        db,
        suffix="villeneuve-audit",
        title=VILLENEUVE_TITLE,
        description=VILLENEUVE_MISSIONS,
    )
    advisor = _SelectingAdvisor(_answer("grc", runner_up="cybersecurite"))

    with caplog.at_level("INFO", logger="jobpilot.tailoring"):
        approve_application(
            db,
            application_id,
            via="test audit",
            advisor=advisor,
            toolchain=_Toolchain(),
            output_root=tmp_path,
        )

    detail = _ready_detail(db, application_id)
    assert detail["variant"] == "grc"
    # The keyword suggestion is kept as the disagreeing comparison point.
    assert detail["routing_variant"] == "Chef de Projet IT"
    assert detail["document_variant"] != "Chef de Projet IT"
    assert detail["variant_selected_by"] == "advisor"
    assert detail["routing_agreed"] is False
    assert "grc" in detail["routing_justification"]
    assert detail["routing_runner_up"] == "cybersecurite"

    logged = "\n".join(record.getMessage() for record in caplog.records)
    assert "variant disagreement" in logged
    assert "grc" in logged and "chef-de-projet-it" in logged


def test_agreement_is_recorded_without_a_fallback_reason(
    db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    application_id = _queued_application(
        db,
        suffix="agreed",
        title="Analyste SOC (H/F)",
        description="Analyser les alertes SIEM et répondre aux incidents dès septembre 2026.",
    )

    approve_application(
        db,
        application_id,
        via="test agreement",
        advisor=_SelectingAdvisor(_answer("soc", runner_up="cybersecurite")),
        toolchain=_Toolchain(),
        output_root=tmp_path,
    )

    detail = _ready_detail(db, application_id)
    assert detail["routing_agreed"] is True
    assert detail["routing_variant"] == "SOC Analyst"
    assert "routing_fallback_reason" not in detail


def test_fallback_reason_is_recorded_when_the_keyword_pick_is_used(
    db: sqlite3.Connection,
    tmp_path: Path,
) -> None:
    application_id = _queued_application(
        db,
        suffix="fallback-audit",
        title=VILLENEUVE_TITLE,
        description=VILLENEUVE_MISSIONS,
    )

    approve_application(
        db,
        application_id,
        via="test fallback",
        advisor=_SelectingAdvisor(_answer("nope"), _answer("still-nope")),
        toolchain=_Toolchain(),
        output_root=tmp_path,
    )

    detail = _ready_detail(db, application_id)
    assert detail["variant_selected_by"] == "keywords"
    assert detail["routing_agreed"] is True  # the keyword pick is what was used
    assert "still-nope" in detail["routing_fallback_reason"]
    assert "routing_justification" not in detail


# ----- validation and the Task 22c retry path -----


def test_invented_slug_is_rejected_then_accepted_on_the_single_retry() -> None:
    advisor = _SelectingAdvisor(
        _answer("cyber-ninja"),  # not in the catalogue
        _answer("appsec"),
    )

    decision = _decision(advisor, _offer())

    assert decision.selection.slug == "appsec"
    assert decision.chosen_by == "advisor"
    assert len(advisor.selection_corrections) == 2
    # The retry is fed the validator's own words, naming the legal choices.
    assert "cyber-ninja" in advisor.selection_corrections[1]
    assert "not a catalogue slug" in advisor.selection_corrections[1]


def test_slug_invented_twice_falls_back_to_the_keyword_pick() -> None:
    advisor = _SelectingAdvisor(_answer("cyber-ninja"), _answer("still-invented"))

    decision = _decision(advisor, _offer())

    assert decision.chosen_by == "keywords"
    assert decision.selection.slug == "soc"  # what the keywords say for this offer
    assert decision.keyword_slug == "soc"
    assert "still-invented" in decision.fallback_reason
    assert len(advisor.selection_corrections) == 2  # one retry, never more


@pytest.mark.parametrize(
    ("answer", "match"),
    (
        ({"slug": "soc", "runner_up": "grc"}, "justification"),
        ({"slug": "soc", "justification": "x", "runner_up": ""}, "runner_up"),
        ({"slug": "soc", "justification": "x", "runner_up": "soc"}, "must differ"),
        (
            {"slug": "soc", "justification": "x", "runner_up": "grc", "extra": 1},
            "unknown fields",
        ),
    ),
)
def test_all_three_selection_fields_are_required_and_checked(
    answer: dict[str, Any],
    match: str,
) -> None:
    from jobpilot.tailoring import TailoringError

    with pytest.raises(TailoringError, match=match):
        VariantChoice.from_mapping(answer, catalogue=default_catalogue())


# ----- mechanical constraints stay mechanical -----


def test_stage_contract_uses_the_dedicated_stage_template_for_the_selected_slug() -> None:
    advisor = _SelectingAdvisor(_answer("cybersecurite"))

    decision = _decision(advisor, _offer(contract_type="stage", duration_months=6))

    assert decision.selection.slug == "cybersecurite-stage"
    assert decision.selection.template_name.endswith("__Stage.html")
    assert decision.selection.adapted_for_stage is False
    assert decision.base_slug == "cybersecurite"


def test_stage_contract_without_a_stage_template_adapts_the_alternance_one() -> None:
    advisor = _SelectingAdvisor(_answer("soc"))

    decision = _decision(advisor, _offer(contract_type="stage", duration_months=4))

    assert decision.selection.slug == "soc"
    assert decision.selection.template_name.endswith("__Alternance.html")
    assert decision.selection.adapted_for_stage is True


@pytest.mark.parametrize("slug", ("grc", "cloudsec", "consultant-it"))
def test_entity_encoded_template_chosen_by_the_model_keeps_entity_handling(
    slug: str,
) -> None:
    advisor = _SelectingAdvisor(_answer(slug))

    decision = _decision(advisor, _offer())

    assert decision.selection.slug == slug
    assert decision.selection.entity_encoded is True


def test_a_slug_with_no_template_file_falls_back_instead_of_failing(
    tmp_path: Path,
) -> None:
    """Template existence is mechanical: never let it break a generation."""

    only_soc = tmp_path / "templates"
    only_soc.mkdir()
    keyword_template = pick_variant(
        _offer().description, title=_offer().title
    ).template_name
    (only_soc / keyword_template).write_text("<html></html>", encoding="utf-8")
    advisor = _SelectingAdvisor(_answer("qa-testing"))

    decision = resolve_variant(
        advisor,
        offer=_offer(),
        application_id=1,
        template_root=only_soc,
    )

    assert decision.chosen_by == "keywords"
    assert decision.selection.template_name == keyword_template
    assert "no template file" in decision.fallback_reason


# ----- failure modes never block generation -----


def test_advisor_without_selection_capability_keeps_the_keyword_pick() -> None:
    class _LegacyAdvisor:
        accepts_correction = True

        def advise(self, offer, selection, template, *, correction=None):  # pragma: no cover
            raise AssertionError("not reached")

    decision = _decision(_LegacyAdvisor(), _offer())

    assert decision.chosen_by == "keywords"
    assert decision.selection.slug == "soc"
    assert "does not implement variant selection" in decision.fallback_reason


@pytest.mark.parametrize("status_code", (401, 429))
@respx.mock
def test_provider_error_during_selection_falls_back_without_a_retry_storm(
    db: sqlite3.Connection,
    tmp_path: Path,
    status_code: int,
) -> None:
    application_id = _queued_application(
        db,
        suffix=f"provider-{status_code}",
        title=VILLENEUVE_TITLE,
        description=VILLENEUVE_MISSIONS,
    )
    selection_route = respx.post(OPENAI_URL).respond(
        status_code, json={"error": {"message": "no"}}
    )
    advisor = OpenAITailoringAdvisor(api_key="test-key")
    tailored: list[str] = []

    def advise(offer, selection, template, *, correction=None):
        tailored.append(selection.slug)
        return TailoringPlan.from_mapping(
            _interactive_structured_payload(offer, selection, template),
            offer=offer,
            selection=selection,
        )

    advisor.advise = advise  # type: ignore[method-assign]

    outcome = approve_application(
        db,
        application_id,
        via="test provider error",
        advisor=advisor,
        toolchain=_Toolchain(),
        output_root=tmp_path,
    )

    # One selection attempt, no retry, and the generation still completed.
    assert selection_route.call_count == 1
    assert tailored == ["chef-de-projet-it"]
    assert current_status(db, application_id) == "ready"
    result = outcome.generation
    assert result is not None
    assert result.decision.chosen_by == "keywords"
    assert str(status_code) in result.decision.fallback_reason


# ----- interactive provider -----


def test_interactive_provider_asks_the_human_with_the_keyword_pick_as_default() -> None:
    asked: list[tuple[str, str]] = []

    def prompt(label: str, default: str) -> str:
        asked.append((label, default))
        if label.startswith("CV slug"):
            return "appsec"
        return default

    advisor = InteractiveTailoringAdvisor(prompt=prompt, echo=lambda _: None)

    decision = _decision(advisor, _offer())

    assert decision.chosen_by == "advisor"
    assert decision.selection.slug == "appsec"
    slug_prompt = next(item for item in asked if item[0].startswith("CV slug"))
    # The keyword suggestion is offered, not imposed.
    assert slug_prompt[1] == "soc"
    assert "skip" in slug_prompt[0]


def test_interactive_decline_falls_back_to_the_keyword_pick() -> None:
    advisor = InteractiveTailoringAdvisor(
        prompt=lambda label, default: "skip" if label.startswith("CV slug") else default,
        echo=lambda _: None,
    )

    decision = _decision(advisor, _offer())

    assert decision.chosen_by == "keywords"
    assert decision.selection.slug == "soc"
    assert "declined" in decision.fallback_reason


def test_interactive_selection_is_never_retried_automatically() -> None:
    calls: list[str] = []

    def prompt(label: str, default: str) -> str:
        calls.append(label)
        return "not-a-slug" if label.startswith("CV slug") else default

    advisor = InteractiveTailoringAdvisor(prompt=prompt, echo=lambda _: None)

    decision = _decision(advisor, _offer())

    assert decision.chosen_by == "keywords"
    assert sum(1 for label in calls if label.startswith("CV slug")) == 1
