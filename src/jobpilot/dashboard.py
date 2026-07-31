"""Loopback-only FastAPI review dashboard."""

from __future__ import annotations

import socket
import sqlite3
import sys
import webbrowser
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Annotated, Any
from urllib.parse import parse_qs, urlencode

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    RedirectResponse,
    Response,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from jobpilot.apply_assist import (
    ApplyAssistError,
    WTTJApplyError,
    launch_application_assist,
    launch_wttj_application,
    open_manually,
)
from jobpilot.apply_flow import (
    APPLICATION_LOCK,
    ARCHIVE_DIR_NAME,
    ApplicationGenerationError,
    ApplicationNotFoundError,
    ApplicationNotQueuedError,
    GenerationInFlight,
    InteractiveAdvisorRequired,
    approve_application,
    archive_artifacts,
    generation_single_flight,
)
from jobpilot.clipboard import copy_text
from jobpilot.config import get_settings
from jobpilot.db import connect
from jobpilot.downloads import download_filename
from jobpilot.facts import FactBankError, load_fact_bank
from jobpilot.library import is_archive_stamp, library_entries
from jobpilot.mailer import (
    MailerError,
    SendBlocked,
    mark_application_sent,
    prepare_application_email,
    prepare_cold_email,
    send_application_email,
    send_cold_email,
)
from jobpilot.progress import MIN_POLL_INTERVAL_MS, REGISTRY, refresh_operation, track
from jobpilot.refresh import RefreshAlreadyRunning, RefreshRunner
from jobpilot.review import (
    TAB_STATUSES,
    application_detail,
    applications_by_status,
    event_history,
    outreach_drafts,
    status_tabs,
    variant_decision,
)
from jobpilot.routing import Route, RouteError, resolve_route
from jobpilot.scheduler import scheduler_status
from jobpilot.skim import (
    DEFAULT_SORT,
    SkimError,
    ignore_offer,
    promote_offer,
    skim_offers,
)
from jobpilot.skim import (
    available_sources as skim_sources,
)
from jobpilot.state import IllegalTransition, current_status, log_event, transition
from jobpilot.tracker import (
    COLUMNS as TRACKER_COLUMNS,
)
from jobpilot.tracker import (
    DEFAULT_SORT as TRACKER_DEFAULT_SORT,
)
from jobpilot.tracker import (
    SORTS as TRACKER_SORTS,
)
from jobpilot.tracker import (
    counts as tracker_counts,
)
from jobpilot.tracker import (
    statuses as tracker_statuses,
)
from jobpilot.tracker import (
    to_csv as tracker_to_csv,
)
from jobpilot.tracker import (
    tracker_rows,
)

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
STATIC_DIR = Path(__file__).resolve().parent / "static"
ALLOWED_ARTIFACTS = frozenset(
    {
        "tailored_cv.html",
        "cv.pdf",
        "letter_body.html",
        "motivation_letter.html",
        "motivation_letter.pdf",
        "tracker.tsv",
    }
)


def _ymd(value: Any) -> str:
    """Render an ISO timestamp as YYYY-MM-DD; pass other values through as text."""

    if value is None:
        return ""
    text = str(value)
    if len(text) >= 10 and text[4] == "-" and text[7] == "-":
        return text[:10]
    return text


def database_connection() -> Iterator[sqlite3.Connection]:
    """Yield one production database connection per request."""

    connection = connect()
    try:
        yield connection
    finally:
        connection.close()


Database = Annotated[sqlite3.Connection, Depends(database_connection)]


async def _posted_body(request: Request) -> str:
    """Read the ``body`` field from a urlencoded POST without python-multipart.

    Runs as an async dependency (event loop) so the endpoint can stay synchronous
    and share the request thread with the connection dependency's APPLICATION_LOCK.
    """

    raw = (await request.body()).decode("utf-8")
    return parse_qs(raw, keep_blank_values=True).get("body", [""])[0]


async def _posted_plan_hash(request: Request) -> str:
    """Read the plan_hash the confirmation page put in the form."""

    raw = (await request.body()).decode("utf-8")
    return parse_qs(raw, keep_blank_values=True).get("plan_hash", [""])[0]


def _record_apply_route(
    db: sqlite3.Connection, application_id: int, route_id: str
) -> None:
    """Record which route the human confirmed. Not a status write.

    The eventual decision about how much of the apply step to automate should
    rest on which routes actually carry the traffic, not on instinct.
    """

    db.execute(
        "UPDATE applications SET apply_route = ? WHERE id = ?",
        (route_id, application_id),
    )
    log_event(db, application_id, "apply_route_selected", {"route": route_id})


def _candidate_name(db: sqlite3.Connection) -> str | None:
    """The operator's name, for the download filename. Absent is not an error."""

    row = db.execute("SELECT full_name FROM profile WHERE id = 1").fetchone()
    return row["full_name"] if row else None


