# Graph Report - jobpilot  (2026-08-04)

## Corpus Check
- 178 files · ~219,205 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3900 nodes · 9894 edges · 171 communities (143 shown, 28 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 369 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b61f1491`
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
- _reject_unsupported_tokens
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
- test_mailer.py
- _application
- FormField
- _reject_placeholders
- Any
- test_form_learning.py
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
- _FakeLocator
- test_dedup.py
- update.sh
- scheduler_status
- _Toolchain
- mappings_for
- vocabulary.py
- import_origin_allowed
- test_the_minimum_is_above_the_alert_card_average
- _Advisor
- test_keyword_router_still_misroutes_the_villeneuve_offer
- Any
- CompletedProcess
- test_ingest_idempotent.py
- Connection
- 010_offers_imported.sql
- test_registry.py
- Path
- Protocol
- RuntimeError
- counts
- parse_indeed
- _approve
- Request
- test_renderer_owned_fields.py
- database_connection
- _generation_warnings
- clear_match_scores
- ClientCredentialsToken
- MenubarUnavailable
- test_imap_transport_searches_domains_and_drops_lookalike_senders
- SendBlocked
- _no_real_sleeping
- test_script_toolchain_passes_windows_paths_as_distinct_subprocess_arguments
- test_openai_failures_use_application_rollback_and_redact_key
- counts
- test_sourcing_targets_changes_no_sending_gate
- test_no_fixture_contains_a_credential

## God Nodes (most connected - your core abstractions)
1. `Settings` - 117 edges
2. `current_status()` - 96 edges
3. `_payload()` - 92 edges
4. `TailoringError` - 84 edges
5. `OfferRecord` - 83 edges
6. `load_fact_bank()` - 76 edges
7. `create_app()` - 70 edges
8. `_Toolchain` - 67 edges
9. `OfferContext` - 62 edges
10. `get_settings()` - 61 edges

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

## Communities (171 total, 28 thin omitted)

### Community 0 - "test_downloads.py"
Cohesion: 0.05
Nodes (41): BaseException, Operation, ProgressRegistry, Any, datetime, Update a running operation. A key that is not running is ignored., Close an operation. The first outcome recorded wins.          A handled failure, Everything running, plus anything that finished very recently. (+33 more)

### Community 1 - "Request"
Cohesion: 0.08
Nodes (57): Path, Resolve one archived artefact, with the same discipline as the live one.      De, _safe_archive_path(), _safe_artifact_path(), _archives_for(), Generation, is_archive_stamp(), library_entries() (+49 more)

### Community 2 - "_candidate_name"
Cohesion: 0.07
Nodes (89): _client(), _days_ago(), _events(), _no_advisor_client(), _offer_application(), Connection, MonkeyPatch, Path (+81 more)

### Community 3 - "_client"
Cohesion: 0.05
Nodes (64): InteractiveTailoringAdvisor, Terminal prompts used when interactive tailoring is selected., CatalogueEntry, default_catalogue(), load_variant_catalogue(), _parse_criteria(), _parse_shortcuts(), Path (+56 more)

### Community 4 - "create_app"
Cohesion: 0.22
Nodes (15): AnthropicTailoringAdvisor, Claude Messages API adviser used when ``ANTHROPIC_API_KEY`` is set., _Client, _offer(), _plan_payload(), Any, Exception, Focused contracts for tailoring advisers and the script toolchain. (+7 more)

### Community 5 - "dashboard.py"
Cohesion: 0.07
Nodes (71): ExperienceFact, GenerationWarning, Match, Pattern, RuntimeError, _add_tech_additions(), _add_tech_keywords(), _cap_experience_selection() (+63 more)

### Community 6 - "run_dashboard"
Cohesion: 0.19
Nodes (17): _dropping_enabled(), _InventsForever, Connection, MonkeyPatch, Path, Task 37 item 3: degradation. Shipped off, turned ON by Task 39.  If the advisor, Turning it off restores the old behaviour exactly., Enabling degradation does not make everything droppable. (+9 more)

### Community 7 - "Path"
Cohesion: 0.09
Nodes (31): _fit(), _offer(), Task 44 item 2: the CV title has a layout budget.  « Ingénieur en data - Optimis, The bug, and the reason step 2 exists at all: the head of that title is     a pe, Cutting keeps the head clause, which is the role only when the posting     is we, The floor must not swallow the case step 2 exists for., The template's own title ends 'Alternance M2 dès Septembre 2026'. Reused     ver, Step 3 is the floor, so it must never itself overflow — otherwise the     degrad (+23 more)

### Community 8 - "test_routing.py"
Cohesion: 0.11
Nodes (55): Cursor, _artifacts(), Path, Resolve the one route this application would go out by. Writes nothing., resolve_route(), _client(), Connection, MonkeyPatch (+47 more)

### Community 9 - "mailer.py"
Cohesion: 0.10
Nodes (43): Show the email that would be sent for a ready application, then confirm (y/N)., send_cmd(), _as_utc(), _build_message(), build_sender(), ColdEmailPreparation, daily_cap_reached(), _default_body() (+35 more)

### Community 10 - "validate_cv.py"
Cohesion: 0.06
Nodes (53): check_orphans(), find_regressions(), Path, Return orphan metrics that are new or materially worse than the template., format_date(), main(), build_letter_html(), detect_github() (+45 more)

### Community 11 - "get_settings"
Cohesion: 0.09
Nodes (26): _correction_block(), _is_validator_rejection(), Raised when an external tailoring provider request fails., Raised when a tailoring provider rejects its API credentials., Raised when a tailoring provider rate-limits a request., Raised when a provider returns an unusable response., The advisor's reasoned CV pick, before any mechanical contract rule., Validate a selection answer. The model may not invent a variant. (+18 more)

### Community 12 - "connect"
Cohesion: 0.12
Nodes (21): derive_fields(), _Derived, Re-derive one offer's card fields from the text that was stored for it.      Pur, _Card, _card_fields(), CardFields, is_title_echo(), parse_card_line() (+13 more)

### Community 13 - "test_descriptions.py"
Cohesion: 0.13
Nodes (42): backfill_descriptions(), is_synthesized(), Regenerate synthesised descriptions for stored offers whose text is thin.      I, True when `description` was produced by this module., Compose a compact French paragraph from the fields the alert provided.      This, synthesize_description(), _offer(), Connection (+34 more)

### Community 14 - "test_generic_vocabulary.py"
Cohesion: 0.09
Nodes (32): extract_template_context(), Read all editable choices without altering the template., bank(), _plan(), Task 40 amendment: bullets had a floor and no ceiling.  _validate_experience_com, The ceiling does not soften the other direction., Floor beats ceiling; a template row count under it cannot make a bad CV., End to end: the renderer inserts what survived, not what was asked for. (+24 more)

### Community 15 - "apply_assist.py"
Cohesion: 0.12
Nodes (42): counts(), Any, Connection, datetime, The tracker: every application, one table, read-only.  Deliberately not a Google, Every offer application, optionally narrowed to one status.      ``include_stale, Statuses that actually occur, so the filter offers no dead options., Export exactly the visible rows, in the visible column order. (+34 more)

### Community 16 - "test_skim.py"
Cohesion: 0.10
Nodes (53): available_sources(), _create_application(), ignore_offer(), promote_offer(), Connection, datetime, Row, ValueError (+45 more)

### Community 17 - "contacts.py"
Cohesion: 0.10
Nodes (38): _candidate_name(), ContactCandidate, discover_and_store(), DiscoverySource, draft_cold_email(), draft_linkedin_note(), _get_or_create_cold_application(), is_professional_address() (+30 more)

### Community 18 - "JobPilot — Codex Handoff (complete A-to-Z)"
Cohesion: 0.04
Nodes (45): 10. HARD REJECTIONS (offers the pipeline should auto-skip), 11. API REFERENCES, 12. DESIGN PRINCIPLES (non-negotiable), 13. ENV VARS (.env), 14. GITHUB PUSH (do this FIRST, before any Codex work), 15. CODEX TASK BREAKDOWN (suggested order), 16. BAIFALL DREAM STAGE REFERENCE, 17. SCRIPTS REFERENCE (+37 more)

### Community 19 - "RefreshRunner"
Cohesion: 0.17
Nodes (25): _client(), _import(), Connection, TestClient, Task 43 item 4: after a description arrives, offer to redo the tailoring.  An ap, Task 34's regenerate refuses anything but `ready`, and an applied CV has     alr, The button posts where the existing Régénérer posts. Asserted by     comparing t, The extension POSTs JSON from the offer page and never lands on the     dashboar (+17 more)

### Community 20 - "_payload"
Cohesion: 0.11
Nodes (43): _bullets(), _project(), The advisor selects; the renderer inserts the bank's wording unchanged., The pre-written variants from the skill asset, used as the asset intends., The contract has no field for prose, so a writing advisor fails loudly., Only the entry's own facts, so a skill id cannot become a bullet., Task 25's tolerance survives: ids are normalised before they are judged., The phrase is short, but it is still generated, so the tiers still read it. (+35 more)

### Community 21 - "wttj.py"
Cohesion: 0.10
Nodes (41): _city(), _contact_email(), _contract(), _first(), map_hit(), _org(), _prose(), Any (+33 more)

### Community 22 - "SourcedBullet"
Cohesion: 0.10
Nodes (30): ConnectionFactory, Event, Any, Connection, Single-flight ingest + score pass driven from the dashboard., Block until the running refresh finishes. Tests use this, not sleeps., Claim the single flight and hand the work to a background thread., One source's outcome, kept even when the source failed or was skipped. (+22 more)

### Community 23 - "france_travail.py"
Cohesion: 0.14
Nodes (22): _first_nonempty(), FranceTravailSource, _map_contact_email(), _map_contract(), _map_duration_months(), map_offer(), Any, Parse '... - 12 Mois' style durations from typeContratLibelle. (+14 more)

### Community 24 - "test_provenance_tiers.py"
Cohesion: 0.08
Nodes (38): bank(), _in_bank(), _offer(), Three kinds of token, three different burdens of proof., Not even the widest scope can support it., The reader has to be able to search for it, or add it to the config., Task 26's handling survives as the digit-shaped corner of tier 2., Presence in the bank is necessary for tier 2, never sufficient. (+30 more)

### Community 25 - "launch_wttj_application"
Cohesion: 0.33
Nodes (4): _OneShotProfileOrphan, Path, _Toolchain, A profile-only layout regression that disappears with template wording.

### Community 26 - "Dashboard"
Cohesion: 0.05
Nodes (40): Actualiser les offres (refresh from the page), Always up, without a terminal, Architecture (summary), ATS application assist (prefill only), Background scheduling, CI, Cold outreach sending (disabled by default), Commands (+32 more)

### Community 27 - "_FakePage"
Cohesion: 0.13
Nodes (16): ApplyAdapter, Common adapter interface for a best-effort ATS prefill., _FakeLauncher, _FakeLocator, _FakePage, Connection, _FakePage, Path (+8 more)

### Community 28 - "cli.py"
Cohesion: 0.11
Nodes (26): Decision, RouteId, _applicant_reason(), _ats_prefill(), _email(), _learned_form(), _manual_open(), _missing_applicant_fields() (+18 more)

### Community 29 - "test_desktop_shell.py"
Cohesion: 0.07
Nodes (40): CaptureFixture, dashboard_already_running(), Whether something is already listening on the dashboard's port.      A connect p, The menu bar text. Short: it competes with every other item up there., title(), _bound_port(), _fake_macos(), _module_level_imports() (+32 more)

### Community 30 - "generate_application"
Cohesion: 0.08
Nodes (29): Connection, date, Path, Protocol, _check_orphans(), _contains_generated_orphan(), DocumentToolchain, _french_date() (+21 more)

### Community 31 - "test_contacts.py"
Cohesion: 0.10
Nodes (27): ModuleType, JobPilot: personal job application pipeline for the French IT/cybersecurity mark, _application(), _ConnectionProxy, Connection, Exception, Path, CLI coverage for offer document generation and cold-application approval. (+19 more)

### Community 32 - "test_email_alerts.py"
Cohesion: 0.22
Nodes (23): LinkedInAlertSource, _FakeIMAP, _fixture_message(), _msg(), Connection, EmailMessage, LogCaptureFixture, LinkedIn / Indeed alert parsing + IMAP-backed Source (with injected transport). (+15 more)

### Community 33 - "test_labonnealternance.py"
Cohesion: 0.15
Nodes (29): _fixture(), _NoWait, LogCaptureFixture, La Bonne Alternance through the API Apprentissage: mapping, rails, ingestion.  E, The endpoint has no pagination, so this is the volume knob that exists., A full ingest reads both lists; it must not pay for the search twice., The live API really does repeat an offer inside one response., A company that has posted nothing must not appear in the review queue. (+21 more)

### Community 34 - "_Toolchain"
Cohesion: 0.07
Nodes (30): Path, Task 43 item 2: the browser extension, and the line it must not cross.  The exte, Two files naming the same three sites. A content script runs in the     page's o, Most of the time JobPilot is not running. The extension has to be     invisible, A rejected promise with no catch surfaces as an unhandled rejection,     which i, One obvious place, with the warning next to it., The requirement that matters most in a year: when LinkedIn changes its     gener, The biggest element on a page is a wrapper holding the whole page. (+22 more)

### Community 35 - "email_alerts.py"
Cohesion: 0.08
Nodes (28): Every id the advisor may cite, flattened out of the context it was given.      D, valid_fact_ids(), facts(), _nested_ids(), Task 37 item 1: tell the advisor the set of ids is closed.  `skill.rules.sigma`, Task 37 must not have quietly added Sigma to make the failure go away., Defensive: a template with no projects must not raise here., The exact mechanism that produced skill.rules.sigma. (+20 more)

### Community 36 - "test_alert_card_fields.py"
Cohesion: 0.10
Nodes (34): as_dicts(), clear_warnings(), _decode(), GenerationWarning, Any, Connection, What a generation had to degrade, recorded where the reviewer will see it.  Task, Gate names per application, for the library and tracker markers.      One query (+26 more)

### Community 37 - "Settings"
Cohesion: 0.08
Nodes (44): CvProfile, _advise_and_tailor(), _advisor_fact_context(), _advisor_prompt(), DroppedCitation, _fit_cv_title(), _infer_region(), _interactive_structured_payload() (+36 more)

### Community 38 - "Job Application Pipeline"
Cohesion: 0.06
Nodes (31): Alternance vs Stage, Edge Cases & Principles, Encoding note, Execution Flow, Flag once, then execute:, Generate with the bundled script:, GitHub Exception, Hard rejections (no output): (+23 more)

### Community 39 - "matcher.py"
Cohesion: 0.15
Nodes (28): bonus_score(), cosine(), hard_filter(), keyword_score(), norm(), pick_variant(), Profile, Connection (+20 more)

### Community 40 - "test_cv_completeness.py"
Cohesion: 0.09
Nodes (31): CvProfile, load_cv_profile(), Renderer-owned candidate facts injected into every generated CV., The location printed in the CV header when the offer yields none., Load the committed CV profile, failing loudly rather than defaulting., _category_skills(), _CompleteAdvisor, Any (+23 more)

### Community 41 - "OfferRecord"
Cohesion: 0.09
Nodes (43): OpenAITailoringAdvisor, pick_variant(), Pick the best of 21 variants from missions, then apply contract rules.      Sinc, OpenAI-compatible Chat Completions adviser., _plan_for(), _experience_content(), _FabricatingAdvisor, _gemini_shaped_payload() (+35 more)

### Community 43 - ".from_mapping"
Cohesion: 0.13
Nodes (34): applications_by_status(), Offer applications in one status, newest first, with their age.      Returns the, _client(), _days_ago(), _offer_application(), Connection, MonkeyPatch, TestClient (+26 more)

### Community 44 - "test_cold_outreach.py"
Cohesion: 0.11
Nodes (16): HTTPStatusError, MissingCredentialError, RuntimeError, Raised when a required secret is absent. We ask; we never silently mock., RateLimiter, Minimum-delay-per-domain limiter. Blocks until the next call is allowed., LaBonneAlternanceAuthError, LaBonneAlternanceError (+8 more)

### Community 45 - "_FakePage"
Cohesion: 0.08
Nodes (34): BrowserLauncher, _ConfirmationBaseline, launch_wttj_application(), _Locator, _open_for_human(), _Page, Protocol, A launch seam: production opens Playwright, tests supply a stub page. (+26 more)

### Community 46 - "MissingCredentialError"
Cohesion: 0.13
Nodes (34): _client(), _fail(), _Fake, _offer(), Connection, Row, TestClient, Task 41 item 6: a source that has stopped answering must not read as healthy.  B (+26 more)

### Community 47 - "ats.py"
Cohesion: 0.15
Nodes (23): download_filename(), Download names an employer folder can still be read a week later.  ``output/appl, Reduce free text to ``[A-Za-z0-9-_]``, or to "" if nothing survives.      Accent, Build ``<Company>_<Type>_<Nom>.<ext>`` for one artefact.      Falls back to the, slugify(), _client(), Connection, Path (+15 more)

### Community 48 - "AnthropicTailoringAdvisor"
Cohesion: 0.22
Nodes (25): _cold_draft(), _configure_dashboard(), _dashboard_client(), _event_rows(), Connection, EmailMessage, Exception, MonkeyPatch (+17 more)

### Community 49 - "OpenAITailoringAdvisor"
Cohesion: 0.16
Nodes (20): _all_template_paths(), _bullet_budget(), _claim_length(), _normalized(), _project_desc_budget(), _project_desc_rows(), An experience claim has to fit the CV's one line.  The renderer inserts a select, The widest project description any template already renders. (+12 more)

### Community 50 - "resolve_fact_id"
Cohesion: 0.08
Nodes (17): CompletedProcess, AmbiguousFactIdError, Raised when generated prose states a figure the bank does not contain.      A si, Raised when a citation matches no fact id, even after normalisation.      ``sect, Raised when a citation could be several facts. Never guess between them., Raised when one automatic validator-feedback retry still failed.      ``str()``, TailoringRejectedError, UnknownFactIdError (+9 more)

### Community 51 - "test_tech_additions.py"
Cohesion: 0.15
Nodes (26): bank(), _offer(), LogCaptureFixture, Zone 3 may add a keyword, but only one he has and the offer asked for., Reorder-only remains the default and the common case., Genuinely his, but padding: the offer did not ask for it., Presence in the bank is necessary, never sufficient., Derived from the file, not a magic number. (+18 more)

### Community 52 - "load_fact_bank"
Cohesion: 0.11
Nodes (37): facts_cmd(), Print the provenance fact bank grouped for human review., _boolean(), CertificationFact, _claim_list(), EducationFact, _entry_claim(), ExperienceFact (+29 more)

### Community 53 - "CompanyRecord"
Cohesion: 0.12
Nodes (38): clean_description(), Collapse the whitespace a copied page carries, and keep the rest., _client(), _fake_score(), _offer(), Connection, TestClient, Task 43 item 1: an offer description captured from an open page.  LinkedIn and I (+30 more)

### Community 54 - "labonnealternance.py"
Cohesion: 0.11
Nodes (17): _InteractiveShapedAdvisor, Human loop: always rejected, and never re-prompted automatically., _InventsThenRecovers, Connection, LogCaptureFixture, Path, Task 37 item 2: give the unknown-id retry something to work with.  An unknown fa, Cites an id that exists nowhere, for a chosen number of attempts. (+9 more)

### Community 55 - "ingest_source"
Cohesion: 0.16
Nodes (9): Any, _canonicalize_prose(), _justification(), Normalize model punctuation that the document contract forbids.      This is a l, One employer's bullets, chosen from its facts rather than written.      The skil, One project, and which of its facts describes it. Inserted verbatim., Validate the one JSON contract shared by every advisor provider., TailoredExperience (+1 more)

### Community 56 - "pick_variant"
Cohesion: 0.19
Nodes (19): IllegalTransition, log_event(), Connection, ValueError, The single authorized writer of applications.status.  Every status transition MU, Raised when a status change is not permitted by the state machine., Append an audit event. Used for status_change, human_approved, email_sent, etc., Move an application to to_status if legal; log a status_change event.      Retur (+11 more)

### Community 57 - "test_fact_id_resolution.py"
Cohesion: 0.19
Nodes (25): invention_report(), How often the advisor cites an id that does not exist, and whether it recovers., Connection, Path, test_a_rejected_number_is_counted_separately_from_an_invented_id(), _Invents, Connection, MonkeyPatch (+17 more)

### Community 58 - "test_letter_locked_fields.py"
Cohesion: 0.18
Nodes (19): bank(), _letter(), _offer(), A letter is prose about a career; a CV is slots the renderer fills., Naming a real-sounding employer he never had is a fabrication, not prose., The renderer injects the address block; the body repeating it is a bug., Otherwise the test above would prove nothing about scope., The bank's own text names nothing it should not; selection is the check. (+11 more)

### Community 60 - "test_letter_quality.py"
Cohesion: 0.13
Nodes (24): FactClaim, _default_letter(), french_de_elision(), Return « de <noun> » or « d'<noun> », applying French elision.      Elides befor, A selected fact must be a real, reviewed fact OF THAT ENTRY.      This is the wh, _validate_letter_body(), _validate_selection(), _raised() (+16 more)

### Community 61 - "test_mailer.py"
Cohesion: 0.03
Nodes (94): add_contact_cmd(), apply_cmd(), apply_matching_profile_cmd(), backfill_descriptions_cmd(), contacts_cmd(), _csv(), daemon_cmd(), dashboard_cmd() (+86 more)

### Community 62 - "models.py"
Cohesion: 0.29
Nodes (16): _client(), fixture_bank(), Connection, MonkeyPatch, Path, TestClient, Read-only fact bank page and honest scheduler reporting on the queue page., test_daemon_state_follows_the_recorded_heartbeat_age() (+8 more)

### Community 63 - "reparse_alerts"
Cohesion: 0.23
Nodes (15): current_status(), _generation_failed_detail(), Any, Connection, LogCaptureFixture, Path, One automatic advisor retry, fed only the validator's own error text., Re-calling on a 429 or a bad key is not feedback, it is a retry storm. (+7 more)

### Community 64 - "test_designation_numbers.py"
Cohesion: 0.08
Nodes (35): LookupError, ApplicationGenerationError, ApplicationNotFoundError, ApplicationNotQueuedError, ApplyOutcome, approve_application(), archive_artifacts(), generation_single_flight() (+27 more)

### Community 65 - "test_fact_id_consistency.py"
Cohesion: 0.20
Nodes (15): bank(), _bank_payload(), Path, Task 35 item 2: a fact bank whose claim ids do not extend their entry is invalid, The real bank must satisfy the rule the loader now enforces., This is the exact shape the Baïfall entry had., Projects have the same shape as experience, so they get the same rule., `experience.baifallX` starts with the entry id as a STRING but is a     differen (+7 more)

### Community 66 - "review.py"
Cohesion: 0.18
Nodes (18): _AlertSource, _ingest_then_import(), Connection, Row, Task 43 item 5: an imported description is never overwritten.  The user opens th, `force` exists to re-compose rows the normal pass skips. That widening     must, The guard must be `imported_at`, not an accident that stopped the     backfill w, A source that keeps offering the thin card, exactly as an alert does. (+10 more)

### Community 67 - "ingest_source"
Cohesion: 0.19
Nodes (17): apply_schema(), init_db(), Connection, Path, Ensure the sources rows exist. Idempotent via INSERT OR IGNORE on unique name., Full initialization: schema + migrations + source seeding., Apply schema.sql. Idempotent: uses CREATE TABLE ... only, so we guard reruns., Apply numbered .sql migrations not yet recorded. Returns count applied.      sch (+9 more)

### Community 68 - "_AnchorParser"
Cohesion: 0.25
Nodes (9): source_id(), content_hash(), sha256(lower(title + company + first 500 chars of description)).      This is th, _offer(), Connection, content_hash dedup + INSERT OR IGNORE behavior., test_content_hash_is_stable_and_case_insensitive(), test_same_content_hash_collapses_to_one_row() (+1 more)

### Community 69 - "test_preview.py"
Cohesion: 0.23
Nodes (19): _fake_clone(), _git(), CompletedProcess, Path, Task 41: one command after a merge, and it refuses rather than half-updates.  sc, The loud refusal. A fast-forward carries uncommitted work with it., The point of the conditions: the two slow steps cost nothing here., Kickstarting the agents is unconditional: new code is only running once     the (+11 more)

### Community 70 - "vocabulary.py"
Cohesion: 0.17
Nodes (17): live_db(), _Observed, _offer(), Connection, Exception, Path, Task 41 follow-up: the write lock is not held across the network.  Task 41 put W, Draining buys the lock back without giving up atomicity — which is what     comm (+9 more)

### Community 71 - "UnknownFactIdError"
Cohesion: 0.11
Nodes (30): parse_linkedin(), Extract jobs from a LinkedIn job-alert email., _card_html(), LogCaptureFixture, Structural parsing of job-alert cards (Task 20).  Every fixture here is shaped a, The same four values models.REMOTE_POLICIES defines for every source., Indeed writes "Villeneuve-d'Ascq (59)" — the postcode is not a workplace., Whatever position the chrome occupies, it must not be stored. (+22 more)

### Community 72 - "Baifall Dream Stage - Reference Document (v3)"
Cohesion: 0.17
Nodes (11): Baifall Dream Stage - Reference Document (v3), Bloc HTML de reference (3 bullets), Bullet 1 (commun, accompli) - 167 car., rendu sur 2 lignes, Bullet 2 (commun, nominal, perimetre complet) - 127 car., 1 ligne, Bullet 3 : declinaisons par variante, Context, Principe v3 : perimetre nominal complet, Regle pour la date (+3 more)

### Community 73 - "test_facts.py"
Cohesion: 0.05
Nodes (79): build_prefill(), discard_mapping(), fields_from_html(), FormField, FormLearningError, FormMapping, infer_profile_field(), mapping_is_complete() (+71 more)

### Community 74 - "test_progress.py"
Cohesion: 0.11
Nodes (15): BackfillResult, enrich_offer(), is_thin(), Replace a thin description in place; richer descriptions are left alone.      Ca, True when a description is too short to be worth embedding on its own., OfferRecord, One normalized offer, ready to insert into the offers table., Coerce enum-constrained fields to legal values (schema CHECK safety). (+7 more)

### Community 75 - "scheduler_status"
Cohesion: 0.22
Nodes (16): _alert_source_clause(), Connection, Restrict to one alert source, or to all of them when none is named., Re-derive company / city / workplace / easy-apply for stored alert offers., reparse_alerts(), ReparseResult, Connection, The card line survived in companies.name; the city held only chrome. (+8 more)

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

### Community 80 - "_reject_unsupported_tokens"
Cohesion: 0.07
Nodes (39): Container, FactBank, _contact_fields(), _cv_locked_fields(), _designation_spans(), document_variant_label(), nearest_entry_claim_ids(), _proper_nouns() (+31 more)

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
Nodes (15): Connection, Path, Task 39 item 3: one funnel, three outcomes.  152 raise sites all meant "abort",, Nothing is weakened: a fabrication ends the run exactly as before., An invented figure is recoverable — the retry is handed the real ones —     but, test_a_fatal_gate_still_aborts(), test_a_recoverable_gate_with_no_degradation_escalates_to_fatal(), test_an_advisory_gate_never_blocks() (+7 more)

### Community 88 - "profile.py"
Cohesion: 0.06
Nodes (61): Return capability-tier tokens that have tripped generations, by frequency., vocabulary_misses(), GenericVocabularyError, load_generic_vocabulary(), parse_rejections(), Path, StrEnum, ValueError (+53 more)

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
Nodes (59): allowed_numbers(), _bank_parts(), _guessed_section(), letter_scope(), _normalized_number(), _offer_identity(), _organisation_names(), Everything the verified bank says the candidate has actually touched.      Only (+51 more)

### Community 112 - "Connection"
Cohesion: 0.14
Nodes (13): attempt(), describe(), fromSelectors(), hostKey(), largestTextBlock(), send(), textOf(), toast() (+5 more)

### Community 113 - "apply_matching_profile_cmd"
Cohesion: 0.17
Nodes (11): bank(), Task 35 item 3: a rejection that says what would have been valid.  Task 22c allo, The regression test for the failure that burned two generations., `experience.` is common to every experience entry. Matching on it would     list, A large entry must not blow the retry prompt., Existing callers and tests match on this prefix; item 3 appends, it does     not, test_a_bad_baifall_id_is_told_a_real_baifall_id(), test_an_unresolvable_id_says_so_plainly_instead_of_dumping_the_bank() (+3 more)

### Community 114 - "test_variant_selection.py"
Cohesion: 0.09
Nodes (33): _fact_id_key(), Fold separator and case differences, and nothing else, for comparison., Map a cited id onto a real fact id, accepting only unambiguous matches.      Mat, resolve_fact_id(), _advise(), ambiguous_bank(), _offer(), Any (+25 more)

### Community 115 - "labonnealternance.py"
Cohesion: 0.13
Nodes (27): FastAPI, create_app(), Build the local dashboard, with injectable generation collaborators for tests., Freshness, How old one offer is, and how sure we are of that., application_detail(), event_history(), import_supersedes_documents() (+19 more)

### Community 116 - "test_profile_domain_anchor.py"
Cohesion: 0.31
Nodes (10): _offer(), Systemic recovery at the generated-prose and document-layout boundaries., Naming the employer is what a motivation letter does.      The rule was never lo, _selection_and_template(), test_a_valid_custom_profile_phrase_is_preserved_exactly(), test_an_invalid_profile_phrase_uses_the_variant_fallback(), test_an_unsupported_candidate_claim_remains_a_hard_failure(), test_model_prose_dashes_are_canonicalized_before_validation() (+2 more)

### Community 117 - "test_mailer.py"
Cohesion: 0.28
Nodes (17): Combined application + cold-mail sends recorded for today (UTC)., sends_today(), _events(), Connection, EmailMessage, Exception, Path, Application email sending: rails, transitions, and events (mocked SMTP). (+9 more)

### Community 118 - "_application"
Cohesion: 0.27
Nodes (18): _application(), _client(), Connection, TestClient, Task 43 item 3: pasting the description is a first-class path.  Not a fallback f, The card is 113 characters and the CV was tailored against it. Saying so     is, A rejected paste must not look like a lost page, and must not have     replaced, One endpoint, two representations. The JSON caller sends no     application_id a (+10 more)

### Community 119 - "FormField"
Cohesion: 0.47
Nodes (11): _offer(), _openai_response(), _plan_payload(), Any, OpenAI-compatible tailoring advisor contracts with mocked HTTP calls., _selection(), _template(), test_custom_openai_base_url_is_honored() (+3 more)

### Community 120 - "_reject_placeholders"
Cohesion: 0.16
Nodes (17): No rendered CV may carry bracketed text. Task 44 item 1.      '[offer duration]', _reject_placeholders(), Task 44 item 1: no rendered CV may carry a bracketed placeholder.  « Stage de [o, If a hand-written template carried brackets, the guard would abort every     gen, The regression, quoted from application 37's rendered CV., Tier is the whole decision here: recoverable would mean retrying, and     the mo, Half the templates are entity-encoded, so the scan reads decoded text.     A pla, No template carries one today. This is about a future stylesheet edit     not fa (+9 more)

### Community 121 - "Any"
Cohesion: 0.22
Nodes (13): SimpleNamespace, build_advisor(), Raised when the selected tailoring provider is not configured., Resolve TAILORING_PROVIDER to a concrete mode, without building anything.      C, Select the configured provider without silently bypassing missing keys., resolve_provider(), TailoringConfigurationError, MonkeyPatch (+5 more)

### Community 122 - "test_form_learning.py"
Cohesion: 0.19
Nodes (14): _consecutive_failures(), daemon_status(), DaemonStatus, _last_runs(), Any, Connection, Row, Leading failures only: one success resets the streak. (+6 more)

### Community 124 - "_reject_unsupported_tokens"
Cohesion: 0.57
Nodes (6): Path, Source enablement via config/sources.yaml., _settings(), test_disabled_source_excluded(), test_no_config_all_enabled(), test_replace_keeps_dataclass_shape()

### Community 125 - "gate"
Cohesion: 0.16
Nodes (22): list_outreach_targets(), Companies an ingestion source flagged as likely to hire an alternant.      These, _backfill_company_source(), get_or_create_company(), Connection, Teach an existing company row where it came from, once.      A company first see, CompanyRecord, Yield companies likely to hire (optional; default: none). (+14 more)

### Community 126 - "Connection"
Cohesion: 0.16
Nodes (8): _AlertAnchor, _AnchorParser, _anchors(), GmailIMAP, HTMLParser, Minimal read-only Gmail IMAP client., Collect anchors plus nearby table/list-card text without dependencies., _TextContainer

### Community 128 - "Path"
Cohesion: 0.09
Nodes (30): _create_offer(), find_offer_by_url(), import_offer_description(), ImportResult, _is_tracking(), normalize_offer_url(), OfferImportError, Any (+22 more)

### Community 129 - "test_bullet_ceiling.py"
Cohesion: 0.14
Nodes (20): ATSSource, infer_contract(), load_targets(), map_greenhouse(), map_lever(), map_smartrecruiters(), _ms_to_iso(), Any (+12 more)

### Community 130 - "score"
Cohesion: 0.07
Nodes (47): apply_matching_profile(), load_matching_profile(), MatchingProfile, Write the vocabulary onto the profile singleton. Returns {field: (before, after), The scoring vocabulary, committed to git rather than typed once.      These thre, Load the committed matching vocabulary, failing loudly rather than defaulting., is_noise(), True when `text` is card chrome that must never be stored as a field. (+39 more)

### Community 131 - "apply_matching_profile"
Cohesion: 0.18
Nodes (19): SentenceTransformer, _as_list(), build_profile_text(), _col(), _model(), Row, Local embeddings via sentence-transformers (all-MiniLM-L6-v2), lazy-loaded.  Pro, Load the model once per process (heavy import kept out of module load). (+11 more)

### Community 132 - "observable_controls"
Cohesion: 0.04
Nodes (68): adapter_for_url(), ApplicantProfile, _application_for_assist(), _application_for_wttj(), ApplyAssistError, AssistResult, _BaseAdapter, _Control (+60 more)

### Community 133 - "_FakeLocator"
Cohesion: 0.17
Nodes (12): Message, EmailAlertError, RuntimeError, Fetch recent mail sent from `domains` (or any of their subdomains).          The, A redacted IMAP or alert-processing failure safe for CLI/log display., Return the lowercased domain of the address in a `From` header.      Parses the, True when the From address sits on one of `domains` or a subdomain of it., sender_allowed() (+4 more)

### Community 134 - "test_dedup.py"
Cohesion: 0.12
Nodes (25): _is_stage(), Apply the mechanical contract and encoding rules to a chosen slug.      These ar, The contract line an adapted alternance CV must carry., The stage contract line, built from what is known.      Task 44 item 1: this is, _stage_contract_phrase(), _validate_stage_contract_phrase(), variant_for_slug(), _offer() (+17 more)

### Community 135 - "update.sh"
Cohesion: 0.60
Nodes (3): changed_since_pull(), die(), update.sh script

### Community 136 - "scheduler_status"
Cohesion: 0.09
Nodes (43): age_in_days(), annotate(), describe(), drop_stale(), _label(), max_offer_age_days(), _parse(), parse_timestamp() (+35 more)

### Community 137 - "_Toolchain"
Cohesion: 0.17
Nodes (11): build_cv_title(), normalise_role_title(), Remove posting metadata while preserving the actual role wording., Build the deterministic CV title used after all advisor providers., Fact-bank loading, review CLI, and deterministic role-title cleaning., test_build_cv_title_uses_clean_role_and_contract_specific_suffix(), test_every_skill_is_explicitly_verified_or_unverified(), test_fact_bank_covers_every_cv_template_and_has_unique_claim_ids() (+3 more)

### Community 138 - "mappings_for"
Cohesion: 0.22
Nodes (7): _plan(), Task 41: the header location is found by its own marker, not by its neighbours., The header is a fixed-width line; the span must not consume any of it., The header location is renderer-owned: it comes from the offer's city., The premise of the fix, asserted rather than assumed.      If this ever fails th, test_the_marker_adds_no_visible_text(), test_the_templates_really_do_disagree_on_both_encodings()

### Community 139 - "vocabulary.py"
Cohesion: 0.17
Nodes (12): _F, gate(), Label what this function refuses, and what refusing costs.      Attached to the, The tier this failure carries HERE.      An unclassified error is fatal. That de, What a gate firing is allowed to cost.      Task 39. Seven consecutive generatio, Tier, tier_for(), StrEnum (+4 more)

### Community 140 - "import_origin_allowed"
Cohesion: 0.50
Nodes (4): import_origin_allowed(), True when `origin` may POST to IMPORT_PATH.      Host-suffix matching, so ``www., test_every_other_origin_is_rejected(), test_the_origins_the_feature_needs_are_allowed()

### Community 141 - "test_the_minimum_is_above_the_alert_card_average"
Cohesion: 0.22
Nodes (13): drop_unknown_citation(), Remove one unusable citation, or refuse when removing it would weaken the CV., _plan(), The completeness floor is a hard failure, not a preference., The spec said "at least one remaining bullet" is enough. It is not: the     Task, Exactly three projects are required, each with its single fact., skill_order has no minimum, so losing one weakens nothing structural., test_a_bullet_can_be_dropped_while_the_entry_stays_above_its_floor() (+5 more)

### Community 142 - "_Advisor"
Cohesion: 0.20
Nodes (9): content_scripts, description, host_permissions, manifest_version, name, version, https://*.indeed.fr/*, https://*.linkedin.com/* (+1 more)

### Community 143 - "test_keyword_router_still_misroutes_the_villeneuve_offer"
Cohesion: 0.21
Nodes (11): _profile_of(), Path, Task 40: the domain phrase is found by its own marker, not by its neighbours.  _, Not just the wordings we ship: any of them, including ones nobody wrote yet., The ±15-character layout budget must not shift under it., The bug. This raised "template profile domain phrase not found"., _stage_plan(), test_a_stage_adapted_cv_can_still_be_re_read() (+3 more)

### Community 146 - "test_ingest_idempotent.py"
Cohesion: 0.20
Nodes (15): ingest_source(), _insert_offer(), INSERT OR IGNORE one offer. Returns True if a new row was created., Run one source end to end. Commits once at the end for atomicity.      Two phase, Append one row to source_runs. Does not commit; the caller owns that.      A fai, record_run(), _utc_now(), FakeSource (+7 more)

### Community 149 - "test_registry.py"
Cohesion: 0.05
Nodes (66): Logger, ingest_cmd(), Fetch offers from a source (or all sources) into the database., copy_text(), Put text on the system clipboard, or say plainly that it could not.  The manual_, Copy ``text``; return whether it actually landed on the clipboard., _env_bool(), get_settings() (+58 more)

### Community 154 - "parse_indeed"
Cohesion: 0.18
Nodes (11): clean_job_url(), html_of(), parse_indeed(), Return the best HTML (or plain-text) body of an email message., Return a stable detail URL with email/tracking parameters removed., Extract jobs from an Indeed job-alert email., test_clean_job_url_removes_tracking_parameters(), test_parse_ignores_non_job_links() (+3 more)

### Community 155 - "_approve"
Cohesion: 0.33
Nodes (11): _approve(), Connection, LogCaptureFixture, Path, The asset file calls these false positives outside a full render., Task 39: the last hard position of the orphan gate went advisory.      It cost t, The reliable control, per the asset file, so it never becomes advisory., test_a_clean_generation_records_no_orphan_warning() (+3 more)

### Community 156 - "Request"
Cohesion: 0.22
Nodes (9): Request, _import_payload(), _posted_body(), _posted_cold_send(), _posted_plan_hash(), Read the ``body`` field from a urlencoded POST without python-multipart.      Ru, Read the import body, whether it arrived as JSON or as a form.      The extensio, Read the plan_hash the confirmation page put in the form. (+1 more)

### Community 157 - "test_renderer_owned_fields.py"
Cohesion: 0.25
Nodes (7): The guarantees that made four _validate_plan branches unreachable.  Task 39 item, The one input to resolve_header_location that comes from config., _offer_start falls back to « septembre 2026 », so there is always one., test_prose_canonicalization_removes_every_dash_the_letter_gate_looked_for(), test_the_built_title_always_carries_a_start_date(), test_the_profiles_own_fallback_is_itself_an_allowed_region(), test_the_resolved_header_location_is_always_one_allowed_region()

### Community 158 - "database_connection"
Cohesion: 0.29
Nodes (7): _candidate_name(), database_connection(), Connection, Yield one production database connection per request., Record which route the human confirmed. Not a status write.      The eventual de, The operator's name, for the download filename. Absent is not an error., _record_apply_route()

### Community 159 - "_generation_warnings"
Cohesion: 0.33
Nodes (7): _citation_warning(), _generation_warnings(), Any, Render an ISO timestamp as YYYY-MM-DD; pass other values through as text., The warning for a CV generated without a citation the advisor invented.      Rea, What this generation degraded, for the amber block on the detail page.      Appl, _ymd()

### Community 160 - "clear_match_scores"
Cohesion: 0.38
Nodes (6): clear_match_scores(), Connection, Return an SQL fragment + params restricting a query to one source., Drop match_scores rows so the next `score` pass re-evaluates those offers., RescoreResult, source_filter()

### Community 162 - "MenubarUnavailable"
Cohesion: 0.33
Nodes (6): MenubarUnavailable, Any, RuntimeError, Raised when the menu bar item cannot run on this machine., Import rumps or explain, in French, exactly how to get it., _require_rumps()

### Community 163 - "test_imap_transport_searches_domains_and_drops_lookalike_senders"
Cohesion: 0.40
Nodes (5): MonkeyPatch, The IMAP FROM search is a substring match, so the domain check is local.      `n, test_imap_connection_settings_use_existing_gmail_credentials(), test_imap_transport_searches_domains_and_drops_lookalike_senders(), test_imap_transport_uses_configured_readonly_folder_and_body_peek()

### Community 164 - "SendBlocked"
Cohesion: 0.50
Nodes (4): ColdSendDisabled, A rail (suppression list or daily cap) refuses the send. Not a failure., Live cold sending is disabled by configuration., SendBlocked

### Community 165 - "_no_real_sleeping"
Cohesion: 0.50
Nodes (4): _no_real_sleeping(), MonkeyPatch, Backoff between retries is real seconds; the test suite must not spend them., test_the_contacts_command_still_needs_a_company_without_targets()

### Community 166 - "test_script_toolchain_passes_windows_paths_as_distinct_subprocess_arguments"
Cohesion: 0.50
Nodes (4): MonkeyPatch, Path, test_script_toolchain_passes_windows_paths_as_distinct_subprocess_arguments(), test_script_toolchain_uses_baseline_orphan_gate_and_preserves_tracker_tabs()

### Community 167 - "test_openai_failures_use_application_rollback_and_redact_key"
Cohesion: 0.67
Nodes (4): Connection, Path, _queued_application(), test_openai_failures_use_application_rollback_and_redact_key()

### Community 168 - "counts"
Cohesion: 0.67
Nodes (3): counts(), Connection, Ready and queued offer applications, the two numbers worth a glance.

## Knowledge Gaps
- **171 isolated node(s):** `manifest_version`, `name`, `version`, `description`, `https://*.linkedin.com/*` (+166 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `observable_controls` to `test_bullet_ceiling.py`, `_FakeLocator`, `test_routing.py`, `mailer.py`, `connect`, `test_registry.py`, `wttj.py`, `france_travail.py`, `_FakePage`, `cli.py`, `test_email_alerts.py`, `ClientCredentialsToken`, `test_labonnealternance.py`, `SendBlocked`, `test_cold_outreach.py`, `_FakePage`, `Path`, `test_form_learning.py`, `_reject_unsupported_tokens`, `Connection`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Why does `load_fact_bank()` connect `load_fact_bank` to `dashboard.py`, `_Toolchain`, `test_the_minimum_is_above_the_alert_card_average`, `test_generic_vocabulary.py`, `test_keyword_router_still_misroutes_the_villeneuve_offer`, `test_registry.py`, `test_provenance_tiers.py`, `email_alerts.py`, `test_cv_completeness.py`, `OfferRecord`, `OpenAITailoringAdvisor`, `test_tech_additions.py`, `test_letter_locked_fields.py`, `test_mailer.py`, `test_designation_numbers.py`, `test_fact_id_consistency.py`, `profile.py`, `test_designation_numbers.py`, `_AnchorParser`, `apply_matching_profile_cmd`, `test_variant_selection.py`, `labonnealternance.py`, `test_profile_domain_anchor.py`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `TailoringError` connect `dashboard.py` to `_client`, `create_app`, `test_dedup.py`, `get_settings`, `vocabulary.py`, `test_generic_vocabulary.py`, `test_registry.py`, `launch_wttj_application`, `generate_application`, `Settings`, `test_cv_completeness.py`, `OfferRecord`, `resolve_fact_id`, `labonnealternance.py`, `ingest_source`, `test_letter_quality.py`, `test_designation_numbers.py`, `_reject_unsupported_tokens`, `CompanyRecord`, `_AnchorParser`, `FormField`, `_reject_placeholders`, `Any`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 62 inferred relationships involving `Settings` (e.g. with `ApplicantProfile` and `ApplyAdapter`) actually correct?**
  _`Settings` has 62 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `current_status()` (e.g. with `test_a_fatal_gate_still_aborts()` and `test_a_recoverable_gate_with_no_degradation_escalates_to_fatal()`) actually correct?**
  _`current_status()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `_payload()` (e.g. with `_plan()` and `_plan()`) actually correct?**
  _`_payload()` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `TailoringError` (e.g. with `_CompleteAdvisor` and `_IncompleteAdvisor`) actually correct?**
  _`TailoringError` has 17 INFERRED edges - model-reasoned connections that need verification._