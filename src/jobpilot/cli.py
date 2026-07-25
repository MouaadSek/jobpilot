"""JobPilot CLI."""

from __future__ import annotations

from pathlib import Path

import typer

from jobpilot.apply_flow import (
    ApplicationGenerationError,
    ApplicationNotFoundError,
    ApplicationNotQueuedError,
    approve_application,
)
from jobpilot.config import MissingCredentialError, get_settings
from jobpilot.db import connect, init_db
from jobpilot.ingest import ingest_source
from jobpilot.logging_conf import get_logger
from jobpilot.profile import ProfileInput, load_variants, save_profile, sync_variants
from jobpilot.review import status_counts
from jobpilot.sources.registry import (
    available_sources,
    build_source,
    enabled_sources,
    is_enabled,
)
from jobpilot.state import transition

log = get_logger("cli")

app = typer.Typer(
    name="jobpilot",
    help="Personal job application pipeline (French IT/cybersecurity).",
    no_args_is_help=True,
    add_completion=False,
)


@app.command("init-db")
def init_db_cmd() -> None:
    """Create the database from schema.sql, run migrations, seed sources."""
    settings = get_settings()
    init_db()
    typer.echo(f"initialized database at {settings.db_path}")


@app.command("ingest")
def ingest_cmd(
    source: str = typer.Option(
        "all", "--source", "-s",
        help=f"Source name or 'all'. Available: {', '.join(available_sources())}",
    ),
    since: int | None = typer.Option(
        None, "--since",
        help="France Travail recency window in days (1,3,7,14,31). Default: env/31.",
    ),
) -> None:
    """Fetch offers from a source (or all sources) into the database."""
    conn = connect()
    targets = enabled_sources() if source == "all" else [source]
    total_inserted = 0
    try:
        for name in targets:
            if not is_enabled(name):
                typer.secho(f"skip {name}: disabled in config/sources.yaml",
                            fg=typer.colors.YELLOW, err=True)
                continue
            try:
                src = build_source(name, since=since)
            except MissingCredentialError as exc:
                typer.secho(f"skip {name}: {exc}", fg=typer.colors.YELLOW, err=True)
                continue
            result = ingest_source(conn, src)
            total_inserted += result.inserted
            typer.echo(
                f"{name}: fetched={result.fetched} inserted={result.inserted} "
                f"duplicates={result.duplicates} "
                f"companies_created={result.companies_created}"
            )
    finally:
        conn.close()
    typer.echo(f"done: {total_inserted} new offer(s)")


@app.command("score")
def score_cmd() -> None:
    """Score all unscored offers and queue those above threshold."""
    from jobpilot.scoring import score  # lazy: pulls in the embedding model

    conn = connect()
    try:
        queued = score(conn)
    finally:
        conn.close()
    typer.echo(f"scored; {queued} offer(s) newly queued")


@app.command("queue")
def queue_cmd(
    limit: int = typer.Option(30, "--limit", "-n", help="Max rows to show."),
) -> None:
    """List queued applications, highest final_score first."""
    conn = connect()
    try:
        rows = conn.execute(
            "SELECT a.id, m.final_score AS score, o.title, o.city, "
            "       o.contract_type, o.url, c.name AS company "
            "FROM applications a "
            "JOIN offers o ON o.id = a.offer_id "
            "LEFT JOIN match_scores m ON m.offer_id = o.id "
            "LEFT JOIN companies c ON c.id = o.company_id "
            "WHERE a.status = 'queued' "
            "ORDER BY m.final_score DESC NULLS LAST LIMIT ?",
            (limit,),
        ).fetchall()
    finally:
        conn.close()
    if not rows:
        typer.echo("queue empty")
        return
    for r in rows:
        score = f"{r['score']:.2f}" if r["score"] is not None else " -- "
        typer.echo(
            f"[{r['id']:>4}] {score}  {(r['title'] or '')[:48]:48}  "
            f"{(r['company'] or '?')[:22]:22}  {(r['city'] or '?')[:18]:18}  "
            f"{r['contract_type'] or '?':10}  {r['url']}"
        )


