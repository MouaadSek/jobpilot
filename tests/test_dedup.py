"""content_hash dedup + INSERT OR IGNORE behavior."""

from __future__ import annotations

import sqlite3

from jobpilot.db import source_id
from jobpilot.ingest import _insert_offer
from jobpilot.models import OfferRecord, content_hash


def _offer(**over) -> OfferRecord:
    base = dict(
        external_id="A1",
        url="https://example.test/1",
        title="Alternance Analyste SOC",
        company_name="ACME",
        description="Sécurité cloud, Azure Sentinel, KQL.",
        contract_type="alternance",
    )
    base.update(over)
    return OfferRecord(**base).normalized()


def test_content_hash_is_stable_and_case_insensitive() -> None:
    a = content_hash("Analyste SOC", "ACME", "Description ici")
    b = content_hash("  analyste   soc ", "acme", "description ici")
    assert a == b


def test_same_content_hash_collapses_to_one_row(db: sqlite3.Connection) -> None:
    sid = source_id(db, "france_travail")
    o1 = _offer(external_id="A1")
    # Same title/company/desc but different external id -> same content_hash.
    o2 = _offer(external_id="A2")
    assert o1.hash == o2.hash

    assert _insert_offer(db, sid, None, o1) is True
    assert _insert_offer(db, sid, None, o2) is False  # ignored on content_hash
    db.commit()

    n = db.execute("SELECT count(*) AS n FROM offers").fetchone()["n"]
    assert n == 1


def test_same_external_id_ignored(db: sqlite3.Connection) -> None:
    sid = source_id(db, "france_travail")
    o1 = _offer(external_id="X", title="Poste A")
    o2 = _offer(external_id="X", title="Poste B")  # same (source, external_id)
    assert _insert_offer(db, sid, None, o1) is True
    assert _insert_offer(db, sid, None, o2) is False
    db.commit()
    assert db.execute("SELECT count(*) AS n FROM offers").fetchone()["n"] == 1
