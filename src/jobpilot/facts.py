"""Typed, reviewable facts allowed in generated CVs and motivation letters."""

from __future__ import annotations

import html
import re
import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

import yaml

from jobpilot.config import PROJECT_ROOT

DEFAULT_FACT_BANK_PATH = PROJECT_ROOT / "config" / "fact_bank.yaml"


class FactBankError(ValueError):
    """Raised when the committed fact bank is malformed or ambiguous."""


@dataclass(frozen=True, slots=True)
class FactClaim:
    """One atomic statement that generated content may cite."""

    id: str
    text: str
    section: str
    needs_review: bool = False
    verified: bool = True


@dataclass(frozen=True, slots=True)
class ExperienceFact:
    id: str
    employer: str
    role: str
    dates: str
    location: str
    facts: tuple[FactClaim, ...]


@dataclass(frozen=True, slots=True)
class ProjectFact:
    id: str
    title: str
    stack: tuple[str, ...]
    facts: tuple[FactClaim, ...]
    source_templates: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class EducationFact:
    id: str
    diploma: str
    institution: str
    dates: str
    location: str
    needs_review: bool = False


@dataclass(frozen=True, slots=True)
class CertificationFact:
    id: str
    name: str
    obtained: str
    needs_review: bool = False


@dataclass(frozen=True, slots=True)
class LanguageFact:
    id: str
    name: str
    level: str
    needs_review: bool = False


@dataclass(frozen=True, slots=True)
class SkillFact:
    id: str
    name: str
    verified: bool
    needs_review: bool = False


@dataclass(frozen=True, slots=True)
class LockedFacts:
    name: str
    email: str
    phone: str
    linkedin: str
    diplomas: tuple[str, ...]
    employer_names: tuple[str, ...]
    certification_names: tuple[str, ...]
    dates: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class FactBank:
    version: int
    source_documents: tuple[str, ...]
    source_templates: tuple[str, ...]
    experience: tuple[ExperienceFact, ...]
    projects: tuple[ProjectFact, ...]
    education: tuple[EducationFact, ...]
    certifications: tuple[CertificationFact, ...]
    languages: tuple[LanguageFact, ...]
    skills: tuple[SkillFact, ...]
    locked: LockedFacts
    claims: Mapping[str, FactClaim]


