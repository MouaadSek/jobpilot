"""Task 43 item 3: pasting the description is a first-class path.

Not a fallback for when the extension fails, not hidden behind a disclosure.
Some pages will never parse cleanly — a login wall, a PDF, an iframe, a site
nobody wrote a selector for — and pasting must never feel like the error case.

It reaches the same endpoint by the same code path as the extension. The two
differ only in what they can send: an extension can only send JSON, an HTML
form can only send a form.
"""

from __future__ import annotations

import hashlib
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient

from jobpilot.dashboard import IMPORT_PATH, create_app, database_connection
from jobpilot.offer_import import clean_description
from tests.test_offer_import import ALERT_CARD, POSTING, _fake_score


def _application(
    db: sqlite3.Connection,
    *,
    suffix: str = "p",
    status: str = "queued",
    description: str = ALERT_CARD,
    url: str = "https://www.linkedin.com/jobs/view/555",
) -> int:
    source_id = db.execute(
        "SELECT id FROM sources WHERE name = 'linkedin_alert'"
    ).fetchone()["id"]
    company_id = db.execute(
        "INSERT INTO companies (name) VALUES (?)", (f"Acme {suffix}",)
    ).lastrowid
    offer_id = db.execute(
        "INSERT INTO offers (source_id, company_id, external_id, url, title, "
        "description, contract_type, city, content_hash) "
        "VALUES (?, ?, ?, ?, 'Alternance SOC', ?, 'alternance', 'Lille', ?)",
        (
            source_id, company_id, f"ext-{suffix}", url, description,
            hashlib.sha256(suffix.encode()).hexdigest(),
        ),
    ).lastrowid
    application_id = int(
        db.execute(
            "INSERT INTO applications (offer_id, company_id, kind, status) "
            "VALUES (?, ?, 'offer', ?)",
            (offer_id, company_id, status),
        ).lastrowid
    )
    db.commit()
    return application_id


@contextmanager
def _client(conn: sqlite3.Connection) -> Iterator[TestClient]:
    app = create_app(score_pass=_fake_score())
    app.dependency_overrides[database_connection] = lambda: conn
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


# ----- always visible -----


@pytest.mark.parametrize(
    "status", ("queued", "ready", "applied", "skipped", "rejected")
)
def test_the_paste_box_is_on_every_application_whatever_its_state(
    dashboard_db: sqlite3.Connection, status: str
) -> None:
    """Not conditional on the extension having failed, and not conditional on
    the status either: a posting can turn out to be worth re-reading at any
    point."""

    application_id = _application(dashboard_db, status=status, suffix=status)

    with _client(dashboard_db) as client:
        page = client.get(f"/application/{application_id}")

    assert "Coller la description de l'offre" in page.text
    assert '<textarea name="description"' in page.text


def test_the_box_is_not_hidden_behind_a_disclosure(
    dashboard_db: sqlite3.Connection,
) -> None:
    application_id = _application(dashboard_db)

    with _client(dashboard_db) as client:
        page = client.get(f"/application/{application_id}")

    box = page.text.split('class="import-box"')[1].split("</form>")[0]

    # A disclosure, a hidden container or a display:none is the "fallback" look
    # this must not have. The hidden inputs carrying the URL are not that.
    assert "<details" not in box
    assert "display:none" not in box.replace(" ", "")
    opening_tag = page.text.split('class="import-box"')[0].rsplit("<", 1)[-1]
    assert "hidden" not in opening_tag


def test_a_thin_description_is_named_as_the_problem_it_is(
    dashboard_db: sqlite3.Connection,
) -> None:
    """The card is 113 characters and the CV was tailored against it. Saying so
    is the whole reason anyone would paste."""

    application_id = _application(dashboard_db, description=ALERT_CARD)

    with _client(dashboard_db) as client:
        page = client.get(f"/application/{application_id}")

    assert "carte d'alerte, pas une annonce" in page.text


# ----- the same endpoint -----


def test_the_form_posts_to_the_same_endpoint_as_the_extension(
    dashboard_db: sqlite3.Connection,
) -> None:
    application_id = _application(dashboard_db)

    with _client(dashboard_db) as client:
        page = client.get(f"/application/{application_id}")

    assert f'action="{IMPORT_PATH}"' in page.text


