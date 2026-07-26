"""Re-derive alert card fields (company / city / workplace / easy-apply) in place.

Why this exists
---------------
Before Task 20 the alert parser filled `company` and `city` positionally: it
popped the next available card chunk into each. On real LinkedIn mail those
chunks are interface text, so 85 of 112 stored `linkedin_alert` offers carried a
junk location ("Recrutement actif", "1 relation", "Candidature simplifiée") and
were rejected by the hard filter on location before they were ever scored.

Ingestion is fixed going forward. This module repairs the rows already stored.

What is still recoverable
-------------------------
The alert emails themselves are NOT retained — nothing in the schema keeps the
raw message. What *is* retained is the card text the old parser mis-filed: the
"Company · City (Workplace)" line landed in `companies.name` (65 of 112 rows on
the real database), and the synthesised description quotes both fields verbatim.
That is enough to re-run the structural parse offline.

Where it is not enough — the card line was never captured and `city` holds only
chrome — the true location cannot be reconstructed. Those rows have the junk
cleared to NULL (the hard filter reads NULL as "do not reject", junk as a
guaranteed rejection) and are counted as `unrecoverable`. Re-ingesting is the
way to recover them properly; the alert mail is still in the mailbox.

Rails
-----
Touches `offers` and `companies` only. No `applications` row, status or event is
read or written, and any offer that already has an application is skipped
entirely — its fields back a human decision now owned by the state machine,
exactly as `rescore` treats its scores.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from jobpilot.descriptions import source_filter
from jobpilot.ingest import get_or_create_company
from jobpilot.logging_conf import get_logger
from jobpilot.models import CompanyRecord
from jobpilot.sources.email_alerts import (
    is_noise,
    is_title_echo,
    parse_card_line,
    scrub_chunk,
    split_workplace,
)

log = get_logger("reparse")

# The sources whose offers come from job-alert emails and therefore have card
# text worth re-parsing. Other sources deliver structured fields already.
ALERT_SOURCES: tuple[str, ...] = ("linkedin_alert", "indeed_alert")


@dataclass(slots=True)
class ReparseResult:
    source: str
    scanned: int = 0
    updated: int = 0
    unchanged: int = 0
    skipped_with_application: int = 0
    noise_cleared: int = 0
    unrecoverable: int = 0

    def as_dict(self) -> dict[str, int | str]:
        return {
            "source": self.source,
            "scanned": self.scanned,
            "updated": self.updated,
            "unchanged": self.unchanged,
            "skipped_with_application": self.skipped_with_application,
            "noise_cleared": self.noise_cleared,
            "unrecoverable": self.unrecoverable,
        }


@dataclass(slots=True)
class _Derived:
    company: str | None
    city: str | None
    remote_policy: str
    easy_apply: bool
    had_noise: bool
    unrecoverable: bool


def derive_fields(
    company: str | None,
    city: str | None,
    description: str | None = None,
    title: str | None = None,
) -> _Derived:
    """Re-derive one offer's card fields from the text that was stored for it.

    Pure, so it is testable without a database. Invents nothing: a value that
    cannot be read out of the stored text comes back None.
    """
    stored_company = " ".join((company or "").split()) or None
    stored_city = " ".join((city or "").split()) or None

    # A stored city that merely restates the offer's title is a mis-filed title,
    # not a location. Dropping it is a textual identity check against the row's
    # own title — no place name is being guessed at, here or below.
    if is_title_echo(stored_city, title):
        stored_city = None
    if is_title_echo(stored_company, title):
        stored_company = None

    had_noise = bool(
        (stored_company and is_noise(stored_company))
        or (stored_city and is_noise(stored_city))
    )

    new_company: str | None = None
    new_city: str | None = None
    policy: str | None = None

    # Easy Apply is scanned across every retained field, independently of which
    # one turns out to hold the card line: the old reader scattered the chunks,
    # so the marker and the "Company · City" line rarely share a field. The
    # synthesised description counts too — it quoted the card snippet verbatim.
    easy_apply = any(
        scrub_chunk(candidate)[1]
        for candidate in (stored_company, stored_city, description)
    )

    # The "Company · City (Workplace)" line is the reliable signal. It may sit
    # in either stored field, because the old reader placed it positionally.
    for candidate in (stored_company, stored_city):
        card = parse_card_line(candidate)
        if card is None:
            continue
        new_company = card.company
        new_city = card.city
        policy = card.remote_policy
        break

    # No card line: fall back to the stored fields themselves, noise removed.
    if new_company is None and new_city is None:
        new_company, _ = scrub_chunk(stored_company)
        new_city, _ = scrub_chunk(stored_city)
        new_city, policy = split_workplace(new_city)

    return _Derived(
        company=new_company,
        city=new_city,
        remote_policy=policy or "unknown",
        easy_apply=easy_apply,
        had_noise=had_noise,
        # The city was chrome and no card line was retained: genuinely lost.
        unrecoverable=bool(stored_city and is_noise(stored_city) and new_city is None),
    )


def _alert_source_clause(
    db: sqlite3.Connection, source: str | None
) -> tuple[str, list[int]]:
    """Restrict to one alert source, or to all of them when none is named."""
    if source is not None:
        if source not in ALERT_SOURCES:
            raise ValueError(
                f"{source!r} is not an alert source; expected one of "
                f"{', '.join(ALERT_SOURCES)}"
            )
        return source_filter(db, source)

    names = ", ".join("?" * len(ALERT_SOURCES))
    ids = [
        int(row["id"])
        for row in db.execute(
            f"SELECT id FROM sources WHERE name IN ({names})", ALERT_SOURCES
        )
    ]
    if not ids:
        return " AND 0", []
    return f" AND o.source_id IN ({', '.join('?' * len(ids))})", ids


def reparse_alerts(
    db: sqlite3.Connection, source: str | None = None
) -> ReparseResult:
    """Re-derive company / city / workplace / easy-apply for stored alert offers.

    Idempotent: a second run re-derives the same values from the now-clean text
    and updates nothing.
    """
    clause, params = _alert_source_clause(db, source)
    result = ReparseResult(source=source or "all alert sources")

    result.skipped_with_application = int(
        db.execute(
            "SELECT count(*) AS n FROM offers o "
            "JOIN applications a ON a.offer_id = o.id "
            "WHERE 1 = 1" + clause,
            params,
        ).fetchone()["n"]
    )

    rows = db.execute(
        "SELECT o.id, o.title, o.city, o.remote_policy, o.easy_apply, o.description, "
        "       o.company_id, c.name AS company_name "
        "FROM offers o "
        "LEFT JOIN companies c ON c.id = o.company_id "
        "LEFT JOIN applications a ON a.offer_id = o.id "
        "WHERE a.offer_id IS NULL" + clause,
        params,
    ).fetchall()

    company_cache: dict[str, int] = {}
    for row in rows:
        result.scanned += 1
        derived = derive_fields(
            row["company_name"], row["city"], row["description"], row["title"]
        )
        if derived.had_noise:
            result.noise_cleared += 1
        if derived.unrecoverable:
            result.unrecoverable += 1

        company_id = row["company_id"]
        if derived.company:
            company_id, _ = get_or_create_company(
                db, CompanyRecord(name=derived.company), company_cache
            )

        # Re-deriving must never destroy what an earlier pass already extracted.
        # Once "(Hybride)" has been split off into remote_policy the stored
        # location no longer mentions it, so a second run reads "unknown" — that
        # is absence of evidence, not evidence of onsite. Same for easy_apply.
        stored_policy = row["remote_policy"] or "unknown"
        policy = derived.remote_policy if derived.remote_policy != "unknown" else stored_policy
        easy_apply = derived.easy_apply or bool(row["easy_apply"])

        changed = (
            company_id != row["company_id"]
            or derived.city != row["city"]
            or policy != stored_policy
            or int(easy_apply) != int(row["easy_apply"] or 0)
        )
        if not changed:
            result.unchanged += 1
            continue

        db.execute(
            "UPDATE offers SET company_id = ?, city = ?, remote_policy = ?, "
            "easy_apply = ? WHERE id = ?",
            (company_id, derived.city, policy, int(easy_apply), row["id"]),
        )
        result.updated += 1

    db.commit()
    log.info("reparse-alerts: %s", result.as_dict())
    return result
