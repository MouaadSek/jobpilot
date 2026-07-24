"""matcher.hard_filter tests, driven through the real Profile loader."""

from __future__ import annotations

import sqlite3

import matcher


def _profile(seeded_profile: sqlite3.Connection) -> matcher.Profile:
    return matcher.Profile.load(seeded_profile)


def _row(db: sqlite3.Connection, **cols) -> sqlite3.Row:
    """Build a throwaway offer row with the given columns via an in-memory insert."""
    from jobpilot.db import source_id

    sid = source_id(db, "france_travail")
    defaults = dict(
        source_id=sid, url="u", title="t", content_hash=cols.get("title", "t"),
        contract_type="alternance", city="Lille", remote_policy="onsite",
        duration_months=None, description="desc",
    )
    defaults.update(cols)
    defaults["content_hash"] = str(defaults.get("content_hash") or defaults["title"])
    keys = ", ".join(defaults)
    ph = ", ".join("?" for _ in defaults)
    cur = db.execute(f"INSERT INTO offers ({keys}) VALUES ({ph})",
                     tuple(defaults.values()))
    return db.execute("SELECT * FROM offers WHERE id = ?", (cur.lastrowid,)).fetchone()


def test_accepts_matching_alternance_in_lille(seeded_profile: sqlite3.Connection) -> None:
    p = _profile(seeded_profile)
    offer = _row(seeded_profile, contract_type="alternance", city="Lille")
    ok, reason = matcher.hard_filter(offer, p)
    assert ok, reason


def test_rejects_wrong_contract(seeded_profile: sqlite3.Connection) -> None:
    p = _profile(seeded_profile)
    offer = _row(seeded_profile, contract_type="cdi", city="Lille")
    ok, reason = matcher.hard_filter(offer, p)
    assert not ok
    assert "contract" in reason


def test_rejects_far_city_onsite(seeded_profile: sqlite3.Connection) -> None:
    p = _profile(seeded_profile)
    offer = _row(seeded_profile, contract_type="stage", city="Marseille",
                 remote_policy="onsite")
    ok, reason = matcher.hard_filter(offer, p)
    assert not ok
    assert "location" in reason


def test_unknown_location_passes(seeded_profile: sqlite3.Connection) -> None:
    p = _profile(seeded_profile)
    offer = _row(seeded_profile, contract_type="stage", city="", remote_policy="unknown")
    ok, _ = matcher.hard_filter(offer, p)
    assert ok


def test_full_remote_passes_any_city(seeded_profile: sqlite3.Connection) -> None:
    p = _profile(seeded_profile)
    offer = _row(seeded_profile, contract_type="stage", city="Toulouse",
                 remote_policy="full_remote")
    ok, _ = matcher.hard_filter(offer, p)
    assert ok


def test_duration_too_short_rejected(seeded_profile: sqlite3.Connection) -> None:
    p = _profile(seeded_profile)  # min_duration_months = 6
    offer = _row(seeded_profile, contract_type="stage", city="Lille",
                 duration_months=2)
    ok, reason = matcher.hard_filter(offer, p)
    assert not ok
    assert "duration" in reason
