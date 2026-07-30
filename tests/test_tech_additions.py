"""Zone 3 may add a keyword, but only one he has and the offer asked for."""

from __future__ import annotations

import copy
import re

import pytest

from jobpilot.facts import load_fact_bank
from jobpilot.tailoring import (
    OfferContext,
    TailoringError,
    TailoringPlan,
    _row_budget,
    pick_variant,
    tailor_cv_html,
)
from tests.test_fact_id_resolution import TEMPLATE_PATH
from tests.test_tailoring_provenance import _payload

TEMPLATE = TEMPLATE_PATH.read_text(encoding="utf-8")
#: A row with room to spare in the SOC template.
ROOMY_CATEGORY = "SIEM & Détection"
#: The widest row in that template, so anything added to it overflows.
FULL_CATEGORY = "Cloud & Virtualisation"


@pytest.fixture
def bank():
    return load_fact_bank()


def _offer(description: str) -> OfferContext:
    return OfferContext(
        title="Analyste SOC (H/F) - Paris",
        company="Acme",
        description=description,
        contract_type="alternance",
        duration_months=12,
        city="Paris",
        source="france_travail",
        url="https://example.test/jobs/32",
    )


def _render(payload: dict, description: str) -> str:
    offer = _offer(description)
    selection = pick_variant(offer.description, title=offer.title)
    return tailor_cv_html(
        TEMPLATE,
        TailoringPlan.from_mapping(payload, offer=offer, selection=selection),
        selection,
        offer_description=offer.description,
        offer=offer,
    )


def _row(source: str, category: str) -> str:
    """The rendered skill list of one row, as plain text.

    Categories carry HTML entities in some templates ("SIEM &amp; Détection"),
    so the lookup compares decoded text rather than raw markup.
    """

    import html as html_module

    def plain(value: str) -> str:
        return html_module.unescape(re.sub(r"<[^>]+>", "", value)).strip()

    for match in re.finditer(
        r'<div class="tech-category">(.*?)</div>\s*<div class="tech-list">(.*?)</div>',
        source,
        re.DOTALL,
    ):
        if plain(match.group(1)) == category:
            return plain(match.group(2))
    raise AssertionError(f"row {category} not found")


def _with(additions: dict[str, list[str]]) -> dict:
    payload = copy.deepcopy(_payload())
    payload["tech_additions"] = additions
    return payload


SOC_OFFER = (
    "Analyser les alertes SIEM et répondre aux incidents dès septembre 2026. "
    "Vous travaillerez avec Grafana pour le suivi et Ansible pour l'automatisation."
)


# ----- the permission -----


def test_a_verified_skill_named_by_the_offer_is_inserted() -> None:
    tailored = _render(_with({ROOMY_CATEGORY: ["Grafana"]}), SOC_OFFER)

    row = _row(tailored, ROOMY_CATEGORY)
    assert row.endswith(", Grafana")
    assert "ELK Stack" in row  # the template's own values are untouched


def test_two_keywords_may_be_added() -> None:
    tailored = _render(
        _with({ROOMY_CATEGORY: ["Grafana"], "Scripting": ["Ansible"]}),
        SOC_OFFER,
    )

    assert "Grafana" in _row(tailored, ROOMY_CATEGORY)
    assert "Ansible" in _row(tailored, "Scripting")


def test_no_additions_leaves_the_grid_exactly_as_it_was() -> None:
    """Reorder-only remains the default and the common case."""

    tailored = _render(copy.deepcopy(_payload()), SOC_OFFER)

    def tools(source: str) -> set[str]:
        return {
            value.strip()
            for row in re.findall(r'<div class="tech-list">(.*?)</div>', source, re.DOTALL)
            for value in re.sub(r"<[^>]+>", "", row).split(",")
            if value.strip()
        }

    assert tools(tailored) == tools(TEMPLATE)


# ----- both halves of the rule -----


