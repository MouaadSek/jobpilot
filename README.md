# JobPilot

Personal job application pipeline for the French IT/cybersecurity market.
Single user, local-only, SQLite. See `CLAUDE.md` for the project constitution
(architecture rules, engineering standards, legal/safety rails).

> **Status:** Built and validated — France Travail ingestion, ATS pollers,
> embeddings + scoring (natural-language profile text), review queue, scheduler,
> cold-outreach drafting (contacts, suppression, rate-limit), LinkedIn/Indeed
> **email-alert** ingestion (no scraping), and WTTJ (Algolia). Sources needing a
> credential (La Bonne Alternance, Gmail alerts, WTTJ) are wired and unit-tested
> but skip gracefully until their key is set — see Pending setup.

## Requirements

- Python 3.11
- Windows 10/11 with PowerShell 5.1+, macOS, or Linux

## Setup

### macOS / Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m playwright install chromium

cp .env.example .env       # then fill in credentials
jobpilot init-db
```

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m playwright install chromium

Copy-Item .env.example .env  # then fill in credentials
jobpilot init-db
```

If PowerShell execution policy blocks activation, run the executables directly:
`.venv\Scripts\python.exe -m pip install -e ".[dev]"` and
`.venv\Scripts\jobpilot.exe init-db`.

On Windows, motivation letters render through the installed Playwright Chromium
runtime, so GTK/Pango is not required. Other platforms use WeasyPrint.

The first install downloads the `all-MiniLM-L6-v2` sentence-transformers model
(~90 MB) and caches it under `~/.cache/huggingface`.

## Configuration

All secrets live in `.env` (gitignored); `.env.example` documents every key.

| Key | Purpose |
| --- | --- |
| `FRANCE_TRAVAIL_CLIENT_ID` / `FRANCE_TRAVAIL_CLIENT_SECRET` | France Travail "Offres v2" OAuth2 credentials |
| `FRANCE_TRAVAIL_PUBLISHED_SINCE` | Recency window in days: 1, 3, 7, 14, or 31 (default 31, for backfill) |
| `LBA_API_KEY` | API Apprentissage Bearer token for La Bonne Alternance (see Pending setup) |
| `JOBPILOT_DB` | Override the SQLite path (default `data/jobpilot.db`) |
| `JOBPILOT_LOG_DIR` | Override the log directory (default `logs/`) |
| `JOBPILOT_EMBED_MODEL` | Override the embedding model |
| `JOBPILOT_OUTPUT_DIR` | Tailored HTML/PDF/tracker output (default `output/applications`) |
| `ANTHROPIC_API_KEY` | Enables automatic CV tailoring; absent means interactive mode |
| `ANTHROPIC_MODEL` | Override the pinned Claude Haiku 4.5 model |

Which sources run is controlled by `config/sources.yaml`; ATS targets by
`config/targets.yaml`; CV variants by `config/variants.yaml`.

## Pending setup

Each source below is fully coded and unit-tested; it just needs a credential and
then works via `jobpilot ingest`. Until then it is skipped with a clear message.

- **Gmail alerts (LinkedIn + Indeed)** — set `GMAIL_ADDRESS` and
  `GMAIL_APP_PASSWORD` in `.env` (enable IMAP, create an App Password at
  <https://myaccount.google.com/apppasswords>, requires 2FA). We parse the
  job-alert emails read-only; we never scrape LinkedIn/Indeed. The HTML parsers
  are fixture-tested; their company/location selectors should be confirmed
  against a real forwarded alert.
- **Welcome to the Jungle** — set `WTTJ_API_KEY` (the public Algolia search key;
  open WTTJ job search with devtools Network open and copy the `X-Algolia-API-Key`
  header from the `*-dsn.algolia.net` request). App id/index default but are
  overridable via `WTTJ_APP_ID` / `WTTJ_INDEX`.
- **La Bonne Alternance** — the legacy public API (caller-email auth) was
  decommissioned; the current **API Apprentissage** requires an account plus a
  token. Register and generate a key at
  <https://labonnealternance.apprentissage.beta.gouv.fr/espace-developpeurs>,
  then set `LBA_API_KEY` in `.env` and flip `labonnealternance.enabled: true` in
  `config/sources.yaml`.

## Commands

```bash
jobpilot init-db                 # create schema.sql tables, run migrations, seed sources
jobpilot init-profile            # interactively fill profile + seed cv_variants, cache embedding
jobpilot ingest --source all     # fetch offers from every enabled source
jobpilot ingest -s france_travail --since 7
jobpilot score                   # score unscored offers; queue those above threshold
jobpilot queue                   # list queued applications, highest score first
jobpilot apply <id>              # approve offer, tailor docs, queue them for human review
jobpilot skip <id>               # pass: queued -> skipped
jobpilot stats                   # snapshot: offers, companies, by-contract, applications
jobpilot daemon --interval-hours 3   # loop ingest + score (Ctrl-C to stop)

# Cold outreach (drafting only; nothing sends without `apply`)
jobpilot add-contact --company "ACME" --name "Jean Dupont" --role RSSI --email rh@acme.fr
jobpilot contacts --company "ACME"
jobpilot draft-cold --company "ACME" --role "analyste SOC" --contact 1
jobpilot suppress someone@acme.fr --reason "opted out"
```

**Scoring note:** `matcher` blends `0.50·semantic + 0.35·keyword + 0.15·bonus`.
French postings rarely name specific tools, so keyword stays low and finals for
strong matches cap around 0.45–0.50. The queue threshold is therefore
`JOBPILOT_QUEUE_THRESHOLD` (default **0.35**), applied at runtime without editing
`matcher.py`.

**Cold-mail rails** (in `contacts.py`, enforced at draft/queue time): max 25/day,
≥4 min stagger, suppression list honored, professional addresses only (no free
providers), mandatory opt-out line. Drafts queue in `email_queue` (email) and as
`linkedin_draft` events; **nothing sends without a prior `human_approved` event**
(recorded by `jobpilot apply`).

## Background scheduling

On macOS, edit the paths in `deploy/com.jobpilot.daemon.plist`, copy it to
`~/Library/LaunchAgents/`, then run `launchctl load` on the copied plist.

On Windows, register the current-user scheduled task from PowerShell:

```powershell
.\deploy\install-windows-task.ps1
Start-ScheduledTask -TaskName "JobPilot Daemon" -TaskPath "\"
Get-ScheduledTask -TaskName "JobPilot Daemon" -TaskPath "\"
```

The task uses the current user's interactive token: it stores no password or
API keys, loads the gitignored `.env` at runtime, writes normal JobPilot logs,
and runs only while that user is signed in. Replace its interval with
`.\deploy\install-windows-task.ps1 -IntervalHours 6 -Replace`.

Stop it with `Stop-ScheduledTask -TaskName "JobPilot Daemon" -TaskPath "\"`,
then remove only that scheduled task with:

```powershell
.\deploy\uninstall-windows-task.ps1
```

## Architecture (summary)

- `schema.sql` — source of truth for the data model. Changes go in `migrations/`.
- `matcher.py` — scoring engine. Imported and driven, never modified.
- `src/jobpilot/state.py:transition` — the **only** writer of `applications.status`;
  validates legality and logs to the `events` audit table.
- `src/jobpilot/sources/base.py:Source` — the interface every ingestion source
  implements, so sources are pluggable and mockable.
- Ingestion is idempotent: offers dedup on `content_hash` and
  `(source_id, external_id)` via `INSERT OR IGNORE`.

## Development

```bash
pytest        # in-memory SQLite for all DB tests
ruff check .
```
