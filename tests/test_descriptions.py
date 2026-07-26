"""Synthesised descriptions for thin alert offers, plus backfill and rescore.

The rule under test everywhere here: synthesis ASSEMBLES fields the alert
already carried. It must never introduce a responsibility, technology,
seniority, salary or company detail that was not in the input.
"""

from __future__ import annotations

import re
import sqlite3

import pytest

from jobpilot.descriptions import (
    SCAFFOLDING,
    SYNTHESIZED_DESCRIPTION_PREFIX,
    backfill_descriptions,
    clear_match_scores,
    enrich_offer,
    is_synthesized,
    is_thin,
    synthesize_description,
)
from jobpilot.models import OfferRecord
from jobpilot.state import transition

RICH_DESCRIPTION = (
    "Vous rejoignez l'équipe sécurité pour surveiller le SIEM, qualifier les "
    "alertes, contribuer aux playbooks de réponse à incident et automatiser la "
    "collecte de logs sur un parc Azure. Stack : Sentinel, KQL, Python."
)


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"\w+", text.casefold()))


SCAFFOLDING_TOKENS = set().union(*(_tokens(part) for part in SCAFFOLDING))


def _offer(
    db: sqlite3.Connection,
    *,
    source: str = "linkedin_alert",
    title: str = "Alternance Analyste SOC",
    description: str | None = None,
    company: str | None = "ACME Cyber",
    city: str | None = "Lille",
    external_id: str = "1",
) -> int:
    company_id = None
    if company is not None:
        cur = db.execute("INSERT INTO companies (name) VALUES (?)", (company,))
        company_id = cur.lastrowid
    source_row = db.execute("SELECT id FROM sources WHERE name = ?", (source,)).fetchone()
    cur = db.execute(
        "INSERT INTO offers (source_id, company_id, external_id, url, title, "
        " description, contract_type, city, remote_policy, content_hash) "
        "VALUES (?, ?, ?, ?, ?, ?, 'unknown', ?, 'unknown', ?)",
        (
            source_row["id"],
            company_id,
            external_id,
            f"https://example.test/{source}/{external_id}",
            title,
            description,
            city,
            f"hash-{source}-{external_id}",
        ),
    )
    db.commit()
    return int(cur.lastrowid)


def _score(db: sqlite3.Connection, offer_id: int, final: float = 0.02) -> None:
    db.execute(
        "INSERT INTO match_scores (offer_id, hard_filter_pass, semantic_score, "
        " keyword_score, bonus_score, final_score) VALUES (?, 1, 0.14, 0.0, 0.0, ?)",
        (offer_id, final),
    )
    db.commit()


# ---- synthesis ----


def test_synthesis_assembles_only_fields_present_in_the_alert() -> None:
    result = synthesize_description(
        "Alternance Analyste SOC",
        company="ACME Cyber",
        city="Lille, Hauts-de-France",
        snippet="Surveillez les alertes SIEM.",
    )

    source_tokens = _tokens(
        "Alternance Analyste SOC ACME Cyber Lille, Hauts-de-France "
        "Surveillez les alertes SIEM."
    )
    assert _tokens(result) - SCAFFOLDING_TOKENS <= source_tokens


@pytest.mark.parametrize(
    "invented",
    ["kubernetes", "sentinel", "senior", "salaire", "cdi", "python", "startup", "5"],
)
def test_synthesis_invents_no_responsibilities_skills_or_seniority(invented: str) -> None:
    result = synthesize_description(
        "Alternance Analyste SOC", company="ACME Cyber", city="Lille"
    )

    assert invented not in result.casefold()


def test_synthesis_keeps_every_field_it_was_given() -> None:
    result = synthesize_description(
        "Stage Pentest",
        company="RedTeam SAS",
        city="Villeneuve-d'Ascq (59)",
        snippet="Testez des applications web.",
    )

    for field in ("Stage Pentest", "RedTeam SAS", "Villeneuve-d'Ascq (59)",
                  "Testez des applications web."):
        assert field in result


def test_synthesis_omits_missing_fields_without_placeholders() -> None:
    result = synthesize_description("Analyste SOC")

    assert "proposé par" not in result
    assert "Lieu" not in result
    assert result.endswith("Offre d'emploi : Analyste SOC.")


