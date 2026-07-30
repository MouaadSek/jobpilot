"""Stage 2: contact discovery (pluggable), storage, suppression, and cold-mail
drafting with the legal rails from the constitution.

This is a DRAFTING module. It queues email drafts (email_queue) and records
LinkedIn note drafts (events), staggered and capped, honoring the suppression
list and professional-address rule. Nothing is ever sent here: an actual send
requires a prior human_approved event (recorded via the `apply` command) plus a
future send phase.

Discovery is behind an interface so it is pluggable; the default is manual entry
(no people-scraping). The user looks contacts up and adds them via the CLI.
"""

from __future__ import annotations

import re
import sqlite3
from abc import ABC, abstractmethod
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime, time, timedelta

from jobpilot.logging_conf import get_logger
from jobpilot.state import log_event

log = get_logger("contacts")

# ---- Legal rails (constitution) ----
MAX_PER_DAY = 25
STAGGER_MINUTES = 4
FUTURE_DAY_START = time(9, 0, tzinfo=UTC)  # first slot on a fresh future day
OPT_OUT_LINE = (
    "Pour ne plus recevoir de messages de ma part, répondez simplement "
    "« STOP » à cet e-mail."
)

# Free/personal providers we refuse to cold-mail (only generic pro addresses).
PERSONAL_EMAIL_DOMAINS = {
    "gmail.com", "googlemail.com", "yahoo.com", "yahoo.fr", "ymail.com",
    "hotmail.com", "hotmail.fr", "outlook.com", "outlook.fr", "live.com",
    "live.fr", "msn.com", "icloud.com", "me.com", "aol.com", "gmx.com",
    "gmx.fr", "protonmail.com", "proton.me", "free.fr", "orange.fr",
    "wanadoo.fr", "sfr.fr", "laposte.net", "bbox.fr", "numericable.fr",
}

# Generic mailboxes may be sent after the standard confirmation. A named
# mailbox on a professional domain requires the additional UI confirmation.
GENERIC_EMAIL_LOCAL_PARTS = frozenset(
    {
        "career",
        "careers",
        "contact",
        "emploi",
        "emplois",
        "hiring",
        "hr",
        "info",
        "job",
        "jobs",
        "recrutement",
        "recruiting",
        "rh",
        "talent",
        "talents",
    }
)


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


# ---- Discovery interface (pluggable; default manual) ----

@dataclass(slots=True)
class ContactCandidate:
    full_name: str | None = None
    role: str | None = None
    email: str | None = None
    linkedin_url: str | None = None
    source: str = "manual"


class DiscoverySource(ABC):
    """Finds likely hiring contacts for a company. Implementations must not
    scrape login-walled sites (LinkedIn/Indeed) per the constitution."""

    name: str

    @abstractmethod
    def find_contacts(self, company_name: str) -> list[ContactCandidate]:
        raise NotImplementedError


class ManualDiscovery(DiscoverySource):
    """Default: no automated discovery. The user adds contacts via the CLI."""

    name = "manual"

    def find_contacts(self, company_name: str) -> list[ContactCandidate]:
        return []


# ---- Address validation ----

def is_professional_address(email: str | None) -> bool:
    """True only for well-formed addresses NOT on a personal free-provider domain."""
    if not email or email.count("@") != 1:
        return False
    local, _, domain = email.partition("@")
    domain = domain.lower().strip()
    if not local.strip() or "." not in domain:
        return False
    return domain not in PERSONAL_EMAIL_DOMAINS


def requires_personal_confirmation(email: str | None) -> bool:
    """Whether a named mailbox on a professional domain needs extra approval."""

    if not is_professional_address(email):
        return False
    assert email is not None
    local = email.partition("@")[0].strip().casefold()
    # Qualifiers such as recrutement.paris or jobs-emea remain generic.
    base = re.split(r"[+._-]", local, maxsplit=1)[0]
    return base not in GENERIC_EMAIL_LOCAL_PARTS


