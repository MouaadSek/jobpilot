# JobPilot — Codex Handoff (complete A-to-Z)

> Single source of truth for an AI coding agent to continue building JobPilot.
> Created 2026-07-24. Supersedes all previous handoff docs.

---

## 1. PROJECT OVERVIEW

**JobPilot** is a personal job-search automation pipeline for one person:
Mouaad Sekkouri, M1 cybersecurity student at Supinfo Lille, seeking
**alternance** (12-month work-study) and **stage** (3–6 month internship) in
cyber/cloud/IT in France.

The pipeline: **ingest offers → score/rank → human review → auto-tailor CV
(21 variants) → generate motivation letter → draft cold mail → human approves
→ send.**

It runs locally on a MacBook (Intel), is written in Python, costs nothing to
run (local embeddings, no cloud API), and is NOT a spray-and-pray bot — every
application requires explicit human approval before anything is sent.

**This repo must be pushed to GitHub before Codex can work on it.**

---

## 2. WHO IS MOUAAD (the person this pipeline serves)

```yaml
name: Mouaad Sekkouri
email: mouaadsekkourii@gmail.com          # double-i is correct
phone: "+33 7 51 13 54 25"
linkedin: linkedin.com/in/sekkouri
school: M1 Cybersécurité, Supinfo Lille (2025-2026)
next: M2 starts September 2026
current_stage:
  company: Baifall Dream
  role: "Stage : Étude et Développement d'une Plateforme d'e-Facturation"
  location: Paris
  dates: "Juillet 2026 - Present"     # ends 03/09/2026
  note: "Never name the end client. No alternance conversion."
experience: "~2 years Network & Security Support, Concentrix (Netgear)"
certifications: [AZ-900]               # held, verified
languages:
  french: bilingual
  english: C1 Courant                   # NOT C2
  arabic: native
  german: A2
target_contracts: [alternance 12 months, stage 3-6 months]
target_regions: [Hauts-de-France, Île-de-France, remote/télétravail]
target_domains: [cybersecurity, cloud security, IT infrastructure, consulting IT]
machine: MacBook Intel, native macOS    # NOT WSL2
```

---

## 3. CURRENT STATE (what's built and working)

### Phase 1 — COMPLETE (52 tests, ruff clean)

| Component | Status | Location |
|-----------|--------|----------|
| Python skeleton | ✅ | `src/jobpilot/`, pyproject.toml, Typer CLI |
| SQLite + migrations | ✅ | `src/jobpilot/db.py`, `schema.sql`, `migrations/` |
| State machine + audit | ✅ | `src/jobpilot/state.py` — single `transition()` writer, events table |
| France Travail client | ✅ LIVE | `src/jobpilot/sources/france_travail.py` + `oauth.py` |
| ATS pollers | ✅ | Lever/Greenhouse/SmartRecruiters via `config/targets.yaml` |
| Embeddings | ✅ | all-MiniLM-L6-v2, Intel Mac pinned (torch 2.2.2, numpy<2) |
| Matcher/Scorer | ✅ | `matcher.py` (DO NOT MODIFY logic), `scoring.py` |
| Review queue CLI | ✅ | `queue`, `apply`, `skip` commands |
| Scheduler | ✅ | APScheduler (3h cycle) + macOS launchd plist in `deploy/` |
| La Bonne Alternance | ⏸️ PARKED | Coded + tested, but API needs a key (not yet registered) |

### Stage 1 scoring fix — COMPLETE

- `build_profile_text()` rewritten from keyword bag → natural-language paragraph
- Profile headline added via `migrations/001_add_profile_headline.sql`
- Threshold made configurable: `JOBPILOT_QUEUE_THRESHOLD` env var, set to **0.35**
- Blend: 0.50·semantic + 0.35·keyword + 0.15·bonus (in matcher.py, DO NOT CHANGE)
- Result: semantic scores 0.70–0.89 on real cyber offers, 4 offers queued

### Phases 2–9 — COMPLETE (main is at Task 9; 179 tests, ruff clean)

Everything in the original Phase 2–6 roadmap shipped, plus Tasks 7–9. Highlights:

| Component | Status | Notes |
|-----------|--------|-------|
| CV tailoring pipeline | ✅ | `tailoring.py` — variant picker + 5+1 zones, CV/letter PDFs, tracker row |
| Gmail alert ingestion | ✅ | `sources/email_alerts.py` (LinkedIn/Indeed job-alert emails) |
| WTTJ (Algolia) source | ✅ | `sources/wttj.py` |
| Contact discovery + cold-mail drafting | ✅ | `contacts.py` — draft/queue only, no send yet; rails enforced at draft time |
| Local review dashboard | ✅ | FastAPI thin client on 127.0.0.1: status tabs, inline PDF preview, approve/skip/send — commit `ba62fb9` |
| CI pipeline | ✅ | GitHub Actions (ubuntu + windows), ruff + pytest, pip-audit advisory, frozen-matcher PR guard — commit `a2deff0` |
| OpenAI-compatible tailoring advisor | ✅ | providers `auto` / `anthropic` / `openai` / `interactive`; httpx, no SDK; `OPENAI_BASE_URL` enables local Ollama/LM Studio — commit `36e5b22` |
| Letter quality fixes | ✅ | « votre entreprise » fallback, French `de`→`d'` elision, placeholder-rejection validator — Task 9 |
| Email application sending | ✅ | two-step human confirm → SMTP+STARTTLS → `ready`→`applied` + `application_sent` event; shared ≤25/day cap + suppression rails re-checked at send time; `jobpilot send` / `mark-sent` — Task 9 |

### KEY DESIGN DECISIONS (do not undo)

1. **"sent" maps to the existing `applied` status.** No new status was added,
   per the constitution's reuse-the-transition-table rule. A successful send
   logs an `application_sent` event; a failed send stays `ready` and logs
   `send_failed`.
2. **The dashboard is a thin client.** There is no `UPDATE applications SET
   status` in `dashboard.py`, `review.py`, `apply_flow.py`, or `mailer.py`; all
   status changes go through `state.transition()`. `mailer.py` does update the
   `applied_at` timestamp column directly, which is allowed (it is not a status
   write).
3. **Entry-scoped provenance was removed, on purpose (Task 32).** Task 28 judged
   each CV bullet against the facts of the employer or project it sat under, so
   one employer's figures could not appear under another. Task 30 then made
   bullets *selections* of fact ids, inserted verbatim, and the completeness
   check verifies each selected id belongs to its own entry. Cross-entry
   contamination stopped being something prose could express, so the text-level
   check had nothing left to catch and `entry_scope()` had no caller. A guard
   with no caller reads as protection that is not running, so it went. What
   replaced it is `_validate_selection()` in `tailoring.py`. The tier machinery
   survives for the content still generated — the letter and the profile's
   domain phrase — against `whole_bank_scope()`. If entry-level prose ever
   returns, entry scope has to come back with it.

### What is NOT built yet (your job)

**Task 10 — ATS application assist** and Tasks 11–14. See §15 / NEXT ACTION.

---

## 4. REPO STRUCTURE (after GitHub push)

```
jobpilot/
├── src/jobpilot/
│   ├── __init__.py
│   ├── cli.py                    # Typer CLI (incl. send / mark-sent)
│   ├── config.py                 # Settings + get_settings() (env-driven)
│   ├── db.py                     # SQLite layer, migrations runner
│   ├── state.py                  # State machine + transition() + events
│   ├── matcher.py                # ⛔ DO NOT MODIFY LOGIC
│   ├── scoring.py                # build_profile_text(), score_new_offers()
│   ├── tailoring.py              # ✅ variant picker + 5+1 zones + advisors
│   ├── contacts.py               # ✅ contacts + cold-mail drafting + rails
│   ├── mailer.py                 # ✅ two-step email send + shared rails
│   ├── apply_flow.py             # ✅ shared CLI/dashboard approval+generation
│   ├── review.py                 # ✅ read-only queue/status queries
│   ├── dashboard.py              # ✅ FastAPI review dashboard (127.0.0.1)
│   ├── templates/
│   │   └── dashboard.html        # ✅ single server-rendered page
│   └── sources/
│       ├── france_travail.py     # ✅ live; also captures offers.contact_email
│       ├── oauth.py              # FT OAuth client_credentials
│       ├── labonnealternance.py  # ⏸️ parked (needs LBA_API_KEY)
│       ├── ats.py                # Lever/Greenhouse/SmartRecruiters pollers
│       ├── email_alerts.py       # ✅ Gmail LinkedIn/Indeed alert ingestion
│       ├── wttj.py               # ✅ Welcome to the Jungle (Algolia)
│       └── registry.py           # source registry / enable flags
├── schema.sql
├── migrations/
│   ├── 001_add_profile_headline.sql
│   ├── 002_contacts_suppression.sql
│   └── 003_offers_contact_email.sql   # offers.contact_email
├── .github/workflows/
│   └── ci.yml                    # ✅ CI (ubuntu + windows)
├── config/
│   ├── sources.yaml
│   ├── targets.yaml              # ATS employer URLs
│   └── variants.yaml             # 21 CV variant definitions
├── skill/                        # 🔨 COPY HERE from uploaded skill
│   ├── SKILL.md                  # Complete tailoring rules
│   ├── assets/
│   │   ├── cv-templates/         # 21 HTML templates (19 alternance + 2 stage)
│   │   ├── stage-baifall-dream.md
│   │   └── MANIFEST.md
│   └── scripts/
│       ├── generate_cv_pdf.py    # Playwright → PDF
│       ├── generate_letter_pdf.py # WeasyPrint → PDF
│       ├── verify_page_count.py
│       ├── check_orphan_lines.py
│       ├── format_tracker_row.py
│       └── validate_cv.py        # 13-check validator
├── tests/                        # incl. test_dashboard.py, test_mailer.py,
│                                 #   test_letter_quality.py, test_tailoring_openai.py
├── deploy/
│   └── com.jobpilot.scheduler.plist  # macOS launchd
├── data/                         # .gitignore'd — SQLite DB lives here
├── .env                          # .gitignore'd — API keys
├── .env.example
├── pyproject.toml
└── README.md
```

