"""La Bonne Alternance ingestion through the API Apprentissage.

Built against the live OpenAPI document at
``https://api.apprentissage.beta.gouv.fr/api/documentation/json`` (spec version
1c12a0c, read 2026-07-30), not against the retired endpoints this module used to
call:

- base URL ``https://api.apprentissage.beta.gouv.fr/api`` (the spec's only server)
- auth ``Authorization: Bearer <LBA_API_KEY>`` (security scheme ``api-key``,
  ``http`` / ``bearer``)
- ``GET /job/v1/search`` -> ``{"jobs": [...], "recruiters": [...], "warnings": [...]}``
- documented rate limit: 60 calls per minute per consumer, reported through
  ``x-ratelimit-*`` headers with ``retry-after`` on 429

Two things the endpoint does NOT have, which shape the code below:

- **No pagination.** There is no page or limit parameter; one call returns the
  whole result set for its filters. ``LBA_MAX_PAGES`` therefore caps the number
  of *search calls* a run may issue, which is the volume knob that exists here.
- **No contract-type filter and no email.** The whole API is apprenticeship, so
  every offer is an alternance and stage cannot be requested. ``apply`` exposes a
  URL and sometimes a phone number, never an address, so ``contact_email`` stays
  None.

``recruiters`` is the second capability: companies the service considers likely
to hire an alternant. They are companies, not offers, and are yielded through
``fetch_companies()`` so they never reach the review queue.
"""

from __future__ import annotations

import re
from collections.abc import Iterator, Sequence
from typing import Any

import httpx

from jobpilot.config import MissingCredentialError, Settings
from jobpilot.logging_conf import get_logger
from jobpilot.models import CompanyRecord, OfferRecord
from jobpilot.ratelimit import RateLimiter, with_backoff
from jobpilot.sources.base import Source

log = get_logger("labonnealternance")

BASE_URL = "https://api.apprentissage.beta.gouv.fr/api"
SEARCH_PATH = "/job/v1/search"

# ---- Tunable search block ---------------------------------------------------
# Changing what we look for should not require touching HTTP, mapping or
# persistence code. `romes` takes a comma-separated list; `departements` an array
# of department numbers. Both are optional, and omitting them searches the whole
# of France, which is far more than this pipeline wants.
#
# ROME codes (France Travail's job reference) covering IT work. There is no
# cyber-only ROME, so this is the systems-information family; relevance is then
# decided by scoring, not by the query.
ROME_CODES: tuple[str, ...] = (
    "M1802",  # Expertise et support en systèmes d'information (incl. sécurité)
    "M1810",  # Production et exploitation de systèmes d'information
    "M1801",  # Administration de systèmes d'information
    "M1805",  # Études et développement informatique
    "M1806",  # Conseil et maîtrise d'ouvrage en systèmes d'information
)
#: Hauts-de-France and Île-de-France, the two target regions, by department.
#: One search call per group keeps each query readable in the logs.
DEPARTEMENT_GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("hauts-de-france", ("02", "59", "60", "62", "80")),
    ("ile-de-france", ("75", "77", "78", "91", "92", "93", "94", "95")),
)
#: Remote work has no filter parameter; it is read back off each offer instead.
_REMOTE_MAP = {
    "onsite": "onsite",
    "hybrid": "hybrid",
    "remote": "full_remote",
}
#: Every contract label this endpoint publishes is a form of work-study.
_ALTERNANCE_CONTRACTS = ("apprentissage", "professionnalisation")

_POSTCODE_CITY_RE = re.compile(r"\b\d{5}\s+(?P<city>[^,]+)$")


class LaBonneAlternanceError(RuntimeError):
    """API Apprentissage refused or failed a request."""


class LaBonneAlternanceAuthError(LaBonneAlternanceError):
    """The key was rejected (401/403). Retrying will not help."""


class LaBonneAlternanceRateLimited(LaBonneAlternanceError):
    """The documented 60 calls/minute quota was exhausted and backoff gave up."""


