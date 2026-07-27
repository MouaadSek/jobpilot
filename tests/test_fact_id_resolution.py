"""Citation ids are matched tolerantly; what may be claimed is unchanged."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import pytest

from jobpilot.config import PROJECT_ROOT
from jobpilot.facts import load_fact_bank
from jobpilot.tailoring import (
    AmbiguousFactIdError,
    OfferContext,
    SourcedBullet,
    TailoringError,
    TailoringPlan,
    UnknownFactIdError,
    _advise_and_tailor,
    extract_template_context,
    pick_variant,
    resolve_fact_id,
    tailor_cv_html,
    validate_provenance,
)
from tests.test_tailoring_provenance import _payload

TEMPLATE_PATH = (
    PROJECT_ROOT
    / "skill"
    / "assets"
    / "cv-templates"
    / "Mouaad_Sekkouri_-_SOC__Alternance.html"
)

# Two facts whose ids differ only by their section prefix, so a prefix-less
# citation cannot be resolved to one of them.
AMBIGUOUS_BANK = """
version: 1
source_documents: ["skill/SKILL.md"]
source_templates: ["Mouaad_Sekkouri_-_SOC__Alternance.html"]
experience:
  - id: experience.concentrix
    employer: Concentrix
    role: Support
    dates: 2021 - 2023
    location: Lille
    facts:
      - id: experience.concentrix.incidents
        text: 1500 incidents traités
projects:
  - id: project.lab
    title: Lab SIEM
    stack: ["Wazuh"]
    source_templates: ["Mouaad_Sekkouri_-_SOC__Alternance.html"]
    facts:
      - id: project.foo.bar
        text: Règles de détection sur 12 cas d'usage
education:
  - id: education.supinfo
    diploma: M1 Cybersécurité
    institution: Supinfo
    dates: 2025 - 2026
    location: Lille
certifications:
  - id: certification.az900
    name: AZ-900
    obtained: "2025"
languages:
  - id: language.english
    name: Anglais
    level: C1 Courant
skills:
  - id: skill.foo.bar
    name: Foo Bar
    verified: true
locked:
  name: Mouaad Sekkouri
  email: mouaadsekkourii@gmail.com
  phone: "+33 7 51 13 54 25"
  linkedin: linkedin.com/in/sekkouri
  diplomas: ["M1 Cybersécurité"]
  employer_names: ["Concentrix"]
  certification_names: ["AZ-900"]
  dates: ["2021 - 2023"]