---

## 5. FULL ROADMAP (Phases 2–6)

### Phase 2 — CV PIPELINE INTEGRATION (highest priority)

The job-application skill (`skill/`) contains 21 pre-compliant HTML CV
templates and a complete tailoring ruleset. Integrate it into JobPilot so
that when a user approves an offer from the review queue, the pipeline:

1. **Auto-picks the best CV variant** using the routing table (see §7 below).
   The pick is based on the offer's *mission description*, not the job title.
2. **Tailors the CV** by editing 5 zones (title, profil, tech stack order,
   project order, location) + conditional Zone 6 (Baifall Dream bullet 3 swap).
3. **Generates the CV PDF** via `scripts/generate_cv_pdf.py` (Playwright).
4. **Generates a motivation letter PDF** via `scripts/generate_letter_pdf.py`
   (WeasyPrint) — French, modern tone, 1 page max.
5. **Generates a tracker row** via `scripts/format_tracker_row.py` (18-col TSV).
6. **Queues everything for human review** — the user sees the PDFs and
   approves or requests changes before anything is sent.

**Implementation notes:**
- Tailoring requires an LLM to read the offer description and decide which
  zones to change and how. Use the Anthropic API (Claude Haiku 4.5 for cost:
  $1/$5 per MTok) or allow the user to run tailoring interactively in Claude
  Code (zero cost). Make this configurable.
- The CV templates are self-contained HTML files. Copy the selected template
  to a working directory, apply edits, generate PDF.
- All tailoring rules are in `skill/SKILL.md` — that file is the law. The
  routing table, zone rules, encoding notes, and validation steps are all there.
- After tailoring, run `validate_cv.py` and `check_orphan_lines.py` as quality gates.
- Entity-encoded templates (CloudSec, Consultant IT ×2, GRC) must be edited
  with care — no raw accents in entity-encoded files.

### Phase 3 — GMAIL ALERT INGESTION (reliable, no-scraping source)

LinkedIn and Indeed send job alert emails. Parse them instead of scraping.

Build `src/jobpilot/sources/email_alerts.py`:
- Connect to Gmail via IMAP or Gmail API (user configures credentials).
- Filter for LinkedIn job alert and Indeed job alert sender addresses.
- Extract: job title, company, location, URL to original posting.
- Ingest into `applications` table with `source='linkedin_alert'` or
  `source='indeed_alert'`.
- Dedup on `content_hash` (same SHA-256 approach as France Travail).
- Run scoring on new ingested offers.

This is the **primary** LinkedIn/Indeed channel — reliable, legal, no bans.

### Phase 4 — WTTJ (Welcome to the Jungle)

WTTJ exposes an Algolia-powered JSON search endpoint. Build `sources/wttj.py`:
- Hit the Algolia endpoint with cyber/security/cloud keywords + France filters.
- Parse results (title, company, location, description, URL).
- Ingest + dedup + score.
- WTTJ is high signal for French tech/cyber alternances.

To discover the Algolia endpoint: inspect network requests on
`www.welcometothejungle.com/fr/jobs?refinementList...&query=cybersecurite`.
The XHR calls go to an Algolia `*.algolianet.com` URL with an app ID and
search-only API key visible in the page source. This is a public search
endpoint, not scraping.

### Phase 5 — LINKEDIN + INDEED SCRAPING (high risk, secondary)

> **⚠️ WARNING:** Both LinkedIn and Indeed actively fight scrapers with
> Cloudflare challenges, fingerprinting, IP bans, and legal action. LinkedIn
> has sued multiple scraping companies. This is a SECONDARY source — build
> it, but expect breakage and have the email-alert path (Phase 3) as the
> reliable fallback.

