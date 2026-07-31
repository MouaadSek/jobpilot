"""Task 36 item 2: downloads named for the employer.

The filename is set in the Content-Disposition header, never on disk: on-disk
paths stay keyed by application id, so every module that resolves an artefact
path is unaffected and no migration is needed.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from jobpilot.apply_flow import APPLICATION_LOCK
from jobpilot.dashboard import create_app, database_connection
from jobpilot.downloads import MAX_COMPANY_CHARS, download_filename, slugify
from jobpilot.state import transition
from tests.test_dashboard import _offer_application

# ----- slugify -----


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Advens", "Advens"),
        ("Société Générale", "Societe_Generale"),
        # The case the spec names: this must not contribute a path separator.
        ("Société Générale / IT", "Societe_Generale_IT"),
        ("Thales\\Defence", "Thales_Defence"),
        ('Orange "Cyberdefense"', "Orange_Cyberdefense"),
        ("Capgemini   Engineering", "Capgemini_Engineering"),
        ("Atos-Worldline", "Atos-Worldline"),
        ("../../etc/passwd", "etc_passwd"),
        ("  leading and trailing  ", "leading_and_trailing"),
        ("Déjà Vu & Co.", "Deja_Vu_Co"),
    ],
)
def test_slugify_reduces_to_a_safe_filename_fragment(raw: str, expected: str) -> None:
    assert slugify(raw) == expected


@pytest.mark.parametrize("raw", ["", None, "   ", "///", "***", "…", "、。", "!!!"])
def test_slugify_returns_empty_when_nothing_survives(raw: str | None) -> None:
    assert slugify(raw) == ""


def test_slugify_never_yields_a_path_separator() -> None:
    for raw in ("a/b", "a\\b", "..", "../..", "C:\\Users", "/etc/passwd"):
        result = slugify(raw)
        assert "/" not in result
        assert "\\" not in result
        assert result not in (".", "..")


def test_slugify_caps_length() -> None:
    slug = slugify("Société Générale Corporate and Investment Banking France SA" * 4)

    assert len(slug) <= MAX_COMPANY_CHARS
    assert not slug.endswith("_")


def test_a_two_hundred_character_name_is_capped_and_still_usable() -> None:
    name = download_filename("cv.pdf", application_id=7, company="A" * 200,
                             candidate="Mouaad Sekkouri")

    assert name.endswith(".pdf")
    assert len(name.split("_CV_")[0]) <= MAX_COMPANY_CHARS


# ----- filenames -----


def test_the_documented_shape() -> None:
    assert download_filename(
        "cv.pdf", application_id=1, company="Advens", candidate="Mouaad Sekkouri"
    ) == "Advens_CV_Mouaad_Sekkouri.pdf"
    assert download_filename(
        "motivation_letter.pdf", application_id=1, company="Advens",
        candidate="Mouaad Sekkouri",
    ) == "Advens_LM_Mouaad_Sekkouri.pdf"


@pytest.mark.parametrize("company", ["", None, "***", "   "])
def test_the_application_id_is_the_fallback_when_the_company_slugifies_away(
    company: str | None,
) -> None:
    """Falling back keeps the name unique and never empty."""

    name = download_filename(
        "cv.pdf", application_id=42, company=company, candidate="Mouaad Sekkouri"
    )

    assert name == "application_42_CV_Mouaad_Sekkouri.pdf"


def test_a_missing_candidate_name_simply_drops_that_part() -> None:
    assert download_filename(
        "cv.pdf", application_id=3, company="Advens", candidate=None
    ) == "Advens_CV.pdf"


def test_the_extension_follows_the_artefact() -> None:
    assert download_filename(
        "tracker.tsv", application_id=3, company="Advens"
    ).endswith("_Tracker.tsv")
    assert download_filename(
        "tailored_cv.html", application_id=3, company="Advens"
    ).endswith("_CV.html")


# ----- serving -----


@contextmanager
def _client(db: sqlite3.Connection, tmp_path: Path) -> Iterator[TestClient]:
    app = create_app(output_root=tmp_path)

    def connection() -> Iterator[sqlite3.Connection]:
        with APPLICATION_LOCK:
            yield db

    app.dependency_overrides[database_connection] = connection
    with TestClient(app) as client:
        yield client


def _ready_with_artifacts(db: sqlite3.Connection, tmp_path: Path, company: str) -> int:
    with APPLICATION_LOCK:
        application_id = _offer_application(
            db, title="Analyste SOC", score=0.9, suffix=f"dl-{company[:6]}"
        )
        db.execute(
            "UPDATE companies SET name = ? WHERE id = ("
            " SELECT company_id FROM offers WHERE id = ("
            "  SELECT offer_id FROM applications WHERE id = ?))",
            (company, application_id),
        )
        db.execute(
            "INSERT INTO profile (id, full_name, target_roles, hard_skills, certs, "
            "languages, locations_ok, contract_wanted) "
            "VALUES (1, 'Mouaad Sekkouri', '[]', '[]', '[]', '{}', '[]', '[]')"
        )
        transition(db, application_id, "generating")
        transition(db, application_id, "ready")
    directory = tmp_path / str(application_id)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "cv.pdf").write_bytes(b"%PDF-cv")
    (directory / "motivation_letter.pdf").write_bytes(b"%PDF-lm")
    return application_id


def test_download_names_the_file_for_the_employer(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    application_id = _ready_with_artifacts(dashboard_db, tmp_path, "Advens")

    with _client(dashboard_db, tmp_path) as client:
        response = client.get(f"/files/{application_id}/cv.pdf")

    assert response.status_code == 200
    disposition = response.headers["content-disposition"]
    assert "attachment" in disposition
    assert "Advens_CV_Mouaad_Sekkouri.pdf" in disposition


def test_a_company_with_a_slash_cannot_inject_a_path_separator(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    application_id = _ready_with_artifacts(dashboard_db, tmp_path, "Société Générale / IT")

    with _client(dashboard_db, tmp_path) as client:
        response = client.get(f"/files/{application_id}/cv.pdf")

    disposition = response.headers["content-disposition"]
    assert "Societe_Generale_IT_CV_Mouaad_Sekkouri.pdf" in disposition
    assert "/IT" not in disposition
