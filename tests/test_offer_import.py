"""Task 43 item 1: an offer description captured from an open page.

LinkedIn and Indeed arrive as alert emails carrying ~113 characters of
description. All five applications sent so far come from that source, so every
CV that has reached an employer was tailored against a card rather than a
posting. The text exists — it is on the page the user opened.

Nothing here fetches anything. The endpoint receives text a human was already
reading; that is the line between this and scraping (CLAUDE.md, "Scope of rule
11") and `test_the_import_path_never_fetches_anything` holds it.
"""

from __future__ import annotations

import hashlib
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient

from jobpilot.dashboard import (
    IMPORT_PATH,
    create_app,
    database_connection,
    import_origin_allowed,
)
from jobpilot.offer_import import (
    MIN_IMPORTED_DESCRIPTION_CHARS,
    OfferImportError,
    clean_description,
    find_offer_by_url,
    import_offer_description,
    normalize_offer_url,
)

#: Long enough to pass the minimum, and recognisably a posting.
POSTING = (
    "Nous recherchons un alternant en cybersécurité pour rejoindre notre SOC. "
    "Vous participerez à la détection et à la réponse aux incidents, à "
    "l'écriture de règles Sigma et à l'exploitation d'un SIEM ELK. "
    "Environnement technique : Wazuh, Splunk, Azure Sentinel, Python, Bash. "
    "Formation Bac+5 en cours, rythme 1 semaine école / 1 semaine entreprise. "
    "Poste basé à Lille avec deux jours de télétravail par semaine."
)

#: What an alert email gives us instead. This is the problem, to scale.
ALERT_CARD = "Alternance Cybersécurité — Acme, Lille. Postuler maintenant."


def _offer(
    db: sqlite3.Connection,
    *,
    url: str,
    suffix: str = "a",
    description: str = ALERT_CARD,
    source: str = "linkedin_alert",
    application_status: str | None = None,
) -> int:
    source_id = db.execute(
        "SELECT id FROM sources WHERE name = ?", (source,)
    ).fetchone()["id"]
    company_id = db.execute(
        "INSERT INTO companies (name) VALUES (?)", (f"Acme {suffix}",)
    ).lastrowid
    offer_id = int(
        db.execute(
            "INSERT INTO offers (source_id, company_id, external_id, url, title, "
            "description, contract_type, city, content_hash) "
            "VALUES (?, ?, ?, ?, 'Alternance Cybersécurité', ?, 'alternance', "
            "'Lille', ?)",
            (
                source_id,
                company_id,
                f"ext-{suffix}",
                url,
                description,
                hashlib.sha256(suffix.encode()).hexdigest(),
            ),
        ).lastrowid
    )
    if application_status is not None:
        db.execute(
            "INSERT INTO applications (offer_id, company_id, kind, status) "
            "VALUES (?, ?, 'offer', ?)",
            (offer_id, company_id, application_status),
        )
    db.commit()
    return offer_id


def _scored(db: sqlite3.Connection, offer_id: int, final: float = 0.2) -> None:
    db.execute(
        "INSERT INTO match_scores (offer_id, hard_filter_pass, semantic_score, "
        "keyword_score, bonus_score, final_score) VALUES (?, 1, 0.1, 0.1, 0.1, ?)",
        (offer_id, final),
    )
    db.commit()


def _fake_score(recorded: list[int] | None = None):
    """Stand-in for jobpilot.scoring.score, which imports torch.

    Writes a match_scores row for every unscored offer, exactly as
    matcher.score_new_offers does, so the callers under test see the same shape
    of result without a 20-second model load.
    """

    def score(db: sqlite3.Connection, *args, **kwargs) -> int:
        rows = db.execute(
            "SELECT o.id FROM offers o LEFT JOIN match_scores m ON m.offer_id = o.id "
            "WHERE m.offer_id IS NULL"
        ).fetchall()
        for row in rows:
            if recorded is not None:
                recorded.append(int(row["id"]))
            db.execute(
                "INSERT INTO match_scores (offer_id, hard_filter_pass, "
                "semantic_score, keyword_score, bonus_score, final_score) "
                "VALUES (?, 1, 0.7, 0.5, 0.2, 0.61)",
                (int(row["id"]),),
            )
        db.commit()
        return len(rows)

    return score


# ---------------------------------------------------------------------------
# URL normalisation
# ---------------------------------------------------------------------------


def test_an_alert_link_and_the_same_page_in_a_browser_are_one_offer() -> None:
    """The case the whole feature turns on. These are the same posting."""

    from_email = (
        "https://www.linkedin.com/comm/jobs/view/4434968054"
        "?trackingId=xY%2Fabc&refId=def&midToken=ghi"
    )
    from_browser = (
        "https://linkedin.com/jobs/view/4434968054/"
        "?alternateChannel=search&refId=zzz&trk=flagship"
    )

    assert normalize_offer_url(from_email) == normalize_offer_url(from_browser)