@app.command("apply")
def apply_cmd(application_id: int = typer.Argument(..., help="Application id.")) -> None:
    """Approve an application and generate its tailored application documents."""
    conn = connect()
    try:
        try:
            outcome = approve_application(
                conn,
                application_id,
                via="cli apply",
                on_generating=lambda: typer.echo(
                    f"application {application_id}: approved -> generating"
                ),
            )
        except (ApplicationNotFoundError, ApplicationNotQueuedError):
            typer.secho("application is not in 'queued' state", fg=typer.colors.RED,
                        err=True)
            raise typer.Exit(1) from None
        except ApplicationGenerationError as exc:
            typer.secho(
                f"application {application_id}: generation failed; "
                f"returned to queued: {exc}",
                fg=typer.colors.RED,
                err=True,
            )
            raise typer.Exit(1) from exc
        if outcome.is_cold_application:
            return
        result = outcome.generation
    finally:
        conn.close()

    assert result is not None
    typer.echo(f"CV variant: {result.selection.label} ({result.selection.slug})")
    typer.echo(f"Tailoring: {result.rationale}")
    typer.echo(f"CV HTML: {result.cv_html_path}")
    typer.echo(f"CV PDF: {result.cv_pdf_path}")
    typer.echo(f"Motivation letter HTML: {result.letter_body_path}")
    typer.echo(f"Motivation letter PDF: {result.letter_pdf_path}")
    typer.echo(f"Tracker: {result.tracker_path}")
    typer.echo("Tracker row:")
    typer.echo(result.tracker_row)
    typer.echo(f"application {application_id}: ready for human review")


@app.command("skip")
def skip_cmd(application_id: int = typer.Argument(..., help="Application id.")) -> None:
    """Pass on an application: move queued -> skipped."""
    conn = connect()
    try:
        transition(conn, application_id, "skipped", detail={"via": "cli skip"})
    finally:
        conn.close()
    typer.echo(f"application {application_id}: skipped")


@app.command("send")
def send_cmd(
    application_id: int = typer.Argument(..., help="Ready application id."),
) -> None:
    """Show the email that would be sent for a ready application, then confirm (y/N)."""
    from jobpilot.mailer import (
        MailerError,
        SendBlocked,
        prepare_application_email,
        send_application_email,
    )
    from jobpilot.state import current_status

    conn = connect()
    try:
        try:
            status = current_status(conn, application_id)
        except ValueError:
            typer.secho(f"no application with id={application_id}",
                        fg=typer.colors.RED, err=True)
            raise typer.Exit(1) from None
        if status != "ready":
            typer.secho(f"application {application_id} is not in 'ready' state "
                        f"(status={status})", fg=typer.colors.RED, err=True)
            raise typer.Exit(1)
        try:
            prep = prepare_application_email(conn, application_id)
        except MailerError as exc:
            typer.secho(str(exc), fg=typer.colors.RED, err=True)
            raise typer.Exit(1) from exc

        typer.echo(f"To:      {prep.recipient or '(none)'}")
        typer.echo(f"Subject: {prep.subject}")
        typer.echo("Attach:  " + ", ".join(p.name for p in prep.attachments))
        typer.echo("\n" + prep.body + "\n")
        if prep.blocked_reason:
            typer.secho(f"blocked: {prep.blocked_reason}", fg=typer.colors.RED, err=True)
            raise typer.Exit(1)
        if not typer.confirm("Send this email?", default=False):
            typer.echo("aborted")
            return
        try:
            message_id = send_application_email(conn, application_id)
        except SendBlocked as exc:
            typer.secho(f"blocked: {exc}", fg=typer.colors.RED, err=True)
            raise typer.Exit(1) from exc
        except MailerError as exc:
            typer.secho(f"send failed: {exc}", fg=typer.colors.RED, err=True)
            raise typer.Exit(1) from exc
    finally:
        conn.close()
    typer.echo(f"application {application_id}: sent ({message_id})")


@app.command("mark-sent")
def mark_sent_cmd(
    application_id: int = typer.Argument(..., help="Ready application id."),
) -> None:
    """Record an externally-submitted application as sent (ready -> applied)."""
    from jobpilot.mailer import MailerError, mark_application_sent

    conn = connect()
    try:
        try:
            mark_application_sent(conn, application_id)
        except (ValueError, MailerError) as exc:
            typer.secho(str(exc), fg=typer.colors.RED, err=True)
            raise typer.Exit(1) from exc
    finally:
        conn.close()
    typer.echo(f"application {application_id}: marked sent")


