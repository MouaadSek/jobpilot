# Graph Report - jobpilot  (2026-08-01)

## Corpus Check
- 146 files · ~177,860 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3149 nodes · 8331 edges · 119 communities (104 shown, 15 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 501 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `94f91624`
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
- record_form_fields
- Phase 02: Scraper sources (run after phase 01 is green)
- Phase 03: Apply integration (CV/letter generation bridge)
- Phase 04: Cold mail module
- Phase 05: Reply detection + tracker automation
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
- mappings_for
- parse_rejections
- run_menubar
- ApplicationNotQueuedError
- vocabulary.py
- observable_controls
- MailerError
- seeded_application

## God Nodes (most connected - your core abstractions)
1. `Settings` - 117 edges
2. `current_status()` - 94 edges
3. `_payload()` - 83 edges
4. `TailoringError` - 76 edges
5. `OfferRecord` - 68 edges
6. `FactBank` - 66 edges
7. `load_fact_bank()` - 65 edges
8. `get_settings()` - 63 edges
9. `create_app()` - 61 edges
10. `_Toolchain` - 55 edges

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

## Communities (119 total, 15 thin omitted)

### Community 0 - "test_downloads.py"
Cohesion: 0.05
Nodes (41): BaseException, Operation, ProgressRegistry, Any, datetime, Update a running operation. A key that is not running is ignored., Close an operation. The first outcome recorded wins.          A handled failure, Everything running, plus anything that finished very recently. (+33 more)

### Community 1 - "Request"
Cohesion: 0.08
Nodes (55): Resolve one archived artefact, with the same discipline as the live one.      De, _safe_archive_path(), _archives_for(), Generation, is_archive_stamp(), library_entries(), LibraryEntry, _mtime_iso() (+47 more)

### Community 2 - "_candidate_name"
Cohesion: 0.07
Nodes (88): SimpleNamespace, _client(), _events(), _no_advisor_client(), _offer_application(), Connection, MonkeyPatch, Path (+80 more)

### Community 3 - "_client"
Cohesion: 0.05
Nodes (63): FastAPI, LookupError, open_manually(), The manual_open route: open the offer, copy the letter, submit nothing.      A l, ApplicationGenerationError, ApplicationNotFoundError, ApplicationNotQueuedError, ApplyOutcome (+55 more)

### Community 4 - "create_app"
Cohesion: 0.07
Nodes (46): Logger, ingest_cmd(), Fetch offers from a source (or all sources) into the database., _env_bool(), get_settings(), _path(), Configuration and path resolution. Secrets come from .env only (never mocked)., get_logger() (+38 more)

### Community 5 - "dashboard.py"
Cohesion: 0.07
Nodes (71): Match, Pattern, _add_tech_additions(), _add_tech_keywords(), _contact_fields(), _contains(), _contains_any(), _cv_locked_fields() (+63 more)

### Community 6 - "run_dashboard"
Cohesion: 0.17
Nodes (18): bank(), _dropping_enabled(), _InventsForever, Connection, MonkeyPatch, Path, Task 37 item 3: degradation, shipped OFF.  If the advisor still cites an id that, The shipped default: nothing is dropped and the generation fails. (+10 more)

### Community 7 - "Path"
Cohesion: 0.11
Nodes (28): load_matching_profile(), Load the committed matching vocabulary, failing loudly rather than defaulting., Path, Task 35 item 1: the city parse fix (1a) and the committed matching profile (1b)., role_hit is an unanchored substring test worth a flat +0.15. As bare     tokens, Item 1c withdrawn. These are load-bearing: France Travail writes     'Courbevoie, The old list was already French but multi-word, and substring matching     needs, len(hard_skills) is keyword_score's denominator, so a duplicate silently     low (+20 more)

### Community 8 - "test_routing.py"
Cohesion: 0.06
Nodes (81): Cursor, Decision, RouteId, _applicant_reason(), _artifacts(), _ats_prefill(), _email(), _learned_form() (+73 more)

### Community 9 - "mailer.py"
Cohesion: 0.06
Nodes (93): Show the email that would be sent for a ready application, then confirm (y/N)., send_cmd(), Whether a named mailbox on a professional domain needs extra approval., requires_personal_confirmation(), _as_utc(), _build_message(), build_sender(), ColdEmailPreparation (+85 more)

### Community 10 - "validate_cv.py"
Cohesion: 0.06
Nodes (53): check_orphans(), find_regressions(), Path, Return orphan metrics that are new or materially worse than the template., format_date(), main(), build_letter_html(), detect_github() (+45 more)

### Community 11 - "get_settings"
Cohesion: 0.22
Nodes (16): _alert_source_clause(), Connection, Restrict to one alert source, or to all of them when none is named., Re-derive company / city / workplace / easy-apply for stored alert offers., reparse_alerts(), ReparseResult, Connection, The card line survived in companies.name; the city held only chrome. (+8 more)

### Community 12 - "connect"
Cohesion: 0.06
Nodes (42): _csv(), daemon_cmd(), dashboard_cmd(), init_profile_cmd(), invention_report_cmd(), _langs(), mark_sent_cmd(), Clear stored match_scores so the next `score` run re-evaluates those offers. (+34 more)

### Community 13 - "test_descriptions.py"
Cohesion: 0.08
Nodes (59): backfill_descriptions(), BackfillResult, clear_match_scores(), enrich_offer(), is_synthesized(), is_thin(), Connection, Synthesise matchable text for offers that arrive with no description.  Job-alert (+51 more)

### Community 14 - "test_generic_vocabulary.py"
Cohesion: 0.13
Nodes (17): _Card, _card_fields(), parse_card_line(), Split a trailing "(Sur site)" / "(Hybride)" / "(À distance)" off a location., The fields one alert card can carry, before they reach an OfferRecord., Parse LinkedIn's "Company · City (Workplace)" card line.      Returns None when, Best-effort split of "Title - Company - Location" style anchor text.      Alert, Derive the offer fields of one alert card, structurally.      Order of preferenc (+9 more)

### Community 15 - "apply_assist.py"
Cohesion: 0.36
Nodes (10): apply_matching_profile(), MatchingProfile, Write the vocabulary onto the profile singleton. Returns {field: (before, after), The scoring vocabulary, committed to git rather than typed once.      These thre, Connection, _seed_profile(), test_applying_is_idempotent(), test_applying_reports_what_changed() (+2 more)

### Community 16 - "test_skim.py"
Cohesion: 0.12
Nodes (46): available_sources(), _create_application(), ignore_offer(), promote_offer(), Connection, Row, Offers that passed the hard filter and scored below the queue threshold.      An, The offer row, if it is genuinely one this page may act on. (+38 more)

### Community 17 - "contacts.py"
Cohesion: 0.10
Nodes (38): _candidate_name(), ContactCandidate, discover_and_store(), DiscoverySource, draft_cold_email(), draft_linkedin_note(), _get_or_create_cold_application(), is_professional_address() (+30 more)

### Community 18 - "JobPilot — Codex Handoff (complete A-to-Z)"
Cohesion: 0.04
Nodes (45): 10. HARD REJECTIONS (offers the pipeline should auto-skip), 11. API REFERENCES, 12. DESIGN PRINCIPLES (non-negotiable), 13. ENV VARS (.env), 14. GITHUB PUSH (do this FIRST, before any Codex work), 15. CODEX TASK BREAKDOWN (suggested order), 16. BAIFALL DREAM STAGE REFERENCE, 17. SCRIPTS REFERENCE (+37 more)

### Community 19 - "RefreshRunner"
Cohesion: 0.12
Nodes (27): source_id(), _backfill_company_source(), ingest_source(), _insert_offer(), Connection, Ingestion orchestrator: pull normalized records from a Source into the DB.  Idem, INSERT OR IGNORE one offer. Returns True if a new row was created., Run one source end to end. Commits once at the end for atomicity. (+19 more)

### Community 20 - "_payload"
Cohesion: 0.10
Nodes (46): bank(), _bullets(), _offer(), _project(), The advisor selects; the renderer inserts the bank's wording unchanged., The pre-written variants from the skill asset, used as the asset intends., The contract has no field for prose, so a writing advisor fails loudly., Only the entry's own facts, so a skill id cannot become a bullet. (+38 more)

### Community 21 - "wttj.py"
Cohesion: 0.10
Nodes (41): _city(), _contact_email(), _contract(), _first(), map_hit(), _org(), _prose(), Any (+33 more)

### Community 22 - "SourcedBullet"
Cohesion: 0.10
Nodes (21): ConnectionFactory, Event, IngestResult, _default_score_pass(), _production_connection(), Any, Connection, RuntimeError (+13 more)

### Community 23 - "france_travail.py"
Cohesion: 0.09
Nodes (31): _delay(), Rate limiting + exponential backoff for every external call (constitution rule)., Call fn(); retry on transient HTTP errors with full-jitter exponential backoff., with_backoff(), _first_nonempty(), FranceTravailSource, _map_contact_email(), _map_contract() (+23 more)

### Community 24 - "test_provenance_tiers.py"
Cohesion: 0.08
Nodes (38): bank(), _in_bank(), _offer(), Three kinds of token, three different burdens of proof., Not even the widest scope can support it., The reader has to be able to search for it, or add it to the config., Task 26's handling survives as the digit-shaped corner of tier 2., Presence in the bank is necessary for tier 2, never sufficient. (+30 more)

### Community 25 - "launch_wttj_application"
Cohesion: 0.28
Nodes (9): discard_mapping(), Connection, Drop a mapping whose selector no longer matches. Logged, never guessed., Whether pressing submit is allowed on this domain. Default: no.      Prefill is, Flip the per-domain submit gate. Deliberately has no global counterpart., set_submit_enabled(), submit_enabled(), test_the_submit_gate_can_be_closed_again() (+1 more)

### Community 26 - "Dashboard"
Cohesion: 0.05
Nodes (36): Actualiser les offres (refresh from the page), Always up, without a terminal, Architecture (summary), ATS application assist (prefill only), Background scheduling, CI, Cold outreach sending (disabled by default), Commands (+28 more)

### Community 27 - "_FakePage"
Cohesion: 0.13
Nodes (16): ApplyAdapter, Common adapter interface for a best-effort ATS prefill., _FakeLauncher, _FakeLocator, _FakePage, Connection, _FakePage, Path (+8 more)

### Community 28 - "cli.py"
Cohesion: 0.12
Nodes (42): counts(), Any, Connection, datetime, The tracker: every application, one table, read-only.  Deliberately not a Google, Every offer application, optionally narrowed to one status., Statuses that actually occur, so the filter offers no dead options., Export exactly the visible rows, in the visible column order. (+34 more)

### Community 29 - "test_desktop_shell.py"
Cohesion: 0.08
Nodes (32): CaptureFixture, dashboard_already_running(), Whether something is already listening on the dashboard's port.      A connect p, The menu bar text. Short: it competes with every other item up there., title(), _bound_port(), _fake_macos(), _module_level_imports() (+24 more)

### Community 30 - "generate_application"
Cohesion: 0.08
Nodes (25): CompletedProcess, date, _check_orphans(), DocumentToolchain, _french_date(), generate_application(), _load_offer(), _persist_variant() (+17 more)

### Community 31 - "test_contacts.py"
Cohesion: 0.10
Nodes (27): ModuleType, JobPilot: personal job application pipeline for the French IT/cybersecurity mark, _application(), _ConnectionProxy, Connection, Exception, Path, CLI coverage for offer document generation and cold-application approval. (+19 more)

### Community 32 - "test_email_alerts.py"
Cohesion: 0.09
Nodes (44): Message, GmailIMAP, html_of(), LinkedInAlertSource, Minimal read-only Gmail IMAP client., Fetch recent mail sent from `domains` (or any of their subdomains).          The, Return the best HTML (or plain-text) body of an email message., Return the lowercased domain of the address in a `From` header.      Parses the (+36 more)

### Community 33 - "test_labonnealternance.py"
Cohesion: 0.06
Nodes (74): get_or_create_company(), CompanyRecord, _city(), _company_name(), _contract_type(), _domain(), _first(), map_company() (+66 more)

### Community 34 - "_Toolchain"
Cohesion: 0.06
Nodes (63): ExperienceFact, FactClaim, One atomic statement that generated content may cite., CvProfile, Renderer-owned candidate facts injected into every generated CV., The location printed in the CV header when the offer yields none., AmbiguousFactIdError, build_advisor() (+55 more)

### Community 35 - "email_alerts.py"
Cohesion: 0.05
Nodes (59): _advise_and_tailor(), _advisor_fact_context(), _advisor_prompt(), _correction_block(), _generated_bullets(), _interactive_structured_payload(), _json_object(), _justification() (+51 more)

### Community 36 - "test_alert_card_fields.py"
Cohesion: 0.28
Nodes (9): is_noise(), True when `text` is card chrome that must never be stored as a field., Strip UI markers from one card chunk.      Returns ``(usable_text_or_None, easy_, scrub_chunk(), No literal list can enumerate these; N varies freely., test_connection_counts_are_matched_by_pattern_not_literal(), test_known_noise_is_recognised(), test_plausible_place_names_are_not_treated_as_noise() (+1 more)

### Community 37 - "Settings"
Cohesion: 0.08
Nodes (29): HTTPStatusError, MissingCredentialError, RuntimeError, Remove configured secrets from exception text before display/logging., Raised when a required secret is absent. We ask; we never silently mock., Settings, RateLimiter, Minimum-delay-per-domain limiter. Blocks until the next call is allowed. (+21 more)

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
Cohesion: 0.09
Nodes (26): _advise(), _BadSourceAdvisor, bank(), _offer(), Any, LogCaptureFixture, Citation ids are matched tolerantly; what may be claimed is unchanged., The reported failure: 'unknown skill fact id: azure.sentinel'. (+18 more)

### Community 42 - "test_dashboard_facts_scheduler.py"
Cohesion: 0.29
Nodes (16): _client(), fixture_bank(), Connection, MonkeyPatch, Path, TestClient, Read-only fact bank page and honest scheduler reporting on the queue page., test_daemon_state_follows_the_recorded_heartbeat_age() (+8 more)

### Community 43 - ".from_mapping"
Cohesion: 0.11
Nodes (30): pick_variant(), Pick the best of 21 variants from missions, then apply contract rules.      Sinc, Validate the one JSON contract shared by every advisor provider., test_duplicate_tool_across_categories_is_rejected(), unsupported number 27001' was rejecting real, bank-backed vocabulary., test_the_observed_failure_no_longer_fails_a_generation(), _experience_content(), _gemini_shaped_payload() (+22 more)

### Community 44 - "test_cold_outreach.py"
Cohesion: 0.08
Nodes (32): OfferRecord, One normalized offer, ready to insert into the offers table., Coerce enum-constrained fields to legal values (schema CHECK safety)., ATSSource, infer_contract(), map_greenhouse(), map_lever(), map_smartrecruiters() (+24 more)

### Community 45 - "_FakePage"
Cohesion: 0.15
Nodes (22): _events(), _FakeLauncher, _FakeLocator, _FakePage, Connection, _FakePage, Path, Row (+14 more)

### Community 46 - "MissingCredentialError"
Cohesion: 0.15
Nodes (19): AnthropicTailoringAdvisor, Claude Messages API adviser used when ``ANTHROPIC_API_KEY`` is set., _Client, _offer(), _plan_payload(), Any, Exception, MonkeyPatch (+11 more)

### Community 47 - "ats.py"
Cohesion: 0.15
Nodes (23): download_filename(), Download names an employer folder can still be read a week later.  ``output/appl, Reduce free text to ``[A-Za-z0-9-_]``, or to "" if nothing survives.      Accent, Build ``<Company>_<Type>_<Nom>.<ext>`` for one artefact.      Falls back to the, slugify(), _client(), Connection, Path (+15 more)

### Community 48 - "AnthropicTailoringAdvisor"
Cohesion: 0.25
Nodes (8): add_contact_cmd(), contacts_cmd(), draft_cold_cmd(), Resolve a company by numeric id or name; create by name if absent., Manually add a hiring contact for a company (default discovery path)., List stored contacts for a company, or the sourced outreach targets.      A targ, Draft a LinkedIn note + cold email and queue them for review (no send)., _resolve_company()

### Community 49 - "OpenAITailoringAdvisor"
Cohesion: 0.38
Nodes (7): apply_matching_profile_cmd(), Connection, _queue_snapshot(), Apply config/matching_profile.yaml and report what it changed.      Re-scoring i, Count what currently clears the bar, for an honest before/after., Re-evaluate every offer against the new vocabulary.      ``jobpilot score`` only, _rescore_all()

### Community 50 - "resolve_fact_id"
Cohesion: 0.25
Nodes (10): derive_fields(), _Derived, Re-derive alert card fields (company / city / workplace / easy-apply) in place., Re-derive one offer's card fields from the text that was stored for it.      Pur, is_title_echo(), True when `chunk` restates `title` rather than naming a company or place., The length guard must not sacrifice a genuine place name., test_a_real_city_that_merely_opens_the_title_is_kept() (+2 more)

### Community 51 - "test_tech_additions.py"
Cohesion: 0.15
Nodes (26): bank(), _offer(), LogCaptureFixture, Zone 3 may add a keyword, but only one he has and the offer asked for., Reorder-only remains the default and the common case., Genuinely his, but padding: the offer did not ask for it., Presence in the bank is necessary, never sufficient., Derived from the file, not a magic number. (+18 more)

### Community 52 - "load_fact_bank"
Cohesion: 0.10
Nodes (37): facts_cmd(), Print the provenance fact bank grouped for human review., _boolean(), build_cv_title(), CertificationFact, _claim_list(), EducationFact, _entry_claim() (+29 more)

### Community 53 - "CompanyRecord"
Cohesion: 0.40
Nodes (5): drop_unknown_citation(), Remove one unusable citation, or refuse when removing it would weaken the CV., The completeness floor is a hard failure, not a preference., test_a_bullet_can_be_dropped_while_the_entry_stays_above_its_floor(), test_the_last_bullet_the_floor_requires_is_never_dropped()

### Community 54 - "labonnealternance.py"
Cohesion: 0.50
Nodes (4): menubar_cmd(), Show ready/queued counts in the macOS menu bar (optional extra)., Run the menu bar item until quit. Blocks; opens the dashboard on click., run_menubar()

### Community 55 - "ingest_source"
Cohesion: 0.13
Nodes (18): ApplicantProfile, Whether a stored selector still finds a control on the current page., The non-secret contact values entered into an ATS form., selector_matches_html(), build_prefill(), FormLearningError, FormMapping, PrefillOutcome (+10 more)

### Community 56 - "pick_variant"
Cohesion: 0.05
Nodes (44): _BaseAdapter, _Control, _ControlParser, _controls_from_html(), _css_attribute_value(), FillAction, _first_matching_selector(), _Form (+36 more)

### Community 57 - "test_fact_id_resolution.py"
Cohesion: 0.05
Nodes (71): invention_report(), How often the advisor cites an id that does not exist, and whether it recovers., _Invents, Connection, MonkeyPatch, Path, Task 37 item 4: count invention, so the other three items are not guesswork.  Pr, Item 3 degrades the CV; that is a different outcome from getting it right. (+63 more)

### Community 58 - "test_letter_locked_fields.py"
Cohesion: 0.18
Nodes (19): bank(), _letter(), _offer(), A letter is prose about a career; a CV is slots the renderer fills., Naming a real-sounding employer he never had is a fabrication, not prose., The renderer injects the address block; the body repeating it is a bug., Otherwise the test above would prove nothing about scope., The bank's own text names nothing it should not; selection is the check. (+11 more)

### Community 59 - "launch_application_assist"
Cohesion: 0.08
Nodes (29): adapter_for_url(), _application_for_assist(), _application_for_wttj(), ApplyAssistError, AssistResult, BrowserLauncher, _ConfirmationBaseline, _fallback() (+21 more)

### Community 60 - "test_letter_quality.py"
Cohesion: 0.24
Nodes (16): _default_letter(), french_de_elision(), Return « de <noun> » or « d'<noun> », applying French elision.      Elides befor, _validate_letter_body(), _letter(), _offer(), Letter quality: French elision and the 'Entreprise' placeholder rejection., test_default_letter_elides_poste_before_vowel() (+8 more)

### Community 62 - "models.py"
Cohesion: 0.07
Nodes (39): apply_cmd(), backfill_descriptions_cmd(), init_db_cmd(), queue_cmd(), Synthesise descriptions for stored offers whose text is too thin to score., Re-derive company / city / workplace / easy-apply for stored alert offers., List queued applications, highest final_score first., Approve an application and generate its tailored application documents. (+31 more)

### Community 63 - "reparse_alerts"
Cohesion: 0.11
Nodes (14): ABC, Source interface. Every API, scraper, or mailer sits behind this so it is plugga, Abstract ingestion source.      Implementations must be side-effect free with re, Yield normalized offers. Must apply rate limiting + backoff internally., Yield companies likely to hire (optional; default: none)., Source, _AlertAnchor, _AnchorParser (+6 more)

### Community 64 - "test_designation_numbers.py"
Cohesion: 0.12
Nodes (30): SentenceTransformer, _as_list(), build_profile_text(), _col(), ensure_profile_embedding(), get_embed_fn(), _model(), Connection (+22 more)

### Community 65 - "test_fact_id_consistency.py"
Cohesion: 0.20
Nodes (15): bank(), _bank_payload(), Path, Task 35 item 2: a fact bank whose claim ids do not extend their entry is invalid, The real bank must satisfy the rule the loader now enforces., This is the exact shape the Baïfall entry had., Projects have the same shape as experience, so they get the same rule., `experience.baifallX` starts with the entry id as a STRING but is a     differen (+7 more)

### Community 68 - "_AnchorParser"
Cohesion: 0.06
Nodes (56): CatalogueEntry, default_catalogue(), load_variant_catalogue(), _parse_criteria(), _parse_shortcuts(), Path, The CV catalogue offered to the advisor when it selects a variant.  The selectio, Read the two-column selection table, skipping its header and separator. (+48 more)

### Community 69 - "test_preview.py"
Cohesion: 0.14
Nodes (20): FormField, infer_profile_field(), One control's shape. Deliberately has nowhere to put a typed value., Everything naming this field, with separators folded to spaces.          Real fo, Name the reason this field may never be mapped, or None if it may.      Refused:, Which profile field this control wants, or None to leave it to the human., Every refusal category present in a form, for reporting to the human., refusal_category() (+12 more)

### Community 70 - "vocabulary.py"
Cohesion: 0.18
Nodes (19): application_detail(), applications_by_status(), event_history(), outreach_drafts(), Any, Connection, queued_applications(), Read-only queries shared by review surfaces. (+11 more)

### Community 71 - "UnknownFactIdError"
Cohesion: 0.15
Nodes (24): parse_linkedin(), Extract jobs from a LinkedIn job-alert email., _card_html(), LogCaptureFixture, Structural parsing of job-alert cards (Task 20).  Every fixture here is shaped a, Whatever position the chrome occupies, it must not be stored., None is strictly better: the hard filter reads it as "do not reject"., Observed verbatim: "Levallois-Perret (Sur site) Candidature simplifiée". (+16 more)

### Community 72 - "Baifall Dream Stage - Reference Document (v3)"
Cohesion: 0.17
Nodes (11): Baifall Dream Stage - Reference Document (v3), Bloc HTML de reference (3 bullets), Bullet 1 (commun, accompli) - 167 car., rendu sur 2 lignes, Bullet 2 (commun, nominal, perimetre complet) - 127 car., 1 ligne, Bullet 3 : declinaisons par variante, Context, Principe v3 : perimetre nominal complet, Regle pour la date (+3 more)

### Community 73 - "test_facts.py"
Cohesion: 0.17
Nodes (21): mappings_for(), put_mapping(), Write one mapping. Rejects a profile_field outside the closed enum., Connection, LogCaptureFixture, Task 34.D: form learning — what may be recorded, and what may never be.  This ta, Nothing is written for it, so the next pass re-detects and re-refuses —     whic, Falling back to manual_open is correct behaviour, not a bug. (+13 more)

### Community 74 - "test_progress.py"
Cohesion: 0.50
Nodes (5): load_cv_profile(), Load the committed CV profile, failing loudly rather than defaulting., Renderer-owned CV header location; the advisor has no say in it.      Prefers th, resolve_header_location(), test_header_location_prefers_the_offer_region_then_the_profile()

### Community 75 - "scheduler_status"
Cohesion: 0.33
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
Cohesion: 0.24
Nodes (15): _approve(), Connection, LogCaptureFixture, Path, The asset file calls these false positives outside a full render., The reliable control, per the asset file, so it never becomes advisory., test_a_clean_generation_records_no_orphan_warning(), test_an_orphan_in_the_generated_profile_still_fails() (+7 more)

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

### Community 88 - "record_form_fields"
Cohesion: 0.20
Nodes (21): _offer(), _openai_response(), _plan_payload(), Any, Connection, MonkeyPatch, Path, _queued_application() (+13 more)

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

### Community 110 - "test_designation_numbers.py"
Cohesion: 0.17
Nodes (16): bank(), _in_bank(), LogCaptureFixture, A standard's digits name a thing; a metric's digits measure one., The anti-fabrication guarantee is not weakened by designation handling., Only the designation's own span is exempt from the number rule., Judge as the letter is judged: no entry, so the whole bank answers., Looking like a standard is not evidence of holding one. (+8 more)

### Community 111 - "_AnchorParser"
Cohesion: 0.05
Nodes (74): Container, FactBank, _bank_parts(), _designation_spans(), _fact_id_key(), _guessed_section(), nearest_entry_claim_ids(), _normalized_number() (+66 more)

### Community 112 - "test_ingest_idempotent.py"
Cohesion: 0.22
Nodes (16): bank(), _check(), LogCaptureFixture, Path, The vocabulary tier is config, and its misses are countable., Tier 1 must not be reachable through tier 3, so the file may not try., The whole point: a category word is a config edit, not a release., test_a_malformed_vocabulary_is_refused_loudly() (+8 more)

### Community 113 - "apply_matching_profile_cmd"
Cohesion: 0.25
Nodes (8): _plan(), The spec said "at least one remaining bullet" is enough. It is not: the     Task, Exactly three projects are required, each with its single fact., skill_order has no minimum, so losing one weakens nothing structural., test_a_project_fact_is_never_dropped(), test_a_recent_employer_may_not_fall_to_one_bullet(), test_a_skill_can_be_dropped(), test_an_unrecognised_citation_is_never_dropped()

### Community 114 - "vocabulary_misses"
Cohesion: 0.25
Nodes (17): Return capability-tier tokens that have tripped generations, by frequency., vocabulary_misses(), The one wording for a refused token; every caller goes through here.      Naming, rejection_message(), _failure(), Connection, MonkeyPatch, No vocabulary entry may ever excuse a fabricated number or employer. (+9 more)

### Community 116 - "mappings_for"
Cohesion: 0.50
Nodes (5): mapping_is_complete(), Whether ``domain`` has enough of a mapping to be worth calling a route., has_form_mapping(), Whether a *complete* learned mapping exists for ``domain``.      Complete means, test_a_learned_domain_becomes_routable()

### Community 118 - "parse_rejections"
Cohesion: 0.14
Nodes (14): parse_rejections(), Recover the refused tokens from stored validator messages.      The events table, How much a token has to be backed up before it may be written., One token a validator refused, why, and what it was judged against., TokenRejection, TokenTier, StrEnum, Events outlive the code that wrote them, so the wording is the contract. (+6 more)

### Community 121 - "run_menubar"
Cohesion: 0.33
Nodes (6): MenubarUnavailable, Any, RuntimeError, Raised when the menu bar item cannot run on this machine., Import rumps or explain, in French, exactly how to get it., _require_rumps()

### Community 124 - "ApplicationNotQueuedError"
Cohesion: 0.42
Nodes (9): _app(), Connection, State machine transition tests: legality + event auditing., Constitution: no send/submit without a prior human_approved event., test_full_happy_path(), test_human_approved_event_recorded(), test_illegal_transition_raises_and_no_change(), test_legal_transition_updates_and_logs() (+1 more)

### Community 125 - "vocabulary.py"
Cohesion: 0.22
Nodes (9): GenericVocabularyError, load_generic_vocabulary(), Path, ValueError, Load the terms that assert nothing about the candidate.      Kept in config rath, Raised when the committed generic vocabulary is malformed., Silently allowing nothing would look like a strict validator, not a bug., test_a_missing_vocabulary_file_is_an_error_not_an_empty_set() (+1 more)

### Community 128 - "observable_controls"
Cohesion: 0.18
Nodes (12): observable_controls(), Every fillable control's *shape*, for form learning. Never its contents.      ``, fields_from_html(), Read a page's controls as shapes. Values are stripped before we see them., Record mappings for one manually submitted form. Values are never stored.      C, record_form_fields(), Scan every column of the table for the sentinel values used above., One enforcement point: values are stripped before this module sees them. (+4 more)

### Community 129 - "MailerError"
Cohesion: 0.29
Nodes (7): Request, _posted_body(), _posted_cold_send(), _posted_plan_hash(), Read the ``body`` field from a urlencoded POST without python-multipart.      Ru, Read the plan_hash the confirmation page put in the form., Read editable body and the named-mailbox confirmation checkbox.

## Knowledge Gaps
- **154 isolated node(s):** `profile`, `contacts`, `suppression_list`, `offers`, `offers` (+149 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `Settings` to `test_email_alerts.py`, `test_labonnealternance.py`, `_client`, `create_app`, `test_routing.py`, `launch_application_assist`, `mailer.py`, `test_cold_outreach.py`, `_FakePage`, `test_generic_vocabulary.py`, `france_travail.py`, `wttj.py`, `ingest_source`, `pick_variant`, `_FakePage`, `reparse_alerts`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Why does `current_status()` connect `mailer.py` to `_candidate_name`, `_client`, `_AnchorParser`, `dashboard.py`, `run_dashboard`, `test_cv_completeness.py`, `test_routing.py`, `connect`, `_FakePage`, `test_skim.py`, `test_valid_sourced_advice_completes_the_shared_generation_path`, `record_form_fields`, `test_fact_id_resolution.py`, `_FakePage`, `ApplicationNotQueuedError`, `generate_application`, `test_contacts.py`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Why does `get_logger()` connect `create_app` to `Request`, `_client`, `dashboard.py`, `test_routing.py`, `mailer.py`, `connect`, `test_descriptions.py`, `contacts.py`, `RefreshRunner`, `wttj.py`, `france_travail.py`, `cli.py`, `Settings`, `test_cold_outreach.py`, `resolve_fact_id`, `ingest_source`, `pick_variant`, `models.py`, `test_designation_numbers.py`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Are the 62 inferred relationships involving `Settings` (e.g. with `ApplicantProfile` and `ApplyAdapter`) actually correct?**
  _`Settings` has 62 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `_payload()` (e.g. with `.advise()` and `_plan()`) actually correct?**
  _`_payload()` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `TailoringError` (e.g. with `ExperienceFact` and `FactBank`) actually correct?**
  _`TailoringError` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `OfferRecord` (e.g. with `BackfillResult` and `RescoreResult`) actually correct?**
  _`OfferRecord` has 23 INFERRED edges - model-reasoned connections that need verification._