"""La Bonne Alternance API client (current API: api.apprentissage.beta.gouv.fr).

The legacy public /api/v1/jobs endpoint (caller-email auth) was decommissioned
(HTTP 404). The current job search API requires a Bearer API key (register free
at https://api.apprentissage.beta.gouv.fr/inscription) and returns, per set of
ROME codes around a location:
  - `jobs`:       alternance offers (partners + LBA) -> offers table
  - `recruiters`: companies statistically likely to hire -> companies table

Response fields are defensively mapped and covered by fixture-based tests.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import httpx

from jobpilot.config import MissingCredentialError, Settings
from jobpilot.logging_conf import get_logger
from jobpilot.models import CompanyRecord, OfferRecord
from jobpilot.ratelimit import RateLimiter, with_backoff
from jobpilot.sources.base import Source

log = get_logger("labonnealternance")

# ROME codes closest to IT / cybersecurity (LBA filters by ROME, not free text).
# M1802 expertise/support SI (incl. security), M1810 exploitation SI,
# M1805 études/dev, M1806 conseil/MOA SI.
DEFAULT_ROMES = ["M1802", "M1810", "M1805", "M1806"]

# (label, latitude, longitude, radius_km) — search points near target cities.
DEFAULT_GEOS: list[tuple[str, float, float, int]] = [
    ("Lille", 50.6292, 3.0573, 60),
    ("Paris", 48.8566, 2.3522, 40),
]


class LaBonneAlternanceSource(Source):
    name = "labonnealternance"

    def __init__(
        self,
        settings: Settings,
        *,
        romes: list[str] | None = None,
        geos: list[tuple[str, float, float, int]] | None = None,
        search_url: str | None = None,
        api_key: str | None = None,
        client: httpx.Client | None = None,
        rate_limiter: RateLimiter | None = None,
    ) -> None:
        key = api_key or settings.lba_api_key
        if not key:
            raise MissingCredentialError(
                "La Bonne Alternance requires LBA_API_KEY in .env. The legacy "
                "caller-email API is retired; register for a key at "
                "https://api.apprentissage.beta.gouv.fr/inscription."
            )
        self._key = key
        self._search_url = search_url or settings.lba_search_url
        self._romes = romes if romes is not None else DEFAULT_ROMES
        self._geos = geos if geos is not None else DEFAULT_GEOS
        self._client = client or httpx.Client(
            timeout=30.0,
            headers={"User-Agent": "JobPilot/0.1 (personal job pipeline)",
                     "Accept": "application/json"},
        )
        self._rl = rate_limiter or RateLimiter(min_interval_s=1.0)
        self._last_payloads: list[dict[str, Any]] = []

    # ----- HTTP -----

    def _get_jobs(self, lat: float, lon: float, radius: int) -> dict[str, Any]:
        params = {
            "latitude": f"{lat}",
            "longitude": f"{lon}",
            "radius": str(radius),
            "romes": ",".join(self._romes),
        }

        def _do() -> httpx.Response:
            resp = self._client.get(
                self._search_url, params=params,
                headers={"Authorization": f"Bearer {self._key}"},
            )
            resp.raise_for_status()
            return resp

        self._rl.wait("api.apprentissage.beta.gouv.fr")
        return with_backoff(_do).json()

    def _fetch_all(self) -> list[dict[str, Any]]:
        payloads = []
        for label, lat, lon, radius in self._geos:
            log.info("LBA fetch %s (r=%dkm)", label, radius)
            payloads.append(self._get_jobs(lat, lon, radius))
        self._last_payloads = payloads
        return payloads

    # ----- Source interface -----

    def fetch_offers(self) -> Iterator[OfferRecord]:
        seen: set[str] = set()
        for payload in self._fetch_all():
            for raw in payload.get("jobs", []) or []:
                rec = map_offer(raw)
                if rec is None:
                    continue
                key = rec.external_id or rec.hash
                if key in seen:
                    continue
                seen.add(key)
                yield rec

    def fetch_companies(self) -> Iterator[CompanyRecord]:
        payloads = self._last_payloads or self._fetch_all()
        seen: set[str] = set()
        for payload in payloads:
            for raw in payload.get("recruiters", []) or []:
                rec = map_company(raw)
                if rec is None:
                    continue
                key = (rec.siren or rec.name).lower()
                if key in seen:
                    continue
                seen.add(key)
                yield rec


# ----- mapping (pure, unit-tested) -----

def _dig(node: Any, *path: str) -> Any:
    cur: Any = node
    for p in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(p)
    return cur


def _is_alternance(contract_types: Any) -> bool:
    if not isinstance(contract_types, list):
        return False
    blob = " ".join(str(t).lower() for t in contract_types)
    return any(k in blob for k in ("apprentiss", "professionnalis", "alternance"))


def map_offer(node: dict[str, Any]) -> OfferRecord | None:
    title = _dig(node, "offer", "title")
    url = _dig(node, "apply", "url")
    if not title or not url:
        return None

    skills = _dig(node, "offer", "desired_skills") or []
    tags = [s for s in skills if isinstance(s, str)]
    if not tags:  # sometimes rome codes are the only structured tags
        tags = [c for c in (_dig(node, "offer", "rome_codes") or [])
                if isinstance(c, str)]

    rec = OfferRecord(
        external_id=_first(_dig(node, "identifier", "id"),
                           _dig(node, "identifier", "partner_job_id")),
        url=str(url),
        title=str(title),
        company_name=_first(_dig(node, "workplace", "name")),
        description=_dig(node, "offer", "description"),
        contract_type="alternance"
        if _is_alternance(_dig(node, "contract", "type")) else "unknown",
        city=_first(_dig(node, "workplace", "location", "address")),
        posted_at=_first(_dig(node, "offer", "publication", "creation")),
        stack_tags=tags,
    )
    return rec.normalized()


def map_company(node: dict[str, Any]) -> CompanyRecord | None:
    name = _dig(node, "workplace", "name")
    if not name:
        return None
    return CompanyRecord(
        name=str(name),
        siren=_first(_dig(node, "workplace", "siret")),
        city=_first(_dig(node, "workplace", "location", "address")),
        sector=_first(_dig(node, "workplace", "domain", "naf", "label")),
        size_bucket=_first(_dig(node, "workplace", "size")),
    )


def _first(*vals: Any) -> str | None:
    for v in vals:
        if v:
            return str(v)
    return None