@app.command("init-profile")
def init_profile_cmd(
    variants_file: str = typer.Option(
        "config/variants.yaml", "--variants",
        help="YAML file with the cv_variants definitions.",
    ),
) -> None:
    """Interactively fill the profile singleton and seed cv_variants."""
    settings = get_settings()
    typer.echo("Enter profile details (comma-separated where noted).")
    full_name = typer.prompt("Full name")
    target_roles = _csv(typer.prompt("Target roles (comma-sep)", default=""))
    hard_skills = _csv(typer.prompt("Hard skills (comma-sep)", default=""))
    certs = _csv(typer.prompt("Certifications (comma-sep)", default=""))
    languages = _langs(typer.prompt("Languages as code:level (e.g. fr:C2,en:C1)",
                                    default=""))
    locations_ok = _csv(typer.prompt("Locations OK (comma-sep, e.g. Lille,Paris,remote)",
                                     default=""))
    contract_wanted = _csv(typer.prompt("Contracts wanted (comma-sep)",
                                        default="alternance,stage"))
    min_duration = typer.prompt("Minimum duration in months (blank for none)",
                                default="", show_default=False)
    min_duration_months = int(min_duration) if min_duration.strip() else None

    profile = ProfileInput(
        full_name=full_name, target_roles=target_roles, hard_skills=hard_skills,
        certs=certs, languages=languages, locations_ok=locations_ok,
        contract_wanted=contract_wanted, min_duration_months=min_duration_months,
    )

    conn = connect()
    try:
        save_profile(conn, profile)
        chosen = Path(variants_file)
        if not chosen.is_absolute():
            chosen = settings.config_dir.parent / chosen
        n = 0
        if chosen.exists():
            n = sync_variants(conn, load_variants(chosen))
        else:
            typer.secho(f"no variants file at {chosen}; skipped cv_variants seeding",
                        fg=typer.colors.YELLOW, err=True)

        # Cache the profile embedding now (pulls in the model once).
        from jobpilot.embeddings import ensure_profile_embedding

        ensure_profile_embedding(conn, force=True)
    finally:
        conn.close()
    typer.echo(f"profile saved; {n} cv_variant(s) synced; embedding cached")


@app.command("daemon")
def daemon_cmd(
    interval_hours: float = typer.Option(3.0, "--interval-hours",
                                         help="Cycle interval in hours."),
) -> None:
    """Run ingest + score on a loop (Ctrl-C to stop)."""
    from jobpilot.scheduler import run_daemon

    run_daemon(interval_hours)


def _resolve_company(conn, company: str) -> int:
    """Resolve a company by numeric id or name; create by name if absent."""
    if company.isdigit():
        row = conn.execute("SELECT id FROM companies WHERE id = ?",
                           (int(company),)).fetchone()
        if row is None:
            raise typer.BadParameter(f"no company with id {company}")
        return int(row["id"])
    row = conn.execute("SELECT id FROM companies WHERE lower(name) = ?",
                       (company.lower().strip(),)).fetchone()
    if row:
        return int(row["id"])
    cur = conn.execute("INSERT INTO companies (name) VALUES (?)", (company,))
    conn.commit()
    return int(cur.lastrowid)


@app.command("add-contact")
def add_contact_cmd(
    company: str = typer.Option(..., "--company", help="Company id or name."),
    name: str = typer.Option(None, "--name", help="Contact full name."),
    role: str = typer.Option(None, "--role", help="e.g. RSSI, DRH, Hiring Manager."),
    email: str = typer.Option(None, "--email", help="Professional email."),
    linkedin: str = typer.Option(None, "--linkedin", help="LinkedIn profile URL."),
) -> None:
    """Manually add a hiring contact for a company (default discovery path)."""
    from jobpilot.contacts import is_professional_address, upsert_contact

    conn = connect()
    try:
        company_id = _resolve_company(conn, company)
        if email and not is_professional_address(email):
            typer.secho(f"warning: {email} looks personal/invalid; it won't be "
                        "cold-mailed (LinkedIn note only).", fg=typer.colors.YELLOW,
                        err=True)
        cid = upsert_contact(conn, company_id, full_name=name, role=role,
                             email=email, linkedin_url=linkedin)
    finally:
        conn.close()
    typer.echo(f"contact {cid} saved for company {company_id}")


