# Graph Report - jobpilot  (2026-08-04)

## Corpus Check
- 153 files · ~184,540 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3306 nodes · 8410 edges · 134 communities (114 shown, 20 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 368 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7f9e0a1a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_downloads.py
- Request
- _candidate_name
- _client
- create_app
- dashboard.py
- run_dashboard
- Path
- test_routing.py
- mailer.py
- validate_cv.py
- get_settings
- connect
- test_descriptions.py
- test_generic_vocabulary.py
- apply_assist.py
- test_skim.py
- contacts.py
- JobPilot — Codex Handoff (complete A-to-Z)
- RefreshRunner
- _payload
- wttj.py
- SourcedBullet
- france_travail.py
- test_provenance_tiers.py
- launch_wttj_application
- Dashboard
- _FakePage
- cli.py
- test_desktop_shell.py
- generate_application
- test_contacts.py
- test_email_alerts.py
- test_labonnealternance.py
- _Toolchain
- email_alerts.py
- test_alert_card_fields.py
- Settings
- Job Application Pipeline
- matcher.py
- test_cv_completeness.py
- OfferRecord
- test_dashboard_facts_scheduler.py
- .from_mapping
- test_cold_outreach.py
- _FakePage
- MissingCredentialError
- ats.py
- AnthropicTailoringAdvisor
- OpenAITailoringAdvisor
- resolve_fact_id
- test_tech_additions.py
- load_fact_bank
- CompanyRecord
- labonnealternance.py
- ingest_source
- pick_variant
- test_fact_id_resolution.py
- test_letter_locked_fields.py
- launch_application_assist
- test_letter_quality.py
- test_mailer.py
- models.py
- reparse_alerts
- test_designation_numbers.py
- test_fact_id_consistency.py
- review.py
- ingest_source
- _AnchorParser
- test_preview.py
- vocabulary.py
- UnknownFactIdError
- Baifall Dream Stage - Reference Document (v3)
- test_facts.py
- test_progress.py
- scheduler_status
- schema.sql
- test_packaging.py
- CLAUDE.md - JobPilot project constitution
- AGENTS.md - JobPilot project constitution
- test_valid_sourced_advice_completes_the_shared_generation_path
- JobPilot prompt pack
- JobPilot: kickoff prompt for Claude Code
- CV Template Manifest
- generate_cv_pdf.py
- test_validate_cv_ai.py
- Phase 06: Review interface (Telegram bot)
- test_retry_feedback.py
- record_form_fields
- Phase 02: Scraper sources (run after phase 01 is green)
- Phase 03: Apply integration (CV/letter generation bridge)
- Phase 04: Cold mail module
- Phase 05: Reply detection + tracker automation
- _TextParser
- 002_contacts_suppression.sql
- 007_form_mappings.sql
- Phase 07: Hardening and operations
- 001_add_profile_headline.sql
- 003_offers_contact_email.sql
- 004_offers_easy_apply.sql
- 005_companies_source.sql
- 006_applications_apply_route.sql
- install_agent.sh
- make_app.sh
- uninstall_agent.sh
- sources/__init__.py
- jobpilot
- test_designation_numbers.py
- _AnchorParser
- test_ingest_idempotent.py
- apply_matching_profile_cmd
- mappings_for
- _TextParser
- mappings_for
- tracker.py
- parse_rejections
- UnknownFactIdError
- test_ingest_idempotent.py
- run_menubar
- _FakeLocator
- test_renderer_owned_fields.py
- ApplicationNotQueuedError
- parse_indeed
- test_sourcing_targets_changes_no_sending_gate
- 008_applications_generation_warnings.sql
- Protocol
- apply_matching_profile_cmd
- datetime
- MonkeyPatch
- observable_controls
- LogCaptureFixture

## God Nodes (most connected - your core abstractions)
1. `Settings` - 117 edges
2. `current_status()` - 88 edges
3. `TailoringError` - 78 edges
4. `_payload()` - 77 edges
5. `OfferRecord` - 68 edges
6. `load_fact_bank()` - 60 edges
7. `OfferContext` - 55 edges
8. `pick_variant()` - 55 edges
9. `get_settings()` - 54 edges
10. `_Toolchain` - 53 edges

## Surprising Connections (you probably didn't know these)
- `test_the_library_and_tracker_mark_a_degraded_application()` --calls--> `tracker_rows()`  [INFERRED]
  tests/test_generation_warnings.py → src/jobpilot/tracker.py
- `test_the_warning_is_visible_on_the_application_page()` --calls--> `create_app()`  [INFERRED]
  tests/test_drop_unknown_citation.py → src/jobpilot/dashboard.py
- `_CompleteAdvisor` --uses--> `TailoringError`  [INFERRED]
  tests/test_cv_completeness.py → src/jobpilot/tailoring.py
- `_IncompleteAdvisor` --uses--> `TailoringError`  [INFERRED]
  tests/test_cv_completeness.py → src/jobpilot/tailoring.py
- `_RecordingToolchain` --uses--> `TailoringError`  [INFERRED]
  tests/test_cv_completeness.py → src/jobpilot/tailoring.py

## Import Cycles
- None detected.

## Communities (134 total, 20 thin omitted)

### Community 0 - "test_downloads.py"
Cohesion: 0.05
Nodes (41): BaseException, Operation, ProgressRegistry, Any, datetime, Update a running operation. A key that is not running is ignored., Close an operation. The first outcome recorded wins.          A handled failure, Everything running, plus anything that finished very recently. (+33 more)

### Community 1 - "Request"
Cohesion: 0.19
Nodes (32): library_entries(), Every application that has generated documents, newest generation first.      Ap, _client(), _generated(), Connection, Path, TestClient, Task 36 item 4: the document library, archives included.  The case: an employer (+24 more)

### Community 2 - "_candidate_name"
Cohesion: 0.07
Nodes (90): ModuleType, SimpleNamespace, JobPilot: personal job application pipeline for the French IT/cybersecurity mark, current_status(), _application(), _ConnectionProxy, Connection, Exception (+82 more)

### Community 3 - "_client"
Cohesion: 0.09
Nodes (39): adapter_for_url(), _application_for_assist(), _application_for_wttj(), ApplyAssistError, AssistResult, BrowserLauncher, _css_attribute_value(), _fallback() (+31 more)

### Community 4 - "create_app"
Cohesion: 0.06
Nodes (48): apply_cmd(), backfill_descriptions_cmd(), init_db_cmd(), invention_report_cmd(), Synthesise descriptions for stored offers whose text is too thin to score., Clear stored match_scores so the next `score` run re-evaluates those offers., Approve an application and generate its tailored application documents., Pass on an application: move queued -> skipped. (+40 more)

### Community 5 - "dashboard.py"
Cohesion: 0.08
Nodes (67): ExperienceFact, FactClaim, Match, Pattern, RuntimeError, _add_tech_additions(), _add_tech_keywords(), _contact_fields() (+59 more)

### Community 6 - "run_dashboard"
Cohesion: 0.09
Nodes (34): MonkeyPatch, drop_unknown_citation(), DroppedCitation, _employer_bullet_floor(), One citation removed as a last resort, and where it was removed from., How many bullets the completeness floor guarantees this employer.      Read from, Remove one unusable citation, or refuse when removing it would weaken the CV., _dropping_enabled() (+26 more)

### Community 7 - "Path"
Cohesion: 0.08
Nodes (40): Normalized DTOs that every source emits, decoupled from source-specific JSON., derive_fields(), _Derived, Re-derive alert card fields (company / city / workplace / easy-apply) in place., Re-derive one offer's card fields from the text that was stored for it.      Pur, _AlertAnchor, _anchors(), _Card (+32 more)

### Community 8 - "test_routing.py"
Cohesion: 0.09
Nodes (60): Cursor, _artifacts(), Path, Resolve the one route this application would go out by. Writes nothing., A route the offer qualified for, and the reason it cannot be used., The resolved plan for one application. Carries no state and stores none., Fingerprint of exactly the inputs that decided this route.          Stateless by, resolve_route() (+52 more)

### Community 9 - "mailer.py"
Cohesion: 0.09
Nodes (48): Remove configured secrets from exception text before display/logging., Settings, Whether a named mailbox on a professional domain needs extra approval., requires_personal_confirmation(), _as_utc(), _build_message(), build_sender(), ColdEmailPreparation (+40 more)

### Community 10 - "validate_cv.py"
Cohesion: 0.06
Nodes (53): check_orphans(), find_regressions(), Path, Return orphan metrics that are new or materially worse than the template., format_date(), main(), build_letter_html(), detect_github() (+45 more)

### Community 11 - "get_settings"
Cohesion: 0.08
Nodes (31): LookupError, ApplicationGenerationError, ApplicationNotFoundError, ApplicationNotQueuedError, ApplyOutcome, approve_application(), archive_artifacts(), generation_single_flight() (+23 more)

### Community 12 - "connect"
Cohesion: 0.09
Nodes (27): document_variant_label(), extract_template_context(), Apply the mechanical contract and encoding rules to a chosen slug.      These ar, Read all editable choices without altering the template., Name the variant the rendered CV actually is, not the one routing guessed., variant_for_slug(), rendered(), _offer() (+19 more)

### Community 13 - "test_descriptions.py"
Cohesion: 0.10
Nodes (50): backfill_descriptions(), BackfillResult, clear_match_scores(), is_synthesized(), Connection, Synthesise matchable text for offers that arrive with no description.  Job-alert, Return an SQL fragment + params restricting a query to one source., Regenerate synthesised descriptions for stored offers whose text is thin.      I (+42 more)

### Community 14 - "test_generic_vocabulary.py"
Cohesion: 0.05
Nodes (52): add_contact_cmd(), _csv(), draft_cold_cmd(), init_profile_cmd(), _langs(), mark_sent_cmd(), menubar_cmd(), queue_cmd() (+44 more)

### Community 15 - "apply_assist.py"
Cohesion: 0.32
Nodes (15): _events(), Connection, EmailMessage, Exception, Path, Application email sending: rails, transitions, and events (mocked SMTP)., _ready_app(), _Sender (+7 more)

### Community 16 - "test_skim.py"
Cohesion: 0.10
Nodes (52): available_sources(), _create_application(), ignore_offer(), promote_offer(), Connection, Row, ValueError, The skim list: offers that passed the hard filter but scored below threshold.  T (+44 more)

### Community 17 - "contacts.py"
Cohesion: 0.09
Nodes (40): contacts_cmd(), List stored contacts for a company, or the sourced outreach targets.      A targ, _candidate_name(), ContactCandidate, discover_and_store(), DiscoverySource, draft_cold_email(), draft_linkedin_note() (+32 more)

### Community 18 - "JobPilot — Codex Handoff (complete A-to-Z)"
Cohesion: 0.04
Nodes (45): 10. HARD REJECTIONS (offers the pipeline should auto-skip), 11. API REFERENCES, 12. DESIGN PRINCIPLES (non-negotiable), 13. ENV VARS (.env), 14. GITHUB PUSH (do this FIRST, before any Codex work), 15. CODEX TASK BREAKDOWN (suggested order), 16. BAIFALL DREAM STAGE REFERENCE, 17. SCRIPTS REFERENCE (+37 more)

### Community 19 - "RefreshRunner"
Cohesion: 0.19
Nodes (23): OpenAITailoringAdvisor, OpenAI-compatible Chat Completions adviser., _offer(), _openai_response(), _plan_payload(), Any, Connection, MonkeyPatch (+15 more)

### Community 20 - "_payload"
Cohesion: 0.11
Nodes (41): _bullets(), _project(), The advisor selects; the renderer inserts the bank's wording unchanged., The pre-written variants from the skill asset, used as the asset intends., The contract has no field for prose, so a writing advisor fails loudly., Only the entry's own facts, so a skill id cannot become a bullet., Task 25's tolerance survives: ids are normalised before they are judged., The phrase is short, but it is still generated, so the tiers still read it. (+33 more)

### Community 21 - "wttj.py"
Cohesion: 0.10
Nodes (41): _city(), _contact_email(), _contract(), _first(), map_hit(), _org(), _prose(), Any (+33 more)

### Community 22 - "SourcedBullet"
Cohesion: 0.08
Nodes (24): Event, MissingCredentialError, RuntimeError, Raised when a required secret is absent. We ask; we never silently mock., _default_model_loader(), _default_score_pass(), _production_connection(), Any (+16 more)

### Community 23 - "france_travail.py"
Cohesion: 0.06
Nodes (44): Client, _first_nonempty(), FranceTravailSource, _map_contact_email(), _map_contract(), _map_duration_months(), map_offer(), Any (+36 more)

### Community 24 - "test_provenance_tiers.py"
Cohesion: 0.08
Nodes (37): bank(), _in_bank(), _offer(), Three kinds of token, three different burdens of proof., Not even the widest scope can support it., The reader has to be able to search for it, or add it to the config., Task 26's handling survives as the digit-shaped corner of tier 2., Presence in the bank is necessary for tier 2, never sufficient. (+29 more)

### Community 25 - "launch_wttj_application"
Cohesion: 0.22
Nodes (25): _cold_draft(), _configure_dashboard(), _dashboard_client(), _event_rows(), Connection, EmailMessage, Exception, MonkeyPatch (+17 more)

### Community 26 - "Dashboard"
Cohesion: 0.05
Nodes (36): Actualiser les offres (refresh from the page), Always up, without a terminal, Architecture (summary), ATS application assist (prefill only), Background scheduling, CI, Cold outreach sending (disabled by default), Commands (+28 more)

### Community 27 - "_FakePage"
Cohesion: 0.11
Nodes (19): ApplyAdapter, GreenhouseAdapter, LeverAdapter, Common adapter interface for a best-effort ATS prefill., SmartRecruitersAdapter, _FakeLauncher, _FakeLocator, _FakePage (+11 more)

### Community 28 - "cli.py"
Cohesion: 0.17
Nodes (32): Any, Every offer application, optionally narrowed to one status., Export exactly the visible rows, in the visible column order., to_csv(), tracker_rows(), _application(), _client(), Connection (+24 more)

### Community 29 - "test_desktop_shell.py"
Cohesion: 0.07
Nodes (36): CaptureFixture, dashboard_cmd(), Launch the local review dashboard on 127.0.0.1., dashboard_already_running(), Whether something is already listening on the dashboard's port.      A connect p, Run the dashboard on an intentionally fixed loopback interface.      Returns a p, run_dashboard(), The menu bar text. Short: it competes with every other item up there. (+28 more)

### Community 30 - "generate_application"
Cohesion: 0.07
Nodes (32): CompletedProcess, date, Protocol, build_advisor(), _check_orphans(), _contains_generated_orphan(), DocumentToolchain, _french_date() (+24 more)

### Community 31 - "test_contacts.py"
Cohesion: 0.21
Nodes (14): _app(), company(), Connection, Stage 2: contact storage, suppression, address rules, cap/stagger, drafting., test_daily_cap_rolls_to_next_day(), test_manual_discovery_is_noop(), test_prepare_outreach_idempotent(), test_prepare_outreach_personal_email_skips_email_keeps_linkedin() (+6 more)

### Community 32 - "test_email_alerts.py"
Cohesion: 0.09
Nodes (43): Message, GmailIMAP, html_of(), LinkedInAlertSource, Minimal read-only Gmail IMAP client., Fetch recent mail sent from `domains` (or any of their subdomains).          The, Return the best HTML (or plain-text) body of an email message., Return the lowercased domain of the address in a `From` header.      Parses the (+35 more)

### Community 33 - "test_labonnealternance.py"
Cohesion: 0.13
Nodes (33): _fixture(), _NoWait, LogCaptureFixture, La Bonne Alternance through the API Apprentissage: mapping, rails, ingestion.  E, The endpoint has no pagination, so this is the volume knob that exists., A full ingest reads both lists; it must not pay for the search twice., The live API really does repeat an offer inside one response., A company that has posted nothing must not appear in the review queue. (+25 more)

### Community 34 - "_Toolchain"
Cohesion: 0.07
Nodes (39): GenerationWarning, One thing the reviewer is being asked to check by eye., _correction_block(), _default_letter(), GenerationResult, _offer_identity(), OfferContext, Raised when one automatic validator-feedback retry still failed.      ``str()`` (+31 more)

### Community 35 - "email_alerts.py"
Cohesion: 0.08
Nodes (29): Every id the advisor may cite, flattened out of the context it was given.      D, valid_fact_ids(), context(), facts(), _nested_ids(), Task 37 item 1: tell the advisor the set of ids is closed.  `skill.rules.sigma`, Task 37 must not have quietly added Sigma to make the failure go away., Defensive: a template with no projects must not raise here. (+21 more)

### Community 36 - "test_alert_card_fields.py"
Cohesion: 0.11
Nodes (29): clear_warnings(), _decode(), Connection, What a generation had to degrade, recorded where the reviewer will see it.  Task, Gate names per application, for the library and tracker markers.      One query, Replace this application's warnings with the ones from this run., Drop the previous run's warnings at the start of a new generation.      Cleared, Every warning the current generation of this application carries. (+21 more)

### Community 37 - "Settings"
Cohesion: 0.14
Nodes (13): HTTPStatusError, RateLimiter, Minimum-delay-per-domain limiter. Blocks until the next call is allowed., LaBonneAlternanceAuthError, LaBonneAlternanceError, LaBonneAlternanceRateLimited, LaBonneAlternanceSource, RuntimeError (+5 more)

### Community 38 - "Job Application Pipeline"
Cohesion: 0.06
Nodes (31): Alternance vs Stage, Edge Cases & Principles, Encoding note, Execution Flow, Flag once, then execute:, Generate with the bundled script:, GitHub Exception, Hard rejections (no output): (+23 more)

### Community 39 - "matcher.py"
Cohesion: 0.15
Nodes (28): bonus_score(), cosine(), hard_filter(), keyword_score(), norm(), pick_variant(), Profile, Connection (+20 more)

### Community 40 - "test_cv_completeness.py"
Cohesion: 0.13
Nodes (23): _category_skills(), _CompleteAdvisor, Any, Connection, Path, _Toolchain, _queued_application(), Structural completeness floor for AI-generated CVs (Task 22).  Selection freedom (+15 more)

### Community 41 - "OfferRecord"
Cohesion: 0.05
Nodes (45): LogCaptureFixture, AmbiguousFactIdError, _fact_id_key(), _guessed_section(), nearest_entry_claim_ids(), Raised when a citation could be several facts. Never guess between them., Fold separator and case differences, and nothing else, for comparison., Map a cited id onto a real fact id, accepting only unambiguous matches.      Mat (+37 more)

### Community 42 - "test_dashboard_facts_scheduler.py"
Cohesion: 0.29
Nodes (16): _client(), fixture_bank(), Connection, MonkeyPatch, Path, TestClient, Read-only fact bank page and honest scheduler reporting on the queue page., test_daemon_state_follows_the_recorded_heartbeat_age() (+8 more)

### Community 43 - ".from_mapping"
Cohesion: 0.11
Nodes (20): enrich_offer(), is_thin(), Replace a thin description in place; richer descriptions are left alone.      Ca, True when a description is too short to be worth embedding on its own., content_hash(), OfferRecord, sha256(lower(title + company + first 500 chars of description)).      This is th, One normalized offer, ready to insert into the offers table. (+12 more)

### Community 44 - "test_cold_outreach.py"
Cohesion: 0.15
Nodes (21): ATSSource, infer_contract(), load_targets(), map_greenhouse(), map_lever(), map_smartrecruiters(), _ms_to_iso(), Any (+13 more)

### Community 45 - "_FakePage"
Cohesion: 0.24
Nodes (20): _events(), _FakeLauncher, _FakePage, Connection, Path, Row, WTTJ inline application stays human-approved and dry-run by default., _ready_wttj_application() (+12 more)

### Community 46 - "MissingCredentialError"
Cohesion: 0.10
Nodes (21): _archives_for(), Generation, is_archive_stamp(), LibraryEntry, _mtime_iso(), Any, Connection, Path (+13 more)

### Community 47 - "ats.py"
Cohesion: 0.15
Nodes (23): download_filename(), Download names an employer folder can still be read a week later.  ``output/appl, Reduce free text to ``[A-Za-z0-9-_]``, or to "" if nothing survives.      Accent, Build ``<Company>_<Type>_<Nom>.<ext>`` for one artefact.      Falls back to the, slugify(), _client(), Connection, Path (+15 more)

### Community 48 - "AnthropicTailoringAdvisor"
Cohesion: 0.13
Nodes (27): _experience_content(), _FabricatingAdvisor, _gemini_shaped_payload(), _offer(), Connection, MonkeyPatch, Path, _queued_application() (+19 more)

### Community 49 - "OpenAITailoringAdvisor"
Cohesion: 0.17
Nodes (23): Decision, RouteId, _applicant_reason(), _ats_prefill(), _email(), has_form_mapping(), _learned_form(), _manual_open() (+15 more)

### Community 50 - "resolve_fact_id"
Cohesion: 0.17
Nodes (22): _city(), _company_name(), _contract_type(), _domain(), _first(), map_company(), map_offer(), Any (+14 more)

### Community 51 - "test_tech_additions.py"
Cohesion: 0.15
Nodes (26): bank(), _offer(), LogCaptureFixture, Zone 3 may add a keyword, but only one he has and the offer asked for., Reorder-only remains the default and the common case., Genuinely his, but padding: the offer did not ask for it., Presence in the bank is necessary, never sufficient., Derived from the file, not a magic number. (+18 more)

### Community 52 - "load_fact_bank"
Cohesion: 0.12
Nodes (33): facts_cmd(), Print the provenance fact bank grouped for human review., _boolean(), CertificationFact, _claim_list(), EducationFact, _entry_claim(), ExperienceFact (+25 more)

### Community 53 - "CompanyRecord"
Cohesion: 0.08
Nodes (39): CvProfile, _advise_and_tailor(), _advisor_fact_context(), _advisor_prompt(), _canonicalize_prose(), _generated_bullets(), _interactive_structured_payload(), _json_object() (+31 more)

### Community 54 - "labonnealternance.py"
Cohesion: 0.10
Nodes (17): Path, _Toolchain, _InventsThenRecovers, Connection, LogCaptureFixture, Path, Task 37 item 2: give the unknown-id retry something to work with.  An unknown fa, Cites an id that exists nowhere, for a chosen number of attempts. (+9 more)

### Community 55 - "ingest_source"
Cohesion: 0.13
Nodes (18): ApplicantProfile, The non-secret contact values entered into an ATS form., build_prefill(), discard_mapping(), FormLearningError, FormMapping, PrefillOutcome, _profile_values() (+10 more)

### Community 56 - "pick_variant"
Cohesion: 0.16
Nodes (9): _ConfirmationBaseline, _Locator, _Page, PrefillPlan, Protocol, The actions selected from a page's current HTML fixture/markup., WTTJ inline form adapter with explicit pre-submit assertions., _scoped_selector() (+1 more)

### Community 57 - "test_fact_id_resolution.py"
Cohesion: 0.20
Nodes (20): invention_report(), How often the advisor cites an id that does not exist, and whether it recovers., _Invents, Connection, MonkeyPatch, Path, Task 37 item 4: count invention, so the other three items are not guesswork.  Pr, Item 3 degrades the CV; that is a different outcome from getting it right. (+12 more)

### Community 58 - "test_letter_locked_fields.py"
Cohesion: 0.18
Nodes (19): bank(), _letter(), _offer(), A letter is prose about a career; a CV is slots the renderer fills., Naming a real-sounding employer he never had is a fabrication, not prose., The renderer injects the address block; the body repeating it is a bug., Otherwise the test above would prove nothing about scope., The bank's own text names nothing it should not; selection is the check. (+11 more)

### Community 59 - "launch_application_assist"
Cohesion: 0.17
Nodes (20): pick_variant(), Pick the best of 21 variants from missions, then apply contract rules.      Sinc, _offer(), test_a_fabricated_number_in_the_letter_still_fails(), test_a_review_pending_fact_cannot_be_selected(), test_the_prompt_asks_for_selections_not_prose(), _plan_for(), CV variant routing, 5+1 zone tailoring, and generation orchestration. (+12 more)

### Community 60 - "test_letter_quality.py"
Cohesion: 0.24
Nodes (15): french_de_elision(), Return « de <noun> » or « d'<noun> », applying French elision.      Elides befor, _validate_letter_body(), _letter(), _offer(), Letter quality: French elision and the 'Entreprise' placeholder rejection., test_default_letter_elides_poste_before_vowel(), test_default_letter_uses_votre_entreprise_when_company_unknown() (+7 more)

### Community 61 - "test_mailer.py"
Cohesion: 0.13
Nodes (22): daemon_cmd(), Run ingest + score on a loop (Ctrl-C to stop)., daemon_status(), DaemonStatus, heartbeat_path(), Any, Connection, datetime (+14 more)

### Community 62 - "models.py"
Cohesion: 0.18
Nodes (20): get_or_create_company(), CompanyRecord, _no_real_sleeping(), Connection, MonkeyPatch, Backoff between retries is real seconds; the test suite must not spend them., Only fetch_companies() produces outreach targets, not offer side effects., Task 34.0: a NULL source is backfilled, so the row reaches --targets. (+12 more)

### Community 63 - "reparse_alerts"
Cohesion: 0.16
Nodes (20): _generation_failed_detail(), _InteractiveShapedAdvisor, _offer(), Any, Connection, LogCaptureFixture, Path, _queued_application() (+12 more)

### Community 64 - "test_designation_numbers.py"
Cohesion: 0.17
Nodes (18): fields_from_html(), Connection, Read a page's controls as shapes. Values are stripped before we see them., Whether pressing submit is allowed on this domain. Default: no.      Prefill is, Flip the per-domain submit gate. Deliberately has no global counterpart., set_submit_enabled(), submit_enabled(), Connection (+10 more)

### Community 65 - "test_fact_id_consistency.py"
Cohesion: 0.20
Nodes (15): bank(), _bank_payload(), Path, Task 35 item 2: a fact bank whose claim ids do not extend their entry is invalid, The real bank must satisfy the rule the loader now enforces., This is the exact shape the Baïfall entry had., Projects have the same shape as experience, so they get the same rule., `experience.baifallX` starts with the entry id as a STRING but is a     differen (+7 more)

### Community 66 - "review.py"
Cohesion: 0.20
Nodes (17): application_detail(), applications_by_status(), event_history(), outreach_drafts(), Any, Connection, queued_applications(), Read-only queries shared by review surfaces. (+9 more)

### Community 67 - "ingest_source"
Cohesion: 0.09
Nodes (37): SentenceTransformer, apply_matching_profile_cmd(), Connection, _queue_snapshot(), Apply config/matching_profile.yaml and report what it changed.      Re-scoring i, Count what currently clears the bar, for an honest before/after., Re-evaluate every offer against the new vocabulary.      ``jobpilot score`` only, Score all unscored offers and queue those above threshold. (+29 more)

### Community 68 - "_AnchorParser"
Cohesion: 0.05
Nodes (64): InteractiveTailoringAdvisor, Terminal prompts used when interactive tailoring is selected., CatalogueEntry, default_catalogue(), load_variant_catalogue(), _parse_criteria(), _parse_shortcuts(), Path (+56 more)

### Community 69 - "test_preview.py"
Cohesion: 0.23
Nodes (12): _bullet_budget(), _claim_length(), An experience claim has to fit the CV's one line.  The renderer inserts a select, Every experience bullet the template ships, as (employer, plain text).      Enti, The longest experience bullet the template itself already renders on one line., Derived from the file, not a magic number., Without this the constant could go stale and quietly widen the budget., The renderer inserts these verbatim, so a long one wraps in silence. (+4 more)

### Community 70 - "vocabulary.py"
Cohesion: 0.07
Nodes (37): FastAPI, RefreshRunner, Request, _candidate_name(), _citation_warning(), create_app(), database_connection(), _generation_warnings() (+29 more)

### Community 71 - "UnknownFactIdError"
Cohesion: 0.10
Nodes (41): _alert_source_clause(), Connection, Restrict to one alert source, or to all of them when none is named., Re-derive company / city / workplace / easy-apply for stored alert offers., reparse_alerts(), ReparseResult, parse_linkedin(), Extract jobs from a LinkedIn job-alert email. (+33 more)

### Community 72 - "Baifall Dream Stage - Reference Document (v3)"
Cohesion: 0.17
Nodes (11): Baifall Dream Stage - Reference Document (v3), Bloc HTML de reference (3 bullets), Bullet 1 (commun, accompli) - 167 car., rendu sur 2 lignes, Bullet 2 (commun, nominal, perimetre complet) - 127 car., 1 ligne, Bullet 3 : declinaisons par variante, Context, Principe v3 : perimetre nominal complet, Regle pour la date (+3 more)

### Community 73 - "test_facts.py"
Cohesion: 0.10
Nodes (29): FormField, infer_profile_field(), One control's shape. Deliberately has nowhere to put a typed value., Everything naming this field, with separators folded to spaces.          Real fo, Name the reason this field may never be mapped, or None if it may.      Refused:, Which profile field this control wants, or None to leave it to the human., Record mappings for one manually submitted form. Values are never stored.      C, Every refusal category present in a form, for reporting to the human. (+21 more)

### Community 74 - "test_progress.py"
Cohesion: 0.09
Nodes (38): apply_matching_profile(), load_matching_profile(), MatchingProfile, Write the vocabulary onto the profile singleton. Returns {field: (before, after), The scoring vocabulary, committed to git rather than typed once.      These thre, Load the committed matching vocabulary, failing loudly rather than defaulting., Connection, Path (+30 more)

### Community 75 - "scheduler_status"
Cohesion: 0.27
Nodes (17): _client(), _FakeSource, _offer(), Connection, Exception, TestClient, Dashboard-triggered refresh: single flight, honest per-source results., A source that yields fixed records; no network, no rate limiting needed. (+9 more)

### Community 76 - "schema.sql"
Cohesion: 0.38
Nodes (9): applications, companies, cv_variants, email_queue, events, match_scores, offers, profile (+1 more)

### Community 77 - "test_packaging.py"
Cohesion: 0.22
Nodes (6): Path, Packaging guards: the frozen root-level matcher.py must be importable.  `jobpilo, The real regression: importing from a cwd that is not the repo root.      Run in, Explicit `packages` replaced auto-discovery — keep it from drifting., test_declared_packages_cover_every_source_package(), test_matcher_importable_outside_repo_root()

### Community 78 - "CLAUDE.md - JobPilot project constitution"
Cohesion: 0.25
Nodes (7): CLAUDE.md - JobPilot project constitution, Engineering standards, graphify, Interaction rules for Claude Code, Legal and safety rails (do not remove or weaken), Non-negotiable architecture, What this project is

### Community 79 - "AGENTS.md - JobPilot project constitution"
Cohesion: 0.29
Nodes (6): AGENTS.md - JobPilot project constitution, Engineering standards, Interaction rules for Codex, Legal and safety rails (do not remove or weaken), Non-negotiable architecture, What this project is

### Community 80 - "test_valid_sourced_advice_completes_the_shared_generation_path"
Cohesion: 0.38
Nodes (10): _approve(), Connection, LogCaptureFixture, Path, The asset file calls these false positives outside a full render., The reliable control, per the asset file, so it never becomes advisory., test_a_clean_generation_records_no_orphan_warning(), test_an_orphan_in_the_generated_profile_still_fails() (+2 more)

### Community 81 - "JobPilot prompt pack"
Cohesion: 0.33
Nodes (5): Files, How to use, JobPilot prompt pack, Practical notes, Why it is structured this way

### Community 82 - "JobPilot: kickoff prompt for Claude Code"
Cohesion: 0.33
Nodes (5): Engineering constraints, Existing assets (do not rewrite, build around them), Explicitly OUT of v1 (do not build yet), JobPilot: kickoff prompt for Claude Code, v1 scope, in build order

### Community 83 - "CV Template Manifest"
Cohesion: 0.33
Nodes (5): Alternance Templates (19), Baifall Dream Bullet 3 Variants, CV Template Manifest, Entity-Encoded Templates, Stage Templates (2)

### Community 84 - "generate_cv_pdf.py"
Cohesion: 0.47
Nodes (5): configure_utf8_output(), generate(), main(), Use UTF-8 for CLI output, including on Windows consoles., Render the HTML with Chromium using the skill's fixed PDF settings.

### Community 85 - "test_validate_cv_ai.py"
Cohesion: 0.53
Nodes (5): The post-tailoring script accepts sourced structural edits, not empty content., test_ai_tailoring_allows_one_to_three_rewritten_projects(), test_empty_or_excessive_project_description_still_fails(), test_line_count_is_informational_after_structural_tailoring(), _validator()

### Community 86 - "Phase 06: Review interface (Telegram bot)"
Cohesion: 0.40
Nodes (4): Build, Engineering, Out of scope, Phase 06: Review interface (Telegram bot)

### Community 87 - "test_retry_feedback.py"
Cohesion: 0.17
Nodes (11): bank(), Task 35 item 3: a rejection that says what would have been valid.  Task 22c allo, The regression test for the failure that burned two generations., `experience.` is common to every experience entry. Matching on it would     list, A large entry must not blow the retry prompt., Existing callers and tests match on this prefix; item 3 appends, it does     not, test_a_bad_baifall_id_is_told_a_real_baifall_id(), test_an_unresolvable_id_says_so_plainly_instead_of_dumping_the_bank() (+3 more)

### Community 88 - "record_form_fields"
Cohesion: 0.22
Nodes (4): _AnchorParser, HTMLParser, Collect anchors plus nearby table/list-card text without dependencies., _TextContainer

### Community 89 - "Phase 02: Scraper sources (run after phase 01 is green)"
Cohesion: 0.50
Nodes (3): Out of scope, Phase 02: Scraper sources (run after phase 01 is green), Requirements

### Community 90 - "Phase 03: Apply integration (CV/letter generation bridge)"
Cohesion: 0.50
Nodes (3): Build, Out of scope, Phase 03: Apply integration (CV/letter generation bridge)

### Community 91 - "Phase 04: Cold mail module"
Cohesion: 0.50
Nodes (3): Build, Out of scope, Phase 04: Cold mail module

### Community 92 - "Phase 05: Reply detection + tracker automation"
Cohesion: 0.50
Nodes (3): Build, Out of scope, Phase 05: Reply detection + tracker automation

### Community 93 - "_TextParser"
Cohesion: 0.38
Nodes (13): _client(), Connection, Path, TestClient, Task 36 item 3: read the CV before downloading it.  Reading is the step that dec, Task 34 pinned this. Naming the download must not have widened it., Separate actions, same bytes, same guarded path., _ready_with_artifacts() (+5 more)

### Community 110 - "test_designation_numbers.py"
Cohesion: 0.17
Nodes (16): bank(), _in_bank(), LogCaptureFixture, A standard's digits name a thing; a metric's digits measure one., The anti-fabrication guarantee is not weakened by designation handling., Only the designation's own span is exempt from the number rule., Judge as the letter is judged: no entry, so the whole bank answers., Looking like a standard is not evidence of holding one. (+8 more)

### Community 111 - "_AnchorParser"
Cohesion: 0.05
Nodes (78): Container, FactBank, allowed_numbers(), _bank_parts(), _designation_spans(), letter_scope(), _normalized_number(), _organisation_names() (+70 more)

### Community 112 - "test_ingest_idempotent.py"
Cohesion: 0.06
Nodes (61): Return capability-tier tokens that have tripped generations, by frequency., vocabulary_misses(), GenericVocabularyError, load_generic_vocabulary(), parse_rejections(), Path, ValueError, Three tiers of token, so a category word is not judged like a claim.  A sourced (+53 more)

### Community 113 - "apply_matching_profile_cmd"
Cohesion: 0.25
Nodes (13): ingest_cmd(), Fetch offers from a source (or all sources) into the database., enabled_sources(), _enablement(), is_enabled(), Read config/sources.yaml. Unlisted sources default to enabled., Registered sources that are enabled in config, in registration order., Path (+5 more)

### Community 114 - "mappings_for"
Cohesion: 0.20
Nodes (14): mapping_is_complete(), mappings_for(), put_mapping(), Write one mapping. Rejects a profile_field outside the closed enum., Whether ``domain`` has enough of a mapping to be worth calling a route., LogCaptureFixture, Falling back to manual_open is correct behaviour, not a bug., An arbitrary string is not acceptable — this decides what gets typed in. (+6 more)

### Community 115 - "_TextParser"
Cohesion: 0.17
Nodes (5): _ControlParser, HTMLParser, Strip a generated letter's markup down to what a human would paste., Tiny standard-library parser sufficient to test our simple CSS selectors., _TextParser

### Community 116 - "mappings_for"
Cohesion: 0.12
Nodes (22): ConnectionFactory, source_id(), _backfill_company_source(), ingest_source(), IngestResult, _insert_offer(), Connection, Ingestion orchestrator: pull normalized records from a Source into the DB.  Idem (+14 more)

### Community 117 - "tracker.py"
Cohesion: 0.24
Nodes (10): datetime, counts(), Connection, The tracker: every application, one table, read-only.  Deliberately not a Google, Statuses that actually occur, so the filter offers no dead options., The four numbers worth seeing before the table itself., Monday 00:00 UTC of the current week, as ISO text.      Compared as text against, statuses() (+2 more)

### Community 118 - "parse_rejections"
Cohesion: 0.18
Nodes (10): build_cv_title(), normalise_role_title(), Remove posting metadata while preserving the actual role wording., Build the deterministic CV title used after all advisor providers., Fact-bank loading, review CLI, and deterministic role-title cleaning., test_build_cv_title_uses_clean_role_and_contract_specific_suffix(), test_every_skill_is_explicitly_verified_or_unverified(), test_fact_bank_covers_every_cv_template_and_has_unique_claim_ids() (+2 more)

### Community 119 - "UnknownFactIdError"
Cohesion: 0.22
Nodes (11): Raised when a citation matches no fact id, even after normalisation.      ``sect, Append the legal ids for the section the model got wrong.      When the citation, UnknownFactIdError, _valid_fact_ids_block(), test_a_plain_rejection_still_gets_no_block(), The case that started this: skill.rules.sigma resolves to no entry, so     the s, A rejection that buries the answer in a wall of ids is no more useful     than o, test_a_long_section_is_capped_and_says_so() (+3 more)

### Community 120 - "test_ingest_idempotent.py"
Cohesion: 0.38
Nodes (8): FakeSource, Connection, Re-running ingest must never duplicate rows (constitution idempotency rule)., _sample(), test_company_deduped_across_offers_and_runs(), test_first_run_inserts_all(), test_last_run_at_updated(), test_second_run_inserts_nothing()

### Community 121 - "run_menubar"
Cohesion: 0.11
Nodes (25): Logger, Put text on the system clipboard, or say plainly that it could not.  The manual_, _env_bool(), get_settings(), _path(), Configuration and path resolution. Secrets come from .env only (never mocked)., get_logger(), Central logging setup. Library code logs here; it never uses print(). (+17 more)

### Community 123 - "test_renderer_owned_fields.py"
Cohesion: 0.25
Nodes (7): The guarantees that made four _validate_plan branches unreachable.  Task 39 item, The one input to resolve_header_location that comes from config., _offer_start falls back to « septembre 2026 », so there is always one., test_prose_canonicalization_removes_every_dash_the_letter_gate_looked_for(), test_the_built_title_always_carries_a_start_date(), test_the_built_title_always_carries_its_contract_type(), test_the_profiles_own_fallback_is_itself_an_allowed_region()

### Community 124 - "ApplicationNotQueuedError"
Cohesion: 0.16
Nodes (22): mark_application_sent(), Manual fallback: record an externally-submitted application as sent., _utc_now(), IllegalTransition, log_event(), Connection, ValueError, The single authorized writer of applications.status.  Every status transition MU (+14 more)

### Community 125 - "parse_indeed"
Cohesion: 0.29
Nodes (7): clean_job_url(), parse_indeed(), Return a stable detail URL with email/tracking parameters removed., Extract jobs from an Indeed job-alert email., test_clean_job_url_removes_tracking_parameters(), test_parse_ignores_non_job_links(), test_parse_indeed_extracts_jk_ids()

### Community 126 - "test_sourcing_targets_changes_no_sending_gate"
Cohesion: 0.40
Nodes (3): Which CV was used, who chose it, and what the keyword layer suggested.      Both, The catalogue slug, with any stage suffix removed., VariantDecision

### Community 132 - "observable_controls"
Cohesion: 0.10
Nodes (22): _BaseAdapter, _Control, _controls_from_html(), FillAction, _first_matching_selector(), _Form, _FormParser, _forms_from_html() (+14 more)

## Knowledge Gaps
- **155 isolated node(s):** `applications`, `profile`, `contacts`, `suppression_list`, `offers` (+150 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **20 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `mailer.py` to `_client`, `observable_controls`, `Path`, `test_routing.py`, `wttj.py`, `SourcedBullet`, `france_travail.py`, `_FakePage`, `test_email_alerts.py`, `test_labonnealternance.py`, `Settings`, `.from_mapping`, `test_cold_outreach.py`, `_FakePage`, `OpenAITailoringAdvisor`, `resolve_fact_id`, `ingest_source`, `pick_variant`, `test_mailer.py`, `record_form_fields`, `apply_matching_profile_cmd`, `_TextParser`, `run_menubar`, `_FakeLocator`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `current_status()` connect `_candidate_name` to `create_app`, `test_routing.py`, `mailer.py`, `get_settings`, `connect`, `test_generic_vocabulary.py`, `apply_assist.py`, `test_skim.py`, `RefreshRunner`, `launch_wttj_application`, `_FakePage`, `test_cv_completeness.py`, `_FakePage`, `AnthropicTailoringAdvisor`, `labonnealternance.py`, `reparse_alerts`, `_AnchorParser`, `test_valid_sourced_advice_completes_the_shared_generation_path`, `ApplicationNotQueuedError`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `run_menubar` to `test_email_alerts.py`, `test_labonnealternance.py`, `ingest_source`, `_client`, `create_app`, `test_routing.py`, `mailer.py`, `test_generic_vocabulary.py`, `apply_assist.py`, `test_skim.py`, `OpenAITailoringAdvisor`, `apply_matching_profile_cmd`, `wttj.py`, `SourcedBullet`, `launch_wttj_application`, `test_mailer.py`, `test_fact_id_resolution.py`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 62 inferred relationships involving `Settings` (e.g. with `ApplicantProfile` and `ApplyAdapter`) actually correct?**
  _`Settings` has 62 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `TailoringError` (e.g. with `GenerationWarning` and `_CompleteAdvisor`) actually correct?**
  _`TailoringError` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `_payload()` (e.g. with `.advise()` and `.advise()`) actually correct?**
  _`_payload()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `OfferRecord` (e.g. with `BackfillResult` and `RescoreResult`) actually correct?**
  _`OfferRecord` has 23 INFERRED edges - model-reasoned connections that need verification._