def _manual_open_warning(opened: bool, copied: bool) -> str:
    """Say which half of manual_open did not happen, rather than implying both did."""

    problems = []
    if not opened:
        problems.append("le navigateur n'a pas pu être ouvert")
    if not copied:
        problems.append("la lettre n'a pas pu être copiée dans le presse-papiers")
    return (
        "Candidature à finaliser à la main : "
        + " et ".join(problems)
        + ". L'offre reste « ready » jusqu'à « Marquer comme envoyée »."
    )


async def _posted_cold_send(request: Request) -> tuple[str, bool]:
    """Read editable body and the named-mailbox confirmation checkbox."""

    raw = (await request.body()).decode("utf-8")
    fields = parse_qs(raw, keep_blank_values=True)
    return fields.get("body", [""])[0], fields.get("personal_address_confirmed") == ["1"]


def _safe_artifact_path(
    output_root: Path,
    application_id: int,
    name: str,
) -> Path:
    requested = Path(name)
    if (
        name not in ALLOWED_ARTIFACTS
        or requested.is_absolute()
        or len(requested.parts) != 1
        or ".." in requested.parts
    ):
        raise HTTPException(status_code=404, detail="artifact not found")

    application_dir = (output_root / str(application_id)).resolve()
    candidate = (application_dir / name).resolve()
    try:
        candidate.relative_to(application_dir)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid artifact path") from exc
    if not candidate.is_file():
        raise HTTPException(status_code=404, detail="artifact not found")
    return candidate


def _safe_archive_path(
    output_root: Path,
    application_id: int,
    stamp: str,
    name: str,
) -> Path:
    """Resolve one archived artefact, with the same discipline as the live one.

    Deliberately a second, narrower function rather than a relaxation of
    ``_safe_artifact_path``: the live guard still accepts single-component names
    only, and this one additionally requires the directory to be a stamp
    ``archive_artifacts`` itself wrote. Widening the existing guard to admit a
    subdirectory would have loosened the path Task 34 pinned.
    """

    if not is_archive_stamp(stamp) or name not in ALLOWED_ARTIFACTS:
        raise HTTPException(status_code=404, detail="artifact not found")
    requested = Path(name)
    if requested.is_absolute() or len(requested.parts) != 1 or ".." in requested.parts:
        raise HTTPException(status_code=404, detail="artifact not found")

    archive_root = (
        output_root / str(application_id) / ARCHIVE_DIR_NAME / stamp
    ).resolve()
    candidate = (archive_root / name).resolve()
    try:
        candidate.relative_to(archive_root)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid artifact path") from exc
    if not candidate.is_file():
        raise HTTPException(status_code=404, detail="artifact not found")
    return candidate