Build `sources/linkedin.py` and `sources/indeed.py`:
- Use Playwright (headless Chromium) with stealth settings.
- Implement rate limiting (max 50 requests/hour), random delays, user-agent
  rotation.
- Handle Cloudflare challenges gracefully (detect, back off, log, don't crash).
- Parse job listings from search results pages.
- Ingest + dedup + score.
- If scraping fails or gets blocked, log a warning and fall back silently —
  the pipeline must not crash.

Search queries: `cybersécurité alternance`, `SOC analyst alternance`,
`cloud security alternance`, `ingénieur sécurité alternance`, filtered to
Hauts-de-France and Île-de-France.

### Phase 6 — CONTACT DISCOVERY + COLD MAIL

Build `src/jobpilot/contacts.py`:

**Contact storage:**
- SQLite table: `contacts(id, application_id, name, role, company, email,
  linkedin_url, source, created_at)`
- Source can be: `manual`, `hunter_api`, `linkedin_search`, etc.

**Discovery interface (pluggable):**
- Default = manual entry (user punches in name + contact info after finding
  them on LinkedIn).
- Future: Hunter.io API, Kaspr, or other enrichment tools behind the same
  interface.
- NO automated people-scraping from LinkedIn profiles.

**Drafting:**
- LinkedIn connection message: ≤300 chars, French, professional, references
  the specific role. Template with merge fields.
- Cold email: French, 5–7 sentences, modern tone (not stiff corporate).
  References the company + role specifically.
- All drafts are queued for human review. Nothing sends without
  `human_approved` event through `state.transition()`.

**Legal rails:**
- Max 25 cold mails per day.
- 4-minute minimum stagger between sends.
- Opt-out link placeholder in every email.
- Suppression list: SQLite table `suppression(email, reason, created_at)`.
  Check before every send.
- Only generic professional email addresses (info@, recrutement@, rh@).
  Never personal emails.

**Sending:**
- SMTP via Gmail (user configures app password) or Resend/Mailgun for
  deliverability.
- Configurable — the module drafts and queues; sending is a separate,
  explicit step.

---

## 6. TECHNICAL CONSTRAINTS

```yaml
python: "3.11"
torch: "2.2.2"                    # Intel Mac ceiling
numpy: "<2"                       # torch 2.2.2 requirement
transformers: "4.45"
sentence-transformers: "3.0"
embedding_model: "all-MiniLM-L6-v2"
playwright: latest                # for CV PDF generation + scraping
weasyprint: latest                # for motivation letter PDF
os: macOS (Intel)                 # NOT Apple Silicon, NOT WSL2
cost: zero/near-zero              # local embeddings, no cloud API for core pipeline
```

**Pin these in pyproject.toml.** Do not upgrade torch past 2.2.2 or numpy to
2.x — they will break on this Intel Mac.

---

## 7. CV VARIANT ROUTING TABLE

The picker reads the offer's **mission description** (not the title) and
selects the best CV variant. Hard rules:

| If missions focus on... | Use template |
|---|---|
| SOC, SIEM, detection, incident response, blue team | SOC |
| Pentesting, red team, offensive security | Pentest |
| GRC, risk analysis, compliance, audit, ISO 27001, EBIOS | GRC |
| IAM, identity governance, Active Directory, access mgmt | IAM |
| Application security, OWASP, SAST/DAST, secure SDLC | AppSec |
| Cloud security, Azure/AWS hardening, CIS benchmarks | CloudSec |
| CI/CD security, DevOps + security, pipeline hardening | DevSecOps |
| Project management + IT/cyber context | Chef de Projet IT |
| Consulting, advisory, digital transformation | Consultant IT |
| Infrastructure, sysadmin, network + security | Infra/Cloud |
| Network engineering, telecom, routing/switching | Réseaux |
| Backend development (Python, Java, APIs) | Backend Dev |
| Full-stack development (front + back) | Fullstack Dev |
| DevOps, SRE, CI/CD (no security focus) | DevOps/SRE |
| IT support, helpdesk, sysadmin | Support IT |
| Data engineering, BI, ETL | Data/BI |
| Machine learning, AI development | IA/ML |
| QA, testing, automation testing | QA Testing |
| General cybersecurity (no specific domain) | Cybersécurité |

**Shortcut rules:**
- Title contains "Consultant" → **always** Consultant IT (no exceptions)
- "Cyber" + PM tasks → Chef de Projet IT
- "Ingénieur sécu" + IAM tasks → IAM
- "Consultant cyber" + audit tasks → GRC
- "DevOps" + CI/CD security → DevSecOps
- "Admin sécu" + infra tasks → Infra/Cloud

**Contract type:**
- Alternance (12 months) → `*__Alternance.html`
- Stage (3–6 months) → `*__Stage.html` if available (only Cybersécurité and
  Consultant IT have stage templates). Otherwise adapt the alternance template
  by changing the title + profil rhythm phrase.

**21 template filenames** (in `skill/assets/cv-templates/`):
```
Mouaad_Sekkouri_-_SOC__Alternance.html
Mouaad_Sekkouri_-_GRC__Alternance.html
Mouaad_Sekkouri_-_DevSecOps__Alternance.html
Mouaad_Sekkouri_-CloudSec__Alternance.html
Mouaad_Sekkouri_-_AppSec__Alternance.html
Mouaad_Sekkouri_-_Cybersecurite__Alternance.html
Mouaad_Sekkouri_-_IAM__Alternance.html
Mouaad_Sekkouri_-_Pentest__Alternance.html
Mouaad_Sekkouri_-_Consultant_IT__Alternance.html
Mouaad_Sekkouri_-_Chef_de_Projet_IT__Alternance.html
Mouaad_Sekkouri_-_Backend_Dev__Alternance.html
Mouaad_Sekkouri_-_Fullstack_Dev__Alternance.html
Mouaad_Sekkouri_-_DevOps_SRE__Alternance.html
Mouaad_Sekkouri_-_Infrastructure_Cloud__Alternance.html
Mouaad_Sekkouri_-_Reseaux_Telecoms__Alternance.html
Mouaad_Sekkouri_-_Data_Engineering_BI__Alternance.html
Mouaad_Sekkouri_-_IA_Machine_Learning__Alternance.html
Mouaad_Sekkouri_-_QA_Testing__Alternance.html
Mouaad_Sekkouri_-_Support_IT_Sysadmin__Alternance.html
Mouaad_Sekkouri_-_Cybersecurite__Stage.html
Mouaad_Sekkouri_-_Consultant_IT__Stage.html
```

**Entity-encoded templates** (use str_replace, never sed):
CloudSec, Consultant IT (both alternance and stage), GRC.

---

## 8. CV TAILORING RULES (5 zones + conditional Zone 6)

When tailoring a CV, copy the selected template to a working directory and
edit ONLY these zones:

### Zone 1: Title (`<div class="job-title">`)
- Match the offer's terminology.
- Include contract type and start date.
- Example: `Analyste SOC - Alternance M2 dès Septembre 2026`

### Zone 2: Profil (`<section class="profile">`)
- Swap ONLY the domain phrase (3–5 words after "Profil orienté").
- Do NOT touch "2 ans en sécurité", the rhythm phrase, or the alternance line.
- Keep total length within ±15 chars of original (~240–250).

### Zone 3: Tech Stack (`<div class="tech-grid">`)
- Reorder rows by relevance to the offer (most relevant first).
- Add 1–2 keywords from the offer if genuinely in Mouaad's skill set.

### Zone 4: Projects
- Reorder the 3 projects by relevance (most relevant first).
- Descriptions are pre-set to fit one line (95–134 chars). Avoid rewriting.

### Zone 5: Location (in contact-info)
- Change to the offer's region only (e.g., "Île-de-France", "Nord").
- Never city + region.

### Zone 6 (conditional): Baifall Dream bullet 3
- If offer mentions ISO 27001/conformité/audit/RSSI → swap to GRC bullet.
- If offer mentions développement sécurisé/SDLC/DevSecOps → swap to DevSecOps bullet.
- If offer mentions cloud souverain/hébergement/SecNumCloud → swap to CloudSec bullet.
- Otherwise: leave the template's default bullet untouched.
- Never edit bullets 1–2 or the stage title/dates.

### What NOT to touch (ever)
- Color (#7bd3e9 — already correct)
- English level (C1 — already correct)
- GitHub (already correct per template)
- Contact CSS, photo (already removed), section titles
- Certifications (already clean — no "en cours")
- Baifall Dream position/title/dates/bullets 1–2
- The removed "Démarrage anticipé" subtitle (never re-add)

---

## 9. MOTIVATION LETTER RULES

Generated via `scripts/generate_letter_pdf.py` (WeasyPrint):

```bash
python3 scripts/generate_letter_pdf.py \
    --cv tailored_cv.html \
    --body letter_body.html \
    --output CompanyName_Lettre_Motivation_Poste.pdf \
    --company "Company Name" \
    --location "City" \
    --date "DD mois YYYY"
```

**Body structure** (`letter_body.html` — paragraphs only, no HTML wrapper):
```html
<p>Madame, Monsieur,</p>
<p>[Opening: why this company + role]</p>
<p>[Optional: Baifall Dream current stage — never name end client]</p>
<p>[Concentrix: 1,500+ incidents, 85% first-contact, 20% MTTR reduction]</p>
<p>[1-2 relevant projects, outcome-first]</p>
<p>[AZ-900 + M1 Cybersécurité at Supinfo]</p>
<p>[Closing: enthusiasm, availability, contract match]</p>
<p>Cordialement,<br/>Mouaad Sekkouri</p>
```

**Rules:**
- Language: match the offer (French default, English if offer is in English)
- Duration: match the offer exactly — never substitute
- Tone: modern, natural, human — not stiff corporate
- No "en cours" certifications
- Max 1 page (script auto-verifies)
- **Never use em dashes** (script has a hard-fail check)
- Letter page width is narrower than CV (170mm vs 190mm)

---

## 10. HARD REJECTIONS (offers the pipeline should auto-skip)

- School/bootcamp requiring re-enrollment (REDSUP-type)
- Non-IT / non-technical roles
- Roles requiring 5+ years experience as CDI
- Level mismatches and non-hiring-manager recruitment paths

Flag once then proceed:
- Academic level mismatch
- Duration incompatibility (e.g., 24 months when Mouaad targets 12)
- Non-ideal role Mouaad explicitly wants to apply to

---

## 11. API REFERENCES

### France Travail (WORKING)
```yaml
auth: OAuth2 client_credentials
token_url: https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=/partenaire
scope: "api_offresdemploiv2 o2dsoffre"
search_url: https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search
env_vars: FRANCE_TRAVAIL_CLIENT_ID, FRANCE_TRAVAIL_CLIENT_SECRET
```

**Hard-won quirks (already handled in code):**
- `typeContrat=STG` → 400 error (FT has NO stage code)
- `motsCles` is AND, not OR → one query per keyword + dedup
- Alternance = `natureContrat=E2,FS`
- `publieeDepuis` ∈ {1, 3, 7, 14, 31} (days)
- Content hash dedup: `sha256(lower(title + company + first 500 chars desc))`
- FT reports communes (Villeneuve-d'Ascq), not regions → location filter
  uses department codes to match HDF/IDF

### WTTJ (TO BUILD)
- Algolia JSON endpoint (public, search-only key visible in page source)
- Inspect XHR on `welcometothejungle.com/fr/jobs?query=cybersecurite`
- Returns structured JSON: title, company, location, description, URL

### La Bonne Alternance (PARKED)
- Old endpoint: DEAD (404)
- New: API Apprentissage at `labonnealternance.apprentissage.beta.gouv.fr`
- Needs account + key from `/espace-developpeurs` — not yet registered
- Env var when ready: `LBA_API_KEY`

---

## 12. DESIGN PRINCIPLES (non-negotiable)

1. **Idempotency**: running any ingest twice must not create duplicates.
2. **Single-writer state machine**: ALL status changes go through
   `state.transition()` + events audit table. No direct SQL updates to
   `applications.status`. Ever.
3. **Human approval required**: nothing sends/submits/applies without
   `human_approved` event. The user reviews every offer, every CV, every
   letter, every cold mail.
4. **Legal rails on cold mail**: ≤25/day, 4-min stagger, opt-out placeholder,
   suppression list, generic pro addresses only.
5. **Intel Mac compatibility**: torch 2.2.2 / numpy<2 pins.
6. **Tests**: maintain or improve the 52-test baseline. `pytest` must pass
   after every change.
7. **Lint**: `ruff check` must be clean after every change.
8. **Schema changes**: through numbered migrations in `migrations/`, not by
   editing `schema.sql` directly.
9. **matcher.py**: DO NOT MODIFY the matching logic or blend weights
   (0.50·semantic + 0.35·keyword + 0.15·bonus). Only the profile text
   builder and threshold are tunable.
10. **Not a spray-and-pray bot.** It's a filter + drafter. Quality over
    quantity.

---

## 13. ENV VARS (.env)

```bash
# France Travail API (required)
FRANCE_TRAVAIL_CLIENT_ID=...
FRANCE_TRAVAIL_CLIENT_SECRET=...

# Scoring threshold (default 0.35)
JOBPILOT_QUEUE_THRESHOLD=0.35

# La Bonne Alternance (parked, add when registered)
# LBA_API_KEY=...

# Gmail (Phase 3 — for email alert ingestion)
# GMAIL_USER=mouaadsekkourii@gmail.com
# GMAIL_APP_PASSWORD=...

# CV tailoring advisor (optional). Provider selects the advice source.
# TAILORING_PROVIDER=auto        # auto | anthropic | openai | interactive
# ANTHROPIC_API_KEY=...
# ANTHROPIC_MODEL=claude-haiku-4-5   # cheapest option: $1/$5 per MTok
# OpenAI-compatible provider (also drives local Ollama / LM Studio via base URL)
# OPENAI_API_KEY=...
# OPENAI_MODEL=...
# OPENAI_BASE_URL=https://api.openai.com/v1   # point at a local server if desired

# SMTP — sending an application by email (jobpilot send / dashboard confirm)
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USERNAME=mouaadsekkourii@gmail.com
# SMTP_PASSWORD=...              # redacted from all logs/errors, like API keys
# SMTP_FROM_NAME=Mouaad Sekkouri
```

**Note:** the France Travail client now captures `offers.contact_email` from the
offer's `contact.courriel` field (migration `003`), which is what the email-send
flow uses as the recipient.

---

## 14. GITHUB PUSH (do this FIRST, before any Codex work)

Run these commands on your Mac:

```bash
cd ~/jobpilot

# Initialize git if not already done
git init
echo "data/" >> .gitignore
echo ".env" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".venv/" >> .gitignore
echo "*.egg-info/" >> .gitignore

# Copy the skill into the repo
cp -r /path/to/job-application-skill skill/

# Copy this handoff doc into the repo
cp /path/to/CODEX-HANDOFF.md .

# Commit everything
git add -A
git commit -m "Initial commit: Phase 1 complete + scoring fix + CV skill"

# Create the GitHub repo and push
gh repo create jobpilot --private --source=. --push
# OR manually:
# git remote add origin git@github.com:YOUR_USERNAME/jobpilot.git
# git push -u origin main
```

Then point Codex at the repo.

---

## 15. CODEX TASK BREAKDOWN (suggested order)

> **NEXT ACTION → Task 10 — ATS application assist (prefill, human submits).**
> The full prompt lives in the roadmap the user holds. Immediate scope:
> non-headless Playwright prefill of Lever / Greenhouse / SmartRecruiters apply
> forms from the profile config, upload `cv.pdf`, then **STOP** — never
> auto-submit, never solve CAPTCHAs, never create accounts. Add a dashboard
> "Ouvrir et pré-remplir" button and a `prefill_launched` event; the fallback
> simply opens the offer URL in the default browser. Tasks 11–14 follow:
> **11** cold-send (actual dispatch of the queued cold emails, staggered, rails
> enforced), **12** reply triage, **13** La Bonne Alternance (gated on
> `LBA_API_KEY`), **14** desktop wrapper.
>
> **PROCESS NOTE — always cut task branches from current `origin/main`.** Do not
> branch from an older commit. Task 9 was branched before Task 8 merged, which
> caused a `config.py` merge conflict (trivially resolved by keeping both the
> `openai_*` and `smtp_*` settings blocks, but entirely avoidable).

**Tasks 1–6 below are DONE** (see §3). Kept for historical context; Tasks 7–9
(dashboard, CI, OpenAI advisor, letter fixes, email send) also shipped.

### Task 1: CV pipeline integration (Phase 2) — ✅ DONE
```
Build the CV tailoring pipeline into JobPilot:
- Add a `tailoring.py` module that implements the variant picker (routing
  table from §7 of CODEX-HANDOFF.md) and the 5+1 zone tailoring engine
  (rules from §8).
- Wire it into the CLI: after `queue` → `apply`, the pipeline should
  auto-pick the variant, tailor the CV, generate the PDF, generate the
  motivation letter PDF, and produce the tracker row.
- Tailoring needs an LLM call to read the offer description and decide zone
  edits. Make this configurable: ANTHROPIC_API_KEY in .env enables auto
  mode (Haiku 4.5), otherwise prompt the user interactively.
- Run validate_cv.py and check_orphan_lines.py as post-tailoring quality gates.
- Add tests for the variant picker (given a mission description, assert
  correct template selection).
- Read skill/SKILL.md for the complete ruleset. It is the law.
```

### Task 2: Gmail alert ingestion (Phase 3) — ✅ DONE
```
Build sources/email_alerts.py:
- Gmail IMAP or API connection (configurable via GMAIL_USER + GMAIL_APP_PASSWORD).
- Parse LinkedIn and Indeed job alert emails.
- Extract: title, company, location, URL.
- Ingest into applications table with source='linkedin_alert' or 'indeed_alert'.
- Dedup on content_hash.
- Score new offers.
- Add tests with sample alert email fixtures.
```

### Task 3: WTTJ source (Phase 4) — ✅ DONE
```
Build sources/wttj.py:
- Discover WTTJ's Algolia endpoint (inspect XHR on their job search page).
- Query with cyber/security/cloud keywords + France location filters.
- Parse JSON results into standard offer format.
- Ingest + dedup + score.
- Add tests.
```

### Task 4: LinkedIn + Indeed scraping (Phase 5) — ⏸️ email-alert path shipped; scrapers deferred
```
Build sources/linkedin.py and sources/indeed.py:
- Playwright headless Chromium with stealth settings.
- Rate limiting: max 50 req/hour, random delays 3-8s between requests.
- User-agent rotation.
- Cloudflare challenge detection: detect, back off exponentially, log warning.
- Parse job listings from search result pages.
- Ingest + dedup + score.
- Graceful degradation: if blocked, log and continue (pipeline must not crash).
- Add tests with mocked HTML fixtures.
⚠️ This WILL break periodically. The email alert path (Phase 3) is the
reliable fallback. Both should be active simultaneously.
```

### Task 5: Contact discovery + cold mail (Phase 6) — ✅ DONE (drafting; actual send is Task 11)
```
Build contacts.py:
- Contact SQLite table + CRUD.
- Pluggable discovery interface (manual entry default).
- LinkedIn message drafter (≤300 chars, French).
- Cold email drafter (5-7 sentences, French, modern tone).
- Suppression list table + check.
- Rate limiter: 25/day, 4-min stagger.
- SMTP sender (configurable, opt-out placeholder).
- ALL drafts queued for human_approved event before send.
- Add tests.
```

### Task 6: CI + hardening — ✅ DONE
```
- GitHub Actions CI: pytest + ruff on every PR.
- Error handling: retry with backoff on API failures.
- Logging: structured logging to file + console.
- README.md: setup guide, usage, architecture diagram.
```

---

## 16. BAIFALL DREAM STAGE REFERENCE

The current stage entry appears in ALL 21 CV templates as the FIRST item in
"Expérience Professionnelle":

- **Bullet 1** (common, accomplished): cahier des charges, 95 exigences
- **Bullet 2** (common, nominal scope): dev platform Factur-X/UBL, data model, API
- **Bullet 3** (varies by template): see `skill/assets/stage-baifall-dream.md`
- Backend/Fullstack: only 2 bullets (bullet 2 covers dev)

**Zone 6 swap rules** (during tailoring):
- ISO 27001/conformité/audit → GRC bullet
- Développement sécurisé/SDLC/DevSecOps → DevSecOps bullet
- Cloud souverain/SecNumCloud → CloudSec bullet
- Default: leave template's bullet untouched

**Date rule**: "Juillet 2026 - Present" until 03/09/2026, then past tense.
Never name the end client. Never write "Stage puis Alternance."

---

## 17. SCRIPTS REFERENCE

| Script | Input | Output | When |
|--------|-------|--------|------|
| `generate_cv_pdf.py <html> <pdf>` | Tailored HTML | A4 PDF | After tailoring |
| `generate_letter_pdf.py --cv --body --output --company --location --date` | CV HTML + body HTML | Letter PDF | After CV |
| `verify_page_count.py <pdf>` | Any PDF | Pass/fail | After any PDF |
| `check_orphan_lines.py <html>` | Any CV HTML | Pass/fail | After text edits |
| `format_tracker_row.py --entreprise --poste ...` | Offer metadata | 18-col TSV | After approval |
| `validate_cv.py <html> [--original <base>]` | Tailored HTML | 13 checks | Safety net |

**Dependencies:** Playwright (CV PDFs + orphan check + scraping), WeasyPrint
(letter PDFs), pypdf/PyPDF2 (page count).

---

## 18. KNOWN ISSUES / RISKS

1. **LinkedIn/Indeed scraping WILL break.** Both sites actively fight bots.
   Budget for maintenance. Email alerts are the reliable fallback.
2. **Keyword score stays ~0** because French job postings use different
   terminology than the profile keywords. The semantic score compensates.
   The blend weights in matcher.py are calibrated for this — don't change them.
3. **La Bonne Alternance** is parked until Mouaad registers for an API key.
   Don't build it yet.
4. **Entity-encoded templates** (4 of 21) require special handling — never
   use `sed` on them, always programmatic string replacement.
5. **Intel Mac**: no Apple Silicon optimizations. torch 2.2.2 is the ceiling.
   numpy must stay <2. Don't upgrade these.
6. **Playwright on macOS**: may need `npx playwright install chromium` after
   fresh install.
