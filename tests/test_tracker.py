"""Task 36 item 5: the tracker page.

Read-only in the strict sense: nothing here writes, transitions or sends. It is
the one surface that answers "where does everything stand" without offering a
way to change it by accident.

Deliberately not a Google Sheets sync — that needs OAuth and a connector and is
its own task if it is ever wanted.
"""

from __future__ import annotations

import csv
import io
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from jobpilot.apply_flow import APPLICATION_LOCK
from jobpilot.dashboard import create_app, database_connection
from jobpilot.state import transition
from jobpilot.tracker import COLUMNS, counts, statuses, to_csv, tracker_rows
from tests.test_dashboard import _offer_application

NOW = datetime(2026, 7, 30, 12, 0, tzinfo=UTC)  # a Thursday


@contextmanager
def _client(db: sqlite3.Connection, tmp_path: Path) -> Iterator[TestClient]:
    app = create_app(output_root=tmp_path)

    def connection() -> Iterator[sqlite3.Connection]:
        with APPLICATION_LOCK:
            yield db

    app.dependency_overrides[database_connection] = connection
    with TestClient(app) as client:
        yield client


def _application(
    db: sqlite3.Connection,
    *,
    suffix: str,
    company: str = "Advens",
    status: str = "queued",
    score: float = 0.5,
    applied_at: str | None = None,
    apply_route: str | None = None,
) -> int:
    with APPLICATION_LOCK:
        application_id = _offer_application(
            db, title="Analyste SOC", score=score, suffix=suffix
        )
        db.execute(
            "UPDATE companies SET name = ? WHERE id = ("
            " SELECT company_id FROM offers WHERE id = ("
            "  SELECT offer_id FROM applications WHERE id = ?))",
            (company, application_id),
        )
        for step in {"ready": ("generating", "ready"),
                     "applied": ("generating", "ready", "applied"),
                     "generating": ("generating",),
                     "skipped": ("skipped",)}.get(status, ()):
            transition(db, application_id, step)
        if applied_at or apply_route:
            db.execute(
                "UPDATE applications SET applied_at = COALESCE(?, applied_at), "
                "apply_route = COALESCE(?, apply_route) WHERE id = ?",
                (applied_at, apply_route, application_id),
            )
        db.commit()
    return application_id


# ----- rows -----


def test_every_offer_application_is_listed_with_its_columns(
    db: sqlite3.Connection,
) -> None:
    _application(db, suffix="t1", company="Advens", status="ready",
                 apply_route="manual_open")

    (row,) = tracker_rows(db)

    assert row["company"] == "Advens"
    assert row["title"] == "Analyste SOC"
    assert row["source"] == "france_travail"
    assert row["status"] == "ready"
    assert row["apply_route"] == "manual_open"
    assert row["score"] == pytest.approx(0.5)


def test_filtering_by_status(db: sqlite3.Connection) -> None:
    _application(db, suffix="q", status="queued")
    _application(db, suffix="r", status="ready")

    assert len(tracker_rows(db)) == 2
    assert [r["status"] for r in tracker_rows(db, status="ready")] == ["ready"]
    assert tracker_rows(db, status="applied") == ()


def test_only_offered_statuses_are_filterable(db: sqlite3.Connection) -> None:
    _application(db, suffix="q", status="queued")
    _application(db, suffix="r", status="ready")

    assert statuses(db) == ["queued", "ready"]


@pytest.mark.parametrize("sort", ["recent", "company", "score", "status", "applied"])
def test_every_sort_is_accepted_and_returns_every_row(
    db: sqlite3.Connection, sort: str
) -> None:
    _application(db, suffix="a", company="Zeta", score=0.2)
    _application(db, suffix="b", company="Alpha", score=0.9)

    assert len(tracker_rows(db, sort=sort)) == 2


def test_sorting_by_company_is_alphabetical(db: sqlite3.Connection) -> None:
    _application(db, suffix="z", company="Zeta")
    _application(db, suffix="a", company="Alpha")

    assert [r["company"] for r in tracker_rows(db, sort="company")] == ["Alpha", "Zeta"]


def test_an_unknown_sort_falls_back_rather_than_erroring(
    db: sqlite3.Connection,
) -> None:
    _application(db, suffix="x")

    assert len(tracker_rows(db, sort="'; DROP TABLE applications; --")) == 1


def test_cold_applications_are_not_in_the_offer_tracker(
    db: sqlite3.Connection,
) -> None:
    company_id = db.execute("INSERT INTO companies (name) VALUES ('Acme')").lastrowid
    db.execute(
        "INSERT INTO applications (company_id, kind, status) VALUES (?, 'cold', 'queued')",
        (company_id,),
    )
    db.commit()

    assert tracker_rows(db) == ()


# ----- counts -----


