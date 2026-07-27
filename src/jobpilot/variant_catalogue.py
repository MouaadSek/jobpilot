"""The CV catalogue offered to the advisor when it selects a variant.

The selection criteria are not restated here: they are parsed out of
``skill/SKILL.md``'s "Step 1 -- CV Selection" table and its shortcut list, which
remain the source of truth. Slugs and labels come from ``config/variants.yaml``.
Paraphrasing either into new prose would let the skill and the pipeline drift
apart silently, so this module reads both and fails loudly when they disagree.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

from jobpilot.config import PROJECT_ROOT

DEFAULT_SKILL_PATH = PROJECT_ROOT / "skill" / "SKILL.md"
DEFAULT_VARIANTS_PATH = PROJECT_ROOT / "config" / "variants.yaml"

#: SKILL.md names CVs by their human label; variants.yaml names them by slug.
#: This is the only hand-maintained link between the two, and every entry is
#: verified against both files each time the catalogue loads.
_SKILL_LABEL_SLUGS: dict[str, str] = {
    "SOC": "soc",
    "Pentest": "pentest",
    "GRC": "grc",
    "IAM": "iam",
    "AppSec": "appsec",
    "CloudSec": "cloudsec",
    "DevSecOps": "devsecops",
    "Chef de Projet IT": "chef-de-projet-it",
    "Consultant IT": "consultant-it",
    "Infra/Cloud": "infra-cloud",
    "Reseaux": "reseaux-telecoms",
    "Backend Dev": "backend-dev",
    "Fullstack Dev": "fullstack-dev",
    "DevOps/SRE": "devops-sre",
    "Support IT": "support-it",
    "Data/BI": "data-bi",
    "IA/ML": "ia-ml",
    "QA Testing": "qa-testing",
    "Cybersecurite": "cybersecurite",
}

_SELECTION_HEADING = "## Step 1 -- CV Selection"
_SHORTCUTS_HEADING = "### Shortcuts and traps"
_TABLE_ROW_RE = re.compile(r"^\|(?P<criteria>[^|]+)\|(?P<label>[^|]+)\|\s*$")
_BULLET_RE = re.compile(r"^-\s+(?P<text>.+?)\s*$")


class VariantCatalogueError(RuntimeError):
    """Raised when SKILL.md and config/variants.yaml no longer line up."""


@dataclass(frozen=True, slots=True)
class CatalogueEntry:
    """One selectable CV, with the criteria SKILL.md states for it."""

    slug: str
    label: str
    criteria: str


@dataclass(frozen=True, slots=True)
class VariantCatalogue:
    """Everything the model needs to choose a variant, and nothing else."""

    entries: tuple[CatalogueEntry, ...]
    shortcuts: tuple[str, ...]

    @property
    def slugs(self) -> frozenset[str]:
        return frozenset(entry.slug for entry in self.entries)

    def label_for(self, slug: str) -> str:
        for entry in self.entries:
            if entry.slug == slug:
                return entry.label
        raise KeyError(slug)

    def as_prompt_block(self) -> str:
        """Render the catalogue for a prompt, criteria verbatim from SKILL.md."""

        lines = [f"- {entry.slug} ({entry.label}): {entry.criteria}" for entry in self.entries]
        if self.shortcuts:
            lines.append("")
            lines.append("Shortcuts and traps (apply with judgement, not mechanically):")
            lines.extend(f"- {shortcut}" for shortcut in self.shortcuts)
        return "\n".join(lines)


def _selection_section(text: str) -> str:
    start = text.find(_SELECTION_HEADING)
    if start == -1:
        raise VariantCatalogueError(
            f"SKILL.md has no '{_SELECTION_HEADING}' section to read criteria from"
        )
    end = text.find("\n## ", start + len(_SELECTION_HEADING))
    return text[start:] if end == -1 else text[start:end]


def _parse_criteria(section: str) -> dict[str, str]:
    """Read the two-column selection table, skipping its header and separator."""

    criteria: dict[str, str] = {}
    for line in section.splitlines():
        match = _TABLE_ROW_RE.match(line.strip())
        if match is None:
            continue
        label = match.group("label").strip()
        text = match.group("criteria").strip()
        if not label or not text or label == "Use CV" or set(text) <= set("-: "):
            continue
        if label in criteria:
            raise VariantCatalogueError(f"SKILL.md lists '{label}' twice in the table")
        criteria[label] = text
    if not criteria:
        raise VariantCatalogueError("SKILL.md's CV-selection table produced no rows")
    return criteria


def _parse_shortcuts(section: str) -> tuple[str, ...]:
    start = section.find(_SHORTCUTS_HEADING)
    if start == -1:
        return ()
    block = section[start + len(_SHORTCUTS_HEADING) :]
    end = block.find("\n### ")
    if end != -1:
        block = block[:end]
    shortcuts: list[str] = []
    for line in block.splitlines():
        match = _BULLET_RE.match(line.strip())
        if match is not None:
            # Markdown emphasis is presentation, not content.
            shortcuts.append(match.group("text").replace("**", ""))
    return tuple(shortcuts)


def _variant_labels(path: Path) -> dict[str, str]:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except OSError as exc:
        raise VariantCatalogueError(f"could not read variants file: {path}") from exc
    except yaml.YAMLError as exc:
        raise VariantCatalogueError(f"variants file is invalid YAML: {exc}") from exc
    entries = raw.get("variants") if isinstance(raw, dict) else None
    if not isinstance(entries, list) or not entries:
        raise VariantCatalogueError(f"{path} defines no variants")
    labels: dict[str, str] = {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise VariantCatalogueError(f"variants[{index}] must be an object")
        slug = entry.get("slug")
        label = entry.get("label")
        if not isinstance(slug, str) or not slug.strip():
            raise VariantCatalogueError(f"variants[{index}].slug must be non-empty text")
        if not isinstance(label, str) or not label.strip():
            raise VariantCatalogueError(f"variants[{index}].label must be non-empty text")
        labels[slug.strip()] = label.strip()
    return labels


def load_variant_catalogue(
    *,
    skill_path: Path | None = None,
    variants_path: Path | None = None,
) -> VariantCatalogue:
    """Build the catalogue from SKILL.md plus config/variants.yaml."""

    skill = Path(skill_path or DEFAULT_SKILL_PATH)
    try:
        skill_text = skill.read_text(encoding="utf-8")
    except OSError as exc:
        raise VariantCatalogueError(f"could not read skill file: {skill}") from exc

    section = _selection_section(skill_text)
    criteria = _parse_criteria(section)
    shortcuts = _parse_shortcuts(section)
    labels = _variant_labels(Path(variants_path or DEFAULT_VARIANTS_PATH))

    unknown = sorted(set(criteria) - set(_SKILL_LABEL_SLUGS))
    if unknown:
        raise VariantCatalogueError(
            "SKILL.md's selection table names CVs with no known slug: "
            f"{unknown}. Update _SKILL_LABEL_SLUGS."
        )

    entries: list[CatalogueEntry] = []
    missing: list[str] = []
    for label, slug in _SKILL_LABEL_SLUGS.items():
        if slug not in labels:
            missing.append(slug)
            continue
        if label not in criteria:
            raise VariantCatalogueError(
                f"SKILL.md's selection table no longer states criteria for '{label}'"
            )
        entries.append(
            CatalogueEntry(slug=slug, label=labels[slug], criteria=criteria[label])
        )
    if missing:
        raise VariantCatalogueError(
            f"config/variants.yaml is missing slugs referenced by SKILL.md: {missing}"
        )
    return VariantCatalogue(entries=tuple(entries), shortcuts=shortcuts)


@lru_cache(maxsize=1)
def default_catalogue() -> VariantCatalogue:
    """The committed catalogue, parsed once per process."""

    return load_variant_catalogue()
