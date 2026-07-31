"""Loopback-only FastAPI review dashboard."""

from __future__ import annotations

import sqlite3
import sys
import webbrowser
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Annotated, Any
from urllib.parse import parse_qs

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    RedirectResponse,
    Response,
)
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
from jobpilot.facts import FactBankError, load_fact_bank
from jobpilot.mailer import (
    MailerError,
    SendBlocked,
    mark_application_sent,
    prepare_application_email,
    prepare_cold_email,
    send_application_email,
    send_cold_email,
)
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
from jobpilot.state import IllegalTransition, current_status, log_event, transition

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
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
        with APPLICATION_LOCK:
            try:
                approve_application(
                    db,
                    application_id,
                    via="dashboard",
                    advisor=advisor,
                    toolchain=toolchain,
                    output_root=artifacts_root,
                    # No terminal is attached to a browser request.
                    allow_interactive_advisor=False,
                )
            except ApplicationNotFoundError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc
            except InteractiveAdvisorRequired as exc:
                return detail_response(
                    request,
                    db,
                    application_id,
                    error=str(exc),
                    status_code=409,
                )
            except ApplicationNotQueuedError as exc:
                return detail_response(
                    request,
                    db,
                    application_id,
                    error=str(exc),
                    status_code=409,
                )
            except ApplicationGenerationError as exc:
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

            if route.id == "wttj_inline":
                return wttj_apply(request, application_id, db)
            if route.id == "ats_prefill":
                return prefill(request, application_id, db)
            if route.id == "email":
                # The existing two-step email confirmation is untouched: this
                # route hands over to it rather than sending anything itself.
                return RedirectResponse(
                    url=f"/application/{application_id}/email", status_code=303
                )
            if route.id == "manual_open":
                opened, copied = open_manually(
                    db,
                    application_id,
                    route.target,
                    output_root=artifacts_root,
                    opener=open_url,
                    copier=copy_letter,
                )
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
                    try:
                        approve_application(
                            db,
                            application_id,
                            via="dashboard regenerate",
                            advisor=advisor,
                            toolchain=toolchain,
                            output_root=artifacts_root,
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
    def artifact(application_id: int, name: str, db: Database) -> FileResponse:
        detail = application_detail(db, application_id)
        if detail is None or detail["status"] != "ready":
            raise HTTPException(status_code=404, detail="artifact not found")
        path = _safe_artifact_path(artifacts_root, application_id, name)
        return FileResponse(path)

    return app


def run_dashboard(port: int = 8787) -> None:
    """Run the dashboard on an intentionally fixed loopback interface."""

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")
    import uvicorn

    uvicorn.run(create_app(), host="127.0.0.1", port=port)