def test_an_indeed_job_key_survives_normalisation() -> None:
    """The reason the rule is a denylist and not "drop the query string".

    Indeed puts the job key in the query. Dropping the query wholesale would
    collapse every Indeed posting onto https://indeed.fr/viewjob and merge
    unrelated jobs into one offer — which would tailor a CV against the wrong
    posting and send it.
    """

    one = normalize_offer_url("https://fr.indeed.com/viewjob?jk=1a2b3c&from=serp&tk=xyz")
    two = normalize_offer_url("https://fr.indeed.com/viewjob?jk=9z8y7x&from=serp&tk=xyz")

    assert "jk=1a2b3c" in one
    assert one != two


@pytest.mark.parametrize(
    ("left", "right"),
    (
        ("https://WWW.Linkedin.COM/jobs/view/1", "https://linkedin.com/jobs/view/1"),
        ("https://x.test/a?b=1&c=2", "https://x.test/a?c=2&b=1"),
        ("https://x.test/a/", "https://x.test/a"),
        ("https://x.test/a#section", "https://x.test/a"),
        ("https://x.test:443/a", "https://x.test/a"),
        ("https://x.test/a?utm_source=mail&utm_campaign=x", "https://x.test/a"),
    ),
)
def test_cosmetic_differences_do_not_make_two_offers(left: str, right: str) -> None:
    assert normalize_offer_url(left) == normalize_offer_url(right)


def test_two_genuinely_different_postings_stay_different() -> None:
    assert normalize_offer_url("https://x.test/jobs/1") != normalize_offer_url(
        "https://x.test/jobs/2"
    )


def test_an_unparseable_url_does_not_raise() -> None:
    """Matching just fails and the offer is created, which is recoverable."""

    assert normalize_offer_url("not a url at all") == "not a url at all"
    assert normalize_offer_url("") == ""


def test_the_path_keeps_its_case_because_job_ids_live_there() -> None:
    assert "AbC123" in normalize_offer_url("https://x.test/jobs/AbC123")


# ---------------------------------------------------------------------------
# Storing
# ---------------------------------------------------------------------------


def test_an_imported_description_replaces_the_alert_card(
    db: sqlite3.Connection,
) -> None:
    offer_id = _offer(db, url="https://www.linkedin.com/comm/jobs/view/99?refId=a")

    result = import_offer_description(
        db,
        url="https://linkedin.com/jobs/view/99/?trk=x",
        description=POSTING,
        score_pass=_fake_score(),
    )

    row = db.execute("SELECT * FROM offers WHERE id = ?", (offer_id,)).fetchone()

    assert result.offer_id == offer_id
    assert result.created is False
    assert row["description"] == clean_description(POSTING)
    assert row["imported_at"] is not None
    assert result.replaced_chars == len(ALERT_CARD)


def test_a_short_payload_is_refused_rather_than_overwriting_good_text(
    db: sqlite3.Connection,
) -> None:
    """A cookie banner must not be able to destroy a real description."""

    offer_id = _offer(db, url="https://x.test/j/1", description=POSTING)

    with pytest.raises(OfferImportError, match="trop courte"):
        import_offer_description(
            db, url="https://x.test/j/1", description="Accepter les cookies",
            score_pass=_fake_score(),
        )

    row = db.execute("SELECT description FROM offers WHERE id = ?", (offer_id,)).fetchone()

    assert row["description"] == POSTING


def test_the_minimum_is_above_the_alert_card_average() -> None:
    """113 characters is the measured alert average; accepting that length would
    let an import store the same card the alert already gave us."""

    assert MIN_IMPORTED_DESCRIPTION_CHARS > 113


def test_an_unknown_url_creates_an_offer_that_enters_the_pipeline(
    db: sqlite3.Connection,
) -> None:
    result = import_offer_description(
        db,
        url="https://www.welcometothejungle.com/fr/companies/acme/jobs/soc",
        description=POSTING,
        title="Analyste SOC",
        company="Acme SA",
        score_pass=_fake_score(),
    )

    row = db.execute("SELECT * FROM offers WHERE id = ?", (result.offer_id,)).fetchone()
    source = db.execute(
        "SELECT name FROM sources WHERE id = ?", (row["source_id"],)
    ).fetchone()["name"]
    company = db.execute(
        "SELECT name FROM companies WHERE id = ?", (row["company_id"],)
    ).fetchone()["name"]

    assert result.created is True
    assert row["title"] == "Analyste SOC"
    assert company == "Acme SA"
    # Filed under manual_import, not under a source it never came from.
    assert source == "manual_import"
    # Scored like any other offer, by the same pass.
    assert result.rescored is True
    assert result.score == 0.61


