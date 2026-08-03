# Graph Report - jobpilot  (2026-08-04)

## Corpus Check
- 154 files · ~187,296 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3349 nodes · 8348 edges · 135 communities (109 shown, 26 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 341 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2d241c6f`
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
- _Toolchain

## God Nodes (most connected - your core abstractions)
1. `Settings` - 117 edges
2. `TailoringError` - 82 edges
3. `OfferRecord` - 68 edges
4. `current_status()` - 65 edges
5. `_Toolchain` - 64 edges
6. `get_settings()` - 62 edges
7. `pick_variant()` - 57 edges
8. `OfferContext` - 55 edges
9. `load_fact_bank()` - 55 edges
10. `tailor_cv_html()` - 47 edges

## Surprising Connections (you probably didn't know these)
- `test_the_library_and_tracker_mark_a_degraded_application()` --calls--> `tracker_rows()`  [INFERRED]
  tests/test_generation_warnings.py → src/jobpilot/tracker.py
- `_FakeIMAP` --uses--> `MissingCredentialError`  [INFERRED]
  tests/test_email_alerts.py → src/jobpilot/config.py
- `_NoWait` --uses--> `MissingCredentialError`  [INFERRED]
  tests/test_labonnealternance.py → src/jobpilot/config.py
- `_FakeSource` --uses--> `MissingCredentialError`  [INFERRED]
  tests/test_refresh.py → src/jobpilot/config.py
- `_FakeLauncher` --uses--> `Settings`  [INFERRED]
  tests/test_apply_assist.py → src/jobpilot/config.py

## Import Cycles
- None detected.

## Communities (135 total, 26 thin omitted)

### Community 0 - "test_downloads.py"
Cohesion: 0.08
Nodes (23): _client(), Connection, Path, TestClient, Task 36 item 6: live progress for the slow operations.  Generation, regeneration, It stays briefly so a poll landing just after completion sees the     outcome, t, The point of the whole item: the writer lock is held, and /progress still     an, Task 34's rule: the validator's own message, verbatim, not 'Error: 500'. (+15 more)

### Community 1 - "Request"
Cohesion: 0.08
Nodes (55): Resolve one archived artefact, with the same discipline as the live one.      De, _safe_archive_path(), _archives_for(), Generation, is_archive_stamp(), library_entries(), LibraryEntry, _mtime_iso() (+47 more)

### Community 2 - "_candidate_name"
Cohesion: 0.19
Nodes (41): Row, _client(), _events(), _no_advisor_client(), _offer_application(), Connection, MonkeyPatch, Path (+33 more)

### Community 3 - "_client"
Cohesion: 0.13
Nodes (25): _application_for_assist(), _application_for_wttj(), ApplyAssistError, AssistResult, _fallback(), launch_application_assist(), Connection, Row (+17 more)

### Community 4 - "create_app"
Cohesion: 0.05
Nodes (65): add_contact_cmd(), apply_cmd(), backfill_descriptions_cmd(), contacts_cmd(), _csv(), draft_cold_cmd(), init_db_cmd(), init_profile_cmd() (+57 more)

### Community 5 - "dashboard.py"
Cohesion: 0.07
Nodes (70): Match, Pattern, _add_tech_additions(), _add_tech_keywords(), _contact_fields(), _contains(), _contains_any(), _cv_locked_fields() (+62 more)

### Community 6 - "run_dashboard"
Cohesion: 0.11
Nodes (26): _dropping_enabled(), _InventsForever, _plan(), Connection, MonkeyPatch, Path, Task 37 item 3: degradation. Shipped off, turned ON by Task 39.  If the advisor, The spec said "at least one remaining bullet" is enough. It is not: the     Task (+18 more)

### Community 7 - "Path"
Cohesion: 0.09
Nodes (34): derive_fields(), _Derived, Re-derive alert card fields (company / city / workplace / easy-apply) in place., Re-derive one offer's card fields from the text that was stored for it.      Pur, _AlertAnchor, _AnchorParser, _anchors(), _Card (+26 more)

### Community 8 - "test_routing.py"
Cohesion: 0.10
Nodes (58): Cursor, _artifacts(), Path, Resolve the one route this application would go out by. Writes nothing., The resolved plan for one application. Carries no state and stores none., Fingerprint of exactly the inputs that decided this route.          Stateless by, resolve_route(), Route (+50 more)

### Community 9 - "mailer.py"
Cohesion: 0.09
Nodes (47): _as_utc(), _build_message(), build_sender(), ColdEmailPreparation, ColdSendDisabled, daily_cap_reached(), _default_body(), EmailPreparation (+39 more)

### Community 10 - "validate_cv.py"
Cohesion: 0.06
Nodes (53): check_orphans(), find_regressions(), Path, Return orphan metrics that are new or materially worse than the template., format_date(), main(), build_letter_html(), detect_github() (+45 more)

### Community 11 - "get_settings"
Cohesion: 0.14
Nodes (31): _archives(), _artifact_names(), Connection, Path, Task 34.A: the dashboard's Régénérer button.  The button re-runs the *existing*, Overwriting would destroy the evidence the button exists to produce., Back-to-back clicks land in the same UTC second; neither may be lost., ISO 8601 basic format: the extended form's colons are illegal on NTFS. (+23 more)

### Community 12 - "connect"
Cohesion: 0.05
Nodes (38): CompletedProcess, _fact_id_list(), _justification(), Any, RuntimeError, Raised when the selected tailoring provider is not configured., Raised when generated prose states a figure the bank does not contain.      A si, Raised when a citation matches no fact id, even after normalisation.      ``sect (+30 more)

### Community 13 - "test_descriptions.py"
Cohesion: 0.10
Nodes (50): backfill_descriptions(), BackfillResult, clear_match_scores(), is_synthesized(), Connection, Synthesise matchable text for offers that arrive with no description.  Job-alert, Return an SQL fragment + params restricting a query to one source., Regenerate synthesised descriptions for stored offers whose text is thin.      I (+42 more)

### Community 14 - "test_generic_vocabulary.py"
Cohesion: 0.10
Nodes (26): CvProfile, CvProfileError, load_cv_profile(), load_variants(), MatchingProfileError, ProfileInput, Connection, Path (+18 more)

### Community 15 - "apply_assist.py"
Cohesion: 0.32
Nodes (15): _events(), Connection, EmailMessage, Exception, Path, Application email sending: rails, transitions, and events (mocked SMTP)., _ready_app(), _Sender (+7 more)

### Community 16 - "test_skim.py"
Cohesion: 0.10
Nodes (52): available_sources(), _create_application(), ignore_offer(), promote_offer(), Connection, Row, ValueError, The skim list: offers that passed the hard filter but scored below threshold.  T (+44 more)

### Community 17 - "contacts.py"
Cohesion: 0.10
Nodes (38): _candidate_name(), ContactCandidate, discover_and_store(), DiscoverySource, draft_cold_email(), draft_linkedin_note(), _get_or_create_cold_application(), is_professional_address() (+30 more)

### Community 18 - "JobPilot — Codex Handoff (complete A-to-Z)"
Cohesion: 0.04
Nodes (45): 10. HARD REJECTIONS (offers the pipeline should auto-skip), 11. API REFERENCES, 12. DESIGN PRINCIPLES (non-negotiable), 13. ENV VARS (.env), 14. GITHUB PUSH (do this FIRST, before any Codex work), 15. CODEX TASK BREAKDOWN (suggested order), 16. BAIFALL DREAM STAGE REFERENCE, 17. SCRIPTS REFERENCE (+37 more)

### Community 19 - "RefreshRunner"
Cohesion: 0.10
Nodes (28): CatalogueEntry, default_catalogue(), load_variant_catalogue(), _parse_criteria(), _parse_shortcuts(), Path, RuntimeError, The CV catalogue offered to the advisor when it selects a variant.  The selectio (+20 more)

### Community 20 - "_payload"
Cohesion: 0.07
Nodes (51): _approve(), _bullets(), _project(), Connection, LogCaptureFixture, Path, The advisor selects; the renderer inserts the bank's wording unchanged., The pre-written variants from the skill asset, used as the asset intends. (+43 more)

### Community 21 - "wttj.py"
Cohesion: 0.10
Nodes (41): _city(), _contact_email(), _contract(), _first(), map_hit(), _org(), _prose(), Any (+33 more)

### Community 22 - "SourcedBullet"
Cohesion: 0.05
Nodes (61): ConnectionFactory, Event, daemon_cmd(), ingest_cmd(), Run ingest + score on a loop (Ctrl-C to stop)., Fetch offers from a source (or all sources) into the database., _backfill_company_source(), ingest_source() (+53 more)

### Community 23 - "france_travail.py"
Cohesion: 0.06
Nodes (52): _delay(), Rate limiting + exponential backoff for every external call (constitution rule)., Call fn(); retry on transient HTTP errors with full-jitter exponential backoff., with_backoff(), ATSSource, infer_contract(), load_targets(), map_greenhouse() (+44 more)

### Community 24 - "test_provenance_tiers.py"
Cohesion: 0.08
Nodes (36): bank(), _in_bank(), _offer(), Three kinds of token, three different burdens of proof., Not even the widest scope can support it., The reader has to be able to search for it, or add it to the config., Task 26's handling survives as the digit-shaped corner of tier 2., Presence in the bank is necessary for tier 2, never sufficient. (+28 more)

### Community 25 - "launch_wttj_application"
Cohesion: 0.22
Nodes (25): _cold_draft(), _configure_dashboard(), _dashboard_client(), _event_rows(), Connection, EmailMessage, Exception, MonkeyPatch (+17 more)

### Community 26 - "Dashboard"
Cohesion: 0.05
Nodes (36): Actualiser les offres (refresh from the page), Always up, without a terminal, Architecture (summary), ATS application assist (prefill only), Background scheduling, CI, Cold outreach sending (disabled by default), Commands (+28 more)

### Community 27 - "_FakePage"
Cohesion: 0.10
Nodes (13): ApplicantProfile, ApplyAdapter, _BaseAdapter, GreenhouseAdapter, LeverAdapter, Common adapter interface for a best-effort ATS prefill., Shared plan building and non-submitting form interaction., The non-secret contact values entered into an ATS form. (+5 more)

### Community 28 - "cli.py"
Cohesion: 0.17
Nodes (32): Any, Every offer application, optionally narrowed to one status., Export exactly the visible rows, in the visible column order., to_csv(), tracker_rows(), _application(), _client(), Connection (+24 more)

### Community 29 - "test_desktop_shell.py"
Cohesion: 0.08
Nodes (32): CaptureFixture, dashboard_already_running(), Whether something is already listening on the dashboard's port.      A connect p, The menu bar text. Short: it competes with every other item up there., title(), _bound_port(), _fake_macos(), _module_level_imports() (+24 more)

### Community 30 - "generate_application"
Cohesion: 0.13
Nodes (13): Protocol, _check_orphans(), _contains_generated_orphan(), DocumentToolchain, Path, Subprocess adapter around the scripts bundled with the skill., Run the orphan gate. Advisory everywhere, including generated text.      Task 39, Bundled quality-gate and rendering scripts. (+5 more)

### Community 31 - "test_contacts.py"
Cohesion: 0.10
Nodes (27): ModuleType, JobPilot: personal job application pipeline for the French IT/cybersecurity mark, _application(), _ConnectionProxy, Connection, Exception, Path, CLI coverage for offer document generation and cold-application approval. (+19 more)

### Community 32 - "test_email_alerts.py"
Cohesion: 0.09
Nodes (43): Message, GmailIMAP, html_of(), LinkedInAlertSource, Minimal read-only Gmail IMAP client., Fetch recent mail sent from `domains` (or any of their subdomains).          The, Return the best HTML (or plain-text) body of an email message., Return the lowercased domain of the address in a `From` header.      Parses the (+35 more)

### Community 33 - "test_labonnealternance.py"
Cohesion: 0.15
Nodes (29): _fixture(), _NoWait, LogCaptureFixture, La Bonne Alternance through the API Apprentissage: mapping, rails, ingestion.  E, The endpoint has no pagination, so this is the volume knob that exists., A full ingest reads both lists; it must not pay for the search twice., The live API really does repeat an offer inside one response., A company that has posted nothing must not appear in the review queue. (+21 more)

### Community 34 - "_Toolchain"
Cohesion: 0.05
Nodes (73): date, GenerationWarning, _advise_and_tailor(), _advisor_fact_context(), build_advisor(), _canonicalize_prose(), _correction_block(), drop_unknown_citation() (+65 more)

### Community 35 - "email_alerts.py"
Cohesion: 0.08
Nodes (34): _advisor_prompt(), Every id the advisor may cite, flattened out of the context it was given.      D, valid_fact_ids(), Listing the numbers is not enough on its own: the failure was a dropped +., test_the_prompt_carries_the_closed_number_set(), test_the_prompt_forbids_introducing_a_figure(), test_the_prompt_says_to_copy_the_figure_exactly(), test_the_prompt_says_to_write_the_sentence_without_a_number() (+26 more)

### Community 36 - "test_alert_card_fields.py"
Cohesion: 0.10
Nodes (34): as_dicts(), clear_warnings(), _decode(), GenerationWarning, Any, Connection, What a generation had to degrade, recorded where the reviewer will see it.  Task, Gate names per application, for the library and tracker markers.      One query (+26 more)

### Community 37 - "Settings"
Cohesion: 0.11
Nodes (16): HTTPStatusError, MissingCredentialError, RuntimeError, Raised when a required secret is absent. We ask; we never silently mock., RateLimiter, Minimum-delay-per-domain limiter. Blocks until the next call is allowed., LaBonneAlternanceAuthError, LaBonneAlternanceError (+8 more)

### Community 38 - "Job Application Pipeline"
Cohesion: 0.06
Nodes (31): Alternance vs Stage, Edge Cases & Principles, Encoding note, Execution Flow, Flag once, then execute:, Generate with the bundled script:, GitHub Exception, Hard rejections (no output): (+23 more)

### Community 39 - "matcher.py"
Cohesion: 0.15
Nodes (28): bonus_score(), cosine(), hard_filter(), keyword_score(), norm(), pick_variant(), Profile, Connection (+20 more)

### Community 40 - "test_cv_completeness.py"
Cohesion: 0.12
Nodes (23): _category_skills(), _CompleteAdvisor, _IncompleteAdvisor, Any, Connection, Path, Structural completeness floor for AI-generated CVs (Task 22).  Selection freedom, Every shipped category line with its raw, non-deduplicated tool list. (+15 more)

### Community 41 - "OfferRecord"
Cohesion: 0.04
Nodes (56): LogCaptureFixture, AmbiguousFactIdError, _fact_id_key(), _guessed_section(), nearest_entry_claim_ids(), Fold separator and case differences, and nothing else, for comparison., Map a cited id onto a real fact id, accepting only unambiguous matches.      Mat, The entry a bad citation came closest to naming, and its real claim ids.      Ne (+48 more)

### Community 42 - "test_dashboard_facts_scheduler.py"
Cohesion: 0.15
Nodes (26): daemon_status(), DaemonStatus, Any, Connection, Last recorded run per enabled source. ``last_run_at`` is all the DB keeps., Everything the queue page shows about scheduled ingestion., What can honestly be said about the daemon, and nothing more., Report daemon liveness from the heartbeat file, or admit it is unknown. (+18 more)

### Community 43 - ".from_mapping"
Cohesion: 0.09
Nodes (21): enrich_offer(), is_thin(), Replace a thin description in place; richer descriptions are left alone.      Ca, True when a description is too short to be worth embedding on its own., content_hash(), OfferRecord, Normalized DTOs that every source emits, decoupled from source-specific JSON., sha256(lower(title + company + first 500 chars of description)).      This is th (+13 more)

### Community 44 - "test_cold_outreach.py"
Cohesion: 0.10
Nodes (16): BaseException, Operation, ProgressRegistry, Any, datetime, Update a running operation. A key that is not running is ignored., Close an operation. The first outcome recorded wins.          A handled failure, Everything running, plus anything that finished very recently. (+8 more)

### Community 45 - "_FakePage"
Cohesion: 0.23
Nodes (22): launch_wttj_application(), Fill a WTTJ inline form and submit only behind the explicit live gate., _events(), _FakeLauncher, _FakePage, Connection, Path, Row (+14 more)

### Community 46 - "MissingCredentialError"
Cohesion: 0.10
Nodes (22): _F, gate(), Label what this function refuses, and what refusing costs.      Attached to the, The tier this failure carries HERE.      An unclassified error is fatal. That de, What a gate firing is allowed to cost.      Task 39. Seven consecutive generatio, Tier, tier_for(), StrEnum (+14 more)

### Community 47 - "ats.py"
Cohesion: 0.15
Nodes (23): download_filename(), Download names an employer folder can still be read a week later.  ``output/appl, Reduce free text to ``[A-Za-z0-9-_]``, or to "" if nothing survives.      Accent, Build ``<Company>_<Type>_<Nom>.<ext>`` for one artefact.      Falls back to the, slugify(), _client(), Connection, Path (+15 more)

### Community 48 - "AnthropicTailoringAdvisor"
Cohesion: 0.10
Nodes (37): ApplicationGenerationError, A redacted generation failure suitable for CLI and dashboard display., Validate the one JSON contract shared by every advisor provider., unsupported number 27001' was rejecting real, bank-backed vocabulary., test_the_observed_failure_no_longer_fails_a_generation(), _experience_content(), _FabricatingAdvisor, _gemini_shaped_payload() (+29 more)

### Community 49 - "OpenAITailoringAdvisor"
Cohesion: 0.12
Nodes (29): Decision, RouteId, adapter_for_url(), Return the owning ATS adapter, if the saved offer URL is recognized., Remove configured secrets from exception text before display/logging., Settings, _applicant_reason(), _ats_prefill() (+21 more)

### Community 50 - "resolve_fact_id"
Cohesion: 0.17
Nodes (22): _city(), _company_name(), _contract_type(), _domain(), _first(), map_company(), map_offer(), Any (+14 more)

### Community 51 - "test_tech_additions.py"
Cohesion: 0.15
Nodes (26): bank(), _offer(), LogCaptureFixture, Zone 3 may add a keyword, but only one he has and the offer asked for., Reorder-only remains the default and the common case., Genuinely his, but padding: the offer did not ask for it., Presence in the bank is necessary, never sufficient., Derived from the file, not a magic number. (+18 more)

### Community 52 - "load_fact_bank"
Cohesion: 0.09
Nodes (41): facts_cmd(), Print the provenance fact bank grouped for human review., _boolean(), build_cv_title(), CertificationFact, _claim_list(), EducationFact, _entry_claim() (+33 more)

### Community 53 - "CompanyRecord"
Cohesion: 0.23
Nodes (15): AnthropicTailoringAdvisor, Claude Messages API adviser used when ``ANTHROPIC_API_KEY`` is set., _Client, _offer(), _plan_payload(), Any, Exception, Focused contracts for tailoring advisers and the script toolchain. (+7 more)

### Community 54 - "labonnealternance.py"
Cohesion: 0.12
Nodes (15): _InventsThenRecovers, Connection, LogCaptureFixture, Path, Task 37 item 2: give the unknown-id retry something to work with.  An unknown fa, Cites an id that exists nowhere, for a chosen number of attempts., One retry was not enough for this failure. Two is., Keeps making a provenance error that has no deterministic repair. (+7 more)

### Community 55 - "ingest_source"
Cohesion: 0.15
Nodes (12): Connection, Path, Nothing is weakened: a fabrication ends the run exactly as before., An invented figure is recoverable — the retry is handed the real ones —     but, test_a_fatal_gate_still_aborts(), test_a_recoverable_gate_with_no_degradation_escalates_to_fatal(), test_an_advisory_gate_never_blocks(), Connection (+4 more)

### Community 56 - "pick_variant"
Cohesion: 0.15
Nodes (11): BrowserLauncher, _ConfirmationBaseline, _Locator, _Page, PrefillPlan, Protocol, The actions selected from a page's current HTML fixture/markup., A launch seam: production opens Playwright, tests supply a stub page. (+3 more)

### Community 57 - "test_fact_id_resolution.py"
Cohesion: 0.21
Nodes (20): _queued_application(), _Invents, Connection, MonkeyPatch, Path, Task 37 item 4: count invention, so the other three items are not guesswork.  Pr, Counting is about what the model invented, not about what was salvaged.      Dro, Item 3 degrades the CV; that is a different outcome from getting it right. (+12 more)

### Community 58 - "test_letter_locked_fields.py"
Cohesion: 0.21
Nodes (17): bank(), _letter(), _offer(), A letter is prose about a career; a CV is slots the renderer fills., Naming a real-sounding employer he never had is a fabrication, not prose., The renderer injects the address block; the body repeating it is a bug., The bank's own text names nothing it should not; selection is the check., The blocked sentence: a letter that cannot say where you work is not a letter. (+9 more)

### Community 59 - "launch_application_assist"
Cohesion: 0.10
Nodes (34): FactClaim, pick_variant(), Pick the best of 21 variants from missions, then apply contract rules.      Sinc, Task 39 demoted this to advisory.      A tool listed under two categories is cos, test_duplicate_tool_across_categories_warns_without_blocking(), rendered(), _offer(), Systemic recovery at the generated-prose and document-layout boundaries. (+26 more)

### Community 60 - "test_letter_quality.py"
Cohesion: 0.24
Nodes (16): _default_letter(), french_de_elision(), Return « de <noun> » or « d'<noun> », applying French elision.      Elides befor, _validate_letter_body(), _letter(), _offer(), Letter quality: French elision and the 'Entreprise' placeholder rejection., test_default_letter_elides_poste_before_vowel() (+8 more)

### Community 61 - "test_mailer.py"
Cohesion: 0.22
Nodes (16): _alert_source_clause(), Connection, Restrict to one alert source, or to all of them when none is named., Re-derive company / city / workplace / easy-apply for stored alert offers., reparse_alerts(), ReparseResult, Connection, The card line survived in companies.name; the city held only chrome. (+8 more)

### Community 62 - "models.py"
Cohesion: 0.17
Nodes (22): list_outreach_targets(), Companies an ingestion source flagged as likely to hire an alternant.      These, get_or_create_company(), CompanyRecord, _no_real_sleeping(), Connection, MonkeyPatch, Backoff between retries is real seconds; the test suite must not spend them. (+14 more)

### Community 63 - "reparse_alerts"
Cohesion: 0.20
Nodes (17): _generation_failed_detail(), _InteractiveShapedAdvisor, Any, Connection, LogCaptureFixture, Path, _queued_application(), One automatic advisor retry, fed only the validator's own error text. (+9 more)

### Community 64 - "test_designation_numbers.py"
Cohesion: 0.20
Nodes (15): Container, _designation_spans(), ProvenanceScope, Everything true of the career the generated text is describing.      Generated t, Check every designation against the scope; return what it covers.      Designati, Blank out validated designations, keeping every other offset intact., Build the rejection and record it, so the misses can be counted later.      This, Tier 1. A measurement belongs to the entry it was measured in. (+7 more)

### Community 65 - "test_fact_id_consistency.py"
Cohesion: 0.20
Nodes (15): bank(), _bank_payload(), Path, Task 35 item 2: a fact bank whose claim ids do not extend their entry is invalid, The real bank must satisfy the rule the loader now enforces., This is the exact shape the Baïfall entry had., Projects have the same shape as experience, so they get the same rule., `experience.baifallX` starts with the entry id as a STRING but is a     differen (+7 more)

### Community 66 - "review.py"
Cohesion: 0.12
Nodes (26): application_detail(), applications_by_status(), event_history(), invention_report(), outreach_drafts(), Any, Connection, queued_applications() (+18 more)

### Community 67 - "ingest_source"
Cohesion: 0.13
Nodes (26): apply_matching_profile_cmd(), Connection, _queue_snapshot(), Apply config/matching_profile.yaml and report what it changed.      Re-scoring i, Count what currently clears the bar, for an honest before/after., Re-evaluate every offer against the new vocabulary.      ``jobpilot score`` only, _rescore_all(), ensure_profile_embedding() (+18 more)

### Community 68 - "_AnchorParser"
Cohesion: 0.05
Nodes (73): Client, LookupError, SimpleNamespace, ApplicationNotFoundError, ApplyOutcome, approve_application(), archive_artifacts(), Any (+65 more)

### Community 69 - "test_preview.py"
Cohesion: 0.23
Nodes (12): _bullet_budget(), _claim_length(), An experience claim has to fit the CV's one line.  The renderer inserts a select, Every experience bullet the template ships, as (employer, plain text).      Enti, The longest experience bullet the template itself already renders on one line., Derived from the file, not a magic number., Without this the constant could go stale and quietly widen the budget., The renderer inserts these verbatim, so a long one wraps in silence. (+4 more)

### Community 70 - "vocabulary.py"
Cohesion: 0.07
Nodes (38): FastAPI, RefreshRunner, Request, dashboard_cmd(), Launch the local review dashboard on 127.0.0.1., _candidate_name(), _citation_warning(), create_app() (+30 more)

### Community 71 - "UnknownFactIdError"
Cohesion: 0.10
Nodes (33): parse_linkedin(), Extract jobs from a LinkedIn job-alert email., _card_html(), LogCaptureFixture, Structural parsing of job-alert cards (Task 20).  Every fixture here is shaped a, The same four values models.REMOTE_POLICIES defines for every source., Indeed writes "Villeneuve-d'Ascq (59)" — the postcode is not a workplace., Whatever position the chrome occupies, it must not be stored. (+25 more)

### Community 72 - "Baifall Dream Stage - Reference Document (v3)"
Cohesion: 0.17
Nodes (11): Baifall Dream Stage - Reference Document (v3), Bloc HTML de reference (3 bullets), Bullet 1 (commun, accompli) - 167 car., rendu sur 2 lignes, Bullet 2 (commun, nominal, perimetre complet) - 127 car., 1 ligne, Bullet 3 : declinaisons par variante, Context, Principe v3 : perimetre nominal complet, Regle pour la date (+3 more)

### Community 73 - "test_facts.py"
Cohesion: 0.05
Nodes (81): observable_controls(), Every fillable control's *shape*, for form learning. Never its contents.      ``, Whether a stored selector still finds a control on the current page., selector_matches_html(), build_prefill(), discard_mapping(), fields_from_html(), FormField (+73 more)

### Community 74 - "test_progress.py"
Cohesion: 0.09
Nodes (39): apply_matching_profile(), load_matching_profile(), MatchingProfile, Write the vocabulary onto the profile singleton. Returns {field: (before, after), The scoring vocabulary, committed to git rather than typed once.      These thre, Load the committed matching vocabulary, failing loudly rather than defaulting., Connection, Path (+31 more)

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
Cohesion: 0.29
Nodes (8): ExperienceFact, _employer_bullet_floor(), _experience_start(), Sort key from an experience's start date, most recent first., How many bullets the completeness floor guarantees this employer.      Read from, _reverse_chronological_experiences(), The completeness floor is a hard failure, not a preference., test_the_last_bullet_the_floor_requires_is_never_dropped()

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
Cohesion: 0.40
Nodes (5): letter_plain_text(), open_manually(), Path, The generated letter as plain text, or '' when it was never generated., The manual_open route: open the offer, copy the letter, submit nothing.      A l

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
Nodes (68): FactBank, allowed_numbers(), _bank_parts(), letter_scope(), _normalized_number(), _offer_identity(), _organisation_names(), Everything the verified bank says the candidate has actually touched.      Only (+60 more)

### Community 112 - "test_ingest_idempotent.py"
Cohesion: 0.07
Nodes (55): Return capability-tier tokens that have tripped generations, by frequency., vocabulary_misses(), GenericVocabularyError, load_generic_vocabulary(), parse_rejections(), Path, ValueError, Recover the refused tokens from stored validator messages.      The events table (+47 more)

### Community 113 - "apply_matching_profile_cmd"
Cohesion: 0.50
Nodes (7): is_enabled(), Path, Source enablement via config/sources.yaml., _settings(), test_disabled_source_excluded(), test_no_config_all_enabled(), test_replace_keeps_dataclass_shape()

### Community 116 - "mappings_for"
Cohesion: 0.48
Nodes (6): source_id(), _offer(), Connection, content_hash dedup + INSERT OR IGNORE behavior., test_same_content_hash_collapses_to_one_row(), test_same_external_id_ignored()

### Community 117 - "tracker.py"
Cohesion: 0.24
Nodes (10): datetime, counts(), Connection, The tracker: every application, one table, read-only.  Deliberately not a Google, Statuses that actually occur, so the filter offers no dead options., The four numbers worth seeing before the table itself., Monday 00:00 UTC of the current week, as ISO text.      Compared as text against, statuses() (+2 more)

### Community 120 - "test_ingest_idempotent.py"
Cohesion: 0.38
Nodes (8): FakeSource, Connection, Re-running ingest must never duplicate rows (constitution idempotency rule)., _sample(), test_company_deduped_across_offers_and_runs(), test_first_run_inserts_all(), test_last_run_at_updated(), test_second_run_inserts_nothing()

### Community 121 - "run_menubar"
Cohesion: 0.08
Nodes (31): Logger, SentenceTransformer, Put text on the system clipboard, or say plainly that it could not.  The manual_, _env_bool(), get_settings(), _path(), Configuration and path resolution. Secrets come from .env only (never mocked)., _as_list() (+23 more)

### Community 123 - "test_renderer_owned_fields.py"
Cohesion: 0.17
Nodes (12): CvProfile, Renderer-owned CV header location; the advisor has no say in it.      Prefers th, resolve_header_location(), test_header_location_prefers_the_offer_region_then_the_profile(), The guarantees that made four _validate_plan branches unreachable.  Task 39 item, The one input to resolve_header_location that comes from config., _offer_start falls back to « septembre 2026 », so there is always one., test_prose_canonicalization_removes_every_dash_the_letter_gate_looked_for() (+4 more)

### Community 124 - "ApplicationNotQueuedError"
Cohesion: 0.12
Nodes (30): ApplicationNotQueuedError, generation_single_flight(), GenerationInFlight, InteractiveAdvisorRequired, RuntimeError, Shared human-approval and document-generation application flow., Raised when an approval targets an application outside the review queue., Raised when a generation is already running for this application. (+22 more)

### Community 125 - "parse_indeed"
Cohesion: 0.29
Nodes (7): clean_job_url(), parse_indeed(), Return a stable detail URL with email/tracking parameters removed., Extract jobs from an Indeed job-alert email., test_clean_job_url_removes_tracking_parameters(), test_parse_ignores_non_job_links(), test_parse_indeed_extracts_jk_ids()

### Community 126 - "test_sourcing_targets_changes_no_sending_gate"
Cohesion: 0.40
Nodes (3): Which CV was used, who chose it, and what the keyword layer suggested.      Both, The catalogue slug, with any stage suffix removed., VariantDecision

### Community 132 - "observable_controls"
Cohesion: 0.07
Nodes (34): _Control, _ControlParser, _controls_from_html(), _css_attribute_value(), FillAction, _first_matching_selector(), _Form, _FormParser (+26 more)

## Knowledge Gaps
- **155 isolated node(s):** `applications`, `profile`, `contacts`, `suppression_list`, `offers` (+150 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `OpenAITailoringAdvisor` to `_client`, `observable_controls`, `Path`, `test_routing.py`, `mailer.py`, `wttj.py`, `SourcedBullet`, `france_travail.py`, `_FakePage`, `test_email_alerts.py`, `test_labonnealternance.py`, `Settings`, `test_dashboard_facts_scheduler.py`, `.from_mapping`, `_FakePage`, `resolve_fact_id`, `pick_variant`, `test_retry_feedback.py`, `apply_matching_profile_cmd`, `run_menubar`, `_FakeLocator`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `run_menubar` to `_client`, `create_app`, `observable_controls`, `dashboard.py`, `run_dashboard`, `test_routing.py`, `mailer.py`, `apply_assist.py`, `test_skim.py`, `wttj.py`, `SourcedBullet`, `launch_wttj_application`, `test_email_alerts.py`, `_Toolchain`, `_FakePage`, `OpenAITailoringAdvisor`, `test_fact_id_resolution.py`, `ingest_source`, `vocabulary.py`, `test_retry_feedback.py`, `apply_matching_profile_cmd`, `mappings_for`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `TailoringError` connect `connect` to `test_designation_numbers.py`, `test_downloads.py`, `_Toolchain`, `_AnchorParser`, `dashboard.py`, `vocabulary.py`, `test_cv_completeness.py`, `OfferRecord`, `MissingCredentialError`, `_AnchorParser`, `test_valid_sourced_advice_completes_the_shared_generation_path`, `AnthropicTailoringAdvisor`, `CompanyRecord`, `labonnealternance.py`, `ingest_source`, `test_letter_quality.py`, `generate_application`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Are the 62 inferred relationships involving `Settings` (e.g. with `ApplicantProfile` and `ApplyAdapter`) actually correct?**
  _`Settings` has 62 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `TailoringError` (e.g. with `_CompleteAdvisor` and `_IncompleteAdvisor`) actually correct?**
  _`TailoringError` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `OfferRecord` (e.g. with `BackfillResult` and `RescoreResult`) actually correct?**
  _`OfferRecord` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `_Toolchain` (e.g. with `TailoringError` and `TailoringPlan`) actually correct?**
  _`_Toolchain` has 2 INFERRED edges - model-reasoned connections that need verification._