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
| `TAILORING_PROVIDER` | `auto` (default), `anthropic`, `openai`, or `interactive` |
| `ANTHROPIC_API_KEY` | Anthropic tailoring credential |
| `ANTHROPIC_MODEL` | Override the pinned Claude Haiku 4.5 model |
| `OPENAI_API_KEY` | OpenAI or OpenAI-compatible tailoring credential |
| `OPENAI_MODEL` | Model name (default `gpt-5.4-mini`) |
| `OPENAI_BASE_URL` | Chat Completions API base (default `https://api.openai.com/v1`) |
| `APPLICANT_FULL_NAME` / `APPLICANT_EMAIL` / `APPLICANT_PHONE` / `APPLICANT_LINKEDIN_URL` | Contact details used only to prefill visible ATS forms |
| `WTTJ_AUTO_SUBMIT_ENABLED` | WTTJ inline apply gate: `false` (default) is fill/upload-only dry run; `true` explicitly enables live submission |

Which sources run is controlled by `config/sources.yaml`; ATS targets by
`config/targets.yaml`; CV variants by `config/variants.yaml`.

## LLM providers

CV tailoring supports three modes through `TAILORING_PROVIDER`:

- `anthropic` uses `ANTHROPIC_API_KEY`.
- `openai` uses `OPENAI_API_KEY`, `OPENAI_MODEL`, and `OPENAI_BASE_URL`.
- `interactive` prompts in the terminal and ignores configured API keys.

The default `auto` mode tries Anthropic first, then OpenAI, then interactive
prompts. Choosing `anthropic` or `openai` explicitly without its API key fails
with a clear configuration error instead of silently falling back.

`OPENAI_BASE_URL` may point to any compatible hosted or local Chat Completions
endpoint, including Ollama or LM Studio. **Google Gemini is a supported
configuration** through its OpenAI-compatible endpoint:

```bash
TAILORING_PROVIDER=openai
OPENAI_API_KEY=<your Gemini API key>
OPENAI_MODEL=gemini-2.5-flash
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
```

Every provider feeds the same guarded tailoring and document-validation
pipeline; nothing is auto-sent or submitted.

Responses are normalized before validation: when a model returns the sourced
structure (`experience_content`, `project_content`, `skill_order`,
`letter_paragraphs`) **and** the legacy fields it supersedes (`tech_keywords`,
`letter_body_html`), the sourced structure wins and the redundant fields are
dropped with a debug log line instead of failing the run. Normalization is
shape-only — provenance, structural completeness, and locked-field rules still
apply in full to the sourced content.

### CV variant selection

Choosing **which** of the 21 CVs to use is a judgement call, so the advisor makes
it, mirroring the skill's "Step 1 — CV Selection" then tailoring flow. It is a
separate, small request: offer text plus the catalogue, answered with a chosen
`slug`, a one-sentence `justification`, and a `runner_up`. All three are
required, and a slug outside the catalogue is rejected and rides the same
one-retry validation-feedback path as tailoring. Budget one extra call per
generation.

**`skill/SKILL.md` remains the source of truth for the selection criteria.** The
catalogue is parsed out of its "Step 1 — CV Selection" table and its shortcut
list at load time and combined with the slugs and labels in
`config/variants.yaml`; nothing is paraphrased into a second copy, and a
mismatch between the two files is a loud error rather than a silent drift.

These stay mechanical, applied in code after the model's pick: stage vs
alternance resolution and the dedicated stage templates, the adapted-for-stage
fallback, entity-encoded template handling, and template file existence.

Keyword routing (`matcher`-style signal scoring in `tailoring._route_slug`) is
**not** deleted — it still runs, as a sanity check and as the fallback. If the
selection call fails after its retry, the provider errors, the catalogue cannot
be loaded, the chosen template file is missing, or an interactive human declines
to choose, generation continues with the keyword pick and records that it was a
fallback. A selection failure never blocks a generation.

### Validation-feedback retry

Models tend to miss one mechanical rule at a time, and every rejection used to
cost a human approve click. When a generated plan is rejected by the validator,
the API advisors (`anthropic`, `openai`) are re-called **exactly once** with the
validator's error appended to the prompt and an instruction to fix only that.
Budget for up to two calls per generation.

