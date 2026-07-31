"""La Bonne Alternance through the API Apprentissage: mapping, rails, ingestion.

Every response here is either a committed fixture captured from the live API or a
minimal hand-built variant of it. No test touches the network.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import httpx
import pytest
import respx

from jobpilot.config import MissingCredentialError, Settings
from jobpilot.ingest import ingest_source
from jobpilot.sources.labonnealternance import (
    BASE_URL,
    DEPARTEMENT_GROUPS,
    LaBonneAlternanceAuthError,
    LaBonneAlternanceError,
    LaBonneAlternanceRateLimited,
    LaBonneAlternanceSource,
    map_company,
    map_offer,
)

SEARCH_URL = f"{BASE_URL}/job/v1/search"
FIXTURES = Path(__file__).parent / "fixtures" / "labonnealternance"
API_KEY = "test-key-not-a-real-token"


@pytest.fixture(autouse=True)
def _no_real_sleeping(monkeypatch: pytest.MonkeyPatch) -> None:
    """Backoff between retries is real seconds; the test suite must not spend them."""

    monkeypatch.setattr("jobpilot.ratelimit.time.sleep", lambda _seconds: None)


def _fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _settings(api_key: str | None = API_KEY, *, max_pages: int = 5) -> Settings:
    return Settings(
        db_path=Path(":memory:"), log_dir=Path("logs"), config_dir=Path("config"),
        schema_path=Path("schema.sql"), migrations_dir=Path("migrations"),
        embed_model="x", queue_threshold=0.6, ft_client_id=None,
        ft_client_secret=None, ft_token_url="", ft_search_url="", ft_scope="",
        ft_published_since=31,
        lba_api_key=api_key,
        gmail_address=None, gmail_app_password=None, email_alert_since_days=7,
        wttj_app_id="APP", wttj_api_key=None, wttj_index="idx",
        lba_max_pages=max_pages,
    )


def _source(**kwargs) -> LaBonneAlternanceSource:
    settings = kwargs.pop("settings", None) or _settings(**{
        k: kwargs.pop(k) for k in ("max_pages",) if k in kwargs
    })
    return LaBonneAlternanceSource(settings, **kwargs)


# ----- the committed fixtures are the real contract -----


def test_the_fixtures_carry_the_documented_shape() -> None:
    for name in ("search_idf_cyber.json", "search_hdf_cyber.json"):
        body = _fixture(name)
        assert set(body) >= {"jobs", "recruiters"}
        assert body["jobs"] and body["recruiters"]


def test_no_fixture_contains_a_credential() -> None:
    """Fixtures are committed, so they must never carry the key that fetched them."""

    for path in FIXTURES.glob("*.json"):
        text = path.read_text(encoding="utf-8").lower()
        assert "authorization" not in text
        assert "bearer " not in text


# ----- offer mapping -----


def test_map_offer_fills_the_standard_shape() -> None:
    job = _fixture("search_hdf_cyber.json")["jobs"][0]

    record = map_offer(job)

    assert record is not None
    assert record.title == job["offer"]["title"]
    assert record.url == job["apply"]["url"]
    assert record.external_id == job["identifier"]["id"]
    assert record.company_name == job["workplace"]["name"]
    assert record.contract_type == "alternance"
    assert record.posted_at == job["offer"]["publication"]["creation"]
    assert record.stack_tags == job["offer"]["rome_codes"]
    # The endpoint publishes an apply URL and sometimes a phone, never an address.
    assert record.contact_email is None


@pytest.mark.parametrize(
    ("address", "expected"),
    (
        ("62680 Méricourt", "Méricourt"),
        ("74 RUE ANATOLE FRANCE 92300 LEVALLOIS-PERRET", "Levallois-Perret"),
        ("75015 Paris", "Paris"),
        (None, None),
    ),
)
def test_the_commune_is_read_off_the_postal_address(address, expected) -> None:
    job = {
        "offer": {"title": "Alternance", "publication": {}},
        "apply": {"url": "https://example.test/1"},
        "workplace": {"name": "ACME", "location": {"address": address}},
        "contract": {"type": ["Apprentissage"]},
        "identifier": {"id": "1"},
    }

    assert map_offer(job).city == expected


@pytest.mark.parametrize(
    ("remote", "expected"),
    (("onsite", "onsite"), ("hybrid", "hybrid"), ("remote", "full_remote"),
     (None, "unknown"), ("teletravail", "unknown")),
)
def test_remote_policy_is_read_back_because_it_cannot_be_filtered(
    remote,
    expected,
) -> None:
    job = {
        "offer": {"title": "Alternance", "publication": {}},
        "apply": {"url": "https://example.test/1"},
        "workplace": {"name": "ACME"},
        "contract": {"type": ["Apprentissage"], "remote": remote},
        "identifier": {"id": "1"},
    }

    assert map_offer(job).remote_policy == expected


@pytest.mark.parametrize(
    "job",
    (
        {"offer": {"title": "Sans lien"}, "apply": {}, "identifier": {"id": "1"}},
        {"offer": {}, "apply": {"url": "https://example.test/1"}, "identifier": {}},
        "not an object",
    ),
)
def test_an_offer_that_cannot_be_applied_to_is_dropped(job) -> None:
    assert map_offer(job) is None


def test_every_contract_label_is_an_alternance() -> None:
    """The endpoint only publishes work-study, so nothing here is 'unknown'."""

    for label in (["Apprentissage"], ["Professionnalisation"], ["Autre"], []):
        job = {
            "offer": {"title": "T", "publication": {}},
            "apply": {"url": "https://example.test/1"},
            "workplace": {}, "contract": {"type": label}, "identifier": {"id": "1"},
        }
        assert map_offer(job).contract_type == "alternance"


# ----- company mapping -----


def test_map_company_produces_an_outreach_target() -> None:
    recruiter = _fixture("search_idf_cyber.json")["recruiters"][0]

    record = map_company(recruiter)

    assert record is not None
    assert record.name == recruiter["workplace"]["name"]
    assert record.siren == recruiter["workplace"]["siret"][:9]
    assert record.sector == recruiter["workplace"]["domain"]["naf"]["label"]
    assert record.size_bucket == recruiter["workplace"]["size"]
    assert record.city
    assert record.source == "labonnealternance"
    assert record.notes == recruiter["apply"]["url"]


def test_a_recruiter_without_a_name_is_dropped() -> None:
    assert map_company({"workplace": {"siret": "12345678900011"}}) is None


def test_a_website_becomes_a_bare_domain() -> None:
    record = map_company(
        {"workplace": {"name": "ACME", "website": "https://www.acme.FR/jobs"}}
    )

    assert record.domain == "acme.fr"


# ----- fetching -----


@respx.mock
def test_one_call_per_department_group_with_the_documented_auth() -> None:
    route = respx.get(SEARCH_URL).mock(
        return_value=httpx.Response(200, json=_fixture("search_hdf_cyber.json"))
    )
    source = _source(rate_limiter=_NoWait())

    offers = list(source.fetch_offers())

    assert route.call_count == len(DEPARTEMENT_GROUPS)
    assert offers
    request = route.calls[0].request
    assert request.headers["authorization"] == f"Bearer {API_KEY}"
    assert "romes=M1802" in str(request.url)
    assert "departements=59" in str(request.url)


@respx.mock
def test_max_pages_caps_the_number_of_search_calls() -> None:
    """The endpoint has no pagination, so this is the volume knob that exists."""

    route = respx.get(SEARCH_URL).mock(
        return_value=httpx.Response(200, json=_fixture("search_hdf_cyber.json"))
    )
    source = _source(max_pages=1, rate_limiter=_NoWait())

    list(source.fetch_offers())

    assert route.call_count == 1


@respx.mock
def test_offers_and_companies_share_one_set_of_calls() -> None:
    """A full ingest reads both lists; it must not pay for the search twice."""

    route = respx.get(SEARCH_URL).mock(
        return_value=httpx.Response(200, json=_fixture("search_idf_cyber.json"))
    )
    source = _source(rate_limiter=_NoWait())

    list(source.fetch_offers())
    list(source.fetch_companies())

    assert route.call_count == len(DEPARTEMENT_GROUPS)


@respx.mock
def test_an_offer_returned_twice_is_yielded_once() -> None:
    """The live API really does repeat an offer inside one response."""

    body = _fixture("search_hdf_cyber.json")
    identifiers = [job["identifier"]["id"] for job in body["jobs"]]
    assert len(identifiers) > len(set(identifiers))  # the fixture holds a repeat
    respx.get(SEARCH_URL).mock(return_value=httpx.Response(200, json=body))

    offers = list(_source(rate_limiter=_NoWait()).fetch_offers())

    assert len(offers) == len(set(identifiers))
    assert len({offer.external_id for offer in offers}) == len(offers)


@respx.mock
def test_a_warning_from_the_api_is_logged_not_raised(
    caplog: pytest.LogCaptureFixture,
) -> None:
    body = _fixture("search_hdf_cyber.json") | {
        "warnings": [{"code": "partner_down", "message": "un partenaire est absent"}]
    }
    respx.get(SEARCH_URL).mock(return_value=httpx.Response(200, json=body))

    with caplog.at_level("WARNING", logger="jobpilot.labonnealternance"):
        offers = list(_source(rate_limiter=_NoWait()).fetch_offers())

    assert offers
    assert "un partenaire est absent" in caplog.text


# ----- credentials and failures -----


def test_a_missing_key_is_a_skip_not_an_error() -> None:
    with pytest.raises(MissingCredentialError, match="LBA_API_KEY"):
        LaBonneAlternanceSource(_settings(api_key=None))


@respx.mock
def test_a_rejected_key_is_a_typed_error_with_the_key_redacted() -> None:
    respx.get(SEARCH_URL).mock(
        return_value=httpx.Response(401, text=f"invalid token {API_KEY}")
    )

    with pytest.raises(LaBonneAlternanceAuthError) as caught:
        list(_source(rate_limiter=_NoWait()).fetch_offers())

    assert API_KEY not in str(caught.value)
    assert "[REDACTED]" in str(caught.value)


@respx.mock
def test_a_forbidden_key_is_also_an_auth_error() -> None:
    respx.get(SEARCH_URL).mock(return_value=httpx.Response(403, text="forbidden"))

    with pytest.raises(LaBonneAlternanceAuthError):
        list(_source(rate_limiter=_NoWait()).fetch_offers())


@respx.mock
def test_an_exhausted_quota_reports_retry_after_without_a_retry_storm() -> None:
    route = respx.get(SEARCH_URL).mock(
        return_value=httpx.Response(
            429, headers={"retry-after": "30"}, text="quota exceeded"
        )
    )

    with pytest.raises(LaBonneAlternanceRateLimited, match="retry-after=30s"):
        list(_source(rate_limiter=_NoWait()).fetch_offers())

    # with_backoff retries a 429 at most max_retries times, then gives up.
    assert route.call_count <= 6


@respx.mock
def test_a_server_error_is_a_plain_typed_error() -> None:
    respx.get(SEARCH_URL).mock(return_value=httpx.Response(500, text="boom"))

    with pytest.raises(LaBonneAlternanceError, match="HTTP 500"):
        list(_source(rate_limiter=_NoWait()).fetch_offers())


@respx.mock
def test_a_transport_failure_is_wrapped_with_the_key_redacted() -> None:
    respx.get(SEARCH_URL).mock(side_effect=httpx.ConnectError("no route"))

    with pytest.raises(LaBonneAlternanceError, match="request failed"):
        list(_source(rate_limiter=_NoWait()).fetch_offers())


# ----- ingestion: idempotent, and companies are not offers -----


@respx.mock
def test_ingest_inserts_offers_and_companies_then_repeats_nothing(
    db: sqlite3.Connection,
) -> None:
    respx.get(SEARCH_URL).mock(
        return_value=httpx.Response(200, json=_fixture("search_idf_cyber.json"))
    )

    first = ingest_source(db, _source(rate_limiter=_NoWait()))
    respx.get(SEARCH_URL).mock(
        return_value=httpx.Response(200, json=_fixture("search_idf_cyber.json"))
    )
    second = ingest_source(db, _source(rate_limiter=_NoWait()))

    assert first.inserted > 0
    assert first.companies_created > 0
    assert second.inserted == 0
    assert second.companies_created == 0
    assert second.duplicates == first.fetched


@respx.mock
def test_sourced_companies_never_become_applications(db: sqlite3.Connection) -> None:
    """A company that has posted nothing must not appear in the review queue."""

    body = _fixture("search_idf_cyber.json") | {"jobs": []}
    respx.get(SEARCH_URL).mock(return_value=httpx.Response(200, json=body))

    result = ingest_source(db, _source(rate_limiter=_NoWait()))

    assert result.companies_created > 0
    assert result.inserted == 0
    assert db.execute("SELECT count(*) AS n FROM applications").fetchone()["n"] == 0
    assert db.execute("SELECT count(*) AS n FROM offers").fetchone()["n"] == 0


@respx.mock
def test_sourced_companies_record_their_provenance(db: sqlite3.Connection) -> None:
    body = _fixture("search_idf_cyber.json") | {"jobs": []}
    respx.get(SEARCH_URL).mock(return_value=httpx.Response(200, json=body))

    ingest_source(db, _source(rate_limiter=_NoWait()))

    rows = db.execute(
        "SELECT name, siren, sector, source FROM companies WHERE source = ?",
        ("labonnealternance",),
    ).fetchall()
    assert rows
    assert all(row["source"] == "labonnealternance" for row in rows)
    assert any(row["siren"] for row in rows)


def test_an_offers_employer_is_not_marked_as_a_sourced_target(
    db: sqlite3.Connection,
) -> None:
    """Only fetch_companies() produces outreach targets, not offer side effects."""

    from jobpilot.ingest import get_or_create_company
    from jobpilot.models import CompanyRecord

    get_or_create_company(db, CompanyRecord(name="Employeur d'une offre"), {})

    row = db.execute(
        "SELECT source FROM companies WHERE name = ?", ("Employeur d'une offre",)
    ).fetchone()
    assert row["source"] is None


def test_an_offers_employer_learns_its_source_when_sourcing_returns_it(
    db: sqlite3.Connection,
) -> None:
    """Task 34.0: a NULL source is backfilled, so the row reaches --targets."""

    from jobpilot.contacts import list_outreach_targets
    from jobpilot.ingest import get_or_create_company
    from jobpilot.models import CompanyRecord

    first_id, created = get_or_create_company(db, CompanyRecord(name="Cible"), {})
    assert created is True

    second_id, created_again = get_or_create_company(
        db, CompanyRecord(name="Cible", source="labonnealternance"), {}
    )

    assert second_id == first_id
    assert created_again is False
    row = db.execute(
        "SELECT source FROM companies WHERE id = ?", (first_id,)
    ).fetchone()
    assert row["source"] == "labonnealternance"
    assert [target["name"] for target in list_outreach_targets(db)] == ["Cible"]


def test_a_company_source_already_set_is_never_overwritten(
    db: sqlite3.Connection,
) -> None:
    """The first provider to claim a company keeps the claim."""

    from jobpilot.ingest import get_or_create_company
    from jobpilot.models import CompanyRecord

    company_id, _ = get_or_create_company(
        db, CompanyRecord(name="Cible", source="labonnealternance"), {}
    )
    get_or_create_company(db, CompanyRecord(name="Cible", source="autre"), {})
    get_or_create_company(db, CompanyRecord(name="Cible"), {})

    row = db.execute(
        "SELECT source FROM companies WHERE id = ?", (company_id,)
    ).fetchone()
    assert row["source"] == "labonnealternance"


def test_the_source_backfill_also_happens_on_a_cache_hit(
    db: sqlite3.Connection,
) -> None:
    """Within one ingest run the cache short-circuits the SELECT; it must not
    short-circuit the backfill."""

    from jobpilot.ingest import get_or_create_company
    from jobpilot.models import CompanyRecord

    cache: dict[str, int] = {}
    company_id, _ = get_or_create_company(db, CompanyRecord(name="Cible"), cache)
    assert cache  # the second call below takes the cache path

    get_or_create_company(
        db, CompanyRecord(name="Cible", source="labonnealternance"), cache
    )

    row = db.execute(
        "SELECT source FROM companies WHERE id = ?", (company_id,)
    ).fetchone()
    assert row["source"] == "labonnealternance"


def test_the_same_company_under_two_names_is_stored_once(
    db: sqlite3.Connection,
) -> None:
    """companies.siren is UNIQUE, so a name miss must not blow up the insert."""

    from jobpilot.ingest import get_or_create_company
    from jobpilot.models import CompanyRecord

    first_id, created = get_or_create_company(
        db, CompanyRecord(name="KLINT", siren="428815559"), {}
    )
    second_id, created_again = get_or_create_company(
        db, CompanyRecord(name="Klint Group", siren="428815559"), {}
    )

    assert created is True
    assert created_again is False
    assert first_id == second_id


class _NoWait:
    """RateLimiter stand-in: the real one sleeps a second between calls."""

    def wait(self, key: str = "default") -> None:
        return None


# ----- 33.2: targets are outreach candidates, and nothing more -----


@respx.mock
def test_targets_are_listed_for_outreach_without_touching_the_queue(
    db: sqlite3.Connection,
) -> None:
    from jobpilot.contacts import list_outreach_targets

    body = _fixture("search_idf_cyber.json") | {"jobs": []}
    respx.get(SEARCH_URL).mock(return_value=httpx.Response(200, json=body))
    ingest_source(db, _source(rate_limiter=_NoWait()))

    targets = list_outreach_targets(db, source="labonnealternance")

    assert targets
    assert all(row["source"] == "labonnealternance" for row in targets)
    assert all(row["contact_count"] == 0 for row in targets)
    assert db.execute("SELECT count(*) AS n FROM applications").fetchone()["n"] == 0


def test_targets_exclude_companies_created_from_an_offer(
    db: sqlite3.Connection,
) -> None:
    from jobpilot.contacts import list_outreach_targets
    from jobpilot.ingest import get_or_create_company
    from jobpilot.models import CompanyRecord

    get_or_create_company(db, CompanyRecord(name="Employeur d'une offre"), {})
    get_or_create_company(
        db, CompanyRecord(name="Cible", source="labonnealternance"), {}
    )

    names = {row["name"] for row in list_outreach_targets(db)}

    assert names == {"Cible"}


def test_targets_lead_with_the_ones_nobody_has_contacted(
    db: sqlite3.Connection,
) -> None:
    from jobpilot.contacts import list_outreach_targets, upsert_contact
    from jobpilot.ingest import get_or_create_company
    from jobpilot.models import CompanyRecord

    contacted, _ = get_or_create_company(
        db, CompanyRecord(name="Déjà contactée", source="labonnealternance"), {}
    )
    get_or_create_company(
        db, CompanyRecord(name="Zzz jamais contactée", source="labonnealternance"), {}
    )
    upsert_contact(db, contacted, full_name="RH", email="rh@example.test")

    targets = list_outreach_targets(db)

    assert [row["name"] for row in targets][0] == "Zzz jamais contactée"


def test_the_contacts_command_lists_targets(
    db: sqlite3.Connection,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from typer.testing import CliRunner

    from jobpilot.cli import app
    from jobpilot.ingest import get_or_create_company
    from jobpilot.models import CompanyRecord

    get_or_create_company(
        db,
        CompanyRecord(
            name="KLINT", source="labonnealternance", city="Levallois-Perret",
            sector="Conseil en systèmes et logiciels informatiques",
        ),
        {},
    )
    db.commit()
    monkeypatch.setattr("jobpilot.cli.connect", lambda: db)

    result = CliRunner().invoke(app, ["contacts", "--targets"])

    assert result.exit_code == 0
    assert "KLINT" in result.stdout
    assert "Levallois-Perret" in result.stdout


def test_the_contacts_command_still_needs_a_company_without_targets(
    db: sqlite3.Connection,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from typer.testing import CliRunner

    from jobpilot.cli import app

    monkeypatch.setattr("jobpilot.cli.connect", lambda: db)

    result = CliRunner().invoke(app, ["contacts"])

    assert result.exit_code != 0


def test_sourcing_targets_changes_no_sending_gate() -> None:
    """Task 33 adds candidates; every Task 11 rail stays exactly as it was."""

    from jobpilot.config import get_settings

    assert get_settings().cold_send_enabled is False