def test_a_created_offer_gets_no_application_of_its_own(
    db: sqlite3.Connection,
) -> None:
    """matcher.score_new_offers owns the only path that queues an offer.

    Creating one here would put a row in `applications` outside both that path
    and state.transition.
    """

    result = import_offer_description(
        db, url="https://x.test/j/new", description=POSTING,
        score_pass=lambda conn, *a, **k: 0,
    )

    assert result.application_id is None
    assert db.execute("SELECT count(*) AS n FROM applications").fetchone()["n"] == 0


def test_the_page_title_never_overwrites_one_the_source_parsed(
    db: sqlite3.Connection,
) -> None:
    """Page headings are frequently "Postuler | Acme" or a cookie prompt."""

    offer_id = _offer(db, url="https://x.test/j/7")

    import_offer_description(
        db, url="https://x.test/j/7", description=POSTING,
        title="Postuler | Acme", score_pass=_fake_score(),
    )

    row = db.execute("SELECT title FROM offers WHERE id = ?", (offer_id,)).fetchone()

    assert row["title"] == "Alternance Cybersécurité"


def test_whitespace_from_a_copied_page_is_collapsed() -> None:
    assert clean_description("a\r\n\n\n\n   b   \n\n") == "a\n\nb"


# ---------------------------------------------------------------------------
# Re-scoring
# ---------------------------------------------------------------------------


def test_the_stale_score_is_dropped_and_recomputed_by_the_existing_pass(
    db: sqlite3.Connection,
) -> None:
    """Scoring is not reimplemented here: the row is deleted and the normal
    pass — which selects offers with no match_scores row — picks it up."""

    offer_id = _offer(db, url="https://x.test/j/3")
    _scored(db, offer_id, final=0.02)
    rescored: list[int] = []

    result = import_offer_description(
        db, url="https://x.test/j/3", description=POSTING,
        score_pass=_fake_score(rescored),
    )

    assert rescored == [offer_id]
    assert result.score == 0.61


def test_an_offer_that_already_has_an_application_is_still_rescored(
    db: sqlite3.Connection,
) -> None:
    """descriptions.clear_match_scores deliberately skips these — that rail
    protects a bulk pass from rewriting under a human decision. Here the human
    is the one asking, on one offer they named."""

    offer_id = _offer(db, url="https://x.test/j/4", application_status="ready")
    _scored(db, offer_id, final=0.02)
    rescored: list[int] = []

    result = import_offer_description(
        db, url="https://x.test/j/4", description=POSTING,
        score_pass=_fake_score(rescored),
    )

    assert rescored == [offer_id]
    assert result.application_status == "ready"


def test_rescoring_never_disturbs_an_existing_application_status(
    db: sqlite3.Connection,
) -> None:
    """applications.offer_id is UNIQUE and matcher uses INSERT OR IGNORE, so a
    re-score cannot revert a ready application to queued. Asserted rather than
    assumed, because it is the thing that would silently lose generated work."""

    offer_id = _offer(db, url="https://x.test/j/5", application_status="ready")
    _scored(db, offer_id)

    import_offer_description(
        db, url="https://x.test/j/5", description=POSTING, score_pass=_fake_score()
    )

    rows = db.execute("SELECT status FROM applications WHERE offer_id = ?", (offer_id,)).fetchall()

    assert [row["status"] for row in rows] == ["ready"]


def test_a_failed_rescore_keeps_the_text_and_says_it_did_not_score(
    db: sqlite3.Connection,
) -> None:
    """The description is committed before scoring, so a missing embedding model
    costs the offer its new score and nothing else. The next `jobpilot score`
    picks it up, because the match_scores row is already gone."""

    offer_id = _offer(db, url="https://x.test/j/6")
    _scored(db, offer_id)

    def explode(conn: sqlite3.Connection, *args, **kwargs) -> int:
        raise RuntimeError("no torch here")

    result = import_offer_description(
        db, url="https://x.test/j/6", description=POSTING, score_pass=explode
    )

    row = db.execute("SELECT description FROM offers WHERE id = ?", (offer_id,)).fetchone()
    scores = db.execute(
        "SELECT count(*) AS n FROM match_scores WHERE offer_id = ?", (offer_id,)
    ).fetchone()["n"]

    assert result.rescored is False
    assert result.score is None
    assert row["description"] == clean_description(POSTING)
    assert scores == 0


# ---------------------------------------------------------------------------
# The endpoint
# ---------------------------------------------------------------------------


