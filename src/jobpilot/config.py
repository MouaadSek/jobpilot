"""Configuration and path resolution. Secrets come from .env only (never mocked)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

# Project root = two levels up from this file (src/jobpilot/config.py -> project root).
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OPENAI_MODEL = "gpt-5.4-mini"
DEFAULT_OPENAI_BASE_URL = "https://api.openai.com/v1"
# Descriptions shorter than this count as absent; see jobpilot.descriptions.
DEFAULT_ALERT_MIN_DESCRIPTION_CHARS = 120

# Load .env from the project root once, without overriding real environment vars.
load_dotenv(PROJECT_ROOT / ".env", override=False)


class MissingCredentialError(RuntimeError):
    """Raised when a required secret is absent. We ask; we never silently mock."""


def _path(env_var: str, default_rel: str) -> Path:
    raw = os.getenv(env_var)
    p = Path(raw) if raw else PROJECT_ROOT / default_rel
    return p if p.is_absolute() else PROJECT_ROOT / p


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    normalized = raw.strip().casefold()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be true or false")


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

    # La Bonne Alternance through the API Apprentissage (Bearer key)
    lba_api_key: str | None

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
    tailoring_provider: str = "auto"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-haiku-4-5-20251001"
    openai_api_key: str | None = None
    openai_model: str = DEFAULT_OPENAI_MODEL
    openai_base_url: str = DEFAULT_OPENAI_BASE_URL

    # SMTP for sending an application by email (Gmail app password recommended).
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_name: str = "Mouaad Sekkouri"
    cold_send_enabled: bool = False

    # Applicant contact details used only to prefill ATS forms. These stay in
    # .env rather than the matching profile because they are not scoring data.
    applicant_full_name: str | None = None
    applicant_email: str | None = None
    applicant_phone: str | None = None
    applicant_linkedin_url: str | None = None

    # IMAP transport tuning; Gmail credentials above remain the single login.
    imap_host: str = "imap.gmail.com"
    imap_port: int = 993
    imap_folder: str = "INBOX"

    # Below this many characters an offer description counts as absent and gets
    # synthesised from the alert's own fields (jobpilot.descriptions).
    alert_min_description_chars: int = DEFAULT_ALERT_MIN_DESCRIPTION_CHARS

    # WTTJ request ceiling per search query.
    wttj_max_pages: int = 5
    #: The search endpoint has no pagination, so this caps how many search calls
    #: one ingest run may issue (one per department group).
    lba_max_pages: int = 5
    # WTTJ inline apply remains a fill/upload-only dry run unless explicitly enabled.
    wttj_auto_submit_enabled: bool = False
    # Last-resort degradation for a citation the advisor could not get right
    # after every retry. OFF by design: a silently weaker CV is worse than a
    # failed generation, because nobody reviews what they were not told about.
    # Task 37 item 4 measures whether this is ever needed; turning it on is a
    # separate decision that should have that evidence behind it.
    tailoring_drop_unknown_citations: bool = False

    def require_smtp_credentials(self) -> tuple[str, int, str, str, str]:
        if not self.smtp_username or not self.smtp_password:
            raise MissingCredentialError(
                "SMTP credentials missing. Set SMTP_USERNAME and SMTP_PASSWORD in "
                ".env (for Gmail, create an App Password; requires 2FA). See "
                ".env.example."
            )
        return (
            self.smtp_host,
            self.smtp_port,
            self.smtp_username,
            self.smtp_password,
            self.smtp_from_name,
        )

    def redact(self, text: str) -> str:
        """Remove configured secrets from exception text before display/logging."""

        secrets = (
            self.ft_client_secret,
            self.lba_api_key,
            self.gmail_app_password,
            self.wttj_api_key,
            self.anthropic_api_key,
            self.openai_api_key,
            self.smtp_password,
        )
        for secret in secrets:
            if secret:
                text = text.replace(secret, "[REDACTED]")
        return text

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
        gmail_address=os.getenv("GMAIL_ADDRESS") or None,
        gmail_app_password=os.getenv("GMAIL_APP_PASSWORD") or None,
        email_alert_since_days=int(os.getenv("EMAIL_ALERT_SINCE_DAYS", "7")),
        wttj_app_id=os.getenv("WTTJ_APP_ID", "CSEKHVMS53"),
        wttj_api_key=os.getenv("WTTJ_API_KEY") or None,
        wttj_index=os.getenv("WTTJ_INDEX", "wk_cms_jobs_production"),
        output_dir=_path("JOBPILOT_OUTPUT_DIR", "output/applications"),
        tailoring_provider=os.getenv("TAILORING_PROVIDER", "auto"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY") or None,
        anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001"),
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        openai_model=os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
        openai_base_url=os.getenv("OPENAI_BASE_URL", DEFAULT_OPENAI_BASE_URL),
        smtp_host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_username=os.getenv("SMTP_USERNAME") or None,
        smtp_password=os.getenv("SMTP_PASSWORD") or None,
        smtp_from_name=os.getenv("SMTP_FROM_NAME", "Mouaad Sekkouri"),
        cold_send_enabled=_env_bool("COLD_SEND_ENABLED"),
        applicant_full_name=os.getenv("APPLICANT_FULL_NAME") or None,
        applicant_email=os.getenv("APPLICANT_EMAIL") or None,
        applicant_phone=os.getenv("APPLICANT_PHONE") or None,
        applicant_linkedin_url=os.getenv("APPLICANT_LINKEDIN_URL") or None,
        imap_host=os.getenv("IMAP_HOST", "imap.gmail.com"),
        imap_port=int(os.getenv("IMAP_PORT", "993")),
        imap_folder=os.getenv("IMAP_FOLDER", "INBOX"),
        alert_min_description_chars=int(
            os.getenv(
                "ALERT_MIN_DESCRIPTION_CHARS", str(DEFAULT_ALERT_MIN_DESCRIPTION_CHARS)
            )
        ),
        wttj_max_pages=int(os.getenv("WTTJ_MAX_PAGES", "5")),
        lba_max_pages=int(os.getenv("LBA_MAX_PAGES", "5")),
        wttj_auto_submit_enabled=_env_bool("WTTJ_AUTO_SUBMIT_ENABLED"),
        tailoring_drop_unknown_citations=_env_bool(
            "TAILORING_DROP_UNKNOWN_CITATIONS"
        ),
    )
