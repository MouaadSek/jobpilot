# JobPilot

Personal job application pipeline for the French IT/cybersecurity market.
Single user, local-only, SQLite. See `CLAUDE.md` for the project constitution
(architecture rules, engineering standards, legal/safety rails).

> **Status:** Built and validated — France Travail ingestion, ATS pollers,
> embeddings + scoring (natural-language profile text), review queue, scheduler,
> cold-outreach drafting (contacts, suppression, rate-limit), LinkedIn/Indeed
> **email-alert** ingestion (no scraping), WTTJ (Algolia), and La Bonne
> Alternance through the API Apprentissage (offers plus likely-to-hire companies
> as outreach targets). Sources needing a credential (Gmail alerts, WTTJ) are
> wired and unit-tested but skip gracefully until their key is set — see Pending
> setup.

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
| `LBA_API_KEY` | API Apprentissage Bearer token for La Bonne Alternance |
| `LBA_MAX_PAGES` | Cap on search calls per ingest run (default 5; see below) |
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

Both picks are always computed, and the disagreement is surfaced rather than
swallowed. Every `ready` status-change event records `routing_variant` (the
keyword suggestion), `document_variant` (the CV actually produced),
`variant_selected_by`, `routing_agreed`, plus `routing_justification` and
`routing_runner_up` from the model, and `routing_fallback_reason` when the
keyword pick was used. A disagreement is also logged at INFO with both slugs and
the justification. The application detail page shows the chosen variant, the
justification, the runner-up, and — when they differ — what the keyword router
would have picked instead; `jobpilot apply` prints the same summary.

That record is the measurement: it is what will tell us whether the keyword layer
is worth keeping. Its signal tables (`_PM_SIGNALS`, `_ROUTE_SIGNALS`,
`_ROUTE_PRIORITY`) are deliberately left untuned so the two changes are not
confounded.

### Validation-feedback retry

Models tend to miss one mechanical rule at a time, and every rejection used to
cost a human approve click. When a generated plan is rejected by the validator,
the API advisors (`anthropic`, `openai`) are re-called **exactly once** with the
validator's error appended to the prompt and an instruction to fix only that.
Budget for up to two calls per generation.

- Interactive mode never retries: a person is already reading the error.
- Transport, auth, rate-limit, and malformed-response failures are never
  retried, so a 429 does not turn into a retry storm.
- The retry feeds back the error text and nothing else, with one exception: an
  unknown fact id also gets a labelled `<valid_fact_ids section="...">` block
  listing the ids that section offered for this generation (ids only). A retry
  that is not told which ids exist just repeats the same slip.
- It relaxes no rule; the second answer faces the same provenance, completeness,
  and locked-field checks as the first.
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

All three advisor modes use the same sourced-content JSON contract. Identity,
contact details, employers, dates, diplomas, and certification names remain
renderer-owned and cannot be supplied by the model.

**In the CV.** Generated CV text — the profile domain phrase — may not contain any
of them. Each has a slot the renderer fills, so writing one there duplicates or
contradicts that slot.

**In the letter.** Prose about a career has to be able to name it, so a letter
paragraph may say « Mon stage actuel chez Baïfall Dream… », name Supinfo, or cite
the AZ-900. Two limits still hold and they come from different rules:

- **contact details** — name, email, phone, LinkedIn — are refused in the letter
  body, because the renderer injects the address block and a body that repeats it
  is duplicating the header rather than writing a sentence;
- an employer, school or certification the **bank never records** is refused by
  the capability tier exactly like any other unsupported proper noun, so
  « Capgemini » does not become sayable. The bank's own dates are part of the
  whole-bank scope, so « depuis juillet 2026 » is fine and « depuis 2014 » is not.

### The advisor selects; the renderer inserts

**The CV's experience bullets and project descriptions are not generated.** The
advisor returns, per employer, an ordered list of **fact ids**, and per project a
project id plus the fact id of its description. The renderer inserts
`bank.claims[id].text` unchanged — only re-encoded to match the template's accent
convention. There is no field for prose, so an advisor that writes instead of
selecting fails loudly rather than quietly reflowing the page.