- Interactive mode never retries: a person is already reading the error.
- Transport, auth, rate-limit, and malformed-response failures are never
  retried, so a 429 does not turn into a retry storm.
- The retry feeds back the error text and nothing else. It relaxes no rule; the
  second answer faces the same provenance, completeness, and locked-field checks
  as the first.
- If the retry is also rejected, the run fails exactly as before — rollback to
  `queued` plus a `generation_failed` event, which now records both attempts'
  errors under `attempts`.

### Fact bank

`config/fact_bank.yaml` is the reviewable source of truth for every factual
claim the tailoring model may use. It records stable fact ids, locked identity
and career fields, and an explicit verified/unverified state for skills. Review
it at any time with `jobpilot facts`; entries marked `needs_review` stay visible
instead of being guessed. Posting titles are normalized before rendering so
gender markers, reference codes, locations, and marketing noise do not reach the CV.

All three advisor modes now use the same sourced-content JSON contract. The
advisor may rewrite and reorder experience/project content and lead with the
most relevant verified skills, but every generated bullet and letter paragraph
cites stable fact ids. The shared validator rejects unknown/review-pending ids,
unverified skills, unsupported numbers, and unsupported proper nouns before any
PDF is generated. Identity, contact details, employers, dates, diplomas, and
certification names remain renderer-owned and cannot be supplied by the model.

### Structural completeness floor

Provenance stops fabrication; a second set of rules stops omission. A generated
CV is rejected (rollback to `queued` plus a `generation_failed` event) unless:

- every employer in the fact bank appears, in reverse-chronological order by
  start date, with at least 2 bullets for the two most recent employers and at
  least 1 for each older one;
- exactly 3 projects are selected;
- no tool is listed under two skill categories;
- the header location is a real region, never a bare country.

The model still chooses which bullets represent an employer, how they read,
which 3 projects to show, and how the letter is written. It no longer chooses
whether an employer appears. The header location is renderer-owned: it uses the
offer's region and falls back to `config/profile.yaml` (city + region) instead of
a bare country. The tracker row's variant and project columns are derived from
the validated document, not from the pre-generation routing guess, which is
recorded as `routing_variant` in the status-change event detail.

## Sources

Each source below is fully coded and unit-tested; it just needs a credential and
then works via `jobpilot ingest`. Until then it is skipped with a clear message.

