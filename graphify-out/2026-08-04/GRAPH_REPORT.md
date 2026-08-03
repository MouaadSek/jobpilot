# Graph Report - jobpilot  (2026-08-03)

## Corpus Check
- 149 files · ~182,425 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3242 nodes · 8606 edges · 130 communities (115 shown, 15 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 517 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b0ce8cd6`
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
- apply_matching_profile_cmd
- observable_controls

## God Nodes (most connected - your core abstractions)
1. `Settings` - 117 edges
2. `current_status()` - 95 edges
3. `_payload()` - 88 edges
4. `TailoringError` - 83 edges
5. `load_fact_bank()` - 73 edges
6. `FactBank` - 71 edges
7. `OfferRecord` - 68 edges
8. `get_settings()` - 63 edges
9. `create_app()` - 61 edges
10. `OfferContext` - 60 edges

## Surprising Connections (you probably didn't know these)
- `_FakeLauncher` --uses--> `WTTJApplyError`  [INFERRED]
  tests/test_wttj_apply.py → src/jobpilot/apply_assist.py
- `_FakeLocator` --uses--> `WTTJApplyError`  [INFERRED]
  tests/test_wttj_apply.py → src/jobpilot/apply_assist.py
- `_FakePage` --uses--> `WTTJApplyError`  [INFERRED]
  tests/test_wttj_apply.py → src/jobpilot/apply_assist.py
- `_FakeLauncher` --uses--> `ApplicantProfile`  [INFERRED]
  tests/test_apply_assist.py → src/jobpilot/apply_assist.py
- `_FakeLocator` --uses--> `ApplicantProfile`  [INFERRED]
  tests/test_apply_assist.py → src/jobpilot/apply_assist.py

## Import Cycles
- None detected.

## Communities (130 total, 15 thin omitted)

### Community 0 - "test_downloads.py"
Cohesion: 0.05
Nodes (41): BaseException, Operation, ProgressRegistry, Any, datetime, Update a running operation. A key that is not running is ignored., Close an operation. The first outcome recorded wins.          A handled failure, Everything running, plus anything that finished very recently. (+33 more)

### Community 1 - "Request"
Cohesion: 0.08
Nodes (55): Resolve one archived artefact, with the same discipline as the live one.      De, _safe_archive_path(), _archives_for(), Generation, is_archive_stamp(), library_entries(), LibraryEntry, _mtime_iso() (+47 more)

### Community 2 - "_candidate_name"
Cohesion: 0.06
Nodes (95): ModuleType, SimpleNamespace, JobPilot: personal job application pipeline for the French IT/cybersecurity mark, current_status(), ValueError, _application(), _ConnectionProxy, Connection (+87 more)

### Community 3 - "_client"
Cohesion: 0.05
Nodes (62): LookupError, adapter_for_url(), _application_for_assist(), _application_for_wttj(), ApplyAssistError, AssistResult, _fallback(), launch_application_assist() (+54 more)

### Community 4 - "create_app"
Cohesion: 0.06
Nodes (49): add_contact_cmd(), apply_cmd(), backfill_descriptions_cmd(), contacts_cmd(), _csv(), daemon_cmd(), dashboard_cmd(), draft_cold_cmd() (+41 more)

### Community 5 - "dashboard.py"
Cohesion: 0.07
Nodes (72): Match, Pattern, _add_tech_additions(), _add_tech_keywords(), _contains(), _contains_any(), document_variant_label(), _encode_fragment() (+64 more)

### Community 6 - "run_dashboard"
Cohesion: 0.23
Nodes (13): _dropping_enabled(), _InventsForever, Connection, MonkeyPatch, Path, The shipped default: nothing is dropped and the generation fails., Enabling degradation does not make everything droppable., Nobody reviews what they were not told about. (+5 more)

### Community 7 - "Path"
Cohesion: 0.25
Nodes (10): derive_fields(), _Derived, Re-derive alert card fields (company / city / workplace / easy-apply) in place., Re-derive one offer's card fields from the text that was stored for it.      Pur, is_title_echo(), True when `chunk` restates `title` rather than naming a company or place., The length guard must not sacrifice a genuine place name., test_a_real_city_that_merely_opens_the_title_is_kept() (+2 more)

### Community 8 - "test_routing.py"
Cohesion: 0.10
Nodes (58): Cursor, _artifacts(), Path, Resolve the one route this application would go out by. Writes nothing., The resolved plan for one application. Carries no state and stores none., Fingerprint of exactly the inputs that decided this route.          Stateless by, resolve_route(), Route (+50 more)

### Community 9 - "mailer.py"
Cohesion: 0.09
Nodes (49): is_professional_address(), True only for well-formed addresses NOT on a personal free-provider domain., Whether a named mailbox on a professional domain needs extra approval., requires_personal_confirmation(), _as_utc(), _build_message(), build_sender(), ColdEmailPreparation (+41 more)

### Community 10 - "validate_cv.py"
Cohesion: 0.06
Nodes (53): check_orphans(), find_regressions(), Path, Return orphan metrics that are new or materially worse than the template., format_date(), main(), build_letter_html(), detect_github() (+45 more)

### Community 11 - "get_settings"
Cohesion: 0.13
Nodes (15): _fact_id_key(), Fold separator and case differences, and nothing else, for comparison., Map a cited id onto a real fact id, accepting only unambiguous matches.      Mat, resolve_fact_id(), LogCaptureFixture, The reported failure: 'unknown skill fact id: azure.sentinel'., skill_order can only mean a skill, so its own prefix settles the match., Resembling what a fact is about is not evidence the model read that fact. (+7 more)

### Community 12 - "connect"
Cohesion: 0.13
Nodes (21): _offer(), _OneShotProfileOrphan, Connection, Path, _Toolchain, Systemic recovery at the generated-prose and document-layout boundaries., Naming the employer is what a motivation letter does.      The rule was never lo, A profile-only layout regression that disappears with template wording. (+13 more)

### Community 13 - "test_descriptions.py"
Cohesion: 0.09
Nodes (57): backfill_descriptions(), clear_match_scores(), enrich_offer(), is_synthesized(), is_thin(), Connection, Replace a thin description in place; richer descriptions are left alone.      Ca, Return an SQL fragment + params restricting a query to one source. (+49 more)

### Community 14 - "test_generic_vocabulary.py"
Cohesion: 0.13
Nodes (21): CvProfileError, load_variants(), MatchingProfileError, ProfileInput, Connection, Path, ValueError, Profile singleton + cv_variants seeding.  Persistence logic only (no prompting/p (+13 more)

### Community 15 - "apply_assist.py"
Cohesion: 0.32
Nodes (15): _events(), Connection, EmailMessage, Exception, Path, Application email sending: rails, transitions, and events (mocked SMTP)., _ready_app(), _Sender (+7 more)

### Community 16 - "test_skim.py"
Cohesion: 0.10
Nodes (52): available_sources(), _create_application(), ignore_offer(), promote_offer(), Connection, Row, ValueError, The skim list: offers that passed the hard filter but scored below threshold.  T (+44 more)

### Community 17 - "contacts.py"
Cohesion: 0.11
Nodes (35): _candidate_name(), ContactCandidate, discover_and_store(), DiscoverySource, draft_cold_email(), draft_linkedin_note(), _get_or_create_cold_application(), is_suppressed() (+27 more)

### Community 18 - "JobPilot — Codex Handoff (complete A-to-Z)"
Cohesion: 0.04
Nodes (45): 10. HARD REJECTIONS (offers the pipeline should auto-skip), 11. API REFERENCES, 12. DESIGN PRINCIPLES (non-negotiable), 13. ENV VARS (.env), 14. GITHUB PUSH (do this FIRST, before any Codex work), 15. CODEX TASK BREAKDOWN (suggested order), 16. BAIFALL DREAM STAGE REFERENCE, 17. SCRIPTS REFERENCE (+37 more)

### Community 19 - "RefreshRunner"
Cohesion: 0.20
Nodes (21): _offer(), _openai_response(), _plan_payload(), Any, Connection, MonkeyPatch, Path, _queued_application() (+13 more)

### Community 20 - "_payload"
Cohesion: 0.11
Nodes (42): _bullets(), _project(), The advisor selects; the renderer inserts the bank's wording unchanged., The pre-written variants from the skill asset, used as the asset intends., The contract has no field for prose, so a writing advisor fails loudly., Only the entry's own facts, so a skill id cannot become a bullet., Task 25's tolerance survives: ids are normalised before they are judged., The phrase is short, but it is still generated, so the tiers still read it. (+34 more)

### Community 21 - "wttj.py"
Cohesion: 0.10
Nodes (40): _city(), _contact_email(), _contract(), _first(), map_hit(), _org(), _prose(), Any (+32 more)

### Community 22 - "SourcedBullet"
Cohesion: 0.09
Nodes (23): ConnectionFactory, Event, IngestResult, _default_model_loader(), _default_score_pass(), _production_connection(), Any, Connection (+15 more)

### Community 23 - "france_travail.py"
Cohesion: 0.09
Nodes (30): _delay(), Rate limiting + exponential backoff for every external call (constitution rule)., Call fn(); retry on transient HTTP errors with full-jitter exponential backoff., with_backoff(), _first_nonempty(), FranceTravailSource, _map_contact_email(), _map_contract() (+22 more)

### Community 24 - "test_provenance_tiers.py"
Cohesion: 0.08
Nodes (34): _in_bank(), _offer(), Three kinds of token, three different burdens of proof., Not even the widest scope can support it., The reader has to be able to search for it, or add it to the config., Task 26's handling survives as the digit-shaped corner of tier 2., Presence in the bank is necessary for tier 2, never sufficient., No fact anywhere carries these figures, so no scope can accept them. (+26 more)

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
Cohesion: 0.12
Nodes (42): counts(), Any, Connection, datetime, The tracker: every application, one table, read-only.  Deliberately not a Google, Every offer application, optionally narrowed to one status., Statuses that actually occur, so the filter offers no dead options., Export exactly the visible rows, in the visible column order. (+34 more)

### Community 29 - "test_desktop_shell.py"
Cohesion: 0.08
Nodes (32): CaptureFixture, dashboard_already_running(), Whether something is already listening on the dashboard's port.      A connect p, The menu bar text. Short: it competes with every other item up there., title(), _bound_port(), _fake_macos(), _module_level_imports() (+24 more)

### Community 30 - "generate_application"
Cohesion: 0.09
Nodes (29): date, build_advisor(), _check_orphans(), _contains_generated_orphan(), DocumentToolchain, _french_date(), generate_application(), _load_offer() (+21 more)

### Community 31 - "test_contacts.py"
Cohesion: 0.21
Nodes (14): _app(), company(), Connection, Stage 2: contact storage, suppression, address rules, cap/stagger, drafting., test_daily_cap_rolls_to_next_day(), test_manual_discovery_is_noop(), test_prepare_outreach_idempotent(), test_prepare_outreach_personal_email_skips_email_keeps_linkedin() (+6 more)

### Community 32 - "test_email_alerts.py"
Cohesion: 0.08
Nodes (50): Message, clean_job_url(), EmailAlertError, html_of(), LinkedInAlertSource, parse_indeed(), RuntimeError, Fetch recent mail sent from `domains` (or any of their subdomains).          The (+42 more)

### Community 33 - "test_labonnealternance.py"
Cohesion: 0.06
Nodes (73): get_or_create_company(), _city(), _company_name(), _contract_type(), _domain(), _first(), map_company(), map_offer() (+65 more)

### Community 34 - "_Toolchain"
Cohesion: 0.06
Nodes (61): ExperienceFact, FactClaim, One atomic statement that generated content may cite., SkillFact, CvProfile, Renderer-owned candidate facts injected into every generated CV., The location printed in the CV header when the offer yields none., AmbiguousFactIdError (+53 more)

### Community 35 - "email_alerts.py"
Cohesion: 0.09
Nodes (32): _advisor_prompt(), Every id the advisor may cite, flattened out of the context it was given.      D, valid_fact_ids(), Listing the numbers is not enough on its own: the failure was a dropped +., test_the_prompt_forbids_introducing_a_figure(), test_the_prompt_says_to_copy_the_figure_exactly(), test_the_prompt_says_to_write_the_sentence_without_a_number(), _nested_ids() (+24 more)

### Community 36 - "test_alert_card_fields.py"
Cohesion: 0.15
Nodes (5): _ControlParser, HTMLParser, Strip a generated letter's markup down to what a human would paste., Tiny standard-library parser sufficient to test our simple CSS selectors., _TextParser

### Community 37 - "Settings"
Cohesion: 0.11
Nodes (19): HTTPStatusError, MissingCredentialError, RuntimeError, Raised when a required secret is absent. We ask; we never silently mock., CompanyRecord, RateLimiter, Minimum-delay-per-domain limiter. Blocks until the next call is allowed., Yield companies likely to hire (optional; default: none). (+11 more)

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
Cohesion: 0.15
Nodes (19): _advise(), ambiguous_bank(), bank(), _offer(), Any, Connection, Path, Citation ids are matched tolerantly; what may be claimed is unchanged. (+11 more)

### Community 42 - "test_dashboard_facts_scheduler.py"
Cohesion: 0.29
Nodes (16): _client(), fixture_bank(), Connection, MonkeyPatch, Path, TestClient, Read-only fact bank page and honest scheduler reporting on the queue page., test_daemon_state_follows_the_recorded_heartbeat_age() (+8 more)

### Community 43 - ".from_mapping"
Cohesion: 0.11
Nodes (22): Validate the one JSON contract shared by every advisor provider., _tailor(), _experience_content(), _gemini_shaped_payload(), _offer(), MonkeyPatch, AI-authored CV/letter content must be traceable to the fact bank., The observed real case: Gemini fills both structures, we keep the sourced one. (+14 more)

### Community 44 - "test_cold_outreach.py"
Cohesion: 0.08
Nodes (31): BackfillResult, Synthesise matchable text for offers that arrive with no description.  Job-alert, content_hash(), OfferRecord, Normalized DTOs that every source emits, decoupled from source-specific JSON., sha256(lower(title + company + first 500 chars of description)).      This is th, One normalized offer, ready to insert into the offers table., Coerce enum-constrained fields to legal values (schema CHECK safety). (+23 more)

### Community 45 - "_FakePage"
Cohesion: 0.26
Nodes (18): _events(), _FakeLauncher, _FakePage, Connection, Path, Row, WTTJ inline application stays human-approved and dry-run by default., _ready_wttj_application() (+10 more)

### Community 46 - "MissingCredentialError"
Cohesion: 0.18
Nodes (17): _Client, _offer(), _plan_payload(), Any, Exception, MonkeyPatch, Path, Focused contracts for tailoring advisers and the script toolchain. (+9 more)

### Community 47 - "ats.py"
Cohesion: 0.15
Nodes (23): download_filename(), Download names an employer folder can still be read a week later.  ``output/appl, Reduce free text to ``[A-Za-z0-9-_]``, or to "" if nothing survives.      Accent, Build ``<Company>_<Type>_<Nom>.<ext>`` for one artefact.      Falls back to the, slugify(), _client(), Connection, Path (+15 more)

### Community 48 - "AnthropicTailoringAdvisor"
Cohesion: 0.12
Nodes (29): extract_template_context(), pick_variant(), Pick the best of 21 variants from missions, then apply contract rules.      Sinc, Read all editable choices without altering the template., unsupported number 27001' was rejecting real, bank-backed vocabulary., test_the_observed_failure_no_longer_fails_a_generation(), rendered(), _offer() (+21 more)

### Community 49 - "OpenAITailoringAdvisor"
Cohesion: 0.15
Nodes (23): Decision, RouteId, _applicant_reason(), _ats_prefill(), _email(), _learned_form(), _manual_open(), _missing_applicant_fields() (+15 more)

### Community 50 - "resolve_fact_id"
Cohesion: 0.16
Nodes (22): FormMapping, mapping_is_complete(), mappings_for(), put_mapping(), Connection, A stored selector -> profile field mapping. Never a stored value., Write one mapping. Rejects a profile_field outside the closed enum., Whether ``domain`` has enough of a mapping to be worth calling a route. (+14 more)

### Community 51 - "test_tech_additions.py"
Cohesion: 0.16
Nodes (25): _offer(), LogCaptureFixture, Zone 3 may add a keyword, but only one he has and the offer asked for., Reorder-only remains the default and the common case., Genuinely his, but padding: the offer did not ask for it., Presence in the bank is necessary, never sufficient., Derived from the file, not a magic number., One page matters more than one keyword; the CV is still true without it. (+17 more)

### Community 52 - "load_fact_bank"
Cohesion: 0.15
Nodes (28): _boolean(), CertificationFact, _claim_list(), EducationFact, _entry_claim(), FactBankError, LanguageFact, load_fact_bank() (+20 more)

### Community 53 - "CompanyRecord"
Cohesion: 0.10
Nodes (38): FactBank, load_cv_profile(), Load the committed CV profile, failing loudly rather than defaulting., _advise_and_tailor(), _advisor_fact_context(), _contact_fields(), _cv_locked_fields(), DroppedCitation (+30 more)

### Community 54 - "labonnealternance.py"
Cohesion: 0.10
Nodes (19): ApplicationGenerationError, A redacted generation failure suitable for CLI and dashboard display., _InteractiveShapedAdvisor, Human loop: always rejected, and never re-prompted automatically., _InventsThenRecovers, Connection, LogCaptureFixture, Path (+11 more)

### Community 55 - "ingest_source"
Cohesion: 0.14
Nodes (13): ApplicantProfile, The non-secret contact values entered into an ATS form., build_prefill(), discard_mapping(), FormLearningError, PrefillOutcome, _profile_values(), ValueError (+5 more)

### Community 56 - "pick_variant"
Cohesion: 0.13
Nodes (12): BrowserLauncher, _ConfirmationBaseline, _css_attribute_value(), _Locator, _Page, PrefillPlan, Protocol, The actions selected from a page's current HTML fixture/markup. (+4 more)

### Community 57 - "test_fact_id_resolution.py"
Cohesion: 0.16
Nodes (27): ApplyOutcome, approve_application(), Any, Connection, Path, Record human approval, transition, and generate through one shared path.      ``, The result shared by the CLI and dashboard approval surfaces., invention_report() (+19 more)

### Community 58 - "test_letter_locked_fields.py"
Cohesion: 0.18
Nodes (19): bank(), _letter(), _offer(), A letter is prose about a career; a CV is slots the renderer fills., Naming a real-sounding employer he never had is a fabrication, not prose., The renderer injects the address block; the body repeating it is a bug., Otherwise the test above would prove nothing about scope., The bank's own text names nothing it should not; selection is the check. (+11 more)

### Community 59 - "launch_application_assist"
Cohesion: 0.12
Nodes (18): observable_controls(), Every fillable control's *shape*, for form learning. Never its contents.      ``, fields_from_html(), Read a page's controls as shapes. Values are stripped before we see them., Whether pressing submit is allowed on this domain. Default: no.      Prefill is, Flip the per-domain submit gate. Deliberately has no global counterpart., set_submit_enabled(), submit_enabled() (+10 more)

### Community 60 - "test_letter_quality.py"
Cohesion: 0.22
Nodes (17): _default_letter(), french_de_elision(), Return « de <noun> » or « d'<noun> », applying French elision.      Elides befor, _render_sourced_letter(), _validate_letter_body(), _letter(), _offer(), Letter quality: French elision and the 'Entreprise' placeholder rejection. (+9 more)

### Community 61 - "test_mailer.py"
Cohesion: 0.16
Nodes (19): init_db_cmd(), Create the database from schema.sql, run migrations, seed sources., apply_schema(), init_db(), Connection, Path, Full initialization: schema + migrations + source seeding., Apply schema.sql. Idempotent: uses CREATE TABLE ... only, so we guard reruns. (+11 more)

### Community 62 - "models.py"
Cohesion: 0.17
Nodes (18): drop_unknown_citation(), Remove one unusable citation, or refuse when removing it would weaken the CV., bank(), _plan(), Task 37 item 3: degradation, shipped OFF.  If the advisor still cites an id that, The completeness floor is a hard failure, not a preference., The spec said "at least one remaining bullet" is enough. It is not: the     Task, Exactly three projects are required, each with its single fact. (+10 more)

### Community 63 - "reparse_alerts"
Cohesion: 0.24
Nodes (15): _generation_failed_detail(), Any, Connection, LogCaptureFixture, Path, _queued_application(), One automatic advisor retry, fed only the validator's own error text., Re-calling on a 429 or a bad key is not feedback, it is a retry storm. (+7 more)

### Community 64 - "test_designation_numbers.py"
Cohesion: 0.15
Nodes (19): Container, _designation_spans(), _proper_nouns(), ProvenanceScope, Everything true of the career the generated text is describing.      Generated t, Check every designation against the scope; return what it covers.      Designati, Blank out validated designations, keeping every other offset intact., Named things in the text, as {matched form: as written}.      The written form i (+11 more)

### Community 65 - "test_fact_id_consistency.py"
Cohesion: 0.20
Nodes (15): bank(), _bank_payload(), Path, Task 35 item 2: a fact bank whose claim ids do not extend their entry is invalid, The real bank must satisfy the rule the loader now enforces., This is the exact shape the Baïfall entry had., Projects have the same shape as experience, so they get the same rule., `experience.baifallX` starts with the entry id as a STRING but is a     differen (+7 more)

### Community 66 - "UnknownFactIdError"
Cohesion: 0.12
Nodes (10): CompletedProcess, Raised when a citation matches no fact id, even after normalisation.      ``sect, UnknownFactIdError, _BadSourceAdvisor, Cites a prefix-less unknown id first, then whatever the retry was told., Cites an unresolvable id in a letter paragraph, where no section is implied., _RecordingAdvisor, A rejection that buries the answer in a wall of ids is no more useful     than o (+2 more)

### Community 67 - "ingest_source"
Cohesion: 0.27
Nodes (14): Connection, EmbedFn, Score all unscored offers. Returns the number newly queued.      The queue thres, score(), _fake_embed(), _insert_offer(), Connection, Scoring wiring: profile embedding cache + end-to-end scoring via a fake embed_fn (+6 more)

### Community 68 - "_AnchorParser"
Cohesion: 0.06
Nodes (56): CatalogueEntry, default_catalogue(), load_variant_catalogue(), _parse_criteria(), _parse_shortcuts(), Path, The CV catalogue offered to the advisor when it selects a variant.  The selectio, Read the two-column selection table, skipping its header and separator. (+48 more)

### Community 69 - "test_preview.py"
Cohesion: 0.23
Nodes (12): _bullet_budget(), _claim_length(), An experience claim has to fit the CV's one line.  The renderer inserts a select, Every experience bullet the template ships, as (employer, plain text).      Enti, The longest experience bullet the template itself already renders on one line., Derived from the file, not a magic number., Without this the constant could go stale and quietly widen the budget., The renderer inserts these verbatim, so a long one wraps in silence. (+4 more)

### Community 70 - "vocabulary.py"
Cohesion: 0.10
Nodes (33): FastAPI, _citation_warning(), create_app(), Any, Path, Render an ISO timestamp as YYYY-MM-DD; pass other values through as text., Run the dashboard on an intentionally fixed loopback interface.      Returns a p, The warning for a CV generated without a citation the advisor invented.      Rea (+25 more)

### Community 71 - "UnknownFactIdError"
Cohesion: 0.05
Nodes (63): _alert_source_clause(), Connection, Restrict to one alert source, or to all of them when none is named., Re-derive company / city / workplace / easy-apply for stored alert offers., reparse_alerts(), ReparseResult, is_noise(), parse_linkedin() (+55 more)

### Community 72 - "Baifall Dream Stage - Reference Document (v3)"
Cohesion: 0.17
Nodes (11): Baifall Dream Stage - Reference Document (v3), Bloc HTML de reference (3 bullets), Bullet 1 (commun, accompli) - 167 car., rendu sur 2 lignes, Bullet 2 (commun, nominal, perimetre complet) - 127 car., 1 ligne, Bullet 3 : declinaisons par variante, Context, Principe v3 : perimetre nominal complet, Regle pour la date (+3 more)

### Community 73 - "test_facts.py"
Cohesion: 0.11
Nodes (30): FormField, infer_profile_field(), Learn the shape of an unknown application form once, reuse it forever.  An unkno, One control's shape. Deliberately has nowhere to put a typed value., Everything naming this field, with separators folded to spaces.          Real fo, What one learning pass did, including everything it refused., Name the reason this field may never be mapped, or None if it may.      Refused:, Which profile field this control wants, or None to leave it to the human. (+22 more)

### Community 74 - "test_progress.py"
Cohesion: 0.13
Nodes (30): apply_matching_profile(), load_matching_profile(), MatchingProfile, Write the vocabulary onto the profile singleton. Returns {field: (before, after), The scoring vocabulary, committed to git rather than typed once.      These thre, Load the committed matching vocabulary, failing loudly rather than defaulting., Connection, Path (+22 more)

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
Cohesion: 0.07
Nodes (40): ingest_cmd(), Fetch offers from a source (or all sources) into the database., Remove configured secrets from exception text before display/logging., Settings, ABC, Source interface. Every API, scraper, or mailer sits behind this so it is plugga, Abstract ingestion source.      Implementations must be side-effect free with re, Source (+32 more)

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
Cohesion: 0.06
Nodes (63): allowed_numbers(), _bank_parts(), _guessed_section(), letter_scope(), nearest_entry_claim_ids(), _normalized_number(), _offer_identity(), _organisation_names() (+55 more)

### Community 112 - "test_ingest_idempotent.py"
Cohesion: 0.07
Nodes (58): Return capability-tier tokens that have tripped generations, by frequency., vocabulary_misses(), GenericVocabularyError, load_generic_vocabulary(), parse_rejections(), Path, ValueError, Three tiers of token, so a category word is not judged like a claim.  A sourced (+50 more)

### Community 113 - "apply_matching_profile_cmd"
Cohesion: 0.20
Nodes (10): menubar_cmd(), Show ready/queued counts in the macOS menu bar (optional extra)., MenubarUnavailable, Any, RuntimeError, Raised when the menu bar item cannot run on this machine., Import rumps or explain, in French, exactly how to get it., Run the menu bar item until quit. Blocks; opens the dashboard on click. (+2 more)

### Community 114 - "vocabulary_misses"
Cohesion: 0.18
Nodes (10): build_cv_title(), normalise_role_title(), Remove posting metadata while preserving the actual role wording., Build the deterministic CV title used after all advisor providers., Fact-bank loading, review CLI, and deterministic role-title cleaning., test_build_cv_title_uses_clean_role_and_contract_specific_suffix(), test_every_skill_is_explicitly_verified_or_unverified(), test_fact_bank_covers_every_cv_template_and_has_unique_claim_ids() (+2 more)

### Community 116 - "mappings_for"
Cohesion: 0.15
Nodes (23): source_id(), _backfill_company_source(), ingest_source(), _insert_offer(), Connection, Ingestion orchestrator: pull normalized records from a Source into the DB.  Idem, INSERT OR IGNORE one offer. Returns True if a new row was created., Run one source end to end. Commits once at the end for atomicity. (+15 more)

### Community 117 - "test_progress.py"
Cohesion: 0.36
Nodes (5): _canonicalize_prose(), _fact_id_list(), _justification(), Any, Normalize model punctuation that the document contract forbids.      This is a l

### Community 118 - "parse_rejections"
Cohesion: 0.23
Nodes (5): Connection, Path, test_a_rejected_number_is_counted_separately_from_an_invented_id(), Path, _Toolchain

### Community 119 - ".finish"
Cohesion: 0.57
Nodes (6): Path, Source enablement via config/sources.yaml., _settings(), test_disabled_source_excluded(), test_no_config_all_enabled(), test_replace_keeps_dataclass_shape()

### Community 120 - "_Toolchain"
Cohesion: 0.27
Nodes (7): _Form, _FormParser, _forms_from_html(), _identity(), _page_offer_identity(), Collect controls by form so automation never targets the wrong form., _wttj_application_form()

### Community 121 - "run_menubar"
Cohesion: 0.07
Nodes (41): Logger, SentenceTransformer, _env_bool(), get_settings(), _path(), Configuration and path resolution. Secrets come from .env only (never mocked)., Database connection factory, schema application, and migration runner., _model() (+33 more)

### Community 122 - "_Advisor"
Cohesion: 0.25
Nodes (7): launch_wttj_application(), _open_for_human(), Auditable outcome of one approved WTTJ dashboard action., Launch Playwright visibly and retain it until the human closes it., Fill a WTTJ inline form and submit only behind the explicit live gate., VisibleBrowserLauncher, WTTJApplyResult

### Community 123 - "format_fact_bank"
Cohesion: 0.29
Nodes (7): Request, _posted_body(), _posted_cold_send(), _posted_plan_hash(), Read the ``body`` field from a urlencoded POST without python-multipart.      Ru, Read the plan_hash the confirmation page put in the form., Read editable body and the named-mailbox confirmation checkbox.

### Community 124 - "ApplicationNotQueuedError"
Cohesion: 0.42
Nodes (9): _app(), Connection, State machine transition tests: legality + event auditing., Constitution: no send/submit without a prior human_approved event., test_full_happy_path(), test_human_approved_event_recorded(), test_illegal_transition_raises_and_no_change(), test_legal_transition_updates_and_logs() (+1 more)

### Community 125 - "vocabulary.py"
Cohesion: 0.50
Nodes (4): WTTJ inline form adapter with explicit pre-submit assertions., WTTJAdapter, test_wttj_actions_are_scoped_to_the_identified_application_form(), test_wttj_form_can_use_page_data_offer_identity()

### Community 126 - "test_sourcing_targets_changes_no_sending_gate"
Cohesion: 0.50
Nodes (4): facts_cmd(), Print the provenance fact bank grouped for human review., format_fact_bank(), Render the bank as plain UTF-8 text for human review in the CLI.

### Community 129 - "apply_matching_profile_cmd"
Cohesion: 0.17
Nodes (17): apply_matching_profile_cmd(), Connection, _queue_snapshot(), Apply config/matching_profile.yaml and report what it changed.      Re-scoring i, Count what currently clears the bar, for an honest before/after., Re-evaluate every offer against the new vocabulary.      ``jobpilot score`` only, _rescore_all(), _as_list() (+9 more)

### Community 132 - "observable_controls"
Cohesion: 0.16
Nodes (15): _BaseAdapter, _Control, _controls_from_html(), FillAction, _first_matching_selector(), One safe local-file upload; never a form submit action., Whether a stored selector still finds a control on the current page., Match the deliberately simple tag[attr=value] selectors used below. (+7 more)

## Knowledge Gaps
- **154 isolated node(s):** `profile`, `contacts`, `suppression_list`, `offers`, `offers` (+149 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `record_form_fields` to `_client`, `observable_controls`, `test_routing.py`, `mailer.py`, `wttj.py`, `france_travail.py`, `_FakePage`, `test_email_alerts.py`, `test_labonnealternance.py`, `test_alert_card_fields.py`, `Settings`, `test_cold_outreach.py`, `_FakePage`, `OpenAITailoringAdvisor`, `ingest_source`, `pick_variant`, `approve_application`, `.finish`, `_Toolchain`, `run_menubar`, `_Advisor`, `vocabulary.py`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Why does `current_status()` connect `_candidate_name` to `_client`, `create_app`, `dashboard.py`, `run_dashboard`, `test_routing.py`, `mailer.py`, `connect`, `apply_assist.py`, `test_skim.py`, `RefreshRunner`, `launch_wttj_application`, `_FakePage`, `generate_application`, `test_cv_completeness.py`, `_FakePage`, `labonnealternance.py`, `test_fact_id_resolution.py`, `reparse_alerts`, `_AnchorParser`, `vocabulary.py`, `test_valid_sourced_advice_completes_the_shared_generation_path`, `ApplicationNotQueuedError`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `run_menubar` to `apply_matching_profile_cmd`, `_client`, `create_app`, `dashboard.py`, `run_dashboard`, `test_routing.py`, `mailer.py`, `apply_assist.py`, `test_skim.py`, `wttj.py`, `SourcedBullet`, `launch_wttj_application`, `generate_application`, `test_email_alerts.py`, `test_labonnealternance.py`, `OpenAITailoringAdvisor`, `CompanyRecord`, `test_fact_id_resolution.py`, `test_mailer.py`, `models.py`, `ingest_source`, `vocabulary.py`, `record_form_fields`, `_Advisor`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 62 inferred relationships involving `Settings` (e.g. with `ApplicantProfile` and `ApplyAdapter`) actually correct?**
  _`Settings` has 62 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `_payload()` (e.g. with `.advise()` and `_plan()`) actually correct?**
  _`_payload()` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `TailoringError` (e.g. with `ExperienceFact` and `FactBank`) actually correct?**
  _`TailoringError` has 23 INFERRED edges - model-reasoned connections that need verification._
- **What connects `profile`, `contacts`, `suppression_list` to the rest of the system?**
  _154 weakly-connected nodes found - possible documentation gaps or missing edges._