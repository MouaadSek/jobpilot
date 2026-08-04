# Graph Report - jobpilot  (2026-08-04)

## Corpus Check
- 166 files · ~203,704 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3618 nodes · 9569 edges · 143 communities (123 shown, 20 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 568 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `11f37744`
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
- test_profile_domain_anchor.py
- test_only_two_of_the_five_concentrix_facts_carry_the_figure
- .__init__
- _Advisor

## God Nodes (most connected - your core abstractions)
1. `Settings` - 117 edges
2. `current_status()` - 99 edges
3. `_payload()` - 92 edges
4. `TailoringError` - 90 edges
5. `load_fact_bank()` - 81 edges
6. `FactBank` - 73 edges
7. `OfferRecord` - 69 edges
8. `_Toolchain` - 69 edges
9. `OfferContext` - 67 edges
10. `get_settings()` - 66 edges

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

## Communities (143 total, 20 thin omitted)

### Community 0 - "test_downloads.py"
Cohesion: 0.05
Nodes (42): BaseException, Operation, ProgressRegistry, Any, datetime, What the dashboard is doing right now, readable while it does it.  ``RefreshRunn, Update a running operation. A key that is not running is ignored., Close an operation. The first outcome recorded wins.          A handled failure (+34 more)

### Community 1 - "Request"
Cohesion: 0.08
Nodes (55): Resolve one archived artefact, with the same discipline as the live one.      De, _safe_archive_path(), _archives_for(), Generation, is_archive_stamp(), library_entries(), LibraryEntry, _mtime_iso() (+47 more)

### Community 2 - "_candidate_name"
Cohesion: 0.07
Nodes (86): _client(), _days_ago(), _events(), _no_advisor_client(), _offer_application(), Connection, MonkeyPatch, Path (+78 more)

### Community 3 - "_client"
Cohesion: 0.14
Nodes (17): _application_for_assist(), _application_for_wttj(), ApplyAssistError, AssistResult, _fallback(), launch_application_assist(), Connection, Row (+9 more)

### Community 4 - "create_app"
Cohesion: 0.09
Nodes (21): enrich_offer(), is_thin(), Replace a thin description in place; richer descriptions are left alone.      Ca, True when a description is too short to be worth embedding on its own., content_hash(), OfferRecord, sha256(lower(title + company + first 500 chars of description)).      This is th, One normalized offer, ready to insert into the offers table. (+13 more)

### Community 5 - "dashboard.py"
Cohesion: 0.05
Nodes (104): Match, Pattern, FactBank, _add_tech_additions(), _add_tech_keywords(), _advisor_fact_context(), _bank_parts(), _cap_experience_selection() (+96 more)

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
Cohesion: 0.11
Nodes (36): is_professional_address(), True only for well-formed addresses NOT on a personal free-provider domain., Whether a named mailbox on a professional domain needs extra approval., requires_personal_confirmation(), _as_utc(), ColdEmailPreparation, ColdSendDisabled, daily_cap_reached() (+28 more)

### Community 10 - "validate_cv.py"
Cohesion: 0.06
Nodes (53): check_orphans(), find_regressions(), Path, Return orphan metrics that are new or materially worse than the template., format_date(), main(), build_letter_html(), detect_github() (+45 more)

### Community 11 - "get_settings"
Cohesion: 0.05
Nodes (95): ExperienceFact, FactClaim, One atomic statement that generated content may cite., GenerationWarning, One thing the reviewer is being asked to check by eye., CvProfile, Renderer-owned candidate facts injected into every generated CV., The location printed in the CV header when the offer yields none. (+87 more)

### Community 12 - "connect"
Cohesion: 0.09
Nodes (36): _extract_profile_domain(), Apply the mechanical contract and encoding rules to a chosen slug.      These ar, The contract line an adapted alternance CV must carry., The stage contract line to fall back to, built from what is known.      Determin, Preserve a valid contract phrase; replace only a rejected one.      Same shape a, _resolve_stage_contract_phrase(), _stage_contract_fallback(), _validate_stage_contract_phrase() (+28 more)

### Community 13 - "test_descriptions.py"
Cohesion: 0.10
Nodes (50): backfill_descriptions(), BackfillResult, clear_match_scores(), is_synthesized(), Connection, Synthesise matchable text for offers that arrive with no description.  Job-alert, Return an SQL fragment + params restricting a query to one source., Regenerate synthesised descriptions for stored offers whose text is thin.      I (+42 more)

### Community 15 - "apply_assist.py"
Cohesion: 0.14
Nodes (32): _client(), _days_ago(), _offer_application(), Connection, MonkeyPatch, TestClient, Task 42: what the four lists do with recency, end to end.  tests/test_freshness., The bug: a three-week 0.72 sat above a one-day 0.61 and stayed there. (+24 more)

### Community 16 - "test_skim.py"
Cohesion: 0.09
Nodes (51): _create_application(), ignore_offer(), promote_offer(), Connection, datetime, Row, ValueError, Offers that passed the hard filter and scored below the queue threshold.      An (+43 more)

### Community 17 - "contacts.py"
Cohesion: 0.11
Nodes (34): _candidate_name(), ContactCandidate, discover_and_store(), DiscoverySource, draft_cold_email(), draft_linkedin_note(), _get_or_create_cold_application(), is_suppressed() (+26 more)

### Community 18 - "JobPilot — Codex Handoff (complete A-to-Z)"
Cohesion: 0.04
Nodes (45): 10. HARD REJECTIONS (offers the pipeline should auto-skip), 11. API REFERENCES, 12. DESIGN PRINCIPLES (non-negotiable), 13. ENV VARS (.env), 14. GITHUB PUSH (do this FIRST, before any Codex work), 15. CODEX TASK BREAKDOWN (suggested order), 16. BAIFALL DREAM STAGE REFERENCE, 17. SCRIPTS REFERENCE (+37 more)

### Community 19 - "RefreshRunner"
Cohesion: 0.06
Nodes (46): apply_cmd(), backfill_descriptions_cmd(), init_db_cmd(), menubar_cmd(), Synthesise descriptions for stored offers whose text is too thin to score., Clear stored match_scores so the next `score` run re-evaluates those offers., Approve an application and generate its tailored application documents., Create the database from schema.sql, run migrations, seed sources. (+38 more)

### Community 20 - "_payload"
Cohesion: 0.16
Nodes (31): _project(), The advisor selects; the renderer inserts the bank's wording unchanged., The contract has no field for prose, so a writing advisor fails loudly., Only the entry's own facts, so a skill id cannot become a bullet., The phrase is short, but it is still generated, so the tiers still read it., Cross-entry contamination is now unrepresentable rather than policed., _render(), test_a_category_word_in_the_domain_phrase_is_free() (+23 more)

### Community 21 - "wttj.py"
Cohesion: 0.10
Nodes (41): _city(), _contact_email(), _contract(), _first(), map_hit(), _org(), _prose(), Any (+33 more)

### Community 22 - "SourcedBullet"
Cohesion: 0.13
Nodes (15): ConnectionFactory, Event, _production_connection(), Any, Connection, Single-flight ingest + score pass driven from the dashboard., Block until the running refresh finishes. Tests use this, not sleeps., Claim the single flight and hand the work to a background thread. (+7 more)

### Community 23 - "france_travail.py"
Cohesion: 0.09
Nodes (29): _delay(), Call fn(); retry on transient HTTP errors with full-jitter exponential backoff., with_backoff(), _first_nonempty(), FranceTravailSource, _map_contact_email(), _map_contract(), _map_duration_months() (+21 more)

### Community 24 - "test_provenance_tiers.py"
Cohesion: 0.08
Nodes (37): bank(), _in_bank(), _offer(), Three kinds of token, three different burdens of proof., Not even the widest scope can support it., The reader has to be able to search for it, or add it to the config., Task 26's handling survives as the digit-shaped corner of tier 2., Presence in the bank is necessary for tier 2, never sufficient. (+29 more)

### Community 25 - "launch_wttj_application"
Cohesion: 0.22
Nodes (28): Send one approved cold draft after rechecking every legal rail., send_cold_email(), current_status(), _cold_draft(), _configure_dashboard(), _dashboard_client(), _event_rows(), Connection (+20 more)

### Community 26 - "Dashboard"
Cohesion: 0.05
Nodes (39): Actualiser les offres (refresh from the page), Always up, without a terminal, Architecture (summary), ATS application assist (prefill only), Background scheduling, CI, Cold outreach sending (disabled by default), Commands (+31 more)

### Community 27 - "_FakePage"
Cohesion: 0.10
Nodes (21): ApplyAdapter, _BaseAdapter, GreenhouseAdapter, LeverAdapter, Common adapter interface for a best-effort ATS prefill., Shared plan building and non-submitting form interaction., SmartRecruitersAdapter, _FakeLauncher (+13 more)

### Community 28 - "cli.py"
Cohesion: 0.17
Nodes (32): Any, Every offer application, optionally narrowed to one status.      ``include_stale, Export exactly the visible rows, in the visible column order., to_csv(), tracker_rows(), _application(), _client(), Connection (+24 more)

### Community 29 - "test_desktop_shell.py"
Cohesion: 0.07
Nodes (40): CaptureFixture, dashboard_already_running(), Whether something is already listening on the dashboard's port.      A connect p, The menu bar text. Short: it competes with every other item up there., title(), _bound_port(), _fake_macos(), _module_level_imports() (+32 more)

### Community 30 - "generate_application"
Cohesion: 0.09
Nodes (20): date, _check_orphans(), _contains_generated_orphan(), DocumentToolchain, _french_date(), generate_application(), CompletedProcess, Path (+12 more)

### Community 31 - "test_contacts.py"
Cohesion: 0.10
Nodes (27): ModuleType, JobPilot: personal job application pipeline for the French IT/cybersecurity mark, _application(), _ConnectionProxy, Connection, Exception, Path, CLI coverage for offer document generation and cold-application approval. (+19 more)

### Community 32 - "test_email_alerts.py"
Cohesion: 0.09
Nodes (43): Message, GmailIMAP, html_of(), LinkedInAlertSource, Minimal read-only Gmail IMAP client., Fetch recent mail sent from `domains` (or any of their subdomains).          The, Return the best HTML (or plain-text) body of an email message., Return the lowercased domain of the address in a `From` header.      Parses the (+35 more)

### Community 33 - "test_labonnealternance.py"
Cohesion: 0.08
Nodes (54): list_outreach_targets(), Companies an ingestion source flagged as likely to hire an alternant.      These, get_or_create_company(), _fixture(), _no_real_sleeping(), _NoWait, Connection, LogCaptureFixture (+46 more)

### Community 34 - "_Toolchain"
Cohesion: 0.08
Nodes (26): HTTPStatusError, MissingCredentialError, RuntimeError, Raised when a required secret is absent. We ask; we never silently mock., CompanyRecord, Normalized DTOs that every source emits, decoupled from source-specific JSON., RateLimiter, Minimum-delay-per-domain limiter. Blocks until the next call is allowed. (+18 more)

### Community 35 - "email_alerts.py"
Cohesion: 0.08
Nodes (28): Every id the advisor may cite, flattened out of the context it was given.      D, valid_fact_ids(), facts(), _nested_ids(), Task 37 item 1: tell the advisor the set of ids is closed.  `skill.rules.sigma`, Task 37 must not have quietly added Sigma to make the failure go away., Defensive: a template with no projects must not raise here., The exact mechanism that produced skill.rules.sigma. (+20 more)

### Community 36 - "test_alert_card_fields.py"
Cohesion: 0.11
Nodes (29): as_dicts(), clear_warnings(), _decode(), Any, Connection, What a generation had to degrade, recorded where the reviewer will see it.  Task, Gate names per application, for the library and tracker markers.      One query, Template-facing shape. (+21 more)

### Community 37 - "Settings"
Cohesion: 0.10
Nodes (21): build_cv_title(), Build the deterministic CV title used after all advisor providers., load_cv_profile(), Load the committed CV profile, failing loudly rather than defaulting., _canonicalize_prose(), _fact_id_list(), _justification(), Any (+13 more)

### Community 38 - "Job Application Pipeline"
Cohesion: 0.06
Nodes (31): Alternance vs Stage, Edge Cases & Principles, Encoding note, Execution Flow, Flag once, then execute:, Generate with the bundled script:, GitHub Exception, Hard rejections (no output): (+23 more)

### Community 39 - "matcher.py"
Cohesion: 0.15
Nodes (28): bonus_score(), cosine(), hard_filter(), keyword_score(), norm(), pick_variant(), Profile, Connection (+20 more)

### Community 40 - "test_cv_completeness.py"
Cohesion: 0.20
Nodes (16): _category_skills(), Any, Structural completeness floor for AI-generated CVs (Task 22).  Selection freedom, Every shipped category line with its raw, non-deduplicated tool list., Task 39 demoted this to advisory.      A tool listed under two categories is cos, _render(), test_duplicate_tool_across_categories_warns_without_blocking(), test_employers_out_of_chronological_order_are_rejected() (+8 more)

### Community 41 - "OfferRecord"
Cohesion: 0.11
Nodes (16): Raised when a citation matches no fact id, even after normalisation.      ``sect, Append the legal ids for the section the model got wrong.      When the citation, UnknownFactIdError, _valid_fact_ids_block(), _BadSourceAdvisor, Cites a prefix-less unknown id first, then whatever the retry was told., Cites an unresolvable id in a letter paragraph, where no section is implied., _RecordingAdvisor (+8 more)

### Community 42 - "test_dashboard_facts_scheduler.py"
Cohesion: 0.07
Nodes (42): derive_fields(), _Derived, Re-derive one offer's card fields from the text that was stored for it.      Pur, _AlertAnchor, _AnchorParser, _anchors(), _Card, _card_fields() (+34 more)

### Community 43 - ".from_mapping"
Cohesion: 0.12
Nodes (29): Decision, RouteId, adapter_for_url(), Auditable outcome of one approved WTTJ dashboard action., Return the owning ATS adapter, if the saved offer URL is recognized., WTTJApplyResult, Remove configured secrets from exception text before display/logging., Settings (+21 more)

### Community 44 - "test_cold_outreach.py"
Cohesion: 0.28
Nodes (17): Combined application + cold-mail sends recorded for today (UTC)., sends_today(), _events(), Connection, EmailMessage, Exception, Path, Application email sending: rails, transitions, and events (mocked SMTP). (+9 more)

### Community 45 - "_FakePage"
Cohesion: 0.23
Nodes (22): launch_wttj_application(), Fill a WTTJ inline form and submit only behind the explicit live gate., _events(), _FakeLauncher, _FakePage, Connection, Path, Row (+14 more)

### Community 46 - "MissingCredentialError"
Cohesion: 0.16
Nodes (30): _client(), _fail(), _Fake, _offer(), Connection, Row, TestClient, Task 41 item 6: a source that has stopped answering must not read as healthy.  B (+22 more)

### Community 47 - "ats.py"
Cohesion: 0.15
Nodes (23): download_filename(), Download names an employer folder can still be read a week later.  ``output/appl, Reduce free text to ``[A-Za-z0-9-_]``, or to "" if nothing survives.      Accent, Build ``<Company>_<Type>_<Nom>.<ext>`` for one artefact.      Falls back to the, slugify(), _client(), Connection, Path (+15 more)

### Community 48 - "AnthropicTailoringAdvisor"
Cohesion: 0.04
Nodes (81): ApplicationGenerationError, A redacted generation failure suitable for CLI and dashboard display., extract_template_context(), OpenAITailoringAdvisor, pick_variant(), Pick the best of 21 variants from missions, then apply contract rules.      Sinc, Read all editable choices without altering the template., OpenAI-compatible Chat Completions adviser. (+73 more)

### Community 49 - "OpenAITailoringAdvisor"
Cohesion: 0.16
Nodes (20): _all_template_paths(), _bullet_budget(), _claim_length(), _normalized(), _project_desc_budget(), _project_desc_rows(), An experience claim has to fit the CV's one line.  The renderer inserts a select, The widest project description any template already renders. (+12 more)

### Community 50 - "resolve_fact_id"
Cohesion: 0.13
Nodes (28): create_app(), Build the local dashboard, with injectable generation collaborators for tests., drop_stale(), Freshness, Filter annotated rows, returning what is kept and how many were hidden.      Hid, How old one offer is, and how sure we are of that., application_detail(), applications_by_status() (+20 more)

### Community 51 - "test_tech_additions.py"
Cohesion: 0.16
Nodes (25): _offer(), LogCaptureFixture, Zone 3 may add a keyword, but only one he has and the offer asked for., Reorder-only remains the default and the common case., Genuinely his, but padding: the offer did not ask for it., Presence in the bank is necessary, never sufficient., Derived from the file, not a magic number., One page matters more than one keyword; the CV is still true without it. (+17 more)

### Community 52 - "load_fact_bank"
Cohesion: 0.11
Nodes (34): _boolean(), CertificationFact, _claim_list(), EducationFact, _entry_claim(), FactBankError, LanguageFact, load_fact_bank() (+26 more)

### Community 53 - "CompanyRecord"
Cohesion: 0.09
Nodes (39): SimpleNamespace, _Client, _offer(), _plan_payload(), Any, Exception, MonkeyPatch, Path (+31 more)

### Community 54 - "labonnealternance.py"
Cohesion: 0.27
Nodes (10): Connection, LogCaptureFixture, Path, One retry was not enough for this failure. Two is., A non-citation rejection keeps exactly the count it had., The extra attempt buys another chance at a real id, never acceptance of a     fa, test_an_interactive_advisor_is_still_never_retried(), test_an_invented_id_recovers_on_the_second_retry() (+2 more)

### Community 55 - "ingest_source"
Cohesion: 0.08
Nodes (32): FastAPI, Request, archive_artifacts(), Path, Move an application's current artefacts aside; return where they went.      Diff, copy_text(), Copy ``text``; return whether it actually landed on the clipboard., _candidate_name() (+24 more)

### Community 56 - "pick_variant"
Cohesion: 0.16
Nodes (11): BrowserLauncher, _ConfirmationBaseline, _Locator, _Page, PrefillPlan, Protocol, The actions selected from a page's current HTML fixture/markup., A launch seam: production opens Playwright, tests supply a stub page. (+3 more)

### Community 57 - "test_fact_id_resolution.py"
Cohesion: 0.13
Nodes (30): ApplyOutcome, approve_application(), Any, Connection, Record human approval, transition, and generate through one shared path.      ``, The result shared by the CLI and dashboard approval surfaces., invention_report(), How often the advisor cites an id that does not exist, and whether it recovers. (+22 more)

### Community 58 - "test_letter_locked_fields.py"
Cohesion: 0.18
Nodes (19): bank(), _letter(), _offer(), A letter is prose about a career; a CV is slots the renderer fills., Naming a real-sounding employer he never had is a fabrication, not prose., The renderer injects the address block; the body repeating it is a bug., Otherwise the test above would prove nothing about scope., The bank's own text names nothing it should not; selection is the check. (+11 more)

### Community 59 - "launch_application_assist"
Cohesion: 0.18
Nodes (11): generation_single_flight(), GenerationInFlight, InteractiveAdvisorRequired, RuntimeError, Raised when a generation is already running for this application., Raised when only the terminal advisor is available to a headless caller.      Th, Claim the one generation slot for ``application_id``, or refuse.      Taken *bef, Two applications must be able to regenerate at the same time. (+3 more)

### Community 60 - "test_letter_quality.py"
Cohesion: 0.24
Nodes (15): french_de_elision(), Return « de <noun> » or « d'<noun> », applying French elision.      Elides befor, _validate_letter_body(), _letter(), _offer(), Letter quality: French elision and the 'Entreprise' placeholder rejection., test_default_letter_elides_poste_before_vowel(), test_default_letter_uses_votre_entreprise_when_company_unknown() (+7 more)

### Community 61 - "test_mailer.py"
Cohesion: 0.05
Nodes (56): LookupError, ApplicationNotFoundError, ApplicationNotQueuedError, Raised when an approval targets an unknown application., Raised when an approval targets an application outside the review queue., add_contact_cmd(), contacts_cmd(), _csv() (+48 more)

### Community 62 - "models.py"
Cohesion: 0.21
Nodes (20): daemon_status(), DaemonStatus, What can honestly be said about the daemon, and nothing more., Report daemon liveness from the heartbeat file, or admit it is unknown., _client(), fixture_bank(), Connection, MonkeyPatch (+12 more)

### Community 63 - "reparse_alerts"
Cohesion: 0.19
Nodes (17): application(), Connection, _generation_failed_detail(), Any, Connection, LogCaptureFixture, Path, _queued_application() (+9 more)

### Community 64 - "test_designation_numbers.py"
Cohesion: 0.19
Nodes (19): IllegalTransition, log_event(), Connection, ValueError, The single authorized writer of applications.status.  Every status transition MU, Raised when a status change is not permitted by the state machine., Append an audit event. Used for status_change, human_approved, email_sent, etc., Move an application to to_status if legal; log a status_change event.      Retur (+11 more)

### Community 65 - "test_fact_id_consistency.py"
Cohesion: 0.20
Nodes (15): bank(), _bank_payload(), Path, Task 35 item 2: a fact bank whose claim ids do not extend their entry is invalid, The real bank must satisfy the rule the loader now enforces., This is the exact shape the Baïfall entry had., Projects have the same shape as experience, so they get the same rule., `experience.baifallX` starts with the entry id as a STRING but is a     differen (+7 more)

### Community 66 - "review.py"
Cohesion: 0.14
Nodes (22): CatalogueEntry, default_catalogue(), load_variant_catalogue(), _parse_criteria(), _parse_shortcuts(), Path, The CV catalogue offered to the advisor when it selects a variant.  The selectio, Read the two-column selection table, skipping its header and separator. (+14 more)

### Community 67 - "ingest_source"
Cohesion: 0.12
Nodes (34): _answer(), _decision(), _offer(), Any, Connection, Exception, LogCaptureFixture, Path (+26 more)

### Community 68 - "_AnchorParser"
Cohesion: 0.19
Nodes (16): CompanyRecord, _backfill_company_source(), _drain(), ingest_source(), IngestResult, _insert_offer(), Connection, OfferRecord (+8 more)

### Community 69 - "test_preview.py"
Cohesion: 0.23
Nodes (19): _fake_clone(), _git(), CompletedProcess, Path, Task 41: one command after a merge, and it refuses rather than half-updates.  sc, The loud refusal. A fast-forward carries uncommitted work with it., The point of the conditions: the two slow steps cost nothing here., Kickstarting the agents is unconditional: new code is only running once     the (+11 more)

### Community 70 - "vocabulary.py"
Cohesion: 0.15
Nodes (18): Exception, Path, live_db(), _Observed, _offer(), Connection, OfferRecord, Source (+10 more)

### Community 71 - "UnknownFactIdError"
Cohesion: 0.10
Nodes (32): parse_linkedin(), Extract jobs from a LinkedIn job-alert email., _card_html(), LogCaptureFixture, Structural parsing of job-alert cards (Task 20).  Every fixture here is shaped a, The same four values models.REMOTE_POLICIES defines for every source., Indeed writes "Villeneuve-d'Ascq (59)" — the postcode is not a workplace., Whatever position the chrome occupies, it must not be stored. (+24 more)

### Community 72 - "Baifall Dream Stage - Reference Document (v3)"
Cohesion: 0.17
Nodes (11): Baifall Dream Stage - Reference Document (v3), Bloc HTML de reference (3 bullets), Bullet 1 (commun, accompli) - 167 car., rendu sur 2 lignes, Bullet 2 (commun, nominal, perimetre complet) - 127 car., 1 ligne, Bullet 3 : declinaisons par variante, Context, Principe v3 : perimetre nominal complet, Regle pour la date (+3 more)

### Community 73 - "test_facts.py"
Cohesion: 0.05
Nodes (79): build_prefill(), discard_mapping(), fields_from_html(), FormField, FormLearningError, FormMapping, infer_profile_field(), mapping_is_complete() (+71 more)

### Community 74 - "test_progress.py"
Cohesion: 0.09
Nodes (39): apply_matching_profile(), load_matching_profile(), MatchingProfile, Path, Write the vocabulary onto the profile singleton. Returns {field: (before, after), The scoring vocabulary, committed to git rather than typed once.      These thre, Load the committed matching vocabulary, failing loudly rather than defaulting., Connection (+31 more)

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
Cohesion: 0.19
Nodes (18): Score all unscored offers and queue those above threshold., score_cmd(), _default_score_pass(), Score exactly as ``jobpilot score`` does, with the model already loaded., Connection, EmbedFn, Score all unscored offers. Returns the number newly queued.      The queue thres, score() (+10 more)

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
Cohesion: 0.20
Nodes (17): test_the_library_and_tracker_mark_a_degraded_application(), _approve(), Connection, LogCaptureFixture, Path, The asset file calls these false positives outside a full render., Task 39: the last hard position of the orphan gate went advisory.      It cost t, The reliable control, per the asset file, so it never becomes advisory. (+9 more)

### Community 88 - "profile.py"
Cohesion: 0.07
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
Nodes (66): _advisor_prompt(), allowed_numbers(), _correction_block(), _generated_bullets(), letter_scope(), _normalized_number(), _offer_identity(), _organisation_names() (+58 more)

### Community 112 - "Connection"
Cohesion: 0.17
Nodes (13): Show the email that would be sent for a ready application, then confirm (y/N)., send_cmd(), _build_message(), build_sender(), EmailSender, EmailMessage, Path, Protocol (+5 more)

### Community 113 - "apply_matching_profile_cmd"
Cohesion: 0.50
Nodes (4): facts_cmd(), Print the provenance fact bank grouped for human review., format_fact_bank(), Render the bank as plain UTF-8 text for human review in the CLI.

### Community 114 - "test_variant_selection.py"
Cohesion: 0.09
Nodes (27): _advise(), ambiguous_bank(), bank(), _offer(), Any, LogCaptureFixture, Path, Citation ids are matched tolerantly; what may be claimed is unchanged. (+19 more)

### Community 115 - "labonnealternance.py"
Cohesion: 0.22
Nodes (16): _alert_source_clause(), Connection, Restrict to one alert source, or to all of them when none is named., Re-derive company / city / workplace / easy-apply for stored alert offers., reparse_alerts(), ReparseResult, Connection, The card line survived in companies.name; the city held only chrome. (+8 more)

### Community 116 - "test_profile_domain_anchor.py"
Cohesion: 0.20
Nodes (8): _OneShotProfileOrphan, Connection, Path, _Toolchain, A profile-only layout regression that disappears with template wording., test_profile_orphan_recovers_with_template_wording(), Returns the reference selection payload, unchanged., _SelectingAdvisor

### Community 117 - "tracker.py"
Cohesion: 0.38
Nodes (8): FakeSource, Connection, Re-running ingest must never duplicate rows (constitution idempotency rule)., _sample(), test_company_deduped_across_offers_and_runs(), test_first_run_inserts_all(), test_last_run_at_updated(), test_second_run_inserts_nothing()

### Community 118 - "_TextParser"
Cohesion: 0.18
Nodes (7): letter_plain_text(), open_manually(), Path, Strip a generated letter's markup down to what a human would paste., The generated letter as plain text, or '' when it was never generated., The manual_open route: open the offer, copy the letter, submit nothing.      A l, _TextParser

### Community 119 - "FormField"
Cohesion: 0.13
Nodes (23): SentenceTransformer, apply_matching_profile_cmd(), Connection, _queue_snapshot(), Apply config/matching_profile.yaml and report what it changed.      Re-scoring i, Count what currently clears the bar, for an honest before/after., Re-evaluate every offer against the new vocabulary.      ``jobpilot score`` only, _rescore_all() (+15 more)

### Community 120 - "test_preview.py"
Cohesion: 0.67
Nodes (3): _F, gate(), Label what this function refuses, and what refusing costs.      Attached to the

### Community 121 - "Any"
Cohesion: 0.18
Nodes (14): _consecutive_failures(), _last_runs(), Any, Connection, Row, Leading failures only: one success resets the streak., Last recorded run per enabled source, with what that run actually did.      ``la, Everything the queue page shows about scheduled ingestion. (+6 more)

### Community 124 - "_reject_unsupported_tokens"
Cohesion: 0.17
Nodes (17): Container, _designation_spans(), ProvenanceScope, Everything true of the career the generated text is describing.      Generated t, Check every designation against the scope; return what it covers.      Designati, Blank out validated designations, keeping every other offset intact., Build the rejection and record it, so the misses can be counted later.      This, Tier 1. A measurement belongs to the entry it was measured in. (+9 more)

### Community 125 - "gate"
Cohesion: 0.17
Nodes (15): The tier this failure carries HERE.      An unclassified error is fatal. That de, tier_for(), bank(), _raised(), Task 39 item 3: one funnel, three outcomes.  152 raise sites all meant "abort",, The one gate stopping a CV experience entry at the offer's employer., The safety property of the whole task: forgetting to classify a gate     keeps t, The same capability refusal is fatal in the letter and recoverable in the     pr (+7 more)

### Community 126 - "Connection"
Cohesion: 0.25
Nodes (13): ingest_cmd(), Fetch offers from a source (or all sources) into the database., enabled_sources(), _enablement(), is_enabled(), Read config/sources.yaml. Unlisted sources default to enabled., Registered sources that are enabled in config, in registration order., Path (+5 more)

### Community 128 - "Path"
Cohesion: 0.26
Nodes (9): _CompleteAdvisor, Connection, Path, _Toolchain, _queued_application(), _RecordingToolchain, test_generated_cv_is_complete_and_locally_located(), test_incomplete_cv_rolls_the_application_back_to_queued() (+1 more)

### Community 129 - "test_bullet_ceiling.py"
Cohesion: 0.15
Nodes (12): bank(), Task 35 item 3: a rejection that says what would have been valid.  Task 22c allo, The regression test for the failure that burned two generations., `experience.` is common to every experience entry. Matching on it would     list, A large entry must not blow the retry prompt., Existing callers and tests match on this prefix; item 3 appends, it does     not, test_a_bad_baifall_id_is_told_a_real_baifall_id(), test_an_unresolvable_id_says_so_plainly_instead_of_dumping_the_bank() (+4 more)

### Community 130 - "score"
Cohesion: 0.09
Nodes (31): Logger, Shared human-approval and document-generation application flow., Put text on the system clipboard, or say plainly that it could not.  The manual_, _env_bool(), get_settings(), _path(), Configuration and path resolution. Secrets come from .env only (never mocked)., Ingestion orchestrator: pull normalized records from a Source into the DB.  Idem (+23 more)

### Community 131 - "apply_matching_profile"
Cohesion: 0.24
Nodes (10): counts(), Connection, datetime, The tracker: every application, one table, read-only.  Deliberately not a Google, Statuses that actually occur, so the filter offers no dead options., The four numbers worth seeing before the table itself., Monday 00:00 UTC of the current week, as ISO text.      Compared as text against, statuses() (+2 more)

### Community 132 - "observable_controls"
Cohesion: 0.08
Nodes (32): ApplicantProfile, _Control, _ControlParser, _controls_from_html(), _css_attribute_value(), FillAction, _first_matching_selector(), _Form (+24 more)

### Community 133 - "_bullets"
Cohesion: 0.25
Nodes (8): _bullets(), The pre-written variants from the skill asset, used as the asset intends., Task 25's tolerance survives: ids are normalised before they are judged., The rendered <li> texts under one employer, decoded back to plain text., No paraphrase, no reflow: the hand-tuned line fit survives generation., test_a_prefix_less_selection_still_resolves(), test_a_rendered_bullet_is_byte_identical_to_its_fact(), test_the_baifall_variant_bullets_are_selectable_verbatim()

### Community 134 - "test_dedup.py"
Cohesion: 0.48
Nodes (6): source_id(), _offer(), Connection, content_hash dedup + INSERT OR IGNORE behavior., test_same_content_hash_collapses_to_one_row(), test_same_external_id_ignored()

### Community 135 - "update.sh"
Cohesion: 0.60
Nodes (3): changed_since_pull(), die(), update.sh script

### Community 136 - "scheduler_status"
Cohesion: 0.09
Nodes (43): age_in_days(), annotate(), describe(), _label(), max_offer_age_days(), _parse(), Any, datetime (+35 more)

### Community 137 - "run_dashboard"
Cohesion: 0.50
Nodes (4): dashboard_cmd(), Launch the local review dashboard on 127.0.0.1., Run the dashboard on an intentionally fixed loopback interface.      Returns a p, run_dashboard()

### Community 138 - "mappings_for"
Cohesion: 0.15
Nodes (11): _plan(), Path, Task 41: the header location is found by its own marker, not by its neighbours., A template re-exported with a plain pin and a different separator.      Under th, The header is a fixed-width line; the span must not consume any of it., The header location is renderer-owned: it comes from the offer's city., The premise of the fix, asserted rather than assumed.      If this ever fails th, test_every_template_still_extracts_its_location() (+3 more)

### Community 142 - "_Advisor"
Cohesion: 0.13
Nodes (17): Connection, Path, Nothing is weakened: a fabrication ends the run exactly as before., An invented figure is recoverable — the retry is handed the real ones —     but, test_a_fatal_gate_still_aborts(), test_a_recoverable_gate_with_no_degradation_escalates_to_fatal(), test_an_advisory_gate_never_blocks(), Amber, not red: the document is usable, it just needs a look. (+9 more)

## Knowledge Gaps
- **158 isolated node(s):** `Requirements`, `macOS / Linux`, `Windows PowerShell`, `Configuration`, `CV variant selection` (+153 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **20 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `.from_mapping` to `score`, `_client`, `observable_controls`, `create_app`, `Path`, `test_routing.py`, `mailer.py`, `wttj.py`, `france_travail.py`, `launch_wttj_application`, `_FakePage`, `test_email_alerts.py`, `test_labonnealternance.py`, `_Toolchain`, `test_dashboard_facts_scheduler.py`, `_FakePage`, `pick_variant`, `models.py`, `Path`, `Connection`, `_TextParser`, `Any`, `_FakeLocator`, `Connection`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `score` to `_client`, `observable_controls`, `dashboard.py`, `run_dashboard`, `scheduler_status`, `mailer.py`, `test_routing.py`, `get_settings`, `RefreshRunner`, `wttj.py`, `SourcedBullet`, `launch_wttj_application`, `generate_application`, `test_email_alerts.py`, `test_labonnealternance.py`, `.from_mapping`, `test_cold_outreach.py`, `_FakePage`, `resolve_fact_id`, `ingest_source`, `test_fact_id_resolution.py`, `test_mailer.py`, `test_valid_sourced_advice_completes_the_shared_generation_path`, `Connection`, `_TextParser`, `FormField`, `Connection`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Why does `current_status()` connect `launch_wttj_application` to `Path`, `score`, `_candidate_name`, `dashboard.py`, `run_dashboard`, `scheduler_status`, `mailer.py`, `test_routing.py`, `_Advisor`, `test_skim.py`, `_FakePage`, `generate_application`, `test_contacts.py`, `test_cold_outreach.py`, `_FakePage`, `resolve_fact_id`, `CompanyRecord`, `labonnealternance.py`, `ingest_source`, `test_fact_id_resolution.py`, `test_mailer.py`, `reparse_alerts`, `test_designation_numbers.py`, `ingest_source`, `CompanyRecord`, `Connection`, `test_profile_domain_anchor.py`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 62 inferred relationships involving `Settings` (e.g. with `ApplicantProfile` and `ApplyAdapter`) actually correct?**
  _`Settings` has 62 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `current_status()` (e.g. with `test_a_fatal_gate_still_aborts()` and `test_a_recoverable_gate_with_no_degradation_escalates_to_fatal()`) actually correct?**
  _`current_status()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `_payload()` (e.g. with `_plan()` and `_plan()`) actually correct?**
  _`_payload()` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `TailoringError` (e.g. with `ExperienceFact` and `FactBank`) actually correct?**
  _`TailoringError` has 24 INFERRED edges - model-reasoned connections that need verification._