def test_a_verified_skill_the_offer_never_mentions_is_rejected() -> None:
    """Genuinely his, but padding: the offer did not ask for it."""

    with pytest.raises(TailoringError, match="does not appear in the offer: Terraform"):
        _render(_with({ROOMY_CATEGORY: ["Terraform"]}), SOC_OFFER)


def test_a_skill_absent_from_the_bank_is_rejected() -> None:
    offer = SOC_OFFER + " La stack repose sur CrowdStrike."

    with pytest.raises(TailoringError, match="not a verified skill.*CrowdStrike"):
        _render(_with({ROOMY_CATEGORY: ["CrowdStrike"]}), offer)


def test_an_unverified_skill_is_rejected(bank) -> None:
    """Presence in the bank is necessary, never sufficient."""

    import dataclasses

    from jobpilot.facts import SkillFact

    unverified = SkillFact(id="skill.qradar", name="QRadar", verified=False)
    widened = dataclasses.replace(bank, skills=bank.skills + (unverified,))
    offer = SOC_OFFER + " Le SIEM QRadar est en place."
    selection = pick_variant(offer, title="Analyste SOC (H/F) - Paris")

    with pytest.raises(TailoringError, match="not a verified skill.*QRadar"):
        tailor_cv_html(
            TEMPLATE,
            TailoringPlan.from_mapping(
                _with({ROOMY_CATEGORY: ["QRadar"]}),
                offer=_offer(offer),
                selection=selection,
            ),
            selection,
            offer_description=offer,
            fact_bank=widened,
            offer=_offer(offer),
        )


def test_a_third_keyword_is_rejected() -> None:
    offer = SOC_OFFER + " Nous utilisons aussi Jenkins."

    with pytest.raises(TailoringError, match="at most 2 offer keywords"):
        _render(
            _with(
                {
                    ROOMY_CATEGORY: ["Grafana"],
                    "Scripting": ["Ansible"],
                    "Systèmes & Réseaux": ["Jenkins"],
                }
            ),
            offer,
        )


def test_a_category_absent_from_the_template_is_rejected() -> None:
    with pytest.raises(TailoringError, match="unknown tech category"):
        _render(_with({"Quantique": ["Grafana"]}), SOC_OFFER)


# ----- the line budget -----


def test_the_budget_is_the_templates_own_widest_row() -> None:
    """Derived from the file, not a magic number."""

    assert _row_budget(TEMPLATE) == len(_row(TEMPLATE, FULL_CATEGORY))


def test_a_keyword_that_would_overflow_its_row_is_dropped_not_fatal(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """One page matters more than one keyword; the CV is still true without it."""

    before = _row(TEMPLATE, FULL_CATEGORY)

    with caplog.at_level("DEBUG", logger="jobpilot.tailoring"):
        tailored = _render(_with({FULL_CATEGORY: ["Grafana"]}), SOC_OFFER)

    assert _row(tailored, FULL_CATEGORY) == before
    assert "dropped tech keyword 'Grafana'" in caplog.text
    assert "widest row" in caplog.text


def test_a_keyword_already_in_the_grid_is_a_no_op() -> None:
    """Wazuh is already listed; adding it must not duplicate the tool."""

    offer = SOC_OFFER + " Vous exploitez Wazuh au quotidien."

    tailored = _render(_with({"Systèmes & Réseaux": ["Wazuh"]}), offer)

    assert _row(tailored, "Systèmes & Réseaux") == _row(TEMPLATE, "Systèmes & Réseaux")
    assert _row(tailored, ROOMY_CATEGORY).count("Wazuh") == 1


# ----- the contract -----


def test_the_prompt_documents_the_permission_and_its_two_conditions() -> None:
    from jobpilot.tailoring import _advisor_prompt, extract_template_context

    offer = _offer(SOC_OFFER)
    prompt = _advisor_prompt(
        offer,
        pick_variant(offer.description, title=offer.title),
        extract_template_context(TEMPLATE),
    )

    assert "tech_additions" in prompt
    assert "at most 2 keywords" in prompt
    assert "verified skill in the fact" in prompt
