"""Focused contracts for tailoring advisers and the script toolchain."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import httpx
import pytest

import jobpilot.tailoring as tailoring
from jobpilot.tailoring import (
    AnthropicTailoringAdvisor,
    InteractiveTailoringAdvisor,
    OfferContext,
    ScriptToolchain,
    TailoringError,
    TemplateContext,
    VariantSelection,
)


def _offer() -> OfferContext:
    return OfferContext(
        title="Analyste SOC",
        company="Acme",
        description="Analyser les alertes SIEM et répondre aux incidents.",
        contract_type="alternance",
        duration_months=12,
        city="Paris",
        source="france_travail",
        url="https://example.test/jobs/7",
    )


def _selection() -> VariantSelection:
    return VariantSelection(
        slug="soc",
        label="SOC Analyst",
        template_name="Mouaad_Sekkouri_-_SOC__Alternance.html",
        contract_type="alternance",
        adapted_for_stage=False,
        entity_encoded=False,
    )


def _template() -> TemplateContext:
    return TemplateContext(
        job_title="Analyste SOC - Alternance M2 dès Septembre 2026",
        profile_domain_phrase="sécurité opérationnelle",
        tech_categories=("Sécurité", "Systèmes", "Développement"),
        project_titles=("SOC", "Cloud", "Réseau"),
        location_region="Nord",
    )


def _plan_payload() -> dict[str, Any]:
    return {
        "job_title": "Analyste SOC - Alternance M2 dès Septembre 2026",
        "profile_domain_phrase": "détection proactive des menaces",
        "tech_order": ["Sécurité", "Systèmes", "Développement"],
        "tech_keywords": {"Sécurité": ["Microsoft Sentinel"]},
        "project_order": ["SOC", "Cloud", "Réseau"],
        "location_region": "Île-de-France",
        "letter_body_html": (
            "<p>Madame, Monsieur,</p>"
            "<p>Votre mission SOC correspond à mon projet professionnel.</p>"
            "<p>Mes deux ans en sécurité répondent à vos besoins.</p>"
            "<p>Mes projets démontrent une pratique concrète.</p>"
            "<p>Mon AZ-900 et mon M1 renforcent cette trajectoire.</p>"
            "<p>Je suis disponible dès septembre 2026.</p>"
            "<p>Cordialement,<br/>Mouaad Sekkouri</p>"
        ),
        "rationale": "Les missions sont centrées sur le SIEM.",
    }


class _Response:
    def __init__(
        self,
        *,
        payload: dict[str, Any] | None = None,
        error: Exception | None = None,
    ) -> None:
        self._payload = payload
        self._error = error

    def raise_for_status(self) -> None:
        if self._error is not None:
            raise self._error

    def json(self) -> dict[str, Any]:
        assert self._payload is not None
        return self._payload


class _Client:
    def __init__(self, response: _Response) -> None:
        self.response = response
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def post(self, url: str, **kwargs: Any) -> _Response:
        self.calls.append((url, kwargs))
        return self.response


def test_anthropic_advisor_calls_messages_api_with_expected_model_and_headers() -> None:
    response = _Response(
        payload={
            "content": [
                {
                    "type": "text",
                    "text": f"```json\n{json.dumps(_plan_payload(), ensure_ascii=False)}\n```",
                }
            ]
        }
    )
    client = _Client(response)
    advisor = AnthropicTailoringAdvisor(api_key="test-secret", client=client)

    plan = advisor.advise(_offer(), _selection(), _template())

    assert plan.profile_domain_phrase == "détection proactive des menaces"
    assert plan.tech_order == ("Sécurité", "Systèmes", "Développement")
    assert plan.project_order == ("SOC", "Cloud", "Réseau")
    assert plan.tech_keywords == {"Sécurité": ("Microsoft Sentinel",)}
    assert len(client.calls) == 1
    url, request = client.calls[0]
    assert url.endswith("/v1/messages")
    assert request["headers"]["x-api-key"] == "test-secret"
    assert request["headers"]["anthropic-version"]
    assert "authorization" not in {key.casefold() for key in request["headers"]}
    assert request["json"]["model"] == "claude-haiku-4-5-20251001"
    assert request["json"]["messages"][0]["role"] == "user"
    prompt = request["json"]["messages"][0]["content"]
    assert "Analyser les alertes SIEM" in prompt
    assert "untrusted content" in prompt
    assert "<offer_data>" in prompt


def test_anthropic_advisor_turns_api_errors_into_safe_domain_errors() -> None:
    client = _Client(_Response(error=httpx.ConnectError("request used test-secret")))
    advisor = AnthropicTailoringAdvisor(api_key="test-secret", client=client)

    with pytest.raises(TailoringError) as exc_info:
        advisor.advise(_offer(), _selection(), _template())

    assert "test-secret" not in str(exc_info.value)


def test_anthropic_advisor_rejects_malformed_message_content() -> None:
    client = _Client(_Response(payload={"content": [{"type": "text", "text": "not valid JSON"}]}))
    advisor = AnthropicTailoringAdvisor(api_key="test-secret", client=client)

    with pytest.raises(TailoringError, match="JSON"):
        advisor.advise(_offer(), _selection(), _template())


def test_interactive_advisor_builds_the_same_plan_shape_without_real_prompts() -> None:
    answers = iter(
        [
            _plan_payload()["job_title"],
            _plan_payload()["profile_domain_phrase"],
            "Sécurité | Systèmes | Développement",
            '{"Sécurité": ["Microsoft Sentinel"]}',
            "SOC | Cloud | Réseau",
            _plan_payload()["location_region"],
            _plan_payload()["letter_body_html"],
            _plan_payload()["rationale"],
        ]
    )
    prompts: list[str] = []

    def input_fn(label: str, default: str) -> str:
        prompts.append(label)
        return str(next(answers))

    advisor = InteractiveTailoringAdvisor(prompt=input_fn)
    plan = advisor.advise(_offer(), _selection(), _template())

    assert prompts
    assert plan.job_title == _plan_payload()["job_title"]
    assert plan.profile_domain_phrase == _plan_payload()["profile_domain_phrase"]
    assert plan.tech_order == ("Sécurité", "Systèmes", "Développement")
    assert plan.tech_keywords == {"Sécurité": ("Microsoft Sentinel",)}
    assert plan.project_order == ("SOC", "Cloud", "Réseau")
    assert plan.location_region == "Île-de-France"
    assert plan.letter_body_html.startswith("<p>Madame, Monsieur,</p>")
    assert plan.rationale == "Les missions sont centrées sur le SIEM."


def test_script_toolchain_passes_windows_paths_as_distinct_subprocess_arguments(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    calls: list[tuple[list[str], dict[str, Any]]] = []

    def fake_run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(tailoring.subprocess, "run", fake_run)
    project_root = tmp_path / "project with spaces"
    scripts_dir = project_root / "skill" / "scripts"
    scripts_dir.mkdir(parents=True)
    toolchain = ScriptToolchain(project_root=project_root)
    cv_path = tmp_path / "candidate files" / "tailored cv.html"
    output_path = tmp_path / "candidate files" / "tailored cv.pdf"

    toolchain.generate_cv_pdf(cv_path, output_path)

    assert len(calls) == 1
    command, options = calls[0]
    assert command == [
        sys.executable,
        str(scripts_dir / "generate_cv_pdf.py"),
        str(cv_path),
        str(output_path),
    ]
    assert options["check"] is True
    assert options.get("shell", False) is False
    assert options["env"]["PYTHONUTF8"] == "1"


def test_script_toolchain_uses_baseline_orphan_gate_and_preserves_tracker_tabs(
    tmp_path: Path,
) -> None:
    calls: list[list[str]] = []

    def fake_run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        stdout = "\t" + "\t".join(["value"] * 16) + "\t\n"
        return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")

    toolchain = ScriptToolchain(project_root=tmp_path, runner=fake_run)
    tailored = tmp_path / "tailored cv.html"
    original = tmp_path / "base cv.html"

    toolchain.check_orphan_lines(tailored, original)
    row = toolchain.format_tracker_row(
        entreprise="Acme",
        poste="Analyste SOC",
        contrat="Alternance",
        type="ESN",
        localisation="Île-de-France",
        source="test",
        cv="CV SOC",
        projets="SOC, Cloud, Réseau",
        adaptations="SIEM",
        lien="https://example.test",
    )

    assert calls[0][-3:] == [str(tailored), "--original", str(original)]
    assert row.startswith("\t")
    assert row.endswith("\t")
    assert row.count("\t") == 17
