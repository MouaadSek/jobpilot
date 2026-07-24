# JobPilot prompt pack

Seven files, model-agnostic, designed so any Claude Code model (Fable,
Opus, Sonnet) produces the same architecture.

## How to use

1. Create the repo: `mkdir ~/jobpilot && cd ~/jobpilot && git init`
2. Copy into it: `schema.sql`, `matcher.py`, and `CLAUDE.md` (repo root,
   this is the constitution every session auto-loads).
3. Run phases in order, one Claude Code session each. Paste the phase file
   content as the opening prompt. Do not start a phase before the previous
   one's acceptance criteria are met.
4. If a session drifts or overbuilds, say: "Re-read CLAUDE.md and the
   current phase's out-of-scope list." That resets it.

## Files

| Order | File | What it builds |
|-------|------|----------------|
| 0 | CLAUDE.md | Project constitution (goes in repo root, not pasted) |
| 1 | 01-core-pipeline.md | Skeleton, France Travail + La Bonne Alternance APIs, embeddings, scoring, CLI queue, daemon |
| 2 | 02-scrapers.md | WTTJ, HelloWork, Apec sources |
| 3 | 03-apply-integration.md | Bridge to the existing CV/letter PDF pipeline, channels, human-approved submit |
| 4 | 04-cold-mail.md | Pappers sourcing, email discovery, Gmail sender with caps/stagger/opt-out |
| 5 | 05-reply-tracking.md | Gmail polling, AI reply triage, lifecycle sweeps, stats |
| 6 | 06-review-bot.md | Telegram bot: queue cards, approvals, digests |
| 7 | 07-hardening.md | Backups, doctor, logging, security pass, docs |

## Why it is structured this way

- CLAUDE.md holds everything that must survive across sessions and models:
  the state machine rule, idempotency, legal rails, interaction rules.
  Phase prompts stay short because the constitution carries the weight.
- Each phase has explicit prerequisites, out-of-scope lists, and
  acceptance criteria: the three things that keep any model from
  improvising.
- Human approval is wired into the state machine itself (event
  'human_approved'), so no future phase can accidentally make sending
  fully automatic.

## Practical notes

- Get France Travail credentials (francetravail.io) before phase 1, and a
  Google Cloud project with Gmail API enabled before phase 4.
- Phases 1-3 give you daily value already. 4-5 are the multiplier.
  6-7 are comfort. Stop anywhere and the system still works.
