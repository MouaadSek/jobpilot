"""La Bonne Alternance client (current API): mapping + fetch flow."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest
import respx

from jobpilot.config import MissingCredentialError, Settings
from jobpilot.sources.labonnealternance import (
    LaBonneAlternanceSource,
    map_company,
    map_offer,
)

SEARCH_URL = "https://lba.test/api/job/v1/search"


def _settings(api_key: str | None = "key123") -> Settings:
    return Settings(
        db_path=Path(":memory:"), log_dir=Path("logs"), config_dir=Path("config"),
        schema_path=Path("schema.sql"), migrations_dir=Path("migrations"),
        embed_model="x", queue_threshold=0.6, ft_client_id=None,
        ft_client_secret=None, ft_token_url="", ft_search_url="", ft_scope="",
        ft_published_since=31,
        lba_api_key=api_key, lba_search_url=SEARCH_URL, lba_caller_email=None,
        gmail_address=None, gmail_app_password=None, email_alert_since_days=7,
        wttj_app_id="APP", wttj_api_key=None, wttj_index="idx",
    )


def _job(jid: str, title: str = "Alternance Cybersécurité") -> dict:
    return {
        "identifier": {"id": jid, "partner_job_id": f"p-{jid}"},
        "workplace": {"name": "ACME", "siret": "12345678900011",
                      "location": {"address": "59000 Lille"},
                      "domain": {"naf": {"label": "Conseil SI"}}, "size": "51-200"},
        "apply": {"url": f"https://lba/{jid}"},
        "contract": {"type": ["Apprentissage"]},
        "offer": {"title": title, "description": "azure sentinel",
                  "rome_codes": ["M1802"], "desired_skills": ["Azure", "SIEM"],
                  "publication": {"creation": "2026-07-10T00:00:00Z"}},
    }


def test_map_offer_new_shape() -> None:
    rec = map_offer(_job("1"))
    assert rec is not None
    assert rec.external_id == "1"
    assert rec.contract_type == "alternance"
    assert rec.company_name == "ACME"
    assert rec.city == "59000 Lille"
    assert rec.stack_tags == ["Azure", "SIEM"]


def test_map_offer_non_alternance_marked_unknown() -> None:
    node = _job("2")
    node["contract"]["type"] = ["CDI"]
    rec = map_offer(node)
    assert rec is not None and rec.contract_type == "unknown"


def test_map_offer_requires_title_and_url() -> None:
    assert map_offer({"offer": {}, "apply": {"url": "u"}}) is None
    assert map_offer({"offer": {"title": "t"}, "apply": {}}) is None


def test_map_company_new_shape() -> None:
    c = map_company({"workplace": {"name": "ACME", "siret": "999",
                                   "location": {"address": "Lille"},
                                   "domain": {"naf": {"label": "Conseil"}},
                                   "size": "11-50"}})
    assert c is not None
    assert c.name == "ACME" and c.siren == "999"
    assert c.sector == "Conseil" and c.size_bucket == "11-50"


def test_missing_api_key_raises() -> None:
    with pytest.raises(MissingCredentialError):
        LaBonneAlternanceSource(_settings(api_key=None))


@respx.mock
def test_fetch_offers_and_companies_dedup() -> None:
    payload = {
        "jobs": [_job("1"), _job("1", "dup")],  # same id -> deduped
        "recruiters": [
            {"workplace": {"name": "ACME"}},
            {"workplace": {"name": "ACME"}},  # same name -> deduped
        ],
    }
    respx.get(SEARCH_URL).mock(return_value=httpx.Response(200, json=payload))
    src = LaBonneAlternanceSource(_settings(), geos=[("Lille", 50.6, 3.0, 30)])
    offers = list(src.fetch_offers())
    companies = list(src.fetch_companies())
    assert [o.external_id for o in offers] == ["1"]
    assert len(companies) == 1 and companies[0].name == "ACME"


@respx.mock
def test_sends_bearer_key() -> None:
    route = respx.get(SEARCH_URL).mock(
        return_value=httpx.Response(200, json={"jobs": [], "recruiters": []})
    )
    src = LaBonneAlternanceSource(_settings(api_key="secret-k"),
                                  geos=[("Lille", 50.6, 3.0, 30)])
    list(src.fetch_offers())
    assert route.calls.last.request.headers["Authorization"] == "Bearer secret-k"
