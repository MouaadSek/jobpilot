"""Task 35 item 3: a rejection that says what would have been valid.

Task 22c allows exactly one retry. A message that says only what is wrong spends
that retry re-guessing, which is why the Baïfall id failed twice rather than
once. This item changes an error message and nothing else: not the retry count,
not the validators, not what is accepted.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from jobpilot.facts import load_fact_bank
from jobpilot.tailoring import (
    MAX_SUGGESTED_FACT_IDS,
    UnknownFactIdError,
    nearest_entry_claim_ids,
    resolve_fact_id,
)

ROOT = Path(__file__).resolve().parents[1]
COMMITTED_BANK = ROOT / "config" / "fact_bank.yaml"


@pytest.fixture
def bank():
    return load_fact_bank(COMMITTED_BANK)


def test_a_bad_baifall_id_is_told_a_real_baifall_id(bank) -> None:
    """The regression test for the failure that burned two generations."""

    baifall = next(
        entry for entry in bank.experience if "baifall" in entry.id.casefold()
    )
    bad_id = f"{baifall.id}_dream.mission_principale"

    with pytest.raises(UnknownFactIdError) as excinfo:
        resolve_fact_id(bad_id, bank)

    message = str(excinfo.value)
    real_ids = [claim.id for claim in baifall.facts]
    assert any(real in message for real in real_ids), message
    assert baifall.id in message


def test_the_nearest_entry_is_the_longest_shared_prefix(bank) -> None:
    baifall = next(
        entry for entry in bank.experience if "baifall" in entry.id.casefold()
    )

    entry_id, ids = nearest_entry_claim_ids(f"{baifall.id}.does_not_exist", bank)

    assert entry_id == baifall.id
    assert set(ids) == {claim.id for claim in baifall.facts}


def test_sharing_only_the_section_name_is_not_near_enough(bank) -> None:
    """`experience.` is common to every experience entry. Matching on it would
    list the whole section back and teach the retry nothing."""

    entry_id, ids = nearest_entry_claim_ids("experience.totally_made_up", bank)

    assert entry_id is None
    assert ids == ()


def test_an_unresolvable_id_says_so_plainly_instead_of_dumping_the_bank(bank) -> None:
    with pytest.raises(UnknownFactIdError) as excinfo:
        resolve_fact_id("chose.qui.nexiste.pas", bank)

    message = str(excinfo.value)
    assert "No entry in the bank has a similar id." in message
    # The whole bank is emphatically not listed.
    assert len(message) < 300


def test_the_suggestion_list_is_capped(bank) -> None:
    """A large entry must not blow the retry prompt."""

    biggest = max(
        (*bank.experience, *bank.projects), key=lambda entry: len(entry.facts)
    )
    error = UnknownFactIdError(
        "x",
        suggestions=[claim.id for claim in biggest.facts] * 5,
        entry_id=biggest.id,
    )

    listed = str(error).count("(+")
    assert MAX_SUGGESTED_FACT_IDS == 15
    if len(biggest.facts) * 5 > MAX_SUGGESTED_FACT_IDS:
        assert listed == 1, "an over-long list must say how many it hid"


def test_the_message_still_opens_with_the_original_wording(bank) -> None:
    """Existing callers and tests match on this prefix; item 3 appends, it does
    not rewrite."""

    with pytest.raises(
        UnknownFactIdError, match=r"^unknown fact id in sourced content: nope"
    ):
        resolve_fact_id("nope", bank)


def test_validate_provenance_also_gets_the_valid_ids(bank) -> None:
    """The path the Baïfall citation actually took used to raise a bare
    TailoringError, so it never reached the retry's valid-id block."""

    from jobpilot.tailoring import SourcedBullet, validate_provenance, whole_bank_scope

    baifall = next(
        entry for entry in bank.experience if "baifall" in entry.id.casefold()
    )
    bullet = SourcedBullet(
        text="Traitement des incidents.", sources=(f"{baifall.id}_dream.mission",)
    )

    with pytest.raises(UnknownFactIdError) as excinfo:
        validate_provenance([bullet], bank, scope=whole_bank_scope(bank))

    assert baifall.id in str(excinfo.value)
