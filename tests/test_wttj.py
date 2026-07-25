"""WTTJ Algolia client: hit mapping + search flow (with respx) + missing key."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import httpx
import pytest
import respx

from jobpilot.config import MissingCredentialError, Settings
from jobpilot.ingest import ingest_source
from jobpilot.sources.wttj import (
    ALGOLIA_FACET_FILTERS,
    SEARCH_QUERIES,
    WelcomeToTheJungleSource,
    map_hit,
)

APP_ID = "TESTAPP"
INDEX = "wttj_jobs_test"
QUERY_URL = f"https://{APP_ID}-dsn.algolia.net/1/indexes/{INDEX}/query"
FIXTURE_PATH = Path(__file__).parent / "fixtures" / "wttj" / "search_response.json"


def _sample_response() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _settings(api_key: str | None = "algolia-key") -> Settings:
    return Settings(
        db_path=Path(":memory:"),
        log_dir=Path("logs"),
        config_dir=Path("config"),
        schema_path=Path("schema.sql"),
        migrations_dir=Path("migrations"),
        embed_model="x",
        queue_threshold=0.35,
        ft_client_id=None,
        ft_client_secret=None,
        ft_token_url="",
        ft_search_url="",
        ft_scope="",
        ft_published_since=31,
        lba_api_key=None,
        lba_search_url="",
        lba_caller_email=None,
        gmail_address=None,
        gmail_app_password=None,
        email_alert_since_days=7,
        wttj_app_id=APP_ID,
        wttj_api_key=api_key,
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
        "https://www.welcometothejungle.com/fr/companies/acme-cyber/jobs/analyste-soc-42"
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
    src = WelcomeToTheJungleSource(_settings(api_key="secret-algolia"), keywords=["SOC"])
    list(src.fetch_offers())
    req = route.calls.last.request
    assert req.headers["X-Algolia-API-Key"] == "secret-algolia"
    assert req.headers["X-Algolia-Application-Id"] == APP_ID


def test_saved_response_maps_full_offer_shape() -> None:
    records = [map_hit(hit) for hit in _sample_response()["hits"]]

    assert all(record is not None for record in records)
    first = records[0]
    assert first is not None
    assert first.external_id == "wttj-42"
    assert first.title == "Alternance Analyste SOC"
    assert first.company_name == "ACME Cyber"
    assert first.city == "Lille"
    assert first.contract_type == "alternance"
    assert first.description.startswith("Superviser les alertes SIEM")
    assert first.posted_at == "2026-07-24T07:30:00Z"
    assert first.remote_policy == "hybrid"
    assert first.contact_email == "recrutement@acme.example"
    assert first.stack_tags == ["Tech", "Cybersecurity"]

    second = records[1]
    assert second is not None
    assert second.contract_type == "stage"
    assert second.remote_policy == "full_remote"
    assert second.posted_at == "2026-07-23"


@respx.mock
def test_query_payload_contains_tunable_volume_targets() -> None:
    route = respx.post(QUERY_URL).mock(
        return_value=httpx.Response(200, json={"hits": [], "nbPages": 0})
    )
    source = WelcomeToTheJungleSource(
        _settings(),
        keywords=[SEARCH_QUERIES[0]],
    )

    list(source.fetch_offers())

    payload = json.loads(route.calls.last.request.content)
    assert payload["query"] == SEARCH_QUERIES[0]
    assert payload["hitsPerPage"] == 50
    assert payload["facetFilters"] == [list(group) for group in ALGOLIA_FACET_FILTERS]
    assert any("APPRENTICESHIP" in item for item in ALGOLIA_FACET_FILTERS[0])
    assert any("INTERNSHIP" in item for item in ALGOLIA_FACET_FILTERS[0])
    assert any("Hauts-de-France" in item for item in ALGOLIA_FACET_FILTERS[1])
    assert any("Île-de-France" in item for item in ALGOLIA_FACET_FILTERS[1])
    assert any("remote" in item.casefold() for item in ALGOLIA_FACET_FILTERS[1])


@respx.mock
def test_configurable_max_pages_stops_pagination() -> None:
    route = respx.post(QUERY_URL)
    route.side_effect = [
        httpx.Response(
            200,
            json={"hits": [_hit("page-0")], "nbPages": 10},
        ),
        httpx.Response(
            200,
            json={"hits": [_hit("page-1")], "nbPages": 10},
        ),
    ]
    source = WelcomeToTheJungleSource(
        _settings(),
        keywords=["cybersécurité"],
        max_pages=2,
    )

    records = list(source.fetch_offers())

    assert [record.external_id for record in records] == ["page-0", "page-1"]
    assert route.call_count == 2
    pages = [json.loads(call.request.content)["page"] for call in route.calls]
    assert pages == [0, 1]


@respx.mock
def test_wttj_ingestion_is_idempotent_across_runs(
    db: sqlite3.Connection,
) -> None:
    route = respx.post(QUERY_URL)
    route.side_effect = [
        httpx.Response(200, json=_sample_response()),
        httpx.Response(200, json=_sample_response()),
    ]

    first = ingest_source(
        db,
        WelcomeToTheJungleSource(_settings(), keywords=["cybersécurité"]),
    )
    second = ingest_source(
        db,
        WelcomeToTheJungleSource(_settings(), keywords=["cybersécurité"]),
    )

    assert first.inserted == 2
    assert second.inserted == 0
    assert second.duplicates == 2
    assert db.execute("SELECT count(*) AS n FROM offers").fetchone()["n"] == 2


def test_wttj_max_pages_uses_existing_env_names(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from jobpilot import config

    monkeypatch.setenv("WTTJ_APP_ID", "ENVAPP")
    monkeypatch.setenv("WTTJ_API_KEY", "existing-key")
    monkeypatch.setenv("WTTJ_INDEX", "env-index")
    monkeypatch.setenv("WTTJ_MAX_PAGES", "7")
    config.get_settings.cache_clear()
    try:
        settings = config.get_settings()
        assert settings.wttj_app_id == "ENVAPP"
        assert settings.wttj_api_key == "existing-key"
        assert settings.wttj_index == "env-index"
        assert settings.wttj_max_pages == 7
    finally:
        config.get_settings.cache_clear()
