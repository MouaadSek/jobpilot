"""Synthesise matchable text for offers that arrive with no description.

Job-alert emails carry a title, a company and a location but effectively no
description (measured on real data: 14 chars on average across 112
`linkedin_alert` offers, against 1916 for `france_travail`). matcher.py builds
its matching text from ``title + description`` and semantic similarity is 50% of
the blend, so those offers scored 0.143 semantic / 0.018 final on average and
only 1 of 112 cleared the threshold. They are unscoreable, not unsuitable.

matcher.py is frozen, so the fix has to put text into the stored `description`.
This module assembles the fields the alert DID provide into sentence form. It
invents nothing: no responsibilities, technologies, seniority, salary or company
details, no LLM call, no scraping. Every non-scaffolding token in the output is
copied from the alert, so contract and seniority wording survives exactly as the
alert spelled it.

This does not turn an alert into a rich posting — there is no information to
recover — but it lifts mean semantic score on the real 112 from 0.182 to 0.265
and replaces a flat near-zero cluster with a usable ranking. See SCAFFOLDING for
how the phrasing was chosen.

Synthesised descriptions carry a stable prefix (`SYNTHESIZED_DESCRIPTION_PREFIX`)
so they stay distinguishable from source-provided text without a schema change.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from jobpilot.config import DEFAULT_ALERT_MIN_DESCRIPTION_CHARS
from jobpilot.logging_conf import get_logger
from jobpilot.models import OfferRecord

log = get_logger("descriptions")

# Descriptions shorter than this are treated as absent. Configurable via
# ALERT_MIN_DESCRIPTION_CHARS (Settings.alert_min_description_chars).
DEFAULT_MIN_DESCRIPTION_CHARS = DEFAULT_ALERT_MIN_DESCRIPTION_CHARS

# Stable marker, deliberately not a schema column (constitution: prefer no
# schema change). `is_synthesized` is the only thing that should test for it.
SYNTHESIZED_DESCRIPTION_PREFIX = "[synthèse-alerte]"

# Fixed French scaffolding. Everything else in the output comes from the alert.
#
# The phrasing is not cosmetic: it was chosen by measuring mean semantic score
# over the 112 real linkedin_alert offers against the stored profile embedding.
# Short prose leads beat a metadata-style label list ("Intitulé du poste : ...",
# 0.234) and beat bare field concatenation (0.214). Padding the paragraph with a
# separate contract/seniority keyword sentence LOWERS the score (0.265 -> 0.254):
# those terms already appear verbatim in the title and snippet, which are quoted
# in full, so restating them only dilutes the embedding.
TITLE_LEAD = "Offre d'emploi"
COMPANY_LEAD = "Poste proposé par"
LOCATION_LEAD = "Lieu"
SCAFFOLDING = (
    SYNTHESIZED_DESCRIPTION_PREFIX,
    TITLE_LEAD,
    COMPANY_LEAD,
    LOCATION_LEAD,
)


def is_synthesized(description: str | None) -> bool:
    """True when `description` was produced by this module."""
    return bool(description) and description.lstrip().startswith(
        SYNTHESIZED_DESCRIPTION_PREFIX
    )


def is_thin(description: str | None, min_chars: int = DEFAULT_MIN_DESCRIPTION_CHARS) -> bool:
    """True when a description is too short to be worth embedding on its own."""
    return len((description or "").strip()) < min_chars


def synthesize_description(
    title: str,
    *,
    company: str | None = None,
    city: str | None = None,
    snippet: str | None = None,
) -> str:
    """Compose a compact French paragraph from the fields the alert provided.

    This is field assembly, not content generation: every non-scaffolding token
    in the result is copied from the arguments. The snippet is quoted in full,
    so any contract or seniority wording the alert carried survives verbatim.
    """
    title = (title or "").strip()
    company = (company or "").strip()
    city = (city or "").strip()
    snippet = (snippet or "").strip()

    segments = [f"{TITLE_LEAD} : {title}."]
    if company:
        segments.append(f"{COMPANY_LEAD} {company}.")
    if city:
        segments.append(f"{LOCATION_LEAD} : {city}.")
    if snippet:
        segments.append(snippet)
    return f"{SYNTHESIZED_DESCRIPTION_PREFIX} " + " ".join(segments)


def enrich_offer(
    offer: OfferRecord, min_chars: int = DEFAULT_MIN_DESCRIPTION_CHARS
) -> OfferRecord:
    """Replace a thin description in place; richer descriptions are left alone.

    Called at ingest time so the synthesised text is what gets stored, hashed
    and later embedded. Returns the same record for convenient chaining.
    """
    if is_synthesized(offer.description) or not is_thin(offer.description, min_chars):
        return offer
    composed = synthesize_description(
        offer.title,
        company=offer.company_name,
        city=offer.city,
        snippet=offer.description,
    )
    if len(composed) > len(offer.description or ""):
        offer.description = composed
    return offer


# ---- backfill / rescore over already-stored offers ----


@dataclass(slots=True)
class BackfillResult:
    source: str
    scanned: int = 0
    updated: int = 0
    unchanged: int = 0
    already_synthesized: int = 0
    skipped_with_application: int = 0
    skipped_degraded: int = 0

    def as_dict(self) -> dict[str, int | str]:
        return {
            "source": self.source,
            "scanned": self.scanned,
            "updated": self.updated,
            "unchanged": self.unchanged,
            "already_synthesized": self.already_synthesized,
            "skipped_with_application": self.skipped_with_application,
            "skipped_degraded": self.skipped_degraded,
        }


@dataclass(slots=True)
class RescoreResult:
    source: str
    cleared: int = 0
    skipped_with_application: int = 0

    def as_dict(self) -> dict[str, int | str]:
        return {
            "source": self.source,
            "cleared": self.cleared,
            "skipped_with_application": self.skipped_with_application,
        }


def source_filter(db: sqlite3.Connection, source: str | None) -> tuple[str, list[int]]:
    """Return an SQL fragment + params restricting a query to one source."""
    if source is None:
        return "", []
    row = db.execute("SELECT id FROM sources WHERE name = ?", (source,)).fetchone()
    if row is None:
        raise ValueError(f"unknown source {source!r}")
    return " AND o.source_id = ?", [int(row["id"])]


def backfill_descriptions(
    db: sqlite3.Connection,
    source: str | None = None,
    min_chars: int = DEFAULT_MIN_DESCRIPTION_CHARS,
    *,
    force: bool = False,
) -> BackfillResult:
    """Regenerate synthesised descriptions for stored offers whose text is thin.

    Idempotent: a second run finds the rows already synthesised (they carry the
    prefix and are no longer thin) and updates nothing. `content_hash` is left
    untouched on purpose — it is the dedup key of the row as it was ingested,
    and alert offers dedup on (source_id, external_id) anyway.

    `force` additionally re-composes rows that already carry the prefix, from the
    row's CURRENT title / company / city. That is the repair path for synthesised
    text written before `reparse-alerts` fixed those fields: the stored paragraph
    still quotes the old wrong values ("Lieu : Recrutement actif."), the backfill
    normally skips it because it carries the prefix, and that stale text is what
    the semantic score embeds. Forcing changes nothing about how the text is
    built — still field assembly, no LLM, no scraping, nothing invented.
    """
    clause, params = source_filter(db, source)
    result = BackfillResult(source=source or "all")

    if not force:
        rows = db.execute(
            "SELECT o.id, o.title, o.description, o.city, c.name AS company_name "
            "FROM offers o LEFT JOIN companies c ON c.id = o.company_id "
            "WHERE length(coalesce(o.description, '')) < ?" + clause,
            [min_chars, *params],
        ).fetchall()
    else:
        # Already-synthesised rows are no longer thin, so length alone will not
        # find them. Match the prefix the same way `is_synthesized` does.
        prefix_test = "substr(ltrim(coalesce(o.description, '')), 1, ?) = ?"
        prefix_params = [len(SYNTHESIZED_DESCRIPTION_PREFIX), SYNTHESIZED_DESCRIPTION_PREFIX]
        # Rails, as in `rescore` / `reparse-alerts`: an offer that already has an
        # application had its text read by a human whose decision the state
        # machine now owns. Rewriting under that decision is not ours to do.
        result.skipped_with_application = int(
            db.execute(
                "SELECT count(*) AS n FROM offers o "
                "JOIN applications a ON a.offer_id = o.id "
                f"WHERE (length(coalesce(o.description, '')) < ? OR {prefix_test})" + clause,
                [min_chars, *prefix_params, *params],
            ).fetchone()["n"]
        )
        rows = db.execute(
            "SELECT o.id, o.title, o.description, o.city, c.name AS company_name "
            "FROM offers o "
            "LEFT JOIN companies c ON c.id = o.company_id "
            "LEFT JOIN applications a ON a.offer_id = o.id "
            "WHERE a.offer_id IS NULL "
            f"  AND (length(coalesce(o.description, '')) < ? OR {prefix_test})" + clause,
            [min_chars, *prefix_params, *params],
        ).fetchall()

    for row in rows:
        result.scanned += 1
        current = row["description"]
        stale = is_synthesized(current)
        if stale and not force:
            result.already_synthesized += 1
            continue

        if stale:
            # No snippet: the tail of a synthesised paragraph is this module's own
            # scaffolding plus the values it quoted when it ran. Re-quoting it
            # would fold the stale company/city straight back into the new text.
            if not (row["title"] or "").strip():
                # Nothing left to anchor the offer on — the regenerated text
                # cannot be better than what is stored, so keep what is stored.
                result.skipped_degraded += 1
                continue
            composed = synthesize_description(
                row["title"], company=row["company_name"], city=row["city"]
            )
            if composed == current:
                result.unchanged += 1
                continue
        else:
            composed = synthesize_description(
                row["title"],
                company=row["company_name"],
                city=row["city"],
                snippet=current,
            )
            if len(composed) <= len(current or ""):
                result.unchanged += 1
                continue

        db.execute("UPDATE offers SET description = ? WHERE id = ?", (composed, row["id"]))
        result.updated += 1

    db.commit()
    log.info("backfill-descriptions: %s", result.as_dict())
    return result


def clear_match_scores(db: sqlite3.Connection, source: str | None = None) -> RescoreResult:
    """Drop match_scores rows so the next `score` pass re-evaluates those offers.

    Offers that already have an application row are left alone entirely: their
    scores back a human decision that is now owned by the state machine. Nothing
    here touches `applications`, statuses or events.
    """
    clause, params = source_filter(db, source)
    selectable = (
        "SELECT o.id FROM offers o "
        "LEFT JOIN applications a ON a.offer_id = o.id "
        "WHERE a.offer_id IS NULL" + clause
    )

    result = RescoreResult(source=source or "all")
    result.skipped_with_application = int(
        db.execute(
            "SELECT count(*) AS n FROM offers o "
            "JOIN applications a ON a.offer_id = o.id "
            "JOIN match_scores m ON m.offer_id = o.id "
            "WHERE 1 = 1" + clause,
            params,
        ).fetchone()["n"]
    )
    cur = db.execute(
        f"DELETE FROM match_scores WHERE offer_id IN ({selectable})",
        params,
    )
    result.cleared = int(cur.rowcount)
    db.commit()
    log.info("rescore: %s", result.as_dict())
    return result