class LaBonneAlternanceSource(Source):
    """Offers and likely-to-hire companies from the API Apprentissage."""

    name = "labonnealternance"

    def __init__(
        self,
        settings: Settings,
        *,
        api_key: str | None = None,
        romes: Sequence[str] | None = None,
        departement_groups: Sequence[tuple[str, Sequence[str]]] | None = None,
        client: httpx.Client | None = None,
        rate_limiter: RateLimiter | None = None,
        max_pages: int | None = None,
    ) -> None:
        key = api_key or settings.lba_api_key
        if not key:
            raise MissingCredentialError(
                "La Bonne Alternance requires LBA_API_KEY in .env. Register at "
                "https://api.apprentissage.beta.gouv.fr and generate a token from "
                "your profile page."
            )
        self._settings = settings
        self._api_key = key
        self._romes = tuple(romes) if romes is not None else ROME_CODES
        self._groups = (
            tuple((label, tuple(codes)) for label, codes in departement_groups)
            if departement_groups is not None
            else DEPARTEMENT_GROUPS
        )
        self._max_calls = settings.lba_max_pages if max_pages is None else max_pages
        if self._max_calls < 1:
            raise ValueError("LBA_MAX_PAGES must be at least 1")
        self._client = client or httpx.Client(
            base_url=BASE_URL,
            timeout=45.0,
            headers={
                "User-Agent": "JobPilot/0.1 (personal job pipeline)",
                "Authorization": f"Bearer {self._api_key}",
                "Accept": "application/json",
            },
        )
        # The documented quota is 60/minute; one call per second stays well under
        # it even when every group runs back to back.
        self._rl = rate_limiter or RateLimiter(min_interval_s=1.0)
        #: Filled by whichever of fetch_offers/fetch_companies runs first, so a
        #: full ingest costs one set of calls rather than two.
        self._pages: list[dict[str, Any]] | None = None

    # ----- fetching -----

    def _search_all(self) -> list[dict[str, Any]]:
        if self._pages is not None:
            return self._pages
        pages: list[dict[str, Any]] = []
        for label, departements in self._groups[: self._max_calls]:
            body = self._search(departements)
            for warning in body.get("warnings") or []:
                log.warning(
                    "labonnealternance %s: %s", label, warning.get("message", warning)
                )
            log.info(
                "labonnealternance %s: %d offer(s), %d recruiter(s)",
                label,
                len(body.get("jobs") or []),
                len(body.get("recruiters") or []),
            )
            pages.append(body)
        if len(self._groups) > self._max_calls:
            log.info(
                "labonnealternance: stopped after %d search call(s) (LBA_MAX_PAGES)",
                self._max_calls,
            )
        self._pages = pages
        return pages

    def _search(self, departements: Sequence[str]) -> dict[str, Any]:
        params = {
            "romes": ",".join(self._romes),
            "departements": list(departements),
        }

        def _do() -> httpx.Response:
            resp = self._client.get(SEARCH_PATH, params=params)
            resp.raise_for_status()
            return resp

        self._rl.wait("api.apprentissage.beta.gouv.fr")
        try:
            response = with_backoff(_do)
        except httpx.HTTPStatusError as exc:
            raise self._error(exc) from None
        except httpx.HTTPError as exc:
            detail = self._settings.redact(str(exc))
            raise LaBonneAlternanceError(
                f"API Apprentissage request failed: {detail}"
            ) from None
        remaining = response.headers.get("x-ratelimit-remaining")
        if remaining is not None:
            log.debug("labonnealternance quota remaining: %s", remaining)
        return response.json()

    def _error(self, exc: httpx.HTTPStatusError) -> LaBonneAlternanceError:
        """Turn an HTTP failure into a typed error, with the key removed."""

        status = exc.response.status_code
        detail = self._settings.redact((exc.response.text or str(exc)).strip()[:400])
        if status in (401, 403):
            return LaBonneAlternanceAuthError(
                f"API Apprentissage rejected LBA_API_KEY (HTTP {status}): {detail}"
            )
        if status == 429:
            retry_after = exc.response.headers.get("retry-after", "?")
            return LaBonneAlternanceRateLimited(
                "API Apprentissage rate limit reached (HTTP 429); retry-after="
                f"{retry_after}s: {detail}"
            )
        return LaBonneAlternanceError(
            f"API Apprentissage request failed (HTTP {status}): {detail}"
        )

    def fetch_offers(self) -> Iterator[OfferRecord]:
        seen: set[str] = set()
        for body in self._search_all():
            for job in body.get("jobs") or []:
                record = map_offer(job)
                if record is None:
                    continue
                # Groups do not overlap, but a partner can publish the same offer
                # into more than one of them.
                key = record.external_id or record.url
                if key in seen:
                    continue
                seen.add(key)
                yield record

    def fetch_companies(self) -> Iterator[CompanyRecord]:
        seen: set[str] = set()
        for body in self._search_all():
            for recruiter in body.get("recruiters") or []:
                record = map_company(recruiter)
                if record is None:
                    continue
                key = record.siren or record.name.lower()
                if key in seen:
                    continue
                seen.add(key)
                yield record


