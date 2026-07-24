# Phase 04: Cold mail module

Prerequisite: phases 01-03 green. Read CLAUDE.md first, especially the
legal and safety rails: they are hard requirements in this phase.

## Build

1. **Company sourcing**:
   - Extend the La Bonne Alternance companies import (already ingesting)
     with a Pappers API client: filter NAF codes 62.02A, 62.01Z, 6202B,
     regions Hauts-de-France + Île-de-France, size 11-1000.
   - `jobpilot companies list/add/blacklist` commands. Blacklisted
     companies never receive mail (suppression table via migration).

2. **Email discovery** (src/jobpilot/discovery.py):
   - Priority order: generic addresses from the company website
     (contact@, rh@, recrutement@, jobs@) found by fetching the site's
     contact/legal pages; then pattern guess from companies.domain
     (prenom.nom pattern only if a contact name is publicly listed on the
     company site). MX record check to validate the domain accepts mail.
   - Never scrape personal emails from LinkedIn or aggregator databases.
   - Store discovered address + provenance on the application row.

3. **Mailer** (Gmail API, OAuth installed-app flow):
   - `jobpilot mail queue <company_id>` creates a cold application
     (kind='cold') and drafts initial mail from templates/messages/cold_*.
   - Sending daemon respects: max 25/day, min 4 min stagger, business hours
     Europe/Paris only (9:00-18:00, Mon-Fri), suppression list checked at
     send time, opt-out footer always appended.
   - Every send requires prior 'human_approved' event
     (`jobpilot mail review` shows drafts, `jobpilot mail approve <id>`).
   - Followups: J+4 and J+10 auto-queued in email_queue, cancelled
     immediately if a reply is detected (phase 05) or opt-out received.

4. **Opt-out handling**: a plus-address (me+optout@gmail.com) link in the
   footer; phase 05 will parse it, but build the suppression insert now
   with a manual `jobpilot mail optout <email>` command.

## Out of scope

- Buying email lists, Hunter.io or similar enrichment services
- HTML emails (plain text only, higher deliverability, more personal)
- Any send without human approval

Acceptance: end-to-end dry-run mode (`--dry-run` prints instead of sends)
covered by tests; a real send test to my own address; caps and stagger
proven by unit tests on the scheduler logic.
