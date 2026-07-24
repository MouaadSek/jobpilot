"""Generic ATS pollers for a hand-configured company list (config/targets.yaml).

Supports the public JSON endpoints of Lever, Greenhouse and SmartRecruiters. One
mapper per ATS turns their JSON into OfferRecord; ATSSource iterates the targets
file and yields everything. Contract type is inferred from title/commitment text
(stage/alternance) and left 'unknown' otherwise so the matcher can still judge it.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import httpx
import yaml

from jobpilot.config import Settings
from jobpilot.logging_conf import get_logger
from jobpilot.models import OfferRecord
from jobpilot.ratelimit import RateLimiter, with_backoff
from jobpilot.sources.base import Source

log = get_logger("ats")

GREENHOUSE_URL = "https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"
LEVER_URL = "https://api.lever.co/v0/postings/{board}?mode=json"
SMARTRECRUITERS_URL = "https://api.smartrecruiters.com/v1/companies/{board}/postings"

SUPPORTED_ATS = {"greenhouse", "lever", "smartrecruiters"}


def infer_contract(*texts: str | None) -> str:
    """Best-effort contract inference from free text (title, commitment, ...)."""
    blob = " ".join(t.lower() for t in texts if t)
    if any(k in blob for k in ("alternance", "apprentice", "apprenti", "work-study")):
        return "alternance"
    if any(k in blob for k in ("stage", "stagiaire", "internship", "intern")):
        return "stage"
    return "unknown"


# ----- per-ATS mappers (pure, unit-tested) -----

def map_greenhouse(job: dict[str, Any], company: str) -> OfferRecord | None:
    title = job.get("title")
    url = job.get("absolute_url")
    if not title or not url:
        return None
    location = (job.get("location") or {}).get("name")
    return OfferRecord(
        external_id=_s(job.get("id")),
        url=str(url),
        title=str(title),
        company_name=company,
        description=job.get("content"),  # HTML; fine for embedding/keyword scan
        contract_type=infer_contract(title, location),
        city=location,
        posted_at=job.get("updated_at"),
    ).normalized()


def map_lever(post: dict[str, Any], company: str) -> OfferRecord | None:
    title = post.get("text")
    url = post.get("hostedUrl") or post.get("applyUrl")
    if not title or not url:
        return None
    cats = post.get("categories") or {}
    location = cats.get("location")
    commitment = cats.get("commitment")
    posted = post.get("createdAt")
    posted_iso = _ms_to_iso(posted) if isinstance(posted, int) else None
    return OfferRecord(
        external_id=_s(post.get("id")),
        url=str(url),
        title=str(title),
        company_name=company,
        description=post.get("descriptionPlain") or post.get("description"),
        contract_type=infer_contract(title, commitment),
        city=location,
        posted_at=posted_iso,
        stack_tags=[cats["team"]] if cats.get("team") else [],
    ).normalized()


def map_smartrecruiters(posting: dict[str, Any], company: str, board: str
                        ) -> OfferRecord | None:
    title = posting.get("name")
    pid = posting.get("id")
    if not title or not pid:
        return None
    loc = posting.get("location") or {}
    city = loc.get("city")
    url = posting.get("ref") or f"https://jobs.smartrecruiters.com/{board}/{pid}"
    type_emp = (posting.get("typeOfEmployment") or {}).get("label")
    return OfferRecord(
        external_id=_s(pid),
        url=str(url),
        title=str(title),
        company_name=company,
        contract_type=infer_contract(title, type_emp),
        city=city,
        posted_at=posting.get("releasedDate"),
    ).normalized()


# ----- source -----

class ATSSource(Source):
    name = "ats"

    def __init__(
        self,
        settings: Settings,
        *,
        targets: list[dict[str, str]] | None = None,
        client: httpx.Client | None = None,
        rate_limiter: RateLimiter | None = None,
    ) -> None:
        self._targets = (
            targets if targets is not None
            else load_targets(settings.config_dir / "targets.yaml")
        )
        self._client = client or httpx.Client(
            timeout=30.0, follow_redirects=True,
            headers={"User-Agent": "JobPilot/0.1 (personal job pipeline)",
                     "Accept": "application/json"},
        )
        # Public ATS endpoints: polite modest per-domain delay.
        self._rl = rate_limiter or RateLimiter(min_interval_s=2.0)

    def fetch_offers(self) -> Iterator[OfferRecord]:
        for target in self._targets:
            ats = (target.get("ats") or "").lower()
            board = target.get("board")
            company = target.get("company") or board or "unknown"
            if ats not in SUPPORTED_ATS or not board:
                log.warning("skipping malformed target: %r", target)
                continue
            try:
                yield from self._poll(ats, board, company)
            except httpx.HTTPError as exc:
                log.warning("ATS %s/%s failed: %s", ats, board, exc)

    def _poll(self, ats: str, board: str, company: str) -> Iterator[OfferRecord]:
        if ats == "greenhouse":
            data = self._get(GREENHOUSE_URL.format(board=board), "boards-api.greenhouse.io")
            for job in data.get("jobs", []):
                rec = map_greenhouse(job, company)
                if rec:
                    yield rec
        elif ats == "lever":
            data = self._get(LEVER_URL.format(board=board), "api.lever.co")
            for post in data if isinstance(data, list) else []:
                rec = map_lever(post, company)
                if rec:
                    yield rec
        elif ats == "smartrecruiters":
            data = self._get(SMARTRECRUITERS_URL.format(board=board),
                             "api.smartrecruiters.com")
            for posting in data.get("content", []):
                rec = map_smartrecruiters(posting, company, board)
                if rec:
                    yield rec

    def _get(self, url: str, domain: str) -> Any:
        def _do() -> httpx.Response:
            resp = self._client.get(url)
            resp.raise_for_status()
            return resp

        self._rl.wait(domain)
        return with_backoff(_do).json()


# ----- helpers -----

def load_targets(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        log.warning("no ATS targets file at %s", path)
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data.get("targets", []) or []


def _s(v: Any) -> str | None:
    return str(v) if v is not None else None


def _ms_to_iso(ms: int) -> str:
    from datetime import UTC, datetime

    return datetime.fromtimestamp(ms / 1000, tz=UTC).isoformat()
