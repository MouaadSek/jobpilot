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


class CvProfileError(ValueError):
    """Raised when the committed CV profile is missing or malformed."""


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
