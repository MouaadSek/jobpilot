"""WTTJ Algolia client: hit mapping + search flow (with respx) + missing key."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest
import respx

from jobpilot.config import MissingCredentialError, Settings
from jobpilot.sources.wttj import WelcomeToTheJungleSource, map_hit

APP_ID = "TESTAPP"
INDEX = "wttj_jobs_test"
QUERY_URL = f"https://{APP_ID}-dsn.algolia.net/1/indexes/{INDEX}/query"


def _settings(api_key: str | None = "algolia-key") -> Settings:
    return Settings(
        db_path=Path(":memory:"), log_dir=Path("logs"), config_dir=Path("config"),
        schema_path=Path("schema.sql"), migrations_dir=Path("migrations"),
        embed_model="x", queue_threshold=0.35, ft_client_id=None,
        ft_client_secret=None, ft_token_url="", ft_search_url="", ft_scope="",
        ft_published_since=31, lba_api_key=None, lba_search_url="",
        lba_caller_email=None, gmail_address=None, gmail_app_password=None,
        email_alert_since_days=7, wttj_app_id=APP_ID, wttj_api_key=api_key,
        wttj_index=INDEX,
    )


def _hit(oid: str, contract: str = "APPRENTICESHIP") -> dict:
    return {
        "objectID": oid,
        "name": "Alternance Analyste SOC",
        "organization": {"name": "ACME Cyber", "slug": "acme-cyber"},
        "slug": f"analyste-soc-{oid}",
        "offices": [{"city": "Lille"}],
        "contract_type": contract,
        "published_at": "2026-07-15T00:00:00Z",
        "profession": {"category_name": "Cybersecurity"},
    }


def test_map_hit_builds_url_and_contract() -> None:
    rec = map_hit(_hit("42"))
    assert rec is not None
    assert rec.external_id == "42"
    assert rec.contract_type == "alternance"
    assert rec.company_name == "ACME Cyber"
    assert rec.city == "Lille"
    assert rec.url == (
        "https://www.welcometothejungle.com/fr/companies/acme-cyber/jobs/"
        "analyste-soc-42"
    )
    assert rec.stack_tags == ["Cybersecurity"]


def test_map_hit_contract_variants() -> None:
    assert map_hit(_hit("1", "INTERNSHIP")).contract_type == "stage"
    assert map_hit(_hit("2", "FULL_TIME")).contract_type == "cdi"
    assert map_hit(_hit("3", "WEIRD")).contract_type == "unknown"


def test_map_hit_requires_title_and_url() -> None:
    assert map_hit({"objectID": "x", "slug": "s"}) is None  # no title
    assert map_hit({"objectID": "x", "name": "t"}) is None  # no url (no slugs)


def test_missing_api_key_raises() -> None:
    with pytest.raises(MissingCredentialError):
        WelcomeToTheJungleSource(_settings(api_key=None))


@respx.mock
def test_fetch_offers_paginates_and_dedups() -> None:
    route = respx.post(QUERY_URL)
    route.side_effect = [
        httpx.Response(200, json={"hits": [_hit("1"), _hit("2")], "nbPages": 2}),
        httpx.Response(200, json={"hits": [_hit("2"), _hit("3")], "nbPages": 2}),
    ]
    src = WelcomeToTheJungleSource(_settings(), keywords=["cybersécurité"])
    recs = list(src.fetch_offers())
    assert [r.external_id for r in recs] == ["1", "2", "3"]  # "2" deduped


@respx.mock
def test_sends_algolia_headers() -> None:
    route = respx.post(QUERY_URL).mock(
        return_value=httpx.Response(200, json={"hits": [], "nbPages": 0})
    )
    src = WelcomeToTheJungleSource(_settings(api_key="secret-algolia"),
                                   keywords=["SOC"])
    list(src.fetch_offers())
    req = route.calls.last.request
    assert req.headers["X-Algolia-API-Key"] == "secret-algolia"
    assert req.headers["X-Algolia-Application-Id"] == APP_ID
