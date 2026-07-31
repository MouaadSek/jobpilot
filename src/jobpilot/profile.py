"""Profile singleton + cv_variants seeding.

Persistence logic only (no prompting/print — the CLI owns interaction). Both the
profile upsert and variant sync are idempotent so re-running init-profile is safe.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from jobpilot.config import PROJECT_ROOT
from jobpilot.logging_conf import get_logger

log = get_logger("profile")

DEFAULT_CV_PROFILE_PATH = PROJECT_ROOT / "config" / "profile.yaml"
DEFAULT_MATCHING_PROFILE_PATH = PROJECT_ROOT / "config" / "matching_profile.yaml"

#: The only profile columns the committed matching vocabulary owns. Everything
#: else on the row (name, certs, languages, headline) stays whatever
#: ``init-profile`` put there.
MATCHING_PROFILE_FIELDS: tuple[str, ...] = (
    "target_roles",
    "hard_skills",
    "locations_ok",
)


class CvProfileError(ValueError):
    """Raised when the committed CV profile is missing or malformed."""


class MatchingProfileError(ValueError):
    """Raised when the committed matching vocabulary is missing or malformed."""


@dataclass(frozen=True, slots=True)
class CvProfile:
    """Renderer-owned candidate facts injected into every generated CV."""

    city: str
    region: str

    @property
    def header_location(self) -> str:
        """The location printed in the CV header when the offer yields none."""
        return self.region or self.city


def load_cv_profile(path: Path | None = None) -> CvProfile:
    """Load the committed CV profile, failing loudly rather than defaulting."""
    chosen = Path(path or DEFAULT_CV_PROFILE_PATH)
    try:
        raw = yaml.safe_load(chosen.read_text(encoding="utf-8")) or {}
    except OSError as exc:
        raise CvProfileError(f"could not read CV profile: {chosen}") from exc
    except yaml.YAMLError as exc:
        raise CvProfileError(f"CV profile is invalid YAML: {exc}") from exc
    if not isinstance(raw, dict):
        raise CvProfileError("CV profile must be an object")
    location = raw.get("location")
    if not isinstance(location, dict):
        raise CvProfileError("CV profile must define a 'location' object")
    city = location.get("city")
    region = location.get("region")
    if not isinstance(city, str) or not city.strip():
        raise CvProfileError("CV profile location.city must be non-empty text")
    if not isinstance(region, str) or not region.strip():
        raise CvProfileError("CV profile location.region must be non-empty text")
    return CvProfile(city=city.strip(), region=region.strip())


@dataclass(frozen=True, slots=True)
class MatchingProfile:
    """The scoring vocabulary, committed to git rather than typed once.

    These three lists drive ``matcher.keyword_score``, ``matcher.hard_filter``
    *and* the profile embedding, so keeping them in the database alone made the
    matching behaviour unreviewable and unreproducible.
    """

    target_roles: list[str]
    hard_skills: list[str]
    locations_ok: list[str]

    def as_json(self) -> dict[str, str]:
        return {
            name: json.dumps(getattr(self, name), ensure_ascii=False)
            for name in MATCHING_PROFILE_FIELDS
        }


def load_matching_profile(path: Path | None = None) -> MatchingProfile:
    """Load the committed matching vocabulary, failing loudly rather than defaulting."""

    chosen = Path(path or DEFAULT_MATCHING_PROFILE_PATH)
    try:
        raw = yaml.safe_load(chosen.read_text(encoding="utf-8")) or {}
    except OSError as exc:
        raise MatchingProfileError(f"could not read matching profile: {chosen}") from exc
    except yaml.YAMLError as exc:
        raise MatchingProfileError(f"matching profile is invalid YAML: {exc}") from exc
    if not isinstance(raw, dict):
        raise MatchingProfileError("matching profile must be an object")

    values: dict[str, list[str]] = {}
    for name in MATCHING_PROFILE_FIELDS:
        items = raw.get(name)
        if not isinstance(items, list) or not items:
            raise MatchingProfileError(
                f"matching profile must define a non-empty '{name}' list"
            )
        cleaned = [str(item).strip() for item in items]
        if not all(cleaned):
            raise MatchingProfileError(f"'{name}' contains an empty entry")
        # Duplicates inflate len(hard_skills), which is keyword_score's
        # denominator, so they silently lower every score.
        seen = {item.casefold() for item in cleaned}
        if len(seen) != len(cleaned):
            raise MatchingProfileError(f"'{name}' contains duplicate entries")
        values[name] = cleaned
    return MatchingProfile(**values)


def apply_matching_profile(
    db: sqlite3.Connection, profile: MatchingProfile
) -> dict[str, tuple[list[str], list[str]]]:
    """Write the vocabulary onto the profile singleton. Returns {field: (before, after)}.

    Touches only the three matching columns; idempotent, so re-running it is a
    no-op rather than a second edit.
    """

    row = db.execute("SELECT * FROM profile WHERE id = 1").fetchone()
    if row is None:
        raise MatchingProfileError(
            "no profile row; run `jobpilot init-profile` before applying the "
            "matching vocabulary"
        )
    before = {
        name: json.loads(row[name] or "[]") for name in MATCHING_PROFILE_FIELDS
    }
    payload = profile.as_json()
    db.execute(
        "UPDATE profile SET target_roles = :target_roles, "
        " hard_skills = :hard_skills, locations_ok = :locations_ok WHERE id = 1",
        payload,
    )
    db.commit()
    changed = [
        name
        for name in MATCHING_PROFILE_FIELDS
        if before[name] != getattr(profile, name)
    ]
    log.info(
        "applied matching profile; %s",
        f"changed: {', '.join(changed)}" if changed else "no change",
    )
    return {
        name: (before[name], getattr(profile, name))
        for name in MATCHING_PROFILE_FIELDS
    }


@dataclass(slots=True)
class ProfileInput:
    full_name: str
    target_roles: list[str] = field(default_factory=list)
    hard_skills: list[str] = field(default_factory=list)
    certs: list[str] = field(default_factory=list)
    languages: dict[str, str] = field(default_factory=dict)
    locations_ok: list[str] = field(default_factory=list)
    contract_wanted: list[str] = field(default_factory=list)
    min_duration_months: int | None = None
    headline: str | None = None  # free-text professional summary (feeds embedding)


def save_profile(db: sqlite3.Connection, p: ProfileInput) -> None:
    """Upsert the singleton profile row (id=1), preserving any cached embedding."""
    db.execute(
        "INSERT INTO profile (id, full_name, target_roles, hard_skills, certs, "
        " languages, locations_ok, contract_wanted, min_duration_months, headline) "
        "VALUES (1, :full_name, :target_roles, :hard_skills, :certs, :languages, "
        " :locations_ok, :contract_wanted, :min_duration_months, :headline) "
        "ON CONFLICT(id) DO UPDATE SET "
        " full_name=excluded.full_name, target_roles=excluded.target_roles, "
        " hard_skills=excluded.hard_skills, certs=excluded.certs, "
        " languages=excluded.languages, locations_ok=excluded.locations_ok, "
        " contract_wanted=excluded.contract_wanted, "
        " min_duration_months=excluded.min_duration_months, "
        " headline=excluded.headline",
        {
            "full_name": p.full_name,
            "target_roles": json.dumps(p.target_roles, ensure_ascii=False),
            "hard_skills": json.dumps(p.hard_skills, ensure_ascii=False),
            "certs": json.dumps(p.certs, ensure_ascii=False),
            "languages": json.dumps(p.languages, ensure_ascii=False),
            "locations_ok": json.dumps(p.locations_ok, ensure_ascii=False),
            "contract_wanted": json.dumps(p.contract_wanted, ensure_ascii=False),
            "min_duration_months": p.min_duration_months,
            "headline": p.headline,
        },
    )
    db.commit()
    log.info("saved profile for %s", p.full_name)


def load_variants(path: Path) -> list[dict]:
    """Read cv_variants definitions from a YAML file (list under 'variants')."""
    if not path.exists():
        raise FileNotFoundError(f"CV variants file not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    variants = data.get("variants", []) or []
    for v in variants:
        missing = {"slug", "label", "template_path"} - set(v)
        if missing:
            raise ValueError(f"variant {v!r} missing keys: {sorted(missing)}")
    return variants


def sync_variants(db: sqlite3.Connection, variants: list[dict]) -> int:
    """Upsert cv_variants by unique slug. Returns the number of rows written."""
    n = 0
    for v in variants:
        db.execute(
            "INSERT INTO cv_variants (slug, label, keywords, template_path) "
            "VALUES (:slug, :label, :keywords, :template_path) "
            "ON CONFLICT(slug) DO UPDATE SET "
            " label=excluded.label, keywords=excluded.keywords, "
            " template_path=excluded.template_path",
            {
                "slug": v["slug"],
                "label": v["label"],
                "keywords": json.dumps(v.get("keywords", []), ensure_ascii=False),
                "template_path": v["template_path"],
            },
        )
        n += 1
    db.commit()
    log.info("synced %d cv_variants", n)
    return n
