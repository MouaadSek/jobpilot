# CLAUDE.md - JobPilot project constitution

This file is loaded by Claude Code in every session. Follow it strictly,
regardless of which prompt phase is being executed.

## What this project is

Personal job application pipeline for the French IT/cybersecurity market.
Owner: M1 cybersecurity student, Lille, targeting alternance/stage then
Cloud Security / DevSecOps roles. Runs locally on native macOS (Intel),
Python 3.11+, SQLite; CI also runs the suite on Windows, so keep paths and
shell assumptions portable. Single user, no multi-tenancy, no cloud deploy.

## Non-negotiable architecture

- schema.sql is the source of truth for the data model. Never alter tables
  ad hoc: write numbered migration files in migrations/ instead.
- matcher.py owns scoring logic (it lives at the repo root, not under
  src/jobpilot/). Extend via its config, do not fork it.
- The state machine lives in applications.status. Every transition MUST
  be written through a single function (src/jobpilot/state.py:transition)
  that validates legality and logs to the events table. No direct UPDATE
  of status anywhere else.
- Every external source (API, scraper, mailer) sits behind an interface in
  src/jobpilot/sources/base.py so it is pluggable and mockable.
- Idempotency everywhere: any command re-run must never duplicate rows,
  re-send emails, or re-queue skipped offers.

## Engineering standards

- Type hints on everything, ruff clean, no bare except.
- pytest for all new logic, in-memory SQLite for DB tests.
- Secrets only via .env (gitignored), .env.example kept current.
- Timestamps UTC ISO 8601. Text normalized lowercase UTF-8 before matching.
- Logging via the logging module to logs/, never print() in library code.
- Rate limiting + exponential backoff on every external call.
- Small commits, conventional commit messages (feat:, fix:, test:).

## Legal and safety rails (do not remove or weaken)

- Cold email: max 25 sends/day, staggered minimum 4 minutes apart, only
  professional/generic addresses, mandatory opt-out line in every mail,
  suppression list honored before every send.
- Scrapers: respect robots.txt where present, minimum 5s delay per domain,
  identifiable user-agent for APIs, no login-walled scraping, LinkedIn and
  Indeed scrapers stay out of scope unless explicitly re-authorized.
- Never auto-submit an application or send an email without a prior human
  approval recorded in the events table (event = 'human_approved').

### Scope of rule 11

Rule 11 is the scraper rail above — the one that keeps LinkedIn and Indeed
scrapers out of scope unless explicitly re-authorized. Task 43 added a browser
extension that reads LinkedIn, Indeed and WTTJ pages and sends their text to
JobPilot, which looks like it crosses that line. It does not, and this section
records why so a future reader does not have to reconstruct the reasoning.

What the rail forbids is JobPilot going and getting pages: choosing a URL,
requesting it, and taking what comes back. That is what generates load on
someone else's site, what robots.txt speaks to, and what LinkedIn's terms and
its lawsuits are about.

The extension does none of that. It reads a page the user opened, in their own
browser, in their own session, while they are looking at it. It never
navigates, never fetches, never runs on a page the user did not open, and never
touches more than the page currently in front of them. The text was already
delivered to the human; the extension moves it from their screen into their
database. Removing the extension would not remove a single request from
LinkedIn's servers.

`POST /offer/import` is the same fact on the server side: it receives text in
the request body and never dereferences the URL it is given. The URL is an
identifier used to match an existing offer, not something to retrieve.
`test_the_import_path_never_fetches_anything` holds that.

Concretely, and non-negotiably, this scope means the extension must have:

- no background script or service worker,
- no scheduled job,
- nothing that opens, navigates or reloads a tab,
- no host permissions beyond the three domains it reads,
- no request the user's own browsing did not already cause.

Adding any of those turns the extension into a scraper and puts it back under
rule 11. If a feature seems to need one, it is out of scope: stop and say so.

## Interaction rules for Claude Code

- If credentials or config are missing, ask; never silently mock.
- Before writing code in a new phase, print the planned file tree and wait
  for confirmation.
- After each phase, run pytest and ruff, show results, update README.md.
- Do not build anything listed as out-of-scope in the current phase prompt,
  even if it seems useful.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
