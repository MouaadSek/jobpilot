"""The vocabulary tier is config, and its misses are countable."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from typer.testing import CliRunner

from jobpilot.cli import app
from jobpilot.facts import load_fact_bank
from jobpilot.review import vocabulary_misses
from jobpilot.state import log_event
from jobpilot.tailoring import SourcedBullet, TailoringError, validate_provenance
from jobpilot.vocabulary import (
    DEFAULT_VOCABULARY_PATH,
    GenericVocabularyError,
    TokenTier,
    load_generic_vocabulary,
    parse_rejections,
    rejection_message,
)

CITED = "experience.concentrix.incidents"


@pytest.fixture
def bank():
    return load_fact_bank()


@pytest.fixture
def seeded_application(db: sqlite3.Connection) -> int:
    """One queued application, so failures have somewhere to be recorded."""

    source_id = db.execute(
        "SELECT id FROM sources WHERE name = 'france_travail'"
    ).fetchone()["id"]
    company_id = db.execute("INSERT INTO companies (name) VALUES ('Acme')").lastrowid
    offer_id = db.execute(
        "INSERT INTO offers (source_id, company_id, external_id, url, title, "
        "description, contract_type, duration_months, city, content_hash) "
        "VALUES (?, ?, 'task-27', 'https://example.test/task-27', 'Analyste SOC', "
        "'SIEM dès septembre 2026', 'alternance', 12, 'Paris', 'hash-27')",
        (source_id, company_id),
    ).lastrowid
    application_id = db.execute(
        "INSERT INTO applications (offer_id, company_id, kind, status) "
        "VALUES (?, ?, 'offer', 'queued')",
        (offer_id, company_id),
    ).lastrowid
    db.commit()
    return int(application_id)


def _vocabulary(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "generic_vocabulary.yaml"
    path.write_text(body, encoding="utf-8")
    return path


def _check(text: str, bank, *, vocabulary_path: Path | None = None) -> None:
    validate_provenance(
        [SourcedBullet(text=text, sources=(CITED,))],
        bank,
        vocabulary_path=vocabulary_path,
    )


# ----- the file is the maintenance point -----


def test_the_committed_vocabulary_loads_and_covers_the_reported_token() -> None:
    terms = load_generic_vocabulary()

    assert "SIEM" in terms
    assert DEFAULT_VOCABULARY_PATH.exists()


def test_a_term_added_to_the_config_is_honoured_without_touching_code(
    bank,
    tmp_path: Path,
) -> None:
    """The whole point: a category word is a config edit, not a release."""

    before = _vocabulary(tmp_path, "version: 1\nterms:\n  - SIEM\n")
    with pytest.raises(TailoringError, match="unsupported capability 'SASE'"):
        _check("Migration vers une architecture SASE.", bank, vocabulary_path=before)

    after = _vocabulary(tmp_path, "version: 1\nterms:\n  - SIEM\n  - SASE\n")
    _check("Migration vers une architecture SASE.", bank, vocabulary_path=after)


def test_a_term_is_matched_whatever_its_case_and_accents(
    bank,
    tmp_path: Path,
) -> None:
    path = _vocabulary(tmp_path, "version: 1\nterms:\n  - télétravail\n")

    _check("Poste ouvert au Télétravail complet.", bank, vocabulary_path=path)


def test_a_quantity_cannot_be_smuggled_in_as_vocabulary(tmp_path: Path) -> None:
    """Tier 1 must not be reachable through tier 3, so the file may not try."""

    path = _vocabulary(tmp_path, "version: 1\nterms:\n  - SIEM\n  - 15 000\n")

    with pytest.raises(GenericVocabularyError, match="quantity"):
        load_generic_vocabulary(path)


@pytest.mark.parametrize(
    ("body", "message"),
    (
        ("terms:\n  - SIEM\n", "version"),
        ("version: 1\n", "terms"),
        ("version: 1\nterms: []\n", "terms"),
        ("version: 1\nterms:\n  - ''\n", "non-empty string"),
        ("- SIEM\n", "must be an object"),
    ),
)
def test_a_malformed_vocabulary_is_refused_loudly(
    tmp_path: Path,
    body: str,
    message: str,
) -> None:
    path = _vocabulary(tmp_path, body)

    with pytest.raises(GenericVocabularyError, match=message):
        load_generic_vocabulary(path)


def test_a_missing_vocabulary_file_is_an_error_not_an_empty_set(
    tmp_path: Path,
) -> None:
    """Silently allowing nothing would look like a strict validator, not a bug."""

    with pytest.raises(GenericVocabularyError, match="could not read"):
        load_generic_vocabulary(tmp_path / "absent.yaml")


# ----- rejections are logged and can be read back -----


def test_a_refusal_is_logged_with_token_tier_and_cited_facts(
    bank,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level("INFO", logger="jobpilot.tailoring"):
        with pytest.raises(TailoringError):
            _check("Analyse des alertes avec CrowdStrike.", bank)

    logged = "\n".join(record.getMessage() for record in caplog.records)
    assert "CrowdStrike" in logged
    assert "capability" in logged
    assert CITED in logged


def test_a_refused_quantity_is_logged_with_its_own_tier(
    bank,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level("INFO", logger="jobpilot.tailoring"):
        with pytest.raises(TailoringError):
            _check("Résolution de 15 000 incidents.", bank)

    logged = "\n".join(record.getMessage() for record in caplog.records)
    assert "attribution" in logged
    assert "capability" not in logged


@pytest.mark.parametrize(
    ("kind", "tier"),
    (
        ("number", TokenTier.ATTRIBUTION),
        ("organisation", TokenTier.ATTRIBUTION),
        ("designation", TokenTier.CAPABILITY),
        ("capability", TokenTier.CAPABILITY),
    ),
)
def test_a_stored_message_still_yields_its_tier(kind: str, tier: TokenTier) -> None:
    """Events outlive the code that wrote them, so the wording is the contract."""

    (rejection,) = parse_rejections([rejection_message(kind, "Zzz")])

    assert rejection.tier is tier
    assert rejection.token == "Zzz"


@pytest.mark.parametrize("kind", ("proper noun", "tool or skill"))
def test_a_retired_wording_is_still_read_back_as_capability(kind: str) -> None:
    """Rows written before the tier model must not crash the reader.

    These wordings are gone from the code but not from the events table, and
    both refused a named thing for the reason the capability tier now owns.
    """

    (rejection,) = parse_rejections([f"unsupported {kind} 'siem' in sourced content"])

    assert rejection.tier is TokenTier.CAPABILITY
    assert rejection.kind == kind
    assert rejection.token == "siem"


@pytest.mark.parametrize("kind", ("proper noun", "tool or skill"))
def test_a_retired_wording_may_not_be_written_again(kind: str) -> None:
    with pytest.raises(KeyError):
        rejection_message(kind, "siem")


def test_unrelated_error_text_yields_no_rejections() -> None:
    assert parse_rejections(["provider returned 429", ""]) == ()


@pytest.mark.parametrize(
    "message",
    (
        "unsupported proper noun 'siem' in sourced content",
        "unsupported tool or skill 'Splunk' in sourced content",
    ),
)
def test_wordings_retired_by_this_task_are_still_readable(message: str) -> None:
    """The events table outlives the code, so old failures still count."""

    (rejection,) = parse_rejections([message])

    assert rejection.tier is TokenTier.CAPABILITY


def test_a_retired_wording_can_be_read_but_never_written() -> None:
    with pytest.raises(KeyError):
        rejection_message("proper noun", "siem")


# ----- vocab-misses -----


def _failure(db: sqlite3.Connection, application_id: int, detail: dict) -> None:
    log_event(db, application_id, "generation_failed", detail)
    db.commit()


def test_misses_are_counted_across_errors_and_retry_attempts(
    db: sqlite3.Connection,
    seeded_application: int,
) -> None:
    _failure(
        db,
        seeded_application,
        {
            "error": rejection_message("capability", "CrowdStrike"),
            "attempts": [
                rejection_message("designation", "ISO 31000"),
                rejection_message("capability", "CrowdStrike"),
            ],
        },
    )

    misses = vocabulary_misses(db)

    by_token = {miss["token"]: miss for miss in misses}
    assert by_token["CrowdStrike"]["count"] == 2
    assert by_token["CrowdStrike"]["kind"] == "capability"
    assert by_token["ISO 31000"]["kind"] == "designation"
    assert by_token["CrowdStrike"]["applications"] == [seeded_application]


def test_attribution_refusals_are_not_offered_as_config_fixes(
    db: sqlite3.Connection,
    seeded_application: int,
) -> None:
    """No vocabulary entry may ever excuse a fabricated number or employer."""

    _failure(
        db,
        seeded_application,
        {
            "error": rejection_message("number", "15 000"),
            "attempts": [
                rejection_message("number", "15 000"),
                rejection_message("organisation", "Lionbridge"),
            ],
        },
    )

    assert vocabulary_misses(db) == []


def test_the_most_frequent_token_is_reported_first(
    db: sqlite3.Connection,
    seeded_application: int,
) -> None:
    _failure(db, seeded_application, {"error": rejection_message("capability", "Rare")})
    for _ in range(3):
        _failure(
            db,
            seeded_application,
            {"error": rejection_message("capability", "Common")},
        )

    misses = vocabulary_misses(db)

    assert [miss["token"] for miss in misses] == ["Common", "Rare"]
    assert vocabulary_misses(db, limit=1) == misses[:1]


def test_malformed_event_detail_is_skipped_not_fatal(
    db: sqlite3.Connection,
    seeded_application: int,
) -> None:
    db.execute(
        "INSERT INTO events (application_id, event, detail) VALUES (?, ?, ?)",
        (seeded_application, "generation_failed", "not json"),
    )
    _failure(db, seeded_application, {"error": rejection_message("capability", "Zzz")})

    assert [miss["token"] for miss in vocabulary_misses(db)] == ["Zzz"]


def test_the_command_lists_the_tokens_and_names_the_config_file(
    db: sqlite3.Connection,
    seeded_application: int,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _failure(
        db,
        seeded_application,
        {"error": rejection_message("capability", "CrowdStrike")},
    )
    monkeypatch.setattr("jobpilot.cli.connect", lambda: db)

    result = CliRunner().invoke(app, ["vocab-misses"])

    assert result.exit_code == 0
    assert "CrowdStrike" in result.stdout
    assert "generic_vocabulary.yaml" in result.stdout


def test_the_command_says_so_when_nothing_has_been_refused(
    db: sqlite3.Connection,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("jobpilot.cli.connect", lambda: db)

    result = CliRunner().invoke(app, ["vocab-misses"])

    assert result.exit_code == 0
    assert "no capability-tier rejections" in result.stdout


def test_the_events_row_written_by_a_real_failure_is_readable_by_the_command(
    db: sqlite3.Connection,
    seeded_application: int,
    bank,
) -> None:
    """The parser reads what the validator writes, not a hand-made string."""

    try:
        _check("Analyse des alertes avec CrowdStrike.", bank)
    except TailoringError as exc:
        _failure(db, seeded_application, {"error": str(exc)})
    else:  # pragma: no cover - the bullet is designed to fail
        pytest.fail("expected the bullet to be refused")

    assert [miss["token"] for miss in vocabulary_misses(db)] == ["CrowdStrike"]


def test_stored_details_survive_a_json_round_trip(
    db: sqlite3.Connection,
    seeded_application: int,
) -> None:
    detail = {"error": rejection_message("capability", "Élan")}
    _failure(db, seeded_application, detail)

    row = db.execute(
        "SELECT detail FROM events WHERE event = 'generation_failed'"
    ).fetchone()

    assert json.loads(row["detail"])["error"] == detail["error"]
    assert [miss["token"] for miss in vocabulary_misses(db)] == ["Élan"]
