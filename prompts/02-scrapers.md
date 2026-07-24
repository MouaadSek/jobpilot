# Phase 02: Scraper sources (run after phase 01 is green)

Prerequisite: phase 01 complete, `jobpilot ingest` pulls France Travail and
La Bonne Alternance, tests pass. Read CLAUDE.md first.

Add three scraper-based sources behind the existing source interface:

1. **Welcome to the Jungle**: use their internal search JSON endpoint
   (inspect the network tab of their job search page; it is an Algolia
   query). Query for cybersecurity keywords, France. No headless browser
   needed if the JSON endpoint works; fall back to Playwright only if not.

2. **HelloWork**: focus Hauts-de-France + Île-de-France. Playwright,
   headless, 5s minimum delay between pages, max 3 result pages per run.

3. **Apec**: cadre offers, cybersecurity filter. Their search has a JSON
   API behind the SPA; prefer it over DOM scraping.

## Requirements

- Each scraper is a class implementing sources/base.py, registered in the
  ingest command, individually enable/disable via config/sources.yaml.
- Map into the offers table exactly like API sources; the content_hash
  dedup must collapse offers already ingested from France Travail.
- Robots.txt check at startup per domain; if disallowed, log and skip.
- Randomized realistic user-agent, but do NOT implement CAPTCHA bypass,
  proxy rotation, or login automation. If a scraper gets blocked, it logs
  and gives up gracefully for that run.
- Per-scraper pytest with recorded fixture responses (no live calls in CI).
- Failure isolation: one scraper crashing must not stop the ingest run.

## Out of scope

- LinkedIn, Indeed (hostile targets, not worth it)
- Any anti-bot evasion beyond polite delays
- Parallel scraping

Acceptance: `jobpilot ingest --source wttj` inserts real offers, dedup
proven by a test, ruff + pytest green.
