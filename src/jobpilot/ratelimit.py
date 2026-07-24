"""Rate limiting + exponential backoff for every external call (constitution rule)."""

from __future__ import annotations

import random
import time
from collections.abc import Callable
from typing import TypeVar

import httpx

from jobpilot.logging_conf import get_logger

log = get_logger("ratelimit")

T = TypeVar("T")


class RateLimiter:
    """Minimum-delay-per-domain limiter. Blocks until the next call is allowed."""

    def __init__(self, min_interval_s: float) -> None:
        self.min_interval_s = min_interval_s
        self._last_call: dict[str, float] = {}

    def wait(self, key: str = "default") -> None:
        now = time.monotonic()
        last = self._last_call.get(key)
        if last is not None:
            elapsed = now - last
            if elapsed < self.min_interval_s:
                time.sleep(self.min_interval_s - elapsed)
        self._last_call[key] = time.monotonic()


def with_backoff(
    fn: Callable[[], T],
    *,
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    retry_statuses: tuple[int, ...] = (429, 500, 502, 503, 504),
) -> T:
    """Call fn(); retry on transient HTTP errors with full-jitter exponential backoff."""
    attempt = 0
    while True:
        try:
            return fn()
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            if status not in retry_statuses or attempt >= max_retries:
                raise
            delay = _delay(attempt, base_delay, max_delay, exc.response)
            log.warning("HTTP %s, retry %d/%d in %.1fs", status, attempt + 1,
                        max_retries, delay)
        except (httpx.TransportError, httpx.TimeoutException) as exc:
            if attempt >= max_retries:
                raise
            delay = _delay(attempt, base_delay, max_delay, None)
            log.warning("%s, retry %d/%d in %.1fs", type(exc).__name__,
                        attempt + 1, max_retries, delay)
        time.sleep(delay)
        attempt += 1


def _delay(attempt: int, base: float, cap: float, resp: httpx.Response | None) -> float:
    if resp is not None:
        ra = resp.headers.get("Retry-After")
        if ra and ra.isdigit():
            return min(float(ra), cap)
    return random.uniform(0, min(cap, base * (2**attempt)))
