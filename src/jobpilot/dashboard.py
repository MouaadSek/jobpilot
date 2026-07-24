"""Loopback-only FastAPI review dashboard."""

from __future__ import annotations

import sqlite3
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Annotated, Any

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from jobpilot.apply_flow import (
    APPLICATION_LOCK,
    ApplicationGenerationError,
    ApplicationNotFoundError,
    ApplicationNotQueuedError,
    approve_application,
)
from jobpilot.config import get_settings
from jobpilot.db import connect
from jobpilot.review import (
    TAB_STATUSES,
    application_detail,
    applications_by_status,
    event_history,
    status_tabs,
)
from jobpilot.state import IllegalTransition, transition

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
) -> FastAPI:
    """Build the local dashboard, with injectable generation collaborators for tests."""

    app = FastAPI(title="JobPilot Review Dashboard", docs_url=None, redoc_url=None)
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
    templates.env.filters["ymd"] = _ymd
    artifacts_root = Path(output_root or get_settings().output_dir)

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
                "events": event_history(db, application_id),
                "tracker_row": tracker_row,
                "error": error,
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
                )
            except ApplicationNotFoundError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc
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
