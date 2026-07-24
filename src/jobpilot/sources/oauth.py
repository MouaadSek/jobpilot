"""OAuth2 client_credentials helper with in-memory token caching."""

from __future__ import annotations

import threading
import time

import httpx

from jobpilot.logging_conf import get_logger
from jobpilot.ratelimit import with_backoff

log = get_logger("oauth")


class ClientCredentialsToken:
    """Fetches and caches a bearer token, refreshing shortly before expiry.

    Thread-safe so the APScheduler daemon and CLI can share one instance.
    """

    def __init__(
        self,
        token_url: str,
        client_id: str,
        client_secret: str,
        scope: str,
        *,
        client: httpx.Client | None = None,
        early_refresh_s: int = 60,
    ) -> None:
        self._token_url = token_url
        self._client_id = client_id
        self._client_secret = client_secret
        self._scope = scope
        self._client = client or httpx.Client(timeout=30.0)
        self._early_refresh_s = early_refresh_s
        self._lock = threading.Lock()
        self._access_token: str | None = None
        self._expires_at: float = 0.0

    def token(self) -> str:
        with self._lock:
            if self._access_token and time.time() < self._expires_at:
                return self._access_token
            return self._refresh()

    def _refresh(self) -> str:
        data = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "scope": self._scope,
        }

        def _do() -> httpx.Response:
            resp = self._client.post(
                self._token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            resp.raise_for_status()
            return resp

        resp = with_backoff(_do)
        payload = resp.json()
        self._access_token = payload["access_token"]
        expires_in = int(payload.get("expires_in", 1499))
        self._expires_at = time.time() + max(0, expires_in - self._early_refresh_s)
        log.info("obtained access token, expires_in=%ss", expires_in)
        return self._access_token

    def auth_header(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token()}"}
