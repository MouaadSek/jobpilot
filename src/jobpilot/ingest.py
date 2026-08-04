"""Ingestion orchestrator: pull normalized records from a Source into the DB.

Idempotent by design (constitution rule): offers are inserted with INSERT OR
IGNORE against the content_hash / (source_id, external_id) UNIQUE constraints, so
re-running never duplicates rows. Companies are deduped by normalized name.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime

from jobpilot.db import source_id
from jobpilot.logging_conf import get_logger
from jobpilot.models import CompanyRecord, OfferRecord
from jobpilot.sources.base import Source

log = get_logger("ingest")


@dataclass(slots=True)
class IngestResult:
    source: str
    fetched: int = 0
    inserted: int = 0
    duplicates: int = 0
    companies_created: int = 0

    def as_dict(self) -> dict[str, int | str]:
        return {
            "source": self.source,
            "fetched": self.fetched,
            "inserted": self.inserted,
            "duplicates": self.duplicates,
            "companies_created": self.companies_created,
        }


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


#: An error message is for a human reading one table cell, not for forensics —
#: the traceback is already in logs/. Truncated so one exploded HTTP body cannot
#: make the Planification table unreadable.
_ERROR_EXCERPT = 240


def record_run(
    db: sqlite3.Connection,
    sid: int,
    *,
    started_at: str,
    result: IngestResult | None,
    error: str | None = None,
) -> None:
    """Append one row to source_runs. Does not commit; the caller owns that.

    A failed run keeps its ``fetched`` count — the API really did return that
    many records — and zeroes the rest, because the caller rolls the transaction
    back before this is written, so nothing it inserted survived.
    """

    db.execute(
        "INSERT INTO source_runs "
        "(source_id, started_at, finished_at, fetched, inserted, duplicates, "
        " companies_created, error) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            sid,
            started_at,
            _utc_now(),
            result.fetched if result else 0,
            result.inserted if error is None and result else 0,
            result.duplicates if error is None and result else 0,
            result.companies_created if error is None and result else 0,
            error[:_ERROR_EXCERPT] if error else None,
        ),
    )


def _backfill_company_source(
    db: sqlite3.Connection, company_id: int, source: str | None
) -> None:
    """Teach an existing company row where it came from, once.

    A company first seen as an offer's employer is stored with ``source`` NULL.
    When a sourcing provider later returns that same company as an outreach
    target, the row has to learn its provenance or it never appears in
    ``contacts --targets``. The ``source IS NULL`` guard makes this a backfill
    and never a rewrite: the first provider to claim a company keeps the claim.
    """

    if source is None:
        return
    db.execute(
        "UPDATE companies SET source = ? WHERE id = ? AND source IS NULL",
        (source, company_id),
    )


def get_or_create_company(
    db: sqlite3.Connection, company: CompanyRecord, cache: dict[str, int]
) -> tuple[int, bool]:
    key = " ".join(company.name.lower().split())
    if key in cache:
        _backfill_company_source(db, cache[key], company.source)
        return cache[key], False
    row = db.execute(
        "SELECT id FROM companies WHERE lower(name) = ? LIMIT 1", (key,)
    ).fetchone()
    if row is None and company.siren:
        # companies.siren is UNIQUE, and one firm trades under several names, so
        # a name miss is not proof it is new. Checking the identifier keeps the
        # insert below from raising on a company we already hold.
        row = db.execute(
            "SELECT id FROM companies WHERE siren = ? LIMIT 1", (company.siren,)
        ).fetchone()
    if row is not None:
        cache[key] = row["id"]
        _backfill_company_source(db, row["id"], company.source)
        return row["id"], False
    cur = db.execute(
        "INSERT INTO companies (name, siren, domain, size_bucket, sector, city, "
        "country, notes, source) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (company.name, company.siren, company.domain, company.size_bucket,
         company.sector, company.city, company.country, company.notes,
         company.source),
    )
    cid = int(cur.lastrowid)
    cache[key] = cid
    return cid, True


def _insert_offer(
    db: sqlite3.Connection, sid: int, company_id: int | None, offer: OfferRecord
) -> bool:
    """INSERT OR IGNORE one offer. Returns True if a new row was created."""
    cur = db.execute(
        "INSERT OR IGNORE INTO offers "
        "(source_id, company_id, external_id, url, title, description, "
        " contract_type, duration_months, city, remote_policy, salary_min, "
        " salary_max, stack_tags, posted_at, scraped_at, content_hash, "
        " contact_email, easy_apply) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            sid, company_id, offer.external_id, offer.url, offer.title,
            offer.description, offer.contract_type, offer.duration_months,
            offer.city, offer.remote_policy, offer.salary_min, offer.salary_max,
            offer.stack_tags_json, offer.posted_at, _utc_now(), offer.hash,
            offer.contact_email, int(offer.easy_apply),
        ),
    )
    return cur.rowcount > 0


def ingest_source(db: sqlite3.Connection, src: Source) -> IngestResult:
    """Run one source end to end. Commits once at the end for atomicity.

    Every outcome is recorded in source_runs, success or failure, because this
    is the only place that knows both. A source that has stopped returning
    anything keeps ticking sources.last_run_at forward and looks healthy from
    the outside — WTTJ did that for a week — so the failure path commits its
    own row rather than re-raising into silence.

    One caution on the transaction: it opens at the first insert and closes at
    the commit below, which means it is held across ``fetch_offers``, and that
    is a paginated HTTP walk with rate limiting in it. Under WAL a reader is
    never blocked by it, but a second writer — the dashboard generating an
    application while the daemon ingests — waits on it for as long as the walk
    takes, and gives up after db.BUSY_TIMEOUT_MS.
    """
    sid = source_id(db, src.name)
    started_at = _utc_now()
    result = IngestResult(source=src.name)
    company_cache: dict[str, int] = {}

    try:
        # Companies-likely-to-hire (used by later cold-mail phase) go in first.
        for company in src.fetch_companies():
            _, created = get_or_create_company(db, company, company_cache)
            if created:
                result.companies_created += 1

        for offer in src.fetch_offers():
            result.fetched += 1
            company_id: int | None = None
            if offer.company_name:
                company_id, created = get_or_create_company(
                    db, CompanyRecord(name=offer.company_name), company_cache
                )
                if created:
                    result.companies_created += 1
            if _insert_offer(db, sid, company_id, offer):
                result.inserted += 1
            else:
                result.duplicates += 1

        db.execute(
            "UPDATE sources SET last_run_at = ? WHERE id = ?", (_utc_now(), sid)
        )
        record_run(db, sid, started_at=started_at, result=result)
        db.commit()
    except Exception as exc:
        # Roll the partial ingest back first, so the row written next is the
        # only thing this run leaves behind — and so its zeros are true.
        db.rollback()
        record_run(
            db, sid, started_at=started_at, result=result, error=f"{type(exc).__name__}: {exc}"
        )
        db.commit()
        log.exception("ingest %s failed after %d fetched", src.name, result.fetched)
        raise

    log.info("ingest %s: %s", src.name, result.as_dict())
    return result
