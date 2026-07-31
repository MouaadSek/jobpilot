"""Task 35 item 1: the city parse fix (1a) and the committed matching profile (1b).

Item 1c was withdrawn after measurement: removing the two-digit department
entries from ``locations_ok`` costs 50 offers and 4 applications in order to
block 4 near-zero false passes, because France Travail writes cities as
"Courbevoie (92)" and "92400 Courbevoie". The unanchored ``any(loc in city)``
match is a real defect, but fixing it means anchored matching inside the frozen
``matcher.hard_filter`` — a separate decision, not a data change.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
import yaml

from jobpilot.profile import (
    MATCHING_PROFILE_FIELDS,
    MatchingProfile,
    MatchingProfileError,
    apply_matching_profile,
    load_matching_profile,
)
from jobpilot.sources.email_alerts import is_noise

ROOT = Path(__file__).resolve().parents[1]
COMMITTED = ROOT / "config" / "matching_profile.yaml"
FACT_BANK = ROOT / "config" / "fact_bank.yaml"


# ----- 1a: the city parse bug -----


@pytest.mark.parametrize(
    "rating", ["3.7", "4.2", "2.8", "4", "0", "5", "3,7", "4,0", "1.1"]
)
def test_an_employer_star_rating_is_card_chrome_not_a_city(rating: str) -> None:
    """59 offers had an Indeed star rating filed as their city; the hard filter
    then rejected every one of them on location."""

    assert is_noise(rating) is True


@pytest.mark.parametrize(
    "city",
    [
        "Lille",
        "Paris",
        "Roubaix",
        "Courbevoie (92)",
        "92400 Courbevoie",
        "94 - Thiais",
        "59000 Lille",
        "Villeneuve-d'Ascq",
        "Île-de-France, France",
        "Le Havre et périphérie",
    ],
)
def test_a_real_place_is_never_mistaken_for_a_rating(city: str) -> None:
    """The rating rule is bounded to 0-5 with one decimal precisely so the
    postcode and department notations keep working."""

    assert is_noise(city) is False


def test_a_headline_question_is_not_a_place() -> None:
    assert is_noise(
        "comment garantir la protection des données personnelles ?"
    ) is True


@pytest.mark.parametrize("title", ["Stage ?", "Alternance ?", "Dev ?"])
def test_a_short_question_is_left_alone(title: str) -> None:
    """The length guard is what keeps the question rule off job titles."""

    assert is_noise(title) is False


def test_a_six_is_not_a_rating() -> None:
    """Ratings run 0-5. A bare 6 is something else, and guessing is not the job."""

    assert is_noise("6") is False


# ----- 1b: the committed matching profile -----


def test_the_committed_profile_loads_and_covers_every_field() -> None:
    profile = load_matching_profile(COMMITTED)

    for field in MATCHING_PROFILE_FIELDS:
        assert getattr(profile, field), f"{field} must not be empty"


def test_every_hard_skill_is_a_verified_fact_bank_skill() -> None:
    """"Defensible as something Mouaad can claim" is machine-checked, because
    this list feeds CV variant selection as well as scoring."""

    bank = yaml.safe_load(FACT_BANK.read_text(encoding="utf-8"))
    verified = {
        skill["name"].casefold()
        for skill in bank.get("skills", [])
        if skill.get("verified") and not skill.get("needs_review")
    }
    profile = load_matching_profile(COMMITTED)

    unbacked = [s for s in profile.hard_skills if s.casefold() not in verified]
    assert unbacked == [], f"not verified in the fact bank: {unbacked}"


@pytest.mark.parametrize("token", ["soc", "si", "data"])
def test_the_dangerous_bare_tokens_stay_out_of_target_roles(token: str) -> None:
    """role_hit is an unanchored substring test worth a flat +0.15. As bare
    tokens these match 'societe', 'assistant', 'baby-sitter' and 'hotellerie';
    measured, they handed the bonus to offers with nothing to do with cyber."""

    profile = load_matching_profile(COMMITTED)

    assert token not in [role.casefold() for role in profile.target_roles]


def test_the_department_tokens_are_still_there() -> None:
    """Item 1c withdrawn. These are load-bearing: France Travail writes
    'Courbevoie (92)'. Removing them measured 9 queued -> 5."""

    profile = load_matching_profile(COMMITTED)

    for department in ("59", "62", "75", "92", "93", "94"):
        assert department in profile.locations_ok


def test_target_roles_are_short_enough_to_match_a_real_title() -> None:
    """The old list was already French but multi-word, and substring matching
    needs exact adjacency: 'Ingenieur EN Cybersecurite' missed
    'ingenieur cybersecurite'. At least half the list must be one or two words."""

    profile = load_matching_profile(COMMITTED)
    short = [role for role in profile.target_roles if len(role.split()) <= 2]

    assert len(short) >= len(profile.target_roles) / 2


# ----- validation -----


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "mp.yaml"
    path.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")
    return path


def _valid() -> dict:
    return {
        "target_roles": ["cybersécurité"],
        "hard_skills": ["Python"],
        "locations_ok": ["Lille"],
    }


@pytest.mark.parametrize("missing", MATCHING_PROFILE_FIELDS)
def test_a_missing_field_is_refused(tmp_path: Path, missing: str) -> None:
    payload = _valid()
    del payload[missing]

    with pytest.raises(MatchingProfileError, match=missing):
        load_matching_profile(_write(tmp_path, payload))


@pytest.mark.parametrize("field", MATCHING_PROFILE_FIELDS)
def test_an_empty_list_is_refused(tmp_path: Path, field: str) -> None:
    payload = _valid()
    payload[field] = []

    with pytest.raises(MatchingProfileError, match=field):
        load_matching_profile(_write(tmp_path, payload))


def test_duplicates_are_refused(tmp_path: Path) -> None:
    """len(hard_skills) is keyword_score's denominator, so a duplicate silently
    lowers every score in the database."""

    payload = _valid()
    payload["hard_skills"] = ["Python", "python"]

    with pytest.raises(MatchingProfileError, match="duplicate"):
        load_matching_profile(_write(tmp_path, payload))


def test_a_missing_file_is_refused(tmp_path: Path) -> None:
    with pytest.raises(MatchingProfileError, match="could not read"):
        load_matching_profile(tmp_path / "nope.yaml")


# ----- applying it -----


def _seed_profile(db: sqlite3.Connection) -> None:
    db.execute(
        "INSERT INTO profile (id, full_name, target_roles, hard_skills, certs, "
        "languages, locations_ok, contract_wanted, min_duration_months, headline, "
        "embedding) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            "Mouaad Sekkouri",
            json.dumps(["Analyste SOC"]),
            json.dumps(["SIEM"]),
            json.dumps(["AZ-900"]),
            json.dumps({"fr": "C2"}),
            json.dumps(["Lille"]),
            json.dumps(["alternance"]),
            6,
            "M1 cybersécurité",
            json.dumps([0.1, 0.2]),
        ),
    )
    db.commit()


def test_applying_touches_only_the_three_matching_columns(
    db: sqlite3.Connection,
) -> None:
    _seed_profile(db)
    profile = MatchingProfile(
        target_roles=["cybersécurité"], hard_skills=["Python"], locations_ok=["Paris"]
    )

    apply_matching_profile(db, profile)

    row = db.execute("SELECT * FROM profile WHERE id = 1").fetchone()
    assert json.loads(row["target_roles"]) == ["cybersécurité"]
    assert json.loads(row["hard_skills"]) == ["Python"]
    assert json.loads(row["locations_ok"]) == ["Paris"]
    # Everything init-profile owns survives untouched.
    assert row["full_name"] == "Mouaad Sekkouri"
    assert json.loads(row["certs"]) == ["AZ-900"]
    assert json.loads(row["contract_wanted"]) == ["alternance"]
    assert row["min_duration_months"] == 6
    assert row["headline"] == "M1 cybersécurité"


def test_applying_reports_what_changed(db: sqlite3.Connection) -> None:
    _seed_profile(db)
    profile = MatchingProfile(
        target_roles=["cybersécurité"], hard_skills=["Python"], locations_ok=["Lille"]
    )

    changes = apply_matching_profile(db, profile)

    assert changes["target_roles"] == (["Analyste SOC"], ["cybersécurité"])
    assert changes["locations_ok"] == (["Lille"], ["Lille"])  # unchanged


def test_applying_is_idempotent(db: sqlite3.Connection) -> None:
    _seed_profile(db)
    profile = load_matching_profile(COMMITTED)

    apply_matching_profile(db, profile)
    first = db.execute("SELECT * FROM profile WHERE id = 1").fetchone()
    changes = apply_matching_profile(db, profile)
    second = db.execute("SELECT * FROM profile WHERE id = 1").fetchone()

    assert tuple(first) == tuple(second)
    for before, after in changes.values():
        assert before == after


def test_applying_without_a_profile_row_says_what_to_run(
    db: sqlite3.Connection,
) -> None:
    profile = MatchingProfile(
        target_roles=["x"], hard_skills=["y"], locations_ok=["z"]
    )

    with pytest.raises(MatchingProfileError, match="init-profile"):
        apply_matching_profile(db, profile)
