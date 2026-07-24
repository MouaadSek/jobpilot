# Phase 05: Reply detection + tracker automation

Prerequisite: phases 01-04 green. Read CLAUDE.md first.

## Build

1. **Gmail polling** (reuse phase 04 OAuth):
   - `jobpilot sync-mail` (also run by the daemon every 30 min): for every
     application with a gmail_thread_id, check for new inbound messages.
   - For cold mails sent without a thread (first send), match replies by
     In-Reply-To / References headers, fallback to from-address matching
     against applications.contact_email.
   - On reply: transition to 'replied', cancel pending followups in
     email_queue, log the reply snippet (first 300 chars) to events.

2. **Reply triage** (Claude API, model claude-sonnet-4-6, key from .env):
   - Classify each reply: positive / interview_request / rejection /
     auto_reply / optout / other. Map interview_request -> 'interview',
     rejection -> 'rejected', optout -> suppression insert + 'rejected'.
   - Ambiguous (other/auto_reply): stay 'replied', flag for manual review.
   - Prompt lives in prompts/triage.txt, includes 3 few-shot examples in
     French. Never send the full thread, only the latest inbound message.

3. **Lifecycle automation**:
   - Daily sweep: applications in 'applied'/'followup_2' with
     last_event_at older than 21 days -> 'ghosted'.
   - `jobpilot stats`: funnel counts per state, reply rate per source,
     reply rate cold vs offer, average days-to-reply. Plain table output.

4. **Notifications**: on transitions to 'replied' or 'interview', send a
   local notification: append to logs/inbox.md AND send a self-email via
   the mailer (exempt from the daily cap, marked kind='system').

## Out of scope

- Telegram/web notifications (phase 06)
- Auto-responding to any recruiter email. Drafts only, never send.

Acceptance: simulated mailbox fixtures drive tests for every triage class
and every transition; ghosted sweep proven idempotent.
