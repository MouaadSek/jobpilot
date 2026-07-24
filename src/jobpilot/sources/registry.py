"""Maps source names (rows in the sources table) to Source implementations.

Keeping construction in one place means ingest.py / the CLI never import concrete
sources directly. Extra keyword args from the caller are forwarded to factories.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import yaml

from jobpilot.config import Settings, get_settings
from jobpilot.logging_conf import get_logger
from jobpilot.sources.ats import ATSSource
from jobpilot.sources.base import Source
from jobpilot.sources.email_alerts import IndeedAlertSource, LinkedInAlertSource
from jobpilot.sources.france_travail import FranceTravailSource
from jobpilot.sources.labonnealternance import LaBonneAlternanceSource
from jobpilot.sources.wttj import WelcomeToTheJungleSource

log = get_logger("registry")

# name -> factory(settings, **kwargs) -> Source. Factories pull the kwargs they
# understand and ignore the rest, so the CLI can pass shared options blindly.
_FACTORIES: dict[str, Callable[..., Source]] = {
    "france_travail": lambda s, **kw: FranceTravailSource(
        s, published_since_days=kw.get("since")
    ),
    "labonnealternance": lambda s, **kw: LaBonneAlternanceSource(s),
    "ats": lambda s, **kw: ATSSource(s),
    "linkedin_alert": lambda s, **kw: LinkedInAlertSource(s),
    "indeed_alert": lambda s, **kw: IndeedAlertSource(s),
    "wttj": lambda s, **kw: WelcomeToTheJungleSource(s),
}


def available_sources() -> list[str]:
    return list(_FACTORIES)


def _enablement(settings: Settings) -> dict[str, bool]:
    """Read config/sources.yaml. Unlisted sources default to enabled."""
    path = settings.config_dir / "sources.yaml"
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    out: dict[str, bool] = {}
    for name, cfg in (data.get("sources") or {}).items():
        out[name] = bool((cfg or {}).get("enabled", True))
    return out


def is_enabled(name: str, settings: Settings | None = None) -> bool:
    return _enablement(settings or get_settings()).get(name, True)


def enabled_sources(settings: Settings | None = None) -> list[str]:
    """Registered sources that are enabled in config, in registration order."""
    enab = _enablement(settings or get_settings())
    return [n for n in _FACTORIES if enab.get(n, True)]


def build_source(name: str, settings: Settings | None = None, **kwargs: Any) -> Source:
    if name not in _FACTORIES:
        raise ValueError(
            f"no source registered for '{name}'. Available: {available_sources()}"
        )
    return _FACTORIES[name](settings or get_settings(), **kwargs)
