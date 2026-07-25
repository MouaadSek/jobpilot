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


def _get_or_create_company(
    db: sqlite3.Connection, company: CompanyRecord, cache: dict[str, int]
) -> tuple[int, bool]:
    key = " ".join(company.name.lower().split())
    if key in cache:
        return cache[key], False
    row = db.execute(
        "SELECT id FROM companies WHERE lower(name) = ? LIMIT 1", (key,)
    ).fetchone()
    if row is not None:
        cache[key] = row["id"]
        return row["id"], False
    cur = db.execute(
        "INSERT INTO companies (name, siren, domain, size_bucket, sector, city, "
        "country, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (company.name, company.siren, company.domain, company.size_bucket,
         company.sector, company.city, company.country, company.notes),
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
        " contact_email) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            sid, company_id, offer.external_id, offer.url, offer.title,
            offer.description, offer.contract_type, offer.duration_months,
            offer.city, offer.remote_policy, offer.salary_min, offer.salary_max,
            offer.stack_tags_json, offer.posted_at, _utc_now(), offer.hash,
            offer.contact_email,
        ),
    )
    return cur.rowcount > 0


def ingest_source(db: sqlite3.Connection, src: Source) -> IngestResult:
    """Run one source end to end. Commits once at the end for atomicity."""
    sid = source_id(db, src.name)
    result = IngestResult(source=src.name)
    company_cache: dict[str, int] = {}

    # Companies-likely-to-hire (used by later cold-mail phase) go in first.
    for company in src.fetch_companies():
        _, created = _get_or_create_company(db, company, company_cache)
        if created:
            result.companies_created += 1

    for offer in src.fetch_offers():
        result.fetched += 1
        company_id: int | None = None
        if offer.company_name:
            company_id, created = _get_or_create_company(
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
    db.commit()
    log.info("ingest %s: %s", src.name, result.as_dict())
    return result
