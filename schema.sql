-- JobPilot: core schema (SQLite compatible, upgrades cleanly to Postgres)
-- State machine lives in applications.status

PRAGMA foreign_keys = ON;

-- ============ SOURCING ============

CREATE TABLE sources (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,          -- 'france_travail', 'adzuna', 'wttw_scraper', 'linkedin'
    kind TEXT NOT NULL CHECK (kind IN ('api', 'scraper', 'manual')),
    enabled INTEGER NOT NULL DEFAULT 1,
    last_run_at TEXT,                   -- ISO 8601
    run_interval_min INTEGER DEFAULT 180
);

CREATE TABLE companies (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    siren TEXT UNIQUE,                  -- via Pappers, nullable for foreign cos
    domain TEXT,                        -- for email pattern guessing
    size_bucket TEXT,                   -- '1-10', '11-50', '51-200', '201-1000', '1000+'
    sector TEXT,
    city TEXT,
    country TEXT DEFAULT 'FR',
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE offers (
    id INTEGER PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES sources(id),
    company_id INTEGER REFERENCES companies(id),
    external_id TEXT,                   -- id on the source platform
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,                   -- full text, used for embedding
    contract_type TEXT CHECK (contract_type IN ('stage','alternance','cdi','cdd','freelance','unknown')),
    duration_months INTEGER,
    city TEXT,
    remote_policy TEXT CHECK (remote_policy IN ('onsite','hybrid','full_remote','unknown')),
    salary_min INTEGER,
    salary_max INTEGER,
    stack_tags TEXT,                    -- JSON array: ["azure","siem","kubernetes"]
    posted_at TEXT,
    scraped_at TEXT NOT NULL DEFAULT (datetime('now')),
    content_hash TEXT NOT NULL,         -- sha256(title+company+desc) for dedup
    UNIQUE (source_id, external_id),
    UNIQUE (content_hash)               -- same offer cross-posted = one row
);

CREATE INDEX idx_offers_scraped ON offers(scraped_at);
CREATE INDEX idx_offers_contract ON offers(contract_type);

-- ============ MATCHING ============

CREATE TABLE profile (
    id INTEGER PRIMARY KEY CHECK (id = 1),  -- singleton row
    full_name TEXT,
    target_roles TEXT,                  -- JSON: ["SOC Analyst","Cloud Security","DevSecOps"]
    hard_skills TEXT,                   -- JSON: ["azure","sentinel","kql","docker","k8s","python"]
    certs TEXT,                         -- JSON: ["AZ-900","SC-200 (in progress)"]
    languages TEXT,                     -- JSON: {"fr":"C2","en":"C1","ar":"native","de":"A2"}
    locations_ok TEXT,                  -- JSON: ["Lille","Paris","Bruxelles","remote"]
    contract_wanted TEXT,               -- JSON: ["alternance","stage"]
    min_duration_months INTEGER,
    embedding BLOB                      -- cached profile embedding
);

CREATE TABLE cv_variants (
    id INTEGER PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,          -- 'soc-analyst', 'cloud-security', ...
    label TEXT NOT NULL,
    keywords TEXT,                      -- JSON, used to pick variant per offer
    template_path TEXT NOT NULL
);

CREATE TABLE match_scores (
    offer_id INTEGER PRIMARY KEY REFERENCES offers(id),
    hard_filter_pass INTEGER NOT NULL,  -- 0/1
    hard_filter_reason TEXT,            -- why rejected, for tuning
    semantic_score REAL,                -- 0..1 embedding similarity
    keyword_score REAL,                 -- 0..1 stack overlap
    bonus_score REAL,                   -- recency, salary, remote bonuses
    final_score REAL,                   -- weighted blend
    best_cv_variant_id INTEGER REFERENCES cv_variants(id),
    scored_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============ APPLICATIONS (state machine) ============

CREATE TABLE applications (
    id INTEGER PRIMARY KEY,
    offer_id INTEGER UNIQUE REFERENCES offers(id),
    company_id INTEGER REFERENCES companies(id),  -- set for cold mail (no offer)
    kind TEXT NOT NULL CHECK (kind IN ('offer','cold')),
    status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN (
        'queued',        -- matched, waiting for your click
        'skipped',       -- you passed
        'generating',    -- CV + lettre being built
        'ready',         -- docs generated, awaiting send/submit
        'applied',       -- sent or form submitted
        'followup_1',    -- J+4 relance sent
        'followup_2',    -- J+10 relance sent
        'replied',
        'interview',
        'offer_received',
        'rejected',
        'ghosted'        -- auto after 21 days no reply
    )),
    cv_pdf_path TEXT,
    letter_pdf_path TEXT,
    contact_email TEXT,
    contact_name TEXT,
    applied_at TEXT,
    last_event_at TEXT NOT NULL DEFAULT (datetime('now')),
    gmail_thread_id TEXT                -- for reply detection
);

CREATE TABLE events (                   -- full audit trail
    id INTEGER PRIMARY KEY,
    application_id INTEGER NOT NULL REFERENCES applications(id),
    event TEXT NOT NULL,                -- 'status_change', 'email_sent', 'reply_detected'
    detail TEXT,                        -- JSON payload
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============ COLD MAIL ============

CREATE TABLE email_queue (
    id INTEGER PRIMARY KEY,
    application_id INTEGER NOT NULL REFERENCES applications(id),
    to_email TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    scheduled_at TEXT NOT NULL,         -- staggered sends
    sent_at TEXT,
    kind TEXT NOT NULL CHECK (kind IN ('initial','followup_1','followup_2'))
);

CREATE INDEX idx_queue_pending ON email_queue(scheduled_at) WHERE sent_at IS NULL;

-- Daily send cap enforcement: count sent_at >= date('now') before dispatching
