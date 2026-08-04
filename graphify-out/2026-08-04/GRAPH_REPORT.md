# Graph Report - jobpilot  (2026-08-04)

## Corpus Check
- 176 files · ~215,780 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3835 nodes · 9913 edges · 158 communities (133 shown, 25 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 573 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2fed7902`
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
- _bullets
- test_dedup.py
- update.sh
- scheduler_status
- run_dashboard
- mappings_for
- vocabulary.py
- GmailIMAP
- send_application_email
- _Advisor
- record_form_fields
- ingest_source
- parse_indeed
- test_ingest_idempotent.py
- mapping_is_complete
- 010_offers_imported.sql
- test_registry.py
- .__init__
- observable_controls
- gate
- counts
- suppress_email
- test_sourcing_targets_changes_no_sending_gate
- test_no_fixture_contains_a_credential
- .__init__

## God Nodes (most connected - your core abstractions)
1. `Settings` - 117 edges
2. `current_status()` - 97 edges
3. `_payload()` - 92 edges
4. `TailoringError` - 89 edges
5. `load_fact_bank()` - 79 edges
6. `FactBank` - 73 edges
7. `OfferRecord` - 73 edges
8. `_Toolchain` - 69 edges
9. `OfferContext` - 67 edges
10. `pick_variant()` - 60 edges

## Surprising Connections (you probably didn't know these)
- `test_the_warning_is_visible_on_the_application_page()` --calls--> `create_app()`  [INFERRED]
  tests/test_drop_unknown_citation.py → src/jobpilot/dashboard.py
- `test_the_detail_page_shows_the_warning_in_amber()` --calls--> `create_app()`  [INFERRED]
  tests/test_generation_warnings.py → src/jobpilot/dashboard.py
- `_row()` --calls--> `source_id()`  [INFERRED]
  tests/test_hard_filter.py → src/jobpilot/db.py
- `_FakeLauncher` --uses--> `WTTJApplyError`  [INFERRED]
  tests/test_wttj_apply.py → src/jobpilot/apply_assist.py
- `_FakeLocator` --uses--> `WTTJApplyError`  [INFERRED]
  tests/test_wttj_apply.py → src/jobpilot/apply_assist.py

## Import Cycles
- None detected.

## Communities (158 total, 25 thin omitted)

### Community 0 - "test_downloads.py"
Cohesion: 0.05
Nodes (41): BaseException, Operation, ProgressRegistry, Any, datetime, Update a running operation. A key that is not running is ignored., Close an operation. The first outcome recorded wins.          A handled failure, Everything running, plus anything that finished very recently. (+33 more)

### Community 1 - "Request"
Cohesion: 0.08
Nodes (55): Resolve one archived artefact, with the same discipline as the live one.      De, _safe_archive_path(), _archives_for(), Generation, is_archive_stamp(), library_entries(), LibraryEntry, _mtime_iso() (+47 more)

### Community 2 - "_candidate_name"
Cohesion: 0.07
Nodes (92): SimpleNamespace, generation_single_flight(), Claim the one generation slot for ``application_id``, or refuse.      Taken *bef, _client(), _days_ago(), _events(), _no_advisor_client(), _offer_application() (+84 more)

### Community 3 - "_client"
Cohesion: 0.18
Nodes (15): _application_for_assist(), _application_for_wttj(), ApplyAssistError, AssistResult, _fallback(), launch_application_assist(), Connection, Row (+7 more)

### Community 4 - "create_app"
Cohesion: 0.15
Nodes (19): AnthropicTailoringAdvisor, Claude Messages API adviser used when ``ANTHROPIC_API_KEY`` is set., _Client, _offer(), _plan_payload(), Any, Exception, MonkeyPatch (+11 more)

### Community 5 - "dashboard.py"
Cohesion: 0.06
Nodes (78): Container, Match, Pattern, _add_tech_additions(), _add_tech_keywords(), _contains(), _contains_any(), _designation_spans() (+70 more)

### Community 6 - "run_dashboard"
Cohesion: 0.11
Nodes (31): drop_unknown_citation(), Remove one unusable citation, or refuse when removing it would weaken the CV., bank(), _dropping_enabled(), _InventsForever, _plan(), Connection, MonkeyPatch (+23 more)

### Community 7 - "Path"
Cohesion: 0.15
Nodes (21): ATSSource, infer_contract(), load_targets(), map_greenhouse(), map_lever(), map_smartrecruiters(), _ms_to_iso(), Any (+13 more)

### Community 8 - "test_routing.py"
Cohesion: 0.10
Nodes (58): Cursor, _artifacts(), Path, Resolve the one route this application would go out by. Writes nothing., The resolved plan for one application. Carries no state and stores none., Fingerprint of exactly the inputs that decided this route.          Stateless by, resolve_route(), Route (+50 more)

### Community 9 - "mailer.py"
Cohesion: 0.10
Nodes (41): _as_utc(), _build_message(), build_sender(), ColdEmailPreparation, daily_cap_reached(), _default_body(), EmailPreparation, EmailSender (+33 more)

### Community 10 - "validate_cv.py"
Cohesion: 0.06
Nodes (53): check_orphans(), find_regressions(), Path, Return orphan metrics that are new or materially worse than the template., format_date(), main(), build_letter_html(), detect_github() (+45 more)

### Community 11 - "get_settings"
Cohesion: 0.06
Nodes (69): ExperienceFact, FactClaim, One atomic statement that generated content may cite., SkillFact, GenerationWarning, One thing the reviewer is being asked to check by eye., CvProfile, Renderer-owned candidate facts injected into every generated CV. (+61 more)

### Community 12 - "connect"
Cohesion: 0.15
Nodes (22): Apply the mechanical contract and encoding rules to a chosen slug.      These ar, The contract line an adapted alternance CV must carry., The stage contract line to fall back to, built from what is known.      Determin, Preserve a valid contract phrase; replace only a rejected one.      Same shape a, _resolve_stage_contract_phrase(), _stage_contract_fallback(), _validate_stage_contract_phrase(), variant_for_slug() (+14 more)

### Community 13 - "test_descriptions.py"
Cohesion: 0.11
Nodes (46): backfill_descriptions(), clear_match_scores(), Connection, Return an SQL fragment + params restricting a query to one source., Regenerate synthesised descriptions for stored offers whose text is thin.      I, Drop match_scores rows so the next `score` pass re-evaluates those offers., Compose a compact French paragraph from the fields the alert provided.      This, RescoreResult (+38 more)

### Community 14 - "test_generic_vocabulary.py"
Cohesion: 0.08
Nodes (39): pick_variant(), Pick the best of 21 variants from missions, then apply contract rules.      Sinc, Validate the one JSON contract shared by every advisor provider., Task 39 demoted this to advisory.      A tool listed under two categories is cos, test_duplicate_tool_across_categories_warns_without_blocking(), unsupported number 27001' was rejecting real, bank-backed vocabulary., test_the_observed_failure_no_longer_fails_a_generation(), _tailor() (+31 more)

### Community 15 - "apply_assist.py"
Cohesion: 0.13
Nodes (34): applications_by_status(), Offer applications in one status, newest first, with their age.      Returns the, _client(), _days_ago(), _offer_application(), Connection, MonkeyPatch, TestClient (+26 more)

### Community 16 - "test_skim.py"
Cohesion: 0.08
Nodes (58): max_offer_age_days(), The instant a row must be at or after to survive the staleness filter.      For, stale_cutoff(), available_sources(), _create_application(), ignore_offer(), promote_offer(), Connection (+50 more)

### Community 17 - "contacts.py"
Cohesion: 0.08
Nodes (47): add_contact_cmd(), contacts_cmd(), draft_cold_cmd(), Resolve a company by numeric id or name; create by name if absent., Manually add a hiring contact for a company (default discovery path)., List stored contacts for a company, or the sourced outreach targets.      A targ, Draft a LinkedIn note + cold email and queue them for review (no send)., _resolve_company() (+39 more)

### Community 18 - "JobPilot — Codex Handoff (complete A-to-Z)"
Cohesion: 0.04
Nodes (45): 10. HARD REJECTIONS (offers the pipeline should auto-skip), 11. API REFERENCES, 12. DESIGN PRINCIPLES (non-negotiable), 13. ENV VARS (.env), 14. GITHUB PUSH (do this FIRST, before any Codex work), 15. CODEX TASK BREAKDOWN (suggested order), 16. BAIFALL DREAM STAGE REFERENCE, 17. SCRIPTS REFERENCE (+37 more)

### Community 19 - "RefreshRunner"
Cohesion: 0.17
Nodes (25): TestClient, _client(), _import(), Connection, Task 43 item 4: after a description arrives, offer to redo the tailoring.  An ap, Task 34's regenerate refuses anything but `ready`, and an applied CV has     alr, The button posts where the existing Régénérer posts. Asserted by     comparing t, The extension POSTs JSON from the offer page and never lands on the     dashboar (+17 more)

### Community 20 - "_payload"
Cohesion: 0.10
Nodes (45): _bullets(), _project(), The advisor selects; the renderer inserts the bank's wording unchanged., The pre-written variants from the skill asset, used as the asset intends., The contract has no field for prose, so a writing advisor fails loudly., Only the entry's own facts, so a skill id cannot become a bullet., Task 25's tolerance survives: ids are normalised before they are judged., The phrase is short, but it is still generated, so the tiers still read it. (+37 more)

### Community 21 - "wttj.py"
Cohesion: 0.10
Nodes (41): _city(), _contact_email(), _contract(), _first(), map_hit(), _org(), _prose(), Any (+33 more)

### Community 22 - "SourcedBullet"
Cohesion: 0.09
Nodes (29): ConnectionFactory, Event, _default_model_loader(), _default_score_pass(), _production_connection(), Any, Connection, RuntimeError (+21 more)

### Community 23 - "france_travail.py"
Cohesion: 0.14
Nodes (22): _first_nonempty(), FranceTravailSource, _map_contact_email(), _map_contract(), _map_duration_months(), map_offer(), Any, Parse '... - 12 Mois' style durations from typeContratLibelle. (+14 more)

### Community 24 - "test_provenance_tiers.py"
Cohesion: 0.08
Nodes (37): bank(), _in_bank(), _offer(), Three kinds of token, three different burdens of proof., Not even the widest scope can support it., The reader has to be able to search for it, or add it to the config., Task 26's handling survives as the digit-shaped corner of tier 2., Presence in the bank is necessary for tier 2, never sufficient. (+29 more)

### Community 25 - "launch_wttj_application"
Cohesion: 0.22
Nodes (25): _cold_draft(), _configure_dashboard(), _dashboard_client(), _event_rows(), Connection, EmailMessage, Exception, MonkeyPatch (+17 more)

### Community 26 - "Dashboard"
Cohesion: 0.05
Nodes (40): Actualiser les offres (refresh from the page), Always up, without a terminal, Architecture (summary), ATS application assist (prefill only), Background scheduling, CI, Cold outreach sending (disabled by default), Commands (+32 more)

### Community 27 - "_FakePage"
Cohesion: 0.10
Nodes (21): ApplyAdapter, _BaseAdapter, GreenhouseAdapter, LeverAdapter, Common adapter interface for a best-effort ATS prefill., Shared plan building and non-submitting form interaction., SmartRecruitersAdapter, _FakeLauncher (+13 more)

### Community 28 - "cli.py"
Cohesion: 0.20
Nodes (27): _application(), _client(), Connection, Path, TestClient, Task 36 item 5: the tracker page.  Read-only in the strict sense: nothing here w, After the POST the tracker shows the new state with no manual refresh., No form, no button that changes anything: this surface only reports. (+19 more)

### Community 29 - "test_desktop_shell.py"
Cohesion: 0.07
Nodes (40): CaptureFixture, dashboard_already_running(), Whether something is already listening on the dashboard's port.      A connect p, The menu bar text. Short: it competes with every other item up there., title(), _bound_port(), _fake_macos(), _module_level_imports() (+32 more)

### Community 30 - "generate_application"
Cohesion: 0.08
Nodes (23): date, _check_orphans(), _contains_generated_orphan(), DocumentToolchain, _french_date(), generate_application(), _persist_variant(), CompletedProcess (+15 more)

### Community 31 - "test_contacts.py"
Cohesion: 0.10
Nodes (27): ModuleType, JobPilot: personal job application pipeline for the French IT/cybersecurity mark, _application(), _ConnectionProxy, Connection, Exception, Path, CLI coverage for offer document generation and cold-application approval. (+19 more)

### Community 32 - "test_email_alerts.py"
Cohesion: 0.09
Nodes (46): Message, EmailAlertError, GmailIMAP, html_of(), LinkedInAlertSource, RuntimeError, Minimal read-only Gmail IMAP client., Fetch recent mail sent from `domains` (or any of their subdomains).          The (+38 more)

### Community 33 - "test_labonnealternance.py"
Cohesion: 0.15
Nodes (29): _fixture(), _NoWait, LogCaptureFixture, La Bonne Alternance through the API Apprentissage: mapping, rails, ingestion.  E, The endpoint has no pagination, so this is the volume knob that exists., A full ingest reads both lists; it must not pay for the search twice., The live API really does repeat an offer inside one response., A company that has posted nothing must not appear in the review queue. (+21 more)

### Community 34 - "_Toolchain"
Cohesion: 0.07
Nodes (29): Task 43 item 2: the browser extension, and the line it must not cross.  The exte, Two files naming the same three sites. A content script runs in the     page's o, Most of the time JobPilot is not running. The extension has to be     invisible, A rejected promise with no catch surfaces as an unhandled rejection,     which i, One obvious place, with the warning next to it., The requirement that matters most in a year: when LinkedIn changes its     gener, The biggest element on a page is a wrapper holding the whole page., Sending the navigation bar would replace a real description with chrome.     The (+21 more)

### Community 35 - "email_alerts.py"
Cohesion: 0.08
Nodes (28): Every id the advisor may cite, flattened out of the context it was given.      D, valid_fact_ids(), facts(), _nested_ids(), Task 37 item 1: tell the advisor the set of ids is closed.  `skill.rules.sigma`, Task 37 must not have quietly added Sigma to make the failure go away., Defensive: a template with no projects must not raise here., The exact mechanism that produced skill.rules.sigma. (+20 more)

### Community 36 - "test_alert_card_fields.py"
Cohesion: 0.10
Nodes (32): as_dicts(), clear_warnings(), _decode(), Any, Connection, What a generation had to degrade, recorded where the reviewer will see it.  Task, Gate names per application, for the library and tracker markers.      One query, Template-facing shape. (+24 more)

### Community 37 - "Settings"
Cohesion: 0.08
Nodes (50): FactBank, _advise_and_tailor(), _advisor_fact_context(), _advisor_prompt(), _cap_experience_selection(), _contact_fields(), _correction_block(), _cv_locked_fields() (+42 more)

### Community 38 - "Job Application Pipeline"
Cohesion: 0.06
Nodes (31): Alternance vs Stage, Edge Cases & Principles, Encoding note, Execution Flow, Flag once, then execute:, Generate with the bundled script:, GitHub Exception, Hard rejections (no output): (+23 more)

### Community 39 - "matcher.py"
Cohesion: 0.15
Nodes (28): bonus_score(), cosine(), hard_filter(), keyword_score(), norm(), pick_variant(), Profile, Connection (+20 more)

### Community 40 - "test_cv_completeness.py"
Cohesion: 0.13
Nodes (22): _category_skills(), Any, Connection, Path, _Toolchain, _queued_application(), Structural completeness floor for AI-generated CVs (Task 22).  Selection freedom, Every shipped category line with its raw, non-deduplicated tool list. (+14 more)

### Community 41 - "OfferRecord"
Cohesion: 0.08
Nodes (32): Path, Request, dashboard_cmd(), Launch the local review dashboard on 127.0.0.1., _candidate_name(), _citation_warning(), database_connection(), _generation_warnings() (+24 more)

### Community 42 - "test_dashboard_facts_scheduler.py"
Cohesion: 0.18
Nodes (11): HTTPStatusError, LaBonneAlternanceAuthError, LaBonneAlternanceError, LaBonneAlternanceRateLimited, LaBonneAlternanceSource, RuntimeError, Turn an HTTP failure into a typed error, with the key removed., API Apprentissage refused or failed a request. (+3 more)

### Community 43 - ".from_mapping"
Cohesion: 0.13
Nodes (27): Decision, RouteId, adapter_for_url(), Return the owning ATS adapter, if the saved offer URL is recognized., Remove configured secrets from exception text before display/logging., Settings, _applicant_reason(), _ats_prefill() (+19 more)

### Community 44 - "test_cold_outreach.py"
Cohesion: 0.25
Nodes (19): Show the email that would be sent for a ready application, then confirm (y/N)., send_cmd(), Send the application by email, then transition ready -> applied.      Returns th, send_application_email(), _events(), Connection, EmailMessage, Exception (+11 more)

### Community 45 - "_FakePage"
Cohesion: 0.24
Nodes (20): _events(), _FakeLauncher, _FakePage, Connection, Path, Row, WTTJ inline application stays human-approved and dry-run by default., _ready_wttj_application() (+12 more)

### Community 46 - "MissingCredentialError"
Cohesion: 0.16
Nodes (30): _client(), _fail(), _Fake, _offer(), Connection, Row, TestClient, Task 41 item 6: a source that has stopped answering must not read as healthy.  B (+22 more)

### Community 47 - "ats.py"
Cohesion: 0.15
Nodes (23): download_filename(), Download names an employer folder can still be read a week later.  ``output/appl, Reduce free text to ``[A-Za-z0-9-_]``, or to "" if nothing survives.      Accent, Build ``<Company>_<Type>_<Nom>.<ext>`` for one artefact.      Falls back to the, slugify(), _client(), Connection, Path (+15 more)

### Community 48 - "AnthropicTailoringAdvisor"
Cohesion: 0.10
Nodes (29): extract_template_context(), Read all editable choices without altering the template., bank(), _plan(), Task 40 amendment: bullets had a floor and no ceiling.  _validate_experience_com, The ceiling does not soften the other direction., Floor beats ceiling; a template row count under it cannot make a bad CV., End to end: the renderer inserts what survived, not what was asked for. (+21 more)

### Community 49 - "OpenAITailoringAdvisor"
Cohesion: 0.16
Nodes (20): _all_template_paths(), _bullet_budget(), _claim_length(), _normalized(), _project_desc_budget(), _project_desc_rows(), An experience claim has to fit the CV's one line.  The renderer inserts a select, The widest project description any template already renders. (+12 more)

### Community 51 - "test_tech_additions.py"
Cohesion: 0.15
Nodes (26): bank(), _offer(), LogCaptureFixture, Zone 3 may add a keyword, but only one he has and the offer asked for., Reorder-only remains the default and the common case., Genuinely his, but padding: the offer did not ask for it., Presence in the bank is necessary, never sufficient., Derived from the file, not a magic number. (+18 more)

### Community 52 - "load_fact_bank"
Cohesion: 0.11
Nodes (35): _boolean(), build_cv_title(), CertificationFact, _claim_list(), EducationFact, _entry_claim(), FactBankError, LanguageFact (+27 more)

### Community 53 - "CompanyRecord"
Cohesion: 0.14
Nodes (33): clean_description(), Collapse the whitespace a copied page carries, and keep the rest., _client(), _fake_score(), _offer(), Connection, Task 43 item 1: an offer description captured from an open page.  LinkedIn and I, Stand-in for jobpilot.scoring.score, which imports torch.      Writes a match_sc (+25 more)

### Community 54 - "labonnealternance.py"
Cohesion: 0.12
Nodes (15): _InventsThenRecovers, Connection, LogCaptureFixture, Path, Task 37 item 2: give the unknown-id retry something to work with.  An unknown fa, Cites an id that exists nowhere, for a chosen number of attempts., One retry was not enough for this failure. Two is., Keeps making a provenance error that has no deterministic repair. (+7 more)

### Community 55 - "ingest_source"
Cohesion: 0.13
Nodes (16): load_cv_profile(), Load the committed CV profile, failing loudly rather than defaulting., _canonicalize_prose(), _justification(), Any, Normalize model punctuation that the document contract forbids.      This is a l, Renderer-owned CV header location; the advisor has no say in it.      Prefers th, resolve_header_location() (+8 more)

### Community 56 - "pick_variant"
Cohesion: 0.12
Nodes (17): BrowserLauncher, _ConfirmationBaseline, launch_wttj_application(), _Locator, _Page, PrefillPlan, Protocol, The actions selected from a page's current HTML fixture/markup. (+9 more)

### Community 57 - "test_fact_id_resolution.py"
Cohesion: 0.15
Nodes (31): approve_application(), Any, Connection, Record human approval, transition, and generate through one shared path.      ``, invention_report(), How often the advisor cites an id that does not exist, and whether it recovers., Connection, Path (+23 more)

### Community 58 - "test_letter_locked_fields.py"
Cohesion: 0.18
Nodes (19): bank(), _letter(), _offer(), A letter is prose about a career; a CV is slots the renderer fills., Naming a real-sounding employer he never had is a fabrication, not prose., The renderer injects the address block; the body repeating it is a bug., Otherwise the test above would prove nothing about scope., The bank's own text names nothing it should not; selection is the check. (+11 more)

### Community 59 - "launch_application_assist"
Cohesion: 0.08
Nodes (24): BackfillResult, enrich_offer(), is_synthesized(), is_thin(), OfferRecord, Synthesise matchable text for offers that arrive with no description.  Job-alert, Replace a thin description in place; richer descriptions are left alone.      Ca, True when `description` was produced by this module. (+16 more)

### Community 60 - "test_letter_quality.py"
Cohesion: 0.22
Nodes (17): _default_letter(), french_de_elision(), Return « de <noun> » or « d'<noun> », applying French elision.      Elides befor, _render_sourced_letter(), _validate_letter_body(), _letter(), _offer(), Letter quality: French elision and the 'Entreprise' placeholder rejection. (+9 more)

### Community 61 - "test_mailer.py"
Cohesion: 0.12
Nodes (21): backfill_descriptions_cmd(), daemon_cmd(), init_db_cmd(), Synthesise descriptions for stored offers whose text is too thin to score., Create the database from schema.sql, run migrations, seed sources., Run ingest + score on a loop (Ctrl-C to stop)., _env_bool(), get_settings() (+13 more)

### Community 62 - "models.py"
Cohesion: 0.25
Nodes (18): daemon_status(), Report daemon liveness from the heartbeat file, or admit it is unknown., _client(), fixture_bank(), Connection, MonkeyPatch, Path, TestClient (+10 more)

### Community 63 - "reparse_alerts"
Cohesion: 0.23
Nodes (15): current_status(), _generation_failed_detail(), Any, Connection, LogCaptureFixture, Path, One automatic advisor retry, fed only the validator's own error text., Re-calling on a 429 or a bad key is not feedback, it is a retry storm. (+7 more)

### Community 64 - "test_designation_numbers.py"
Cohesion: 0.09
Nodes (35): LookupError, ApplicationNotFoundError, ApplicationNotQueuedError, ApplyOutcome, archive_artifacts(), GenerationInFlight, InteractiveAdvisorRequired, Path (+27 more)

### Community 65 - "test_fact_id_consistency.py"
Cohesion: 0.20
Nodes (15): bank(), _bank_payload(), Path, Task 35 item 2: a fact bank whose claim ids do not extend their entry is invalid, The real bank must satisfy the rule the loader now enforces., This is the exact shape the Baïfall entry had., Projects have the same shape as experience, so they get the same rule., `experience.baifallX` starts with the entry id as a STRING but is a     differen (+7 more)

### Community 66 - "review.py"
Cohesion: 0.17
Nodes (19): Source, _AlertSource, _ingest_then_import(), Connection, OfferRecord, Task 43 item 5: an imported description is never overwritten.  The user opens th, `force` exists to re-compose rows the normal pass skips. That widening     must, The guard must be `imported_at`, not an accident that stopped the     backfill w (+11 more)

### Community 67 - "ingest_source"
Cohesion: 0.08
Nodes (54): CatalogueEntry, default_catalogue(), load_variant_catalogue(), _parse_criteria(), _parse_shortcuts(), Path, The CV catalogue offered to the advisor when it selects a variant.  The selectio, Read the two-column selection table, skipping its header and separator. (+46 more)

### Community 68 - "_AnchorParser"
Cohesion: 0.23
Nodes (14): _backfill_company_source(), _drain(), ingest_source(), IngestResult, _insert_offer(), Connection, Ingestion orchestrator: pull normalized records from a Source into the DB.  Idem, INSERT OR IGNORE one offer. Returns True if a new row was created. (+6 more)

### Community 69 - "test_preview.py"
Cohesion: 0.23
Nodes (19): _fake_clone(), _git(), CompletedProcess, Path, Task 41: one command after a merge, and it refuses rather than half-updates.  sc, The loud refusal. A fast-forward carries uncommitted work with it., The point of the conditions: the two slow steps cost nothing here., Kickstarting the agents is unconditional: new code is only running once     the (+11 more)

### Community 70 - "vocabulary.py"
Cohesion: 0.17
Nodes (17): live_db(), _Observed, _offer(), Connection, Exception, Path, Task 41 follow-up: the write lock is not held across the network.  Task 41 put W, Draining buys the lock back without giving up atomicity — which is what     comm (+9 more)

### Community 71 - "UnknownFactIdError"
Cohesion: 0.10
Nodes (33): parse_linkedin(), Extract jobs from a LinkedIn job-alert email., _card_html(), LogCaptureFixture, Structural parsing of job-alert cards (Task 20).  Every fixture here is shaped a, The same four values models.REMOTE_POLICIES defines for every source., Indeed writes "Villeneuve-d'Ascq (59)" — the postcode is not a workplace., Whatever position the chrome occupies, it must not be stored. (+25 more)

### Community 72 - "Baifall Dream Stage - Reference Document (v3)"
Cohesion: 0.17
Nodes (11): Baifall Dream Stage - Reference Document (v3), Bloc HTML de reference (3 bullets), Bullet 1 (commun, accompli) - 167 car., rendu sur 2 lignes, Bullet 2 (commun, nominal, perimetre complet) - 127 car., 1 ligne, Bullet 3 : declinaisons par variante, Context, Principe v3 : perimetre nominal complet, Regle pour la date (+3 more)

### Community 73 - "test_facts.py"
Cohesion: 0.05
Nodes (81): ApplicantProfile, The non-secret contact values entered into an ATS form., build_prefill(), discard_mapping(), fields_from_html(), FormField, FormLearningError, FormMapping (+73 more)

### Community 74 - "test_progress.py"
Cohesion: 0.09
Nodes (34): _csv(), facts_cmd(), init_profile_cmd(), _langs(), mark_sent_cmd(), Pass on an application: move queued -> skipped., Record an externally-submitted application as sent (ready -> applied)., Interactively fill the profile singleton and seed cv_variants. (+26 more)

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
Cohesion: 0.22
Nodes (8): CLAUDE.md - JobPilot project constitution, Engineering standards, graphify, Interaction rules for Claude Code, Legal and safety rails (do not remove or weaken), Non-negotiable architecture, Scope of rule 11, What this project is

### Community 79 - "AGENTS.md - JobPilot project constitution"
Cohesion: 0.29
Nodes (6): AGENTS.md - JobPilot project constitution, Engineering standards, Interaction rules for Codex, Legal and safety rails (do not remove or weaken), Non-negotiable architecture, What this project is

### Community 80 - "test_valid_sourced_advice_completes_the_shared_generation_path"
Cohesion: 0.29
Nodes (17): _application(), _client(), Connection, Task 43 item 3: pasting the description is a first-class path.  Not a fallback f, The card is 113 characters and the CV was tailored against it. Saying so     is, A rejected paste must not look like a lost page, and must not have     replaced, One endpoint, two representations. The JSON caller sends no     application_id a, Not conditional on the extension having failed, and not conditional on     the s (+9 more)

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
Cohesion: 0.13
Nodes (16): Connection, Path, Nothing is weakened: a fabrication ends the run exactly as before., An invented figure is recoverable — the retry is handed the real ones —     but, test_a_fatal_gate_still_aborts(), test_a_recoverable_gate_with_no_degradation_escalates_to_fatal(), test_an_advisory_gate_never_blocks(), End to end, on the failure that killed applications 25 and 28.      The live re- (+8 more)

### Community 88 - "profile.py"
Cohesion: 0.06
Nodes (59): Return capability-tier tokens that have tripped generations, by frequency., vocabulary_misses(), GenericVocabularyError, load_generic_vocabulary(), parse_rejections(), Path, StrEnum, ValueError (+51 more)

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
Cohesion: 0.17
Nodes (22): _city(), _company_name(), _contract_type(), _domain(), _first(), map_company(), map_offer(), Any (+14 more)

### Community 110 - "test_designation_numbers.py"
Cohesion: 0.17
Nodes (16): bank(), _in_bank(), LogCaptureFixture, A standard's digits name a thing; a metric's digits measure one., The anti-fabrication guarantee is not weakened by designation handling., Only the designation's own span is exempt from the number rule., Judge as the letter is judged: no entry, so the whole bank answers., Looking like a standard is not evidence of holding one. (+8 more)

### Community 111 - "_AnchorParser"
Cohesion: 0.06
Nodes (66): allowed_numbers(), _bank_parts(), _generated_bullets(), letter_scope(), _normalized_number(), _offer_identity(), _organisation_names(), Everything the verified bank says the candidate has actually touched.      Only (+58 more)

### Community 112 - "Connection"
Cohesion: 0.14
Nodes (13): attempt(), describe(), fromSelectors(), hostKey(), largestTextBlock(), send(), textOf(), toast() (+5 more)

### Community 113 - "apply_matching_profile_cmd"
Cohesion: 0.15
Nodes (16): The tier this failure carries HERE.      An unclassified error is fatal. That de, A selected fact must be a real, reviewed fact OF THAT ENTRY.      This is the wh, tier_for(), _validate_selection(), _raised(), Task 39 item 3: one funnel, three outcomes.  152 raise sites all meant "abort",, The one gate stopping a CV experience entry at the offer's employer., The safety property of the whole task: forgetting to classify a gate     keeps t (+8 more)

### Community 114 - "test_variant_selection.py"
Cohesion: 0.09
Nodes (27): _advise(), ambiguous_bank(), bank(), _offer(), Any, LogCaptureFixture, Path, Citation ids are matched tolerantly; what may be claimed is unchanged. (+19 more)

### Community 115 - "labonnealternance.py"
Cohesion: 0.13
Nodes (26): FastAPI, RefreshRunner, create_app(), Build the local dashboard, with injectable generation collaborators for tests., application_detail(), event_history(), import_supersedes_documents(), offer_freshness() (+18 more)

### Community 116 - "test_profile_domain_anchor.py"
Cohesion: 0.15
Nodes (17): _offer(), _OneShotProfileOrphan, Connection, Path, _Toolchain, Systemic recovery at the generated-prose and document-layout boundaries., Naming the employer is what a motivation letter does.      The rule was never lo, A profile-only layout regression that disappears with template wording. (+9 more)

### Community 117 - "tracker.py"
Cohesion: 0.20
Nodes (21): _offer(), _openai_response(), _plan_payload(), Any, Connection, MonkeyPatch, Path, _queued_application() (+13 more)

### Community 118 - "_TextParser"
Cohesion: 0.13
Nodes (7): letter_plain_text(), open_manually(), Path, Strip a generated letter's markup down to what a human would paste., The generated letter as plain text, or '' when it was never generated., The manual_open route: open the offer, copy the letter, submit nothing.      A l, _TextParser

### Community 119 - "FormField"
Cohesion: 0.07
Nodes (39): apply_cmd(), invention_report_cmd(), queue_cmd(), Re-derive company / city / workplace / easy-apply for stored alert offers., Clear stored match_scores so the next `score` run re-evaluates those offers., List queued applications, newest posting first.      Same ordering and the same, Approve an application and generate its tailored application documents., Show a quick snapshot of the pipeline. (+31 more)

### Community 120 - "test_preview.py"
Cohesion: 0.15
Nodes (20): Row, _create_offer(), find_offer_by_url(), import_offer_description(), ImportResult, OfferImportError, Any, Connection (+12 more)

### Community 121 - "Any"
Cohesion: 0.14
Nodes (19): annotate(), drop_stale(), Attach a ``freshness`` mapping to every row that selected the columns., Filter annotated rows, returning what is kept and how many were hidden.      Hid, counts(), Any, Connection, datetime (+11 more)

### Community 124 - "_reject_unsupported_tokens"
Cohesion: 0.22
Nodes (16): _approve(), Connection, LogCaptureFixture, Path, The asset file calls these false positives outside a full render., Task 39: the last hard position of the orphan gate went advisory.      It cost t, The reliable control, per the asset file, so it never becomes advisory., test_a_clean_generation_records_no_orphan_warning() (+8 more)

### Community 125 - "gate"
Cohesion: 0.16
Nodes (21): get_or_create_company(), CompanyRecord, Yield companies likely to hire (optional; default: none)., _no_real_sleeping(), Connection, MonkeyPatch, Backoff between retries is real seconds; the test suite must not spend them., Only fetch_companies() produces outreach targets, not offer side effects. (+13 more)

### Community 126 - "Connection"
Cohesion: 0.07
Nodes (33): _fact_id_key(), _guessed_section(), nearest_entry_claim_ids(), Raised when a citation matches no fact id, even after normalisation.      ``sect, Fold separator and case differences, and nothing else, for comparison., Map a cited id onto a real fact id, accepting only unambiguous matches.      Mat, The entry a bad citation came closest to naming, and its real claim ids.      Ne, The section the citation was aiming at, read from its own prefix. (+25 more)

### Community 128 - "Path"
Cohesion: 0.17
Nodes (12): _is_tracking(), normalize_offer_url(), Canonical form of an offer URL, for matching one posting to itself.      Scheme, The case the whole feature turns on. These are the same posting., The reason the rule is a denylist and not "drop the query string".      Indeed p, Matching just fails and the offer is created, which is recoverable., test_an_alert_link_and_the_same_page_in_a_browser_are_one_offer(), test_an_indeed_job_key_survives_normalisation() (+4 more)

### Community 129 - "test_bullet_ceiling.py"
Cohesion: 0.07
Nodes (41): derive_fields(), _Derived, Re-derive alert card fields (company / city / workplace / easy-apply) in place., Re-derive one offer's card fields from the text that was stored for it.      Pur, _AlertAnchor, _AnchorParser, _anchors(), _Card (+33 more)

### Community 130 - "score"
Cohesion: 0.09
Nodes (39): apply_matching_profile(), load_matching_profile(), MatchingProfile, Write the vocabulary onto the profile singleton. Returns {field: (before, after), The scoring vocabulary, committed to git rather than typed once.      These thre, Load the committed matching vocabulary, failing loudly rather than defaulting., Connection, Path (+31 more)

### Community 131 - "apply_matching_profile"
Cohesion: 0.10
Nodes (35): SentenceTransformer, apply_matching_profile_cmd(), Connection, _queue_snapshot(), Apply config/matching_profile.yaml and report what it changed.      Re-scoring i, Count what currently clears the bar, for an honest before/after., Re-evaluate every offer against the new vocabulary.      ``jobpilot score`` only, _rescore_all() (+27 more)

### Community 132 - "observable_controls"
Cohesion: 0.09
Nodes (32): _Control, _ControlParser, _controls_from_html(), _css_attribute_value(), FillAction, _first_matching_selector(), _Form, _FormParser (+24 more)

### Community 133 - "_bullets"
Cohesion: 0.22
Nodes (16): _alert_source_clause(), Connection, Restrict to one alert source, or to all of them when none is named., Re-derive company / city / workplace / easy-apply for stored alert offers., reparse_alerts(), ReparseResult, Connection, The card line survived in companies.name; the city held only chrome. (+8 more)

### Community 134 - "test_dedup.py"
Cohesion: 0.19
Nodes (14): _extract_profile_domain(), _profile_of(), Path, Task 40: the domain phrase is found by its own marker, not by its neighbours.  _, Not just the wordings we ship: any of them, including ones nobody wrote yet., A rewrite that dropped it would break the next read instead of this one., The ±15-character layout budget must not shift under it., The bug. This raised "template profile domain phrase not found". (+6 more)

### Community 135 - "update.sh"
Cohesion: 0.60
Nodes (3): changed_since_pull(), die(), update.sh script

### Community 136 - "scheduler_status"
Cohesion: 0.10
Nodes (38): age_in_days(), describe(), Freshness, _label(), _parse(), parse_timestamp(), Any, datetime (+30 more)

### Community 137 - "run_dashboard"
Cohesion: 0.14
Nodes (7): MissingCredentialError, RuntimeError, Raised when a required secret is absent. We ask; we never silently mock., RateLimiter, Minimum-delay-per-domain limiter. Blocks until the next call is allowed., DaemonStatus, What can honestly be said about the daemon, and nothing more.

### Community 138 - "mappings_for"
Cohesion: 0.14
Nodes (13): _plan(), Path, Task 41: the header location is found by its own marker, not by its neighbours., A template re-exported with a plain pin and a different separator.      Under th, The rewrite site and the two read sites agree, on real tailored output., The header is a fixed-width line; the span must not consume any of it., The header location is renderer-owned: it comes from the offer's city., The premise of the fix, asserted rather than assumed.      If this ever fails th (+5 more)

### Community 139 - "vocabulary.py"
Cohesion: 0.67
Nodes (3): _F, gate(), Label what this function refuses, and what refusing costs.      Attached to the

### Community 140 - "GmailIMAP"
Cohesion: 0.22
Nodes (12): _consecutive_failures(), _last_runs(), Any, Connection, Row, Leading failures only: one success resets the streak., Last recorded run per enabled source, with what that run actually did.      ``la, Everything the queue page shows about scheduled ingestion. (+4 more)

### Community 141 - "send_application_email"
Cohesion: 0.33
Nodes (8): source_id(), _offer(), Connection, content_hash dedup + INSERT OR IGNORE behavior., test_same_content_hash_collapses_to_one_row(), test_same_external_id_ignored(), It is called inside the caller's transaction, on both paths., test_record_run_does_not_commit_on_its_own()

### Community 142 - "_Advisor"
Cohesion: 0.20
Nodes (9): content_scripts, description, host_permissions, manifest_version, name, version, https://*.indeed.fr/*, https://*.linkedin.com/* (+1 more)

### Community 144 - "ingest_source"
Cohesion: 0.20
Nodes (9): ApplicationGenerationError, A redacted generation failure suitable for CLI and dashboard display., _CompleteAdvisor, _IncompleteAdvisor, Drops the current stage, exactly as the observed failure did., Returns the reference selection payload, unchanged., _SelectingAdvisor, _InteractiveShapedAdvisor (+1 more)

### Community 146 - "test_ingest_idempotent.py"
Cohesion: 0.38
Nodes (8): FakeSource, Connection, Re-running ingest must never duplicate rows (constitution idempotency rule)., _sample(), test_company_deduped_across_offers_and_runs(), test_first_run_inserts_all(), test_last_run_at_updated(), test_second_run_inserts_nothing()

### Community 149 - "test_registry.py"
Cohesion: 0.22
Nodes (15): ingest_cmd(), Fetch offers from a source (or all sources) into the database., available_sources(), enabled_sources(), _enablement(), is_enabled(), Maps source names (rows in the sources table) to Source implementations.  Keepin, Read config/sources.yaml. Unlisted sources default to enabled. (+7 more)

### Community 150 - ".__init__"
Cohesion: 0.50
Nodes (4): import_origin_allowed(), True when `origin` may POST to IMPORT_PATH.      Host-suffix matching, so ``www., test_every_other_origin_is_rejected(), test_the_origins_the_feature_needs_are_allowed()

### Community 151 - "observable_controls"
Cohesion: 0.50
Nodes (4): ColdSendDisabled, A rail (suppression list or daily cap) refuses the send. Not a failure., Live cold sending is disabled by configuration., SendBlocked

### Community 153 - "counts"
Cohesion: 0.07
Nodes (30): Logger, menubar_cmd(), Show ready/queued counts in the macOS menu bar (optional extra)., Put text on the system clipboard, or say plainly that it could not.  The manual_, get_logger(), Central logging setup. Library code logs here; it never uses print()., Idempotent: attaches a rotating file handler + console handler once., setup_logging() (+22 more)

### Community 154 - "suppress_email"
Cohesion: 0.67
Nodes (3): Add an address to the cold-mail suppression list (honored before sends)., suppress_cmd(), suppress_email()

## Knowledge Gaps
- **171 isolated node(s):** `Requirements`, `macOS / Linux`, `Windows PowerShell`, `Configuration`, `CV variant selection` (+166 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **25 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `current_status()` connect `reparse_alerts` to `_candidate_name`, `dashboard.py`, `run_dashboard`, `test_routing.py`, `mailer.py`, `test_skim.py`, `launch_wttj_application`, `_FakePage`, `generate_application`, `test_contacts.py`, `test_cv_completeness.py`, `test_cold_outreach.py`, `_FakePage`, `labonnealternance.py`, `test_fact_id_resolution.py`, `test_designation_numbers.py`, `ingest_source`, `test_progress.py`, `CompanyRecord`, `test_profile_domain_anchor.py`, `tracker.py`, `_reject_unsupported_tokens`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `test_mailer.py` to `_client`, `observable_controls`, `apply_matching_profile`, `dashboard.py`, `run_dashboard`, `test_routing.py`, `mailer.py`, `get_settings`, `test_skim.py`, `test_registry.py`, `SourcedBullet`, `wttj.py`, `launch_wttj_application`, `counts`, `test_sourcing_targets_changes_no_sending_gate`, `generate_application`, `test_email_alerts.py`, `Settings`, `.from_mapping`, `test_cold_outreach.py`, `pick_variant`, `test_fact_id_resolution.py`, `test_progress.py`, `_TextParser`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `get_logger()` connect `counts` to `Request`, `test_bullet_ceiling.py`, `apply_matching_profile`, `observable_controls`, `dashboard.py`, `Path`, `mailer.py`, `test_skim.py`, `contacts.py`, `test_registry.py`, `SourcedBullet`, `wttj.py`, `.from_mapping`, `test_mailer.py`, `test_designation_numbers.py`, `_AnchorParser`, `test_facts.py`, `test_progress.py`, `Path`, `Any`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 62 inferred relationships involving `Settings` (e.g. with `ApplicantProfile` and `ApplyAdapter`) actually correct?**
  _`Settings` has 62 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `current_status()` (e.g. with `test_a_fatal_gate_still_aborts()` and `test_a_recoverable_gate_with_no_degradation_escalates_to_fatal()`) actually correct?**
  _`current_status()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `_payload()` (e.g. with `_plan()` and `_plan()`) actually correct?**
  _`_payload()` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `TailoringError` (e.g. with `ExperienceFact` and `FactBank`) actually correct?**
  _`TailoringError` has 24 INFERRED edges - model-reasoned connections that need verification._