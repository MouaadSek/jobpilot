-- Stage 2: contact storage + cold-mail suppression list.
-- Contacts feed cold outreach (applications.kind='cold'); email drafts still go
-- through email_queue with staggering + daily cap, and nothing is sent without a
-- recorded human_approved event.

CREATE TABLE contacts (
    id INTEGER PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    full_name TEXT,
    role TEXT,                          -- RSSI, DRH, Hiring Manager, Recrutement...
    email TEXT,
    linkedin_url TEXT,
    source TEXT NOT NULL DEFAULT 'manual',  -- discovery source that produced it
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (company_id, email)
);

CREATE INDEX idx_contacts_company ON contacts(company_id);

CREATE TABLE suppression_list (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,         -- lowercased; honored before every send
    reason TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
