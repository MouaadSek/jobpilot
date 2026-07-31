-- Task 34.D: remember the shape of an application form, never its contents.
--
-- An unknown form costs effort once; the next offer on the same domain is
-- prefilled from what was learned. What is stored is a mapping only --
-- selector -> profile field -- because this table decides what gets typed into
-- a stranger's form, and a table of values would be a table of personal data
-- with no reason to exist.
--
-- profile_field is a closed enum enforced in jobpilot.form_learning, not a free
-- string. A CHECK constraint here would freeze the enum into the schema and
-- every future field would need a migration, so the constraint lives with the
-- code that owns the enum, and a write with an unknown value is rejected before
-- it reaches SQLite.

CREATE TABLE IF NOT EXISTS form_mappings (
    id INTEGER PRIMARY KEY,
    domain TEXT NOT NULL,
    selector TEXT NOT NULL,
    label TEXT,
    profile_field TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    last_used_at TEXT,
    uses INTEGER NOT NULL DEFAULT 0,
    UNIQUE (domain, selector)
);

-- The per-domain submit gate. The spec's own hard rule requires it ("a
-- per-domain flag, default off") but its DDL had nowhere to put it, so it gets
-- its own table rather than being smuggled into form_mappings, where it would
-- be duplicated once per selector and could disagree with itself.
--
-- Default 0: prefill is automatic, pressing submit never is. Flipping this is a
-- separate decision with its own evidence.

CREATE TABLE IF NOT EXISTS form_domains (
    domain TEXT PRIMARY KEY,
    submit_enabled INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
