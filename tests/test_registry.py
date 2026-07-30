"""Source enablement via config/sources.yaml."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from jobpilot.config import Settings
from jobpilot.sources.registry import available_sources, enabled_sources, is_enabled


def _settings(config_dir: Path) -> Settings:
    return Settings(
        db_path=Path(":memory:"), log_dir=Path("logs"), config_dir=config_dir,
        schema_path=Path("schema.sql"), migrations_dir=Path("migrations"),
        embed_model="x", queue_threshold=0.6, ft_client_id=None,
        ft_client_secret=None, ft_token_url="", ft_search_url="", ft_scope="",
        ft_published_since=31,
        lba_api_key=None,
        gmail_address=None, gmail_app_password=None, email_alert_since_days=7,
        wttj_app_id="APP", wttj_api_key=None, wttj_index="idx",
    )


def test_no_config_all_enabled(tmp_path: Path) -> None:
    s = _settings(tmp_path)
    assert enabled_sources(s) == available_sources()
    assert is_enabled("labonnealternance", s) is True


def test_disabled_source_excluded(tmp_path: Path) -> None:
    (tmp_path / "sources.yaml").write_text(
        "sources:\n"
        "  france_travail:\n    enabled: true\n"
        "  labonnealternance:\n    enabled: false\n",
        encoding="utf-8",
    )
    s = _settings(tmp_path)
    assert "labonnealternance" not in enabled_sources(s)
    assert "france_travail" in enabled_sources(s)
    assert is_enabled("labonnealternance", s) is False
    # ats is unlisted -> defaults to enabled
    assert is_enabled("ats", s) is True


def test_replace_keeps_dataclass_shape(tmp_path: Path) -> None:
    # Guard: Settings stays a flat frozen dataclass we can copy in tests.
    s = replace(_settings(tmp_path), embed_model="y")
    assert s.embed_model == "y"
