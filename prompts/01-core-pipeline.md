# JobPilot: kickoff prompt for Claude Code

Copy everything below the line into Claude Code from an empty project folder
(e.g. ~/jobpilot on WSL2). Put schema.sql and matcher.py in the folder first,
they are the starting point.

---

Build "JobPilot", a personal job application pipeline for the French
IT/cybersecurity market. I am an M1 cybersecurity student in Lille looking
for alternance/stage offers. Python 3.11+, SQLite, runs locally on
WSL2 Ubuntu. No Docker for v1, plain venv.

## Existing assets (do not rewrite, build around them)

- schema.sql: the full database schema. Apply it as-is. Read it carefully,
  it defines the state machine in applications.status and dedup via
  offers.content_hash.
- matcher.py: the scoring engine (hard filters, keyword score, semantic
  score, weighted blend, CV variant picker). Wire it up, do not redesign it.

## v1 scope, in build order

1. **Project skeleton**: src/ layout, pyproject.toml, .env handling
   (python-dotenv), a single CLI entrypoint `jobpilot` with subcommands
   (typer or argparse): `init-db`, `ingest`, `score`, `queue`, `apply`,
   `stats`.

2. **Ingestion: France Travail API client** (priority #1).
   - OAuth2 client_credentials flow against francetravail.io
     ("Offres d'emploi v2" API). Credentials from .env.
   - Search params: keywords list (cybersécurité, SOC, sécurité cloud,
     DevSecOps, pentest), region filters (Hauts-de-France, Île-de-France),
     contract types alternance + stage.
   - Map results into the offers table matching schema.sql exactly.
     Compute content_hash = sha256(lower(title + company + first 500 chars
     of description)). Respect the UNIQUE constraints, INSERT OR IGNORE.
   - Rate limiting and retry with backoff. Log to a file, not just stdout.

3. **Ingestion: La Bonne Alternance API client**.
   - Same pattern. Also pull their "companies likely to hire" endpoint
     into the companies table (feeds cold mail later).

4. **Ingestion: ATS pollers** for a hand-configured company list
   (config/targets.yaml). Support Lever, Greenhouse and SmartRecruiters
   public JSON endpoints. One generic poller per ATS type.

5. **Embeddings**: use sentence-transformers all-MiniLM-L6-v2 locally,
   lazy-loaded. Write the embed_fn expected by matcher.semantic_score.
   Cache the profile embedding into profile.embedding as JSON.

6. **Profile seeding**: `jobpilot init-profile` interactive command that
   fills the profile singleton row and the cv_variants table. Seed
   cv_variants with 10 slugs I will provide in config/variants.yaml.

7. **Review queue CLI**: `jobpilot queue` lists queued applications sorted
   by final_score with a compact one-line format (score, title, company,
   city, contract, url). `jobpilot apply <id>` and `jobpilot skip <id>`
   move the state machine and log to events.

8. **Scheduler**: a `jobpilot daemon` command that runs ingest + score
   every 3 hours (APScheduler), plus a systemd user service file for WSL2.

## Explicitly OUT of v1 (do not build yet)

- Any scraping (WTTJ, Indeed, LinkedIn)
- Cold mailing / Gmail integration
- CV/letter PDF generation (I have a separate pipeline for that)
- Web dashboard, Telegram bot

## Engineering constraints

- Every external call behind an interface so sources are pluggable.
- Type hints everywhere, ruff clean, pytest with at least: hash dedup test,
  hard filter tests, state machine transition tests (use an in-memory DB).
- No secrets in code, .env.example committed, .env gitignored.
- All timestamps UTC ISO 8601.
- Idempotent by design: re-running ingest or score must never duplicate
  rows or re-queue skipped offers.
- French text is the norm in offer data, keep everything UTF-8 and
  lowercase-normalize before matching.

Start with steps 1 and 2, show me the tree and the France Travail client,
then continue. Ask me for API credentials when you get there, do not mock
them silently.
