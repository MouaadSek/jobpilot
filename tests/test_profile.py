"""Profile upsert + cv_variants sync idempotency."""

from __future__ import annotations

import json
import sqlite3

import pytest

from jobpilot.profile import ProfileInput, load_variants, save_profile, sync_variants


def test_save_profile_upserts_singleton(db: sqlite3.Connection) -> None:
    save_profile(db, ProfileInput(full_name="A", hard_skills=["azure"],
                                  contract_wanted=["alternance"]))
    save_profile(db, ProfileInput(full_name="B", hard_skills=["kql"],
                                  contract_wanted=["stage"]))
    rows = db.execute("SELECT * FROM profile").fetchall()
    assert len(rows) == 1
    assert rows[0]["full_name"] == "B"
    assert json.loads(rows[0]["hard_skills"]) == ["kql"]


def test_sync_variants_idempotent_by_slug(db: sqlite3.Connection) -> None:
    variants = [
        {"slug": "soc", "label": "SOC", "keywords": ["siem"],
         "template_path": "t/soc.tex"},
        {"slug": "cloud", "label": "Cloud", "keywords": ["azure"],
         "template_path": "t/cloud.tex"},
    ]
    assert sync_variants(db, variants) == 2
    # Re-sync with an updated label -> still 2 rows, label updated.
    variants[0]["label"] = "SOC Analyst"
    sync_variants(db, variants)
    rows = db.execute("SELECT slug, label FROM cv_variants ORDER BY slug").fetchall()
    assert len(rows) == 2
    assert dict(rows[0]) == {"slug": "cloud", "label": "Cloud"}
    assert dict(rows[1]) == {"slug": "soc", "label": "SOC Analyst"}


def test_load_variants_validates_required_keys(tmp_path) -> None:
    p = tmp_path / "variants.yaml"
    p.write_text("variants:\n  - slug: x\n    label: X\n", encoding="utf-8")
    with pytest.raises(ValueError, match="template_path"):
        load_variants(p)


def test_load_variants_missing_file(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        load_variants(tmp_path / "nope.yaml")