def test_synthesis_is_marked_and_detectable() -> None:
    result = synthesize_description("Alternance Analyste SOC")

    assert result.startswith(SYNTHESIZED_DESCRIPTION_PREFIX)
    assert is_synthesized(result)
    assert not is_synthesized(RICH_DESCRIPTION)
    assert not is_synthesized(None)


def test_synthesis_is_deterministic() -> None:
    kwargs = {"company": "ACME Cyber", "city": "Lille", "snippet": "SIEM."}

    assert synthesize_description("Alternance SOC", **kwargs) == synthesize_description(
        "Alternance SOC", **kwargs
    )


def test_contract_and_seniority_wording_survives_verbatim() -> None:
    """No separate keyword sentence: the title and snippet already carry them.

    Restating them measurably dilutes the embedding, so they are preserved by
    quoting the alert's own text rather than by re-listing normalised labels.
    """
    result = synthesize_description(
        "Alternance DevSecOps",
        snippet="Télétravail hybride, profil Junior.",
    )

    for wording in ("Alternance", "Télétravail", "hybride", "Junior"):
        assert wording in result


# ---- enrich_offer (ingest time) ----


def test_thin_description_is_replaced() -> None:
    offer = OfferRecord(
        external_id="1",
        url="https://example.test/1",
        title="Alternance Analyste SOC",
        company_name="ACME Cyber",
        city="Lille",
        description="Il y a 3 jours",
    )

    enrich_offer(offer)

    assert is_synthesized(offer.description)
    assert "Il y a 3 jours" in offer.description  # the snippet is preserved


def test_missing_description_is_replaced() -> None:
    offer = OfferRecord(
        external_id="1", url="https://example.test/1", title="Stage Pentest"
    )

    enrich_offer(offer)

    assert is_synthesized(offer.description)


def test_rich_description_is_left_untouched() -> None:
    offer = OfferRecord(
        external_id="1",
        url="https://example.test/1",
        title="Alternance Analyste SOC",
        description=RICH_DESCRIPTION,
    )

    enrich_offer(offer)

    assert offer.description == RICH_DESCRIPTION
    assert not is_thin(RICH_DESCRIPTION)


def test_enrich_offer_is_idempotent() -> None:
    offer = OfferRecord(
        external_id="1",
        url="https://example.test/1",
        title="Alternance Analyste SOC",
        company_name="ACME Cyber",
        city="Lille",
        description="14 chars here",
    )

    enrich_offer(offer)
    once = offer.description
    enrich_offer(offer)

    assert offer.description == once


def test_threshold_is_configurable() -> None:
    offer = OfferRecord(
        external_id="1",
        url="https://example.test/1",
        title="Alternance Analyste SOC",
        description="Court mais suffisant sous un seuil bas.",
    )

    enrich_offer(offer, min_chars=10)

    assert offer.description == "Court mais suffisant sous un seuil bas."


# ---- backfill ----


def test_backfill_replaces_thin_descriptions_and_keeps_rich_ones(
    db: sqlite3.Connection,
) -> None:
    thin_id = _offer(db, description="Il y a 3 jours", external_id="thin")
    rich_id = _offer(db, description=RICH_DESCRIPTION, external_id="rich")
    empty_id = _offer(db, description=None, external_id="empty")

    result = backfill_descriptions(db)

    assert result.updated == 2
    assert result.scanned == 2  # the rich offer is never even selected
    descriptions = dict(
        db.execute("SELECT id, description FROM offers").fetchall()  # type: ignore[arg-type]
    )
    assert is_synthesized(descriptions[thin_id])
    assert is_synthesized(descriptions[empty_id])
    assert descriptions[rich_id] == RICH_DESCRIPTION


def test_backfill_is_idempotent(db: sqlite3.Connection) -> None:
    _offer(db, description="Il y a 3 jours", external_id="thin")

    first = backfill_descriptions(db)
    stored = db.execute("SELECT description FROM offers").fetchone()["description"]
    second = backfill_descriptions(db)

    assert first.updated == 1
    assert second.updated == 0
    assert db.execute("SELECT description FROM offers").fetchone()["description"] == stored


def test_backfill_uses_the_offers_company_and_city(db: sqlite3.Connection) -> None:
    _offer(db, description=None, company="ACME Cyber", city="Lille", external_id="a")

    backfill_descriptions(db)

    description = db.execute("SELECT description FROM offers").fetchone()["description"]
    assert "ACME Cyber" in description
    assert "Lille" in description
    assert "Alternance Analyste SOC" in description


