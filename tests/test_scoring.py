"""Scoring wiring: profile embedding cache + end-to-end scoring via a fake embed_fn."""

from __future__ import annotations

import json
import sqlite3

from jobpilot.db import source_id
from jobpilot.embeddings import build_profile_text, ensure_profile_embedding
from jobpilot.scoring import score


def _fake_embed(text: str) -> list[float]:
    """Deterministic 4-dim embedding aligned with the seeded profile vector.

    The seeded profile embedding is [0.1,0.2,0.3,0.4]; returning the same vector
    yields cosine=1 so semantic_score is high for any offer.
    """
    return [0.1, 0.2, 0.3, 0.4]


def _insert_offer(db: sqlite3.Connection, **cols) -> int:
    sid = source_id(db, "france_travail")
    import time

    defaults = dict(
        source_id=sid, url="u", title="t", contract_type="alternance",
        city="Lille", remote_policy="hybrid", description="desc",
        content_hash=f"h{time.time_ns()}", posted_at=None, salary_min=None,
        duration_months=None, stack_tags="[]",
    )
    defaults.update(cols)
    keys = ", ".join(defaults)
    ph = ", ".join("?" for _ in defaults)
    cur = db.execute(f"INSERT INTO offers ({keys}) VALUES ({ph})",
                     tuple(defaults.values()))
    db.commit()
    return int(cur.lastrowid)


def test_build_profile_text(seeded_profile: sqlite3.Connection) -> None:
    row = seeded_profile.execute("SELECT * FROM profile WHERE id=1").fetchone()
    text = build_profile_text(row)
    # Natural-language sentences, data-driven from the profile row.
    assert "azure" in text and "soc analyst" in text
    assert "compétences" in text and "type de contrat" in text
    assert "alternance" in text and "fr (" in text  # languages rendered as "fr (c2)"


def test_ensure_profile_embedding_computes_when_missing(
    seeded_profile: sqlite3.Connection,
) -> None:
    seeded_profile.execute("UPDATE profile SET embedding = NULL WHERE id = 1")
    seeded_profile.commit()
    ensure_profile_embedding(seeded_profile, _fake_embed)
    row = seeded_profile.execute("SELECT embedding FROM profile WHERE id=1").fetchone()
    assert json.loads(row["embedding"]) == [0.1, 0.2, 0.3, 0.4]


def test_score_queues_strong_match(seeded_profile: sqlite3.Connection) -> None:
    from datetime import UTC, datetime

    _insert_offer(
        seeded_profile,
        title="alternance soc analyst azure sentinel kql",
        description="azure sentinel kql docker kubernetes python",
        remote_policy="hybrid", salary_min=20000,
        posted_at=datetime.now(UTC).isoformat(),
    )
    queued = score(seeded_profile, _fake_embed)
    assert queued == 1
    app = seeded_profile.execute(
        "SELECT status FROM applications WHERE kind='offer'"
    ).fetchone()
    assert app["status"] == "queued"


def test_score_records_hard_filter_rejection(
    seeded_profile: sqlite3.Connection,
) -> None:
    oid = _insert_offer(seeded_profile, title="cdi sre", contract_type="cdi",
                        city="Marseille", remote_policy="onsite")
    score(seeded_profile, _fake_embed)
    ms = seeded_profile.execute(
        "SELECT hard_filter_pass, hard_filter_reason FROM match_scores "
        "WHERE offer_id = ?", (oid,)
    ).fetchone()
    assert ms["hard_filter_pass"] == 0
    assert "contract" in ms["hard_filter_reason"]


def test_score_is_idempotent(seeded_profile: sqlite3.Connection) -> None:
    _insert_offer(seeded_profile, title="alternance soc azure sentinel kql")
    first = score(seeded_profile, _fake_embed)
    second = score(seeded_profile, _fake_embed)  # nothing new to score
    assert second == 0
    n = seeded_profile.execute("SELECT count(*) AS n FROM match_scores").fetchone()["n"]
    assert n == 1
    assert first >= 0
