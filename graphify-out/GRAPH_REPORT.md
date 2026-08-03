# Graph Report - jobpilot  (2026-08-04)

## Corpus Check
- 154 files · ~187,296 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3336 nodes · 8891 edges · 119 communities (104 shown, 15 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 563 edges (avg confidence: 0.52)
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
- test_ingest_idempotent.py
- run_menubar
- _FakeLocator
- test_renderer_owned_fields.py
- ApplicationNotQueuedError
- parse_indeed
- 008_applications_generation_warnings.sql
- observable_controls

## God Nodes (most connected - your core abstractions)
1. `Settings` - 117 edges
2. `current_status()` - 98 edges
3. `TailoringError` - 89 edges
4. `_payload()` - 89 edges
5. `load_fact_bank()` - 75 edges
6. `FactBank` - 72 edges
7. `OfferRecord` - 68 edges
8. `_Toolchain` - 67 edges
9. `get_settings()` - 64 edges
10. `create_app()` - 62 edges

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
Cohesion: 0.18
Nodes (15): _application_for_assist(), _application_for_wttj(), ApplyAssistError, AssistResult, _fallback(), launch_application_assist(), Connection, Row (+7 more)

### Community 4 - "create_app"
Cohesion: 0.04
Nodes (75): add_contact_cmd(), apply_cmd(), backfill_descriptions_cmd(), contacts_cmd(), daemon_cmd(), draft_cold_cmd(), init_db_cmd(), invention_report_cmd() (+67 more)

### Community 5 - "dashboard.py"
Cohesion: 0.07
Nodes (58): Match, Pattern, FactBank, _add_tech_additions(), _add_tech_keywords(), _contact_fields(), _cv_locked_fields(), _employer_bullet_floor() (+50 more)

### Community 6 - "run_dashboard"
Cohesion: 0.12
Nodes (30): drop_unknown_citation(), Remove one unusable citation, or refuse when removing it would weaken the CV., _dropping_enabled(), _InventsForever, _plan(), Connection, MonkeyPatch, Path (+22 more)

### Community 7 - "Path"
Cohesion: 0.07
Nodes (40): Logger, copy_text(), Put text on the system clipboard, or say plainly that it could not.  The manual_, Copy ``text``; return whether it actually landed on the clipboard., get_logger(), Central logging setup. Library code logs here; it never uses print()., Idempotent: attaches a rotating file handler + console handler once., setup_logging() (+32 more)

### Community 8 - "test_routing.py"
Cohesion: 0.11
Nodes (55): Cursor, _artifacts(), Path, Resolve the one route this application would go out by. Writes nothing., resolve_route(), _client(), Connection, MonkeyPatch (+47 more)

### Community 9 - "mailer.py"
Cohesion: 0.09
Nodes (44): is_professional_address(), True only for well-formed addresses NOT on a personal free-provider domain., Whether a named mailbox on a professional domain needs extra approval., requires_personal_confirmation(), _as_utc(), _build_message(), build_sender(), ColdEmailPreparation (+36 more)

### Community 10 - "validate_cv.py"
Cohesion: 0.06
Nodes (53): check_orphans(), find_regressions(), Path, Return orphan metrics that are new or materially worse than the template., format_date(), main(), build_letter_html(), detect_github() (+45 more)

### Community 11 - "get_settings"
Cohesion: 0.12
Nodes (27): _advise_and_tailor(), _advisor_fact_context(), _advisor_prompt(), _correction_block(), _interactive_structured_payload(), _is_validator_rejection(), _json_object(), _offer_start() (+19 more)

### Community 12 - "connect"
Cohesion: 0.14
Nodes (8): CompletedProcess, Raised when a citation matches no fact id, even after normalisation.      ``sect, UnknownFactIdError, _BadSourceAdvisor, Cites an unresolvable id in a letter paragraph, where no section is implied., A rejection that buries the answer in a wall of ids is no more useful     than o, test_a_long_section_is_capped_and_says_so(), test_a_short_section_is_not_annotated_as_truncated()

### Community 13 - "test_descriptions.py"
Cohesion: 0.11
Nodes (48): backfill_descriptions(), clear_match_scores(), is_synthesized(), Connection, Return an SQL fragment + params restricting a query to one source., Regenerate synthesised descriptions for stored offers whose text is thin.      I, Drop match_scores rows so the next `score` pass re-evaluates those offers., True when `description` was produced by this module. (+40 more)

### Community 14 - "test_generic_vocabulary.py"
Cohesion: 0.12
Nodes (22): LookupError, ApplicationGenerationError, ApplicationNotFoundError, ApplicationNotQueuedError, ApplyOutcome, approve_application(), archive_artifacts(), GenerationInFlight (+14 more)

### Community 15 - "apply_assist.py"
Cohesion: 0.21
Nodes (22): mark_application_sent(), Combined application + cold-mail sends recorded for today (UTC)., Send the application by email, then transition ready -> applied.      Returns th, Manual fallback: record an externally-submitted application as sent., send_application_email(), sends_today(), _utc_now(), _events() (+14 more)

### Community 16 - "test_skim.py"
Cohesion: 0.10
Nodes (52): available_sources(), _create_application(), ignore_offer(), promote_offer(), Connection, Row, ValueError, The skim list: offers that passed the hard filter but scored below threshold.  T (+44 more)

### Community 17 - "contacts.py"
Cohesion: 0.11
Nodes (34): _candidate_name(), ContactCandidate, discover_and_store(), DiscoverySource, draft_cold_email(), draft_linkedin_note(), _get_or_create_cold_application(), is_suppressed() (+26 more)

### Community 18 - "JobPilot — Codex Handoff (complete A-to-Z)"
Cohesion: 0.04
Nodes (45): 10. HARD REJECTIONS (offers the pipeline should auto-skip), 11. API REFERENCES, 12. DESIGN PRINCIPLES (non-negotiable), 13. ENV VARS (.env), 14. GITHUB PUSH (do this FIRST, before any Codex work), 15. CODEX TASK BREAKDOWN (suggested order), 16. BAIFALL DREAM STAGE REFERENCE, 17. SCRIPTS REFERENCE (+37 more)

### Community 19 - "RefreshRunner"
Cohesion: 0.20
Nodes (21): _offer(), _openai_response(), _plan_payload(), Any, Connection, MonkeyPatch, Path, _queued_application() (+13 more)

### Community 20 - "_payload"
Cohesion: 0.11
Nodes (43): _bullets(), _project(), The advisor selects; the renderer inserts the bank's wording unchanged., The pre-written variants from the skill asset, used as the asset intends., The contract has no field for prose, so a writing advisor fails loudly., Only the entry's own facts, so a skill id cannot become a bullet., Task 25's tolerance survives: ids are normalised before they are judged., The phrase is short, but it is still generated, so the tiers still read it. (+35 more)

### Community 21 - "wttj.py"
Cohesion: 0.10
Nodes (41): _city(), _contact_email(), _contract(), _first(), map_hit(), _org(), _prose(), Any (+33 more)

### Community 22 - "SourcedBullet"
Cohesion: 0.11
Nodes (19): ConnectionFactory, Event, _default_model_loader(), _default_score_pass(), _production_connection(), Any, Connection, Load the embedding model. Lazy exactly as the CLI's `score` path is. (+11 more)

### Community 23 - "france_travail.py"
Cohesion: 0.06
Nodes (52): _delay(), Rate limiting + exponential backoff for every external call (constitution rule)., Call fn(); retry on transient HTTP errors with full-jitter exponential backoff., with_backoff(), ATSSource, infer_contract(), load_targets(), map_greenhouse() (+44 more)

### Community 24 - "test_provenance_tiers.py"
Cohesion: 0.08
Nodes (38): bank(), _in_bank(), _offer(), Three kinds of token, three different burdens of proof., Not even the widest scope can support it., The reader has to be able to search for it, or add it to the config., Task 26's handling survives as the digit-shaped corner of tier 2., Presence in the bank is necessary for tier 2, never sufficient. (+30 more)

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
Cohesion: 0.10
Nodes (23): date, _check_orphans(), _contains_generated_orphan(), DocumentToolchain, _french_date(), generate_application(), _load_offer(), _persist_variant() (+15 more)

### Community 31 - "test_contacts.py"
Cohesion: 0.10
Nodes (27): ModuleType, JobPilot: personal job application pipeline for the French IT/cybersecurity mark, _application(), _ConnectionProxy, Connection, Exception, Path, CLI coverage for offer document generation and cold-application approval. (+19 more)

### Community 32 - "test_email_alerts.py"
Cohesion: 0.09
Nodes (43): Message, GmailIMAP, html_of(), LinkedInAlertSource, Minimal read-only Gmail IMAP client., Fetch recent mail sent from `domains` (or any of their subdomains).          The, Return the best HTML (or plain-text) body of an email message., Return the lowercased domain of the address in a `From` header.      Parses the (+35 more)

### Community 33 - "test_labonnealternance.py"
Cohesion: 0.08
Nodes (55): list_outreach_targets(), Companies an ingestion source flagged as likely to hire an alternant.      These, get_or_create_company(), CompanyRecord, _fixture(), _no_real_sleeping(), _NoWait, Connection (+47 more)

### Community 34 - "_Toolchain"
Cohesion: 0.06
Nodes (73): ExperienceFact, FactClaim, One atomic statement that generated content may cite., GenerationWarning, One thing the reviewer is being asked to check by eye., CvProfile, Renderer-owned candidate facts injected into every generated CV., The location printed in the CV header when the offer yields none. (+65 more)

### Community 35 - "email_alerts.py"
Cohesion: 0.08
Nodes (28): Every id the advisor may cite, flattened out of the context it was given.      D, valid_fact_ids(), facts(), _nested_ids(), Task 37 item 1: tell the advisor the set of ids is closed.  `skill.rules.sigma`, Task 37 must not have quietly added Sigma to make the failure go away., Defensive: a template with no projects must not raise here., The exact mechanism that produced skill.rules.sigma. (+20 more)

### Community 36 - "test_alert_card_fields.py"
Cohesion: 0.10
Nodes (32): as_dicts(), clear_warnings(), _decode(), Any, Connection, What a generation had to degrade, recorded where the reviewer will see it.  Task, Gate names per application, for the library and tracker markers.      One query, Template-facing shape. (+24 more)

### Community 37 - "Settings"
Cohesion: 0.11
Nodes (16): HTTPStatusError, MissingCredentialError, RuntimeError, Raised when a required secret is absent. We ask; we never silently mock., RateLimiter, Minimum-delay-per-domain limiter. Blocks until the next call is allowed., LaBonneAlternanceAuthError, LaBonneAlternanceError (+8 more)

### Community 38 - "Job Application Pipeline"
Cohesion: 0.06
Nodes (31): Alternance vs Stage, Edge Cases & Principles, Encoding note, Execution Flow, Flag once, then execute:, Generate with the bundled script:, GitHub Exception, Hard rejections (no output): (+23 more)

### Community 39 - "matcher.py"
Cohesion: 0.06
Nodes (66): bonus_score(), cosine(), hard_filter(), keyword_score(), norm(), pick_variant(), Profile, Connection (+58 more)

### Community 40 - "test_cv_completeness.py"
Cohesion: 0.11
Nodes (27): _category_skills(), _CompleteAdvisor, _IncompleteAdvisor, Any, Connection, Path, _Toolchain, _queued_application() (+19 more)

### Community 41 - "OfferRecord"
Cohesion: 0.09
Nodes (27): _advise(), bank(), _offer(), Any, LogCaptureFixture, Citation ids are matched tolerantly; what may be claimed is unchanged., The reported failure: 'unknown skill fact id: azure.sentinel'., skill_order can only mean a skill, so its own prefix settles the match. (+19 more)

### Community 42 - "test_dashboard_facts_scheduler.py"
Cohesion: 0.25
Nodes (18): daemon_status(), Report daemon liveness from the heartbeat file, or admit it is unknown., _client(), fixture_bank(), Connection, MonkeyPatch, Path, TestClient (+10 more)

### Community 43 - ".from_mapping"
Cohesion: 0.09
Nodes (23): BackfillResult, enrich_offer(), is_thin(), Synthesise matchable text for offers that arrive with no description.  Job-alert, Replace a thin description in place; richer descriptions are left alone.      Ca, True when a description is too short to be worth embedding on its own., content_hash(), OfferRecord (+15 more)

### Community 44 - "test_cold_outreach.py"
Cohesion: 0.16
Nodes (17): DaemonStatus, heartbeat_path(), Any, Connection, datetime, Path, Background daemon: run ingest + score on a fixed interval (default 3h).  The dae, Last recorded run per enabled source. ``last_run_at`` is all the DB keeps. (+9 more)

### Community 45 - "_FakePage"
Cohesion: 0.24
Nodes (20): _events(), _FakeLauncher, _FakePage, Connection, Path, Row, WTTJ inline application stays human-approved and dry-run by default., _ready_wttj_application() (+12 more)

### Community 46 - "MissingCredentialError"
Cohesion: 0.16
Nodes (17): The tier this failure carries HERE.      An unclassified error is fatal. That de, tier_for(), bank(), _raised(), Task 39 item 3: one funnel, three outcomes.  152 raise sites all meant "abort",, validate_provenance delegates; the capability tier is what actually fired., The one gate stopping a CV experience entry at the offer's employer., The safety property of the whole task: forgetting to classify a gate     keeps t (+9 more)

### Community 47 - "ats.py"
Cohesion: 0.15
Nodes (23): download_filename(), Download names an employer folder can still be read a week later.  ``output/appl, Reduce free text to ``[A-Za-z0-9-_]``, or to "" if nothing survives.      Accent, Build ``<Company>_<Type>_<Nom>.<ext>`` for one artefact.      Falls back to the, slugify(), _client(), Connection, Path (+15 more)

### Community 48 - "AnthropicTailoringAdvisor"
Cohesion: 0.10
Nodes (25): _canonicalize_prose(), _justification(), Any, Normalize model punctuation that the document contract forbids.      This is a l, Validate the one JSON contract shared by every advisor provider., _experience_content(), _gemini_shaped_payload(), _offer() (+17 more)

### Community 49 - "OpenAITailoringAdvisor"
Cohesion: 0.10
Nodes (32): Decision, RouteId, adapter_for_url(), Return the owning ATS adapter, if the saved offer URL is recognized., Remove configured secrets from exception text before display/logging., Settings, _applicant_reason(), _ats_prefill() (+24 more)

### Community 50 - "resolve_fact_id"
Cohesion: 0.17
Nodes (22): _city(), _company_name(), _contract_type(), _domain(), _first(), map_company(), map_offer(), Any (+14 more)

### Community 51 - "test_tech_additions.py"
Cohesion: 0.15
Nodes (26): bank(), _offer(), LogCaptureFixture, Zone 3 may add a keyword, but only one he has and the offer asked for., Reorder-only remains the default and the common case., Genuinely his, but padding: the offer did not ask for it., Presence in the bank is necessary, never sufficient., Derived from the file, not a magic number. (+18 more)

### Community 52 - "load_fact_bank"
Cohesion: 0.15
Nodes (28): _boolean(), CertificationFact, _claim_list(), EducationFact, _entry_claim(), FactBankError, LanguageFact, load_fact_bank() (+20 more)

### Community 53 - "CompanyRecord"
Cohesion: 0.15
Nodes (19): AnthropicTailoringAdvisor, Claude Messages API adviser used when ``ANTHROPIC_API_KEY`` is set., _Client, _offer(), _plan_payload(), Any, Exception, MonkeyPatch (+11 more)

### Community 54 - "labonnealternance.py"
Cohesion: 0.11
Nodes (17): _InteractiveShapedAdvisor, Human loop: always rejected, and never re-prompted automatically., _InventsThenRecovers, Connection, LogCaptureFixture, Path, Task 37 item 2: give the unknown-id retry something to work with.  An unknown fa, Cites an id that exists nowhere, for a chosen number of attempts. (+9 more)

### Community 55 - "ingest_source"
Cohesion: 0.15
Nodes (12): Connection, Path, test_a_rejected_number_is_counted_separately_from_an_invented_id(), Amber, not red: the document is usable, it just needs a look., test_the_detail_page_shows_the_warning_in_amber(), _Advisor, _application(), Connection (+4 more)

### Community 56 - "pick_variant"
Cohesion: 0.11
Nodes (18): BrowserLauncher, _ConfirmationBaseline, launch_wttj_application(), _Locator, _Page, PrefillPlan, Path, Protocol (+10 more)

### Community 57 - "test_fact_id_resolution.py"
Cohesion: 0.21
Nodes (21): invention_report(), How often the advisor cites an id that does not exist, and whether it recovers., _Invents, Connection, MonkeyPatch, Path, Task 37 item 4: count invention, so the other three items are not guesswork.  Pr, Counting is about what the model invented, not about what was salvaged.      Dro (+13 more)

### Community 58 - "test_letter_locked_fields.py"
Cohesion: 0.18
Nodes (19): bank(), _letter(), _offer(), A letter is prose about a career; a CV is slots the renderer fills., Naming a real-sounding employer he never had is a fabrication, not prose., The renderer injects the address block; the body repeating it is a bug., Otherwise the test above would prove nothing about scope., The bank's own text names nothing it should not; selection is the check. (+11 more)

### Community 59 - "launch_application_assist"
Cohesion: 0.12
Nodes (30): extract_template_context(), pick_variant(), Pick the best of 21 variants from missions, then apply contract rules.      Sinc, Read all editable choices without altering the template., It is droppable because of what it IS, not because of which gate noticed.      _, The unwrapped second call that killed the Capgemini generation.      A degradati, test_an_unknown_fact_id_is_recoverable_wherever_it_is_raised(), test_the_profile_fallback_survives_its_own_fallback_failing() (+22 more)

### Community 60 - "test_letter_quality.py"
Cohesion: 0.16
Nodes (21): _default_letter(), french_de_elision(), _omit_offending_paragraph(), _paragraph_offends(), Return « de <noun> » or « d'<noun> », applying French elision.      Elides befor, Whether this one paragraph is what _validate_letter_body refused.      Only the, Drop the one paragraph the letter gate refused, keeping the rest.      The retry, _render_sourced_letter() (+13 more)

### Community 61 - "test_mailer.py"
Cohesion: 0.20
Nodes (16): Connection, Path, Nothing is weakened: a fabrication ends the run exactly as before., test_a_fatal_gate_still_aborts(), test_an_advisory_gate_never_blocks(), _approve(), Connection, LogCaptureFixture (+8 more)

### Community 62 - "models.py"
Cohesion: 0.21
Nodes (11): _OneShotProfileOrphan, Connection, Path, _Toolchain, A profile-only layout regression that disappears with template wording., test_profile_orphan_recovers_with_template_wording(), Connection, Path (+3 more)

### Community 63 - "reparse_alerts"
Cohesion: 0.21
Nodes (18): current_status(), An invented figure is recoverable — the retry is handed the real ones —     but, test_a_recoverable_gate_with_no_degradation_escalates_to_fatal(), _generation_failed_detail(), Any, Connection, LogCaptureFixture, Path (+10 more)

### Community 64 - "test_designation_numbers.py"
Cohesion: 0.06
Nodes (60): Container, _F, load_cv_profile(), Load the committed CV profile, failing loudly rather than defaulting., _contains(), _contains_any(), _designation_spans(), document_variant_label() (+52 more)

### Community 65 - "test_fact_id_consistency.py"
Cohesion: 0.22
Nodes (14): _bank_payload(), Path, Task 35 item 2: a fact bank whose claim ids do not extend their entry is invalid, The real bank must satisfy the rule the loader now enforces., This is the exact shape the Baïfall entry had., Projects have the same shape as experience, so they get the same rule., `experience.baifallX` starts with the entry id as a STRING but is a     differen, Education, certifications, languages and skills have no sub-claims: the     entr (+6 more)

### Community 66 - "review.py"
Cohesion: 0.17
Nodes (11): bank(), Task 35 item 3: a rejection that says what would have been valid.  Task 22c allo, The regression test for the failure that burned two generations., `experience.` is common to every experience entry. Matching on it would     list, A large entry must not blow the retry prompt., Existing callers and tests match on this prefix; item 3 appends, it does     not, test_a_bad_baifall_id_is_told_a_real_baifall_id(), test_an_unresolvable_id_says_so_plainly_instead_of_dumping_the_bank() (+3 more)

### Community 67 - "ingest_source"
Cohesion: 0.31
Nodes (10): _offer(), Systemic recovery at the generated-prose and document-layout boundaries., Naming the employer is what a motivation letter does.      The rule was never lo, _selection_and_template(), test_a_valid_custom_profile_phrase_is_preserved_exactly(), test_an_invalid_profile_phrase_uses_the_variant_fallback(), test_an_unsupported_candidate_claim_remains_a_hard_failure(), test_model_prose_dashes_are_canonicalized_before_validation() (+2 more)

### Community 68 - "_AnchorParser"
Cohesion: 0.06
Nodes (56): CatalogueEntry, default_catalogue(), load_variant_catalogue(), _parse_criteria(), _parse_shortcuts(), Path, The CV catalogue offered to the advisor when it selects a variant.  The selectio, Read the two-column selection table, skipping its header and separator. (+48 more)

### Community 69 - "test_preview.py"
Cohesion: 0.23
Nodes (12): _bullet_budget(), _claim_length(), An experience claim has to fit the CV's one line.  The renderer inserts a select, Every experience bullet the template ships, as (employer, plain text).      Enti, The longest experience bullet the template itself already renders on one line., Derived from the file, not a magic number., Without this the constant could go stale and quietly widen the budget., The renderer inserts these verbatim, so a long one wraps in silence. (+4 more)

### Community 70 - "vocabulary.py"
Cohesion: 0.06
Nodes (58): FastAPI, Request, open_manually(), The manual_open route: open the offer, copy the letter, submit nothing.      A l, generation_single_flight(), Claim the one generation slot for ``application_id``, or refuse.      Taken *bef, dashboard_cmd(), Launch the local review dashboard on 127.0.0.1. (+50 more)

### Community 71 - "UnknownFactIdError"
Cohesion: 0.08
Nodes (47): _alert_source_clause(), Connection, Restrict to one alert source, or to all of them when none is named., Re-derive company / city / workplace / easy-apply for stored alert offers., reparse_alerts(), ReparseResult, parse_linkedin(), Extract jobs from a LinkedIn job-alert email. (+39 more)

### Community 72 - "Baifall Dream Stage - Reference Document (v3)"
Cohesion: 0.17
Nodes (11): Baifall Dream Stage - Reference Document (v3), Bloc HTML de reference (3 bullets), Bullet 1 (commun, accompli) - 167 car., rendu sur 2 lignes, Bullet 2 (commun, nominal, perimetre complet) - 127 car., 1 ligne, Bullet 3 : declinaisons par variante, Context, Principe v3 : perimetre nominal complet, Regle pour la date (+3 more)

### Community 73 - "test_facts.py"
Cohesion: 0.05
Nodes (81): ApplicantProfile, observable_controls(), Every fillable control's *shape*, for form learning. Never its contents.      ``, The non-secret contact values entered into an ATS form., build_prefill(), discard_mapping(), fields_from_html(), FormField (+73 more)

### Community 74 - "test_progress.py"
Cohesion: 0.05
Nodes (64): _csv(), init_profile_cmd(), _langs(), Interactively fill the profile singleton and seed cv_variants., apply_matching_profile(), CvProfileError, load_matching_profile(), load_variants() (+56 more)

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
Cohesion: 0.50
Nodes (4): facts_cmd(), Print the provenance fact bank grouped for human review., format_fact_bank(), Render the bank as plain UTF-8 text for human review in the CLI.

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
Cohesion: 0.18
Nodes (15): _in_bank(), LogCaptureFixture, A standard's digits name a thing; a metric's digits measure one., The anti-fabrication guarantee is not weakened by designation handling., Only the designation's own span is exempt from the number rule., Judge as the letter is judged: no entry, so the whole bank answers., Looking like a standard is not evidence of holding one., Over-permissiveness has to be auditable after the fact. (+7 more)

### Community 111 - "_AnchorParser"
Cohesion: 0.05
Nodes (63): allowed_numbers(), _bank_parts(), _fact_id_key(), _guessed_section(), letter_scope(), nearest_entry_claim_ids(), _offer_identity(), _organisation_names() (+55 more)

### Community 112 - "test_ingest_idempotent.py"
Cohesion: 0.07
Nodes (59): Return capability-tier tokens that have tripped generations, by frequency., vocabulary_misses(), GenericVocabularyError, load_generic_vocabulary(), parse_rejections(), Path, StrEnum, ValueError (+51 more)

### Community 113 - "apply_matching_profile_cmd"
Cohesion: 0.10
Nodes (29): ingest_cmd(), Fetch offers from a source (or all sources) into the database., _env_bool(), _path(), Configuration and path resolution. Secrets come from .env only (never mocked)., RuntimeError, Background ingest + score refresh triggered from the dashboard.  The web layer o, Raised when a second refresh is requested while one is still running. (+21 more)

### Community 120 - "test_ingest_idempotent.py"
Cohesion: 0.14
Nodes (24): source_id(), _backfill_company_source(), ingest_source(), IngestResult, _insert_offer(), Connection, Ingestion orchestrator: pull normalized records from a Source into the DB.  Idem, INSERT OR IGNORE one offer. Returns True if a new row was created. (+16 more)

### Community 121 - "run_menubar"
Cohesion: 0.67
Nodes (3): counts(), Connection, Ready and queued offer applications, the two numbers worth a glance.

### Community 123 - "test_renderer_owned_fields.py"
Cohesion: 0.17
Nodes (11): build_cv_title(), normalise_role_title(), Remove posting metadata while preserving the actual role wording., Build the deterministic CV title used after all advisor providers., Fact-bank loading, review CLI, and deterministic role-title cleaning., test_build_cv_title_uses_clean_role_and_contract_specific_suffix(), test_every_skill_is_explicitly_verified_or_unverified(), test_fact_bank_covers_every_cv_template_and_has_unique_claim_ids() (+3 more)

### Community 124 - "ApplicationNotQueuedError"
Cohesion: 0.19
Nodes (19): IllegalTransition, log_event(), Connection, ValueError, The single authorized writer of applications.status.  Every status transition MU, Raised when a status change is not permitted by the state machine., Append an audit event. Used for status_change, human_approved, email_sent, etc., Move an application to to_status if legal; log a status_change event.      Retur (+11 more)

### Community 125 - "parse_indeed"
Cohesion: 0.12
Nodes (13): _AlertAnchor, _AnchorParser, _anchors(), clean_job_url(), parse_indeed(), HTMLParser, Collect anchors plus nearby table/list-card text without dependencies., Return a stable detail URL with email/tracking parameters removed. (+5 more)

### Community 132 - "observable_controls"
Cohesion: 0.07
Nodes (32): _Control, _ControlParser, _controls_from_html(), _css_attribute_value(), FillAction, _first_matching_selector(), _Form, _FormParser (+24 more)

## Knowledge Gaps
- **155 isolated node(s):** `profile`, `contacts`, `suppression_list`, `offers`, `offers` (+150 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `OpenAITailoringAdvisor` to `_client`, `observable_controls`, `create_app`, `Path`, `test_routing.py`, `mailer.py`, `apply_assist.py`, `wttj.py`, `france_travail.py`, `_FakePage`, `test_email_alerts.py`, `test_labonnealternance.py`, `Settings`, `test_dashboard_facts_scheduler.py`, `.from_mapping`, `test_cold_outreach.py`, `_FakePage`, `resolve_fact_id`, `pick_variant`, `vocabulary.py`, `test_facts.py`, `apply_matching_profile_cmd`, `_FakeLocator`, `parse_indeed`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Why does `current_status()` connect `reparse_alerts` to `_candidate_name`, `create_app`, `run_dashboard`, `test_routing.py`, `mailer.py`, `test_generic_vocabulary.py`, `apply_assist.py`, `test_skim.py`, `RefreshRunner`, `launch_wttj_application`, `_FakePage`, `generate_application`, `test_contacts.py`, `test_cv_completeness.py`, `_FakePage`, `labonnealternance.py`, `ingest_source`, `test_mailer.py`, `models.py`, `test_designation_numbers.py`, `_AnchorParser`, `vocabulary.py`, `ApplicationNotQueuedError`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `create_app` to `_client`, `observable_controls`, `dashboard.py`, `run_dashboard`, `Path`, `test_routing.py`, `mailer.py`, `apply_assist.py`, `test_skim.py`, `wttj.py`, `SourcedBullet`, `launch_wttj_application`, `generate_application`, `test_email_alerts.py`, `test_labonnealternance.py`, `_Toolchain`, `matcher.py`, `test_cold_outreach.py`, `OpenAITailoringAdvisor`, `pick_variant`, `test_fact_id_resolution.py`, `test_designation_numbers.py`, `vocabulary.py`, `test_progress.py`, `apply_matching_profile_cmd`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 62 inferred relationships involving `Settings` (e.g. with `ApplicantProfile` and `ApplyAdapter`) actually correct?**
  _`Settings` has 62 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `current_status()` (e.g. with `test_a_fatal_gate_still_aborts()` and `test_a_recoverable_gate_with_no_degradation_escalates_to_fatal()`) actually correct?**
  _`current_status()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `TailoringError` (e.g. with `ExperienceFact` and `FactBank`) actually correct?**
  _`TailoringError` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `_payload()` (e.g. with `.advise()` and `_plan()`) actually correct?**
  _`_payload()` has 10 INFERRED edges - model-reasoned connections that need verification._