# ----- mapping (pure, fixture-tested) -----


def _text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _first(*values: Any) -> str | None:
    for value in values:
        text = _text(value)
        if text:
            return text
    return None


def _city(address: Any) -> str | None:
    """Pull the commune out of a French postal address.

    Addresses arrive either as "62680 Méricourt" or as a full street line ending
    in "92300 LEVALLOIS-PERRET", so the postcode is the reliable anchor.
    """

    text = _text(address)
    if not text:
        return None
    match = _POSTCODE_CITY_RE.search(text)
    city = match.group("city").strip() if match else text
    # Some partners upper-case the whole address; title-case only those.
    return city.title() if city.isupper() else city


def _workplace(entry: dict[str, Any]) -> dict[str, Any]:
    workplace = entry.get("workplace")
    return workplace if isinstance(workplace, dict) else {}


def _company_name(workplace: dict[str, Any]) -> str | None:
    return _first(
        workplace.get("name"), workplace.get("brand"), workplace.get("legal_name")
    )


def _contract_type(contract: dict[str, Any]) -> str:
    kinds = " ".join(str(value).lower() for value in contract.get("type") or [])
    if any(signal in kinds for signal in _ALTERNANCE_CONTRACTS):
        return "alternance"
    # This endpoint only publishes work-study offers, so an unrecognised label is
    # still an alternance; "unknown" would drop it out of contract-aware scoring.
    return "alternance"


def map_offer(job: dict[str, Any]) -> OfferRecord | None:
    """Map one `jobs[]` entry. Returns None when it cannot be applied to."""

    if not isinstance(job, dict):
        return None
    offer = job.get("offer") if isinstance(job.get("offer"), dict) else {}
    apply_block = job.get("apply") if isinstance(job.get("apply"), dict) else {}
    identifier = job.get("identifier") if isinstance(job.get("identifier"), dict) else {}
    contract = job.get("contract") if isinstance(job.get("contract"), dict) else {}
    workplace = _workplace(job)

    title = _text(offer.get("title"))
    url = _text(apply_block.get("url"))
    if not title or not url:
        return None

    publication = (
        offer.get("publication") if isinstance(offer.get("publication"), dict) else {}
    )
    location = workplace.get("location") if isinstance(workplace.get("location"), dict) else {}
    duration = contract.get("duration")
    return OfferRecord(
        external_id=_first(identifier.get("id"), identifier.get("partner_job_id")),
        url=url,
        title=title,
        company_name=_company_name(workplace),
        description=_text(offer.get("description")),
        contract_type=_contract_type(contract),
        duration_months=duration if isinstance(duration, int) else None,
        city=_city(location.get("address")),
        remote_policy=_REMOTE_MAP.get(
            str(contract.get("remote") or "").lower(), "unknown"
        ),
        stack_tags=[str(code) for code in offer.get("rome_codes") or []],
        posted_at=_text(publication.get("creation")),
        # The API exposes an apply URL and sometimes a phone, never an address.
        contact_email=None,
    ).normalized()


def map_company(recruiter: dict[str, Any]) -> CompanyRecord | None:
    """Map one `recruiters[]` entry into a cold-outreach target."""

    if not isinstance(recruiter, dict):
        return None
    workplace = _workplace(recruiter)
    name = _company_name(workplace)
    if not name:
        return None
    siret = _text(workplace.get("siret"))
    domain = workplace.get("domain") if isinstance(workplace.get("domain"), dict) else {}
    naf = domain.get("naf") if isinstance(domain.get("naf"), dict) else {}
    apply_block = recruiter.get("apply") if isinstance(recruiter.get("apply"), dict) else {}
    location = workplace.get("location") if isinstance(workplace.get("location"), dict) else {}
    return CompanyRecord(
        name=name,
        # SIRET is establishment-level; its first nine digits are the SIREN the
        # companies table keys on.
        siren=siret[:9] if siret and len(siret) >= 9 else None,
        domain=_domain(_text(workplace.get("website"))),
        size_bucket=_text(workplace.get("size")),
        sector=_text(naf.get("label")),
        city=_city(location.get("address")),
        notes=_first(apply_block.get("url")),
        source="labonnealternance",
    )


def _domain(website: str | None) -> str | None:
    """Reduce a site URL to a bare domain, which is what contacts.py expects."""

    if not website:
        return None
    host = re.sub(r"^https?://", "", website).split("/")[0].strip()
    return host.removeprefix("www.").lower() or None
