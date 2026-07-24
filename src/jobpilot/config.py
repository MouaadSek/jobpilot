"""Configuration and path resolution. Secrets come from .env only (never mocked)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

# Project root = two levels up from this file (src/jobpilot/config.py -> project root).
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Load .env from the project root once, without overriding real environment vars.
load_dotenv(PROJECT_ROOT / ".env", override=False)


class MissingCredentialError(RuntimeError):
    """Raised when a required secret is absent. We ask; we never silently mock."""


def _path(env_var: str, default_rel: str) -> Path:
    raw = os.getenv(env_var)
    p = Path(raw) if raw else PROJECT_ROOT / default_rel
    return p if p.is_absolute() else PROJECT_ROOT / p


@dataclass(frozen=True)
class Settings:
    db_path: Path
    log_dir: Path
    config_dir: Path
    schema_path: Path
    migrations_dir: Path
    embed_model: str
    queue_threshold: float  # final_score >= this -> review queue

    # France Travail
    ft_client_id: str | None
    ft_client_secret: str | None
    ft_token_url: str
    ft_search_url: str
    ft_scope: str
    ft_published_since: int  # days; FT allows 1, 3, 7, 14, 31

    # La Bonne Alternance (current API needs a Bearer key; caller email is legacy)
    lba_api_key: str | None
    lba_search_url: str
    lba_caller_email: str | None

    # Gmail (IMAP) for LinkedIn/Indeed job-alert ingestion
    gmail_address: str | None
    gmail_app_password: str | None
    email_alert_since_days: int

    # Welcome to the Jungle (Algolia)
    wttj_app_id: str
    wttj_api_key: str | None
    wttj_index: str

    # Phase 2 application artifacts and optional automated tailoring.
    # Defaults keep direct Settings(...) construction in tests/backends compatible.
    output_dir: Path = PROJECT_ROOT / "output" / "applications"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-haiku-4-5-20251001"

    def require_gmail_credentials(self) -> tuple[str, str]:
        if not self.gmail_address or not self.gmail_app_password:
            raise MissingCredentialError(
                "Gmail IMAP credentials missing. Set GMAIL_ADDRESS and "
                "GMAIL_APP_PASSWORD in .env (create an App Password in your Google "
                "account; requires 2FA). See .env.example."
            )
        return self.gmail_address, self.gmail_app_password

    def require_ft_credentials(self) -> tuple[str, str]:
        if not self.ft_client_id or not self.ft_client_secret:
            raise MissingCredentialError(
                "France Travail credentials missing. Set FRANCE_TRAVAIL_CLIENT_ID and "
                "FRANCE_TRAVAIL_CLIENT_SECRET in .env (see .env.example)."
            )
        return self.ft_client_id, self.ft_client_secret


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        db_path=_path("JOBPILOT_DB", "data/jobpilot.db"),
        log_dir=_path("JOBPILOT_LOG_DIR", "logs"),
        config_dir=PROJECT_ROOT / "config",
        schema_path=PROJECT_ROOT / "schema.sql",
        migrations_dir=PROJECT_ROOT / "migrations",
        embed_model=os.getenv("JOBPILOT_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
        queue_threshold=float(os.getenv("JOBPILOT_QUEUE_THRESHOLD", "0.35")),
        ft_client_id=os.getenv("FRANCE_TRAVAIL_CLIENT_ID") or None,
        ft_client_secret=os.getenv("FRANCE_TRAVAIL_CLIENT_SECRET") or None,
        ft_token_url=os.getenv(
            "FRANCE_TRAVAIL_TOKEN_URL",
            "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=/partenaire",
        ),
        ft_search_url=os.getenv(
            "FRANCE_TRAVAIL_SEARCH_URL",
            "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search",
        ),
        ft_scope=os.getenv("FRANCE_TRAVAIL_SCOPE", "api_offresdemploiv2 o2dsoffre"),
        ft_published_since=int(os.getenv("FRANCE_TRAVAIL_PUBLISHED_SINCE", "31")),
        lba_api_key=os.getenv("LBA_API_KEY") or None,
        lba_search_url=os.getenv(
            "LBA_SEARCH_URL",
            "https://api.apprentissage.beta.gouv.fr/api/job/v1/search",
        ),
        lba_caller_email=os.getenv("LBA_CALLER_EMAIL") or None,
        gmail_address=os.getenv("GMAIL_ADDRESS") or None,
        gmail_app_password=os.getenv("GMAIL_APP_PASSWORD") or None,
        email_alert_since_days=int(os.getenv("EMAIL_ALERT_SINCE_DAYS", "7")),
        wttj_app_id=os.getenv("WTTJ_APP_ID", "CSEKHVMS53"),
        wttj_api_key=os.getenv("WTTJ_API_KEY") or None,
        wttj_index=os.getenv("WTTJ_INDEX", "wttj_jobs_production_c3_search"),
        output_dir=_path("JOBPILOT_OUTPUT_DIR", "output/applications"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY") or None,
        anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001"),
    )
