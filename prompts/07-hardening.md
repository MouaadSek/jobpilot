# Phase 07: Hardening and operations

Prerequisite: phases 01-06 green. Read CLAUDE.md first. No new features:
this phase makes the system boring and reliable.

## Build

1. **Backups**: nightly sqlite .backup to backups/ with 14-day rotation,
   plus a `jobpilot backup now` command. Verify restore in a test.

2. **Health**: `jobpilot doctor` checks: DB integrity (PRAGMA
   integrity_check), Gmail token validity, France Travail token refresh,
   embedding model loads, disk space, stale 'generating' rows, scheduler
   last-run recency. Non-zero exit on failure. Daemon runs doctor daily
   and pushes a Telegram alert on failure.

3. **Observability**: structured logging (JSON lines) with per-source
   ingest counts, scoring durations, send counts. `jobpilot stats --week`
   summary. Rotate logs at 10MB, keep 5.

4. **Resilience review**: audit every external call for timeout + retry +
   circuit-breaking (skip a source for the rest of the day after 3
   consecutive failures). Add missing tests.

5. **Security pass** (treat this as a mini pentest of my own tool):
   - No secrets in logs, repo history clean (scan with gitleaks).
   - .env permissions 600, backups exclude nothing sensitive beyond DB
     (DB contains contact emails: encrypt backups with age, key in .env).
   - Telegram: verify the chat_id allowlist cannot be bypassed via
     inline queries or callback spoofing.
   - Dependency audit: pip-audit in a `make audit` target.
   - Threat model note in docs/SECURITY.md: what an attacker with my
     laptop, my Telegram, or my Gmail token could do, and mitigations.

6. **Docs**: README with full setup from zero (WSL2), runbook for common
   failures, architecture diagram (mermaid) matching reality.

Acceptance: `make check` runs ruff, pytest, pip-audit, gitleaks, doctor,
all green. Fresh-clone setup following README works first try.
