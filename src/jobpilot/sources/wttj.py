"""Welcome to the Jungle (WTTJ) ingestion via its Algolia search endpoint.

WTTJ powers job search with Algolia. We query the index directly (JSON API, no
HTML scraping) with cyber/security keywords and map hits into offers. The public
Algolia search key is injected client-side and rotates, so it is treated as a
credential (WTTJ_API_KEY in .env); the app id and index have overridable defaults.

Hit fields vary, so mapping is defensive and covered by fixture tests. Confirm the
app id / index / key against the live site if WTTJ changes them.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import httpx

from jobpilot.config import MissingCredentialError, Settings
from jobpilot.logging_conf import get_logger
from jobpilot.models import OfferRecord
from jobpilot.ratelimit import RateLimiter, with_backoff
from jobpilot.sources.base import Source

log = get_logger("wttj")

KEYWORDS = ["cybersécurité", "SOC", "sécurité cloud", "DevSecOps", "pentest"]

# WTTJ Algolia contract codes -> our schema's contract_type enum.
_CONTRACT_MAP = {
    "INTERNSHIP": "stage",
    "APPRENTICESHIP": "alternance",
    "FULL_TIME": "cdi",
    "PART_TIME": "cdi",
    "TEMPORARY": "cdd",
    "FIXED_TERM": "cdd",
    "FREELANCE": "freelance",
    "VIE": "cdd",
}

_HITS_PER_PAGE = 50
_MAX_PAGES = 3  # per keyword safety ceiling


class WelcomeToTheJungleSource(Source):
    name = "wttj"

    def __init__(
        self,
        settings: Settings,
        *,
        keywords: list[str] | None = None,
        app_id: str | None = None,
        api_key: str | None = None,
        index: str | None = None,
        client: httpx.Client | None = None,
        rate_limiter: RateLimiter | None = None,
    ) -> None:
        key = api_key or settings.wttj_api_key
        if not key:
            raise MissingCredentialError(
                "WTTJ requires WTTJ_API_KEY in .env (the public Algolia search key "
                "from welcometothejungle.com; it rotates, so grab the current one). "
                "Optionally override WTTJ_APP_ID / WTTJ_INDEX."
            )
        self._app_id = app_id or settings.wttj_app_id
        self._api_key = key
        self._index = index or settings.wttj_index
        self._keywords = keywords if keywords is not None else KEYWORDS
        self._url = (
            f"https://{self._app_id}-dsn.algolia.net/1/indexes/{self._index}/query"
        )
        self._client = client or httpx.Client(
            timeout=30.0,
            headers={
                "User-Agent": "JobPilot/0.1 (personal job pipeline)",
                "X-Algolia-Application-Id": self._app_id,
                "X-Algolia-API-Key": self._api_key,
                "Content-Type": "application/json",
            },
        )
        self._rl = rate_limiter or RateLimiter(min_interval_s=1.0)

    def fetch_offers(self) -> Iterator[OfferRecord]:
        seen: set[str] = set()
        for keyword in self._keywords:
            for page in range(_MAX_PAGES):
                body = self._search(keyword, page)
                hits = body.get("hits", []) or []
                for hit in hits:
                    oid = str(hit.get("objectID", ""))
                    if oid and oid in seen:
                        continue
                    if oid:
                        seen.add(oid)
                    rec = map_hit(hit)
                    if rec is not None:
                        yield rec
                if page + 1 >= int(body.get("nbPages", 0) or 0):
                    break

    def _search(self, query: str, page: int) -> dict[str, Any]:
        payload = {"query": query, "hitsPerPage": _HITS_PER_PAGE, "page": page}

        def _do() -> httpx.Response:
            resp = self._client.post(self._url, json=payload)
            resp.raise_for_status()
            return resp

        self._rl.wait("algolia.net")
        return with_backoff(_do).json()


# ----- mapping (pure, fixture-tested) -----

def _first(*vals: Any) -> str | None:
    for v in vals:
        if v:
            return str(v)
    return None


def _org(hit: dict[str, Any]) -> dict[str, Any]:
    org = hit.get("organization")
    return org if isinstance(org, dict) else {}


def _city(hit: dict[str, Any]) -> str | None:
    offices = hit.get("offices")
    if isinstance(offices, list) and offices and isinstance(offices[0], dict):
        o = offices[0]
        return _first(o.get("city"), o.get("local_city"), o.get("name"))
    return _first(hit.get("city"))


def _url(hit: dict[str, Any]) -> str | None:
    slug = hit.get("slug")
    org_slug = _org(hit).get("slug") or hit.get("organization_slug")
    if slug and org_slug:
        return (f"https://www.welcometothejungle.com/fr/companies/"
                f"{org_slug}/jobs/{slug}")
    return _first(hit.get("url"), hit.get("reference"))


def _contract(hit: dict[str, Any]) -> str:
    raw = (hit.get("contract_type") or hit.get("contractType") or "")
    return _CONTRACT_MAP.get(str(raw).upper(), "unknown")


def map_hit(hit: dict[str, Any]) -> OfferRecord | None:
    title = hit.get("name") or hit.get("title")
    if not title:
        return None
    url = _url(hit)
    if not url:
        return None

    profession = hit.get("profession")
    tags = []
    if isinstance(profession, dict):
        tags = [v for v in (profession.get("category_name"),
                            profession.get("sub_category_name")) if v]

    return OfferRecord(
        external_id=_first(hit.get("objectID")),
        url=url,
        title=str(title),
        company_name=_first(_org(hit).get("name")),
        description=_first(hit.get("description")),
        contract_type=_contract(hit),
        city=_city(hit),
        posted_at=_first(hit.get("published_at"), hit.get("published_at_date")),
        stack_tags=tags,
    ).normalized()