def test_the_counts_answer_the_four_questions(db: sqlite3.Connection) -> None:
    _application(db, suffix="s1", status="applied", applied_at="2026-07-28T09:00:00+00:00")
    _application(db, suffix="s2", status="applied", applied_at="2026-06-01T09:00:00+00:00")
    _application(db, suffix="r1", status="ready")
    _application(db, suffix="q1", status="queued")
    _application(db, suffix="q2", status="queued")

    tally = counts(db, now=NOW)

    assert tally.sent_this_week == 1  # only the 28th falls in the week of the 30th
    assert tally.sent_total == 2
    assert tally.ready == 1
    assert tally.queued == 2


def test_the_week_boundary_is_monday(db: sqlite3.Connection) -> None:
    # Monday of NOW's week is 2026-07-27.
    _application(db, suffix="mon", status="applied",
                 applied_at="2026-07-27T00:00:00+00:00")
    _application(db, suffix="sun", status="applied",
                 applied_at="2026-07-26T23:59:59+00:00")

    assert counts(db, now=NOW).sent_this_week == 1


def test_counts_are_zero_on_an_empty_database(db: sqlite3.Connection) -> None:
    assert counts(db, now=NOW).as_dict() == {
        "sent_this_week": 0, "sent_total": 0, "ready": 0, "queued": 0,
    }


# ----- CSV -----


def test_the_csv_exports_the_visible_rows_in_the_visible_order(
    db: sqlite3.Connection,
) -> None:
    _application(db, suffix="c1", company="Advens", status="ready",
                 apply_route="manual_open")

    body = to_csv(tracker_rows(db))
    parsed = list(csv.reader(io.StringIO(body)))

    # Indexed off COLUMNS rather than hard-coded: Task 41 inserted « Publiée »
    # into the middle of the table, and a literal position would have made this
    # a test of the column order rather than of the export.
    keys = [key for key, _ in COLUMNS]
    assert parsed[0] == [label for _, label in COLUMNS]
    assert parsed[1][keys.index("company")] == "Advens"
    assert parsed[1][keys.index("status")] == "ready"
    assert len(parsed) == 2


def test_the_csv_honours_the_filter(db: sqlite3.Connection) -> None:
    _application(db, suffix="k1", status="queued")
    _application(db, suffix="k2", status="ready")

    body = to_csv(tracker_rows(db, status="ready"))

    assert len(list(csv.reader(io.StringIO(body)))) == 2  # header + one row


def test_the_csv_writes_empty_cells_rather_than_the_word_none(
    db: sqlite3.Connection,
) -> None:
    _application(db, suffix="n1", status="queued")

    body = to_csv(tracker_rows(db))

    assert "None" not in body
    assert ",," in body or body.rstrip().endswith(",")


# ----- the page -----


def test_the_page_shows_the_table_and_the_counts(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    _application(dashboard_db, suffix="p1", company="Advens", status="ready")

    with _client(dashboard_db, tmp_path) as client:
        page = client.get("/tracker")

    assert page.status_code == 200
    assert "Advens" in page.text
    assert "Envoyées cette semaine" in page.text
    for _, label in COLUMNS:
        assert label in page.text


def test_the_page_is_reachable_from_the_navigation(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    with _client(dashboard_db, tmp_path) as client:
        assert 'href="/tracker"' in client.get("/").text


def test_marking_sent_is_reflected_immediately(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    """After the POST the tracker shows the new state with no manual refresh."""

    application_id = _application(dashboard_db, suffix="sent", status="ready")

    with _client(dashboard_db, tmp_path) as client:
        before = client.get("/tracker")
        assert "applied" not in before.text.split("<tbody>")[1]

        client.post(f"/application/{application_id}/mark-sent")
        after = client.get("/tracker")

    body = after.text.split("<tbody>")[1]
    assert "applied" in body
    assert "Envoyées au total <strong>1</strong>" in after.text


def test_the_csv_endpoint_downloads(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    _application(dashboard_db, suffix="dl", company="Advens", status="ready")

    with _client(dashboard_db, tmp_path) as client:
        response = client.get("/tracker.csv")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment" in response.headers["content-disposition"]
    assert "jobpilot_tracker.csv" in response.headers["content-disposition"]
    assert "Advens" in response.text


def test_the_page_is_read_only(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    """No form, no button that changes anything: this surface only reports."""

    _application(dashboard_db, suffix="ro", status="ready")

    with _client(dashboard_db, tmp_path) as client:
        page = client.get("/tracker")

    assert 'method="post"' not in page.text
    assert "<form" in page.text  # the GET filter form is fine
    assert page.text.count('method="get"') >= 1


def test_the_empty_state_says_what_to_do_next(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    with _client(dashboard_db, tmp_path) as client:
        assert "Approuvez une offre" in client.get("/tracker").text
