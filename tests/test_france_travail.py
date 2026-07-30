"""France Travail client: pure mapping + HTTP flow (OAuth + paginated search)."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest
import respx

from jobpilot.config import Settings
from jobpilot.sources.france_travail import FranceTravailSource, map_offer

TOKEN_URL = "https://auth.test/token"
SEARCH_URL = "https://api.test/offres/search"


def _settings() -> Settings:
    return Settings(
        db_path=Path(":memory:"), log_dir=Path("logs"), config_dir=Path("config"),
        schema_path=Path("schema.sql"), migrations_dir=Path("migrations"),
        embed_model="x", queue_threshold=0.6,
        ft_client_id="id", ft_client_secret="secret",
        ft_token_url=TOKEN_URL, ft_search_url=SEARCH_URL,
        ft_scope="api_offresdemploiv2 o2dsoffre", ft_published_since=31,
        lba_api_key=None,
        gmail_address=None, gmail_app_password=None, email_alert_since_days=7,
        wttj_app_id="APP", wttj_api_key=None, wttj_index="idx",
    )


# ----- pure mapping -----

def test_map_offer_alternance() -> None:
    raw = {
        "id": "0001",
        "intitule": "Alternance Analyste SOC",
        "description": "Azure Sentinel, KQL, cybersécurité.",
        "entreprise": {"nom": "ACME"},
        "lieuTravail": {"libelle": "59 - LILLE"},
        "typeContrat": "STG",  # overridden by alternance flag below
        "alternance": True,
        "dateCreation": "2026-07-20T09:00:00.000Z",
        "competences": [{"libelle": "Azure"}, {"libelle": "SIEM"}],
        "origineOffre": {"urlOrigine": "https://candidat.francetravail.fr/o/1"},
    }
    rec = map_offer(raw)
    assert rec is not None
    assert rec.external_id == "0001"
    assert rec.contract_type == "alternance"
    assert rec.city == "59 - LILLE"
    assert rec.stack_tags == ["Azure", "SIEM"]
    assert rec.url == "https://candidat.francetravail.fr/o/1"


def test_map_offer_parses_duration_from_libelle() -> None:
    raw = {"id": "7", "intitule": "Alternance SecOps", "alternance": True,
           "typeContrat": "CDD", "typeContratLibelle": "CDD - 12 Mois",
           "origineOffre": {}}
    rec = map_offer(raw)
    assert rec is not None and rec.duration_months == 12


def test_map_offer_stage_by_typecontrat() -> None:
    raw = {"id": "2", "intitule": "Stage Pentest", "typeContrat": "STG",
           "origineOffre": {}}
    rec = map_offer(raw)
    assert rec is not None and rec.contract_type == "stage"


def test_map_offer_builds_fallback_url() -> None:
    raw = {"id": "42", "intitule": "CDI SecOps", "typeContrat": "CDI"}
    rec = map_offer(raw)
    assert rec is not None
    assert rec.url.endswith("/42")
    assert rec.contract_type == "cdi"


def test_map_offer_without_title_is_dropped() -> None:
    assert map_offer({"id": "9", "origineOffre": {}}) is None


def test_map_offer_parses_contact_email() -> None:
    raw = {
        "id": "51",
        "intitule": "Alternance Analyste SOC",
        "typeContrat": "CDD",
        "origineOffre": {},
        "contact": {"nom": "Service RH", "courriel": "Recrutement@ACME.fr"},
    }
    rec = map_offer(raw)
    assert rec is not None
    assert rec.contact_email == "recrutement@acme.fr"


def test_map_offer_ignores_malformed_contact_email() -> None:
    for contact in ({}, {"courriel": "not-an-email"}, {"courriel": 123}, "oops"):
        raw = {
            "id": "52",
            "intitule": "Alternance SecOps",
            "typeContrat": "CDD",
            "origineOffre": {},
            "contact": contact,
        }
        rec = map_offer(raw)
        assert rec is not None and rec.contact_email is None


# ----- HTTP flow -----

@respx.mock
def test_fetch_offers_paginates_and_dedups() -> None:
    respx.post(TOKEN_URL).mock(
        return_value=httpx.Response(200, json={"access_token": "tok",
                                               "expires_in": 1499})
    )

    def _offer(i: int) -> dict:
        return {"id": str(i), "intitule": f"Alternance {i}",
                "alternance": True, "origineOffre": {"urlOrigine": f"https://x/{i}"}}

    # One search config, two pages: full page (206) then short page (ends).
    page1 = [_offer(i) for i in range(100)]
    page2 = [_offer(i) for i in range(100, 130)]
    route = respx.get(SEARCH_URL)
    route.side_effect = [
        httpx.Response(206, json={"resultats": page1}),
        httpx.Response(200, json={"resultats": page2}),
    ]

    src = FranceTravailSource(
        _settings(),
        filters=[{"region": "32"}],  # single filter + single keyword => deterministic
        keywords=["cybersécurité"],
    )
    recs = list(src.fetch_offers())
    assert len(recs) == 130
    assert recs[0].contract_type == "alternance"


@respx.mock
def test_search_retries_on_429_then_succeeds() -> None:
    respx.post(TOKEN_URL).mock(
        return_value=httpx.Response(200, json={"access_token": "tok",
                                               "expires_in": 1499})
    )
    route = respx.get(SEARCH_URL)
    route.side_effect = [
        httpx.Response(429, headers={"Retry-After": "0"}),
        httpx.Response(200, json={"resultats": [
            {"id": "1", "intitule": "Alternance SOC", "alternance": True,
             "origineOffre": {"urlOrigine": "https://x/1"}}]}),
    ]
    src = FranceTravailSource(
        _settings(), filters=[{"region": "32"}], keywords=["cybersécurité"]
    )
    recs = list(src.fetch_offers())
    assert len(recs) == 1


def test_missing_credentials_raises() -> None:
    from jobpilot.config import MissingCredentialError

    bad = _settings()
    bad = Settings(**{**bad.__dict__, "ft_client_id": None})
    with pytest.raises(MissingCredentialError):
        FranceTravailSource(bad)
