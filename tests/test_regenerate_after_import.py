"""Task 43 item 4: after a description arrives, offer to redo the tailoring.

An application that is already `ready` was tailored against the alert card. Its
CV is on disk, adapted to 113 characters of nothing. Importing the real posting
re-scores the offer but does not touch those documents, so the banner has to
say that and offer the redo.

No new generation path: `ready` gets Task 34's Régénérer, `queued` gets the
ordinary Approve. A second entry point into generation is a second thing to
keep correct.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient

from jobpilot.dashboard import IMPORT_PATH, create_app, database_connection
from tests.test_offer_import import POSTING, _fake_score
from tests.test_paste_box import _application

OFFER_URL = "https://www.linkedin.com/jobs/view/555"


@contextmanager
def _client(conn: sqlite3.Connection) -> Iterator[TestClient]:
    app = create_app(score_pass=_fake_score())
    app.dependency_overrides[database_connection] = lambda: conn
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def _import(client: TestClient, application_id: int) -> str:
    response = client.post(
        IMPORT_PATH,
        data={
            "application_id": str(application_id),
            "url": OFFER_URL,
            "description": POSTING,
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    return response.text


def test_a_ready_application_is_offered_the_existing_regenerate(
    dashboard_db: sqlite3.Connection,
) -> None:
    """Its CV was adapted to the card. That is the case the banner is for."""

    application_id = _application(dashboard_db, status="ready", suffix="r1")

    with _client(dashboard_db) as client:
        page = _import(client, application_id)

    assert "Description importée" in page
    assert "Régénérer avec le texte importé" in page
    assert f'action="/application/{application_id}/regenerate"' in page


def test_the_banner_states_that_the_tailoring_will_use_the_imported_text(
    dashboard_db: sqlite3.Connection,
) -> None:
    application_id = _application(dashboard_db, status="ready", suffix="r2")

    with _client(dashboard_db) as client:
        page = _import(client, application_id)

    assert "adaptés au texte précédent" in page
    assert "à partir de l'annonce importée" in page
    # Task 34 archives rather than overwrites, and saying so is what makes the
    # button safe to press.
    assert "archivée, pas écrasée" in page


def test_a_queued_application_is_offered_the_ordinary_approve(
    dashboard_db: sqlite3.Connection,
) -> None:
    """Nothing has been generated yet, so there is nothing to regenerate. The
    Approve path already tailors against whatever description is stored."""

    application_id = _application(dashboard_db, status="queued", suffix="q1")

    with _client(dashboard_db) as client:
        page = _import(client, application_id)

    assert f'action="/application/{application_id}/approve"' in page
    assert "utilisera l'annonce importée" in page
    assert "Régénérer avec le texte importé" not in page


@pytest.mark.parametrize("status", ("applied", "skipped", "rejected"))
def test_no_regeneration_is_offered_from_a_state_that_cannot_regenerate(
    dashboard_db: sqlite3.Connection, status: str
) -> None:
    """Task 34's regenerate refuses anything but `ready`, and an applied CV has
    already been sent. Offering a button that would 409 is worse than not
    offering one."""

    application_id = _application(dashboard_db, status=status, suffix=status)

    with _client(dashboard_db) as client:
        page = _import(client, application_id)

    assert "Description importée" in page
    assert "Régénérer avec le texte importé" not in page
    assert f"Statut « {status} »" in page


def test_the_banner_is_absent_until_something_is_imported(
    dashboard_db: sqlite3.Connection,
) -> None:
    application_id = _application(dashboard_db, status="ready", suffix="none")

    with _client(dashboard_db) as client:
        page = client.get(f"/application/{application_id}").text

    assert "Description importée :" not in page


def test_the_regenerate_button_is_the_task_34_route_and_not_a_new_one(
    dashboard_db: sqlite3.Connection,
) -> None:
    """The button posts where the existing Régénérer posts. Asserted by
    comparing the two rather than by reading the template twice."""

    application_id = _application(dashboard_db, status="ready", suffix="same")

    with _client(dashboard_db) as client:
        before = client.get(f"/application/{application_id}").text
        after = _import(client, application_id)

    action = f'action="/application/{application_id}/regenerate"'

    assert action in before  # the standing button on a ready application
    assert after.count(action) == 2  # plus the one in the banner


def test_the_extension_route_also_raises_the_banner(
    dashboard_db: sqlite3.Connection,
) -> None:
    """The extension POSTs JSON from the offer page and never lands on the
    dashboard, so there is no redirect and no query parameter. If the banner
    rode only on that, the automatic route — the point of the whole task —
    would import 1900 characters and leave the detail page showing nothing."""

    application_id = _application(dashboard_db, status="ready", suffix="ext")

    with _client(dashboard_db) as client:
        posted = client.post(
            IMPORT_PATH,
            json={"url": OFFER_URL, "description": POSTING},
            headers={"Origin": "https://www.linkedin.com"},
        )
        assert posted.status_code == 200
        page = client.get(f"/application/{application_id}").text

    # "Description importée le" alone would prove nothing: the paste box says
    # it too. The warning and its button are what only the banner renders.
    assert "adaptés au texte précédent" in page
    assert "Régénérer avec le texte importé" in page
    assert page.count(f'action="/application/{application_id}/regenerate"') == 2


def test_the_banner_survives_a_later_plain_visit(
    dashboard_db: sqlite3.Connection,
) -> None:
    """Stale tailoring does not stop being stale because the page was
    reloaded. The query parameter is a confirmation, not the state."""

    application_id = _application(dashboard_db, status="ready", suffix="again")

    with _client(dashboard_db) as client:
        _import(client, application_id)
        page = client.get(f"/application/{application_id}").text

    assert "Régénérer avec le texte importé" in page
    # The transient confirmation is gone; the durable warning is not.
    assert "Description importée :" not in page


def test_regenerating_after_the_import_clears_the_banner(
    dashboard_db: sqlite3.Connection,
) -> None:
    """Nothing resets a flag: Task 34 runs `ready -> queued -> ready`, so the
    documents come to be dated after the import and the question answers
    itself. Simulated here by dating the transition, because a real
    regeneration would cost an API call.

    The banner goes away entirely rather than turning reassuring: once the
    documents read the imported text there is nothing to warn about, and the
    paste box below still records that the description was imported."""

    application_id = _application(dashboard_db, status="ready", suffix="done")

    with _client(dashboard_db) as client:
        _import(client, application_id)
        dashboard_db.execute(
            "UPDATE applications SET last_event_at = ? WHERE id = ?",
            ("2099-01-01T00:00:00+00:00", application_id),
        )
        dashboard_db.commit()
        page = client.get(f"/application/{application_id}").text

    assert "Régénérer avec le texte importé" not in page
    assert "adaptés au texte précédent" not in page
    # The paste box keeps the record; only the warning retires.
    assert "import-box" in page
    assert "Description importée le" in page


def test_an_application_with_no_import_never_shows_the_banner(
    dashboard_db: sqlite3.Connection,
) -> None:
    """The durable half must not fire on the ordinary case: most applications
    have a description that arrived from a source and was never imported."""

    application_id = _application(dashboard_db, status="ready", suffix="plain")

    with _client(dashboard_db) as client:
        page = client.get(f"/application/{application_id}").text

    assert "Description importée" not in page
    assert "Régénérer avec le texte importé" not in page


def test_importing_does_not_itself_regenerate_anything(
    dashboard_db: sqlite3.Connection,
) -> None:
    """The import stores text and re-scores. Generation costs an API call and
    about twenty seconds and stays behind a human click."""

    application_id = _application(dashboard_db, status="ready", suffix="noauto")

    with _client(dashboard_db) as client:
        _import(client, application_id)

    row = dashboard_db.execute(
        "SELECT status FROM applications WHERE id = ?", (application_id,)
    ).fetchone()
    events = dashboard_db.execute(
        "SELECT event FROM events WHERE application_id = ?", (application_id,)
    ).fetchall()

    assert row["status"] == "ready"
    assert [event["event"] for event in events] == []