This is what `skill/SKILL.md` has always described. Its six zones reorder, swap
and make small bounded edits; the bullet text in the templates is the *line-fit*
version, hand-tuned so the CV renders on one page without orphan lines with claims
that are already true. `skill/assets/stage-baifall-dream.md` holds eight
pre-written Baïfall bullet-3 variants (GRC, DevSecOps, AppSec, CloudSec, SOC, Chef
de Projet, Consultant, IAM), and each is a fact-bank entry: selecting is how they
were meant to be used.

Several facts of one employer say the same thing for different audiences, so
selection is a real judgement — the advisor also returns a one-line justification
per entry, recorded on the `ready` event for the detail page and never printed on
the CV.

What the advisor still **writes**:

- the **profile domain phrase** — 3 to 7 words after « Profil orienté », with the
  rendered profile held within ±15 characters of the template's;
- the **job title** — the offer's terminology plus contract and start date;
- the **motivation letter** — free generation. The letter has room and no line-fit
  constraint, so its rules are unchanged.

Tech rows are **reordered** by `skill_order`, which ranks the values already in
the template and never drops one. `tech_additions` may insert **at most 2**
keywords into categories that already exist, and only when both halves of the
skill's rule hold: the keyword is a **verified, reviewed skill in the fact bank**
*and* it **appears in the offer text**. The first stops invention, the second
stops padding the CV with everything he knows; failing either rejects the plan.
Rows are never created. A keyword that would push its row past the template's own
widest line is dropped with a debug log rather than failing the run — one page
matters more than one keyword, and `verify_page_count` still gates the PDF.

Région comes from the offer's region, else the profile.

### Scope: what a claim is judged against

Generated text is judged against a **scope**. The letter and the domain phrase
describe a whole career, so their scope is the whole verified bank. A selected
bullet has no scope question left — its text is the bank's own — so its whole check
is the selection: the id must resolve (below) and must belong to *that* entry.
Borrowing another employer's achievement is no longer something the validator has
to catch in prose; it is unrepresentable.

Entry scope was introduced when bullets were still written, because judging one
against the facts it happened to cite made the same true sentence pass or fail on
bookkeeping alone: Concentrix has five facts and only two carry « 1 500+ », so
« Triage de 1 500+ incidents » was accepted or refused depending on the citation.
Selection removed the question. `entry_scope()` remains as the executable
definition of the model, exercised by tests, for the day entry-level prose returns.

Letter citations stay **required** and still have to resolve to real, reviewed
facts — they are the audit trail.

The whole-bank scope is genuinely looser than an entry's: a small figure that
exists anywhere in the bank passes, so attribution in the letter means "the bank
knows this number" rather than "this employer produced it". Anything absent from
the bank is refused everywhere.

### The three provenance tiers

Within a scope, tokens that are wrong in very different ways are not held to the
same standard. Classification is deterministic — no model call — and tier 1 always
runs first, so nothing below can reach it.

**Tier 1 — attribution: must appear in the scope.** Quantitative claims (`1 500`,
`85 %`, `8 mois`, `3 VMs`) and the names of organisations the bank knows
structurally — employers, schools, diplomas. This is the anti-fabrication and
anti-misattribution guarantee and it never weakens: Baïfall's « 93 mesures » under
a Concentrix bullet is refused because no Concentrix fact carries 93, Lionbridge's
« 200 000+ » is refused under Testronic, and a bullet under one employer may not
name another. (An organisation that exists only inside a fact's prose, such as a
client mentioned in passing, is not recognised structurally and falls through to
tier 2.)

**Tier 2 — capability: must appear in the scope.** Named products, tools,
standards and certifications (`Wazuh`, `Terraform`, `ISO 27001`, `AZ-900`,
`EBIOS RM`). Claiming a tool under an employer says that employer's work involved
it, so `Terraform` and `Kubernetes` — real skills, learned on personal projects —
are refused in a support-desk bullet and accepted under the projects that own
them. `CrowdStrike` is refused everywhere, because nothing in the bank mentions
it. The corpus is verified, non-`needs_review` content only, and **never the offer
text** — a posting is untrusted input (Task 16) and must not be able to license a
claim.

Designations are the digit-shaped corner of this tier: `ISO 27001`,
`ISO/IEC 27002:2022`, `NIS2`, `RGPD art. 32`, `AZ-900`, `802.1X`, `CVSS v3`,
`OWASP Top 10`, `ITIL v4`, `L2/L3` and ANSSI references are recognised by
**shape**, in one extendable constants block (`_DESIGNATION_PATTERNS`), never by
a list of accepted values. The shape only decides which tier applies; acceptance
is still corpus presence, which is why `ISO 31000` and `AZ-104` are refused. A
validated designation's own span is then excluded from the tiers that read the
rest of the bullet, so `ISO 27001 sur 42 applications` still fails on the 42.