# ---- Suppression list ----

def suppress_email(db: sqlite3.Connection, email: str, reason: str | None = None) -> None:
    db.execute(
        "INSERT OR IGNORE INTO suppression_list (email, reason) VALUES (?, ?)",
        (email.lower().strip(), reason),
    )
    db.commit()


def is_suppressed(db: sqlite3.Connection, email: str) -> bool:
    row = db.execute(
        "SELECT 1 FROM suppression_list WHERE email = ?", (email.lower().strip(),)
    ).fetchone()
    return row is not None


# ---- Contact storage ----

def upsert_contact(
    db: sqlite3.Connection,
    company_id: int,
    *,
    full_name: str | None = None,
    role: str | None = None,
    email: str | None = None,
    linkedin_url: str | None = None,
    source: str = "manual",
) -> int:
    """Idempotent on (company_id, email). Returns the contact id."""
    norm_email = email.lower().strip() if email else None
    if norm_email:
        existing = db.execute(
            "SELECT id FROM contacts WHERE company_id = ? AND email = ?",
            (company_id, norm_email),
        ).fetchone()
        if existing:
            db.execute(
                "UPDATE contacts SET full_name=?, role=?, linkedin_url=?, source=? "
                "WHERE id=?",
                (full_name, role, linkedin_url, source, existing["id"]),
            )
            db.commit()
            return int(existing["id"])
    cur = db.execute(
        "INSERT INTO contacts (company_id, full_name, role, email, linkedin_url, "
        "source) VALUES (?, ?, ?, ?, ?, ?)",
        (company_id, full_name, role, norm_email, linkedin_url, source),
    )
    db.commit()
    return int(cur.lastrowid)


def list_contacts(db: sqlite3.Connection, company_id: int) -> list[sqlite3.Row]:
    return db.execute(
        "SELECT * FROM contacts WHERE company_id = ? ORDER BY id", (company_id,)
    ).fetchall()


def list_outreach_targets(
    db: sqlite3.Connection,
    *,
    source: str | None = None,
    limit: int = 30,
) -> list[sqlite3.Row]:
    """Companies an ingestion source flagged as likely to hire an alternant.

    These are outreach candidates, never offers: nothing here has posted a job,
    so none of it belongs in the review queue. Ordered with the ones nobody has
    contacted yet first, since those are the work.
    """

    clause = "WHERE c.source IS NOT NULL"
    params: list[object] = []
    if source:
        clause = "WHERE c.source = ?"
        params.append(source)
    params.append(limit)
    return db.execute(
        "SELECT c.id, c.name, c.city, c.sector, c.size_bucket, c.source, c.notes, "
        "       count(ct.id) AS contact_count "
        "FROM companies c "
        "LEFT JOIN contacts ct ON ct.company_id = c.id "
        f"{clause} "
        "GROUP BY c.id "
        "ORDER BY contact_count ASC, c.name ASC "
        "LIMIT ?",
        params,
    ).fetchall()


def discover_and_store(
    db: sqlite3.Connection, company_id: int, company_name: str,
    discovery: DiscoverySource | None = None,
) -> list[int]:
    """Run a discovery source and persist candidates. Default manual = no-op."""
    src = discovery or ManualDiscovery()
    ids = []
    for c in src.find_contacts(company_name):
        ids.append(upsert_contact(
            db, company_id, full_name=c.full_name, role=c.role, email=c.email,
            linkedin_url=c.linkedin_url, source=c.source,
        ))
    return ids


# ---- Send scheduling (stagger + daily cap) ----

def _pending_slots(db: sqlite3.Connection) -> list[datetime]:
    rows = db.execute(
        "SELECT scheduled_at FROM email_queue WHERE sent_at IS NULL"
    ).fetchall()
    out = []
    for r in rows:
        try:
            out.append(datetime.fromisoformat(r["scheduled_at"]))
        except (ValueError, TypeError):
            continue
    return sorted(out)


