# Graph Report - jobpilot  (2026-08-03)

## Corpus Check
- 149 files · ~182,465 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3252 nodes · 8368 edges · 136 communities (117 shown, 19 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 344 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e777bcc5`
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
- UnknownFactIdError
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
- vocabulary_misses
- approve_application
- mappings_for
- test_progress.py
- parse_rejections
- .finish
- _Toolchain
- run_menubar
- _Advisor
- format_fact_bank
- ApplicationNotQueuedError
- vocabulary.py
- test_sourcing_targets_changes_no_sending_gate
- _Advisor
- _plan_for
- apply_matching_profile_cmd
- _plan
- Any
- observable_controls
- Protocol
- RuntimeError
- _Toolchain

## God Nodes (most connected - your core abstractions)
1. `Settings` - 117 edges
2. `current_status()` - 92 edges
3. `_payload()` - 84 edges
4. `TailoringError` - 77 edges
5. `OfferRecord` - 68 edges
6. `create_app()` - 61 edges
7. `load_fact_bank()` - 60 edges
8. `get_settings()` - 58 edges
9. `pick_variant()` - 55 edges
10. `_Toolchain` - 55 edges

## Surprising Connections (you probably didn't know these)
- `_CompleteAdvisor` --uses--> `TailoringError`  [INFERRED]
  tests/test_cv_completeness.py → src/jobpilot/tailoring.py
- `_IncompleteAdvisor` --uses--> `TailoringError`  [INFERRED]
  tests/test_cv_completeness.py → src/jobpilot/tailoring.py
- `_RecordingToolchain` --uses--> `TailoringError`  [INFERRED]
  tests/test_cv_completeness.py → src/jobpilot/tailoring.py
- `_BadSourceAdvisor` --uses--> `TailoringError`  [INFERRED]
  tests/test_fact_id_resolution.py → src/jobpilot/tailoring.py
- `_RecordingAdvisor` --uses--> `TailoringError`  [INFERRED]
  tests/test_fact_id_resolution.py → src/jobpilot/tailoring.py

## Import Cycles
- None detected.

## Communities (136 total, 19 thin omitted)

### Community 0 - "test_downloads.py"
Cohesion: 0.14
Nodes (14): ProgressRegistry, Report one operation for as long as it runs, however it ends.      ``with track(, Every operation currently worth reporting, keyed by a stable string., track, _utc_now(), It stays briefly so a poll landing just after completion sees the     outcome, t, A failure that never cleared its progress would leave the page claiming     work, test_a_failure_closes_the_operation_and_keeps_its_message() (+6 more)

### Community 1 - "Request"
Cohesion: 0.08
Nodes (55): Resolve one archived artefact, with the same discipline as the live one.      De, _safe_archive_path(), _archives_for(), Generation, is_archive_stamp(), library_entries(), LibraryEntry, _mtime_iso() (+47 more)

### Community 2 - "_candidate_name"
Cohesion: 0.07
Nodes (88): SimpleNamespace, _client(), _events(), _no_advisor_client(), _offer_application(), Connection, MonkeyPatch, Path (+80 more)

### Community 3 - "_client"
Cohesion: 0.12
Nodes (22): _application_for_assist(), _application_for_wttj(), ApplyAssistError, AssistResult, _fallback(), launch_application_assist(), launch_wttj_application(), _open_for_human() (+14 more)

### Community 4 - "create_app"
Cohesion: 0.05
Nodes (66): add_contact_cmd(), apply_cmd(), backfill_descriptions_cmd(), contacts_cmd(), _csv(), dashboard_cmd(), draft_cold_cmd(), init_db_cmd() (+58 more)

### Community 5 - "dashboard.py"
Cohesion: 0.10
Nodes (56): CvProfile, Match, Pattern, RuntimeError, _add_tech_additions(), _add_tech_keywords(), _contains(), _contains_any() (+48 more)

### Community 6 - "run_dashboard"
Cohesion: 0.18
Nodes (17): _dropping_enabled(), _InventsForever, Connection, MonkeyPatch, Path, Task 37 item 3: degradation, shipped OFF.  If the advisor still cites an id that, Exactly three projects are required, each with its single fact., The shipped default: nothing is dropped and the generation fails. (+9 more)

### Community 7 - "Path"
Cohesion: 0.11
Nodes (28): _backfill_company_source(), get_or_create_company(), Connection, Ingestion orchestrator: pull normalized records from a Source into the DB.  Idem, Teach an existing company row where it came from, once.      A company first see, CompanyRecord, Normalized DTOs that every source emits, decoupled from source-specific JSON., _Derived (+20 more)

### Community 8 - "test_routing.py"
Cohesion: 0.11
Nodes (55): Cursor, _artifacts(), Path, Resolve the one route this application would go out by. Writes nothing., resolve_route(), _client(), Connection, MonkeyPatch (+47 more)

### Community 9 - "mailer.py"
Cohesion: 0.10
Nodes (41): _as_utc(), _build_message(), ColdSendDisabled, daily_cap_reached(), _default_body(), EmailPreparation, EmailSender, _has_human_approval() (+33 more)

### Community 10 - "validate_cv.py"
Cohesion: 0.06
Nodes (53): check_orphans(), find_regressions(), Path, Return orphan metrics that are new or materially worse than the template., format_date(), main(), build_letter_html(), detect_github() (+45 more)

### Community 11 - "get_settings"
Cohesion: 0.13
Nodes (15): _fact_id_key(), Fold separator and case differences, and nothing else, for comparison., Map a cited id onto a real fact id, accepting only unambiguous matches.      Mat, resolve_fact_id(), LogCaptureFixture, The reported failure: 'unknown skill fact id: azure.sentinel'., skill_order can only mean a skill, so its own prefix settles the match., Resembling what a fact is about is not evidence the model read that fact. (+7 more)

### Community 12 - "connect"
Cohesion: 0.22
Nodes (7): Connection, Path, test_a_rejected_number_is_counted_separately_from_an_invented_id(), _OneShotProfileOrphan, Path, A profile-only layout regression that disappears with template wording., _Toolchain

### Community 13 - "test_descriptions.py"
Cohesion: 0.10
Nodes (50): backfill_descriptions(), BackfillResult, clear_match_scores(), is_synthesized(), Connection, Synthesise matchable text for offers that arrive with no description.  Job-alert, Return an SQL fragment + params restricting a query to one source., Regenerate synthesised descriptions for stored offers whose text is thin.      I (+42 more)

### Community 14 - "test_generic_vocabulary.py"
Cohesion: 0.14
Nodes (13): _AlertAnchor, _AnchorParser, _anchors(), clean_job_url(), parse_indeed(), HTMLParser, Collect anchors plus nearby table/list-card text without dependencies., Return a stable detail URL with email/tracking parameters removed. (+5 more)

### Community 15 - "apply_assist.py"
Cohesion: 0.32
Nodes (15): _events(), Connection, EmailMessage, Exception, Path, Application email sending: rails, transitions, and events (mocked SMTP)., _ready_app(), _Sender (+7 more)

### Community 16 - "test_skim.py"
Cohesion: 0.17
Nodes (34): promote_offer(), Offers that passed the hard filter and scored below the queue threshold.      An, Put a below-threshold offer into the normal review flow. Returns its id., skim_offers(), _client(), _events(), _offer(), Connection (+26 more)

### Community 17 - "contacts.py"
Cohesion: 0.09
Nodes (40): _candidate_name(), ContactCandidate, discover_and_store(), DiscoverySource, draft_cold_email(), draft_linkedin_note(), _get_or_create_cold_application(), is_professional_address() (+32 more)

### Community 18 - "JobPilot — Codex Handoff (complete A-to-Z)"
Cohesion: 0.04
Nodes (45): 10. HARD REJECTIONS (offers the pipeline should auto-skip), 11. API REFERENCES, 12. DESIGN PRINCIPLES (non-negotiable), 13. ENV VARS (.env), 14. GITHUB PUSH (do this FIRST, before any Codex work), 15. CODEX TASK BREAKDOWN (suggested order), 16. BAIFALL DREAM STAGE REFERENCE, 17. SCRIPTS REFERENCE (+37 more)

### Community 19 - "RefreshRunner"
Cohesion: 0.12
Nodes (18): enrich_offer(), is_thin(), Replace a thin description in place; richer descriptions are left alone.      Ca, True when a description is too short to be worth embedding on its own., OfferRecord, One normalized offer, ready to insert into the offers table., Coerce enum-constrained fields to legal values (schema CHECK safety)., Yield normalized offers. Must apply rate limiting + backoff internally. (+10 more)

### Community 20 - "_payload"
Cohesion: 0.09
Nodes (49): _plan(), The spec said "at least one remaining bullet" is enough. It is not: the     Task, skill_order has no minimum, so losing one weakens nothing structural., test_a_bullet_can_be_dropped_while_the_entry_stays_above_its_floor(), test_a_recent_employer_may_not_fall_to_one_bullet(), test_a_skill_can_be_dropped(), test_an_unrecognised_citation_is_never_dropped(), _bullets() (+41 more)

### Community 21 - "wttj.py"
Cohesion: 0.10
Nodes (41): _city(), _contact_email(), _contract(), _first(), map_hit(), _org(), _prose(), Any (+33 more)

### Community 22 - "SourcedBullet"
Cohesion: 0.10
Nodes (28): ConnectionFactory, Event, IngestResult, _default_model_loader(), _default_score_pass(), _production_connection(), Any, Connection (+20 more)

### Community 23 - "france_travail.py"
Cohesion: 0.10
Nodes (24): _first_nonempty(), FranceTravailSource, _map_contact_email(), _map_contract(), _map_duration_months(), map_offer(), Any, Parse '... - 12 Mois' style durations from typeContratLibelle. (+16 more)

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
Cohesion: 0.10
Nodes (21): ApplyAdapter, _BaseAdapter, GreenhouseAdapter, LeverAdapter, Common adapter interface for a best-effort ATS prefill., Shared plan building and non-submitting form interaction., SmartRecruitersAdapter, _FakeLauncher (+13 more)

### Community 28 - "cli.py"
Cohesion: 0.12
Nodes (42): counts(), Any, Connection, datetime, The tracker: every application, one table, read-only.  Deliberately not a Google, Every offer application, optionally narrowed to one status., Statuses that actually occur, so the filter offers no dead options., Export exactly the visible rows, in the visible column order. (+34 more)

### Community 29 - "test_desktop_shell.py"
Cohesion: 0.08
Nodes (32): CaptureFixture, dashboard_already_running(), Whether something is already listening on the dashboard's port.      A connect p, The menu bar text. Short: it competes with every other item up there., title(), _bound_port(), _fake_macos(), _module_level_imports() (+24 more)

### Community 30 - "generate_application"
Cohesion: 0.08
Nodes (25): CompletedProcess, date, Protocol, _check_orphans(), _contains_generated_orphan(), DocumentToolchain, _french_date(), generate_application() (+17 more)

### Community 31 - "test_contacts.py"
Cohesion: 0.10
Nodes (27): ModuleType, JobPilot: personal job application pipeline for the French IT/cybersecurity mark, _application(), _ConnectionProxy, Connection, Exception, Path, CLI coverage for offer document generation and cold-application approval. (+19 more)

### Community 32 - "test_email_alerts.py"
Cohesion: 0.14
Nodes (32): html_of(), LinkedInAlertSource, Return the best HTML (or plain-text) body of an email message., _FakeIMAP, _fixture_message(), _msg(), Connection, EmailMessage (+24 more)

### Community 33 - "test_labonnealternance.py"
Cohesion: 0.13
Nodes (33): _fixture(), _NoWait, LogCaptureFixture, La Bonne Alternance through the API Apprentissage: mapping, rails, ingestion.  E, The endpoint has no pagination, so this is the volume knob that exists., A full ingest reads both lists; it must not pay for the search twice., The live API really does repeat an offer inside one response., A company that has posted nothing must not appear in the review queue. (+25 more)

### Community 34 - "_Toolchain"
Cohesion: 0.07
Nodes (33): _correction_block(), _offer_identity(), OfferContext, Apply the mechanical contract and encoding rules to a chosen slug.      These ar, The parsed fields a letter is entitled to say back to its reader.      An unname, The advisor's reasoned CV pick, before any mechanical contract rule., Validate a selection answer. The model may not invent a variant., Offer data exposed to an automatic or interactive tailoring adviser. (+25 more)

### Community 35 - "email_alerts.py"
Cohesion: 0.07
Nodes (37): extract_template_context(), Read all editable choices without altering the template., Every id the advisor may cite, flattened out of the context it was given.      D, valid_fact_ids(), Connection, test_profile_orphan_recovers_with_template_wording(), _offer(), test_the_prompt_asks_for_selections_not_prose() (+29 more)

### Community 36 - "test_alert_card_fields.py"
Cohesion: 0.14
Nodes (5): letter_plain_text(), Path, Strip a generated letter's markup down to what a human would paste., The generated letter as plain text, or '' when it was never generated., _TextParser

### Community 37 - "Settings"
Cohesion: 0.13
Nodes (16): HTTPStatusError, MissingCredentialError, RuntimeError, Raised when a required secret is absent. We ask; we never silently mock., RateLimiter, Minimum-delay-per-domain limiter. Blocks until the next call is allowed., LaBonneAlternanceAuthError, LaBonneAlternanceError (+8 more)

### Community 38 - "Job Application Pipeline"
Cohesion: 0.06
Nodes (31): Alternance vs Stage, Edge Cases & Principles, Encoding note, Execution Flow, Flag once, then execute:, Generate with the bundled script:, GitHub Exception, Hard rejections (no output): (+23 more)

### Community 39 - "matcher.py"
Cohesion: 0.15
Nodes (28): bonus_score(), cosine(), hard_filter(), keyword_score(), norm(), pick_variant(), Profile, Connection (+20 more)

### Community 40 - "test_cv_completeness.py"
Cohesion: 0.12
Nodes (24): _category_skills(), _CompleteAdvisor, Any, Connection, Path, _Toolchain, _queued_application(), Structural completeness floor for AI-generated CVs (Task 22).  Selection freedom (+16 more)

### Community 41 - "OfferRecord"
Cohesion: 0.18
Nodes (16): _advise(), ambiguous_bank(), bank(), _offer(), Any, Path, Citation ids are matched tolerantly; what may be claimed is unchanged., A tool absent from the bank, in the letter the advisor still writes.      Splunk (+8 more)

### Community 42 - "test_dashboard_facts_scheduler.py"
Cohesion: 0.29
Nodes (16): _client(), fixture_bank(), Connection, MonkeyPatch, Path, TestClient, Read-only fact bank page and honest scheduler reporting on the queue page., test_daemon_state_follows_the_recorded_heartbeat_age() (+8 more)

### Community 43 - ".from_mapping"
Cohesion: 0.09
Nodes (32): OpenAITailoringAdvisor, OpenAI-compatible Chat Completions adviser., Validate the one JSON contract shared by every advisor provider., _tailor(), _experience_content(), _FabricatingAdvisor, _gemini_shaped_payload(), _offer() (+24 more)

### Community 44 - "test_cold_outreach.py"
Cohesion: 0.15
Nodes (21): ATSSource, infer_contract(), load_targets(), map_greenhouse(), map_lever(), map_smartrecruiters(), _ms_to_iso(), Any (+13 more)

### Community 45 - "_FakePage"
Cohesion: 0.24
Nodes (20): _events(), _FakeLauncher, _FakePage, Connection, Path, Row, WTTJ inline application stays human-approved and dry-run by default., _ready_wttj_application() (+12 more)

### Community 46 - "MissingCredentialError"
Cohesion: 0.08
Nodes (41): Client, AnthropicTailoringAdvisor, Claude Messages API adviser used when ``ANTHROPIC_API_KEY`` is set., _Client, _offer(), _plan_payload(), Any, Exception (+33 more)

### Community 47 - "ats.py"
Cohesion: 0.15
Nodes (23): download_filename(), Download names an employer folder can still be read a week later.  ``output/appl, Reduce free text to ``[A-Za-z0-9-_]``, or to "" if nothing survives.      Accent, Build ``<Company>_<Type>_<Nom>.<ext>`` for one artefact.      Falls back to the, slugify(), _client(), Connection, Path (+15 more)

### Community 48 - "AnthropicTailoringAdvisor"
Cohesion: 0.14
Nodes (24): pick_variant(), Pick the best of 21 variants from missions, then apply contract rules.      Sinc, unsupported number 27001' was rejecting real, bank-backed vocabulary., test_the_observed_failure_no_longer_fails_a_generation(), rendered(), _offer(), Systemic recovery at the generated-prose and document-layout boundaries., Naming the employer is what a motivation letter does.      The rule was never lo (+16 more)

### Community 49 - "OpenAITailoringAdvisor"
Cohesion: 0.09
Nodes (33): Decision, RouteId, open_manually(), The manual_open route: open the offer, copy the letter, submit nothing.      A l, Remove configured secrets from exception text before display/logging., Settings, build_sender(), Default STARTTLS SMTP sender built from settings. (+25 more)

### Community 50 - "resolve_fact_id"
Cohesion: 0.16
Nodes (20): FormMapping, mapping_is_complete(), mappings_for(), put_mapping(), Connection, A stored selector -> profile field mapping. Never a stored value., Write one mapping. Rejects a profile_field outside the closed enum., Whether ``domain`` has enough of a mapping to be worth calling a route. (+12 more)

### Community 51 - "test_tech_additions.py"
Cohesion: 0.15
Nodes (26): bank(), _offer(), LogCaptureFixture, Zone 3 may add a keyword, but only one he has and the offer asked for., Reorder-only remains the default and the common case., Genuinely his, but padding: the offer did not ask for it., Presence in the bank is necessary, never sufficient., Derived from the file, not a magic number. (+18 more)

### Community 52 - "load_fact_bank"
Cohesion: 0.08
Nodes (44): facts_cmd(), Print the provenance fact bank grouped for human review., _boolean(), build_cv_title(), CertificationFact, _claim_list(), EducationFact, _entry_claim() (+36 more)

### Community 53 - "CompanyRecord"
Cohesion: 0.06
Nodes (57): ExperienceFact, FactBank, FactClaim, _advise_and_tailor(), _advisor_fact_context(), _contact_fields(), _cv_locked_fields(), drop_unknown_citation() (+49 more)

### Community 54 - "labonnealternance.py"
Cohesion: 0.11
Nodes (17): _InteractiveShapedAdvisor, Human loop: always rejected, and never re-prompted automatically., _InventsThenRecovers, Connection, LogCaptureFixture, Path, Task 37 item 2: give the unknown-id retry something to work with.  An unknown fa, Cites an id that exists nowhere, for a chosen number of attempts. (+9 more)

### Community 55 - "ingest_source"
Cohesion: 0.13
Nodes (18): ApplicantProfile, Whether a stored selector still finds a control on the current page., The non-secret contact values entered into an ATS form., selector_matches_html(), build_prefill(), discard_mapping(), FormLearningError, PrefillOutcome (+10 more)

### Community 56 - "pick_variant"
Cohesion: 0.13
Nodes (15): BrowserLauncher, _ConfirmationBaseline, _css_attribute_value(), _identity(), _Locator, _Page, PrefillPlan, Protocol (+7 more)

### Community 57 - "test_fact_id_resolution.py"
Cohesion: 0.10
Nodes (41): approve_application(), Any, Connection, Record human approval, transition, and generate through one shared path.      ``, invention_report(), How often the advisor cites an id that does not exist, and whether it recovers., _Invents, Connection (+33 more)

### Community 58 - "test_letter_locked_fields.py"
Cohesion: 0.18
Nodes (19): bank(), _letter(), _offer(), A letter is prose about a career; a CV is slots the renderer fills., Naming a real-sounding employer he never had is a fabrication, not prose., The renderer injects the address block; the body repeating it is a bug., Otherwise the test above would prove nothing about scope., The bank's own text names nothing it should not; selection is the check. (+11 more)

### Community 59 - "launch_application_assist"
Cohesion: 0.16
Nodes (19): fields_from_html(), Read a page's controls as shapes. Values are stripped before we see them., Whether pressing submit is allowed on this domain. Default: no.      Prefill is, Flip the per-domain submit gate. Deliberately has no global counterpart., set_submit_enabled(), submit_enabled(), Connection, Task 34.D: form learning — what may be recorded, and what may never be.  This ta (+11 more)

### Community 60 - "test_letter_quality.py"
Cohesion: 0.22
Nodes (17): _default_letter(), french_de_elision(), Return « de <noun> » or « d'<noun> », applying French elision.      Elides befor, _render_sourced_letter(), _validate_letter_body(), _letter(), _offer(), Letter quality: French elision and the 'Entreprise' placeholder rejection. (+9 more)

### Community 61 - "test_mailer.py"
Cohesion: 0.13
Nodes (22): daemon_cmd(), Run ingest + score on a loop (Ctrl-C to stop)., daemon_status(), DaemonStatus, heartbeat_path(), Any, Connection, datetime (+14 more)

### Community 62 - "models.py"
Cohesion: 0.17
Nodes (22): _city(), _company_name(), _contract_type(), _domain(), _first(), map_company(), map_offer(), Any (+14 more)

### Community 63 - "reparse_alerts"
Cohesion: 0.14
Nodes (18): available_sources(), _create_application(), ignore_offer(), Connection, Row, ValueError, The skim list: offers that passed the hard filter but scored below threshold.  T, The offer row, if it is genuinely one this page may act on. (+10 more)

### Community 64 - "test_designation_numbers.py"
Cohesion: 0.14
Nodes (20): Container, _designation_spans(), _proper_nouns(), ProvenanceScope, Everything true of the career the generated text is describing.      Generated t, Check every designation against the scope; return what it covers.      Designati, Blank out validated designations, keeping every other offset intact., Named things in the text, as {matched form: as written}.      The written form i (+12 more)

### Community 65 - "test_fact_id_consistency.py"
Cohesion: 0.20
Nodes (15): bank(), _bank_payload(), Path, Task 35 item 2: a fact bank whose claim ids do not extend their entry is invalid, The real bank must satisfy the rule the loader now enforces., This is the exact shape the Baïfall entry had., Projects have the same shape as experience, so they get the same rule., `experience.baifallX` starts with the entry id as a STRING but is a     differen (+7 more)

### Community 66 - "UnknownFactIdError"
Cohesion: 0.15
Nodes (11): AmbiguousFactIdError, Raised when a citation matches no fact id, even after normalisation.      ``sect, Raised when a citation could be several facts. Never guess between them., UnknownFactIdError, _BadSourceAdvisor, Cites a prefix-less unknown id first, then whatever the retry was told., Cites an unresolvable id in a letter paragraph, where no section is implied., _RecordingAdvisor (+3 more)

### Community 67 - "ingest_source"
Cohesion: 0.20
Nodes (12): source_id(), _insert_offer(), INSERT OR IGNORE one offer. Returns True if a new row was created., _utc_now(), content_hash(), sha256(lower(title + company + first 500 chars of description)).      This is th, _offer(), Connection (+4 more)

### Community 68 - "_AnchorParser"
Cohesion: 0.05
Nodes (64): InteractiveTailoringAdvisor, Terminal prompts used when interactive tailoring is selected., CatalogueEntry, default_catalogue(), load_variant_catalogue(), _parse_criteria(), _parse_shortcuts(), Path (+56 more)

### Community 69 - "test_preview.py"
Cohesion: 0.23
Nodes (12): _bullet_budget(), _claim_length(), An experience claim has to fit the CV's one line.  The renderer inserts a select, Every experience bullet the template ships, as (employer, plain text).      Enti, The longest experience bullet the template itself already renders on one line., Derived from the file, not a magic number., Without this the constant could go stale and quietly widen the budget., The renderer inserts these verbatim, so a long one wraps in silence. (+4 more)

### Community 70 - "vocabulary.py"
Cohesion: 0.06
Nodes (61): FastAPI, LookupError, Request, ApplicationGenerationError, ApplicationNotFoundError, ApplicationNotQueuedError, ApplyOutcome, archive_artifacts() (+53 more)

### Community 71 - "UnknownFactIdError"
Cohesion: 0.11
Nodes (31): parse_linkedin(), Extract jobs from a LinkedIn job-alert email., _card_html(), LogCaptureFixture, Structural parsing of job-alert cards (Task 20).  Every fixture here is shaped a, The same four values models.REMOTE_POLICIES defines for every source., Indeed writes "Villeneuve-d'Ascq (59)" — the postcode is not a workplace., Whatever position the chrome occupies, it must not be stored. (+23 more)

### Community 72 - "Baifall Dream Stage - Reference Document (v3)"
Cohesion: 0.17
Nodes (11): Baifall Dream Stage - Reference Document (v3), Bloc HTML de reference (3 bullets), Bullet 1 (commun, accompli) - 167 car., rendu sur 2 lignes, Bullet 2 (commun, nominal, perimetre complet) - 127 car., 1 ligne, Bullet 3 : declinaisons par variante, Context, Principe v3 : perimetre nominal complet, Regle pour la date (+3 more)

### Community 73 - "test_facts.py"
Cohesion: 0.11
Nodes (26): FormField, infer_profile_field(), One control's shape. Deliberately has nowhere to put a typed value., Everything naming this field, with separators folded to spaces.          Real fo, Name the reason this field may never be mapped, or None if it may.      Refused:, Which profile field this control wants, or None to leave it to the human., Record mappings for one manually submitted form. Values are never stored.      C, Every refusal category present in a form, for reporting to the human. (+18 more)

### Community 74 - "test_progress.py"
Cohesion: 0.05
Nodes (65): apply_matching_profile(), CvProfile, CvProfileError, load_cv_profile(), load_matching_profile(), load_variants(), MatchingProfile, MatchingProfileError (+57 more)

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
Cohesion: 0.26
Nodes (12): _approve(), Connection, LogCaptureFixture, Path, Returns the reference selection payload, unchanged., The asset file calls these false positives outside a full render., The reliable control, per the asset file, so it never becomes advisory., _SelectingAdvisor (+4 more)

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
Cohesion: 0.13
Nodes (15): nearest_entry_claim_ids(), The entry a bad citation came closest to naming, and its real claim ids.      Ne, _shared_prefix(), bank(), Task 35 item 3: a rejection that says what would have been valid.  Task 22c allo, The regression test for the failure that burned two generations., `experience.` is common to every experience entry. Matching on it would     list, A large entry must not blow the retry prompt. (+7 more)

### Community 88 - "record_form_fields"
Cohesion: 0.11
Nodes (29): derive_fields(), Re-derive one offer's card fields from the text that was stored for it.      Pur, _Card, _card_fields(), CardFields, is_noise(), is_title_echo(), parse_card_line() (+21 more)

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
Cohesion: 0.22
Nodes (16): _alert_source_clause(), Connection, Restrict to one alert source, or to all of them when none is named., Re-derive company / city / workplace / easy-apply for stored alert offers., reparse_alerts(), ReparseResult, Connection, The card line survived in companies.name; the city held only chrome. (+8 more)

### Community 110 - "test_designation_numbers.py"
Cohesion: 0.17
Nodes (16): bank(), _in_bank(), LogCaptureFixture, A standard's digits name a thing; a metric's digits measure one., The anti-fabrication guarantee is not weakened by designation handling., Only the designation's own span is exempt from the number rule., Judge as the letter is judged: no entry, so the whole bank answers., Looking like a standard is not evidence of holding one. (+8 more)

### Community 111 - "_AnchorParser"
Cohesion: 0.06
Nodes (65): _advisor_prompt(), allowed_numbers(), _bank_parts(), _generated_bullets(), _guessed_section(), letter_scope(), _normalized_number(), _organisation_names() (+57 more)

### Community 112 - "test_ingest_idempotent.py"
Cohesion: 0.06
Nodes (61): Return capability-tier tokens that have tripped generations, by frequency., vocabulary_misses(), GenericVocabularyError, load_generic_vocabulary(), parse_rejections(), Path, ValueError, Three tiers of token, so a category word is not judged like a claim.  A sourced (+53 more)

### Community 113 - "apply_matching_profile_cmd"
Cohesion: 0.20
Nodes (10): menubar_cmd(), Show ready/queued counts in the macOS menu bar (optional extra)., MenubarUnavailable, Any, RuntimeError, Raised when the menu bar item cannot run on this machine., Import rumps or explain, in French, exactly how to get it., Run the menu bar item until quit. Blocks; opens the dashboard on click. (+2 more)

### Community 114 - "vocabulary_misses"
Cohesion: 0.14
Nodes (11): Message, GmailIMAP, Minimal read-only Gmail IMAP client., Fetch recent mail sent from `domains` (or any of their subdomains).          The, Return the lowercased domain of the address in a `From` header.      Parses the, True when the From address sits on one of `domains` or a subdomain of it., sender_allowed(), sender_domain() (+3 more)

### Community 116 - "mappings_for"
Cohesion: 0.30
Nodes (10): ingest_source(), Run one source end to end. Commits once at the end for atomicity., FakeSource, Connection, Re-running ingest must never duplicate rows (constitution idempotency rule)., _sample(), test_company_deduped_across_offers_and_runs(), test_first_run_inserts_all() (+2 more)

### Community 117 - "test_progress.py"
Cohesion: 0.24
Nodes (8): Any, _canonicalize_prose(), _justification(), Normalize model punctuation that the document contract forbids.      This is a l, One employer's bullets, chosen from its facts rather than written.      The skil, One project, and which of its facts describes it. Inserted verbatim., TailoredExperience, TailoredProject

### Community 118 - "parse_rejections"
Cohesion: 0.23
Nodes (9): Operation, Any, datetime, Everything running, plus anything that finished very recently., Present a RefreshRunner snapshot in the same shape as everything else.      Refr, One slow thing, and how far along it is., refresh_operation(), test_a_refresh_snapshot_becomes_a_per_source_operation() (+1 more)

### Community 119 - ".finish"
Cohesion: 0.20
Nodes (16): ingest_cmd(), Fetch offers from a source (or all sources) into the database., available_sources(), build_source(), enabled_sources(), _enablement(), is_enabled(), Any (+8 more)

### Community 120 - "_Toolchain"
Cohesion: 0.33
Nodes (11): _client(), Connection, Path, TestClient, The point of the whole item: the writer lock is held, and /progress still     an, Task 34's rule: the validator's own message, verbatim, not 'Error: 500'., It must answer while a generation holds the writer lock., test_a_generation_failure_is_reported_in_the_interface_voice() (+3 more)

### Community 121 - "run_menubar"
Cohesion: 0.10
Nodes (26): Logger, Put text on the system clipboard, or say plainly that it could not.  The manual_, _env_bool(), get_settings(), _path(), Configuration and path resolution. Secrets come from .env only (never mocked)., get_logger(), Central logging setup. Library code logs here; it never uses print(). (+18 more)

### Community 122 - "_Advisor"
Cohesion: 0.20
Nodes (3): Task 36 item 6: live progress for the slow operations.  Generation, regeneration, The token system disables motion wholesale rather than per-animation., test_the_spinner_respects_reduced_motion()

### Community 123 - "format_fact_bank"
Cohesion: 0.22
Nodes (4): BaseException, Update a running operation. A key that is not running is ignored., Close an operation. The first outcome recorded wins.          A handled failure, Record a failure the caller handled rather than raised.          The dashboard c

### Community 124 - "ApplicationNotQueuedError"
Cohesion: 0.17
Nodes (23): ColdEmailPreparation, _log_cold_failure(), One queued cold draft rendered by the confirmation page., current_status(), IllegalTransition, log_event(), Connection, ValueError (+15 more)

### Community 125 - "vocabulary.py"
Cohesion: 0.29
Nodes (7): _candidate_name(), database_connection(), Connection, Yield one production database connection per request., Record which route the human confirmed. Not a status write.      The eventual de, The operator's name, for the download filename. Absent is not an error., _record_apply_route()

### Community 126 - "test_sourcing_targets_changes_no_sending_gate"
Cohesion: 0.40
Nodes (6): build_advisor(), Resolve TAILORING_PROVIDER to a concrete mode, without building anything.      C, Select the configured provider without silently bypassing missing keys., Raised when the selected tailoring provider is not configured., resolve_provider(), TailoringConfigurationError

### Community 127 - "_Advisor"
Cohesion: 0.53
Nodes (5): _Advisor, _application(), Connection, test_generation_failure_returns_application_to_queue(), test_generation_runs_quality_gates_before_pdfs_and_moves_to_ready()

### Community 128 - "_plan_for"
Cohesion: 0.40
Nodes (5): _plan_for(), The V&V case: a natural French phrase needs more room than five words., test_tailoring_accepts_a_six_word_french_domain_phrase(), test_tailoring_preserves_entity_encoding(), test_tailoring_rejects_profile_phrase_outside_three_to_seven_words()

### Community 129 - "apply_matching_profile_cmd"
Cohesion: 0.10
Nodes (35): SentenceTransformer, apply_matching_profile_cmd(), Connection, _queue_snapshot(), Apply config/matching_profile.yaml and report what it changed.      Re-scoring i, Count what currently clears the bar, for an honest before/after., Re-evaluate every offer against the new vocabulary.      ``jobpilot score`` only, _rescore_all() (+27 more)

### Community 132 - "observable_controls"
Cohesion: 0.12
Nodes (25): _Control, _ControlParser, _controls_from_html(), FillAction, _first_matching_selector(), _Form, _FormParser, _forms_from_html() (+17 more)

## Knowledge Gaps
- **154 isolated node(s):** `Requirements`, `macOS / Linux`, `Windows PowerShell`, `Configuration`, `CV variant selection` (+149 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `OpenAITailoringAdvisor` to `_client`, `observable_controls`, `test_routing.py`, `mailer.py`, `test_generic_vocabulary.py`, `RefreshRunner`, `wttj.py`, `france_travail.py`, `_FakePage`, `test_email_alerts.py`, `test_labonnealternance.py`, `test_alert_card_fields.py`, `Settings`, `test_cold_outreach.py`, `_FakePage`, `ingest_source`, `pick_variant`, `test_mailer.py`, `models.py`, `record_form_fields`, `vocabulary_misses`, `approve_application`, `.finish`, `run_menubar`, `ApplicationNotQueuedError`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `run_menubar` to `apply_matching_profile_cmd`, `_client`, `observable_controls`, `create_app`, `run_dashboard`, `test_routing.py`, `mailer.py`, `apply_assist.py`, `wttj.py`, `SourcedBullet`, `launch_wttj_application`, `test_email_alerts.py`, `test_labonnealternance.py`, `OpenAITailoringAdvisor`, `test_fact_id_resolution.py`, `test_mailer.py`, `reparse_alerts`, `vocabulary.py`, `.finish`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Why does `TailoringError` connect `dashboard.py` to `connect`, `generate_application`, `_Toolchain`, `email_alerts.py`, `test_cv_completeness.py`, `.from_mapping`, `MissingCredentialError`, `CompanyRecord`, `labonnealternance.py`, `test_fact_id_resolution.py`, `test_letter_quality.py`, `test_designation_numbers.py`, `UnknownFactIdError`, `_AnchorParser`, `vocabulary.py`, `test_valid_sourced_advice_completes_the_shared_generation_path`, `_AnchorParser`, `test_progress.py`, `test_sourcing_targets_changes_no_sending_gate`, `_Advisor`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Are the 62 inferred relationships involving `Settings` (e.g. with `ApplicantProfile` and `ApplyAdapter`) actually correct?**
  _`Settings` has 62 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `_payload()` (e.g. with `.advise()` and `_plan()`) actually correct?**
  _`_payload()` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `TailoringError` (e.g. with `_CompleteAdvisor` and `_IncompleteAdvisor`) actually correct?**
  _`TailoringError` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `OfferRecord` (e.g. with `BackfillResult` and `RescoreResult`) actually correct?**
  _`OfferRecord` has 23 INFERRED edges - model-reasoned connections that need verification._