"""ATS pollers: per-ATS mapping, contract inference, and the polling flow."""

from __future__ import annotations

from pathlib import Path

import httpx
import respx

from jobpilot.config import Settings
from jobpilot.sources.ats import (
    ATSSource,
    infer_contract,
    map_greenhouse,
    map_lever,
    map_smartrecruiters,
)


def _settings() -> Settings:
    return Settings(
        db_path=Path(":memory:"), log_dir=Path("logs"), config_dir=Path("config"),
        schema_path=Path("schema.sql"), migrations_dir=Path("migrations"),
        embed_model="x", queue_threshold=0.6, ft_client_id=None,
        ft_client_secret=None, ft_token_url="", ft_search_url="", ft_scope="",
        ft_published_since=31,
        lba_api_key=None,
        gmail_address=None, gmail_app_password=None, email_alert_since_days=7,
        wttj_app_id="APP", wttj_api_key=None, wttj_index="idx",
    )


def test_infer_contract() -> None:
    assert infer_contract("Alternance DevSecOps") == "alternance"
    assert infer_contract("Security Internship") == "stage"
    assert infer_contract("Senior SRE") == "unknown"


def test_map_greenhouse() -> None:
    rec = map_greenhouse(
        {"id": 7, "title": "Stage Sécurité", "absolute_url": "https://gh/7",
         "location": {"name": "Paris"}, "content": "<p>desc</p>",
         "updated_at": "2026-07-01T00:00:00Z"},
        company="ACME",
    )
    assert rec is not None
    assert rec.external_id == "7"
    assert rec.contract_type == "stage"
    assert rec.city == "Paris"


def test_map_lever_creation_ms_to_iso() -> None:
    rec = map_lever(
        {"id": "abc", "text": "Alternance Cloud", "hostedUrl": "https://lever/abc",
         "categories": {"location": "Lille", "commitment": "Apprenticeship",
                        "team": "Security"},
         "createdAt": 1700000000000, "descriptionPlain": "desc"},
        company="ACME",
    )
    assert rec is not None
    assert rec.contract_type == "alternance"
    assert rec.stack_tags == ["Security"]
    assert rec.posted_at is not None and rec.posted_at.startswith("2023-")


def test_map_smartrecruiters_fallback_url() -> None:
    rec = map_smartrecruiters(
        {"id": "p1", "name": "Internship SOC", "location": {"city": "Paris"}},
        company="ACME", board="ACMEInc",
    )
    assert rec is not None
    assert rec.url == "https://jobs.smartrecruiters.com/ACMEInc/p1"
    assert rec.contract_type == "stage"


@respx.mock
def test_ats_source_polls_multiple_boards() -> None:
    respx.get("https://boards-api.greenhouse.io/v1/boards/acme/jobs?content=true").mock(
        return_value=httpx.Response(200, json={"jobs": [
            {"id": 1, "title": "Alternance SecOps", "absolute_url": "https://gh/1"}]})
    )
    respx.get("https://api.lever.co/v0/postings/acme?mode=json").mock(
        return_value=httpx.Response(200, json=[
            {"id": "l1", "text": "Stage Pentest", "hostedUrl": "https://lever/l1",
             "categories": {}}])
    )
    src = ATSSource(_settings(), targets=[
        {"ats": "greenhouse", "board": "acme", "company": "ACME"},
        {"ats": "lever", "board": "acme", "company": "ACME"},
    ])
    recs = list(src.fetch_offers())
    assert {r.title for r in recs} == {"Alternance SecOps", "Stage Pentest"}


@respx.mock
def test_ats_source_survives_one_failing_board() -> None:
    respx.get("https://boards-api.greenhouse.io/v1/boards/dead/jobs?content=true").mock(
        return_value=httpx.Response(404)
    )
    respx.get("https://api.lever.co/v0/postings/live?mode=json").mock(
        return_value=httpx.Response(200, json=[
            {"id": "l1", "text": "Alternance X", "hostedUrl": "https://lever/l1",
             "categories": {}}])
    )
    src = ATSSource(_settings(), targets=[
        {"ats": "greenhouse", "board": "dead", "company": "Dead"},
        {"ats": "lever", "board": "live", "company": "Live"},
    ])
    recs = list(src.fetch_offers())
    assert [r.title for r in recs] == ["Alternance X"]


def test_ats_skips_malformed_targets() -> None:
    src = ATSSource(_settings(), targets=[
        {"ats": "unknownats", "board": "x"},
        {"ats": "greenhouse"},  # no board
    ])
    assert list(src.fetch_offers()) == []