@app.command("contacts")
def contacts_cmd(
    company: str = typer.Option(..., "--company", help="Company id or name."),
) -> None:
    """List stored contacts for a company."""
    from jobpilot.contacts import list_contacts

    conn = connect()
    try:
        company_id = _resolve_company(conn, company)
        rows = list_contacts(conn, company_id)
    finally:
        conn.close()
    if not rows:
        typer.echo("no contacts")
        return
    for r in rows:
        typer.echo(f"[{r['id']:>4}] {(r['full_name'] or '?'):24} "
                   f"{(r['role'] or '?'):18} {(r['email'] or '-'):32} "
                   f"{r['linkedin_url'] or ''}")


@app.command("suppress")
def suppress_cmd(
    email: str = typer.Argument(..., help="Email to add to the suppression list."),
    reason: str = typer.Option(None, "--reason", help="Why suppressed."),
) -> None:
    """Add an address to the cold-mail suppression list (honored before sends)."""
    from jobpilot.contacts import suppress_email

    conn = connect()
    try:
        suppress_email(conn, email, reason)
    finally:
        conn.close()
    typer.echo(f"suppressed {email.lower().strip()}")


@app.command("draft-cold")
def draft_cold_cmd(
    company: str = typer.Option(..., "--company", help="Company id or name."),
    role: str = typer.Option(..., "--role", help="Role to reference in the draft."),
    contact_id: int = typer.Option(..., "--contact", help="Contact id (see contacts)."),
) -> None:
    """Draft a LinkedIn note + cold email and queue them for review (no send)."""
    from jobpilot.contacts import prepare_outreach

    conn = connect()
    try:
        company_id = _resolve_company(conn, company)
        draft = prepare_outreach(conn, company_id, role, contact_id)
    finally:
        conn.close()

    typer.echo(f"cold application {draft.application_id} queued (status=queued)\n")
    typer.echo(f"--- LinkedIn note ({len(draft.linkedin_note)} chars) ---")
    typer.echo(draft.linkedin_note + "\n")
    if draft.email_queue_id:
        typer.echo(f"--- Cold email (queued #{draft.email_queue_id}) ---")
        typer.echo(f"Subject: {draft.email_subject}\n")
        typer.echo(draft.email_body)
    else:
        typer.secho(f"email not queued: {draft.email_skipped_reason}",
                    fg=typer.colors.YELLOW)
    typer.echo(f"\nReview then approve with: jobpilot apply {draft.application_id}")


@app.command("dashboard")
def dashboard_cmd(
    port: int = typer.Option(
        8787,
        "--port",
        min=1,
        max=65535,
        help="Loopback dashboard port.",
    ),
) -> None:
    """Launch the local review dashboard on 127.0.0.1."""
    from jobpilot.dashboard import run_dashboard

    run_dashboard(port)


@app.command("stats")
def stats_cmd() -> None:
    """Show a quick snapshot of the pipeline."""
    conn = connect()
    try:
        offers = conn.execute("SELECT count(*) AS n FROM offers").fetchone()["n"]
        companies = conn.execute(
            "SELECT count(*) AS n FROM companies"
        ).fetchone()["n"]
        typer.echo(f"offers:    {offers}")
        typer.echo(f"companies: {companies}")

        by_contract = conn.execute(
            "SELECT contract_type, count(*) AS n FROM offers "
            "GROUP BY contract_type ORDER BY n DESC"
        ).fetchall()
        if by_contract:
            typer.echo("by contract:")
            for row in by_contract:
                typer.echo(f"  {row['contract_type'] or 'unknown':12} {row['n']}")

        apps = status_counts(conn)
        if apps:
            typer.echo("applications:")
            for row in apps:
                typer.echo(f"  {row['status']:14} {row['n']}")
    finally:
        conn.close()


# ----- helpers -----

def _csv(value: str) -> list[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


def _langs(value: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for pair in _csv(value):
        if ":" in pair:
            code, level = pair.split(":", 1)
            out[code.strip()] = level.strip()
    return out


if __name__ == "__main__":
    app()