def test_pasting_stores_the_description_and_returns_to_the_application(
    dashboard_db: sqlite3.Connection,
) -> None:
    application_id = _application(dashboard_db)

    with _client(dashboard_db) as client:
        response = client.post(
            IMPORT_PATH,
            data={
                "application_id": str(application_id),
                "url": "https://www.linkedin.com/jobs/view/555",
                "description": POSTING,
            },
            follow_redirects=False,
        )

    stored = dashboard_db.execute(
        "SELECT o.description, o.imported_at FROM offers o "
        "JOIN applications a ON a.offer_id = o.id WHERE a.id = ?",
        (application_id,),
    ).fetchone()

    # A form submission gets a page back, not JSON printed over the page it came
    # from.
    assert response.status_code == 303
    assert response.headers["location"].startswith(f"/application/{application_id}")
    assert stored["description"] == clean_description(POSTING)
    assert stored["imported_at"] is not None


def test_a_pasted_description_triggers_the_same_rescore(
    dashboard_db: sqlite3.Connection,
) -> None:
    application_id = _application(dashboard_db)
    offer_id = dashboard_db.execute(
        "SELECT offer_id FROM applications WHERE id = ?", (application_id,)
    ).fetchone()["offer_id"]
    dashboard_db.execute(
        "INSERT INTO match_scores (offer_id, hard_filter_pass, final_score) "
        "VALUES (?, 1, 0.02)",
        (offer_id,),
    )
    dashboard_db.commit()

    with _client(dashboard_db) as client:
        client.post(
            IMPORT_PATH,
            data={
                "application_id": str(application_id),
                "url": "https://www.linkedin.com/jobs/view/555",
                "description": POSTING,
            },
            follow_redirects=False,
        )

    score = dashboard_db.execute(
        "SELECT final_score FROM match_scores WHERE offer_id = ?", (offer_id,)
    ).fetchone()["final_score"]

    assert score == 0.61


def test_a_short_paste_returns_the_page_with_the_reason_and_changes_nothing(
    dashboard_db: sqlite3.Connection,
) -> None:
    """A rejected paste must not look like a lost page, and must not have
    replaced a real description with a cookie banner on the way."""

    application_id = _application(dashboard_db, description=POSTING)

    with _client(dashboard_db) as client:
        response = client.post(
            IMPORT_PATH,
            data={
                "application_id": str(application_id),
                "url": "https://www.linkedin.com/jobs/view/555",
                "description": "Accepter les cookies",
            },
        )

    stored = dashboard_db.execute(
        "SELECT o.description FROM offers o JOIN applications a ON a.offer_id = o.id "
        "WHERE a.id = ?",
        (application_id,),
    ).fetchone()

    assert response.status_code == 422
    assert "trop courte" in response.text
    assert "Coller la description de l'offre" in response.text
    assert stored["description"] == POSTING


def test_the_extension_still_gets_json_from_the_same_endpoint(
    dashboard_db: sqlite3.Connection,
) -> None:
    """One endpoint, two representations. The JSON caller sends no
    application_id and gets the result rather than a redirect."""

    _application(dashboard_db)

    with _client(dashboard_db) as client:
        response = client.post(
            IMPORT_PATH,
            json={
                "url": "https://www.linkedin.com/jobs/view/555",
                "description": POSTING,
            },
        )

    assert response.status_code == 200
    assert response.json()["imported_chars"] == len(clean_description(POSTING))


def test_an_already_imported_offer_says_so_rather_than_repeating_the_pitch(
    dashboard_db: sqlite3.Connection,
) -> None:
    application_id = _application(dashboard_db)

    with _client(dashboard_db) as client:
        client.post(
            IMPORT_PATH,
            data={
                "application_id": str(application_id),
                "url": "https://www.linkedin.com/jobs/view/555",
                "description": POSTING,
            },
            follow_redirects=False,
        )
        page = client.get(f"/application/{application_id}")

    assert "Description importée le" in page.text
    assert "carte d'alerte" not in page.text
