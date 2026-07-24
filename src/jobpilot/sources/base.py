"""Source interface. Every API, scraper, or mailer sits behind this so it is
pluggable and mockable (constitution rule)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator

from jobpilot.models import CompanyRecord, OfferRecord


class Source(ABC):
    """Abstract ingestion source.

    Implementations must be side-effect free with respect to the DB: they yield
    normalized records; ingest.py owns persistence, dedup, and idempotency.
    """

    #: Must match a row in the sources table (see db._SEED_SOURCES).
    name: str

    @abstractmethod
    def fetch_offers(self) -> Iterator[OfferRecord]:
        """Yield normalized offers. Must apply rate limiting + backoff internally."""
        raise NotImplementedError

    def fetch_companies(self) -> Iterable[CompanyRecord]:
        """Yield companies likely to hire (optional; default: none)."""
        return ()