**Tier 3 — generic vocabulary: free.** Category words and industry acronyms that
assert nothing about the candidate: SIEM, SOC, EDR, PKI, MFA, API, REST, CI/CD,
RGPD, ITIL, DevSecOps… The bank names *products* (Azure Sentinel, ELK, Wazuh,
règles Sigma), so SIEM and SOC appear in no fact at all and no corpus rule could
ever have reached them. Being on this list is never permission to claim a skill:
SIEM says the bullet is about log supervision, `Wazuh` says the candidate has run
one.

A refusal names the scope that could not support the token —
`unsupported number '93' for entry 'Concentrix'` — so it explains itself, and so
that a token refused under one employer and accepted under another reads as a
scope problem rather than a vocabulary one.

### Maintaining the vocabulary

`config/generic_vocabulary.yaml` is the maintenance point for tier 3. It is
config, not code, so a category word the validator has not met yet is an edit
rather than a release. Terms are matched case- and accent-insensitively, and a
term that is only digits is refused at load time — tier 1 must never be reachable
through tier 3.

Every refusal is logged at INFO with the token, its tier, the scope it was judged
against, and the bullet's cited fact ids. For runs nobody was watching,
`jobpilot vocab-misses [--limit N]` reads the same information back out of the
`generation_failed` events and counts the tokens that keep tripping generations,
with the entries that could not support them:

```bash
jobpilot vocab-misses
```

Each listed token is a two-way decision: it is a category word, and belongs in
`generic_vocabulary.yaml`, or it is a claim the fact bank does not support, and
belongs nowhere. Only capability-tier tokens are listed — no config entry may
ever excuse a fabricated number or a borrowed employer name. The wordings this
model retired (`unsupported proper noun`, `unsupported tool or skill`) are still
parsed, so failures recorded before the tiers existed are counted too.

### Fact id citations

Models reconstruct fact ids from the fact's name and drop the section prefix
(`azure.sentinel` for `skill.azure.sentinel`), which is a citation-format slip
rather than a claim about a different fact. A cited id that is not found verbatim
is resolved by adding a known section prefix (`skill.`, `project.`,
`experience.`, `education.`, `certification.`, `language.`) and by folding case
and separators (`.` / `_` / `-`), **and is accepted only when exactly one fact
matches**. Two matches, or none, stay an error; normalised citations are logged
at debug with both forms.

Matching looks at fact **ids only**, never at a fact's name or text: a citation
that merely resembles what a fact is about is not evidence the model read that
fact. Nothing else changes — every claim must still resolve to a real fact, and
the provenance, completeness, and locked-field checks run against the resolved
ids exactly as before.

### Structural completeness floor

Provenance stops fabrication; a second set of rules stops omission. A generated
CV is rejected (rollback to `queued` plus a `generation_failed` event) unless:

- every employer in the fact bank appears, in reverse-chronological order by
  start date, with at least 2 selected facts for the two most recent employers
  and at least 1 for each older one;
- exactly 3 projects are selected;
- no tool is listed under two skill categories;
- the header location is a real region, never a bare country.

The model still chooses which of an employer's facts represent it and in what
order, which 3 projects to show, and how the letter is written. It no longer
chooses whether an employer appears, nor how a bullet reads. The header location
is renderer-owned: it uses the offer's region and falls back to
`config/profile.yaml` (city + region) instead of a bare country. The tracker row's
variant and project columns are derived from the validated document, not from the
pre-generation routing guess, which is recorded as `routing_variant` in the
status-change event detail.

### Rendering gates: hard vs advisory

`verify_page_count.py` is a **hard gate** on both rendered PDFs. It is the control
`skill/assets/stage-baifall-dream.md` calls reliable, and nothing downgrades it.

`check_orphan_lines.py` is **split**, because that same file says plainly that the
script reports false positives outside a full rendering environment (« largeur de
conteneur mal mesurée ») and that the reliable control is the rendered PDF:

- an orphan reported against `li` or `.project-desc` — **verbatim** bank text,
  whose line fit was tuned by hand — logs a warning and is recorded as
  `orphan_warning` on the `ready` event. It does not fail the generation.
- an orphan reported against `.profile` — the **generated** domain phrase — still
  fails the generation, with the usual rollback to `queued`.

The split is by the selector the script blames, so it follows the text's origin
rather than a guess.

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
- **La Bonne Alternance / API Apprentissage** — register an account and generate
  a token at <https://api.apprentissage.beta.gouv.fr>, then set `LBA_API_KEY` in
  `.env`. The source is enabled in `config/sources.yaml` and skips with a notice
  until the key is present, like every other keyed source. See the section below
  for what it does.

### La Bonne Alternance (API Apprentissage)

Built against the live OpenAPI document at
<https://api.apprentissage.beta.gouv.fr/api/documentation/json>: base URL
`https://api.apprentissage.beta.gouv.fr/api`, `Authorization: Bearer
<LBA_API_KEY>`, `GET /job/v1/search`. The documented quota is **60 calls per
minute per consumer**, reported through `x-ratelimit-*` headers with
`retry-after` on 429; the shared limiter and backoff honour both.

`GET /job/v1/search` answers with two lists, and JobPilot uses them for two
different things:

- **`jobs` → offers.** Mapped into the standard offer shape and ingested through
  the same idempotent path as every other source, so re-running never duplicates
  a row. The tunable block at the top of `sources/labonnealternance.py` holds the
  ROME codes (the IT/systems family) and the department groups
  (Hauts-de-France, Île-de-France).
- **`recruiters` → cold-outreach targets.** Companies the service considers
  likely to hire an alternant. They have posted nothing, so they are **not
  offers**: they are stored in `companies` with `source = 'labonnealternance'`
  (migration `005`) and never reach the review queue. List them with
  `jobpilot contacts --targets`, then add a contact with `jobpilot add-contact`.

  **This adds candidates; it sends nothing.** Every Task 11 rail is untouched:
  `COLD_SEND_ENABLED` stays false, the suppression list, the ≤25/day cap, the
  4-minute stagger, the opt-out footer, and the two-step human confirmation all
  still gate any actual send.

Three things the API does not have, which shape the client:

- **No pagination.** One call returns the whole result set for its filters, so
  `LBA_MAX_PAGES` caps how many *search calls* a run may issue (one per
  department group) rather than paging through results.
- **No contract-type filter, and no stage.** The endpoint publishes
  apprenticeship only, so every offer it returns is an alternance.
- **No contact email.** `apply` exposes a URL and sometimes a phone number, so
  `offers.contact_email` stays empty for this source and the email-send flow has
  nothing to use; apply through the offer's URL.

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
jobpilot vocab-misses            # tokens that keep failing generations, by frequency
jobpilot daemon --interval-hours 3   # loop ingest + score (Ctrl-C to stop)

# Cold outreach (draft here; final confirmation is in the local dashboard)
jobpilot add-contact --company "ACME" --name "Jean Dupont" --role RSSI --email rh@acme.fr
jobpilot contacts --company "ACME"
jobpilot contacts --targets                        # sourced companies likely to hire
jobpilot contacts --targets --source labonnealternance --limit 50
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

### Régénérer (iterate on tailoring output from the browser)

A `ready` application carries a **Régénérer** button next to **Marquer comme
envoyée**. It runs the same generation path as **Approve** — there is no second
tailoring implementation — after moving the application back through
`ready → queued`, so the full event chain stays in `events` and
`state.transition()` remains the only writer of `applications.status`.

The previous run is **moved, not overwritten**, to

```
output/applications/<application_id>/archive/<UTC timestamp>/
```

so generation N can be diffed against N+1. The timestamp is ISO 8601 basic
format (`20260731T014530Z`) because the extended form's colons are not legal in
a Windows filename. Archive directories are never read back by the application
and are not reachable through `/files/…`; they are there for a human with a diff
tool, under the already-gitignored `output/`.

Regeneration is single-flight **per application**: a second click while one is
in flight returns `409` with « Une génération est déjà en cours pour cette
candidature. » instead of starting a parallel run, while a different application
can regenerate at the same time. Regenerating anything that is not `ready`
returns `409` with the current status rather than silently doing nothing. When
the validator rejects a generation, the application returns to `queued` and the
validator's own message is shown verbatim on the detail page.

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
