# Phase 06: Review interface (Telegram bot)

Prerequisite: phases 01-05 green. Read CLAUDE.md first.

Replace the CLI review flow with a Telegram bot so I can triage from my
phone. python-telegram-bot v21+, token in .env, restricted to my chat_id
(reject all other users, log attempts).

## Build

1. **Queue cards**: /queue sends one message per queued application:
   score, title, company, city, contract, source, URL, chosen CV variant.
   Inline buttons: Apply, Skip, Details. Apply triggers the phase 03
   generation flow and replies with the two PDFs as documents for review.

2. **Approval flow**: after reviewing PDFs, buttons Confirm submit /
   Regenerate / Cancel. Confirm records 'human_approved' and, for email
   channel, queues the send in phase 04's mailer. This is the only
   Telegram path that can lead to a send, and it must reuse the existing
   state machine transition function, no shortcuts.

3. **Cold mail review**: /coldqueue same pattern for drafted cold mails:
   show the full text, Approve / Edit subject / Skip.

4. **Notifications push**: replace the phase 05 self-email with Telegram
   messages for 'replied' and 'interview' transitions, including the
   reply snippet and triage class.

5. **Daily digest** at 08:30 Europe/Paris: new matches count, top 3 by
   score, pending approvals, yesterday's sends, any replies.

## Engineering

- Bot runs inside the existing daemon (same process, asyncio), not a
  second service.
- All bot actions go through the same service layer as the CLI; zero
  business logic in handlers.
- Handlers covered by tests using python-telegram-bot's test utilities.

## Out of scope

- Web dashboard (only if Telegram proves insufficient)
- Multi-user support

Acceptance: full apply flow phone-only, from card to human_approved,
with the state machine and events table showing the same trail as the CLI.
