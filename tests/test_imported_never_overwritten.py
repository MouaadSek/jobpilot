"""Task 43 item 5: an imported description is never overwritten.

The user opens the posting, captures 1900 characters of the employer's own
prose, and the offer finally has something worth tailoring against. Then the
daemon runs. It runs every three hours, so anything that would quietly put the
113-character alert card back does it within the day, and the CV goes out
adapted to a card again.

`imported_at` is the flag — `is_imported` is `imported_at IS NOT NULL` and
nothing else tests for it. Two paths could undo an import and both are held
here: re-ingestion from the source, and the synthesised-description backfill.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator

from jobpilot.descriptions import backfill_descriptions
from jobpilot.ingest import ingest_source
from jobpilot.models import OfferRecord
from jobpilot.offer_import import import_offer_description
from jobpilot.sources.base import Source
from tests.test_offer_import import ALERT_CARD, POSTING, _fake_score

OFFER_URL = "https://www.linkedin.com/jobs/view/555"


class _AlertSource(Source):
    """A source that keeps offering the thin card, exactly as an alert does."""

    name = "france_travail"

    def __init__(self, description: str = ALERT_CARD) -> None:
        self._description = description

    def fetch_offers(self) -> Iterator[OfferRecord]:
        yield OfferRecord(
            external_id="555",
            url=OFFER_URL,
            title="Alternance SOC",
            company_name="ACME",
            description=self._description,
        ).normalized()


def _ingest_then_import(db: sqlite3.Connection) -> int:
    """The real sequence: the alert arrives first, the human imports second."""

    ingest_source(db, _AlertSource())
    result = import_offer_description(
        db, url=OFFER_URL, description=POSTING, score_pass=_fake_score()
    )
    return int(result.offer_id)


def _stored(db: sqlite3.Connection, offer_id: int) -> sqlite3.Row:
    return db.execute(
        "SELECT description, imported_at FROM offers WHERE id = ?", (offer_id,)
    ).fetchone()


def test_re_ingesting_the_same_offer_leaves_the_imported_text_alone(
    db: sqlite3.Connection,
) -> None:
    """The daemon case, and the one that matters immediately."""

    offer_id = _ingest_then_import(db)

    ingest_source(db, _AlertSource())

    row = _stored(db, offer_id)
    assert row["description"] == POSTING
    assert row["imported_at"] is not None


def test_re_ingesting_does_not_create_a_second_row_for_the_offer(
    db: sqlite3.Connection,
) -> None:
    """Losing the import by being routed around it is the same bug as being
    overwritten: the application points at the row that was imported into."""

    _ingest_then_import(db)

    ingest_source(db, _AlertSource())

    assert db.execute("SELECT count(*) AS n FROM offers").fetchone()["n"] == 1


def test_the_backfill_does_not_synthesise_over_an_imported_description(
    db: sqlite3.Connection,
) -> None:
    """Synthesised text is field assembly standing in for prose nobody has.
    An imported description is the prose. Replacing it is a strict loss.

    `min_chars` is raised past the 200-character import floor deliberately: it
    comes from ALERT_MIN_DESCRIPTION_CHARS, so length alone is not a rail.
    """

    offer_id = _ingest_then_import(db)

    result = backfill_descriptions(db, min_chars=len(POSTING) + 500)

    assert _stored(db, offer_id)["description"] == POSTING
    assert result.updated == 0
    assert result.skipped_imported == 1


def test_the_forced_backfill_does_not_either(db: sqlite3.Connection) -> None:
    """`force` exists to re-compose rows the normal pass skips. That widening
    must not reach an imported posting."""

    offer_id = _ingest_then_import(db)

    backfill_descriptions(db, min_chars=len(POSTING) + 500, force=True)

    assert _stored(db, offer_id)["description"] == POSTING


def test_the_backfill_still_synthesises_over_a_thin_card(
    db: sqlite3.Connection,
) -> None:
    """The guard must be `imported_at`, not an accident that stopped the
    backfill working at all."""

    ingest_source(db, _AlertSource())
    offer_id = int(db.execute("SELECT id FROM offers").fetchone()["id"])

    result = backfill_descriptions(db, min_chars=len(POSTING) + 500)

    assert result.updated == 1
    assert result.skipped_imported == 0
    assert _stored(db, offer_id)["description"] != ALERT_CARD