def _mapping(value: object, label: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise FactBankError(f"{label} must be an object")
    return value


def _sequence(value: object, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise FactBankError(f"{label} must be a list")
    return value


def _text(data: Mapping[str, Any], key: str, label: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise FactBankError(f"{label}.{key} must be non-empty text")
    return value.strip()


def _boolean(data: Mapping[str, Any], key: str, label: str, *, default: bool) -> bool:
    value = data.get(key, default)
    if not isinstance(value, bool):
        raise FactBankError(f"{label}.{key} must be true or false")
    return value


def _texts(data: Mapping[str, Any], key: str, label: str) -> tuple[str, ...]:
    values = _sequence(data.get(key), f"{label}.{key}")
    if not all(isinstance(value, str) and value.strip() for value in values):
        raise FactBankError(f"{label}.{key} must contain non-empty text")
    return tuple(value.strip() for value in values)


def _claim_list(
    data: Mapping[str, Any],
    *,
    section: str,
    label: str,
) -> tuple[FactClaim, ...]:
    claims: list[FactClaim] = []
    for index, raw in enumerate(_sequence(data.get("facts"), f"{label}.facts")):
        item = _mapping(raw, f"{label}.facts[{index}]")
        claims.append(
            FactClaim(
                id=_text(item, "id", f"{label}.facts[{index}]"),
                text=_text(item, "text", f"{label}.facts[{index}]"),
                section=section,
                needs_review=_boolean(
                    item,
                    "needs_review",
                    f"{label}.facts[{index}]",
                    default=False,
                ),
            )
        )
    if not claims:
        raise FactBankError(f"{label}.facts must not be empty")
    return tuple(claims)


def _entry_claim(
    entry_id: str,
    text: str,
    section: str,
    *,
    needs_review: bool,
    verified: bool = True,
) -> FactClaim:
    return FactClaim(
        id=entry_id,
        text=text,
        section=section,
        needs_review=needs_review,
        verified=verified,
    )


def _reject_orphan_claim_id(entry_id: str, claim_id: str) -> None:
    """Every claim id must extend its own entry id with a dot.

    ``experience.baifall_dream`` held claims named ``experience.baifall.*`` while
    every other entry in the bank followed ``entry.id + "." + slug``. The advisor
    generalised from the majority and emitted an id that did not exist — on the
    one entry the completeness floor forces onto every CV, so it failed on every
    generation, and Task 22c's single retry burned its one attempt re-guessing
    the same way.

    Only experience and projects carry sub-claims; education, certifications,
    languages and skills are leaf facts whose id is the claim id.
    """

    prefix = f"{entry_id}."
    if not claim_id.startswith(prefix):
        raise FactBankError(
            f"claim id {claim_id!r} does not extend its entry id {entry_id!r}: "
            f"every claim under {entry_id!r} must start with {prefix!r}. "
            "Inconsistent ids make the advisor guess, and it guesses the majority."
        )


def load_fact_bank(path: Path | None = None) -> FactBank:
    """Load and strictly validate the committed fact bank."""

    chosen = Path(path or DEFAULT_FACT_BANK_PATH)
    try:
        raw = yaml.safe_load(chosen.read_text(encoding="utf-8"))
    except OSError as exc:
        raise FactBankError(f"could not read fact bank: {chosen}") from exc
    except yaml.YAMLError as exc:
        raise FactBankError(f"fact bank is invalid YAML: {exc}") from exc
    root = _mapping(raw, "fact_bank")
    version = root.get("version")
    if not isinstance(version, int) or version < 1:
        raise FactBankError("fact_bank.version must be a positive integer")
    source_documents = _texts(root, "source_documents", "fact_bank")
    source_templates = _texts(root, "source_templates", "fact_bank")

    experiences: list[ExperienceFact] = []
    for index, raw_entry in enumerate(_sequence(root.get("experience"), "experience")):
        entry = _mapping(raw_entry, f"experience[{index}]")
        experiences.append(
            ExperienceFact(
                id=_text(entry, "id", f"experience[{index}]"),
                employer=_text(entry, "employer", f"experience[{index}]"),
                role=_text(entry, "role", f"experience[{index}]"),
                dates=_text(entry, "dates", f"experience[{index}]"),
                location=_text(entry, "location", f"experience[{index}]"),
                facts=_claim_list(
                    entry,
                    section="experience",
                    label=f"experience[{index}]",
                ),
            )
        )

    projects: list[ProjectFact] = []
    for index, raw_entry in enumerate(_sequence(root.get("projects"), "projects")):
        entry = _mapping(raw_entry, f"projects[{index}]")
        projects.append(
            ProjectFact(
                id=_text(entry, "id", f"projects[{index}]"),
                title=_text(entry, "title", f"projects[{index}]"),
                stack=_texts(entry, "stack", f"projects[{index}]"),
                facts=_claim_list(entry, section="projects", label=f"projects[{index}]"),
                source_templates=_texts(
                    entry,
                    "source_templates",
                    f"projects[{index}]",
                ),
            )
        )

    education: list[EducationFact] = []
    for index, raw_entry in enumerate(_sequence(root.get("education"), "education")):
        entry = _mapping(raw_entry, f"education[{index}]")
        education.append(
            EducationFact(
                id=_text(entry, "id", f"education[{index}]"),
                diploma=_text(entry, "diploma", f"education[{index}]"),
                institution=_text(entry, "institution", f"education[{index}]"),
                dates=_text(entry, "dates", f"education[{index}]"),
                location=_text(entry, "location", f"education[{index}]"),
                needs_review=_boolean(
                    entry,
                    "needs_review",
                    f"education[{index}]",
                    default=False,
                ),
            )
        )

    certifications: list[CertificationFact] = []
    for index, raw_entry in enumerate(
        _sequence(root.get("certifications"), "certifications")
    ):
        entry = _mapping(raw_entry, f"certifications[{index}]")
        certifications.append(
            CertificationFact(
                id=_text(entry, "id", f"certifications[{index}]"),
                name=_text(entry, "name", f"certifications[{index}]"),
                obtained=_text(entry, "obtained", f"certifications[{index}]"),
                needs_review=_boolean(
                    entry,
                    "needs_review",
                    f"certifications[{index}]",
                    default=False,
                ),
            )
        )

    languages: list[LanguageFact] = []
    for index, raw_entry in enumerate(_sequence(root.get("languages"), "languages")):
        entry = _mapping(raw_entry, f"languages[{index}]")
        languages.append(
            LanguageFact(
                id=_text(entry, "id", f"languages[{index}]"),
                name=_text(entry, "name", f"languages[{index}]"),
                level=_text(entry, "level", f"languages[{index}]"),
                needs_review=_boolean(
                    entry,
                    "needs_review",
                    f"languages[{index}]",
                    default=False,
                ),
            )
        )

    skills: list[SkillFact] = []
    for index, raw_entry in enumerate(_sequence(root.get("skills"), "skills")):
        entry = _mapping(raw_entry, f"skills[{index}]")
        skills.append(
            SkillFact(
                id=_text(entry, "id", f"skills[{index}]"),
                name=_text(entry, "name", f"skills[{index}]"),
                verified=_boolean(entry, "verified", f"skills[{index}]", default=False),
                needs_review=_boolean(
                    entry,
                    "needs_review",
                    f"skills[{index}]",
                    default=False,
                ),
            )
        )

    locked_raw = _mapping(root.get("locked"), "locked")
    locked = LockedFacts(
        name=_text(locked_raw, "name", "locked"),
        email=_text(locked_raw, "email", "locked"),
        phone=_text(locked_raw, "phone", "locked"),
        linkedin=_text(locked_raw, "linkedin", "locked"),
        diplomas=_texts(locked_raw, "diplomas", "locked"),
        employer_names=_texts(locked_raw, "employer_names", "locked"),
        certification_names=_texts(locked_raw, "certification_names", "locked"),
        dates=_texts(locked_raw, "dates", "locked"),
    )

    claims: dict[str, FactClaim] = {}

    def register(claim: FactClaim) -> None:
        if claim.id in claims:
            raise FactBankError(f"duplicate fact id: {claim.id}")
        claims[claim.id] = claim

    entry_ids: set[str] = set()
    for entry in (*experiences, *projects):
        if entry.id in entry_ids:
            raise FactBankError(f"duplicate entry id: {entry.id}")
        entry_ids.add(entry.id)
        for claim in entry.facts:
            _reject_orphan_claim_id(entry.id, claim.id)
            register(claim)
    for entry in education:
        register(
            _entry_claim(
                entry.id,
                f"{entry.diploma}, {entry.institution}, {entry.location}, {entry.dates}",
                "education",
                needs_review=entry.needs_review,
            )
        )
    for entry in certifications:
        register(
            _entry_claim(
                entry.id,
                f"{entry.name}, obtenu {entry.obtained}",
                "certifications",
                needs_review=entry.needs_review,
            )
        )
    for entry in languages:
        register(
            _entry_claim(
                entry.id,
                f"{entry.name}: {entry.level}",
                "languages",
                needs_review=entry.needs_review,
            )
        )
    for entry in skills:
        register(
            _entry_claim(
                entry.id,
                entry.name,
                "skills",
                needs_review=entry.needs_review,
                verified=entry.verified,
            )
        )

    return FactBank(
        version=version,
        source_documents=source_documents,
        source_templates=source_templates,
        experience=tuple(experiences),
        projects=tuple(projects),
        education=tuple(education),
        certifications=tuple(certifications),
        languages=tuple(languages),
        skills=tuple(skills),
        locked=locked,
        claims=MappingProxyType(claims),
    )


_GENDER_MARKER_RE = re.compile(
    r"\(\s*(?:h\s*/\s*f(?:\s*/\s*(?:x|nb))?|f\s*/\s*h|m\s*/\s*f(?:\s*/\s*d)?)\s*\)",
    re.IGNORECASE,
)
_REFERENCE_RE = re.compile(
    r"(?:\[\s*(?:réf(?:érence)?\.?\s*)?[A-Z0-9][A-Z0-9._/-]{2,}\s*\]|"
    r"\b(?:réf(?:érence)?\.?|ref|offre\s+n[°o]?)\s*:?\s*[A-Z0-9][A-Z0-9._/-]*\b)",
    re.IGNORECASE,
)
_CONTRACT_NOISE_RE = re.compile(
    r"^(?:(?:alternance|alternant(?:e)?|apprentissage|stage|stagiaire|cdi|cdd)"
    r"\s*(?:[:\-–|]\s*)?)+",
    re.IGNORECASE,
)
_MARKETING_PREFIX_RE = re.compile(
    r"^(?:(?:urgent|nouveau|rejoignez-nous)\s*!?\s*[:\-–]?\s*)+",
    re.IGNORECASE,
)
_LOCATION_SUFFIX_RE = re.compile(
    r"\s*(?:[-–|]\s*|(?:à|a)\s+)"
    r"(?:"
    r"(?:\d{5}\s+)?(?:Paris|Lille|Roubaix|Puteaux|Courbevoie|Lyon|Saint-Denis)"
    r"(?:\s*(?:\(\d{2,5}\)|\d{2,5}|(?:\d{1,2})e))?"
    r"|Île-de-France|Hauts-de-France|Remote(?:\s+France)?"
    r"|Département\s+\d{2,3}|\d{2,5}"
    r")\s*$",
    re.IGNORECASE,
)


def normalise_role_title(raw_title: str) -> str:
    """Remove posting metadata while preserving the actual role wording."""

    title = html.unescape(raw_title)
    title = unicodedata.normalize("NFKC", title).strip()
    title = _REFERENCE_RE.sub(" ", title)
    title = re.sub(r"\[\s*\]", " ", title)
    title = _GENDER_MARKER_RE.sub(" ", title)
    title = re.sub(
        r"\b(?:h\s*/\s*f(?:\s*/\s*(?:x|nb))?|f\s*/\s*h|m\s*/\s*f(?:\s*/\s*d)?)\b",
        " ",
        title,
        flags=re.IGNORECASE,
    )
    title = re.sub(r"\b([A-Za-zÀ-ÿ]+)\(e\)", r"\1", title, flags=re.IGNORECASE)
    title = re.sub(r"\b([A-Za-zÀ-ÿ]+)[·.]se\b", r"\1", title, flags=re.IGNORECASE)
    title = re.sub(
        r"\b(Expert|Administrateur)\s*/\s*(?:Experte|Administratrice)\b",
        r"\1",
        title,
        flags=re.IGNORECASE,
    )
    title = re.sub(r"\s+@\s+[^|–-]+(?=\s*[-–|]|$)", " ", title)
    title = _MARKETING_PREFIX_RE.sub("", title)
    title = _CONTRACT_NOISE_RE.sub("", title)
    previous = None
    while previous != title:
        previous = title
        title = _LOCATION_SUFFIX_RE.sub("", title)
    title = re.sub(r"\s*[:|–-]\s*$", "", title)
    title = re.sub(r"\s+", " ", title).strip(" \t\r\n:|-–")
    if not title:
        raise FactBankError("role title is empty after normalisation")
    return title


def build_cv_title(
    raw_title: str,
    *,
    contract_type: str,
    duration_months: int | None = None,
    start_date: str = "septembre 2026",
) -> str:
    """Build the deterministic CV title used after all advisor providers."""

    role = normalise_role_title(raw_title)
    normalized_contract = contract_type.strip().casefold()
    if normalized_contract == "stage":
        duration = f" {duration_months} mois" if duration_months else ""
        suffix = f"Stage{duration} dès {start_date}"
    else:
        suffix = f"Alternance M2 dès {start_date}"
    return f"{role} - {suffix}"


def format_fact_bank(bank: FactBank) -> str:
    """Render the bank as plain UTF-8 text for human review in the CLI."""

    lines: list[str] = []

    def section(title: str) -> None:
        if lines:
            lines.append("")
        lines.append(title)
        lines.append("=" * len(title))

    section("EXPÉRIENCE")
    for entry in bank.experience:
        lines.append(f"{entry.employer} | {entry.role} | {entry.dates} | {entry.location}")
        for claim in entry.facts:
            review = " [À REVOIR]" if claim.needs_review else ""
            lines.append(f"  - {claim.id}: {claim.text}{review}")

    section("PROJETS")
    for entry in bank.projects:
        lines.append(f"{entry.title} [{', '.join(entry.stack)}]")
        for claim in entry.facts:
            review = " [À REVOIR]" if claim.needs_review else ""
            lines.append(f"  - {claim.id}: {claim.text}{review}")

    section("FORMATION")
    for entry in bank.education:
        lines.append(
            f"- {entry.id}: {entry.diploma}, {entry.institution}, "
            f"{entry.location}, {entry.dates}"
        )

    section("CERTIFICATIONS")
    for entry in bank.certifications:
        lines.append(f"- {entry.id}: {entry.name}, obtenu {entry.obtained}")

    section("LANGUES")
    for entry in bank.languages:
        lines.append(f"- {entry.id}: {entry.name}, {entry.level}")

    section("COMPÉTENCES")
    for entry in bank.skills:
        status = "vérifiée" if entry.verified else "non vérifiée"
        review = ", à revoir" if entry.needs_review else ""
        lines.append(f"- {entry.id}: {entry.name} [{status}{review}]")

    section("VERROUILLÉ")
    lines.extend(
        (
            f"Nom: {bank.locked.name}",
            f"E-mail: {bank.locked.email}",
            f"Téléphone: {bank.locked.phone}",
            f"LinkedIn: {bank.locked.linkedin}",
            f"Employeurs: {', '.join(bank.locked.employer_names)}",
            f"Diplômes: {', '.join(bank.locked.diplomas)}",
            f"Certifications: {', '.join(bank.locked.certification_names)}",
            f"Dates: {', '.join(bank.locked.dates)}",
        )
    )
    return "\n".join(lines)