def next_send_slot(db: sqlite3.Connection, now: datetime | None = None) -> datetime:
    """Next allowed send time: >=4 min after the last slot that day, <=25/day.

    Rolls to 09:00 UTC on the next day once a day is full. 25 slots * 4 min =
    100 min, so a day never overflows into the next within its own stagger.
    """
    now = now or datetime.now(UTC)
    slots = _pending_slots(db)
    per_day = Counter(s.date() for s in slots)

    day = now.date()
    while per_day.get(day, 0) >= MAX_PER_DAY:
        day = day + timedelta(days=1)

    same_day = [s for s in slots if s.date() == day]
    if same_day:
        candidate = max(same_day) + timedelta(minutes=STAGGER_MINUTES)
    elif day == now.date():
        candidate = now
    else:
        candidate = datetime.combine(day, FUTURE_DAY_START)
    if candidate < now:
        candidate = now
    return candidate


def queue_cold_email(
    db: sqlite3.Connection, application_id: int, to_email: str, subject: str,
    body: str, *, now: datetime | None = None,
) -> int | None:
    """Queue one initial cold email if allowed. Returns email_queue id or None.

    Skips (returns None) if the address is suppressed or not professional, or if
    an unsent initial email is already queued for this application (idempotency).
    """
    if is_suppressed(db, to_email):
        log.info("skip queue: %s is suppressed", to_email)
        return None
    if not is_professional_address(to_email):
        log.info("skip queue: %s is not a professional address", to_email)
        return None
    dup = db.execute(
        "SELECT id FROM email_queue WHERE application_id = ? AND kind = 'initial' "
        "AND sent_at IS NULL", (application_id,),
    ).fetchone()
    if dup:
        return int(dup["id"])

    slot = next_send_slot(db, now=now)
    cur = db.execute(
        "INSERT INTO email_queue (application_id, to_email, subject, body, "
        "scheduled_at, kind) VALUES (?, ?, ?, ?, ?, 'initial')",
        (application_id, to_email, subject, body, slot.isoformat()),
    )
    db.commit()
    log.info("queued cold email for application %d at %s", application_id,
             slot.isoformat())
    return int(cur.lastrowid)


# ---- Drafting (French) ----

def draft_linkedin_note(
    candidate_name: str, contact_name: str | None, role: str, company: str,
) -> str:
    """<=300-char French LinkedIn connection note referencing the role."""
    greeting = f"Bonjour {contact_name.split()[0]}," if contact_name else "Bonjour,"
    note = (
        f"{greeting} étudiant en M1 cybersécurité à Lille, je recherche une "
        f"alternance/stage en {role} et votre travail chez {company} m'intéresse "
        f"beaucoup. Je serais ravi d'échanger. Bien à vous, {candidate_name}."
    )
    if len(note) > 300:
        note = note[:297].rstrip() + "..."
    return note


def draft_cold_email(
    candidate_name: str, contact_name: str | None, role: str, company: str,
) -> tuple[str, str]:
    """French cold email (subject, body), 5-7 sentences, with opt-out line."""
    subject = f"Candidature spontanée — alternance/stage {role} ({company})"
    greeting = f"Bonjour {contact_name}," if contact_name else "Bonjour,"
    body = (
        f"{greeting}\n\n"
        f"Actuellement en M1 cybersécurité à Lille, je recherche une alternance "
        f"de 12 mois ou un stage en {role}. "
        f"Le positionnement de {company} sur ces sujets correspond précisément à "
        f"mon projet professionnel. "
        f"Je maîtrise notamment la détection et la réponse à incident (SIEM/EDR), "
        f"la sécurité cloud Azure et l'analyse de vulnérabilités. "
        f"Je serais ravi de vous présenter mon parcours lors d'un court échange. "
        f"Seriez-vous disponible pour un appel de quinze minutes dans les "
        f"prochains jours ?\n\n"
        f"Bien cordialement,\n{candidate_name}\n\n{OPT_OUT_LINE}"
    )
    return subject, body