def test_backfill_can_target_one_source(db: sqlite3.Connection) -> None:
    linkedin_id = _offer(db, source="linkedin_alert", description=None, external_id="l")
    ft_id = _offer(db, source="france_travail", description=None, external_id="f")

    result = backfill_descriptions(db, source="linkedin_alert")

    assert result.source == "linkedin_alert"
    assert result.updated == 1
    rows = dict(db.execute("SELECT id, description FROM offers").fetchall())  # type: ignore[arg-type]
    assert is_synthesized(rows[linkedin_id])
    assert rows[ft_id] is None


def test_backfill_rejects_an_unknown_source(db: sqlite3.Connection) -> None:
    with pytest.raises(ValueError, match="unknown source"):
        backfill_descriptions(db, source="nope")


def test_backfill_does_not_change_stored_content_hashes(db: sqlite3.Connection) -> None:
    offer_id = _offer(db, description=None, external_id="a")
    before = db.execute("SELECT content_hash FROM offers").fetchone()["content_hash"]

    backfill_descriptions(db)

    after = db.execute(
        "SELECT content_hash FROM offers WHERE id = ?", (offer_id,)
    ).fetchone()["content_hash"]
    assert after == before


# ---- rescore ----


def test_rescore_clears_scores_so_they_can_be_recomputed(db: sqlite3.Connection) -> None:
    offer_id = _offer(db, description=None, external_id="a")
    _score(db, offer_id)

    result = clear_match_scores(db)

    assert result.cleared == 1
    assert db.execute("SELECT count(*) AS n FROM match_scores").fetchone()["n"] == 0


def test_rescore_leaves_offers_with_an_application_alone(db: sqlite3.Connection) -> None:
    scored_id = _offer(db, description=None, external_id="scored")
    applied_id = _offer(db, description=None, external_id="applied")
    _score(db, scored_id)
    _score(db, applied_id, final=0.42)
    application_id = int(
        db.execute(
            "INSERT INTO applications (offer_id, kind, status) VALUES (?, 'offer', 'queued')",
            (applied_id,),
        ).lastrowid
    )
    transition(db, application_id, "generating", detail={"reason": "test"})
    db.commit()

    result = clear_match_scores(db)

    assert result.cleared == 1
    assert result.skipped_with_application == 1
    remaining = db.execute("SELECT offer_id, final_score FROM match_scores").fetchall()
    assert [(r["offer_id"], r["final_score"]) for r in remaining] == [(applied_id, 0.42)]


def test_rescore_touches_no_applications_statuses_or_events(
    db: sqlite3.Connection,
) -> None:
    offer_id = _offer(db, description=None, external_id="a")
    _score(db, offer_id)
    application_id = int(
        db.execute(
            "INSERT INTO applications (offer_id, kind, status) VALUES (?, 'offer', 'queued')",
            (offer_id,),
        ).lastrowid
    )
    db.commit()
    before_events = db.execute("SELECT count(*) AS n FROM events").fetchone()["n"]

    clear_match_scores(db)

    row = db.execute(
        "SELECT status FROM applications WHERE id = ?", (application_id,)
    ).fetchone()
    assert row["status"] == "queued"
    assert db.execute("SELECT count(*) AS n FROM applications").fetchone()["n"] == 1
    assert db.execute("SELECT count(*) AS n FROM events").fetchone()["n"] == before_events


def test_rescore_can_target_one_source(db: sqlite3.Connection) -> None:
    linkedin_id = _offer(db, source="linkedin_alert", description=None, external_id="l")
    ft_id = _offer(db, source="france_travail", description=None, external_id="f")
    _score(db, linkedin_id)
    _score(db, ft_id)

    result = clear_match_scores(db, source="linkedin_alert")

    assert result.cleared == 1
    remaining = db.execute("SELECT offer_id FROM match_scores").fetchall()
    assert [r["offer_id"] for r in remaining] == [ft_id]


def test_rescore_rejects_an_unknown_source(db: sqlite3.Connection) -> None:
    with pytest.raises(ValueError, match="unknown source"):
        clear_match_scores(db, source="nope")
