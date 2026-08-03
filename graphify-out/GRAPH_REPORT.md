# Graph Report - jobpilot  (2026-08-04)

## Corpus Check
- 157 files · ~190,707 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3419 nodes · 8802 edges · 145 communities (123 shown, 22 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 353 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fe8c0b2b`
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
- Connection
- Path

## God Nodes (most connected - your core abstractions)
1. `Settings` - 117 edges
2. `current_status()` - 94 edges
3. `_payload()` - 89 edges
4. `TailoringError` - 83 edges
5. `_Toolchain` - 69 edges
6. `load_fact_bank()` - 68 edges
7. `OfferRecord` - 68 edges
8. `create_app()` - 62 edges
9. `pick_variant()` - 60 edges
10. `OfferContext` - 59 edges

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

## Communities (145 total, 22 thin omitted)

### Community 0 - "test_downloads.py"
Cohesion: 0.14
Nodes (14): ProgressRegistry, Report one operation for as long as it runs, however it ends.      ``with track(, Every operation currently worth reporting, keyed by a stable string., track, _utc_now(), It stays briefly so a poll landing just after completion sees the     outcome, t, A failure that never cleared its progress would leave the page claiming     work, test_a_failure_closes_the_operation_and_keeps_its_message() (+6 more)

### Community 1 - "Request"
Cohesion: 0.08
Nodes (56): Path, Resolve one archived artefact, with the same discipline as the live one.      De, _safe_archive_path(), _safe_artifact_path(), _archives_for(), Generation, is_archive_stamp(), library_entries() (+48 more)

### Community 2 - "_candidate_name"
Cohesion: 0.09
Nodes (76): SimpleNamespace, current_status(), _client(), _events(), _no_advisor_client(), _offer_application(), Connection, MonkeyPatch (+68 more)

### Community 3 - "_client"
Cohesion: 0.09
Nodes (26): adapter_for_url(), _application_for_assist(), _application_for_wttj(), ApplyAssistError, AssistResult, BrowserLauncher, _fallback(), launch_application_assist() (+18 more)

### Community 4 - "create_app"
Cohesion: 0.06
Nodes (46): apply_cmd(), backfill_descriptions_cmd(), init_db_cmd(), invention_report_cmd(), mark_sent_cmd(), queue_cmd(), Synthesise descriptions for stored offers whose text is too thin to score., Re-derive company / city / workplace / easy-apply for stored alert offers. (+38 more)

### Community 5 - "dashboard.py"
Cohesion: 0.07
Nodes (80): FactBank, FactClaim, Match, Pattern, RuntimeError, _add_tech_additions(), _add_tech_keywords(), _contact_fields() (+72 more)

### Community 6 - "run_dashboard"
Cohesion: 0.21
Nodes (16): _dropping_enabled(), _InventsForever, Connection, MonkeyPatch, Path, Task 37 item 3: degradation. Shipped off, turned ON by Task 39.  If the advisor, Turning it off restores the old behaviour exactly., Enabling degradation does not make everything droppable. (+8 more)

### Community 7 - "Path"
Cohesion: 0.08
Nodes (36): derive_fields(), _Derived, Re-derive alert card fields (company / city / workplace / easy-apply) in place., Re-derive one offer's card fields from the text that was stored for it.      Pur, _Card, _card_fields(), is_noise(), is_title_echo() (+28 more)

### Community 8 - "test_routing.py"
Cohesion: 0.06
Nodes (81): Cursor, Decision, RouteId, _applicant_reason(), _artifacts(), _ats_prefill(), _email(), _learned_form() (+73 more)

### Community 9 - "mailer.py"
Cohesion: 0.11
Nodes (37): Show the email that would be sent for a ready application, then confirm (y/N)., send_cmd(), _as_utc(), _build_message(), build_sender(), ColdEmailPreparation, daily_cap_reached(), _default_body() (+29 more)

### Community 10 - "validate_cv.py"
Cohesion: 0.06
Nodes (53): check_orphans(), find_regressions(), Path, Return orphan metrics that are new or materially worse than the template., format_date(), main(), build_letter_html(), detect_github() (+45 more)

### Community 11 - "get_settings"
Cohesion: 0.08
Nodes (41): Any, CvProfile, _advise_and_tailor(), _advisor_fact_context(), _advisor_prompt(), _canonicalize_prose(), _infer_region(), _interactive_structured_payload() (+33 more)

### Community 12 - "connect"
Cohesion: 0.07
Nodes (42): add_contact_cmd(), contacts_cmd(), _csv(), daemon_cmd(), dashboard_cmd(), draft_cold_cmd(), init_profile_cmd(), _langs() (+34 more)

### Community 13 - "test_descriptions.py"
Cohesion: 0.10
Nodes (50): backfill_descriptions(), clear_match_scores(), is_synthesized(), Connection, Return an SQL fragment + params restricting a query to one source., Regenerate synthesised descriptions for stored offers whose text is thin.      I, Drop match_scores rows so the next `score` pass re-evaluates those offers., True when `description` was produced by this module. (+42 more)

### Community 14 - "test_generic_vocabulary.py"
Cohesion: 0.11
Nodes (32): extract_template_context(), pick_variant(), Pick the best of 21 variants from missions, then apply contract rules.      Sinc, Read all editable choices without altering the template., The model had never been told there was one., test_the_prompt_states_the_ceiling(), unsupported number 27001' was rejecting real, bank-backed vocabulary., test_the_observed_failure_no_longer_fails_a_generation() (+24 more)

### Community 15 - "apply_assist.py"
Cohesion: 0.28
Nodes (17): Combined application + cold-mail sends recorded for today (UTC)., sends_today(), _events(), Connection, EmailMessage, Exception, Path, Application email sending: rails, transitions, and events (mocked SMTP). (+9 more)

### Community 16 - "test_skim.py"
Cohesion: 0.09
Nodes (55): FastAPI, create_app(), Build the local dashboard, with injectable generation collaborators for tests., available_sources(), _create_application(), ignore_offer(), promote_offer(), Connection (+47 more)

### Community 17 - "contacts.py"
Cohesion: 0.10
Nodes (38): _candidate_name(), ContactCandidate, discover_and_store(), DiscoverySource, draft_cold_email(), draft_linkedin_note(), _get_or_create_cold_application(), is_professional_address() (+30 more)

### Community 18 - "JobPilot — Codex Handoff (complete A-to-Z)"
Cohesion: 0.04
Nodes (45): 10. HARD REJECTIONS (offers the pipeline should auto-skip), 11. API REFERENCES, 12. DESIGN PRINCIPLES (non-negotiable), 13. ENV VARS (.env), 14. GITHUB PUSH (do this FIRST, before any Codex work), 15. CODEX TASK BREAKDOWN (suggested order), 16. BAIFALL DREAM STAGE REFERENCE, 17. SCRIPTS REFERENCE (+37 more)

### Community 19 - "RefreshRunner"
Cohesion: 0.11
Nodes (25): ExperienceFact, GenerationWarning, _cap_experience_selection(), _experience_bullet_capacity(), _experience_start(), How many bullet rows the template gives each employer, by employer name.      Th, Sort key from an experience's start date, most recent first., Trim any entry that selected more facts than its block has rows.      Recoverabl (+17 more)

### Community 20 - "_payload"
Cohesion: 0.10
Nodes (43): _bullets(), _project(), The advisor selects; the renderer inserts the bank's wording unchanged., The pre-written variants from the skill asset, used as the asset intends., The contract has no field for prose, so a writing advisor fails loudly., Only the entry's own facts, so a skill id cannot become a bullet., Task 25's tolerance survives: ids are normalised before they are judged., The phrase is short, but it is still generated, so the tiers still read it. (+35 more)

### Community 21 - "wttj.py"
Cohesion: 0.10
Nodes (41): _city(), _contact_email(), _contract(), _first(), map_hit(), _org(), _prose(), Any (+33 more)

### Community 22 - "SourcedBullet"
Cohesion: 0.12
Nodes (17): ConnectionFactory, Event, _default_score_pass(), _production_connection(), Any, Connection, Score exactly as ``jobpilot score`` does, with the model already loaded., Single-flight ingest + score pass driven from the dashboard. (+9 more)

### Community 23 - "france_travail.py"
Cohesion: 0.09
Nodes (31): _delay(), Rate limiting + exponential backoff for every external call (constitution rule)., Call fn(); retry on transient HTTP errors with full-jitter exponential backoff., with_backoff(), _first_nonempty(), FranceTravailSource, _map_contact_email(), _map_contract() (+23 more)

### Community 24 - "test_provenance_tiers.py"
Cohesion: 0.08
Nodes (37): SkillFact, _in_bank(), _offer(), Three kinds of token, three different burdens of proof., Not even the widest scope can support it., The reader has to be able to search for it, or add it to the config., Task 26's handling survives as the digit-shaped corner of tier 2., Presence in the bank is necessary for tier 2, never sufficient. (+29 more)

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
Cohesion: 0.06
Nodes (38): Connection, date, Path, Protocol, build_advisor(), _check_orphans(), _contains_generated_orphan(), DocumentToolchain (+30 more)

### Community 31 - "test_contacts.py"
Cohesion: 0.10
Nodes (27): ModuleType, JobPilot: personal job application pipeline for the French IT/cybersecurity mark, _application(), _ConnectionProxy, Connection, Exception, Path, CLI coverage for offer document generation and cold-application approval. (+19 more)

### Community 32 - "test_email_alerts.py"
Cohesion: 0.09
Nodes (43): Message, GmailIMAP, html_of(), LinkedInAlertSource, Minimal read-only Gmail IMAP client., Fetch recent mail sent from `domains` (or any of their subdomains).          The, Return the best HTML (or plain-text) body of an email message., Return the lowercased domain of the address in a `From` header.      Parses the (+35 more)

### Community 33 - "test_labonnealternance.py"
Cohesion: 0.05
Nodes (81): HTTPStatusError, list_outreach_targets(), Companies an ingestion source flagged as likely to hire an alternant.      These, get_or_create_company(), CompanyRecord, _city(), _company_name(), _contract_type() (+73 more)

### Community 34 - "_Toolchain"
Cohesion: 0.08
Nodes (31): _correction_block(), _is_validator_rejection(), _offer_identity(), OfferContext, Raised when an external tailoring provider request fails., Raised when a tailoring provider rejects its API credentials., Raised when a tailoring provider rate-limits a request., Raised when a provider returns an unusable response. (+23 more)

### Community 35 - "email_alerts.py"
Cohesion: 0.08
Nodes (28): Every id the advisor may cite, flattened out of the context it was given.      D, valid_fact_ids(), facts(), _nested_ids(), Task 37 item 1: tell the advisor the set of ids is closed.  `skill.rules.sigma`, Task 37 must not have quietly added Sigma to make the failure go away., Defensive: a template with no projects must not raise here., The exact mechanism that produced skill.rules.sigma. (+20 more)

### Community 36 - "test_alert_card_fields.py"
Cohesion: 0.11
Nodes (32): as_dicts(), clear_warnings(), _decode(), GenerationWarning, Any, Connection, What a generation had to degrade, recorded where the reviewer will see it.  Task, Gate names per application, for the library and tracker markers.      One query (+24 more)

### Community 37 - "Settings"
Cohesion: 0.11
Nodes (18): MissingCredentialError, RuntimeError, Remove configured secrets from exception text before display/logging., Raised when a required secret is absent. We ask; we never silently mock., Settings, RateLimiter, Minimum-delay-per-domain limiter. Blocks until the next call is allowed., DaemonStatus (+10 more)

### Community 38 - "Job Application Pipeline"
Cohesion: 0.06
Nodes (31): Alternance vs Stage, Edge Cases & Principles, Encoding note, Execution Flow, Flag once, then execute:, Generate with the bundled script:, GitHub Exception, Hard rejections (no output): (+23 more)

### Community 39 - "matcher.py"
Cohesion: 0.15
Nodes (28): bonus_score(), cosine(), hard_filter(), keyword_score(), norm(), pick_variant(), Profile, Connection (+20 more)

### Community 40 - "test_cv_completeness.py"
Cohesion: 0.10
Nodes (29): CvProfile, Renderer-owned candidate facts injected into every generated CV., The location printed in the CV header when the offer yields none., _category_skills(), _CompleteAdvisor, Any, Connection, Path (+21 more)

### Community 41 - "OfferRecord"
Cohesion: 0.09
Nodes (30): _fact_id_key(), Fold separator and case differences, and nothing else, for comparison., Map a cited id onto a real fact id, accepting only unambiguous matches.      Mat, resolve_fact_id(), _advise(), ambiguous_bank(), _offer(), Any (+22 more)

### Community 42 - "test_dashboard_facts_scheduler.py"
Cohesion: 0.25
Nodes (18): daemon_status(), Report daemon liveness from the heartbeat file, or admit it is unknown., _client(), fixture_bank(), Connection, MonkeyPatch, Path, TestClient (+10 more)

### Community 43 - ".from_mapping"
Cohesion: 0.06
Nodes (43): BackfillResult, enrich_offer(), is_thin(), Synthesise matchable text for offers that arrive with no description.  Job-alert, Replace a thin description in place; richer descriptions are left alone.      Ca, True when a description is too short to be worth embedding on its own., content_hash(), OfferRecord (+35 more)

### Community 44 - "test_cold_outreach.py"
Cohesion: 0.43
Nodes (6): Any, Connection, Last recorded run per enabled source. ``last_run_at`` is all the DB keeps., Everything the queue page shows about scheduled ingestion., scheduler_status(), source_runs()

### Community 45 - "_FakePage"
Cohesion: 0.24
Nodes (20): _events(), _FakeLauncher, _FakePage, Connection, Path, Row, WTTJ inline application stays human-approved and dry-run by default., _ready_wttj_application() (+12 more)

### Community 46 - "MissingCredentialError"
Cohesion: 0.11
Nodes (21): _F, gate(), Label what this function refuses, and what refusing costs.      Attached to the, The tier this failure carries HERE.      An unclassified error is fatal. That de, What a gate firing is allowed to cost.      Task 39. Seven consecutive generatio, Tier, tier_for(), StrEnum (+13 more)

### Community 47 - "ats.py"
Cohesion: 0.15
Nodes (23): download_filename(), Download names an employer folder can still be read a week later.  ``output/appl, Reduce free text to ``[A-Za-z0-9-_]``, or to "" if nothing survives.      Accent, Build ``<Company>_<Type>_<Nom>.<ext>`` for one artefact.      Falls back to the, slugify(), _client(), Connection, Path (+15 more)

### Community 48 - "AnthropicTailoringAdvisor"
Cohesion: 0.12
Nodes (28): _experience_content(), _FabricatingAdvisor, _gemini_shaped_payload(), _offer(), Connection, MonkeyPatch, Path, _queued_application() (+20 more)

### Community 49 - "OpenAITailoringAdvisor"
Cohesion: 0.16
Nodes (20): _all_template_paths(), _bullet_budget(), _claim_length(), _normalized(), _project_desc_budget(), _project_desc_rows(), An experience claim has to fit the CV's one line.  The renderer inserts a select, The widest project description any template already renders. (+12 more)

### Community 50 - "resolve_fact_id"
Cohesion: 0.16
Nodes (20): FormMapping, mapping_is_complete(), mappings_for(), put_mapping(), Connection, A stored selector -> profile field mapping. Never a stored value., Write one mapping. Rejects a profile_field outside the closed enum., Whether ``domain`` has enough of a mapping to be worth calling a route. (+12 more)

### Community 51 - "test_tech_additions.py"
Cohesion: 0.15
Nodes (26): bank(), _offer(), LogCaptureFixture, Zone 3 may add a keyword, but only one he has and the offer asked for., Reorder-only remains the default and the common case., Genuinely his, but padding: the offer did not ask for it., Presence in the bank is necessary, never sufficient., Derived from the file, not a magic number. (+18 more)

### Community 52 - "load_fact_bank"
Cohesion: 0.11
Nodes (37): facts_cmd(), Print the provenance fact bank grouped for human review., _boolean(), CertificationFact, _claim_list(), EducationFact, _entry_claim(), ExperienceFact (+29 more)

### Community 53 - "CompanyRecord"
Cohesion: 0.18
Nodes (17): fields_from_html(), Read a page's controls as shapes. Values are stripped before we see them., Whether pressing submit is allowed on this domain. Default: no.      Prefill is, Flip the per-domain submit gate. Deliberately has no global counterpart., set_submit_enabled(), submit_enabled(), Connection, Task 34.D: form learning — what may be recorded, and what may never be.  This ta (+9 more)

### Community 54 - "labonnealternance.py"
Cohesion: 0.11
Nodes (17): _InteractiveShapedAdvisor, Human loop: always rejected, and never re-prompted automatically., _InventsThenRecovers, Connection, LogCaptureFixture, Path, Task 37 item 2: give the unknown-id retry something to work with.  An unknown fa, Cites an id that exists nowhere, for a chosen number of attempts. (+9 more)

### Community 55 - "ingest_source"
Cohesion: 0.14
Nodes (13): Connection, Path, Nothing is weakened: a fabrication ends the run exactly as before., An invented figure is recoverable — the retry is handed the real ones —     but, test_a_fatal_gate_still_aborts(), test_a_recoverable_gate_with_no_degradation_escalates_to_fatal(), test_an_advisory_gate_never_blocks(), Amber, not red: the document is usable, it just needs a look. (+5 more)

### Community 56 - "pick_variant"
Cohesion: 0.19
Nodes (9): _ConfirmationBaseline, _Locator, _Page, PrefillPlan, Protocol, The actions selected from a page's current HTML fixture/markup., WTTJ inline form adapter with explicit pre-submit assertions., _scoped_selector() (+1 more)

### Community 57 - "test_fact_id_resolution.py"
Cohesion: 0.14
Nodes (30): ApplyOutcome, approve_application(), Any, Connection, Record human approval, transition, and generate through one shared path.      ``, The result shared by the CLI and dashboard approval surfaces., invention_report(), How often the advisor cites an id that does not exist, and whether it recovers. (+22 more)

### Community 58 - "test_letter_locked_fields.py"
Cohesion: 0.18
Nodes (19): bank(), _letter(), _offer(), A letter is prose about a career; a CV is slots the renderer fills., Naming a real-sounding employer he never had is a fabrication, not prose., The renderer injects the address block; the body repeating it is a bug., Otherwise the test above would prove nothing about scope., The bank's own text names nothing it should not; selection is the check. (+11 more)

### Community 59 - "launch_application_assist"
Cohesion: 0.18
Nodes (19): ATSSource, infer_contract(), map_greenhouse(), map_lever(), map_smartrecruiters(), _ms_to_iso(), Any, Generic ATS pollers for a hand-configured company list (config/targets.yaml).  S (+11 more)

### Community 60 - "test_letter_quality.py"
Cohesion: 0.24
Nodes (16): _default_letter(), french_de_elision(), Return « de <noun> » or « d'<noun> », applying French elision.      Elides befor, _validate_letter_body(), _letter(), _offer(), Letter quality: French elision and the 'Entreprise' placeholder rejection., test_default_letter_elides_poste_before_vowel() (+8 more)

### Community 61 - "test_mailer.py"
Cohesion: 0.33
Nodes (11): _approve(), Connection, LogCaptureFixture, Path, The asset file calls these false positives outside a full render., Task 39: the last hard position of the orphan gate went advisory.      It cost t, The reliable control, per the asset file, so it never becomes advisory., test_a_clean_generation_records_no_orphan_warning() (+3 more)

### Community 62 - "models.py"
Cohesion: 0.13
Nodes (19): _offer(), _OneShotProfileOrphan, Connection, Path, _Toolchain, Systemic recovery at the generated-prose and document-layout boundaries., Naming the employer is what a motivation letter does.      The rule was never lo, A profile-only layout regression that disappears with template wording. (+11 more)

### Community 63 - "reparse_alerts"
Cohesion: 0.19
Nodes (17): application(), Connection, _generation_failed_detail(), Any, Connection, LogCaptureFixture, Path, _queued_application() (+9 more)

### Community 64 - "test_designation_numbers.py"
Cohesion: 0.20
Nodes (18): mark_application_sent(), Manual fallback: record an externally-submitted application as sent., _utc_now(), log_event(), Connection, Append an audit event. Used for status_change, human_approved, email_sent, etc., Move an application to to_status if legal; log a status_change event.      Retur, transition() (+10 more)

### Community 65 - "test_fact_id_consistency.py"
Cohesion: 0.20
Nodes (15): bank(), _bank_payload(), Path, Task 35 item 2: a fact bank whose claim ids do not extend their entry is invalid, The real bank must satisfy the rule the loader now enforces., This is the exact shape the Baïfall entry had., Projects have the same shape as experience, so they get the same rule., `experience.baifallX` starts with the entry id as a STRING but is a     differen (+7 more)

### Community 66 - "review.py"
Cohesion: 0.08
Nodes (17): CompletedProcess, AmbiguousFactIdError, Raised when generated prose states a figure the bank does not contain.      A si, Raised when a citation matches no fact id, even after normalisation.      ``sect, Raised when a citation could be several facts. Never guess between them., Raised when one automatic validator-feedback retry still failed.      ``str()``, TailoringRejectedError, UnknownFactIdError (+9 more)

### Community 67 - "ingest_source"
Cohesion: 0.05
Nodes (75): Client, AnthropicTailoringAdvisor, InteractiveTailoringAdvisor, OpenAITailoringAdvisor, Claude Messages API adviser used when ``ANTHROPIC_API_KEY`` is set., OpenAI-compatible Chat Completions adviser., Terminal prompts used when interactive tailoring is selected., _Client (+67 more)

### Community 68 - "_AnchorParser"
Cohesion: 0.10
Nodes (28): CatalogueEntry, default_catalogue(), load_variant_catalogue(), _parse_criteria(), _parse_shortcuts(), Path, RuntimeError, The CV catalogue offered to the advisor when it selects a variant.  The selectio (+20 more)

### Community 69 - "test_preview.py"
Cohesion: 0.15
Nodes (22): Apply the mechanical contract and encoding rules to a chosen slug.      These ar, The contract line an adapted alternance CV must carry., The stage contract line to fall back to, built from what is known.      Determin, Preserve a valid contract phrase; replace only a rejected one.      Same shape a, _resolve_stage_contract_phrase(), _stage_contract_fallback(), _validate_stage_contract_phrase(), variant_for_slug() (+14 more)

### Community 70 - "vocabulary.py"
Cohesion: 0.18
Nodes (19): application_detail(), applications_by_status(), event_history(), outreach_drafts(), Any, Connection, queued_applications(), Read-only queries shared by review surfaces. (+11 more)

### Community 71 - "UnknownFactIdError"
Cohesion: 0.10
Nodes (39): _alert_source_clause(), Connection, Restrict to one alert source, or to all of them when none is named., Re-derive company / city / workplace / easy-apply for stored alert offers., reparse_alerts(), ReparseResult, parse_linkedin(), Extract jobs from a LinkedIn job-alert email. (+31 more)

### Community 72 - "Baifall Dream Stage - Reference Document (v3)"
Cohesion: 0.17
Nodes (11): Baifall Dream Stage - Reference Document (v3), Bloc HTML de reference (3 bullets), Bullet 1 (commun, accompli) - 167 car., rendu sur 2 lignes, Bullet 2 (commun, nominal, perimetre complet) - 127 car., 1 ligne, Bullet 3 : declinaisons par variante, Context, Principe v3 : perimetre nominal complet, Regle pour la date (+3 more)

### Community 73 - "test_facts.py"
Cohesion: 0.11
Nodes (26): FormField, infer_profile_field(), One control's shape. Deliberately has nowhere to put a typed value., Everything naming this field, with separators folded to spaces.          Real fo, Name the reason this field may never be mapped, or None if it may.      Refused:, Which profile field this control wants, or None to leave it to the human., Record mappings for one manually submitted form. Values are never stored.      C, Every refusal category present in a form, for reporting to the human. (+18 more)

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
Cohesion: 0.10
Nodes (32): apply_matching_profile_cmd(), Connection, _queue_snapshot(), Apply config/matching_profile.yaml and report what it changed.      Re-scoring i, Count what currently clears the bar, for an honest before/after., Re-evaluate every offer against the new vocabulary.      ``jobpilot score`` only, Score all unscored offers and queue those above threshold., _rescore_all() (+24 more)

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
Cohesion: 0.14
Nodes (18): drop_unknown_citation(), DroppedCitation, _employer_bullet_floor(), One citation removed as a last resort, and where it was removed from., How many bullets the completeness floor guarantees this employer.      Read from, Remove one unusable citation, or refuse when removing it would weaken the CV., _plan(), The completeness floor is a hard failure, not a preference. (+10 more)

### Community 88 - "profile.py"
Cohesion: 0.21
Nodes (17): _check(), LogCaptureFixture, Path, The vocabulary tier is config, and its misses are countable., Tier 1 must not be reachable through tier 3, so the file may not try., The parser reads what the validator writes, not a hand-made string., The whole point: a category word is a config edit, not a release., test_a_malformed_vocabulary_is_refused_loudly() (+9 more)

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
Cohesion: 0.24
Nodes (17): Return capability-tier tokens that have tripped generations, by frequency., vocabulary_misses(), The one wording for a refused token; every caller goes through here.      Naming, rejection_message(), _failure(), Connection, MonkeyPatch, No vocabulary entry may ever excuse a fabricated number or employer. (+9 more)

### Community 110 - "test_designation_numbers.py"
Cohesion: 0.17
Nodes (16): bank(), _in_bank(), LogCaptureFixture, A standard's digits name a thing; a metric's digits measure one., The anti-fabrication guarantee is not weakened by designation handling., Only the designation's own span is exempt from the number rule., Judge as the letter is judged: no entry, so the whole bank answers., Looking like a standard is not evidence of holding one. (+8 more)

### Community 111 - "_AnchorParser"
Cohesion: 0.05
Nodes (77): Container, allowed_numbers(), _bank_parts(), _designation_spans(), _guessed_section(), letter_scope(), _normalized_number(), _organisation_names() (+69 more)

### Community 112 - "test_ingest_idempotent.py"
Cohesion: 0.13
Nodes (17): parse_rejections(), StrEnum, Three tiers of token, so a category word is not judged like a claim.  A sourced, The tier that refused a token, current wordings and retired ones alike., Recover the refused tokens from stored validator messages.      The events table, How much a token has to be backed up before it may be written., One token a validator refused, why, and what it was judged against., tier_of() (+9 more)

### Community 113 - "apply_matching_profile_cmd"
Cohesion: 0.08
Nodes (42): Logger, SentenceTransformer, Put text on the system clipboard, or say plainly that it could not.  The manual_, _env_bool(), get_settings(), _path(), Configuration and path resolution. Secrets come from .env only (never mocked)., Database connection factory, schema application, and migration runner. (+34 more)

### Community 114 - "test_variant_selection.py"
Cohesion: 0.17
Nodes (11): build_cv_title(), normalise_role_title(), Remove posting metadata while preserving the actual role wording., Build the deterministic CV title used after all advisor providers., Fact-bank loading, review CLI, and deterministic role-title cleaning., test_build_cv_title_uses_clean_role_and_contract_specific_suffix(), test_every_skill_is_explicitly_verified_or_unverified(), test_fact_bank_covers_every_cv_template_and_has_unique_claim_ids() (+3 more)

### Community 115 - "reparse_alerts"
Cohesion: 0.17
Nodes (11): bank(), Task 35 item 3: a rejection that says what would have been valid.  Task 22c allo, The regression test for the failure that burned two generations., `experience.` is common to every experience entry. Matching on it would     list, A large entry must not blow the retry prompt., Existing callers and tests match on this prefix; item 3 appends, it does     not, test_a_bad_baifall_id_is_told_a_real_baifall_id(), test_an_unresolvable_id_says_so_plainly_instead_of_dumping_the_bank() (+3 more)

### Community 116 - "test_profile_domain_anchor.py"
Cohesion: 0.21
Nodes (11): _profile_of(), Path, Task 40: the domain phrase is found by its own marker, not by its neighbours.  _, Not just the wordings we ship: any of them, including ones nobody wrote yet., The ±15-character layout budget must not shift under it., The bug. This raised "template profile domain phrase not found"., _stage_plan(), test_a_stage_adapted_cv_can_still_be_re_read() (+3 more)

### Community 117 - "tracker.py"
Cohesion: 0.38
Nodes (8): FakeSource, Connection, Re-running ingest must never duplicate rows (constitution idempotency rule)., _sample(), test_company_deduped_across_offers_and_runs(), test_first_run_inserts_all(), test_last_run_at_updated(), test_second_run_inserts_nothing()

### Community 118 - "_TextParser"
Cohesion: 0.20
Nodes (5): letter_plain_text(), Path, Strip a generated letter's markup down to what a human would paste., The generated letter as plain text, or '' when it was never generated., _TextParser

### Community 119 - "refresh_operation"
Cohesion: 0.23
Nodes (9): Operation, Any, datetime, Everything running, plus anything that finished very recently., Present a RefreshRunner snapshot in the same shape as everything else.      Refr, One slow thing, and how far along it is., refresh_operation(), test_a_refresh_snapshot_becomes_a_per_source_operation() (+1 more)

### Community 120 - "test_ingest_idempotent.py"
Cohesion: 0.15
Nodes (18): source_id(), _backfill_company_source(), ingest_source(), IngestResult, _insert_offer(), Connection, INSERT OR IGNORE one offer. Returns True if a new row was created., Run one source end to end. Commits once at the end for atomicity. (+10 more)

### Community 121 - "run_menubar"
Cohesion: 0.38
Nodes (13): _client(), Connection, Path, TestClient, Task 36 item 3: read the CV before downloading it.  Reading is the step that dec, Task 34 pinned this. Naming the download must not have widened it., Separate actions, same bytes, same guarded path., _ready_with_artifacts() (+5 more)

### Community 123 - "test_renderer_owned_fields.py"
Cohesion: 0.25
Nodes (7): The guarantees that made four _validate_plan branches unreachable.  Task 39 item, The one input to resolve_header_location that comes from config., _offer_start falls back to « septembre 2026 », so there is always one., test_prose_canonicalization_removes_every_dash_the_letter_gate_looked_for(), test_the_built_title_always_carries_a_start_date(), test_the_profiles_own_fallback_is_itself_an_allowed_region(), test_the_resolved_header_location_is_always_one_allowed_region()

### Community 124 - "ApplicationNotQueuedError"
Cohesion: 0.05
Nodes (48): LookupError, Request, open_manually(), The manual_open route: open the offer, copy the letter, submit nothing.      A l, ApplicationGenerationError, ApplicationNotFoundError, ApplicationNotQueuedError, archive_artifacts() (+40 more)

### Community 125 - "parse_indeed"
Cohesion: 0.20
Nodes (10): menubar_cmd(), Show ready/queued counts in the macOS menu bar (optional extra)., MenubarUnavailable, Any, RuntimeError, Raised when the menu bar item cannot run on this machine., Import rumps or explain, in French, exactly how to get it., Run the menu bar item until quit. Blocks; opens the dashboard on click. (+2 more)

### Community 126 - "build_advisor"
Cohesion: 0.22
Nodes (9): GenericVocabularyError, load_generic_vocabulary(), Path, ValueError, Load the terms that assert nothing about the candidate.      Kept in config rath, Raised when the committed generic vocabulary is malformed., Silently allowing nothing would look like a strict validator, not a bug., test_a_missing_vocabulary_file_is_an_error_not_an_empty_set() (+1 more)

### Community 128 - "_client"
Cohesion: 0.33
Nodes (11): _client(), Connection, Path, TestClient, The point of the whole item: the writer lock is held, and /progress still     an, Task 34's rule: the validator's own message, verbatim, not 'Error: 500'., It must answer while a generation holds the writer lock., test_a_generation_failure_is_reported_in_the_interface_voice() (+3 more)

### Community 129 - "ApplicantProfile"
Cohesion: 0.15
Nodes (16): ApplicantProfile, The non-secret contact values entered into an ATS form., build_prefill(), discard_mapping(), FormLearningError, PrefillOutcome, _profile_values(), ValueError (+8 more)

### Community 130 - "test_progress.py"
Cohesion: 0.20
Nodes (3): Task 36 item 6: live progress for the slow operations.  Generation, regeneration, The token system disables motion wholesale rather than per-animation., test_the_spinner_respects_reduced_motion()

### Community 131 - ".finish"
Cohesion: 0.22
Nodes (4): BaseException, Update a running operation. A key that is not running is ignored., Close an operation. The first outcome recorded wins.          A handled failure, Record a failure the caller handled rather than raised.          The dashboard c

### Community 132 - "observable_controls"
Cohesion: 0.10
Nodes (27): _Control, _ControlParser, _controls_from_html(), _css_attribute_value(), FillAction, _first_matching_selector(), _Form, _FormParser (+19 more)

### Community 133 - "test_registry.py"
Cohesion: 0.36
Nodes (9): ingest_cmd(), Fetch offers from a source (or all sources) into the database., is_enabled(), Path, Source enablement via config/sources.yaml., _settings(), test_disabled_source_excluded(), test_no_config_all_enabled() (+1 more)

### Community 134 - "Request"
Cohesion: 0.33
Nodes (7): _citation_warning(), _generation_warnings(), Any, Render an ISO timestamp as YYYY-MM-DD; pass other values through as text., The warning for a CV generated without a citation the advisor invented.      Rea, What this generation degraded, for the amber block on the detail page.      Appl, _ymd()

### Community 135 - "_Advisor"
Cohesion: 0.53
Nodes (5): _Advisor, _application(), Connection, test_generation_failure_returns_application_to_queue(), test_generation_runs_quality_gates_before_pdfs_and_moves_to_ready()

### Community 137 - "InteractiveTailoringAdvisor"
Cohesion: 0.50
Nodes (4): observable_controls(), Every fillable control's *shape*, for form learning. Never its contents.      ``, One enforcement point: values are stripped before this module sees them., test_observable_controls_never_expose_what_the_human_typed()

### Community 138 - "Client"
Cohesion: 0.67
Nodes (3): counts(), Connection, Ready and queued offer applications, the two numbers worth a glance.

## Knowledge Gaps
- **155 isolated node(s):** `profile`, `contacts`, `suppression_list`, `offers`, `offers` (+150 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `Settings` to `ApplicantProfile`, `_client`, `observable_controls`, `test_registry.py`, `Path`, `SendBlocked`, `mailer.py`, `test_routing.py`, `wttj.py`, `france_travail.py`, `_FakePage`, `test_email_alerts.py`, `test_labonnealternance.py`, `test_dashboard_facts_scheduler.py`, `.from_mapping`, `test_cold_outreach.py`, `_FakePage`, `pick_variant`, `launch_application_assist`, `apply_matching_profile_cmd`, `_TextParser`, `_FakeLocator`, `ApplicationNotQueuedError`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `current_status()` connect `_candidate_name` to `run_dashboard`, `test_routing.py`, `mailer.py`, `connect`, `apply_assist.py`, `test_skim.py`, `launch_wttj_application`, `_FakePage`, `test_contacts.py`, `test_cv_completeness.py`, `_FakePage`, `AnthropicTailoringAdvisor`, `labonnealternance.py`, `ingest_source`, `test_fact_id_resolution.py`, `test_mailer.py`, `models.py`, `reparse_alerts`, `test_designation_numbers.py`, `ingest_source`, `ApplicationNotQueuedError`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `apply_matching_profile_cmd` to `_client`, `observable_controls`, `create_app`, `test_registry.py`, `run_dashboard`, `test_routing.py`, `mailer.py`, `connect`, `apply_assist.py`, `test_skim.py`, `wttj.py`, `SourcedBullet`, `launch_wttj_application`, `test_email_alerts.py`, `test_labonnealternance.py`, `Settings`, `test_fact_id_resolution.py`, `test_valid_sourced_advice_completes_the_shared_generation_path`, `ApplicationNotQueuedError`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 62 inferred relationships involving `Settings` (e.g. with `ApplicantProfile` and `ApplyAdapter`) actually correct?**
  _`Settings` has 62 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `current_status()` (e.g. with `test_a_fatal_gate_still_aborts()` and `test_a_recoverable_gate_with_no_degradation_escalates_to_fatal()`) actually correct?**
  _`current_status()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `_payload()` (e.g. with `.advise()` and `_plan()`) actually correct?**
  _`_payload()` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `TailoringError` (e.g. with `_CompleteAdvisor` and `_IncompleteAdvisor`) actually correct?**
  _`TailoringError` has 17 INFERRED edges - model-reasoned connections that need verification._