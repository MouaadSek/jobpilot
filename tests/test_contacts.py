"""Stage 2: contact storage, suppression, address rules, cap/stagger, drafting."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime

import pytest

from jobpilot import contacts as C


@pytest.fixture
def company(db: sqlite3.Connection) -> int:
    cur = db.execute("INSERT INTO companies (name) VALUES ('ACME')")
    db.commit()
    return int(cur.lastrowid)


# ---- address validation ----

@pytest.mark.parametrize("email,ok", [
    ("recrutement@acme.fr", True),
    ("rh@acme-cyber.com", True),
    ("someone@gmail.com", False),
    ("perso@orange.fr", False),
    ("no-at-sign", False),
    ("a@b", False),          # no dot in domain
    ("", False),
    (None, False),
])
def test_is_professional_address(email, ok) -> None:
    assert C.is_professional_address(email) is ok


# ---- suppression ----

def test_suppression_roundtrip(db: sqlite3.Connection) -> None:
    assert C.is_suppressed(db, "X@ACME.fr") is False
    C.suppress_email(db, "X@ACME.fr", reason="asked to stop")
    assert C.is_suppressed(db, "x@acme.fr") is True  # case-insensitive
    C.suppress_email(db, "x@acme.fr")  # idempotent, no error
    n = db.execute("SELECT count(*) n FROM suppression_list").fetchone()["n"]
    assert n == 1


# ---- contact storage ----

def test_upsert_contact_idempotent(db: sqlite3.Connection, company: int) -> None:
    a = C.upsert_contact(db, company, full_name="A", role="RSSI",
                         email="Rssi@Acme.fr")
    b = C.upsert_contact(db, company, full_name="A. Updated", role="RSSI",
                         email="rssi@acme.fr")  # same email (normalized)
    assert a == b
    rows = C.list_contacts(db, company)
    assert len(rows) == 1
    assert rows[0]["full_name"] == "A. Updated"
    assert rows[0]["email"] == "rssi@acme.fr"


def test_manual_discovery_is_noop(db: sqlite3.Connection, company: int) -> None:
    ids = C.discover_and_store(db, company, "ACME", C.ManualDiscovery())
    assert ids == []


# ---- scheduling: stagger + daily cap ----

def _app(db: sqlite3.Connection, company: int) -> int:
    cur = db.execute(
        "INSERT INTO applications (company_id, kind, status) VALUES (?, 'cold', 'queued')",
        (company,))
    db.commit()
    return int(cur.lastrowid)


def test_stagger_four_minutes(db: sqlite3.Connection, company: int) -> None:
    now = datetime(2026, 7, 22, 8, 0, tzinfo=UTC)
    app = _app(db, company)
    id1 = C.queue_cold_email(db, app, "a@acme.fr", "s", "b", now=now)
    # second contact/app so idempotency guard doesn't collapse them
    app2 = _app(db, company)
    id2 = C.queue_cold_email(db, app2, "b@acme.fr", "s", "b", now=now)
    assert id1 and id2
    slots = C._pending_slots(db)
    assert (slots[1] - slots[0]).total_seconds() == C.STAGGER_MINUTES * 60


def test_daily_cap_rolls_to_next_day(db: sqlite3.Connection, company: int) -> None:
    now = datetime(2026, 7, 22, 8, 0, tzinfo=UTC)
    # Pre-fill 25 slots today directly in email_queue.
    for _ in range(C.MAX_PER_DAY):
        db.execute(
            "INSERT INTO email_queue (application_id, to_email, subject, body, "
            "scheduled_at, kind) VALUES (?, 'x@acme.fr', 's', 'b', ?, 'initial')",
            (_app(db, company), now.isoformat()))
    db.commit()
    # 25 already today -> next slot must be tomorrow.
    slot = C.next_send_slot(db, now=now)
    assert slot.date() > now.date()


def test_queue_skips_suppressed_and_personal(db: sqlite3.Connection, company: int) -> None:
    app = _app(db, company)
    C.suppress_email(db, "sup@acme.fr")
    assert C.queue_cold_email(db, app, "sup@acme.fr", "s", "b") is None
    assert C.queue_cold_email(db, app, "perso@gmail.com", "s", "b") is None
    assert db.execute("SELECT count(*) n FROM email_queue").fetchone()["n"] == 0


def test_queue_is_idempotent_per_application(db: sqlite3.Connection, company: int) -> None:
    app = _app(db, company)
    first = C.queue_cold_email(db, app, "a@acme.fr", "s", "b")
    second = C.queue_cold_email(db, app, "a@acme.fr", "s", "b")
    assert first == second
    assert db.execute("SELECT count(*) n FROM email_queue").fetchone()["n"] == 1


# ---- drafting ----

def test_linkedin_note_under_300_chars() -> None:
    note = C.draft_linkedin_note("Mouaad Sekkouri", "Jean Dupont",
                                 "SOC analyst", "ACME Cyber")
    assert len(note) <= 300
    assert "SOC analyst" in note and "Jean" in note


def test_cold_email_has_optout_and_role() -> None:
    subject, body = C.draft_cold_email("Mouaad Sekkouri", "Jean Dupont",
                                       "cloud security", "ACME")
    assert "cloud security" in subject
    assert C.OPT_OUT_LINE in body
    assert "Mouaad Sekkouri" in body
    # 5-7 sentences in the pitch (rough sanity check on '.' + '?')
    assert body.count(".") + body.count("?") >= 5


# ---- orchestration ----

def test_prepare_outreach_queues_but_does_not_send(
    db: sqlite3.Connection, company: int
) -> None:
    db.execute("INSERT INTO profile (id, full_name) VALUES (1, 'Mouaad Sekkouri')")
    db.commit()
    cid = C.upsert_contact(db, company, full_name="Jean Dupont", role="RSSI",
                           email="rssi@acme.fr")
    draft = C.prepare_outreach(db, company, "SOC analyst", cid)

    # cold application created, queued, not sent
    app = db.execute("SELECT status FROM applications WHERE id=?",
                     (draft.application_id,)).fetchone()
    assert app["status"] == "queued"
    # email queued but unsent
    eq = db.execute("SELECT sent_at FROM email_queue WHERE id=?",
                    (draft.email_queue_id,)).fetchone()
    assert eq["sent_at"] is None
    # no human_approved event yet -> nothing may send
    ev = db.execute("SELECT count(*) n FROM events WHERE application_id=? "
                    "AND event='human_approved'", (draft.application_id,)).fetchone()
    assert ev["n"] == 0
    # linkedin draft recorded as an event
    ld = db.execute("SELECT count(*) n FROM events WHERE application_id=? "
                    "AND event='linkedin_draft'", (draft.application_id,)).fetchone()
    assert ld["n"] == 1


def test_prepare_outreach_idempotent(db: sqlite3.Connection, company: int) -> None:
    db.execute("INSERT INTO profile (id, full_name) VALUES (1, 'Mouaad Sekkouri')")
    db.commit()
    cid = C.upsert_contact(db, company, full_name="Jean", email="rh@acme.fr")
    d1 = C.prepare_outreach(db, company, "SOC", cid)
    d2 = C.prepare_outreach(db, company, "SOC", cid)
    assert d1.application_id == d2.application_id
    # one cold application, one queued email
    assert db.execute("SELECT count(*) n FROM applications WHERE kind='cold'"
                      ).fetchone()["n"] == 1
    assert db.execute("SELECT count(*) n FROM email_queue").fetchone()["n"] == 1


def test_prepare_outreach_personal_email_skips_email_keeps_linkedin(
    db: sqlite3.Connection, company: int
) -> None:
    db.execute("INSERT INTO profile (id, full_name) VALUES (1, 'Mouaad')")
    db.commit()
    cid = C.upsert_contact(db, company, full_name="Jean", email="jean@gmail.com")
    draft = C.prepare_outreach(db, company, "SOC", cid)
    assert draft.email_queue_id is None
    assert draft.email_skipped_reason == "non_professional_address"
    assert draft.linkedin_note  # LinkedIn note still drafted
    assert db.execute("SELECT count(*) n FROM email_queue").fetchone()["n"] == 0
