# Graph Report - jobpilot  (2026-08-04)

## Corpus Check
- 177 files · ~216,802 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3866 nodes · 9835 edges · 154 communities (125 shown, 29 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 369 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b8d383f0`
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

## God Nodes (most connected - your core abstractions)
1. `Settings` - 117 edges
2. `current_status()` - 96 edges
3. `_payload()` - 92 edges
4. `TailoringError` - 84 edges
5. `OfferRecord` - 83 edges
6. `load_fact_bank()` - 76 edges
7. `create_app()` - 70 edges
8. `_Toolchain` - 67 edges
9. `get_settings()` - 61 edges
10. `OfferContext` - 60 edges

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

## Communities (154 total, 29 thin omitted)

### Community 0 - "test_downloads.py"
Cohesion: 0.05
Nodes (41): BaseException, Operation, ProgressRegistry, Any, datetime, Update a running operation. A key that is not running is ignored., Close an operation. The first outcome recorded wins.          A handled failure, Everything running, plus anything that finished very recently. (+33 more)

### Community 1 - "Request"
Cohesion: 0.08
Nodes (57): Path, Resolve one archived artefact, with the same discipline as the live one.      De, _safe_archive_path(), _safe_artifact_path(), _archives_for(), Generation, is_archive_stamp(), library_entries() (+49 more)

### Community 2 - "_candidate_name"
Cohesion: 0.06
Nodes (104): current_status(), _client(), _days_ago(), _events(), _no_advisor_client(), _offer_application(), Connection, MonkeyPatch (+96 more)

### Community 3 - "_client"
Cohesion: 0.10
Nodes (28): CatalogueEntry, default_catalogue(), load_variant_catalogue(), _parse_criteria(), _parse_shortcuts(), Path, RuntimeError, The CV catalogue offered to the advisor when it selects a variant.  The selectio (+20 more)

### Community 4 - "create_app"
Cohesion: 0.22
Nodes (15): AnthropicTailoringAdvisor, Claude Messages API adviser used when ``ANTHROPIC_API_KEY`` is set., _Client, _offer(), _plan_payload(), Any, Exception, Focused contracts for tailoring advisers and the script toolchain. (+7 more)

### Community 5 - "dashboard.py"
Cohesion: 0.08
Nodes (66): ExperienceFact, Match, Pattern, RuntimeError, _add_tech_additions(), _add_tech_keywords(), _contains(), _contains_any() (+58 more)

### Community 6 - "run_dashboard"
Cohesion: 0.11
Nodes (31): drop_unknown_citation(), Remove one unusable citation, or refuse when removing it would weaken the CV., bank(), _dropping_enabled(), _InventsForever, _plan(), Connection, MonkeyPatch (+23 more)

### Community 7 - "Path"
Cohesion: 0.14
Nodes (17): ApplicantProfile, Whether a stored selector still finds a control on the current page., The non-secret contact values entered into an ATS form., selector_matches_html(), build_prefill(), discard_mapping(), FormMapping, PrefillOutcome (+9 more)

### Community 8 - "test_routing.py"
Cohesion: 0.06
Nodes (83): Cursor, Decision, RouteId, _applicant_reason(), _artifacts(), _ats_prefill(), _email(), has_form_mapping() (+75 more)

### Community 9 - "mailer.py"
Cohesion: 0.09
Nodes (51): Show the email that would be sent for a ready application, then confirm (y/N)., send_cmd(), Remove configured secrets from exception text before display/logging., Settings, is_professional_address(), True only for well-formed addresses NOT on a personal free-provider domain., Whether a named mailbox on a professional domain needs extra approval., requires_personal_confirmation() (+43 more)

### Community 10 - "validate_cv.py"
Cohesion: 0.06
Nodes (53): check_orphans(), find_regressions(), Path, Return orphan metrics that are new or materially worse than the template., format_date(), main(), build_letter_html(), detect_github() (+45 more)

### Community 11 - "get_settings"
Cohesion: 0.10
Nodes (25): _correction_block(), _is_validator_rejection(), _json_object(), Raised when an external tailoring provider request fails., Raised when a tailoring provider rejects its API credentials., Raised when a tailoring provider rate-limits a request., Raised when a provider returns an unusable response., The advisor's reasoned CV pick, before any mechanical contract rule. (+17 more)

### Community 12 - "connect"
Cohesion: 0.08
Nodes (42): Normalized DTOs that every source emits, decoupled from source-specific JSON., derive_fields(), _Derived, Re-derive alert card fields (company / city / workplace / easy-apply) in place., Re-derive one offer's card fields from the text that was stored for it.      Pur, _AlertAnchor, _anchors(), _Card (+34 more)

### Community 13 - "test_descriptions.py"
Cohesion: 0.10
Nodes (50): backfill_descriptions(), BackfillResult, clear_match_scores(), is_synthesized(), Connection, Synthesise matchable text for offers that arrive with no description.  Job-alert, Return an SQL fragment + params restricting a query to one source., Regenerate synthesised descriptions for stored offers whose text is thin.      I (+42 more)

### Community 14 - "test_generic_vocabulary.py"
Cohesion: 0.08
Nodes (46): extract_template_context(), pick_variant(), Pick the best of 21 variants from missions, then apply contract rules.      Sinc, Read all editable choices without altering the template., bank(), _plan(), Task 40 amendment: bullets had a floor and no ceiling.  _validate_experience_com, The ceiling does not soften the other direction. (+38 more)

### Community 15 - "apply_assist.py"
Cohesion: 0.12
Nodes (42): counts(), Any, Connection, datetime, The tracker: every application, one table, read-only.  Deliberately not a Google, Every offer application, optionally narrowed to one status.      ``include_stale, Statuses that actually occur, so the filter offers no dead options., Export exactly the visible rows, in the visible column order. (+34 more)

### Community 16 - "test_skim.py"
Cohesion: 0.10
Nodes (53): available_sources(), _create_application(), ignore_offer(), promote_offer(), Connection, datetime, Row, ValueError (+45 more)

### Community 17 - "contacts.py"
Cohesion: 0.10
Nodes (36): Add an address to the cold-mail suppression list (honored before sends)., suppress_cmd(), _candidate_name(), ContactCandidate, discover_and_store(), DiscoverySource, draft_cold_email(), draft_linkedin_note() (+28 more)

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
Cohesion: 0.05
Nodes (49): ConnectionFactory, Event, HTTPStatusError, _drain(), IngestResult, Ingestion orchestrator: pull normalized records from a Source into the DB.  Idem, Pull everything the source has, before any write begins.      ``fetch_companies`, Append one row to source_runs. Does not commit; the caller owns that.      A fai (+41 more)

### Community 23 - "france_travail.py"
Cohesion: 0.10
Nodes (24): _first_nonempty(), FranceTravailSource, _map_contact_email(), _map_contract(), _map_duration_months(), map_offer(), Any, Parse '... - 12 Mois' style durations from typeContratLibelle. (+16 more)

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
Cohesion: 0.09
Nodes (23): adapter_for_url(), ApplyAdapter, _BaseAdapter, GreenhouseAdapter, LeverAdapter, Common adapter interface for a best-effort ATS prefill., Shared plan building and non-submitting form interaction., Return the owning ATS adapter, if the saved offer URL is recognized. (+15 more)

### Community 28 - "cli.py"
Cohesion: 0.27
Nodes (11): Connection, Whether pressing submit is allowed on this domain. Default: no.      Prefill is, Flip the per-domain submit gate. Deliberately has no global counterpart., set_submit_enabled(), submit_enabled(), Connection, Prefill is automatic; pressing submit is not., test_the_per_domain_submit_gate_defaults_to_off() (+3 more)

### Community 29 - "test_desktop_shell.py"
Cohesion: 0.07
Nodes (40): CaptureFixture, dashboard_already_running(), Whether something is already listening on the dashboard's port.      A connect p, The menu bar text. Short: it competes with every other item up there., title(), _bound_port(), _fake_macos(), _module_level_imports() (+32 more)

### Community 30 - "generate_application"
Cohesion: 0.06
Nodes (34): CompletedProcess, Connection, date, Path, Protocol, _check_orphans(), _contains_generated_orphan(), DocumentToolchain (+26 more)

### Community 31 - "test_contacts.py"
Cohesion: 0.10
Nodes (27): ModuleType, JobPilot: personal job application pipeline for the French IT/cybersecurity mark, _application(), _ConnectionProxy, Connection, Exception, Path, CLI coverage for offer document generation and cold-application approval. (+19 more)

### Community 32 - "test_email_alerts.py"
Cohesion: 0.09
Nodes (43): Message, GmailIMAP, html_of(), LinkedInAlertSource, Minimal read-only Gmail IMAP client., Fetch recent mail sent from `domains` (or any of their subdomains).          The, Return the best HTML (or plain-text) body of an email message., Return the lowercased domain of the address in a `From` header.      Parses the (+35 more)

### Community 33 - "test_labonnealternance.py"
Cohesion: 0.13
Nodes (33): _fixture(), _NoWait, LogCaptureFixture, La Bonne Alternance through the API Apprentissage: mapping, rails, ingestion.  E, The endpoint has no pagination, so this is the volume knob that exists., A full ingest reads both lists; it must not pay for the search twice., The live API really does repeat an offer inside one response., A company that has posted nothing must not appear in the review queue. (+25 more)

### Community 34 - "_Toolchain"
Cohesion: 0.07
Nodes (30): Path, Task 43 item 2: the browser extension, and the line it must not cross.  The exte, Two files naming the same three sites. A content script runs in the     page's o, Most of the time JobPilot is not running. The extension has to be     invisible, A rejected promise with no catch surfaces as an unhandled rejection,     which i, One obvious place, with the warning next to it., The requirement that matters most in a year: when LinkedIn changes its     gener, The biggest element on a page is a wrapper holding the whole page. (+22 more)

### Community 35 - "email_alerts.py"
Cohesion: 0.08
Nodes (34): _advisor_prompt(), Every id the advisor may cite, flattened out of the context it was given.      D, valid_fact_ids(), Listing the numbers is not enough on its own: the failure was a dropped +., test_the_prompt_carries_the_closed_number_set(), test_the_prompt_forbids_introducing_a_figure(), test_the_prompt_says_to_copy_the_figure_exactly(), test_the_prompt_says_to_write_the_sentence_without_a_number() (+26 more)

### Community 36 - "test_alert_card_fields.py"
Cohesion: 0.09
Nodes (38): _citation_warning(), _generation_warnings(), Any, Render an ISO timestamp as YYYY-MM-DD; pass other values through as text., The warning for a CV generated without a citation the advisor invented.      Rea, What this generation degraded, for the amber block on the detail page.      Appl, _ymd(), as_dicts() (+30 more)

### Community 37 - "Settings"
Cohesion: 0.07
Nodes (54): FactBank, GenerationWarning, _advise_and_tailor(), _advisor_fact_context(), _cap_experience_selection(), _contact_fields(), _cv_locked_fields(), DroppedCitation (+46 more)

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
Cohesion: 0.11
Nodes (31): Validate the one JSON contract shared by every advisor provider., Task 39 demoted this to advisory.      A tool listed under two categories is cos, test_duplicate_tool_across_categories_warns_without_blocking(), _experience_content(), _FabricatingAdvisor, _gemini_shaped_payload(), _offer(), Connection (+23 more)

### Community 43 - ".from_mapping"
Cohesion: 0.13
Nodes (34): applications_by_status(), Offer applications in one status, newest first, with their age.      Returns the, _client(), _days_ago(), _offer_application(), Connection, MonkeyPatch, TestClient (+26 more)

### Community 44 - "test_cold_outreach.py"
Cohesion: 0.14
Nodes (18): FormLearningError, mapping_is_complete(), mappings_for(), put_mapping(), ValueError, Raised when a mapping would break one of this module's hard rules., Write one mapping. Rejects a profile_field outside the closed enum., Whether ``domain`` has enough of a mapping to be worth calling a route. (+10 more)

### Community 45 - "_FakePage"
Cohesion: 0.24
Nodes (20): _events(), _FakeLauncher, _FakePage, Connection, Path, Row, WTTJ inline application stays human-approved and dry-run by default., _ready_wttj_application() (+12 more)

### Community 46 - "MissingCredentialError"
Cohesion: 0.09
Nodes (47): ingest_source(), Run one source end to end. Commits once at the end for atomicity.      Two phase, _consecutive_failures(), _last_runs(), Any, Connection, Row, Leading failures only: one success resets the streak. (+39 more)

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
Cohesion: 0.13
Nodes (20): _application_for_assist(), _application_for_wttj(), ApplyAssistError, AssistResult, _fallback(), launch_application_assist(), launch_wttj_application(), _open_for_human() (+12 more)

### Community 51 - "test_tech_additions.py"
Cohesion: 0.15
Nodes (26): bank(), _offer(), LogCaptureFixture, Zone 3 may add a keyword, but only one he has and the offer asked for., Reorder-only remains the default and the common case., Genuinely his, but padding: the offer did not ask for it., Presence in the bank is necessary, never sufficient., Derived from the file, not a magic number. (+18 more)

### Community 52 - "load_fact_bank"
Cohesion: 0.08
Nodes (45): facts_cmd(), Print the provenance fact bank grouped for human review., _boolean(), build_cv_title(), CertificationFact, _claim_list(), EducationFact, _entry_claim() (+37 more)

### Community 53 - "CompanyRecord"
Cohesion: 0.13
Nodes (36): clean_description(), Collapse the whitespace a copied page carries, and keep the rest., _client(), _fake_score(), _offer(), Connection, TestClient, Task 43 item 1: an offer description captured from an open page.  LinkedIn and I (+28 more)

### Community 54 - "labonnealternance.py"
Cohesion: 0.11
Nodes (17): _InteractiveShapedAdvisor, Human loop: always rejected, and never re-prompted automatically., _InventsThenRecovers, Connection, LogCaptureFixture, Path, Task 37 item 2: give the unknown-id retry something to work with.  An unknown fa, Cites an id that exists nowhere, for a chosen number of attempts. (+9 more)

### Community 55 - "ingest_source"
Cohesion: 0.10
Nodes (18): Any, CvProfile, _canonicalize_prose(), _justification(), Normalize model punctuation that the document contract forbids.      This is a l, Renderer-owned CV header location; the advisor has no say in it.      Prefers th, One employer's bullets, chosen from its facts rather than written.      The skil, One project, and which of its facts describes it. Inserted verbatim. (+10 more)

### Community 56 - "pick_variant"
Cohesion: 0.16
Nodes (11): BrowserLauncher, _ConfirmationBaseline, _Locator, _Page, PrefillPlan, Protocol, The actions selected from a page's current HTML fixture/markup., A launch seam: production opens Playwright, tests supply a stub page. (+3 more)

### Community 57 - "test_fact_id_resolution.py"
Cohesion: 0.14
Nodes (30): ApplyOutcome, approve_application(), Any, Connection, Record human approval, transition, and generate through one shared path.      ``, The result shared by the CLI and dashboard approval surfaces., invention_report(), How often the advisor cites an id that does not exist, and whether it recovers. (+22 more)

### Community 58 - "test_letter_locked_fields.py"
Cohesion: 0.18
Nodes (19): bank(), _letter(), _offer(), A letter is prose about a career; a CV is slots the renderer fills., Naming a real-sounding employer he never had is a fabrication, not prose., The renderer injects the address block; the body repeating it is a bug., Otherwise the test above would prove nothing about scope., The bank's own text names nothing it should not; selection is the check. (+11 more)

### Community 60 - "test_letter_quality.py"
Cohesion: 0.22
Nodes (17): _default_letter(), french_de_elision(), Return « de <noun> » or « d'<noun> », applying French elision.      Elides befor, _render_sourced_letter(), _validate_letter_body(), _letter(), _offer(), Letter quality: French elision and the 'Entreprise' placeholder rejection. (+9 more)

### Community 61 - "test_mailer.py"
Cohesion: 0.04
Nodes (87): add_contact_cmd(), apply_cmd(), backfill_descriptions_cmd(), contacts_cmd(), _csv(), daemon_cmd(), dashboard_cmd(), draft_cold_cmd() (+79 more)

### Community 62 - "models.py"
Cohesion: 0.25
Nodes (18): daemon_status(), Report daemon liveness from the heartbeat file, or admit it is unknown., _client(), fixture_bank(), Connection, MonkeyPatch, Path, TestClient (+10 more)

### Community 63 - "reparse_alerts"
Cohesion: 0.17
Nodes (19): application(), Connection, Amber, not red: the document is usable, it just needs a look., test_the_detail_page_shows_the_warning_in_amber(), _generation_failed_detail(), Any, Connection, LogCaptureFixture (+11 more)

### Community 64 - "test_designation_numbers.py"
Cohesion: 0.06
Nodes (53): LookupError, Request, open_manually(), The manual_open route: open the offer, copy the letter, submit nothing.      A l, ApplicationGenerationError, ApplicationNotFoundError, ApplicationNotQueuedError, archive_artifacts() (+45 more)

### Community 65 - "test_fact_id_consistency.py"
Cohesion: 0.20
Nodes (15): bank(), _bank_payload(), Path, Task 35 item 2: a fact bank whose claim ids do not extend their entry is invalid, The real bank must satisfy the rule the loader now enforces., This is the exact shape the Baïfall entry had., Projects have the same shape as experience, so they get the same rule., `experience.baifallX` starts with the entry id as a STRING but is a     differen (+7 more)

### Community 66 - "review.py"
Cohesion: 0.18
Nodes (18): _AlertSource, _ingest_then_import(), Connection, Row, Task 43 item 5: an imported description is never overwritten.  The user opens th, `force` exists to re-compose rows the normal pass skips. That widening     must, The guard must be `imported_at`, not an accident that stopped the     backfill w, A source that keeps offering the thin card, exactly as an alert does. (+10 more)

### Community 67 - "ingest_source"
Cohesion: 0.18
Nodes (30): _answer(), _decision(), _offer(), Any, Connection, Exception, LogCaptureFixture, Path (+22 more)

### Community 68 - "_AnchorParser"
Cohesion: 0.22
Nodes (11): source_id(), _insert_offer(), INSERT OR IGNORE one offer. Returns True if a new row was created., content_hash(), sha256(lower(title + company + first 500 chars of description)).      This is th, _offer(), Connection, content_hash dedup + INSERT OR IGNORE behavior. (+3 more)

### Community 69 - "test_preview.py"
Cohesion: 0.23
Nodes (19): _fake_clone(), _git(), CompletedProcess, Path, Task 41: one command after a merge, and it refuses rather than half-updates.  sc, The loud refusal. A fast-forward carries uncommitted work with it., The point of the conditions: the two slow steps cost nothing here., Kickstarting the agents is unconditional: new code is only running once     the (+11 more)

### Community 70 - "vocabulary.py"
Cohesion: 0.17
Nodes (17): live_db(), _Observed, _offer(), Connection, Exception, Path, Task 41 follow-up: the write lock is not held across the network.  Task 41 put W, Draining buys the lock back without giving up atomicity — which is what     comm (+9 more)

### Community 71 - "UnknownFactIdError"
Cohesion: 0.08
Nodes (45): _alert_source_clause(), Connection, Restrict to one alert source, or to all of them when none is named., Re-derive company / city / workplace / easy-apply for stored alert offers., reparse_alerts(), ReparseResult, parse_linkedin(), Extract jobs from a LinkedIn job-alert email. (+37 more)

### Community 72 - "Baifall Dream Stage - Reference Document (v3)"
Cohesion: 0.17
Nodes (11): Baifall Dream Stage - Reference Document (v3), Bloc HTML de reference (3 bullets), Bullet 1 (commun, accompli) - 167 car., rendu sur 2 lignes, Bullet 2 (commun, nominal, perimetre complet) - 127 car., 1 ligne, Bullet 3 : declinaisons par variante, Context, Principe v3 : perimetre nominal complet, Regle pour la date (+3 more)

### Community 73 - "test_facts.py"
Cohesion: 0.12
Nodes (25): FormField, infer_profile_field(), One control's shape. Deliberately has nowhere to put a typed value., Everything naming this field, with separators folded to spaces.          Real fo, Name the reason this field may never be mapped, or None if it may.      Refused:, Which profile field this control wants, or None to leave it to the human., Record mappings for one manually submitted form. Values are never stored.      C, Every refusal category present in a form, for reporting to the human. (+17 more)

### Community 74 - "test_progress.py"
Cohesion: 0.13
Nodes (17): enrich_offer(), is_thin(), Replace a thin description in place; richer descriptions are left alone.      Ca, True when a description is too short to be worth embedding on its own., OfferRecord, One normalized offer, ready to insert into the offers table., Coerce enum-constrained fields to legal values (schema CHECK safety)., EmailAlertError (+9 more)

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

### Community 80 - "_reject_unsupported_tokens"
Cohesion: 0.14
Nodes (20): Container, _designation_spans(), _proper_nouns(), ProvenanceScope, Everything true of the career the generated text is describing.      Generated t, Raised when generated prose states a figure the bank does not contain.      A si, Check every designation against the scope; return what it covers.      Designati, Blank out validated designations, keeping every other offset intact. (+12 more)

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
Cohesion: 0.12
Nodes (21): Connection, Path, Nothing is weakened: a fabrication ends the run exactly as before., An invented figure is recoverable — the retry is handed the real ones —     but, test_a_fatal_gate_still_aborts(), test_a_recoverable_gate_with_no_degradation_escalates_to_fatal(), test_an_advisory_gate_never_blocks(), test_the_library_and_tracker_mark_a_degraded_application() (+13 more)

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
Cohesion: 0.09
Nodes (29): MissingCredentialError, RuntimeError, Raised when a required secret is absent. We ask; we never silently mock., RateLimiter, Minimum-delay-per-domain limiter. Blocks until the next call is allowed., _city(), _company_name(), _contract_type() (+21 more)

### Community 110 - "test_designation_numbers.py"
Cohesion: 0.15
Nodes (18): bank(), _in_bank(), LogCaptureFixture, A standard's digits name a thing; a metric's digits measure one., The anti-fabrication guarantee is not weakened by designation handling., Only the designation's own span is exempt from the number rule., unsupported number 27001' was rejecting real, bank-backed vocabulary., Judge as the letter is judged: no entry, so the whole bank answers. (+10 more)

### Community 111 - "_AnchorParser"
Cohesion: 0.06
Nodes (58): allowed_numbers(), _bank_parts(), _generated_bullets(), letter_scope(), _normalized_number(), _offer_identity(), _organisation_names(), Everything the verified bank says the candidate has actually touched.      Only (+50 more)

### Community 112 - "Connection"
Cohesion: 0.14
Nodes (13): attempt(), describe(), fromSelectors(), hostKey(), largestTextBlock(), send(), textOf(), toast() (+5 more)

### Community 113 - "apply_matching_profile_cmd"
Cohesion: 0.06
Nodes (36): AmbiguousFactIdError, _fact_id_key(), _guessed_section(), nearest_entry_claim_ids(), Raised when a citation matches no fact id, even after normalisation.      ``sect, Fold separator and case differences, and nothing else, for comparison., Raised when a citation could be several facts. Never guess between them., Map a cited id onto a real fact id, accepting only unambiguous matches.      Mat (+28 more)

### Community 114 - "test_variant_selection.py"
Cohesion: 0.09
Nodes (26): _advise(), ambiguous_bank(), bank(), _offer(), Any, LogCaptureFixture, Path, Citation ids are matched tolerantly; what may be claimed is unchanged. (+18 more)

### Community 115 - "labonnealternance.py"
Cohesion: 0.13
Nodes (27): FastAPI, create_app(), Build the local dashboard, with injectable generation collaborators for tests., Freshness, How old one offer is, and how sure we are of that., application_detail(), event_history(), import_supersedes_documents() (+19 more)

### Community 116 - "test_profile_domain_anchor.py"
Cohesion: 0.19
Nodes (14): _offer(), Connection, Systemic recovery at the generated-prose and document-layout boundaries., Naming the employer is what a motivation letter does.      The rule was never lo, _selection_and_template(), test_a_valid_custom_profile_phrase_is_preserved_exactly(), test_an_invalid_profile_phrase_uses_the_variant_fallback(), test_an_unsupported_candidate_claim_remains_a_hard_failure() (+6 more)

### Community 117 - "test_mailer.py"
Cohesion: 0.28
Nodes (17): Combined application + cold-mail sends recorded for today (UTC)., sends_today(), _events(), Connection, EmailMessage, Exception, Path, Application email sending: rails, transitions, and events (mocked SMTP). (+9 more)

### Community 118 - "_application"
Cohesion: 0.27
Nodes (18): _application(), _client(), Connection, TestClient, Task 43 item 3: pasting the description is a first-class path.  Not a fallback f, The card is 113 characters and the CV was tailored against it. Saying so     is, A rejected paste must not look like a lost page, and must not have     replaced, One endpoint, two representations. The JSON caller sends no     application_id a (+10 more)

### Community 119 - "FormField"
Cohesion: 0.28
Nodes (17): OpenAITailoringAdvisor, OpenAI-compatible Chat Completions adviser., _offer(), _openai_response(), _plan_payload(), Any, Connection, Path (+9 more)

### Community 120 - "_reject_placeholders"
Cohesion: 0.16
Nodes (17): No rendered CV may carry bracketed text. Task 44 item 1.      '[offer duration]', _reject_placeholders(), Task 44 item 1: no rendered CV may carry a bracketed placeholder.  « Stage de [o, If a hand-written template carried brackets, the guard would abort every     gen, The regression, quoted from application 37's rendered CV., Tier is the whole decision here: recoverable would mean retrying, and     the mo, Half the templates are entity-encoded, so the scan reads decoded text.     A pla, No template carries one today. This is about a future stylesheet edit     not fa (+9 more)

### Community 121 - "Any"
Cohesion: 0.17
Nodes (13): SimpleNamespace, build_advisor(), InteractiveTailoringAdvisor, Terminal prompts used when interactive tailoring is selected., Resolve TAILORING_PROVIDER to a concrete mode, without building anything.      C, Select the configured provider without silently bypassing missing keys., resolve_provider(), MonkeyPatch (+5 more)

### Community 122 - "test_form_learning.py"
Cohesion: 0.16
Nodes (12): observable_controls(), Every fillable control's *shape*, for form learning. Never its contents.      ``, fields_from_html(), Read a page's controls as shapes. Values are stripped before we see them., _fields(), Task 34.D: form learning — what may be recorded, and what may never be.  This ta, Scan every column of the table for the sentinel values used above., One enforcement point: values are stripped before this module sees them. (+4 more)

### Community 124 - "_reject_unsupported_tokens"
Cohesion: 0.25
Nodes (13): ingest_cmd(), Fetch offers from a source (or all sources) into the database., enabled_sources(), _enablement(), is_enabled(), Read config/sources.yaml. Unlisted sources default to enabled., Registered sources that are enabled in config, in registration order., Path (+5 more)

### Community 125 - "gate"
Cohesion: 0.14
Nodes (25): list_outreach_targets(), Companies an ingestion source flagged as likely to hire an alternant.      These, _backfill_company_source(), get_or_create_company(), Connection, Teach an existing company row where it came from, once.      A company first see, CompanyRecord, _no_real_sleeping() (+17 more)

### Community 126 - "Connection"
Cohesion: 0.22
Nodes (4): _AnchorParser, HTMLParser, Collect anchors plus nearby table/list-card text without dependencies., _TextContainer

### Community 128 - "Path"
Cohesion: 0.09
Nodes (30): _create_offer(), find_offer_by_url(), import_offer_description(), ImportResult, _is_tracking(), normalize_offer_url(), OfferImportError, Any (+22 more)

### Community 129 - "test_bullet_ceiling.py"
Cohesion: 0.15
Nodes (21): ATSSource, infer_contract(), load_targets(), map_greenhouse(), map_lever(), map_smartrecruiters(), _ms_to_iso(), Any (+13 more)

### Community 130 - "score"
Cohesion: 0.07
Nodes (48): apply_matching_profile(), CvProfile, load_cv_profile(), load_matching_profile(), MatchingProfile, MatchingProfileError, Path, Write the vocabulary onto the profile singleton. Returns {field: (before, after) (+40 more)

### Community 131 - "apply_matching_profile"
Cohesion: 0.09
Nodes (37): SentenceTransformer, apply_matching_profile_cmd(), Connection, _queue_snapshot(), Apply config/matching_profile.yaml and report what it changed.      Re-scoring i, Count what currently clears the bar, for an honest before/after., Re-evaluate every offer against the new vocabulary.      ``jobpilot score`` only, Score all unscored offers and queue those above threshold. (+29 more)

### Community 132 - "observable_controls"
Cohesion: 0.07
Nodes (32): _Control, _ControlParser, _controls_from_html(), _css_attribute_value(), FillAction, _first_matching_selector(), _Form, _FormParser (+24 more)

### Community 134 - "test_dedup.py"
Cohesion: 0.07
Nodes (38): Apply the mechanical contract and encoding rules to a chosen slug.      These ar, The stage contract line, built from what is known.      Task 44 item 1: this is, Restore the hand-reviewed template phrase without treating it as AI prose., _restore_template_profile_domain(), _stage_contract_phrase(), variant_for_slug(), test_layout_fallback_restores_each_trusted_template_phrase(), _profile_of() (+30 more)

### Community 135 - "update.sh"
Cohesion: 0.60
Nodes (3): changed_since_pull(), die(), update.sh script

### Community 136 - "scheduler_status"
Cohesion: 0.09
Nodes (43): age_in_days(), annotate(), describe(), drop_stale(), _label(), max_offer_age_days(), _parse(), parse_timestamp() (+35 more)

### Community 138 - "mappings_for"
Cohesion: 0.22
Nodes (7): _plan(), Task 41: the header location is found by its own marker, not by its neighbours., The header is a fixed-width line; the span must not consume any of it., The header location is renderer-owned: it comes from the offer's city., The premise of the fix, asserted rather than assumed.      If this ever fails th, test_the_marker_adds_no_visible_text(), test_the_templates_really_do_disagree_on_both_encodings()

### Community 139 - "vocabulary.py"
Cohesion: 0.10
Nodes (24): _F, FactClaim, gate(), Label what this function refuses, and what refusing costs.      Attached to the, The tier this failure carries HERE.      An unclassified error is fatal. That de, A selected fact must be a real, reviewed fact OF THAT ENTRY.      This is the wh, What a gate firing is allowed to cost.      Task 39. Seven consecutive generatio, Tier (+16 more)

### Community 140 - "import_origin_allowed"
Cohesion: 0.50
Nodes (4): import_origin_allowed(), True when `origin` may POST to IMPORT_PATH.      Host-suffix matching, so ``www., test_every_other_origin_is_rejected(), test_the_origins_the_feature_needs_are_allowed()

### Community 142 - "_Advisor"
Cohesion: 0.20
Nodes (9): content_scripts, description, host_permissions, manifest_version, name, version, https://*.indeed.fr/*, https://*.linkedin.com/* (+1 more)

### Community 146 - "test_ingest_idempotent.py"
Cohesion: 0.38
Nodes (8): FakeSource, Connection, Re-running ingest must never duplicate rows (constitution idempotency rule)., _sample(), test_company_deduped_across_offers_and_runs(), test_first_run_inserts_all(), test_last_run_at_updated(), test_second_run_inserts_nothing()

### Community 149 - "test_registry.py"
Cohesion: 0.07
Nodes (40): Logger, Put text on the system clipboard, or say plainly that it could not.  The manual_, _env_bool(), get_settings(), _path(), Configuration and path resolution. Secrets come from .env only (never mocked)., get_logger(), Central logging setup. Library code logs here; it never uses print(). (+32 more)

## Knowledge Gaps
- **171 isolated node(s):** `manifest_version`, `name`, `version`, `description`, `https://*.linkedin.com/*` (+166 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `mailer.py` to `test_bullet_ceiling.py`, `observable_controls`, `_FakeLocator`, `Path`, `test_routing.py`, `connect`, `test_registry.py`, `SourcedBullet`, `france_travail.py`, `wttj.py`, `_FakePage`, `test_email_alerts.py`, `test_labonnealternance.py`, `_FakePage`, `MissingCredentialError`, `resolve_fact_id`, `pick_variant`, `models.py`, `test_designation_numbers.py`, `test_progress.py`, `Path`, `_reject_unsupported_tokens`, `Connection`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Why does `load_fact_bank()` connect `load_fact_bank` to `dashboard.py`, `run_dashboard`, `test_dedup.py`, `vocabulary.py`, `test_generic_vocabulary.py`, `test_provenance_tiers.py`, `email_alerts.py`, `test_cv_completeness.py`, `OfferRecord`, `OpenAITailoringAdvisor`, `test_tech_additions.py`, `test_letter_locked_fields.py`, `test_mailer.py`, `test_designation_numbers.py`, `test_fact_id_consistency.py`, `profile.py`, `test_designation_numbers.py`, `_AnchorParser`, `apply_matching_profile_cmd`, `test_variant_selection.py`, `labonnealternance.py`, `test_profile_domain_anchor.py`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `TailoringError` connect `dashboard.py` to `_candidate_name`, `create_app`, `test_dedup.py`, `_Toolchain`, `get_settings`, `vocabulary.py`, `test_generic_vocabulary.py`, `launch_wttj_application`, `generate_application`, `Settings`, `test_cv_completeness.py`, `OfferRecord`, `labonnealternance.py`, `ingest_source`, `test_letter_quality.py`, `test_designation_numbers.py`, `ingest_source`, `_reject_unsupported_tokens`, `CompanyRecord`, `_AnchorParser`, `apply_matching_profile_cmd`, `test_variant_selection.py`, `test_profile_domain_anchor.py`, `FormField`, `_reject_placeholders`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Are the 62 inferred relationships involving `Settings` (e.g. with `ApplicantProfile` and `ApplyAdapter`) actually correct?**
  _`Settings` has 62 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `current_status()` (e.g. with `test_a_fatal_gate_still_aborts()` and `test_a_recoverable_gate_with_no_degradation_escalates_to_fatal()`) actually correct?**
  _`current_status()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `_payload()` (e.g. with `_plan()` and `_plan()`) actually correct?**
  _`_payload()` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `TailoringError` (e.g. with `_CompleteAdvisor` and `_IncompleteAdvisor`) actually correct?**
  _`TailoringError` has 17 INFERRED edges - model-reasoned connections that need verification._