"""


@pytest.fixture
def bank():
    return load_fact_bank()


@pytest.fixture
def ambiguous_bank(tmp_path: Path):
    path = tmp_path / "fact_bank.yaml"
    path.write_text(AMBIGUOUS_BANK, encoding="utf-8")
    return load_fact_bank(path)


def _offer() -> OfferContext:
    return OfferContext(
        title="Analyste SOC (H/F) - Paris",
        company="Acme",
        description="Analyser les alertes SIEM et répondre aux incidents dès septembre 2026.",
        contract_type="alternance",
        duration_months=12,
        city="Paris",
        source="france_travail",
        url="https://example.test/jobs/25",
    )


def _tailor(payload: dict[str, Any]) -> str:
    original = TEMPLATE_PATH.read_text(encoding="utf-8")
    offer = _offer()
    selection = pick_variant(offer.description, title=offer.title)
    return tailor_cv_html(
        original,
        TailoringPlan.from_mapping(payload, offer=offer, selection=selection),
        selection,
        offer_description=offer.description,
        offer=offer,
    )


# ----- the slip this task exists for -----


def test_a_prefix_less_skill_id_resolves_to_the_real_fact(bank) -> None:
    """The reported failure: 'unknown skill fact id: azure.sentinel'."""

    assert resolve_fact_id("azure.sentinel", bank) == "skill.azure.sentinel"


@pytest.mark.parametrize(
    ("cited", "expected"),
    (
        ("skill.azure.sentinel", "skill.azure.sentinel"),  # already canonical
        ("azure.sentinel", "skill.azure.sentinel"),  # missing section prefix
        ("skill.azure_sentinel", "skill.azure.sentinel"),  # underscores
        ("Skill.Azure-Sentinel", "skill.azure.sentinel"),  # case and hyphens
        ("concentrix.incidents", "experience.concentrix.incidents"),
        ("french", "language.french"),
        ("supinfo.m1_cybersecurity", "education.supinfo.m1_cybersecurity"),
    ),
)
def test_separator_and_prefix_variants_resolve_to_one_fact(
    bank,
    cited: str,
    expected: str,
) -> None:
    assert resolve_fact_id(cited, bank) == expected


def test_a_generation_survives_a_prefix_less_skill_citation() -> None:
    payload = copy.deepcopy(_payload())
    payload["skill_order"] = ["wazuh", "python"]

    tailored = _tailor(payload)

    assert tailored  # the run completed instead of failing on the citation format


def test_normalisation_is_logged_with_both_forms(
    bank,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level("DEBUG", logger="jobpilot.tailoring"):
        resolve_fact_id("azure.sentinel", bank)

    logged = "\n".join(record.getMessage() for record in caplog.records)
    assert "normalised fact id citation" in logged
    assert "azure.sentinel" in logged
    assert "skill.azure.sentinel" in logged


# ----- tolerance is not relaxation -----


def test_an_ambiguous_short_id_is_rejected_rather_than_guessed(ambiguous_bank) -> None:
    with pytest.raises(AmbiguousFactIdError) as caught:
        resolve_fact_id("foo.bar", ambiguous_bank)

    assert set(caught.value.candidates) == {"skill.foo.bar", "project.foo.bar"}


def test_a_section_hint_disambiguates_without_widening_the_search(
    ambiguous_bank,
) -> None:
    """skill_order can only mean a skill, so its own prefix settles the match."""

    assert resolve_fact_id("foo.bar", ambiguous_bank, section_hint="skills") == (
        "skill.foo.bar"
    )


def test_a_genuinely_unknown_id_stays_an_error(bank) -> None:
    with pytest.raises(UnknownFactIdError, match="unknown fact id"):
        resolve_fact_id("skill.quantum.cryptanalysis", bank)


@pytest.mark.parametrize(
    "cited",
    (
        "Azure AD/Entra ID",  # a skill's name, not its id (skill.azure.ad.entra.id)
        "analyse de vulnérabilités",  # accented name vs unaccented id
        "1500 incidents traités",  # a fact's text
    ),
)
def test_a_citation_matching_a_name_or_text_but_no_id_is_rejected(
    bank,
    cited: str,
) -> None:
    """Resembling what a fact is about is not evidence the model read that fact."""

    with pytest.raises(TailoringError):
        resolve_fact_id(cited, bank)


def test_provenance_still_rejects_a_fabricated_number_on_a_normalised_citation(
    bank,
) -> None:
    bullet = SourcedBullet(
        text="Résolution de 9 000 incidents au premier contact.",
        sources=("experience.concentrix.incidents",),
    )
    assert resolve_fact_id("concentrix.incidents", bank) == bullet.sources[0]

    with pytest.raises(TailoringError, match="unsupported number '9 000'"):
        validate_provenance([bullet], bank)


def test_provenance_still_rejects_a_fabricated_tool_through_the_full_path() -> None:
    payload = copy.deepcopy(_payload())
    payload["skill_order"] = ["wazuh", "python"]
    payload["experience_content"][1]["bullets"][0]["text"] = (
        "Résolution de 1 500+ incidents avec 85 % de résolution au premier "
        "contact via Splunk."
    )

    with pytest.raises(TailoringError, match="Splunk"):
        _tailor(payload)


# ----- the retry is told which ids exist -----


class _RecordingAdvisor:
    """Cites a prefix-less unknown id first, then whatever the retry was told."""

    accepts_correction = True

    def __init__(self, first_skill: str, second_skill: str) -> None:
        self.skills = [first_skill, second_skill]
        self.corrections: list[str | None] = []

    def advise(self, offer, selection, template, *, correction: str | None = None):
        payload = copy.deepcopy(_payload())
        payload["skill_order"] = [self.skills[min(len(self.corrections), 1)], "skill.python"]
        self.corrections.append(correction)
        return TailoringPlan.from_mapping(payload, offer=offer, selection=selection)


def _advise(advisor: Any) -> None:
    offer = _offer()
    selection = pick_variant(offer.description, title=offer.title)
    original = TEMPLATE_PATH.read_text(encoding="utf-8")
    _advise_and_tailor(
        advisor,
        offer=offer,
        selection=selection,
        template_context=extract_template_context(original),
        original_html=original,
        bank=load_fact_bank(),
        application_id=1,
    )


def test_the_correction_block_lists_the_valid_ids_for_that_section() -> None:
    advisor = _RecordingAdvisor("skill.quantum.cryptanalysis", "skill.wazuh")

    _advise(advisor)

    assert advisor.corrections[0] is None
    correction = advisor.corrections[1]
    assert 'section="skills"' in correction
    assert "skill.wazuh" in correction
    assert "unknown fact id" in correction
    # Ids only: the retry does not need the texts repeated back at it.
    assert "1500 incidents" not in correction
    # And the list is a labelled machine message, not offer-supplied instructions.
    assert "machine message" in correction


class _BadSourceAdvisor:
    """Cites an unresolvable id in a letter paragraph, where no section is implied."""

    accepts_correction = True

    def __init__(self) -> None:
        self.corrections: list[str | None] = []

    def advise(self, offer, selection, template, *, correction: str | None = None):
        payload = copy.deepcopy(_payload())
        if not self.corrections:
            payload["letter_paragraphs"][0]["sources"] = ["nowhere.at.all"]
        self.corrections.append(correction)
        return TailoringPlan.from_mapping(payload, offer=offer, selection=selection)


def test_an_unknown_id_without_a_prefix_gets_every_section_listed() -> None:
    """A retry told nothing about the legal ids just repeats the same slip."""

    advisor = _BadSourceAdvisor()

    _advise(advisor)

    correction = advisor.corrections[1]
    assert "nowhere.at.all" in correction
    for section in ("skills", "experience", "projects", "languages"):
        assert f'section="{section}"' in correction


def test_the_offered_id_list_is_scoped_to_this_generation() -> None:
    """Feeding back the whole bank would invite citing facts never shown."""

    advisor = _RecordingAdvisor("skill.quantum.cryptanalysis", "skill.wazuh")

    _advise(advisor)

    correction = advisor.corrections[1]
    offered = correction.split('<valid_fact_ids section="skills">')[1]
    offered = offered.split("</valid_fact_ids>")[0].split()
    bank = load_fact_bank()
    assert offered  # non-empty
    assert len(offered) < len([s for s in bank.skills if s.verified])
    assert all(fact_id.startswith("skill.") for fact_id in offered)
