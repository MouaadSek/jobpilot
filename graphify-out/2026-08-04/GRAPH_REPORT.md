# Graph Report - jobpilot  (2026-08-04)

## Corpus Check
- 165 files · ~202,636 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3611 nodes · 8997 edges · 153 communities (122 shown, 31 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 348 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `453498d4`
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
- CompanyRecord
- profile.py
- Phase 02: Scraper sources (run after phase 01 is green)
- Phase 03: Apply integration (CV/letter generation bridge)
- Phase 04: Cold mail module
- Phase 05: Reply detection + tracker automation
- Path
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
- Connection
- apply_matching_profile_cmd
- test_variant_selection.py
- labonnealternance.py
- test_profile_domain_anchor.py
- tracker.py
- _TextParser
- FormField
- test_preview.py
- Any
- _FakeLocator
- Request
- _reject_unsupported_tokens
- gate
- Connection
- 008_applications_generation_warnings.sql
- Path
- test_bullet_ceiling.py
- score
- apply_matching_profile
- observable_controls
- test_registry.py
- apply_matching_profile_cmd
- update.sh
- scheduler_status
- load_generic_vocabulary
- mappings_for
- test_profile_domain_anchor.py
- GmailIMAP
- _Toolchain
- _Advisor
- MailerError
- parse_indeed
- mapping_is_complete
- Connection
- Protocol
- RuntimeError
- StrEnum
- Client
- test_no_fixture_contains_a_credential
- RuntimeError

## God Nodes (most connected - your core abstractions)
1. `Settings` - 111 edges
2. `_payload()` - 91 edges
3. `TailoringError` - 82 edges
4. `current_status()` - 73 edges
5. `load_fact_bank()` - 71 edges
6. `_Toolchain` - 66 edges
7. `OfferRecord` - 65 edges
8. `OfferContext` - 60 edges
9. `pick_variant()` - 60 edges
10. `tailor_cv_html()` - 52 edges

## Surprising Connections (you probably didn't know these)
- `test_the_warning_is_visible_on_the_application_page()` --calls--> `create_app()`  [INFERRED]
  tests/test_drop_unknown_citation.py → src/jobpilot/dashboard.py
- `test_the_detail_page_shows_the_warning_in_amber()` --calls--> `create_app()`  [INFERRED]
  tests/test_generation_warnings.py → src/jobpilot/dashboard.py
- `test_the_library_and_tracker_mark_a_degraded_application()` --calls--> `tracker_rows()`  [INFERRED]
  tests/test_generation_warnings.py → src/jobpilot/tracker.py
- `_FakeIMAP` --uses--> `MissingCredentialError`  [INFERRED]
  tests/test_email_alerts.py → src/jobpilot/config.py
- `_NoWait` --uses--> `MissingCredentialError`  [INFERRED]
  tests/test_labonnealternance.py → src/jobpilot/config.py

## Import Cycles
- None detected.

## Communities (153 total, 31 thin omitted)

### Community 0 - "test_downloads.py"
Cohesion: 0.05
Nodes (41): BaseException, Operation, ProgressRegistry, Any, datetime, Update a running operation. A key that is not running is ignored., Close an operation. The first outcome recorded wins.          A handled failure, Everything running, plus anything that finished very recently. (+33 more)

### Community 1 - "Request"
Cohesion: 0.08
Nodes (55): Resolve one archived artefact, with the same discipline as the live one.      De, _safe_archive_path(), _archives_for(), Generation, is_archive_stamp(), library_entries(), LibraryEntry, _mtime_iso() (+47 more)

### Community 2 - "_candidate_name"
Cohesion: 0.07
Nodes (89): _client(), _days_ago(), _events(), _no_advisor_client(), _offer_application(), Connection, MonkeyPatch, Path (+81 more)

### Community 3 - "_client"
Cohesion: 0.12
Nodes (19): adapter_for_url(), _application_for_assist(), _application_for_wttj(), ApplyAssistError, AssistResult, _fallback(), launch_application_assist(), Connection (+11 more)

### Community 4 - "create_app"
Cohesion: 0.09
Nodes (22): Message, enrich_offer(), is_thin(), Replace a thin description in place; richer descriptions are left alone.      Ca, True when a description is too short to be worth embedding on its own., OfferRecord, One normalized offer, ready to insert into the offers table., Coerce enum-constrained fields to legal values (schema CHECK safety). (+14 more)

### Community 5 - "dashboard.py"
Cohesion: 0.06
Nodes (77): ExperienceFact, FactBank, GenerationWarning, Match, Pattern, _add_tech_additions(), _add_tech_keywords(), _cap_experience_selection() (+69 more)

### Community 6 - "run_dashboard"
Cohesion: 0.12
Nodes (29): drop_unknown_citation(), Remove one unusable citation, or refuse when removing it would weaken the CV., bank(), _dropping_enabled(), _InventsForever, _plan(), Connection, MonkeyPatch (+21 more)

### Community 7 - "Path"
Cohesion: 0.10
Nodes (28): CatalogueEntry, default_catalogue(), load_variant_catalogue(), _parse_criteria(), _parse_shortcuts(), Path, RuntimeError, The CV catalogue offered to the advisor when it selects a variant.  The selectio (+20 more)

### Community 8 - "test_routing.py"
Cohesion: 0.10
Nodes (58): Cursor, _artifacts(), Path, Resolve the one route this application would go out by. Writes nothing., The resolved plan for one application. Carries no state and stores none., Fingerprint of exactly the inputs that decided this route.          Stateless by, resolve_route(), Route (+50 more)

### Community 9 - "mailer.py"
Cohesion: 0.11
Nodes (38): _as_utc(), _build_message(), build_sender(), ColdEmailPreparation, daily_cap_reached(), _default_body(), EmailPreparation, EmailSender (+30 more)

### Community 10 - "validate_cv.py"
Cohesion: 0.06
Nodes (53): check_orphans(), find_regressions(), Path, Return orphan metrics that are new or materially worse than the template., format_date(), main(), build_letter_html(), detect_github() (+45 more)

### Community 11 - "get_settings"
Cohesion: 0.06
Nodes (50): CvProfile, _advise_and_tailor(), _advisor_fact_context(), _correction_block(), DroppedCitation, _infer_region(), _interactive_structured_payload(), _is_validator_rejection() (+42 more)

### Community 12 - "connect"
Cohesion: 0.15
Nodes (22): Apply the mechanical contract and encoding rules to a chosen slug.      These ar, The contract line an adapted alternance CV must carry., The stage contract line to fall back to, built from what is known.      Determin, Preserve a valid contract phrase; replace only a rejected one.      Same shape a, _resolve_stage_contract_phrase(), _stage_contract_fallback(), _validate_stage_contract_phrase(), variant_for_slug() (+14 more)

### Community 13 - "test_descriptions.py"
Cohesion: 0.10
Nodes (50): backfill_descriptions(), BackfillResult, clear_match_scores(), is_synthesized(), Connection, Synthesise matchable text for offers that arrive with no description.  Job-alert, Return an SQL fragment + params restricting a query to one source., Regenerate synthesised descriptions for stored offers whose text is thin.      I (+42 more)

### Community 14 - "test_generic_vocabulary.py"
Cohesion: 0.07
Nodes (51): pick_variant(), Pick the best of 21 variants from missions, then apply contract rules.      Sinc, Validate the one JSON contract shared by every advisor provider., Task 39 demoted this to advisory.      A tool listed under two categories is cos, test_duplicate_tool_across_categories_warns_without_blocking(), unsupported number 27001' was rejecting real, bank-backed vocabulary., test_the_observed_failure_no_longer_fails_a_generation(), _offer() (+43 more)

### Community 15 - "apply_assist.py"
Cohesion: 0.14
Nodes (32): _client(), _days_ago(), _offer_application(), Connection, MonkeyPatch, TestClient, Task 42: what the four lists do with recency, end to end.  tests/test_freshness., The bug: a three-week 0.72 sat above a one-day 0.61 and stayed there. (+24 more)

### Community 16 - "test_skim.py"
Cohesion: 0.15
Nodes (38): ignore_offer(), promote_offer(), Offers that passed the hard filter and scored below the queue threshold.      An, Put a below-threshold offer into the normal review flow. Returns its id., Dismiss a skimmed offer so it stops reappearing. Returns its id.      Persisted, skim_offers(), _client(), _days_ago() (+30 more)

### Community 17 - "contacts.py"
Cohesion: 0.09
Nodes (40): _candidate_name(), ContactCandidate, discover_and_store(), DiscoverySource, draft_cold_email(), draft_linkedin_note(), _get_or_create_cold_application(), is_professional_address() (+32 more)

### Community 18 - "JobPilot — Codex Handoff (complete A-to-Z)"
Cohesion: 0.04
Nodes (45): 10. HARD REJECTIONS (offers the pipeline should auto-skip), 11. API REFERENCES, 12. DESIGN PRINCIPLES (non-negotiable), 13. ENV VARS (.env), 14. GITHUB PUSH (do this FIRST, before any Codex work), 15. CODEX TASK BREAKDOWN (suggested order), 16. BAIFALL DREAM STAGE REFERENCE, 17. SCRIPTS REFERENCE (+37 more)

### Community 19 - "RefreshRunner"
Cohesion: 0.04
Nodes (56): add_contact_cmd(), apply_cmd(), apply_matching_profile_cmd(), backfill_descriptions_cmd(), contacts_cmd(), _csv(), daemon_cmd(), dashboard_cmd() (+48 more)

### Community 20 - "_payload"
Cohesion: 0.09
Nodes (48): _bullets(), _project(), The advisor selects; the renderer inserts the bank's wording unchanged., The pre-written variants from the skill asset, used as the asset intends., The contract has no field for prose, so a writing advisor fails loudly., Only the entry's own facts, so a skill id cannot become a bullet., Task 25's tolerance survives: ids are normalised before they are judged., The phrase is short, but it is still generated, so the tiers still read it. (+40 more)

### Community 21 - "wttj.py"
Cohesion: 0.10
Nodes (41): _city(), _contact_email(), _contract(), _first(), map_hit(), _org(), _prose(), Any (+33 more)

### Community 22 - "SourcedBullet"
Cohesion: 0.08
Nodes (27): ConnectionFactory, Event, IngestResult, Ingestion orchestrator: pull normalized records from a Source into the DB.  Idem, _default_score_pass(), _production_connection(), Any, Connection (+19 more)

### Community 23 - "france_travail.py"
Cohesion: 0.09
Nodes (31): _delay(), Rate limiting + exponential backoff for every external call (constitution rule)., Call fn(); retry on transient HTTP errors with full-jitter exponential backoff., with_backoff(), _first_nonempty(), FranceTravailSource, _map_contact_email(), _map_contract() (+23 more)

### Community 24 - "test_provenance_tiers.py"
Cohesion: 0.08
Nodes (37): bank(), _in_bank(), _offer(), Three kinds of token, three different burdens of proof., Not even the widest scope can support it., The reader has to be able to search for it, or add it to the config., Task 26's handling survives as the digit-shaped corner of tier 2., Presence in the bank is necessary for tier 2, never sufficient. (+29 more)

### Community 25 - "launch_wttj_application"
Cohesion: 0.22
Nodes (25): _cold_draft(), _configure_dashboard(), _dashboard_client(), _event_rows(), Connection, EmailMessage, Exception, MonkeyPatch (+17 more)

### Community 26 - "Dashboard"
Cohesion: 0.05
Nodes (39): Actualiser les offres (refresh from the page), Always up, without a terminal, Architecture (summary), ATS application assist (prefill only), Background scheduling, CI, Cold outreach sending (disabled by default), Commands (+31 more)

### Community 27 - "_FakePage"
Cohesion: 0.10
Nodes (21): ApplyAdapter, _BaseAdapter, GreenhouseAdapter, LeverAdapter, Common adapter interface for a best-effort ATS prefill., Shared plan building and non-submitting form interaction., SmartRecruitersAdapter, _FakeLauncher (+13 more)

### Community 28 - "cli.py"
Cohesion: 0.12
Nodes (42): counts(), Any, Connection, datetime, The tracker: every application, one table, read-only.  Deliberately not a Google, Every offer application, optionally narrowed to one status.      ``include_stale, Statuses that actually occur, so the filter offers no dead options., Export exactly the visible rows, in the visible column order. (+34 more)

### Community 29 - "test_desktop_shell.py"
Cohesion: 0.06
Nodes (52): CaptureFixture, Path, _bound_port(), _fake_macos(), _module_level_imports(), Task 34.C: reaching the dashboard without typing a command.  Nothing here bundle, `jobpilot daemon` heartbeats but nothing kept it alive; launchd does now., Separate labels, separate logs, separate commands.      launchd supervises a lab (+44 more)

### Community 30 - "generate_application"
Cohesion: 0.07
Nodes (33): date, Protocol, build_advisor(), _check_orphans(), _contains_generated_orphan(), DocumentToolchain, _french_date(), generate_application() (+25 more)

### Community 31 - "test_contacts.py"
Cohesion: 0.06
Nodes (52): Client, ModuleType, SimpleNamespace, JobPilot: personal job application pipeline for the French IT/cybersecurity mark, OpenAITailoringAdvisor, OpenAI-compatible Chat Completions adviser., _application(), _ConnectionProxy (+44 more)

### Community 32 - "test_email_alerts.py"
Cohesion: 0.11
Nodes (39): html_of(), LinkedInAlertSource, Return the best HTML (or plain-text) body of an email message., Return the lowercased domain of the address in a `From` header.      Parses the, True when the From address sits on one of `domains` or a subdomain of it., sender_allowed(), sender_domain(), _FakeIMAP (+31 more)

### Community 33 - "test_labonnealternance.py"
Cohesion: 0.12
Nodes (34): _fixture(), _NoWait, LogCaptureFixture, La Bonne Alternance through the API Apprentissage: mapping, rails, ingestion.  E, The endpoint has no pagination, so this is the volume knob that exists., A full ingest reads both lists; it must not pay for the search twice., The live API really does repeat an offer inside one response., A company that has posted nothing must not appear in the review queue. (+26 more)

### Community 34 - "_Toolchain"
Cohesion: 0.11
Nodes (16): HTTPStatusError, RuntimeError, MissingCredentialError, Raised when a required secret is absent. We ask; we never silently mock., RateLimiter, Minimum-delay-per-domain limiter. Blocks until the next call is allowed., LaBonneAlternanceAuthError, LaBonneAlternanceError (+8 more)

### Community 35 - "email_alerts.py"
Cohesion: 0.06
Nodes (50): _advisor_prompt(), extract_template_context(), Read all editable choices without altering the template., Every id the advisor may cite, flattened out of the context it was given.      D, valid_fact_ids(), The model had never been told there was one., test_the_prompt_states_the_ceiling(), Path (+42 more)

### Community 36 - "test_alert_card_fields.py"
Cohesion: 0.10
Nodes (33): as_dicts(), clear_warnings(), _decode(), GenerationWarning, Any, Connection, What a generation had to degrade, recorded where the reviewer will see it.  Task, Gate names per application, for the library and tracker markers.      One query (+25 more)

### Community 37 - "Settings"
Cohesion: 0.05
Nodes (38): CompletedProcess, AmbiguousFactIdError, _canonicalize_prose(), _fact_id_list(), _justification(), _load_offer(), Raised when generated prose states a figure the bank does not contain.      A si, Raised when a citation matches no fact id, even after normalisation.      ``sect (+30 more)

### Community 38 - "Job Application Pipeline"
Cohesion: 0.06
Nodes (31): Alternance vs Stage, Edge Cases & Principles, Encoding note, Execution Flow, Flag once, then execute:, Generate with the bundled script:, GitHub Exception, Hard rejections (no output): (+23 more)

### Community 39 - "matcher.py"
Cohesion: 0.15
Nodes (28): bonus_score(), cosine(), hard_filter(), keyword_score(), norm(), pick_variant(), Profile, Connection (+20 more)

### Community 40 - "test_cv_completeness.py"
Cohesion: 0.09
Nodes (31): CvProfile, load_cv_profile(), Renderer-owned candidate facts injected into every generated CV., The location printed in the CV header when the offer yields none., Load the committed CV profile, failing loudly rather than defaulting., _category_skills(), _CompleteAdvisor, _IncompleteAdvisor (+23 more)

### Community 41 - "OfferRecord"
Cohesion: 0.10
Nodes (24): _fact_id_key(), _guessed_section(), nearest_entry_claim_ids(), Fold separator and case differences, and nothing else, for comparison., Map a cited id onto a real fact id, accepting only unambiguous matches.      Mat, The entry a bad citation came closest to naming, and its real claim ids.      Ne, The section the citation was aiming at, read from its own prefix., Return the plan with every citation rewritten to its canonical fact id.      Pur (+16 more)

### Community 42 - "test_dashboard_facts_scheduler.py"
Cohesion: 0.09
Nodes (34): derive_fields(), _Derived, Re-derive alert card fields (company / city / workplace / easy-apply) in place., Re-derive one offer's card fields from the text that was stored for it.      Pur, _AlertAnchor, _AnchorParser, _anchors(), _Card (+26 more)

### Community 43 - ".from_mapping"
Cohesion: 0.15
Nodes (25): Decision, RouteId, Remove configured secrets from exception text before display/logging., Settings, _applicant_reason(), _ats_prefill(), _email(), _learned_form() (+17 more)

### Community 44 - "test_cold_outreach.py"
Cohesion: 0.24
Nodes (20): mark_application_sent(), Send the application by email, then transition ready -> applied.      Returns th, Manual fallback: record an externally-submitted application as sent., send_application_email(), _utc_now(), _events(), Connection, EmailMessage (+12 more)

### Community 45 - "_FakePage"
Cohesion: 0.24
Nodes (20): _events(), _FakeLauncher, _FakePage, Connection, Path, Row, WTTJ inline application stays human-approved and dry-run by default., _ready_wttj_application() (+12 more)

### Community 46 - "MissingCredentialError"
Cohesion: 0.11
Nodes (39): Exception, Last recorded run per enabled source, with what that run actually did.      ``la, source_runs(), _client(), _fail(), _Fake, _offer(), Connection (+31 more)

### Community 47 - "ats.py"
Cohesion: 0.15
Nodes (23): download_filename(), Download names an employer folder can still be read a week later.  ``output/appl, Reduce free text to ``[A-Za-z0-9-_]``, or to "" if nothing survives.      Accent, Build ``<Company>_<Type>_<Nom>.<ext>`` for one artefact.      Falls back to the, slugify(), _client(), Connection, Path (+15 more)

### Community 48 - "AnthropicTailoringAdvisor"
Cohesion: 0.13
Nodes (18): ApplicantProfile, Whether a stored selector still finds a control on the current page., The non-secret contact values entered into an ATS form., selector_matches_html(), build_prefill(), FormLearningError, FormMapping, PrefillOutcome (+10 more)

### Community 49 - "OpenAITailoringAdvisor"
Cohesion: 0.16
Nodes (20): _all_template_paths(), _bullet_budget(), _claim_length(), _normalized(), _project_desc_budget(), _project_desc_rows(), An experience claim has to fit the CV's one line.  The renderer inserts a select, The widest project description any template already renders. (+12 more)

### Community 50 - "resolve_fact_id"
Cohesion: 0.19
Nodes (19): Any, datetime, age_in_days(), annotate(), describe(), drop_stale(), Freshness, _label() (+11 more)

### Community 51 - "test_tech_additions.py"
Cohesion: 0.15
Nodes (26): bank(), _offer(), LogCaptureFixture, Zone 3 may add a keyword, but only one he has and the offer asked for., Reorder-only remains the default and the common case., Genuinely his, but padding: the offer did not ask for it., Presence in the bank is necessary, never sufficient., Derived from the file, not a magic number. (+18 more)

### Community 52 - "load_fact_bank"
Cohesion: 0.07
Nodes (48): _boolean(), build_cv_title(), CertificationFact, _claim_list(), EducationFact, _entry_claim(), ExperienceFact, FactBank (+40 more)

### Community 53 - "CompanyRecord"
Cohesion: 0.14
Nodes (21): Settings, _consecutive_failures(), daemon_status(), DaemonStatus, heartbeat_path(), _last_runs(), Connection, Path (+13 more)

### Community 54 - "labonnealternance.py"
Cohesion: 0.11
Nodes (17): _InteractiveShapedAdvisor, Human loop: always rejected, and never re-prompted automatically., _InventsThenRecovers, Connection, LogCaptureFixture, Path, Task 37 item 2: give the unknown-id retry something to work with.  An unknown fa, Cites an id that exists nowhere, for a chosen number of attempts. (+9 more)

### Community 55 - "ingest_source"
Cohesion: 0.07
Nodes (50): FastAPI, Freshness, RefreshRunner, _candidate_name(), _citation_warning(), create_app(), dashboard_already_running(), database_connection() (+42 more)

### Community 56 - "pick_variant"
Cohesion: 0.13
Nodes (16): BrowserLauncher, _ConfirmationBaseline, launch_wttj_application(), _Locator, _Page, PrefillPlan, Path, Protocol (+8 more)

### Community 57 - "test_fact_id_resolution.py"
Cohesion: 0.15
Nodes (28): approve_application(), Any, Connection, Record human approval, transition, and generate through one shared path.      ``, invention_report(), How often the advisor cites an id that does not exist, and whether it recovers., Connection, Path (+20 more)

### Community 58 - "test_letter_locked_fields.py"
Cohesion: 0.18
Nodes (19): bank(), _letter(), _offer(), A letter is prose about a career; a CV is slots the renderer fills., Naming a real-sounding employer he never had is a fabrication, not prose., The renderer injects the address block; the body repeating it is a bug., Otherwise the test above would prove nothing about scope., The bank's own text names nothing it should not; selection is the check. (+11 more)

### Community 59 - "launch_application_assist"
Cohesion: 0.15
Nodes (21): ATSSource, infer_contract(), load_targets(), map_greenhouse(), map_lever(), map_smartrecruiters(), _ms_to_iso(), Any (+13 more)

### Community 60 - "test_letter_quality.py"
Cohesion: 0.16
Nodes (21): _default_letter(), french_de_elision(), _omit_offending_paragraph(), _paragraph_offends(), Return « de <noun> » or « d'<noun> », applying French elision.      Elides befor, Whether this one paragraph is what _validate_letter_body refused.      Only the, Drop the one paragraph the letter gate refused, keeping the rest.      The retry, _render_sourced_letter() (+13 more)

### Community 61 - "test_mailer.py"
Cohesion: 0.18
Nodes (17): Connection, Path, Nothing is weakened: a fabrication ends the run exactly as before., test_a_fatal_gate_still_aborts(), test_an_advisory_gate_never_blocks(), test_the_library_and_tracker_mark_a_degraded_application(), _approve(), Connection (+9 more)

### Community 62 - "models.py"
Cohesion: 0.29
Nodes (16): MonkeyPatch, _client(), fixture_bank(), Connection, Path, TestClient, Read-only fact bank page and honest scheduler reporting on the queue page., test_daemon_state_follows_the_recorded_heartbeat_age() (+8 more)

### Community 63 - "reparse_alerts"
Cohesion: 0.21
Nodes (18): current_status(), An invented figure is recoverable — the retry is handed the real ones —     but, test_a_recoverable_gate_with_no_degradation_escalates_to_fatal(), _generation_failed_detail(), Any, Connection, LogCaptureFixture, Path (+10 more)

### Community 64 - "test_designation_numbers.py"
Cohesion: 0.19
Nodes (19): IllegalTransition, log_event(), Connection, ValueError, The single authorized writer of applications.status.  Every status transition MU, Raised when a status change is not permitted by the state machine., Append an audit event. Used for status_change, human_approved, email_sent, etc., Move an application to to_status if legal; log a status_change event.      Retur (+11 more)

### Community 65 - "test_fact_id_consistency.py"
Cohesion: 0.20
Nodes (15): bank(), _bank_payload(), Path, Task 35 item 2: a fact bank whose claim ids do not extend their entry is invalid, The real bank must satisfy the rule the loader now enforces., This is the exact shape the Baïfall entry had., Projects have the same shape as experience, so they get the same rule., `experience.baifallX` starts with the entry id as a STRING but is a     differen (+7 more)

### Community 66 - "review.py"
Cohesion: 0.14
Nodes (17): available_sources(), _create_application(), Connection, datetime, Row, The skim list: offers that passed the hard filter but scored below threshold.  T, The offer row, if it is genuinely one this page may act on., Create the offer's application row in 'queued'.      matcher.score_new_offers ow (+9 more)

### Community 67 - "ingest_source"
Cohesion: 0.07
Nodes (55): AnthropicTailoringAdvisor, InteractiveTailoringAdvisor, Claude Messages API adviser used when ``ANTHROPIC_API_KEY`` is set., Terminal prompts used when interactive tailoring is selected., _Client, _offer(), _plan_payload(), Any (+47 more)

### Community 68 - "_AnchorParser"
Cohesion: 0.19
Nodes (13): CompanyRecord, _backfill_company_source(), ingest_source(), _insert_offer(), Connection, OfferRecord, Source, INSERT OR IGNORE one offer. Returns True if a new row was created. (+5 more)

### Community 69 - "test_preview.py"
Cohesion: 0.14
Nodes (20): FormField, infer_profile_field(), One control's shape. Deliberately has nowhere to put a typed value., Everything naming this field, with separators folded to spaces.          Real fo, Name the reason this field may never be mapped, or None if it may.      Refused:, Which profile field this control wants, or None to leave it to the human., Every refusal category present in a form, for reporting to the human., refusal_category() (+12 more)

### Community 70 - "vocabulary.py"
Cohesion: 0.11
Nodes (20): LookupError, ApplicationGenerationError, ApplicationNotFoundError, ApplicationNotQueuedError, ApplyOutcome, archive_artifacts(), generation_single_flight(), GenerationInFlight (+12 more)

### Community 71 - "UnknownFactIdError"
Cohesion: 0.10
Nodes (33): parse_linkedin(), Extract jobs from a LinkedIn job-alert email., _card_html(), LogCaptureFixture, Structural parsing of job-alert cards (Task 20).  Every fixture here is shaped a, The same four values models.REMOTE_POLICIES defines for every source., Indeed writes "Villeneuve-d'Ascq (59)" — the postcode is not a workplace., Whatever position the chrome occupies, it must not be stored. (+25 more)

### Community 72 - "Baifall Dream Stage - Reference Document (v3)"
Cohesion: 0.17
Nodes (11): Baifall Dream Stage - Reference Document (v3), Bloc HTML de reference (3 bullets), Bullet 1 (commun, accompli) - 167 car., rendu sur 2 lignes, Bullet 2 (commun, nominal, perimetre complet) - 127 car., 1 ligne, Bullet 3 : declinaisons par variante, Context, Principe v3 : perimetre nominal complet, Regle pour la date (+3 more)

### Community 73 - "test_facts.py"
Cohesion: 0.17
Nodes (21): mappings_for(), put_mapping(), Write one mapping. Rejects a profile_field outside the closed enum., Connection, LogCaptureFixture, Task 34.D: form learning — what may be recorded, and what may never be.  This ta, Nothing is written for it, so the next pass re-detects and re-refuses —     whic, Falling back to manual_open is correct behaviour, not a bug. (+13 more)

### Community 74 - "test_progress.py"
Cohesion: 0.06
Nodes (60): apply_matching_profile(), CvProfileError, load_matching_profile(), load_variants(), MatchingProfile, MatchingProfileError, ProfileInput, Connection (+52 more)

### Community 75 - "scheduler_status"
Cohesion: 0.30
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

### Community 87 - "CompanyRecord"
Cohesion: 0.18
Nodes (20): get_or_create_company(), CompanyRecord, _no_real_sleeping(), Connection, MonkeyPatch, Backoff between retries is real seconds; the test suite must not spend them., Only fetch_companies() produces outreach targets, not offer side effects., Task 34.0: a NULL source is backfilled, so the row reaches --targets. (+12 more)

### Community 88 - "profile.py"
Cohesion: 0.06
Nodes (63): Show the tokens that keep failing generations, most frequent first.      Each on, vocab_misses_cmd(), Return capability-tier tokens that have tripped generations, by frequency., vocabulary_misses(), GenericVocabularyError, load_generic_vocabulary(), parse_rejections(), Path (+55 more)

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

### Community 93 - "Path"
Cohesion: 0.25
Nodes (17): _city(), _company_name(), _contract_type(), _domain(), _first(), map_company(), map_offer(), Any (+9 more)

### Community 110 - "test_designation_numbers.py"
Cohesion: 0.17
Nodes (16): bank(), _in_bank(), LogCaptureFixture, A standard's digits name a thing; a metric's digits measure one., The anti-fabrication guarantee is not weakened by designation handling., Only the designation's own span is exempt from the number rule., Judge as the letter is judged: no entry, so the whole bank answers., Looking like a standard is not evidence of holding one. (+8 more)

### Community 111 - "_AnchorParser"
Cohesion: 0.07
Nodes (55): allowed_numbers(), _bank_parts(), letter_scope(), _normalized_number(), _offer_identity(), _organisation_names(), Everything the verified bank says the candidate has actually touched.      Only, The names the bank knows structurally: employers, schools, diplomas.      Naming (+47 more)

### Community 112 - "Connection"
Cohesion: 0.14
Nodes (16): connect(), Open a connection with Row factory, foreign keys, WAL, and a busy timeout., counts(), MenubarUnavailable, Any, Connection, RuntimeError, Optional macOS menu bar item: ready / queued counts, click to open.  ``rumps`` i (+8 more)

### Community 113 - "apply_matching_profile_cmd"
Cohesion: 0.12
Nodes (25): apply_schema(), init_db(), Database connection factory, schema application, and migration runner., Ensure the sources rows exist. Idempotent via INSERT OR IGNORE on unique name., Full initialization: schema + migrations + source seeding., Apply schema.sql. Idempotent: uses CREATE TABLE ... only, so we guard reruns., Apply numbered .sql migrations not yet recorded. Returns count applied.      sch, run_migrations() (+17 more)

### Community 114 - "test_variant_selection.py"
Cohesion: 0.08
Nodes (29): _advise(), ambiguous_bank(), bank(), _offer(), Any, LogCaptureFixture, Path, Citation ids are matched tolerantly; what may be claimed is unchanged. (+21 more)

### Community 115 - "labonnealternance.py"
Cohesion: 0.22
Nodes (16): _alert_source_clause(), Connection, Restrict to one alert source, or to all of them when none is named., Re-derive company / city / workplace / easy-apply for stored alert offers., reparse_alerts(), ReparseResult, Connection, The card line survived in companies.name; the city held only chrome. (+8 more)

### Community 116 - "test_profile_domain_anchor.py"
Cohesion: 0.24
Nodes (11): Connection, test_profile_orphan_recovers_with_template_wording(), Amber, not red: the document is usable, it just needs a look., test_the_detail_page_shows_the_warning_in_amber(), Returns the reference selection payload, unchanged., _SelectingAdvisor, Connection, Path (+3 more)

### Community 117 - "tracker.py"
Cohesion: 0.20
Nodes (12): content_hash(), Normalized DTOs that every source emits, decoupled from source-specific JSON., sha256(lower(title + company + first 500 chars of description)).      This is th, test_content_hash_is_stable_and_case_insensitive(), FakeSource, Connection, Re-running ingest must never duplicate rows (constitution idempotency rule)., _sample() (+4 more)

### Community 118 - "_TextParser"
Cohesion: 0.14
Nodes (6): letter_plain_text(), open_manually(), Strip a generated letter's markup down to what a human would paste., The generated letter as plain text, or '' when it was never generated., The manual_open route: open the offer, copy the letter, submit nothing.      A l, _TextParser

### Community 119 - "FormField"
Cohesion: 0.27
Nodes (14): Connection, EmbedFn, Score all unscored offers. Returns the number newly queued.      The queue thres, score(), _fake_embed(), _insert_offer(), Connection, Scoring wiring: profile embedding cache + end-to-end scoring via a fake embed_fn (+6 more)

### Community 120 - "test_preview.py"
Cohesion: 0.18
Nodes (12): observable_controls(), Every fillable control's *shape*, for form learning. Never its contents.      ``, fields_from_html(), Read a page's controls as shapes. Values are stripped before we see them., Record mappings for one manually submitted form. Values are never stored.      C, record_form_fields(), Scan every column of the table for the sentinel values used above., One enforcement point: values are stripped before this module sees them. (+4 more)

### Community 124 - "_reject_unsupported_tokens"
Cohesion: 0.20
Nodes (15): Container, _designation_spans(), ProvenanceScope, Everything true of the career the generated text is describing.      Generated t, Check every designation against the scope; return what it covers.      Designati, Blank out validated designations, keeping every other offset intact., Build the rejection and record it, so the misses can be counted later.      This, Tier 1. A measurement belongs to the entry it was measured in. (+7 more)

### Community 125 - "gate"
Cohesion: 0.10
Nodes (24): _F, FactClaim, gate(), Label what this function refuses, and what refusing costs.      Attached to the, The tier this failure carries HERE.      An unclassified error is fatal. That de, A selected fact must be a real, reviewed fact OF THAT ENTRY.      This is the wh, What a gate firing is allowed to cost.      Task 39. Seven consecutive generatio, Tier (+16 more)

### Community 129 - "test_bullet_ceiling.py"
Cohesion: 0.19
Nodes (14): bank(), _plan(), Task 40 amendment: bullets had a floor and no ceiling.  _validate_experience_com, The ceiling does not soften the other direction., Floor beats ceiling; a template row count under it cannot make a bad CV., End to end: the renderer inserts what survived, not what was asked for., A plan whose most recent employer selects `facts_for_first` of its facts., The reproduction: nine facts into three rows. (+6 more)

### Community 130 - "score"
Cohesion: 0.07
Nodes (50): Logger, SentenceTransformer, copy_text(), Put text on the system clipboard, or say plainly that it could not.  The manual_, Copy ``text``; return whether it actually landed on the clipboard., _env_bool(), get_settings(), _path() (+42 more)

### Community 132 - "observable_controls"
Cohesion: 0.11
Nodes (26): _Control, _ControlParser, _controls_from_html(), _css_attribute_value(), FillAction, _first_matching_selector(), _Form, _FormParser (+18 more)

### Community 133 - "test_registry.py"
Cohesion: 0.28
Nodes (9): discard_mapping(), Connection, Drop a mapping whose selector no longer matches. Logged, never guessed., Whether pressing submit is allowed on this domain. Default: no.      Prefill is, Flip the per-domain submit gate. Deliberately has no global counterpart., set_submit_enabled(), submit_enabled(), test_the_submit_gate_can_be_closed_again() (+1 more)

### Community 135 - "update.sh"
Cohesion: 0.60
Nodes (3): changed_since_pull(), die(), update.sh script

### Community 136 - "scheduler_status"
Cohesion: 0.14
Nodes (24): Connection, _at(), _offer(), Task 42: recency is first-class, and the age it reports is honest.  France Trava, Some postings state an availability date rather than a posting date., The filter hides what is provably old, not what is merely unlabelled., scraped_at is always after the real posting date, so this age understates     it, A lower bound that already exceeds the limit is proof of age, even though     st (+16 more)

### Community 138 - "mappings_for"
Cohesion: 0.22
Nodes (7): _plan(), Task 41: the header location is found by its own marker, not by its neighbours., The header is a fixed-width line; the span must not consume any of it., The header location is renderer-owned: it comes from the offer's city., The premise of the fix, asserted rather than assumed.      If this ever fails th, test_the_marker_adds_no_visible_text(), test_the_templates_really_do_disagree_on_both_encodings()

### Community 139 - "test_profile_domain_anchor.py"
Cohesion: 0.15
Nodes (17): _extract_profile_domain(), Restore the hand-reviewed template phrase without treating it as AI prose., _restore_template_profile_domain(), test_layout_fallback_restores_each_trusted_template_phrase(), _profile_of(), Path, Task 40: the domain phrase is found by its own marker, not by its neighbours.  _, Not just the wordings we ship: any of them, including ones nobody wrote yet. (+9 more)

### Community 141 - "_Toolchain"
Cohesion: 0.29
Nodes (7): Request, _posted_body(), _posted_cold_send(), _posted_plan_hash(), Read the ``body`` field from a urlencoded POST without python-multipart.      Ru, Read the plan_hash the confirmation page put in the form., Read editable body and the named-mailbox confirmation checkbox.

### Community 142 - "_Advisor"
Cohesion: 0.19
Nodes (9): End to end, on the failure that killed applications 25 and 28.      The live re-, test_a_stage_generation_completes_when_the_model_omits_the_phrase(), _Advisor, _application(), Connection, Path, test_generation_failure_returns_application_to_queue(), test_generation_runs_quality_gates_before_pdfs_and_moves_to_ready() (+1 more)

### Community 144 - "parse_indeed"
Cohesion: 0.29
Nodes (7): clean_job_url(), parse_indeed(), Return a stable detail URL with email/tracking parameters removed., Extract jobs from an Indeed job-alert email., test_clean_job_url_removes_tracking_parameters(), test_parse_ignores_non_job_links(), test_parse_indeed_extracts_jk_ids()

### Community 145 - "mapping_is_complete"
Cohesion: 0.50
Nodes (5): mapping_is_complete(), Whether ``domain`` has enough of a mapping to be worth calling a route., has_form_mapping(), Whether a *complete* learned mapping exists for ``domain``.      Complete means, test_a_learned_domain_becomes_routable()

### Community 150 - "Client"
Cohesion: 0.50
Nodes (4): ColdSendDisabled, A rail (suppression list or daily cap) refuses the send. Not a failure., Live cold sending is disabled by configuration., SendBlocked

## Knowledge Gaps
- **158 isolated node(s):** `Requirements`, `macOS / Linux`, `Windows PowerShell`, `Configuration`, `CV variant selection` (+153 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **31 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `.from_mapping` to `score`, `_client`, `observable_controls`, `create_app`, `test_routing.py`, `mailer.py`, `wttj.py`, `Client`, `france_travail.py`, `_FakePage`, `test_email_alerts.py`, `test_labonnealternance.py`, `_Toolchain`, `test_dashboard_facts_scheduler.py`, `test_cold_outreach.py`, `_FakePage`, `AnthropicTailoringAdvisor`, `pick_variant`, `launch_application_assist`, `Path`, `_TextParser`, `_FakeLocator`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **Why does `current_status()` connect `reparse_alerts` to `test_designation_numbers.py`, `_candidate_name`, `ingest_source`, `vocabulary.py`, `run_dashboard`, `test_cv_completeness.py`, `mailer.py`, `test_routing.py`, `test_cold_outreach.py`, `_FakePage`, `_Advisor`, `test_profile_domain_anchor.py`, `labonnealternance.py`, `test_fact_id_resolution.py`, `_FakePage`, `test_mailer.py`, `launch_wttj_application`, `test_contacts.py`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `score` to `test_email_alerts.py`, `_client`, `observable_controls`, `run_dashboard`, `test_routing.py`, `mailer.py`, `.from_mapping`, `test_cold_outreach.py`, `resolve_fact_id`, `FormField`, `wttj.py`, `_TextParser`, `SourcedBullet`, `pick_variant`, `launch_wttj_application`, `test_fact_id_resolution.py`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Are the 61 inferred relationships involving `Settings` (e.g. with `ApplicantProfile` and `ApplyAdapter`) actually correct?**
  _`Settings` has 61 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `_payload()` (e.g. with `_plan()` and `.advise()`) actually correct?**
  _`_payload()` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `TailoringError` (e.g. with `_CompleteAdvisor` and `_IncompleteAdvisor`) actually correct?**
  _`TailoringError` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `current_status()` (e.g. with `test_a_fatal_gate_still_aborts()` and `test_a_recoverable_gate_with_no_degradation_escalates_to_fatal()`) actually correct?**
  _`current_status()` has 3 INFERRED edges - model-reasoned connections that need verification._