"""France Travail 'Offres d'emploi v2' API client.

OAuth2 client_credentials against francetravail.io. Search endpoint returns 200
(all results) or 206 (partial content, paginated via the `range` param). We page
until exhausted or the API's hard ceiling, mapping each offer into OfferRecord.

Search semantics verified live against the API + /referentiel:
- `motsCles` is ANDed across comma-separated terms, so we issue one query PER
  keyword (filter x keyword) and dedup offers by id across all of them.
- Alternance = natureContrat E2 (apprentissage) + FS (professionnalisation).
- FT's Offres v2 has NO stage contract code (typeContrat=STG -> HTTP 400), so
  stage coverage is left to other sources (La Bonne Alternance, ATS).
- `publieeDepuis` only accepts 1, 3, 7, 14, or 31 days.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from typing import Any

import httpx

from jobpilot.config import Settings
from jobpilot.logging_conf import get_logger
from jobpilot.models import OfferRecord
from jobpilot.ratelimit import RateLimiter, with_backoff
from jobpilot.sources.base import Source
from jobpilot.sources.oauth import ClientCredentialsToken

log = get_logger("france_travail")

# FT region codes: Hauts-de-France = 32, Île-de-France = 11.
REGION_HDF = "32"
REGION_IDF = "11"

KEYWORDS = ["cybersécurité", "SOC", "sécurité cloud", "DevSecOps", "pentest"]

# Region + contract filters, combined with each keyword at query time. Alternance
# only (natureContrat E2,FS); FT has no stage contract. Confirmed via /referentiel.
DEFAULT_FILTERS: list[dict[str, str]] = [
    {"region": REGION_HDF, "natureContrat": "E2,FS"},
    {"region": REGION_IDF, "natureContrat": "E2,FS"},
]

_ALLOWED_PUBLISHED_SINCE = {1, 3, 7, 14, 31}
_PAGE_SIZE = 100  # FT max is 150/page; 100 keeps ranges tidy.
_MAX_TOTAL = 1000  # per query safety ceiling; FT hard cap is 3149.
_DURATION_RE = re.compile(r"(\d+)\s*mois", re.IGNORECASE)


class FranceTravailSource(Source):
    name = "france_travail"

    def __init__(
        self,
        settings: Settings,
        *,
        filters: list[dict[str, str]] | None = None,
        keywords: list[str] | None = None,
        published_since_days: int | None = None,
        client: httpx.Client | None = None,
        token: ClientCredentialsToken | None = None,
        rate_limiter: RateLimiter | None = None,
    ) -> None:
        client_id, client_secret = settings.require_ft_credentials()
        if published_since_days is None:
            published_since_days = settings.ft_published_since
        if published_since_days not in _ALLOWED_PUBLISHED_SINCE:
            raise ValueError(
                f"published_since_days must be one of {sorted(_ALLOWED_PUBLISHED_SINCE)}"
            )
        self._settings = settings
        self._filters = filters if filters is not None else DEFAULT_FILTERS
        self._keywords = keywords if keywords is not None else KEYWORDS
        self._published_since = published_since_days
        self._client = client or httpx.Client(
            timeout=30.0,
            headers={"User-Agent": "JobPilot/0.1 (personal job pipeline)",
                     "Accept": "application/json"},
        )
        self._token = token or ClientCredentialsToken(
            settings.ft_token_url, client_id, client_secret, settings.ft_scope,
            client=self._client,
        )
        # API, not scraper: a modest delay is enough; backoff handles 429s.
        self._rl = rate_limiter or RateLimiter(min_interval_s=1.0)

    # ----- fetching -----

    def fetch_offers(self) -> Iterator[OfferRecord]:
        seen: set[str] = set()
        # motsCles is ANDed, so one query per keyword, ORed via dedup by offer id.
        for flt in self._filters:
            for keyword in self._keywords:
                for raw in self._paginate({**flt, "motsCles": keyword}):
                    oid = str(raw.get("id", ""))
                    if oid and oid in seen:
                        continue
                    if oid:
                        seen.add(oid)
                    rec = map_offer(raw)
                    if rec is not None:
                        yield rec

    def _paginate(self, base_params: dict[str, str]) -> Iterator[dict[str, Any]]:
        start = 0
        while start < _MAX_TOTAL:
            end = start + _PAGE_SIZE - 1
            params = {
                "publieeDepuis": str(self._published_since),
                "range": f"{start}-{end}",
                "sort": "1",  # by date, most recent first
                **base_params,
            }
            self._rl.wait("francetravail.io")
            resp = self._request(params)
            if resp.status_code == 204:  # no content
                return
            body = resp.json()
            results = body.get("resultats", []) or []
            yield from results
            if resp.status_code == 200 or len(results) < _PAGE_SIZE:
                return  # 200 = complete set delivered; short page = last page
            start += _PAGE_SIZE

    def _request(self, params: dict[str, str]) -> httpx.Response:
        def _do() -> httpx.Response:
            resp = self._client.get(
                self._settings.ft_search_url,
                params=params,
                headers=self._token.auth_header(),
            )
            # 200 and 206 are both success (206 = partial content / more pages).
            if resp.status_code not in (200, 204, 206):
                resp.raise_for_status()
            return resp

        return with_backoff(_do)


# ----- mapping (pure, unit-tested against fixtures) -----

def _first_nonempty(*vals: Any) -> str | None:
    for v in vals:
        if v:
            return str(v)
    return None


def _map_contract(raw: dict[str, Any]) -> str:
    if raw.get("alternance") is True:
        return "alternance"
    nature = (raw.get("natureContrat") or "").lower()
    tc = (raw.get("typeContrat") or "").upper()
    tcl = (raw.get("typeContratLibelle") or "").lower()
    if "apprentis" in nature or "professionnalis" in nature or "alternance" in nature:
        return "alternance"
    if tc == "STG" or "stage" in tcl:
        return "stage"
    if tc == "CDI":
        return "cdi"
    if tc == "CDD":
        return "cdd"
    if "alternance" in tcl:
        return "alternance"
    return "unknown"


def _map_duration_months(raw: dict[str, Any]) -> int | None:
    """Parse '... - 12 Mois' style durations from typeContratLibelle."""
    m = _DURATION_RE.search(raw.get("typeContratLibelle") or "")
    return int(m.group(1)) if m else None


def map_offer(raw: dict[str, Any]) -> OfferRecord | None:
    """Map one FT offre JSON object to an OfferRecord, or None if unusable."""
    title = raw.get("intitule")
    if not title:
        return None

    origine = raw.get("origineOffre") or {}
    url = _first_nonempty(
        origine.get("urlOrigine"),
        f"https://candidat.francetravail.fr/offres/recherche/detail/{raw.get('id')}"
        if raw.get("id") else None,
    )
    if not url:
        return None

    entreprise = raw.get("entreprise") or {}
    lieu = raw.get("lieuTravail") or {}
    competences = raw.get("competences") or []
    stack_tags = [
        c["libelle"] for c in competences
        if isinstance(c, dict) and c.get("libelle")
    ]

    rec = OfferRecord(
        external_id=_first_nonempty(raw.get("id")),
        url=url,
        title=title,
        company_name=_first_nonempty(entreprise.get("nom")),
        description=raw.get("description"),
        contract_type=_map_contract(raw),
        duration_months=_map_duration_months(raw),
        city=_first_nonempty(lieu.get("libelle")),
        posted_at=_first_nonempty(raw.get("dateCreation")),
        stack_tags=stack_tags,
    )
    return rec.normalized()