@contextmanager
def _client(conn: sqlite3.Connection) -> Iterator[TestClient]:
    app = create_app(score_pass=_fake_score())
    app.dependency_overrides[database_connection] = lambda: conn
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_the_endpoint_stores_and_reports(dashboard_db: sqlite3.Connection) -> None:
    offer_id = _offer(dashboard_db, url="https://x.test/j/api")

    with _client(dashboard_db) as client:
        response = client.post(
            IMPORT_PATH,
            json={"url": "https://x.test/j/api", "description": POSTING},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["offer_id"] == offer_id
    assert body["created"] is False
    assert body["imported_chars"] == len(clean_description(POSTING))


def test_the_endpoint_refuses_a_short_description(
    dashboard_db: sqlite3.Connection,
) -> None:
    with _client(dashboard_db) as client:
        response = client.post(
            IMPORT_PATH, json={"url": "https://x.test/j/short", "description": "non"}
        )

    assert response.status_code == 422
    assert "trop courte" in response.json()["detail"]


@pytest.mark.parametrize(
    "origin",
    (
        "https://www.linkedin.com",
        "https://fr.indeed.com",
        "https://www.welcometothejungle.com",
        "http://127.0.0.1:8787",
        "http://localhost:8787",
        "chrome-extension://abcdefghijklmnop",
    ),
)
def test_the_origins_the_feature_needs_are_allowed(origin: str) -> None:
    assert import_origin_allowed(origin) is True


@pytest.mark.parametrize(
    "origin",
    (
        "https://evil.test",
        # Suffix matching is anchored on a dot, so this is not a subdomain of
        # anything allowed.
        "https://linkedin.com.evil.test",
        "file://",
        "null",
        "",
    ),
)
def test_every_other_origin_is_rejected(origin: str) -> None:
    assert import_origin_allowed(origin) is False


def test_a_foreign_origin_is_refused_by_the_endpoint(
    dashboard_db: sqlite3.Connection,
) -> None:
    with _client(dashboard_db) as client:
        response = client.post(
            IMPORT_PATH,
            json={"url": "https://x.test/j/evil", "description": POSTING},
            headers={"Origin": "https://evil.test"},
        )

    stored = dashboard_db.execute("SELECT count(*) AS n FROM offers").fetchone()["n"]

    assert response.status_code == 403
    assert stored == 0


def test_cors_headers_are_returned_for_an_allowed_origin(
    dashboard_db: sqlite3.Connection,
) -> None:
    with _client(dashboard_db) as client:
        preflight = client.options(
            IMPORT_PATH,
            headers={
                "Origin": "https://www.linkedin.com",
                "Access-Control-Request-Method": "POST",
            },
        )

    assert preflight.status_code == 204
    assert preflight.headers["access-control-allow-origin"] == "https://www.linkedin.com"
    assert "POST" in preflight.headers["access-control-allow-methods"]


def test_cors_is_enabled_for_this_endpoint_and_no_other(
    dashboard_db: sqlite3.Connection,
) -> None:
    """The dashboard must not acquire CORS. A page on the internet must not be
    able to read the queue by asking a browser nicely."""

    with _client(dashboard_db) as client:
        queue = client.get("/", headers={"Origin": "https://www.linkedin.com"})
        tracker = client.get("/tracker", headers={"Origin": "https://www.linkedin.com"})

    assert "access-control-allow-origin" not in queue.headers
    assert "access-control-allow-origin" not in tracker.headers


# ---------------------------------------------------------------------------
# The line between this and scraping
# ---------------------------------------------------------------------------


def test_the_import_path_never_fetches_anything(db: sqlite3.Connection) -> None:
    """Constitution rule 11. The text arrives in the request; nothing goes out.

    Enforced by breaking the socket layer for the duration, so a hidden HTTP
    call anywhere under import_offer_description fails the test rather than
    quietly working.
    """

    import socket

    import jobpilot.offer_import as module

    def refuse(*args, **kwargs):  # pragma: no cover - the point is it never runs
        raise AssertionError("the import path must not open a network connection")

    original_socket, original_conn = socket.socket, socket.create_connection
    socket.socket, socket.create_connection = refuse, refuse
    try:
        result = module.import_offer_description(
            db, url="https://x.test/j/net", description=POSTING,
            score_pass=_fake_score(),
        )
    finally:
        socket.socket, socket.create_connection = original_socket, original_conn

    assert result.offer_id > 0


def test_find_offer_by_url_reads_and_writes_nothing(db: sqlite3.Connection) -> None:
    _offer(db, url="https://x.test/j/ro")
    before = db.execute("SELECT count(*) AS n FROM offers").fetchone()["n"]

    assert find_offer_by_url(db, "https://x.test/j/ro?utm_source=x") is not None
    assert find_offer_by_url(db, "https://x.test/j/absent") is None
    assert db.execute("SELECT count(*) AS n FROM offers").fetchone()["n"] == before