def create_app(
    *,
    advisor: Any | None = None,
    toolchain: Any | None = None,
    output_root: Path | None = None,
    sender: Any | None = None,
    refresh_runner: RefreshRunner | None = None,
    fact_bank_path: Path | None = None,
    opener: Callable[[str], bool] | None = None,
    copier: Callable[[str], bool] | None = None,
) -> FastAPI:
    """Build the local dashboard, with injectable generation collaborators for tests."""

    app = FastAPI(title="JobPilot Review Dashboard", docs_url=None, redoc_url=None)
    # The design system lives in a real stylesheet rather than a <style> block,
    # so it is cacheable, diffable and has one place to change a token.
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
    templates.env.filters["ymd"] = _ymd
    artifacts_root = Path(output_root or get_settings().output_dir)
    refresher = refresh_runner or RefreshRunner()
    open_url = opener or webbrowser.open
    copy_letter = copier or copy_text

    def advisor_mode() -> str:
        """Name the advisor a web approval would actually use, or why it can't."""

        if advisor is not None:
            return "injected"
        from jobpilot.tailoring import TailoringError, resolve_provider

        try:
            return resolve_provider()
        except TailoringError:
            return "non configuré"

    templates.env.globals["advisor_mode"] = advisor_mode

    def detail_response(
        request: Request,
        db: sqlite3.Connection,
        application_id: int,
        *,
        error: str | None = None,
        status_code: int = 200,
    ) -> HTMLResponse:
        detail = application_detail(db, application_id)
        if detail is None:
            raise HTTPException(status_code=404, detail="application not found")
        events = event_history(db, application_id)
        latest_event = events[-1] if events else None
        latest_event_name = latest_event["event"] if latest_event is not None else None
        wttj_alert = None
        if latest_event_name == "apply_blocked":
            wttj_alert = (
                "La candidature WTTJ a été bloquée avant envoi. "
                f"Détail : {latest_event['detail']}"
            )
        elif latest_event_name == "submit_unconfirmed":
            wttj_alert = (
                "L'envoi WTTJ n'a pas pu être confirmé. Vérifiez la candidature "
                f"manuellement avant de réessayer. Détail : {latest_event['detail']}"
            )
        tracker_row = None
        if detail["status"] == "ready":
            try:
                tracker_path = _safe_artifact_path(
                    artifacts_root, application_id, "tracker.tsv"
                )
                tracker_row = tracker_path.read_text(encoding="utf-8").rstrip("\r\n")
            except (HTTPException, OSError):
                tracker_row = None
        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={
                "view": "detail",
                "application": detail,
                "events": events,
                "tracker_row": tracker_row,
                "variant_decision": variant_decision(db, application_id),
                "prefill_eligible": (
                    detail["status"] == "ready"
                    and detail["source"] == "ats"
                    and bool(detail["url"])
                ),
                "wttj_eligible": (
                    detail["status"] == "ready"
                    and detail["source"] == "wttj"
                    and bool(detail["url"])
                    and latest_event_name != "submit_unconfirmed"
                ),
                "wttj_alert": wttj_alert,
                "error": error,
            },
            status_code=status_code,
        )

    def wttj_confirm_response(
        request: Request,
        db: sqlite3.Connection,
        application_id: int,
    ) -> HTMLResponse:
        detail = application_detail(db, application_id)
        if detail is None:
            raise HTTPException(status_code=404, detail="application not found")
        events = event_history(db, application_id)
        latest_event_name = events[-1]["event"] if events else None
        if (
            detail["status"] != "ready"
            or detail["source"] != "wttj"
            or not detail["url"]
            or latest_event_name == "submit_unconfirmed"
        ):
            return detail_response(
                request,
                db,
                application_id,
                error=(
                    "WTTJ application is only available for a ready WTTJ offer "
                    "with an application URL."
                ),
                status_code=409,
            )
        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={
                "view": "wttj",
                "application": detail,
                "wttj_live_mode": get_settings().wttj_auto_submit_enabled,
                "error": None,
            },
        )

    def email_confirm_response(
        request: Request,
        db: sqlite3.Connection,
        application_id: int,
        *,
        body: str | None = None,
        error: str | None = None,
        status_code: int = 200,
    ) -> HTMLResponse:
        detail = application_detail(db, application_id)
        if detail is None:
            raise HTTPException(status_code=404, detail="application not found")
        if detail["status"] != "ready" or not detail["contact_email"]:
            return detail_response(
                request,
                db,
                application_id,
                error="Email is only available for a ready application with a contact.",
                status_code=409,
            )
        prep = prepare_application_email(
            db, application_id, output_root=artifacts_root
        )
        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={
                "view": "email",
                "application": detail,
                "prep": {
                    "recipient": prep.recipient,
                    "subject": prep.subject,
                    "body": prep.body if body is None else body,
                    "attachments": [path.name for path in prep.attachments],
                },
                "error": error or prep.blocked_reason,
                "can_send": prep.blocked_reason is None,
            },
            status_code=status_code,
        )

    def cold_confirm_response(
        request: Request,
        db: sqlite3.Connection,
        queue_id: int,
        *,
        body: str | None = None,
        error: str | None = None,
        status_code: int = 200,
    ) -> HTMLResponse:
        prep = prepare_cold_email(db, queue_id)
        detail = application_detail(db, prep.application_id)
        if detail is None:
            raise HTTPException(status_code=404, detail="application not found")
        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={
                "view": "cold_email",
                "application": detail,
                "prep": {
                    "queue_id": prep.queue_id,
                    "recipient": prep.recipient,
                    "subject": prep.subject,
                    "body": prep.body if body is None else body,
                    "scheduled_at": prep.scheduled_at,
                    "personal_confirmation_required": (
                        prep.personal_confirmation_required
                    ),
                },
                "error": error or prep.blocked_reason,
                "can_send": prep.blocked_reason is None,
                "cold_send_enabled": get_settings().cold_send_enabled,
            },
            status_code=status_code,
        )

    @app.get("/", response_class=HTMLResponse)
    def queue_page(
        request: Request,
        db: Database,
        status: str = "queued",
    ) -> HTMLResponse:
        if status not in TAB_STATUSES:
            raise HTTPException(status_code=404, detail="unknown status tab")
        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={
                "view": "queue",
                "status": status,
                "applications": applications_by_status(db, status),
                "tabs": status_tabs(db, status),
                "refresh_status": refresher.status().as_dict(),
                "scheduler": scheduler_status(db),
                "error": None,
            },
        )

    @app.get("/skim", response_class=HTMLResponse)
    def skim_page(
        request: Request,
        db: Database,
        source: str | None = None,
        sort: str = DEFAULT_SORT,
        page: int = 1,
        include_ignored: bool = False,
        error: str | None = None,
    ) -> HTMLResponse:
        """Offers that passed the hard filter but scored below the threshold.

        A discovery channel rather than a scoring one: alert-sourced offers
        cannot be scored well and cannot be enriched without scraping, so they
        get a human skimming path instead.
        """

        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={
                "view": "skim",
                "skim": skim_offers(
                    db,
                    source=source or None,
                    include_ignored=include_ignored,
                    sort=sort,
                    page=page,
                ),
                "skim_sources": skim_sources(db),
                "error": error,
            },
        )

    def _skim_redirect(
        page: int, source: str | None, sort: str, include_ignored: bool,
        *, error: str | None = None,
    ) -> RedirectResponse:
        """Back to the same slice of the list, so a skim keeps its place."""

        query = {"page": str(page), "sort": sort}
        if source:
            query["source"] = source
        if include_ignored:
            query["include_ignored"] = "1"
        if error:
            query["error"] = error
        return RedirectResponse(url=f"/skim?{urlencode(query)}", status_code=303)

    @app.post("/skim/{offer_id}/queue")
    def skim_queue(
        offer_id: int,
        db: Database,
        source: str | None = None,
        sort: str = DEFAULT_SORT,
        page: int = 1,
        include_ignored: bool = False,
    ) -> Response:
        """Promote a skimmed offer into the ordinary review queue."""

        with APPLICATION_LOCK:
            try:
                promote_offer(db, offer_id)
            except SkimError as exc:
                return _skim_redirect(
                    page, source, sort, include_ignored, error=str(exc)
                )
            except IllegalTransition as exc:
                return _skim_redirect(
                    page, source, sort, include_ignored, error=str(exc)
                )
        return _skim_redirect(page, source, sort, include_ignored)

    @app.post("/skim/{offer_id}/ignore")
    def skim_ignore(
        offer_id: int,
        db: Database,
        source: str | None = None,
        sort: str = DEFAULT_SORT,
        page: int = 1,
        include_ignored: bool = False,
    ) -> Response:
        """Dismiss a skimmed offer so it stops reappearing."""

        with APPLICATION_LOCK:
            try:
                ignore_offer(db, offer_id)
            except SkimError as exc:
                return _skim_redirect(
                    page, source, sort, include_ignored, error=str(exc)
                )
            except IllegalTransition as exc:
                return _skim_redirect(
                    page, source, sort, include_ignored, error=str(exc)
                )
        return _skim_redirect(page, source, sort, include_ignored)

    @app.get("/facts", response_class=HTMLResponse)
    def facts_page(request: Request) -> HTMLResponse:
        """Read-only fact bank, same content and grouping as `jobpilot facts`."""

        try:
            bank = load_fact_bank(fact_bank_path)
        except FactBankError as exc:
            return templates.TemplateResponse(
                request=request,
                name="dashboard.html",
                context={"view": "facts", "bank": None, "error": str(exc)},
                status_code=500,
            )
        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={"view": "facts", "bank": bank, "error": None},
        )

    @app.post("/refresh")
    def refresh_start() -> JSONResponse:
        """Kick off ingest + score in the background; never run two at once."""

        try:
            snapshot = refresher.start()
        except RefreshAlreadyRunning as exc:
            return JSONResponse(
                {"detail": str(exc), **refresher.status().as_dict()},
                status_code=409,
            )
        return JSONResponse(snapshot.as_dict(), status_code=202)

    @app.get("/progress")
    def progress_status() -> JSONResponse:
        """Everything slow that is happening right now.

        Deliberately touches no database: a generation holds the writer lock for
        its whole duration, so a status endpoint that needed the database could
        not answer until the thing it describes had already finished.
        """

        operations = list(REGISTRY.snapshot())
        refresh = refresh_operation(refresher.status().as_dict())
        if refresh is not None:
            operations.insert(0, refresh)
        return JSONResponse(
            {"operations": operations, "poll_interval_ms": MIN_POLL_INTERVAL_MS}
        )

    @app.get("/refresh/status")
    def refresh_status() -> JSONResponse:
        """Poll target. Deliberately touches no database, so it never blocks."""

        return JSONResponse(refresher.status().as_dict())

    @app.get("/outreach", response_class=HTMLResponse)
    def outreach_page(request: Request, db: Database) -> HTMLResponse:
        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={
                "view": "outreach",
                "drafts": outreach_drafts(db),
                "error": None,
            },
        )

    @app.get("/application/{application_id}", response_class=HTMLResponse)
    def application_page(
        request: Request,
        application_id: int,
        db: Database,
    ) -> HTMLResponse:
        return detail_response(request, db, application_id)

    @app.post("/application/{application_id}/approve")
    def approve(
        request: Request,
        application_id: int,
        db: Database,
    ) -> Response:
        with APPLICATION_LOCK, track(
            f"generate:{application_id}",
            "Génération des documents",
            step="Analyse de l'offre",
        ) as progress:
            try:
                approve_application(
                    db,
                    application_id,
                    via="dashboard",
                    advisor=advisor,
                    toolchain=toolchain,
                    output_root=artifacts_root,
                    on_generating=lambda: progress.advance("Rédaction du CV et de la lettre"),
                    # No terminal is attached to a browser request.
                    allow_interactive_advisor=False,
                )
            except ApplicationNotFoundError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc
            except InteractiveAdvisorRequired as exc:
                progress.fail(str(exc))
                return detail_response(
                    request,
                    db,
                    application_id,
                    error=str(exc),
                    status_code=409,
                )
            except ApplicationNotQueuedError as exc:
                progress.fail(str(exc))
                return detail_response(
                    request,
                    db,
                    application_id,
                    error=str(exc),
                    status_code=409,
                )
            except ApplicationGenerationError as exc:
                progress.fail(str(exc))
                return detail_response(
                    request,
                    db,
                    application_id,
                    error=str(exc),
                    status_code=422,
                )
        return RedirectResponse(
            url=f"/application/{application_id}",
            status_code=303,
        )

    def apply_plan_response(
        request: Request,
        db: sqlite3.Connection,
        application_id: int,
        *,
        route: Route,
        error: str | None = None,
        status_code: int = 200,
    ) -> HTMLResponse:
        detail = application_detail(db, application_id)
        if detail is None:
            raise HTTPException(status_code=404, detail="application not found")
        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={
                "view": "apply",
                "application": detail,
                "route": route.as_dict(),
                "error": error,
            },
            status_code=status_code,
        )

    @app.get("/application/{application_id}/apply-plan", response_class=HTMLResponse)
    def apply_plan(
        request: Request,
        application_id: int,
        db: Database,
    ) -> Response:
        """Say what the apply button will do, before it does it.

        Click one of two. The plan_hash rendered into the form is what the
        second click carries back, so an offer re-ingested in between cannot be
        applied to under a plan the human never saw.
        """

        try:
            route = resolve_route(db, application_id, output_root=artifacts_root)
        except RouteError as exc:
            return detail_response(
                request, db, application_id, error=str(exc), status_code=409
            )
        return apply_plan_response(request, db, application_id, route=route)

    @app.post("/application/{application_id}/apply")
    def apply(
        request: Request,
        application_id: int,
        db: Database,
        plan_hash: str = Depends(_posted_plan_hash),
    ) -> Response:
        """Run the confirmed route. Adds no automation and flips no gate."""

        with APPLICATION_LOCK:
            try:
                route = resolve_route(db, application_id, output_root=artifacts_root)
            except RouteError as exc:
                return detail_response(
                    request, db, application_id, error=str(exc), status_code=409
                )
            if plan_hash != route.plan_hash:
                # The offer was re-ingested, or a contact was added, between the
                # two clicks. Show the new plan and ask again rather than doing
                # something the human did not agree to.
                return apply_plan_response(
                    request,
                    db,
                    application_id,
                    route=route,
                    error=(
                        "L'offre a changé depuis l'affichage du plan. "
                        "Voici le nouveau plan : confirmez à nouveau."
                    ),
                    status_code=409,
                )

            _record_apply_route(db, application_id, route.id)

            progress = track(
                f"apply:{application_id}",
                "Envoi de la candidature",
                step=f"Voie « {route.id} »",
            )

            if route.id == "wttj_inline":
                with progress:
                    return wttj_apply(request, application_id, db)
            if route.id == "ats_prefill":
                with progress:
                    return prefill(request, application_id, db)
            if route.id == "email":
                # The existing two-step email confirmation is untouched: this
                # route hands over to it rather than sending anything itself.
                REGISTRY.finish(progress.key, step="Confirmation requise")
                return RedirectResponse(
                    url=f"/application/{application_id}/email", status_code=303
                )
            if route.id == "manual_open":
                progress.advance("Ouverture de l'offre")
                opened, copied = open_manually(
                    db,
                    application_id,
                    route.target,
                    output_root=artifacts_root,
                    opener=open_url,
                    copier=copy_letter,
                )
                REGISTRY.finish(progress.key, step="Terminé")
                if not opened or not copied:
                    return detail_response(
                        request,
                        db,
                        application_id,
                        error=_manual_open_warning(opened, copied),
                        status_code=200,
                    )
                return RedirectResponse(
                    url=f"/application/{application_id}", status_code=303
                )
            REGISTRY.finish(
                progress.key, step="Échec", error=f"Route « {route.id} » inconnue."
            )
            return detail_response(
                request,
                db,
                application_id,
                error=f"Route « {route.id} » pas encore implémentée.",
                status_code=409,
            )

    @app.post("/application/{application_id}/regenerate")
    def regenerate(
        request: Request,
        application_id: int,
        db: Database,
    ) -> Response:
        """Re-run the existing generation path on a ready application.

        No generation logic of its own: the current artefacts are archived, the
        application goes back through ``ready -> queued``, and then down the
        exact ``approve_application`` path the Approve button uses.
        """

        try:
            with generation_single_flight(application_id):
                with APPLICATION_LOCK:
                    try:
                        status = current_status(db, application_id)
                    except ValueError as exc:
                        raise HTTPException(
                            status_code=404, detail=str(exc)
                        ) from exc
                    if status != "ready":
                        # A silent no-op here would look like a regeneration
                        # that produced identical output.
                        return detail_response(
                            request,
                            db,
                            application_id,
                            error=(
                                "La régénération n'est possible que sur une "
                                "candidature « ready » (statut actuel : "
                                f"« {status} »)."
                            ),
                            status_code=409,
                        )
                    archive_artifacts(artifacts_root, application_id)
                    transition(
                        db,
                        application_id,
                        "queued",
                        detail={"via": "dashboard regenerate"},
                    )
                    with track(
                        f"generate:{application_id}",
                        "Régénération des documents",
                        step="Archivage de la version précédente",
                    ) as progress:
                        try:
                            approve_application(
                                db,
                                application_id,
                                via="dashboard regenerate",
                                advisor=advisor,
                                toolchain=toolchain,
                                output_root=artifacts_root,
                                on_generating=lambda: progress.advance(
                                    "Rédaction du CV et de la lettre"
                                ),
                                # No terminal is attached to a browser request.
                                allow_interactive_advisor=False,
                            )
                        except ApplicationNotFoundError as exc:
                            raise HTTPException(
                                status_code=404, detail=str(exc)
                            ) from exc
                        except (
                            InteractiveAdvisorRequired,
                            ApplicationNotQueuedError,
                        ) as exc:
                            progress.fail(str(exc))
                            return detail_response(
                                request,
                                db,
                                application_id,
                                error=str(exc),
                                status_code=409,
                            )
                        except ApplicationGenerationError as exc:
                            # The generation path has already rolled the
                            # application back to 'queued'; the validator's own
                            # message is what the human needs to see, verbatim.
                            progress.fail(str(exc))
                            return detail_response(
                                request,
                                db,
                                application_id,
                                error=str(exc),
                                status_code=422,
                            )
        except GenerationInFlight as exc:
            # Deliberately touches no database, exactly like /refresh's own
            # single-flight refusal: the request that owns the flight is
            # holding the writer lock.
            return JSONResponse({"detail": str(exc)}, status_code=409)
        return RedirectResponse(
            url=f"/application/{application_id}",
            status_code=303,
        )

    @app.post("/application/{application_id}/skip")
    def skip(application_id: int, db: Database) -> RedirectResponse:
        with APPLICATION_LOCK:
            try:
                transition(
                    db,
                    application_id,
                    "skipped",
                    detail={"via": "dashboard"},
                )
            except ValueError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc
            except IllegalTransition as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
        return RedirectResponse(url="/", status_code=303)

    @app.get("/outreach/{queue_id}", response_class=HTMLResponse)
    def cold_confirm(
        request: Request,
        queue_id: int,
        db: Database,
    ) -> HTMLResponse:
        try:
            return cold_confirm_response(request, db, queue_id)
        except MailerError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/outreach/{queue_id}/send")
    def cold_send(
        request: Request,
        queue_id: int,
        db: Database,
        form: tuple[str, bool] = Depends(_posted_cold_send),
    ) -> Response:
        body, personal_address_confirmed = form
        with APPLICATION_LOCK:
            try:
                prep = prepare_cold_email(db, queue_id)
            except MailerError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc
            try:
                status = current_status(db, prep.application_id)
                if status == "queued":
                    approve_application(
                        db,
                        prep.application_id,
                        via="dashboard outreach",
                    )
                elif status not in {"generating", "ready"}:
                    return cold_confirm_response(
                        request,
                        db,
                        queue_id,
                        body=body,
                        error=(
                            "cold application cannot be sent from "
                            f"status '{status}'"
                        ),
                        status_code=409,
                    )
                send_cold_email(
                    db,
                    queue_id,
                    body=body,
                    personal_address_confirmed=personal_address_confirmed,
                    sender=sender,
                )
            except ApplicationNotFoundError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc
            except ApplicationNotQueuedError as exc:
                return cold_confirm_response(
                    request,
                    db,
                    queue_id,
                    body=body,
                    error=str(exc),
                    status_code=409,
                )
            except SendBlocked as exc:
                return cold_confirm_response(
                    request,
                    db,
                    queue_id,
                    body=body,
                    error=str(exc),
                    status_code=409,
                )
            except MailerError as exc:
                return cold_confirm_response(
                    request,
                    db,
                    queue_id,
                    body=body,
                    error=str(exc),
                    status_code=422,
                )
        return RedirectResponse(url="/outreach", status_code=303)

    @app.get("/application/{application_id}/email", response_class=HTMLResponse)
    def email_confirm(
        request: Request,
        application_id: int,
        db: Database,
    ) -> HTMLResponse:
        return email_confirm_response(request, db, application_id)

    @app.get("/application/{application_id}/wttj", response_class=HTMLResponse)
    def wttj_confirm(
        request: Request,
        application_id: int,
        db: Database,
    ) -> HTMLResponse:
        """Show the final human confirmation before the WTTJ apply assist."""

        return wttj_confirm_response(request, db, application_id)

    @app.post("/application/{application_id}/wttj/apply")
    def wttj_apply(
        request: Request,
        application_id: int,
        db: Database,
    ) -> Response:
        """Run the confirmed WTTJ flow and surface safety outcomes prominently."""

        with APPLICATION_LOCK:
            detail = application_detail(db, application_id)
            if detail is None:
                raise HTTPException(status_code=404, detail="application not found")
            events = event_history(db, application_id)
            latest_event_name = events[-1]["event"] if events else None
            if (
                detail["status"] != "ready"
                or detail["source"] != "wttj"
                or not detail["url"]
                or latest_event_name == "submit_unconfirmed"
            ):
                return detail_response(
                    request,
                    db,
                    application_id,
                    error=(
                        "WTTJ application is only available for a ready WTTJ "
                        "offer with an application URL."
                    ),
                    status_code=409,
                )
            try:
                result = launch_wttj_application(
                    db,
                    application_id,
                    output_root=artifacts_root,
                    via="dashboard",
                )
            except WTTJApplyError as exc:
                return detail_response(
                    request,
                    db,
                    application_id,
                    error=str(exc),
                    status_code=409,
                )

            if result.outcome in {"apply_dry_run", "application_submitted"}:
                return RedirectResponse(
                    url=f"/application/{application_id}",
                    status_code=303,
                )
            if result.outcome == "apply_blocked":
                reason = result.reason or "unknown safety check"
                return detail_response(
                    request,
                    db,
                    application_id,
                    error=(
                        "La candidature WTTJ a été bloquée avant envoi : "
                        f"{reason}."
                    ),
                    status_code=409,
                )
            if result.outcome == "submit_unconfirmed":
                return detail_response(
                    request,
                    db,
                    application_id,
                    error=(
                        "L'envoi WTTJ n'a pas pu être confirmé. Vérifiez la "
                        "candidature manuellement avant de réessayer."
                    ),
                    status_code=409,
                )
            return detail_response(
                request,
                db,
                application_id,
                error=f"Résultat WTTJ inattendu : {result.outcome}.",
                status_code=422,
            )

    @app.post("/application/{application_id}/email/send")
    def email_send(
        request: Request,
        application_id: int,
        db: Database,
        body: str = Depends(_posted_body),
    ) -> Response:
        with APPLICATION_LOCK:
            try:
                send_application_email(
                    db, application_id, body=body, sender=sender,
                    output_root=artifacts_root,
                )
            except ValueError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc
            except SendBlocked as exc:
                return email_confirm_response(
                    request, db, application_id, body=body,
                    error=str(exc), status_code=409,
                )
            except MailerError as exc:
                return email_confirm_response(
                    request, db, application_id, body=body,
                    error=str(exc), status_code=422,
                )
        return RedirectResponse(
            url=f"/application/{application_id}", status_code=303
        )

    @app.post("/application/{application_id}/mark-sent")
    def mark_sent(application_id: int, db: Database) -> Response:
        with APPLICATION_LOCK:
            try:
                mark_application_sent(db, application_id)
            except ValueError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc
            except MailerError as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
        return RedirectResponse(
            url=f"/application/{application_id}", status_code=303
        )

    @app.post("/application/{application_id}/prefill")
    def prefill(request: Request, application_id: int, db: Database) -> Response:
        """Launch a visible ATS form prefill; the human alone may submit it."""

        with APPLICATION_LOCK:
            try:
                launch_application_assist(
                    db,
                    application_id,
                    output_root=artifacts_root,
                )
            except ApplyAssistError as exc:
                # A direct request to an ineligible record stays a clean dashboard
                # response; adapter/browser errors are handled by the URL fallback.
                return detail_response(
                    request, db, application_id, error=str(exc), status_code=409
                )
        return RedirectResponse(
            url=f"/application/{application_id}", status_code=303
        )

    @app.get("/files/{application_id}/{name}", response_class=FileResponse)
    def artifact(
        application_id: int,
        name: str,
        db: Database,
        download: bool = False,
    ) -> FileResponse:
        """Serve one generated artefact, inline by default.

        Preview and download are the same bytes over the same guarded path, so
        the traversal guard has exactly one implementation and previewing can
        never be mistaken for an action. Reading the CV is the step that decides
        whether an application is sent; it should not require a round trip
        through a Downloads folder and a separate PDF viewer.
        """

        detail = application_detail(db, application_id)
        if detail is None or detail["status"] != "ready":
            raise HTTPException(status_code=404, detail="artifact not found")
        path = _safe_artifact_path(artifacts_root, application_id, name)
        return FileResponse(
            path,
            filename=download_filename(
                name,
                application_id=application_id,
                company=detail["company"],
                candidate=_candidate_name(db),
            ),
            # Starlette sets attachment whenever `filename` is given, so inline
            # has to be stated explicitly or every preview would download.
            content_disposition_type="attachment" if download else "inline",
        )

    @app.get("/tracker", response_class=HTMLResponse)
    def tracker_page(
        request: Request,
        db: Database,
        status: str | None = None,
        sort: str = TRACKER_DEFAULT_SORT,
    ) -> HTMLResponse:
        """Where every application stands. Read-only on purpose."""

        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={
                "view": "tracker",
                "rows": tracker_rows(db, status=status or None, sort=sort),
                "columns": TRACKER_COLUMNS,
                "counts": tracker_counts(db).as_dict(),
                "statuses": tracker_statuses(db),
                "status": status or "",
                "sort": sort if sort in TRACKER_SORTS else TRACKER_DEFAULT_SORT,
                "error": None,
            },
        )

    @app.get("/tracker.csv")
    def tracker_csv(
        db: Database,
        status: str | None = None,
        sort: str = TRACKER_DEFAULT_SORT,
    ) -> Response:
        """The visible rows, in the visible order, as CSV."""

        body = tracker_to_csv(tracker_rows(db, status=status or None, sort=sort))
        return Response(
            content=body,
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="jobpilot_tracker.csv"'
            },
        )

    @app.get("/library", response_class=HTMLResponse)
    def library_page(
        request: Request,
        db: Database,
        q: str | None = None,
    ) -> HTMLResponse:
        """Every generation of every application's documents, archives included."""

        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={
                "view": "library",
                "entries": [
                    entry.as_dict()
                    for entry in library_entries(db, artifacts_root, search=q)
                ],
                "search": q or "",
                "error": None,
            },
        )

    @app.get(
        "/files/{application_id}/archive/{stamp}/{name}",
        response_class=FileResponse,
    )
    def archived_artifact(
        application_id: int,
        stamp: str,
        name: str,
        db: Database,
        download: bool = False,
    ) -> FileResponse:
        """Serve one archived artefact. Read-only, and never a status change.

        Unlike the live route this does not require the application to be
        'ready': the whole point of an archive is that it survives the
        application moving on, including to 'applied'.
        """

        detail = application_detail(db, application_id)
        if detail is None:
            raise HTTPException(status_code=404, detail="artifact not found")
        path = _safe_archive_path(artifacts_root, application_id, stamp, name)
        return FileResponse(
            path,
            filename=download_filename(
                name,
                application_id=application_id,
                company=detail["company"],
                candidate=_candidate_name(db),
            ),
            content_disposition_type="attachment" if download else "inline",
        )

    return app


DASHBOARD_HOST = "127.0.0.1"


def dashboard_already_running(
    port: int,
    *,
    host: str = DASHBOARD_HOST,
    timeout: float = 0.5,
) -> bool:
    """Whether something is already listening on the dashboard's port.

    A connect probe rather than a bind probe: bind semantics for an in-use port
    differ between Windows and Unix once SO_REUSEADDR is in play, and the
    question being asked is simply "is the dashboard already up?".
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(timeout)
        return probe.connect_ex((host, port)) == 0


def run_dashboard(port: int = 8787) -> int:
    """Run the dashboard on an intentionally fixed loopback interface.

    Returns a process exit code. A port already in use is **not** an error: the
    LaunchAgent runs under KeepAlive, so a non-zero exit there becomes a restart
    loop fighting whichever dashboard is already serving the page.
    """

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")

    if dashboard_already_running(port):
        print(f"JobPilot tourne déjà sur http://{DASHBOARD_HOST}:{port}")
        return 0

    import uvicorn

    uvicorn.run(create_app(), host=DASHBOARD_HOST, port=port)
    return 0