- **Gmail alerts (LinkedIn + Indeed)** — set `GMAIL_ADDRESS` and
  `GMAIL_APP_PASSWORD` in `.env` (enable IMAP, create an App Password at
  <https://myaccount.google.com/apppasswords>, requires 2FA). Run
  `jobpilot ingest -s linkedin_alert` and
  `jobpilot ingest -s indeed_alert`, or let the scheduler run both. IMAP uses
  `BODY.PEEK[]` against a read-only folder: messages are never moved, deleted,
  or marked read. Optional `IMAP_HOST`, `IMAP_PORT`, `IMAP_FOLDER`, and
  `EMAIL_ALERT_SINCE_DAYS` settings tune the transport and lookback. Extracted
  links are canonicalized without tracking parameters, and repeated alerts are
  deduplicated through the normal offer-ingestion path. We never scrape
  LinkedIn or Indeed pages.

  Senders are matched by **domain**, not by exact address: any address on
  `linkedin.com` / `indeed.com` / `indeedemail.com` or a subdomain of those
  (`fr.indeed.com`, `e.linkedin.com`) is accepted, matched on domain boundaries
  so lookalikes such as `indeed.evil.com` or `notlinkedin.com` are not. Non-job
  mail from those domains simply yields no entries and is skipped with a
  warning.

  Alerts carry a title, company and location but effectively no description, and
  `matcher.py` builds its matching text from `title + description`. Offers whose
  description is shorter than `ALERT_MIN_DESCRIPTION_CHARS` (default 120) get one
  composed from the fields the alert did provide. This is field assembly, not
  generation: no LLM call, no scraping, and nothing that was not in the alert.
  Composed descriptions are prefixed `[synthèse-alerte]` so they stay
  recognizable, which needs no schema change.
- **Welcome to the Jungle** — set `WTTJ_API_KEY` (the public Algolia search key;
  open WTTJ job search with devtools Network open and copy the `X-Algolia-API-Key`
  header from the `*-dsn.algolia.net` request), then run
  `jobpilot ingest -s wttj`. App id/index keep their existing
  `WTTJ_APP_ID` / `WTTJ_INDEX` overrides. `WTTJ_MAX_PAGES` defaults to five
  pages per query. The tunable query block targets alternance and stage roles
  across cyber, cloud, DevSecOps, and IT infrastructure in Hauts-de-France,
  Île-de-France, or remote.
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
jobpilot backfill-descriptions -s linkedin_alert   # compose descriptions for thin stored offers
jobpilot backfill-descriptions -s linkedin_alert --force  # re-compose already-synthesised text from current fields
jobpilot reparse-alerts -s linkedin_alert          # re-derive company/city/workplace from stored card text
jobpilot rescore -s linkedin_alert                 # clear match_scores so `score` re-evaluates
jobpilot queue                   # list queued applications, highest score first
jobpilot apply <id>              # approve offer, tailor docs, queue them for human review
jobpilot skip <id>               # pass: queued -> skipped
jobpilot send <id>               # show the email for a ready app, confirm (y/N), send
jobpilot mark-sent <id>          # record an externally-submitted app as sent (ready -> applied)
jobpilot dashboard --port 8787   # local review UI on 127.0.0.1
jobpilot stats                   # snapshot: offers, companies, by-contract, applications
jobpilot facts                   # review all allowed claims and locked fields
jobpilot daemon --interval-hours 3   # loop ingest + score (Ctrl-C to stop)

# Cold outreach (draft here; final confirmation is in the local dashboard)
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

**Rescoring stored offers.** `backfill-descriptions` composes descriptions for
offers already in the database whose text is too thin to embed; `rescore` then
drops their `match_scores` rows so the next `jobpilot score` re-evaluates them.
Both take an optional `--source`, both are idempotent, and neither touches the
blend, the threshold, or any `applications` row — `rescore` leaves the scores of
offers that already have an application alone, and so does any backfill that
rewrites existing text (`--force`, below). Measured on the 112 stored `linkedin_alert`
offers, backfill + rescore + score lifted the mean semantic score of the
scoreable ones from 0.143 to 0.207 and the mean final from 0.075 to 0.107,
turning a flat near-zero cluster into a usable ranking.

**`backfill-descriptions --force`** re-composes offers that already carry the
`[synthèse-alerte]` marker. A synthesised paragraph quotes the field values as
they stood when it was written, so the rows synthesised before `reparse-alerts`
fixed `company` / `city` still read `Lieu : Recrutement actif.` — and that text
is what the semantic score embeds. The plain backfill skips them (they carry the
marker and are no longer thin), so nothing repairs them without this flag.
Forcing rebuilds the paragraph from the row's *current* title, company and city;
it deliberately does not re-quote the stored paragraph, whose tail is the old
scaffolding and the values being replaced. It is still field assembly — no LLM,
no scraping, nothing invented. Offers that already have an application are
skipped, a row whose fields no longer carry a title keeps its stored text
(counted as `skipped_degraded`), and a second run rewrites nothing. Measured on
a copy of the live database, over the 112 stored `linkedin_alert` offers (111
regenerated, 1 skipped for its application), mean semantic among the 67 that
reach scoring went 0.284 → 0.295, mean final 0.169 → 0.175, median final
0.189 → 0.203, and offers at or above a 0.30 final went 6 → 10. No offer crossed
the 0.35 queue threshold that did not already. Run `rescore` then `score`
afterwards.

**Alert card fields.** LinkedIn and Indeed alert cards read
`Company · City (Workplace)`, where the workplace is `Sur site` / `Hybride` /
`À distance` (or their English equivalents) and maps onto the same
`onsite` / `hybrid` / `full_remote` vocabulary every other source writes. The
parser splits that line structurally and refuses to store interface text —
`Recrutement actif`, `N relation(s)`, `N anciens collègues`, `Candidature
simplifiée`, `Promu`, bare gender markers (`F/H`), salary lines — in `company`,
`city` or `title`. A field it cannot read stays `NULL`, which the hard filter
treats as "unknown location, do not reject"; a wrong value would guarantee
rejection. Nothing is inferred: no city is guessed from a company name, no
region from a city, no workplace type from anything.

`Candidature simplifiée` / `Easy Apply` is kept rather than discarded, as
`offers.easy_apply` (migration `004`), because it marks the offers that support
LinkedIn's inline application flow.

**`reparse-alerts`** repairs offers ingested before that fix. The raw alert
emails are not stored, but the card text survives in the fields the old parser
mis-filed, which is enough to re-run the parse offline. Offers with no card text
left are reported as unrecoverable and have the junk cleared to `NULL` rather
than guessed — re-run `jobpilot ingest -s linkedin_alert` to recover those from
the mailbox. Like `rescore`, it is idempotent, takes an optional `--source`, and
skips any offer that already has an application; it never touches
`applications`, statuses or events. Measured on the 112 stored `linkedin_alert`
offers, it cut hard-filter rejections on location from **85 to 45** and raised
the offers reaching scoring from **27 to 67**. Run `rescore` then `score`
afterwards to re-evaluate them.

**Cold-mail rails** are enforced when drafting and rechecked immediately before
SMTP dispatch: one shared maximum of 25 application/cold emails per UTC day,
at least four minutes between cold sends, suppression-list refusal,
professional-domain recipients only, mandatory opt-out text, and an extra
confirmation for named professional mailboxes. **Nothing sends without a prior
`human_approved` event.**

## Dashboard

Launch the daily review UI on macOS or Linux:

```bash
jobpilot dashboard --port 8787
```

On Windows PowerShell, the installed command is the same; without an activated
virtual environment, run it directly:

```powershell
.venv\Scripts\jobpilot.exe dashboard --port 8787
```

Then open <http://127.0.0.1:8787>. The status chips at the top are clickable
tabs (queued / generating / ready / applied / skipped) that filter the table to
each status; the queue is the default view. The dashboard shows offer and event
details and lets you approve or skip through the same state-machine paths as the
CLI. Approval generates the CV, motivation letter, and tracker row synchronously
for local review. The server always binds to loopback only.

### Actualiser les offres (refresh from the page)

The queue page carries an **Actualiser les offres** button that runs the same
ingest and scoring functions as `jobpilot ingest` and `jobpilot score`, in a
background thread, so the terminal is not needed for the daily loop. The request
returns immediately and the page polls `/refresh/status`.

Only one refresh runs at a time: while it is in flight the button is disabled and
a second `POST /refresh` returns `409` instead of starting a parallel run (SQLite
has a single writer). Progress is reported per source — fetched / inserted /
duplicates, or the skip reason such as missing credentials — and a failing source
is shown as failed without hiding the others' results. Scoring runs after
ingestion and reports how many offers were newly queued. The first refresh of a
process is slow because the embedding model loads lazily, exactly as on the CLI
path; the page shows **Chargement du modèle…** while that happens.

### Fact bank and scheduler status

**Faits** in the header opens `/facts`, a read-only rendering of the fact bank
with the same content and grouping as `jobpilot facts`: experience with its
claims, projects, education, certifications, languages, skills with their
verified flags, and the locked identity block. Editing stays in
`config/fact_bank.yaml`; the page submits nothing.

The queue page also carries a **Planification** panel: the last run time
recorded in `sources.last_run_at` for every enabled source, and the daemon's
state. Only the run time is stored, so the per-cycle result is reported as
`inconnu (non enregistré)` rather than invented. Each completed daemon cycle
writes `logs/scheduler.heartbeat`; the panel reports `actif` while beats are
within two cycle intervals, `inactif` once they are older, and `inconnu` when no
readable heartbeat exists at all.

### Tailoring mode and web approval

The dashboard header shows the tailoring mode resolved from `.env`
(`anthropic` / `openai` / `interactive`), so it is visible at a glance whether
headless tailoring is configured.

**Approve** in the browser never falls back to terminal prompts. If the resolved
mode is `interactive` — typically because no API key is set — the approval is
refused before anything is recorded: the detail page explains that
`OPENAI_API_KEY` or `ANTHROPIC_API_KEY` is required, the status stays `queued`,
and no `human_approved` event is written for an approval that could not proceed.
Interactive tailoring remains available on the CLI with `jobpilot apply`, which
is unchanged.

### Cold outreach sending (disabled by default)

The dashboard's **Outreach** tab lists unsent cold-email drafts. Selecting one
opens a separate confirmation page showing the exact recipient, subject,
editable body, scheduled time, and mandatory French opt-out footer. A named
professional mailbox such as `jean.dupont@company.fr` also requires its own
explicit checkbox. The separate **Confirmer et envoyer** action records human
approval through the existing application flow, rechecks every legal rail, and
only then may call the existing STARTTLS SMTP sender.

Live cold dispatch is protected by this release gate:

```dotenv
COLD_SEND_ENABLED=false
```

Keep it `false` until the owner has explicitly signed off. The Outreach list,
confirmation page, editing, and validation remain available, but final sending
returns a clear disabled message and SMTP is never called. After sign-off,
setting it to `true` enables confirmed sends. Successful sends record
`cold_mail_sent`; blocked or failed attempts record `cold_send_failed`, including
recipient and subject. Suppression can be added at any time with
`jobpilot suppress <email>`.

### Sending an application by email

A `ready` application whose offer carries a contact email can be sent from the
dashboard in two explicit steps: **Préparer l'envoi par email** opens a
confirmation page showing the recipient, subject, the two PDF attachments, and an
editable message body; **Confirmer et envoyer** performs the SMTP send (STARTTLS,
`cv.pdf` + `motivation_letter.pdf` attached), transitions `ready -> applied`, and
logs an `application_sent` event. The CLI equivalent is `jobpilot send <id>`.

Sending shares the cold-mail rails: the global ≤25 sends/day counter
(applications + cold mail combined) and the suppression list are checked first,
and a blocked send is refused with an explanation while the application stays
`ready`. For offers without a contact email, **Marquer comme envoyée**
(`jobpilot mark-sent <id>`) records an externally-submitted application in the
same funnel. Configure SMTP via `SMTP_USERNAME` / `SMTP_PASSWORD` (Gmail app
password); the password is redacted from all logs and errors.

### ATS application assist (prefill only)

For `ready` offers originating from the configured Lever, Greenhouse, or
SmartRecruiters pollers, the dashboard shows **Ouvrir et pré-remplir**. Set all
four `APPLICANT_*` values in `.env` first. The action opens a **visible**
Playwright Chromium window, fills best-effort name, email, phone, LinkedIn,
and CV fields, and adds the motivation letter only where the ATS exposes a
cover-letter upload field.

JobPilot never clicks a final submit/apply/send control, handles a CAPTCHA,
creates an account, or enters a password. The browser remains for the human to
review and manually submit or abandon. If the ATS is unknown, selectors have
changed, files are unavailable, or Playwright fails, the dashboard safely opens
the apply URL in the default browser and records an `apply_url_opened` audit
event. Missing `APPLICANT_*` settings are shown as a clear setup error instead.
A successful prefill records `prefill_launched`; neither event changes
application status. After personally submitting the application, use **Marquer
comme envoyée** to record the existing `ready → applied` transition.

### WTTJ inline application (dry-run by default)

For a `ready` WTTJ offer with generated documents, the dashboard can open the
inline application form in a visible browser, fill the applicant details, and
upload the CV and motivation letter. The default configuration is deliberately
safe:

```dotenv
WTTJ_AUTO_SUBMIT_ENABLED=false
```

In this dry-run mode, JobPilot fills and uploads, saves
`output/applications/<id>/wttj_apply.png` for review, and records
`apply_dry_run`, but it never clicks the final submit control and leaves the
application `ready`.

Set `WTTJ_AUTO_SUBMIT_ENABLED=true` only after explicitly opting into live
submission. Live mode still requires the dashboard's human-approved action and
aborts without submitting if it detects a CAPTCHA, an unmapped required field,
an offer mismatch, or a missing required document. A confirmed submission
records `application_submitted` and transitions `ready → applied`; if WTTJ
does not expose a verifiable confirmation, JobPilot records
`submit_unconfirmed` and leaves the application `ready`. Blocked attempts fall
back to opening the offer URL for manual completion.

> Screenshot placeholder: review queue and generated-document detail view.

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

### CI

GitHub Actions runs the lightweight test suite and Ruff on Python 3.11 for
Ubuntu and Windows. CI installs only the explicit non-ML dependencies, guards
the frozen matcher on pull requests, and runs an advisory dependency audit on
Ubuntu.
