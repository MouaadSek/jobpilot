"""Normalized DTOs that every source emits, decoupled from source-specific JSON."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

CONTRACT_TYPES = {"stage", "alternance", "cdi", "cdd", "freelance", "unknown"}
REMOTE_POLICIES = {"onsite", "hybrid", "full_remote", "unknown"}


def content_hash(title: str, company: str, description: str) -> str:
    """sha256(lower(title + company + first 500 chars of description)).

    This is the dedup key enforced by offers.content_hash UNIQUE. Keep the
    normalization (lowercase, whitespace-collapsed) identical across sources so
    the same offer cross-posted collapses to one row.
    """
    def _n(s: str) -> str:
        return " ".join((s or "").lower().split())

    basis = _n(title) + _n(company) + _n((description or "")[:500])
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()


@dataclass(slots=True)
class CompanyRecord:
    name: str
    siren: str | None = None
    domain: str | None = None
    size_bucket: str | None = None
    sector: str | None = None
    city: str | None = None
    country: str = "FR"
    notes: str | None = None


@dataclass(slots=True)
class OfferRecord:
    """One normalized offer, ready to insert into the offers table."""

    external_id: str | None
    url: str
    title: str
    company_name: str | None = None
    description: str | None = None
    contract_type: str = "unknown"
    duration_months: int | None = None
    city: str | None = None
    remote_policy: str = "unknown"
    salary_min: int | None = None
    salary_max: int | None = None
    stack_tags: list[str] = field(default_factory=list)
    posted_at: str | None = None  # ISO 8601 UTC

    def normalized(self) -> OfferRecord:
        """Coerce enum-constrained fields to legal values (schema CHECK safety)."""
        ct = (self.contract_type or "unknown").lower()
        if ct not in CONTRACT_TYPES:
            ct = "unknown"
        rp = (self.remote_policy or "unknown").lower()
        if rp not in REMOTE_POLICIES:
            rp = "unknown"
        self.contract_type = ct
        self.remote_policy = rp
        return self

    @property
    def hash(self) -> str:
        return content_hash(self.title, self.company_name or "", self.description or "")

    @property
    def stack_tags_json(self) -> str:
        return json.dumps(self.stack_tags, ensure_ascii=False)