# ---- Orchestration ----

@dataclass(slots=True)
class OutreachDraft:
    application_id: int
    contact_id: int
    linkedin_note: str
    email_subject: str | None
    email_body: str | None
    email_queue_id: int | None
    email_skipped_reason: str | None


def _candidate_name(db: sqlite3.Connection) -> str:
    row = db.execute("SELECT full_name FROM profile WHERE id = 1").fetchone()
    return (row["full_name"] if row and row["full_name"] else "Mouaad Sekkouri")


def _get_or_create_cold_application(
    db: sqlite3.Connection, company_id: int, contact: sqlite3.Row,
) -> int:
    existing = db.execute(
        "SELECT id FROM applications WHERE kind='cold' AND company_id=? "
        "AND coalesce(contact_email,'')=coalesce(?, '') "
        "AND status NOT IN ('skipped','rejected','ghosted')",
        (company_id, contact["email"]),
    ).fetchone()
    if existing:
        return int(existing["id"])
    cur = db.execute(
        "INSERT INTO applications (company_id, kind, status, contact_email, "
        "contact_name, last_event_at) VALUES (?, 'cold', 'queued', ?, ?, ?)",
        (company_id, contact["email"], contact["full_name"], _utc_now()),
    )
    db.commit()
    return int(cur.lastrowid)


def prepare_outreach(
    db: sqlite3.Connection, company_id: int, role: str, contact_id: int,
    *, now: datetime | None = None,
) -> OutreachDraft:
    """Draft LinkedIn note + cold email for a contact and queue them for review.

    Creates (or reuses) a cold application in 'queued'. Nothing is sent; approval
    goes through `jobpilot apply <id>` which records human_approved.
    """
    contact = db.execute(
        "SELECT * FROM contacts WHERE id = ? AND company_id = ?",
        (contact_id, company_id),
    ).fetchone()
    if contact is None:
        raise ValueError(f"contact {contact_id} not found for company {company_id}")
    company = db.execute(
        "SELECT name FROM companies WHERE id = ?", (company_id,)
    ).fetchone()
    company_name = company["name"] if company else "votre entreprise"
    candidate = _candidate_name(db)

    app_id = _get_or_create_cold_application(db, company_id, contact)

    note = draft_linkedin_note(candidate, contact["full_name"], role, company_name)
    log_event(db, app_id, "linkedin_draft",
              {"contact_id": contact_id, "note": note, "chars": len(note)})

    subject = body = None
    email_queue_id = None
    skipped = None
    if contact["email"]:
        if is_suppressed(db, contact["email"]):
            skipped = "suppressed"
        elif not is_professional_address(contact["email"]):
            skipped = "non_professional_address"
        else:
            subject, body = draft_cold_email(
                candidate, contact["full_name"], role, company_name)
            email_queue_id = queue_cold_email(
                db, app_id, contact["email"], subject, body, now=now)
            log_event(db, app_id, "cold_email_drafted",
                      {"contact_id": contact_id, "to": contact["email"],
                       "email_queue_id": email_queue_id})
    else:
        skipped = "no_email"

    return OutreachDraft(
        application_id=app_id, contact_id=contact_id, linkedin_note=note,
        email_subject=subject, email_body=body, email_queue_id=email_queue_id,
        email_skipped_reason=skipped,
    )


def pending_outreach(db: sqlite3.Connection) -> Iterable[sqlite3.Row]:
    """Queued cold applications awaiting review."""
    return db.execute(
        "SELECT a.id, a.contact_name, a.contact_email, c.name AS company "
        "FROM applications a LEFT JOIN companies c ON c.id = a.company_id "
        "WHERE a.kind='cold' AND a.status='queued' ORDER BY a.id"
    ).fetchall()
