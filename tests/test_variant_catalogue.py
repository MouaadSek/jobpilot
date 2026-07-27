"""The catalogue is derived from SKILL.md, never paraphrased beside it."""

from __future__ import annotations

from pathlib import Path

import pytest

from jobpilot.config import PROJECT_ROOT
from jobpilot.tailoring import _TEMPLATES
from jobpilot.variant_catalogue import (
    VariantCatalogueError,
    default_catalogue,
    load_variant_catalogue,
)

SKILL_PATH = PROJECT_ROOT / "skill" / "SKILL.md"
VARIANTS_PATH = PROJECT_ROOT / "config" / "variants.yaml"


def test_every_selectable_template_is_offered_with_criteria() -> None:
    catalogue = default_catalogue()

    # The 19 base variants; stage templates are a mechanical mapping, not a choice.
    assert catalogue.slugs == frozenset(_TEMPLATES)
    assert all(entry.criteria.strip() for entry in catalogue.entries)
    assert all(entry.label.strip() for entry in catalogue.entries)


def test_criteria_are_copied_verbatim_from_the_skill_selection_table() -> None:
    """If this drifts, the pipeline and the skill are choosing by different rules."""

    skill_text = SKILL_PATH.read_text(encoding="utf-8")
    catalogue = default_catalogue()

    for entry in catalogue.entries:
        assert f"| {entry.criteria} |" in skill_text

    by_slug = {entry.slug: entry for entry in catalogue.entries}
    assert by_slug["soc"].criteria == "SOC, SIEM, detection, incident response, blue team"
    assert by_slug["chef-de-projet-it"].criteria == "Project management + IT/cyber context"


def test_shortcuts_are_carried_over_as_judgement_not_as_triggers() -> None:
    catalogue = default_catalogue()

    joined = " ".join(catalogue.shortcuts)
    assert "Consultant" in joined
    assert "PM tasks" in joined
    assert "**" not in joined  # markdown emphasis is stripped
    block = catalogue.as_prompt_block()
    assert "apply with judgement, not mechanically" in block


def test_missing_selection_table_is_a_loud_failure(tmp_path: Path) -> None:
    skill = tmp_path / "SKILL.md"
    skill.write_text("# Skill\n\nNo selection section here.\n", encoding="utf-8")

    with pytest.raises(VariantCatalogueError, match="Step 1"):
        load_variant_catalogue(skill_path=skill, variants_path=VARIANTS_PATH)


def test_a_variant_dropped_from_config_is_reported_not_silently_skipped(
    tmp_path: Path,
) -> None:
    variants = tmp_path / "variants.yaml"
    variants.write_text(
        "variants:\n  - slug: soc\n    label: SOC Analyst\n",
        encoding="utf-8",
    )

    with pytest.raises(VariantCatalogueError, match="missing slugs"):
        load_variant_catalogue(skill_path=SKILL_PATH, variants_path=variants)


def test_an_unmapped_cv_label_in_the_skill_is_reported(tmp_path: Path) -> None:
    skill = tmp_path / "SKILL.md"
    skill.write_text(
        "## Step 1 -- CV Selection\n\n"
        "| If missions focus on... | Use CV |\n"
        "|---|---|\n"
        "| Quantum cryptanalysis | Quantum |\n",
        encoding="utf-8",
    )

    with pytest.raises(VariantCatalogueError, match="no known slug"):
        load_variant_catalogue(skill_path=skill, variants_path=VARIANTS_PATH)
