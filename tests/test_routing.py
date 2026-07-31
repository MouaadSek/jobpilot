"""Task 34.B: unified apply — route resolution, the plan hash, and the gates.

The point of resolving before acting is that a route is never selected and then
found to be impossible at click time, so every route is tested twice: once for
the offer that should select it, and once for the same offer with its
availability requirement removed.
"""

from __future__ import annotations

import dataclasses
import hashlib
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from jobpilot.apply_flow import APPLICATION_LOCK
from jobpilot.config import get_settings
from jobpilot.dashboard import create_app, database_connection
from jobpilot.routing import (
    ROUTE_PRECEDENCE,
    Route,
    RouteError,
    resolve_route,
)
from jobpilot.state import current_status, log_event, transition
from tests.test_dashboard import _offer_application
from tests.test_tailoring import _Advisor, _Toolchain

ARTIFACTS = ("cv.pdf", "motivation_letter.pdf")


def _settings(**overrides: object) -> object:
    """Settings with every apply route's requirement satisfied, then overridden."""

    base = dataclasses.replace(
        get_settings(),
        wttj_api_key="wttj-test-key",
        applicant_full_name="Mouaad Sekkouri",
        applicant_email="mouaad@example.test",
        applicant_phone="+33600000000",
        applicant_linkedin_url="https://linkedin.example/in/mouaad",
        smtp_username="mouaad@sender.example",
        smtp_password="smtp-test-secret",
    )
    return dataclasses.replace(base, **overrides)  # type: ignore[arg-type]


def _ready_offer(
    db: sqlite3.Connection,
    tmp_path: Path,
    *,
    suffix: str,
    source_name: str = "france_travail",
    url: str = "https://example.test/jobs/plain",
    contact_email: str | None = None,
    artifacts: tuple[str, ...] = ARTIFACTS,
) -> int:
    """A ready offer application with real files on disk, without generating."""

    with APPLICATION_LOCK:
        application_id = _offer_application(
            db, title="Analyste SOC", score=0.9, suffix=suffix
        )
        source_id = db.execute(
            "SELECT id FROM sources WHERE name = ?", (source_name,)
        ).fetchone()["id"]
        db.execute(
            "UPDATE offers SET source_id = ?, url = ?, contact_email = ? "
            "WHERE id = (SELECT offer_id FROM applications WHERE id = ?)",
            (source_id, url, contact_email, application_id),
        )
        transition(db, application_id, "generating")
        transition(db, application_id, "ready")

    application_dir = tmp_path / str(application_id)
    application_dir.mkdir(parents=True, exist_ok=True)
    for name in artifacts:
        (application_dir / name).write_bytes(b"%PDF-fixture")
    (application_dir / "letter_body.html").write_text(
        "<p>Madame, Monsieur,</p><p>Je souhaite rejoindre votre équipe.</p>",
        encoding="utf-8",
    )
    return application_id


def _route(
    db: sqlite3.Connection, application_id: int, tmp_path: Path, **overrides: object
) -> Route:
    return resolve_route(
        db,
        application_id,
        settings=_settings(**overrides),
        output_root=tmp_path,
    )


# ----- precedence and isolation -----


def test_the_precedence_is_the_one_the_spec_fixes() -> None:
    assert ROUTE_PRECEDENCE == (
        "wttj_inline",
        "ats_prefill",
        "learned_form",
        "email",
        "manual_open",
    )


