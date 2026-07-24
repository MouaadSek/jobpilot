# Phase 03: Apply integration (CV/letter generation bridge)

Prerequisite: phases 01-02 green. Read CLAUDE.md first.

I already have a working CV/letter pipeline: HTML templates rendered to PDF
via Playwright/Chromium, script at a path I will provide, plus 10 CV variant
templates. JobPilot must orchestrate it, not reimplement it.

## Build

1. **Generation bridge** (src/jobpilot/generate.py):
   - `jobpilot apply <id>` moves the application to 'generating', calls my
     external generation script via subprocess with: offer title, company,
     description text, and the chosen cv_variant slug from match_scores.
   - Script outputs land in output/applications/<app_id>/cv.pdf and
     letter.pdf; store paths in the applications row, transition to 'ready'.
   - If generation fails, transition back to 'queued' and log the error to
     events; never leave an application stuck in 'generating' (add a
     startup sweep that resets stale 'generating' rows older than 1h).

2. **Contact resolution**:
   - For each 'ready' application, try to determine the application channel:
     direct email in the offer text (regex), ATS URL, or platform URL.
   - Store contact_email/contact_name when found. Mark the channel in a new
     column via migration: applications.channel
     ('email','ats_form','platform','unknown').

3. **Submission helper** (semi-automatic, human in the loop):
   - `jobpilot submit <id>`:
     - channel=email: build a draft .eml file with the PDFs attached and a
       short French message from a template, open path printed for review.
       Actual sending happens in phase 04's mailer after human approval.
     - channel=ats_form or platform: print the URL and the paths of the two
       PDFs, transition to 'applied' only after `jobpilot confirm <id>`
       which records event 'human_approved'.

4. **Message templates** in templates/messages/ (French), with variables
   {company}, {title}, {variant_pitch}. One initial template, professional,
   sober, max 120 words, no emdashes, no buzzwords.

## Out of scope

- Auto-filling web forms with Playwright (later, maybe never)
- Sending any email (phase 04)

Acceptance: full path offer -> queue -> apply -> generated PDFs -> confirm
-> 'applied' state, with every transition visible in events, tests included.
