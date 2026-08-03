# Graph Report - jobpilot  (2026-08-04)

## Corpus Check
- 156 files · ~188,993 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3385 nodes · 8724 edges · 143 communities (122 shown, 21 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 353 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `780480d3`
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
- skim.py
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
- test_variant_selection.py
- reparse_alerts
- test_profile_domain_anchor.py
- tracker.py
- _TextParser
- refresh_operation
- test_ingest_idempotent.py
- run_menubar
- _FakeLocator
- test_renderer_owned_fields.py
- ApplicationNotQueuedError
- parse_indeed
- build_advisor
- 008_applications_generation_warnings.sql
- _client
- ApplicantProfile
- test_progress.py
- .finish
- observable_controls
- test_registry.py
- Request
- _Advisor
- SendBlocked
- InteractiveTailoringAdvisor
- Client
- Any
- Protocol
- RuntimeError
- StrEnum

## God Nodes (most connected - your core abstractions)
1. `Settings` - 117 edges
2. `current_status()` - 94 edges
3. `_payload()` - 89 edges
4. `TailoringError` - 83 edges
5. `load_fact_bank()` - 70 edges
6. `_Toolchain` - 69 edges
7. `OfferRecord` - 68 edges
8. `create_app()` - 62 edges
9. `OfferContext` - 59 edges
10. `get_settings()` - 59 edges

## Surprising Connections (you probably didn't know these)
- `_CompleteAdvisor` --uses--> `TailoringError`  [INFERRED]
  tests/test_cv_completeness.py → src/jobpilot/tailoring.py
- `_RecordingToolchain` --uses--> `TailoringError`  [INFERRED]
  tests/test_cv_completeness.py → src/jobpilot/tailoring.py
- `_BadSourceAdvisor` --uses--> `TailoringError`  [INFERRED]
  tests/test_fact_id_resolution.py → src/jobpilot/tailoring.py
- `_RecordingAdvisor` --uses--> `TailoringError`  [INFERRED]
  tests/test_fact_id_resolution.py → src/jobpilot/tailoring.py
- `_OneShotProfileOrphan` --uses--> `TailoringError`  [INFERRED]
  tests/test_generation_resilience.py → src/jobpilot/tailoring.py

## Import Cycles
- None detected.

## Communities (143 total, 21 thin omitted)

### Community 0 - "test_downloads.py"
Cohesion: 0.14
Nodes (14): ProgressRegistry, Report one operation for as long as it runs, however it ends.      ``with track(, Every operation currently worth reporting, keyed by a stable string., track, _utc_now(), It stays briefly so a poll landing just after completion sees the     outcome, t, A failure that never cleared its progress would leave the page claiming     work, test_a_failure_closes_the_operation_and_keeps_its_message() (+6 more)

### Community 1 - "Request"
Cohesion: 0.08
Nodes (55): Resolve one archived artefact, with the same discipline as the live one.      De, _safe_archive_path(), _archives_for(), Generation, is_archive_stamp(), library_entries(), LibraryEntry, _mtime_iso() (+47 more)

### Community 2 - "_candidate_name"
Cohesion: 0.09
Nodes (75): current_status(), _client(), _events(), _no_advisor_client(), _offer_application(), Connection, MonkeyPatch, Path (+67 more)

### Community 3 - "_client"
Cohesion: 0.13
Nodes (17): adapter_for_url(), _application_for_assist(), _application_for_wttj(), ApplyAssistError, AssistResult, _fallback(), launch_application_assist(), Connection (+9 more)

### Community 4 - "create_app"
Cohesion: 0.07
Nodes (41): apply_cmd(), invention_report_cmd(), queue_cmd(), List queued applications, highest final_score first., Approve an application and generate its tailored application documents., Show how often the advisor cites a fact id that does not exist.      Task 37 add, apply_schema(), connect() (+33 more)

### Community 5 - "dashboard.py"
Cohesion: 0.06
Nodes (81): CvProfile, ExperienceFact, FactBank, Match, Pattern, _add_tech_additions(), _add_tech_keywords(), _bank_parts() (+73 more)

### Community 6 - "run_dashboard"
Cohesion: 0.11
Nodes (29): bank(), _dropping_enabled(), _InventsForever, _plan(), Connection, MonkeyPatch, Path, Task 37 item 3: degradation. Shipped off, turned ON by Task 39.  If the advisor (+21 more)

### Community 7 - "Path"
Cohesion: 0.09
Nodes (34): derive_fields(), _Derived, Re-derive alert card fields (company / city / workplace / easy-apply) in place., Re-derive one offer's card fields from the text that was stored for it.      Pur, _AlertAnchor, _AnchorParser, _anchors(), _Card (+26 more)

### Community 8 - "test_routing.py"
Cohesion: 0.10
Nodes (58): Cursor, _artifacts(), Path, Resolve the one route this application would go out by. Writes nothing., The resolved plan for one application. Carries no state and stores none., Fingerprint of exactly the inputs that decided this route.          Stateless by, resolve_route(), Route (+50 more)

### Community 9 - "mailer.py"
Cohesion: 0.11
Nodes (41): _as_utc(), _build_message(), build_sender(), ColdEmailPreparation, daily_cap_reached(), _default_body(), EmailPreparation, EmailSender (+33 more)

### Community 10 - "validate_cv.py"
Cohesion: 0.06
Nodes (53): check_orphans(), find_regressions(), Path, Return orphan metrics that are new or materially worse than the template., format_date(), main(), build_letter_html(), detect_github() (+45 more)

### Community 11 - "get_settings"
Cohesion: 0.07
Nodes (42): Any, RuntimeError, _advise_and_tailor(), _advisor_fact_context(), _canonicalize_prose(), _fact_id_list(), _interactive_structured_payload(), _is_validator_rejection() (+34 more)

### Community 12 - "connect"
Cohesion: 0.05
Nodes (51): add_contact_cmd(), apply_matching_profile_cmd(), backfill_descriptions_cmd(), contacts_cmd(), _csv(), draft_cold_cmd(), init_db_cmd(), init_profile_cmd() (+43 more)

### Community 13 - "test_descriptions.py"
Cohesion: 0.10
Nodes (50): backfill_descriptions(), BackfillResult, clear_match_scores(), is_synthesized(), Connection, Synthesise matchable text for offers that arrive with no description.  Job-alert, Return an SQL fragment + params restricting a query to one source., Regenerate synthesised descriptions for stored offers whose text is thin.      I (+42 more)

### Community 14 - "test_generic_vocabulary.py"
Cohesion: 0.18
Nodes (11): ApplyOutcome, approve_application(), Any, Connection, Record human approval, transition, and generate through one shared path.      ``, The result shared by the CLI and dashboard approval surfaces., Connection, Path (+3 more)

### Community 15 - "apply_assist.py"
Cohesion: 0.28
Nodes (17): Combined application + cold-mail sends recorded for today (UTC)., sends_today(), _events(), Connection, EmailMessage, Exception, Path, Application email sending: rails, transitions, and events (mocked SMTP). (+9 more)

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
Cohesion: 0.28
Nodes (17): OpenAITailoringAdvisor, OpenAI-compatible Chat Completions adviser., _offer(), _openai_response(), _plan_payload(), Any, Connection, Path (+9 more)

### Community 20 - "_payload"
Cohesion: 0.10
Nodes (45): _bullets(), _project(), The advisor selects; the renderer inserts the bank's wording unchanged., The pre-written variants from the skill asset, used as the asset intends., The contract has no field for prose, so a writing advisor fails loudly., Only the entry's own facts, so a skill id cannot become a bullet., Task 25's tolerance survives: ids are normalised before they are judged., The phrase is short, but it is still generated, so the tiers still read it. (+37 more)

### Community 21 - "wttj.py"
Cohesion: 0.10
Nodes (41): _city(), _contact_email(), _contract(), _first(), map_hit(), _org(), _prose(), Any (+33 more)

### Community 22 - "SourcedBullet"
Cohesion: 0.11
Nodes (20): ConnectionFactory, Event, IngestResult, Any, RuntimeError, Single-flight ingest + score pass driven from the dashboard., Block until the running refresh finishes. Tests use this, not sleeps., Claim the single flight and hand the work to a background thread. (+12 more)

### Community 23 - "france_travail.py"
Cohesion: 0.09
Nodes (30): _delay(), Rate limiting + exponential backoff for every external call (constitution rule)., Call fn(); retry on transient HTTP errors with full-jitter exponential backoff., with_backoff(), _first_nonempty(), FranceTravailSource, _map_contact_email(), _map_contract() (+22 more)

### Community 24 - "test_provenance_tiers.py"
Cohesion: 0.08
Nodes (33): bank(), _in_bank(), Three kinds of token, three different burdens of proof., Not even the widest scope can support it., The reader has to be able to search for it, or add it to the config., Task 26's handling survives as the digit-shaped corner of tier 2., Presence in the bank is necessary for tier 2, never sufficient., No fact anywhere carries these figures, so no scope can accept them. (+25 more)

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
Cohesion: 0.19
Nodes (29): Every offer application, optionally narrowed to one status., tracker_rows(), _application(), _client(), Connection, Path, TestClient, Task 36 item 5: the tracker page.  Read-only in the strict sense: nothing here w (+21 more)

### Community 29 - "test_desktop_shell.py"
Cohesion: 0.07
Nodes (36): CaptureFixture, dashboard_cmd(), Launch the local review dashboard on 127.0.0.1., dashboard_already_running(), Whether something is already listening on the dashboard's port.      A connect p, Run the dashboard on an intentionally fixed loopback interface.      Returns a p, run_dashboard(), The menu bar text. Short: it competes with every other item up there. (+28 more)

### Community 30 - "generate_application"
Cohesion: 0.08
Nodes (29): date, GenerationWarning, Protocol, _check_orphans(), _contains_generated_orphan(), DocumentToolchain, _french_date(), generate_application() (+21 more)

### Community 31 - "test_contacts.py"
Cohesion: 0.10
Nodes (27): ModuleType, JobPilot: personal job application pipeline for the French IT/cybersecurity mark, _application(), _ConnectionProxy, Connection, Exception, Path, CLI coverage for offer document generation and cold-application approval. (+19 more)

### Community 32 - "test_email_alerts.py"
Cohesion: 0.09
Nodes (43): Message, GmailIMAP, html_of(), LinkedInAlertSource, Minimal read-only Gmail IMAP client., Fetch recent mail sent from `domains` (or any of their subdomains).          The, Return the best HTML (or plain-text) body of an email message., Return the lowercased domain of the address in a `From` header.      Parses the (+35 more)

### Community 33 - "test_labonnealternance.py"
Cohesion: 0.10
Nodes (38): _fixture(), _NoWait, LogCaptureFixture, La Bonne Alternance through the API Apprentissage: mapping, rails, ingestion.  E, The endpoint has no pagination, so this is the volume knob that exists., A full ingest reads both lists; it must not pay for the search twice., The live API really does repeat an offer inside one response., A company that has posted nothing must not appear in the review queue. (+30 more)

### Community 34 - "_Toolchain"
Cohesion: 0.09
Nodes (25): _correction_block(), _json_object(), Raised when an external tailoring provider request fails., Raised when a tailoring provider rejects its API credentials., Raised when a tailoring provider rate-limits a request., Raised when a provider returns an unusable response., The advisor's reasoned CV pick, before any mechanical contract rule., Validate a selection answer. The model may not invent a variant. (+17 more)

### Community 35 - "email_alerts.py"
Cohesion: 0.07
Nodes (44): _advisor_prompt(), extract_template_context(), Read all editable choices without altering the template., Every id the advisor may cite, flattened out of the context it was given.      D, valid_fact_ids(), The unwrapped second call that killed the Capgemini generation.      A degradati, test_the_profile_fallback_survives_its_own_fallback_failing(), Listing the numbers is not enough on its own: the failure was a dropped +. (+36 more)

### Community 36 - "test_alert_card_fields.py"
Cohesion: 0.11
Nodes (31): as_dicts(), clear_warnings(), _decode(), GenerationWarning, Any, Connection, What a generation had to degrade, recorded where the reviewer will see it.  Task, Gate names per application, for the library and tracker markers.      One query (+23 more)

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
Cohesion: 0.13
Nodes (23): _category_skills(), _CompleteAdvisor, Any, Connection, Path, _Toolchain, _queued_application(), Structural completeness floor for AI-generated CVs (Task 22).  Selection freedom (+15 more)

### Community 41 - "OfferRecord"
Cohesion: 0.08
Nodes (28): _advise(), ambiguous_bank(), _BadSourceAdvisor, bank(), _offer(), Any, LogCaptureFixture, Path (+20 more)

### Community 42 - "test_dashboard_facts_scheduler.py"
Cohesion: 0.29
Nodes (16): _client(), fixture_bank(), Connection, MonkeyPatch, Path, TestClient, Read-only fact bank page and honest scheduler reporting on the queue page., test_daemon_state_follows_the_recorded_heartbeat_age() (+8 more)

### Community 43 - ".from_mapping"
Cohesion: 0.11
Nodes (18): enrich_offer(), is_thin(), Replace a thin description in place; richer descriptions are left alone.      Ca, True when a description is too short to be worth embedding on its own., OfferRecord, One normalized offer, ready to insert into the offers table., Coerce enum-constrained fields to legal values (schema CHECK safety)., Yield normalized offers. Must apply rate limiting + backoff internally. (+10 more)

### Community 44 - "test_cold_outreach.py"
Cohesion: 0.11
Nodes (28): daemon_cmd(), ingest_cmd(), Run ingest + score on a loop (Ctrl-C to stop)., Fetch offers from a source (or all sources) into the database., daemon_status(), DaemonStatus, heartbeat_path(), Any (+20 more)

### Community 45 - "_FakePage"
Cohesion: 0.23
Nodes (22): launch_wttj_application(), Fill a WTTJ inline form and submit only behind the explicit live gate., _events(), _FakeLauncher, _FakePage, Connection, Path, Row (+14 more)

### Community 46 - "MissingCredentialError"
Cohesion: 0.10
Nodes (24): _F, FactClaim, gate(), Label what this function refuses, and what refusing costs.      Attached to the, The tier this failure carries HERE.      An unclassified error is fatal. That de, A selected fact must be a real, reviewed fact OF THAT ENTRY.      This is the wh, What a gate firing is allowed to cost.      Task 39. Seven consecutive generatio, Tier (+16 more)

### Community 47 - "ats.py"
Cohesion: 0.15
Nodes (23): download_filename(), Download names an employer folder can still be read a week later.  ``output/appl, Reduce free text to ``[A-Za-z0-9-_]``, or to "" if nothing survives.      Accent, Build ``<Company>_<Type>_<Nom>.<ext>`` for one artefact.      Falls back to the, slugify(), _client(), Connection, Path (+15 more)

### Community 48 - "AnthropicTailoringAdvisor"
Cohesion: 0.06
Nodes (61): OfferContext, _omit_offending_paragraph(), _paragraph_offends(), pick_variant(), Pick the best of 21 variants from missions, then apply contract rules.      Sinc, Offer data exposed to an automatic or interactive tailoring adviser., Whether this one paragraph is what _validate_letter_body refused.      Only the, Drop the one paragraph the letter gate refused, keeping the rest.      The retry (+53 more)

### Community 49 - "OpenAITailoringAdvisor"
Cohesion: 0.15
Nodes (25): Decision, RouteId, Remove configured secrets from exception text before display/logging., Settings, _applicant_reason(), _ats_prefill(), _email(), _learned_form() (+17 more)

### Community 50 - "resolve_fact_id"
Cohesion: 0.25
Nodes (17): _city(), _company_name(), _contract_type(), _domain(), _first(), map_company(), map_offer(), Any (+9 more)

### Community 51 - "test_tech_additions.py"
Cohesion: 0.15
Nodes (26): bank(), _offer(), LogCaptureFixture, Zone 3 may add a keyword, but only one he has and the offer asked for., Reorder-only remains the default and the common case., Genuinely his, but padding: the offer did not ask for it., Presence in the bank is necessary, never sufficient., Derived from the file, not a magic number. (+18 more)

### Community 52 - "load_fact_bank"
Cohesion: 0.09
Nodes (40): facts_cmd(), Print the provenance fact bank grouped for human review., _boolean(), CertificationFact, _claim_list(), EducationFact, _entry_claim(), ExperienceFact (+32 more)

### Community 53 - "CompanyRecord"
Cohesion: 0.17
Nodes (19): AnthropicTailoringAdvisor, Claude Messages API adviser used when ``ANTHROPIC_API_KEY`` is set., _Client, _offer(), _plan_payload(), Any, Exception, MonkeyPatch (+11 more)

### Community 54 - "labonnealternance.py"
Cohesion: 0.11
Nodes (17): _InteractiveShapedAdvisor, Human loop: always rejected, and never re-prompted automatically., _InventsThenRecovers, Connection, LogCaptureFixture, Path, Task 37 item 2: give the unknown-id retry something to work with.  An unknown fa, Cites an id that exists nowhere, for a chosen number of attempts. (+9 more)

### Community 55 - "ingest_source"
Cohesion: 0.16
Nodes (11): Connection, Path, Nothing is weakened: a fabrication ends the run exactly as before., An invented figure is recoverable — the retry is handed the real ones —     but, test_a_fatal_gate_still_aborts(), test_a_recoverable_gate_with_no_degradation_escalates_to_fatal(), test_an_advisory_gate_never_blocks(), End to end, on the failure that killed applications 25 and 28.      The live re- (+3 more)

### Community 56 - "pick_variant"
Cohesion: 0.16
Nodes (11): BrowserLauncher, _ConfirmationBaseline, _Locator, _Page, PrefillPlan, Protocol, The actions selected from a page's current HTML fixture/markup., A launch seam: production opens Playwright, tests supply a stub page. (+3 more)

### Community 57 - "test_fact_id_resolution.py"
Cohesion: 0.21
Nodes (21): invention_report(), How often the advisor cites an id that does not exist, and whether it recovers., _Invents, Connection, MonkeyPatch, Path, Task 37 item 4: count invention, so the other three items are not guesswork.  Pr, Counting is about what the model invented, not about what was salvaged.      Dro (+13 more)

### Community 58 - "test_letter_locked_fields.py"
Cohesion: 0.18
Nodes (19): bank(), _letter(), _offer(), A letter is prose about a career; a CV is slots the renderer fills., Naming a real-sounding employer he never had is a fabrication, not prose., The renderer injects the address block; the body repeating it is a bug., Otherwise the test above would prove nothing about scope., The bank's own text names nothing it should not; selection is the check. (+11 more)

### Community 59 - "launch_application_assist"
Cohesion: 0.15
Nodes (21): ATSSource, infer_contract(), load_targets(), map_greenhouse(), map_lever(), map_smartrecruiters(), _ms_to_iso(), Any (+13 more)

### Community 60 - "test_letter_quality.py"
Cohesion: 0.24
Nodes (16): _default_letter(), french_de_elision(), Return « de <noun> » or « d'<noun> », applying French elision.      Elides befor, _validate_letter_body(), _letter(), _offer(), Letter quality: French elision and the 'Entreprise' placeholder rejection., test_default_letter_elides_poste_before_vowel() (+8 more)

### Community 61 - "test_mailer.py"
Cohesion: 0.23
Nodes (14): It did not block, so the only thing standing between it and invisibility     is, test_an_advisory_orphan_is_recorded_on_the_application(), test_the_library_and_tracker_mark_a_degraded_application(), _approve(), Connection, LogCaptureFixture, Path, The asset file calls these false positives outside a full render. (+6 more)

### Community 62 - "models.py"
Cohesion: 0.13
Nodes (18): _OneShotProfileOrphan, Connection, Path, _Toolchain, Systemic recovery at the generated-prose and document-layout boundaries., A profile-only layout regression that disappears with template wording., _selection_and_template(), test_a_valid_custom_profile_phrase_is_preserved_exactly() (+10 more)

### Community 63 - "reparse_alerts"
Cohesion: 0.22
Nodes (15): _generation_failed_detail(), Any, Connection, LogCaptureFixture, Path, _queued_application(), One automatic advisor retry, fed only the validator's own error text., Re-calling on a 429 or a bad key is not feedback, it is a retry storm. (+7 more)

### Community 64 - "test_designation_numbers.py"
Cohesion: 0.20
Nodes (15): Container, _designation_spans(), ProvenanceScope, Everything true of the career the generated text is describing.      Generated t, Check every designation against the scope; return what it covers.      Designati, Blank out validated designations, keeping every other offset intact., Build the rejection and record it, so the misses can be counted later.      This, Tier 1. A measurement belongs to the entry it was measured in. (+7 more)

### Community 65 - "test_fact_id_consistency.py"
Cohesion: 0.10
Nodes (27): _bullet_budget(), _claim_length(), An experience claim has to fit the CV's one line.  The renderer inserts a select, Every experience bullet the template ships, as (employer, plain text).      Enti, The longest experience bullet the template itself already renders on one line., Derived from the file, not a magic number., Without this the constant could go stale and quietly widen the budget., The renderer inserts these verbatim, so a long one wraps in silence. (+19 more)

### Community 66 - "review.py"
Cohesion: 0.06
Nodes (35): CompletedProcess, AmbiguousFactIdError, _fact_id_key(), _guessed_section(), nearest_entry_claim_ids(), Raised when generated prose states a figure the bank does not contain.      A si, Raised when a citation matches no fact id, even after normalisation.      ``sect, Fold separator and case differences, and nothing else, for comparison. (+27 more)

### Community 67 - "ingest_source"
Cohesion: 0.16
Nodes (15): Connection, Exception, LogCaptureFixture, Path, _queued_application(), Records the gates without pinning them to one offer or one variant., API-shaped advisor: answers selection, then tailors whatever was chosen.      Se, _ready_detail() (+7 more)

### Community 68 - "_AnchorParser"
Cohesion: 0.10
Nodes (28): CatalogueEntry, default_catalogue(), load_variant_catalogue(), _parse_criteria(), _parse_shortcuts(), Path, RuntimeError, The CV catalogue offered to the advisor when it selects a variant.  The selectio (+20 more)

### Community 69 - "test_preview.py"
Cohesion: 0.15
Nodes (22): Apply the mechanical contract and encoding rules to a chosen slug.      These ar, The contract line an adapted alternance CV must carry., The stage contract line to fall back to, built from what is known.      Determin, Preserve a valid contract phrase; replace only a rejected one.      Same shape a, _resolve_stage_contract_phrase(), _stage_contract_fallback(), _validate_stage_contract_phrase(), variant_for_slug() (+14 more)

### Community 70 - "vocabulary.py"
Cohesion: 0.08
Nodes (46): FastAPI, archive_artifacts(), Path, Move an application's current artefacts aside; return where they went.      Diff, copy_text(), Copy ``text``; return whether it actually landed on the clipboard., _candidate_name(), _citation_warning() (+38 more)

### Community 71 - "UnknownFactIdError"
Cohesion: 0.10
Nodes (33): parse_linkedin(), Extract jobs from a LinkedIn job-alert email., _card_html(), LogCaptureFixture, Structural parsing of job-alert cards (Task 20).  Every fixture here is shaped a, The same four values models.REMOTE_POLICIES defines for every source., Indeed writes "Villeneuve-d'Ascq (59)" — the postcode is not a workplace., Whatever position the chrome occupies, it must not be stored. (+25 more)

### Community 72 - "Baifall Dream Stage - Reference Document (v3)"
Cohesion: 0.17
Nodes (11): Baifall Dream Stage - Reference Document (v3), Bloc HTML de reference (3 bullets), Bullet 1 (commun, accompli) - 167 car., rendu sur 2 lignes, Bullet 2 (commun, nominal, perimetre complet) - 127 car., 1 ligne, Bullet 3 : declinaisons par variante, Context, Principe v3 : perimetre nominal complet, Regle pour la date (+3 more)

### Community 73 - "test_facts.py"
Cohesion: 0.05
Nodes (81): Whether a stored selector still finds a control on the current page., selector_matches_html(), build_prefill(), discard_mapping(), fields_from_html(), FormField, FormLearningError, FormMapping (+73 more)

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
Cohesion: 0.15
Nodes (21): Score all unscored offers and queue those above threshold., score_cmd(), _default_score_pass(), _production_connection(), Connection, Score exactly as ``jobpilot score`` does, with the model already loaded., One dedicated connection per refresh; the request's own is long gone., Connection (+13 more)

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
Cohesion: 0.16
Nodes (21): get_or_create_company(), CompanyRecord, Yield companies likely to hire (optional; default: none)., _no_real_sleeping(), Connection, MonkeyPatch, Backoff between retries is real seconds; the test suite must not spend them., Only fetch_companies() produces outreach targets, not offer side effects. (+13 more)

### Community 88 - "profile.py"
Cohesion: 0.13
Nodes (18): CvProfile, CvProfileError, load_cv_profile(), load_variants(), MatchingProfileError, Path, ValueError, Profile singleton + cv_variants seeding.  Persistence logic only (no prompting/p (+10 more)

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

### Community 93 - "skim.py"
Cohesion: 0.14
Nodes (18): available_sources(), _create_application(), ignore_offer(), Connection, Row, ValueError, The skim list: offers that passed the hard filter but scored below threshold.  T, The offer row, if it is genuinely one this page may act on. (+10 more)

### Community 110 - "test_designation_numbers.py"
Cohesion: 0.17
Nodes (16): bank(), _in_bank(), LogCaptureFixture, A standard's digits name a thing; a metric's digits measure one., The anti-fabrication guarantee is not weakened by designation handling., Only the designation's own span is exempt from the number rule., Judge as the letter is judged: no entry, so the whole bank answers., Looking like a standard is not evidence of holding one. (+8 more)

### Community 111 - "_AnchorParser"
Cohesion: 0.07
Nodes (55): allowed_numbers(), letter_scope(), _normalized_number(), _offer_identity(), _organisation_names(), The names the bank knows structurally: employers, schools, diplomas.      Naming, The scope for the letter and the profile's domain phrase.      Attribution still, The parsed fields a letter is entitled to say back to its reader.      An unname (+47 more)

### Community 112 - "test_ingest_idempotent.py"
Cohesion: 0.06
Nodes (61): Return capability-tier tokens that have tripped generations, by frequency., vocabulary_misses(), GenericVocabularyError, load_generic_vocabulary(), parse_rejections(), Path, StrEnum, ValueError (+53 more)

### Community 113 - "apply_matching_profile_cmd"
Cohesion: 0.09
Nodes (34): Logger, SentenceTransformer, Put text on the system clipboard, or say plainly that it could not.  The manual_, _env_bool(), get_settings(), _path(), Configuration and path resolution. Secrets come from .env only (never mocked)., _as_list() (+26 more)

### Community 114 - "test_variant_selection.py"
Cohesion: 0.24
Nodes (19): _answer(), _decision(), _offer(), Any, The advisor chooses the CV; the keyword router is only a sanity check., The bug, pinned: one « pilotage » outweighs twenty technical signals., Template existence is mechanical: never let it break a generation., test_a_slug_with_no_template_file_falls_back_instead_of_failing() (+11 more)

### Community 115 - "reparse_alerts"
Cohesion: 0.22
Nodes (16): _alert_source_clause(), Connection, Restrict to one alert source, or to all of them when none is named., Re-derive company / city / workplace / easy-apply for stored alert offers., reparse_alerts(), ReparseResult, Connection, The card line survived in companies.name; the city held only chrome. (+8 more)

### Community 116 - "test_profile_domain_anchor.py"
Cohesion: 0.19
Nodes (14): _extract_profile_domain(), _profile_of(), Path, Task 40: the domain phrase is found by its own marker, not by its neighbours.  _, Not just the wordings we ship: any of them, including ones nobody wrote yet., A rewrite that dropped it would break the next read instead of this one., The ±15-character layout budget must not shift under it., The bug. This raised "template profile domain phrase not found". (+6 more)

### Community 117 - "tracker.py"
Cohesion: 0.18
Nodes (13): counts(), Any, Connection, datetime, The tracker: every application, one table, read-only.  Deliberately not a Google, Statuses that actually occur, so the filter offers no dead options., Export exactly the visible rows, in the visible column order., The four numbers worth seeing before the table itself. (+5 more)

### Community 118 - "_TextParser"
Cohesion: 0.15
Nodes (5): _ControlParser, HTMLParser, Strip a generated letter's markup down to what a human would paste., Tiny standard-library parser sufficient to test our simple CSS selectors., _TextParser

### Community 119 - "refresh_operation"
Cohesion: 0.23
Nodes (9): Operation, Any, datetime, Everything running, plus anything that finished very recently., Present a RefreshRunner snapshot in the same shape as everything else.      Refr, One slow thing, and how far along it is., refresh_operation(), test_a_refresh_snapshot_becomes_a_per_source_operation() (+1 more)

### Community 120 - "test_ingest_idempotent.py"
Cohesion: 0.11
Nodes (27): source_id(), _backfill_company_source(), ingest_source(), _insert_offer(), Connection, Ingestion orchestrator: pull normalized records from a Source into the DB.  Idem, INSERT OR IGNORE one offer. Returns True if a new row was created., Run one source end to end. Commits once at the end for atomicity. (+19 more)

### Community 121 - "run_menubar"
Cohesion: 0.38
Nodes (13): _client(), Connection, Path, TestClient, Task 36 item 3: read the CV before downloading it.  Reading is the step that dec, Task 34 pinned this. Naming the download must not have widened it., Separate actions, same bytes, same guarded path., _ready_with_artifacts() (+5 more)

### Community 123 - "test_renderer_owned_fields.py"
Cohesion: 0.22
Nodes (9): build_cv_title(), Build the deterministic CV title used after all advisor providers., test_build_cv_title_uses_clean_role_and_contract_specific_suffix(), The guarantees that made four _validate_plan branches unreachable.  Task 39 item, The one input to resolve_header_location that comes from config., _offer_start falls back to « septembre 2026 », so there is always one., test_the_built_title_always_carries_a_start_date(), test_the_built_title_always_carries_its_contract_type() (+1 more)

### Community 124 - "ApplicationNotQueuedError"
Cohesion: 0.09
Nodes (34): LookupError, ApplicationGenerationError, ApplicationNotFoundError, ApplicationNotQueuedError, generation_single_flight(), GenerationInFlight, InteractiveAdvisorRequired, RuntimeError (+26 more)

### Community 125 - "parse_indeed"
Cohesion: 0.29
Nodes (7): clean_job_url(), parse_indeed(), Return a stable detail URL with email/tracking parameters removed., Extract jobs from an Indeed job-alert email., test_clean_job_url_removes_tracking_parameters(), test_parse_ignores_non_job_links(), test_parse_indeed_extracts_jk_ids()

### Community 126 - "build_advisor"
Cohesion: 0.22
Nodes (13): SimpleNamespace, build_advisor(), Raised when the selected tailoring provider is not configured., Resolve TAILORING_PROVIDER to a concrete mode, without building anything.      C, Select the configured provider without silently bypassing missing keys., resolve_provider(), TailoringConfigurationError, MonkeyPatch (+5 more)

### Community 128 - "_client"
Cohesion: 0.33
Nodes (11): _client(), Connection, Path, TestClient, The point of the whole item: the writer lock is held, and /progress still     an, Task 34's rule: the validator's own message, verbatim, not 'Error: 500'., It must answer while a generation holds the writer lock., test_a_generation_failure_is_reported_in_the_interface_voice() (+3 more)

### Community 129 - "ApplicantProfile"
Cohesion: 0.22
Nodes (7): ApplicantProfile, letter_plain_text(), open_manually(), Path, The generated letter as plain text, or '' when it was never generated., The manual_open route: open the offer, copy the letter, submit nothing.      A l, The non-secret contact values entered into an ATS form.

### Community 130 - "test_progress.py"
Cohesion: 0.20
Nodes (3): Task 36 item 6: live progress for the slow operations.  Generation, regeneration, The token system disables motion wholesale rather than per-animation., test_the_spinner_respects_reduced_motion()

### Community 131 - ".finish"
Cohesion: 0.22
Nodes (4): BaseException, Update a running operation. A key that is not running is ignored., Close an operation. The first outcome recorded wins.          A handled failure, Record a failure the caller handled rather than raised.          The dashboard c

### Community 132 - "observable_controls"
Cohesion: 0.10
Nodes (29): _Control, _controls_from_html(), _css_attribute_value(), FillAction, _first_matching_selector(), _Form, _FormParser, _forms_from_html() (+21 more)

### Community 133 - "test_registry.py"
Cohesion: 0.46
Nodes (7): available_sources(), Path, Source enablement via config/sources.yaml., _settings(), test_disabled_source_excluded(), test_no_config_all_enabled(), test_replace_keeps_dataclass_shape()

### Community 134 - "Request"
Cohesion: 0.29
Nodes (7): Request, _posted_body(), _posted_cold_send(), _posted_plan_hash(), Read the ``body`` field from a urlencoded POST without python-multipart.      Ru, Read the plan_hash the confirmation page put in the form., Read editable body and the named-mailbox confirmation checkbox.

### Community 135 - "_Advisor"
Cohesion: 0.53
Nodes (5): _Advisor, _application(), Connection, test_generation_failure_returns_application_to_queue(), test_generation_runs_quality_gates_before_pdfs_and_moves_to_ready()

### Community 136 - "SendBlocked"
Cohesion: 0.50
Nodes (4): ColdSendDisabled, A rail (suppression list or daily cap) refuses the send. Not a failure., Live cold sending is disabled by configuration., SendBlocked

## Knowledge Gaps
- **155 isolated node(s):** `profile`, `contacts`, `suppression_list`, `offers`, `offers` (+150 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `OpenAITailoringAdvisor` to `ApplicantProfile`, `_client`, `observable_controls`, `test_registry.py`, `Path`, `SendBlocked`, `mailer.py`, `test_routing.py`, `wttj.py`, `france_travail.py`, `_FakePage`, `test_email_alerts.py`, `test_labonnealternance.py`, `Settings`, `.from_mapping`, `test_cold_outreach.py`, `_FakePage`, `resolve_fact_id`, `pick_variant`, `launch_application_assist`, `apply_matching_profile_cmd`, `_TextParser`, `_FakeLocator`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `load_fact_bank()` connect `load_fact_bank` to `test_fact_id_consistency.py`, `review.py`, `email_alerts.py`, `vocabulary.py`, `run_dashboard`, `test_cv_completeness.py`, `OfferRecord`, `connect`, `test_designation_numbers.py`, `MissingCredentialError`, `AnthropicTailoringAdvisor`, `_AnchorParser`, `test_ingest_idempotent.py`, `test_tech_additions.py`, `test_provenance_tiers.py`, `test_letter_locked_fields.py`, `models.py`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Why does `TailoringError` connect `get_settings` to `dashboard.py`, `_Advisor`, `RefreshRunner`, `generate_application`, `_Toolchain`, `email_alerts.py`, `test_cv_completeness.py`, `OfferRecord`, `MissingCredentialError`, `AnthropicTailoringAdvisor`, `load_fact_bank`, `CompanyRecord`, `labonnealternance.py`, `ingest_source`, `test_letter_quality.py`, `models.py`, `test_designation_numbers.py`, `review.py`, `ingest_source`, `test_preview.py`, `vocabulary.py`, `_AnchorParser`, `test_profile_domain_anchor.py`, `build_advisor`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 62 inferred relationships involving `Settings` (e.g. with `ApplicantProfile` and `ApplyAdapter`) actually correct?**
  _`Settings` has 62 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `current_status()` (e.g. with `test_a_fatal_gate_still_aborts()` and `test_a_recoverable_gate_with_no_degradation_escalates_to_fatal()`) actually correct?**
  _`current_status()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `_payload()` (e.g. with `.advise()` and `_plan()`) actually correct?**
  _`_payload()` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `TailoringError` (e.g. with `_CompleteAdvisor` and `_IncompleteAdvisor`) actually correct?**
  _`TailoringError` has 17 INFERRED edges - model-reasoned connections that need verification._