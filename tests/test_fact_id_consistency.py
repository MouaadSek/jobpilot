"""Task 35 item 2: a fact bank whose claim ids do not extend their entry is invalid.

`experience.baifall_dream` held claims named `experience.baifall.*` while every
other entry followed `entry.id + "." + slug`. The advisor generalised from the
majority and emitted an id that did not exist, on the one entry the completeness
floor forces onto every CV. This makes such a bank unloadable, so the mistake
cannot be reintroduced by editing YAML. Item 3 covers what the rejection says.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from jobpilot.facts import FactBankError, load_fact_bank

ROOT = Path(__file__).resolve().parents[1]
COMMITTED_BANK = ROOT / "config" / "fact_bank.yaml"


@pytest.fixture
def bank():
    return load_fact_bank(COMMITTED_BANK)


def _bank_payload() -> dict:
    return yaml.safe_load(COMMITTED_BANK.read_text(encoding="utf-8"))


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "bank.yaml"
    path.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")
    return path


# ----- item 2: the consistency assertion -----


def test_the_committed_bank_is_consistent(bank) -> None:
    """The real bank must satisfy the rule the loader now enforces."""

    for entry in (*bank.experience, *bank.projects):
        for claim in entry.facts:
            assert claim.id.startswith(f"{entry.id}.")


def test_an_experience_claim_that_does_not_extend_its_entry_is_refused(
    tmp_path: Path,
) -> None:
    """This is the exact shape the Baïfall entry had."""

    payload = _bank_payload()
    entry = payload["experience"][0]
    entry["id"] = "experience.baifall_dream"
    entry["facts"][0]["id"] = "experience.baifall.mission"

    with pytest.raises(FactBankError) as excinfo:
        load_fact_bank(_write(tmp_path, payload))

    message = str(excinfo.value)
    assert "experience.baifall.mission" in message
    assert "experience.baifall_dream" in message


def test_a_project_claim_that_does_not_extend_its_entry_is_refused(
    tmp_path: Path,
) -> None:
    """Projects have the same shape as experience, so they get the same rule."""

    payload = _bank_payload()
    entry = payload["projects"][0]
    entry["facts"][0]["id"] = "projects.something_else.detail"

    with pytest.raises(FactBankError, match="does not extend its entry id"):
        load_fact_bank(_write(tmp_path, payload))


def test_a_near_miss_prefix_is_still_refused(tmp_path: Path) -> None:
    """`experience.baifallX` starts with the entry id as a STRING but is a
    different entry; the dot is what makes it a child."""

    payload = _bank_payload()
    entry = payload["experience"][0]
    entry_id = entry["id"]
    entry["facts"][0]["id"] = f"{entry_id}X.mission"

    with pytest.raises(FactBankError, match="does not extend its entry id"):
        load_fact_bank(_write(tmp_path, payload))


def test_leaf_sections_are_not_subject_to_the_rule(bank) -> None:
    """Education, certifications, languages and skills have no sub-claims: the
    entry id *is* the claim id, so a prefix rule would be meaningless."""

    leaf_ids = {
        *(e.id for e in bank.education),
        *(c.id for c in bank.certifications),
        *(lang.id for lang in bank.languages),
        *(s.id for s in bank.skills),
    }
    assert leaf_ids <= set(bank.claims)