def test_wttj_offer_selects_the_inline_route(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    application_id = _ready_offer(
        dashboard_db,
        tmp_path,
        suffix="route-wttj",
        source_name="wttj",
        url="https://www.welcometothejungle.com/fr/companies/acme/jobs/soc",
    )

    route = _route(dashboard_db, application_id, tmp_path)

    assert route.id == "wttj_inline"
    assert "WTTJ" in route.sentence
    assert "Ne soumet pas." in route.sentence


def test_wttj_route_is_unavailable_without_the_api_key(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    application_id = _ready_offer(
        dashboard_db,
        tmp_path,
        suffix="route-wttj-nokey",
        source_name="wttj",
        url="https://www.welcometothejungle.com/fr/companies/acme/jobs/soc",
    )

    route = _route(dashboard_db, application_id, tmp_path, wttj_api_key=None)

    assert route.id == "manual_open"
    assert [item.id for item in route.unavailable] == ["wttj_inline"]
    assert route.unavailable[0].reason == "WTTJ_API_KEY manquante"


def test_ats_offer_selects_the_prefill_route(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    application_id = _ready_offer(
        dashboard_db,
        tmp_path,
        suffix="route-ats",
        source_name="ats",
        url="https://jobs.lever.co/acme/security",
    )

    route = _route(dashboard_db, application_id, tmp_path)

    assert route.id == "ats_prefill"
    assert route.target == "https://jobs.lever.co/acme/security"


def test_ats_route_is_unavailable_without_applicant_details(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    """The prefill module raises on missing APPLICANT_*; that is a click-time
    failure, so it has to be an availability requirement here."""

    application_id = _ready_offer(
        dashboard_db,
        tmp_path,
        suffix="route-ats-noapplicant",
        source_name="ats",
        url="https://jobs.lever.co/acme/security",
    )

    route = _route(dashboard_db, application_id, tmp_path, applicant_phone=None)

    assert route.id == "manual_open"
    assert [item.id for item in route.unavailable] == ["ats_prefill"]
    assert "APPLICANT_PHONE" in route.unavailable[0].reason


def test_an_ats_url_from_another_source_is_not_prefilled(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    """The prefill module refuses anything whose source is not 'ats'."""

    application_id = _ready_offer(
        dashboard_db,
        tmp_path,
        suffix="route-lever-ft",
        source_name="france_travail",
        url="https://jobs.lever.co/acme/security",
    )

    assert _route(dashboard_db, application_id, tmp_path).id == "manual_open"


def test_offer_with_a_contact_email_selects_the_email_route(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    application_id = _ready_offer(
        dashboard_db,
        tmp_path,
        suffix="route-email",
        contact_email="recrutement@exemple.fr",
    )

    route = _route(dashboard_db, application_id, tmp_path)

    assert route.id == "email"
    assert route.sentence == (
        "Envoie un email à recrutement@exemple.fr avec 2 pièces jointes."
    )


def test_email_route_is_unavailable_without_smtp(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    application_id = _ready_offer(
        dashboard_db,
        tmp_path,
        suffix="route-email-nosmtp",
        contact_email="recrutement@exemple.fr",
    )

    route = _route(dashboard_db, application_id, tmp_path, smtp_password=None)

    assert route.id == "manual_open"
    assert [item.id for item in route.unavailable] == ["email"]
    assert route.unavailable[0].reason == "SMTP non configuré"


def test_learned_form_is_not_selected_before_a_mapping_exists(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    """Phase D adds the table. Until then no domain has a mapping."""

    application_id = _ready_offer(
        dashboard_db, tmp_path, suffix="route-learned", url="https://carrieres.acme.fr/1"
    )

    route = _route(dashboard_db, application_id, tmp_path)

    assert route.id == "manual_open"
    assert [item.id for item in route.unavailable] == []


def test_manual_open_is_the_common_case_and_not_a_failure(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    """La Bonne Alternance has no contact_email by construction and SMTP is
    not configured, so this is what today's data actually resolves to."""

    application_id = _ready_offer(
        dashboard_db,
        tmp_path,
        suffix="route-manual",
        url="https://labonnealternance.example/offre/1",
    )

    route = _route(dashboard_db, application_id, tmp_path, smtp_username=None)

    assert route.id == "manual_open"
    assert route.sentence == "Ouvre l'offre dans le navigateur et copie la lettre."
    assert route.unavailable == ()


def test_an_offer_eligible_for_two_routes_gets_the_higher_one(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    """A WTTJ offer that also carries a contact email is applied to inline."""

    application_id = _ready_offer(
        dashboard_db,
        tmp_path,
        suffix="route-both",
        source_name="wttj",
        url="https://www.welcometothejungle.com/fr/companies/acme/jobs/soc",
        contact_email="recrutement@exemple.fr",
    )

    assert _route(dashboard_db, application_id, tmp_path).id == "wttj_inline"


def test_an_ats_offer_with_a_contact_email_prefers_prefill(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    application_id = _ready_offer(
        dashboard_db,
        tmp_path,
        suffix="route-ats-and-email",
        source_name="ats",
        url="https://jobs.lever.co/acme/security",
        contact_email="recrutement@exemple.fr",
    )

    assert _route(dashboard_db, application_id, tmp_path).id == "ats_prefill"


def test_an_unconfirmed_wttj_submission_is_never_routed_back_to_wttj(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    application_id = _ready_offer(
        dashboard_db,
        tmp_path,
        suffix="route-wttj-unconfirmed",
        source_name="wttj",
        url="https://www.welcometothejungle.com/fr/companies/acme/jobs/soc",
    )
    log_event(dashboard_db, application_id, "submit_unconfirmed", {})

    assert _route(dashboard_db, application_id, tmp_path).id == "manual_open"


# ----- what may not be routed at all -----


def test_a_cold_application_cannot_be_routed(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    """COLD_SEND_ENABLED and the daily cap live on the outreach path; no cold
    application may be reachable from the offer apply button."""

    with APPLICATION_LOCK:
        company_id = dashboard_db.execute(
            "INSERT INTO companies (name) VALUES ('Acme Cyber')"
        ).lastrowid
        application_id = dashboard_db.execute(
            "INSERT INTO applications (company_id, kind, status) "
            "VALUES (?, 'cold', 'ready')",
            (company_id,),
        ).lastrowid
        dashboard_db.commit()

    with pytest.raises(RouteError, match="only offer applications"):
        resolve_route(dashboard_db, int(application_id), output_root=tmp_path)


@pytest.mark.parametrize("status", ["queued", "generating", "applied", "skipped"])
def test_only_a_ready_application_can_be_routed(
    dashboard_db: sqlite3.Connection, tmp_path: Path, status: str
) -> None:
    with APPLICATION_LOCK:
        application_id = _offer_application(
            dashboard_db, title="Pas prête", score=0.5, status=status, suffix=status
        )

    with pytest.raises(RouteError, match="ready"):
        resolve_route(dashboard_db, application_id, output_root=tmp_path)


def test_an_unknown_application_cannot_be_routed(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    with pytest.raises(RouteError, match="no application"):
        resolve_route(dashboard_db, 4242, output_root=tmp_path)


# ----- purity -----


class _WriteCounting:
    """Wraps a connection and refuses anything that is not a read."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self.statements: list[str] = []

    def execute(self, sql: str, *args: object) -> sqlite3.Cursor:
        self.statements.append(sql)
        verb = sql.strip().split(maxsplit=1)[0].upper()
        if verb != "SELECT":
            raise AssertionError(f"resolve_route must not write: {sql!r}")
        return self._connection.execute(sql, *args)

    def __getattr__(self, name: str) -> object:
        return getattr(self._connection, name)


def test_resolve_route_writes_nothing(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    application_id = _ready_offer(
        dashboard_db,
        tmp_path,
        suffix="route-pure",
        source_name="ats",
        url="https://jobs.lever.co/acme/security",
    )
    before = dashboard_db.total_changes
    guarded = _WriteCounting(dashboard_db)

    route = resolve_route(
        guarded,  # type: ignore[arg-type]
        application_id,
        settings=_settings(),
        output_root=tmp_path,
    )

    assert route.id == "ats_prefill"
    assert guarded.statements  # it really did go to the database
    assert dashboard_db.total_changes == before


# ----- the plan hash -----


def test_the_plan_hash_is_stateless_and_reproducible(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    application_id = _ready_offer(dashboard_db, tmp_path, suffix="hash-stable")

    first = _route(dashboard_db, application_id, tmp_path)
    second = _route(dashboard_db, application_id, tmp_path)

    assert first.plan_hash == second.plan_hash
    assert len(first.plan_hash) == 16
    assert set(first.plan_hash) <= set(hashlib.sha256(b"").hexdigest())


def test_the_plan_hash_changes_when_the_route_inputs_change(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    application_id = _ready_offer(dashboard_db, tmp_path, suffix="hash-change")
    before = _route(dashboard_db, application_id, tmp_path).plan_hash

    # A contact added between the two clicks is exactly the case that must not
    # sail through: the route itself changes underneath the human.
    dashboard_db.execute(
        "UPDATE offers SET contact_email = 'recrutement@exemple.fr' "
        "WHERE id = (SELECT offer_id FROM applications WHERE id = ?)",
        (application_id,),
    )
    dashboard_db.commit()
    after = _route(dashboard_db, application_id, tmp_path)

    assert after.id == "email"
    assert after.plan_hash != before


def test_the_plan_hash_changes_when_the_artefacts_change(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    application_id = _ready_offer(
        dashboard_db,
        tmp_path,
        suffix="hash-artifacts",
        contact_email="recrutement@exemple.fr",
    )
    before = _route(dashboard_db, application_id, tmp_path).plan_hash

    (tmp_path / str(application_id) / "motivation_letter.pdf").unlink()
    after = _route(dashboard_db, application_id, tmp_path)

    assert after.plan_hash != before
    assert "1 pièce jointe" in after.sentence


# ----- the endpoints -----


@contextmanager
def _client(
    db: sqlite3.Connection,
    output_root: Path,
    *,
    opener: object | None = None,
    copier: object | None = None,
) -> Iterator[TestClient]:
    app = create_app(
        advisor=_Advisor(),
        toolchain=_Toolchain(),
        output_root=output_root,
        opener=opener,  # type: ignore[arg-type]
        copier=copier,  # type: ignore[arg-type]
    )

    def in_memory_connection() -> Iterator[sqlite3.Connection]:
        with APPLICATION_LOCK:
            yield db

    app.dependency_overrides[database_connection] = in_memory_connection
    with TestClient(app) as client:
        yield client


def test_the_plan_page_states_the_route_the_sentence_and_the_hash(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    application_id = _ready_offer(dashboard_db, tmp_path, suffix="plan-page")

    with _client(dashboard_db, tmp_path) as client:
        detail = client.get(f"/application/{application_id}")
        plan = client.get(f"/application/{application_id}/apply-plan")

    assert f"/application/{application_id}/apply-plan" in detail.text
    assert "Postuler" in detail.text
    assert plan.status_code == 200
    assert "Ouvre l&#39;offre dans le navigateur et copie la lettre." in plan.text
    route = resolve_route(dashboard_db, application_id, output_root=tmp_path)
    assert f'value="{route.plan_hash}"' in plan.text


def test_the_plan_page_names_the_routes_it_skipped_and_why(
    dashboard_db: sqlite3.Connection, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    application_id = _ready_offer(
        dashboard_db,
        tmp_path,
        suffix="plan-unavailable",
        contact_email="recrutement@exemple.fr",
    )

    with _client(dashboard_db, tmp_path) as client:
        plan = client.get(f"/application/{application_id}/apply-plan")

    # SMTP is not configured in the test environment, so the email route is
    # eligible, unavailable, and must say so rather than being selected.
    assert plan.status_code == 200
    assert "SMTP non configuré" in plan.text
    assert "Envoi par email" in plan.text


def test_a_stale_plan_hash_is_refused_and_nothing_happens(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    application_id = _ready_offer(dashboard_db, tmp_path, suffix="plan-stale")
    opened: list[str] = []

    with _client(
        dashboard_db, tmp_path, opener=lambda url: opened.append(url) or True
    ) as client:
        response = client.post(
            f"/application/{application_id}/apply",
            data={"plan_hash": "0000000000000000"},
        )

    assert response.status_code == 409
    assert "L&#39;offre a changé" in response.text
    assert opened == []
    assert current_status(dashboard_db, application_id) == "ready"
    stored = dashboard_db.execute(
        "SELECT apply_route FROM applications WHERE id = ?", (application_id,)
    ).fetchone()
    assert stored["apply_route"] is None
    assert dashboard_db.execute(
        "SELECT count(*) AS n FROM events WHERE application_id = ? "
        "AND event = 'apply_route_selected'",
        (application_id,),
    ).fetchone()["n"] == 0


def test_manual_open_opens_the_offer_copies_the_letter_and_records_the_route(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    application_id = _ready_offer(
        dashboard_db, tmp_path, suffix="apply-manual", url="https://offres.test/1"
    )
    opened: list[str] = []
    copied: list[str] = []

    with _client(
        dashboard_db,
        tmp_path,
        opener=lambda url: opened.append(url) or True,
        copier=lambda text: copied.append(text) or True,
    ) as client:
        route = resolve_route(dashboard_db, application_id, output_root=tmp_path)
        response = client.post(
            f"/application/{application_id}/apply",
            data={"plan_hash": route.plan_hash},
            follow_redirects=False,
        )
        detail = client.get(f"/application/{application_id}")

    assert response.status_code == 303
    assert opened == ["https://offres.test/1"]
    assert copied and "Madame, Monsieur," in copied[0]
    assert "<p>" not in copied[0]
    # manual_open is terminal but does not send anything: the human still says so.
    assert current_status(dashboard_db, application_id) == "ready"
    assert "Marquer comme envoyée" in detail.text
    stored = dashboard_db.execute(
        "SELECT apply_route FROM applications WHERE id = ?", (application_id,)
    ).fetchone()
    assert stored["apply_route"] == "manual_open"


def test_a_clipboard_that_refuses_is_reported_not_hidden(
    dashboard_db: sqlite3.Connection, tmp_path: Path
) -> None:
    application_id = _ready_offer(
        dashboard_db, tmp_path, suffix="apply-noclip", url="https://offres.test/2"
    )

    with _client(
        dashboard_db,
        tmp_path,
        opener=lambda url: True,
        copier=lambda text: False,
    ) as client:
        route = resolve_route(dashboard_db, application_id, output_root=tmp_path)
        response = client.post(
            f"/application/{application_id}/apply",
            data={"plan_hash": route.plan_hash},
        )

    assert response.status_code == 200
    assert "presse-papiers" in response.text


def test_the_email_route_hands_over_to_the_existing_confirmation(
    dashboard_db: sqlite3.Connection, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Nothing about sending changes in this phase."""

    from jobpilot import routing

    application_id = _ready_offer(
        dashboard_db,
        tmp_path,
        suffix="apply-email",
        contact_email="recrutement@exemple.fr",
    )
    monkeypatch.setattr(routing, "get_settings", lambda: _settings())

    with _client(dashboard_db, tmp_path) as client:
        route = resolve_route(
            dashboard_db, application_id, settings=_settings(), output_root=tmp_path
        )
        response = client.post(
            f"/application/{application_id}/apply",
            data={"plan_hash": route.plan_hash},
            follow_redirects=False,
        )

    assert route.id == "email"
    assert response.status_code == 303
    assert response.headers["location"] == f"/application/{application_id}/email"


# ----- gates, each pinned -----


def test_the_wttj_route_never_submits_while_the_flag_is_false(
    dashboard_db: sqlite3.Connection, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from jobpilot import apply_assist, routing
    from jobpilot import dashboard as dashboard_module

    application_id = _ready_offer(
        dashboard_db,
        tmp_path,
        suffix="gate-wttj",
        source_name="wttj",
        url="https://www.welcometothejungle.com/fr/companies/acme/jobs/soc",
    )
    monkeypatch.setattr(routing, "get_settings", lambda: _settings())
    calls: list[str] = []

    def fake_launch(
        db: sqlite3.Connection, app_id: int, **kwargs: object
    ) -> apply_assist.WTTJApplyResult:
        calls.append("launch")
        assert get_settings().wttj_auto_submit_enabled is False
        return apply_assist.WTTJApplyResult("apply_dry_run")

    monkeypatch.setattr(dashboard_module, "launch_wttj_application", fake_launch)

    with _client(dashboard_db, tmp_path) as client:
        route = resolve_route(
            dashboard_db, application_id, settings=_settings(), output_root=tmp_path
        )
        response = client.post(
            f"/application/{application_id}/apply",
            data={"plan_hash": route.plan_hash},
            follow_redirects=False,
        )

    assert route.id == "wttj_inline"
    assert response.status_code == 303
    assert calls == ["launch"]
    assert get_settings().wttj_auto_submit_enabled is False
    assert current_status(dashboard_db, application_id) == "ready"


def test_the_ats_route_reaches_the_existing_prefill_and_submits_nothing(
    dashboard_db: sqlite3.Connection, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from jobpilot import apply_assist, routing
    from jobpilot import dashboard as dashboard_module

    application_id = _ready_offer(
        dashboard_db,
        tmp_path,
        suffix="gate-ats",
        source_name="ats",
        url="https://jobs.lever.co/acme/security",
    )
    monkeypatch.setattr(routing, "get_settings", lambda: _settings())
    calls: list[int] = []

    def fake_launch(
        db: sqlite3.Connection, app_id: int, **kwargs: object
    ) -> apply_assist.AssistResult:
        calls.append(app_id)
        return apply_assist.AssistResult("prefill_launched", adapter="lever")

    monkeypatch.setattr(dashboard_module, "launch_application_assist", fake_launch)

    with _client(dashboard_db, tmp_path) as client:
        route = resolve_route(
            dashboard_db, application_id, settings=_settings(), output_root=tmp_path
        )
        response = client.post(
            f"/application/{application_id}/apply",
            data={"plan_hash": route.plan_hash},
            follow_redirects=False,
        )

    assert route.id == "ats_prefill"
    assert response.status_code == 303
    assert calls == [application_id]
    assert current_status(dashboard_db, application_id) == "ready"


def test_the_gates_this_phase_must_not_touch_are_still_where_they_were() -> None:
    """COLD_SEND_ENABLED and WTTJ_AUTO_SUBMIT_ENABLED default off, and the
    outreach rails are unchanged: this phase adds no auto-submit path."""

    from jobpilot.contacts import MAX_PER_DAY, OPT_OUT_LINE, STAGGER_MINUTES

    settings = get_settings()
    assert settings.cold_send_enabled is False
    assert settings.wttj_auto_submit_enabled is False
    assert MAX_PER_DAY == 25
    assert STAGGER_MINUTES == 4
    assert OPT_OUT_LINE.strip()


def test_migration_006_adds_a_nullable_apply_route(
    dashboard_db: sqlite3.Connection,
) -> None:
    columns = {
        row["name"]: row
        for row in dashboard_db.execute("PRAGMA table_info(applications)").fetchall()
    }

    assert "apply_route" in columns
    assert columns["apply_route"]["type"] == "TEXT"
    assert columns["apply_route"]["notnull"] == 0
    assert columns["apply_route"]["dflt_value"] is None
