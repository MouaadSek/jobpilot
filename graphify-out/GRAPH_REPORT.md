# Graph Report - jobpilot  (2026-08-05)

## Corpus Check
- 178 files · ~219,205 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3886 nodes · 10193 edges · 153 communities (136 shown, 17 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 616 edges (avg confidence: 0.53)
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
- _approve
- test_renderer_owned_fields.py
- counts

## God Nodes (most connected - your core abstractions)
1. `Settings` - 117 edges
2. `current_status()` - 100 edges
3. `TailoringError` - 92 edges
4. `_payload()` - 92 edges
5. `OfferRecord` - 83 edges
6. `load_fact_bank()` - 81 edges
7. `FactBank` - 74 edges
8. `_Toolchain` - 72 edges
9. `create_app()` - 70 edges
10. `OfferContext` - 70 edges

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

## Communities (153 total, 17 thin omitted)

### Community 0 - "test_downloads.py"
Cohesion: 0.05
Nodes (41): BaseException, Operation, ProgressRegistry, Any, datetime, Update a running operation. A key that is not running is ignored., Close an operation. The first outcome recorded wins.          A handled failure, Everything running, plus anything that finished very recently. (+33 more)

### Community 1 - "Request"
Cohesion: 0.08
Nodes (54): Resolve one archived artefact, with the same discipline as the live one.      De, _safe_archive_path(), _archives_for(), Generation, is_archive_stamp(), library_entries(), LibraryEntry, _mtime_iso() (+46 more)

### Community 2 - "_candidate_name"
Cohesion: 0.07
Nodes (90): SimpleNamespace, _client(), _days_ago(), _events(), _no_advisor_client(), _offer_application(), Connection, MonkeyPatch (+82 more)

### Community 3 - "_client"
Cohesion: 0.06
Nodes (56): CatalogueEntry, default_catalogue(), load_variant_catalogue(), _parse_criteria(), _parse_shortcuts(), Path, The CV catalogue offered to the advisor when it selects a variant.  The selectio, Read the two-column selection table, skipping its header and separator. (+48 more)

### Community 4 - "create_app"
Cohesion: 0.15
Nodes (19): AnthropicTailoringAdvisor, Claude Messages API adviser used when ``ANTHROPIC_API_KEY`` is set., _Client, _offer(), _plan_payload(), Any, Exception, MonkeyPatch (+11 more)

### Community 5 - "dashboard.py"
Cohesion: 0.05
Nodes (97): Container, Match, Pattern, _add_tech_additions(), _add_tech_keywords(), _cap_experience_selection(), _contact_fields(), _contains() (+89 more)

### Community 6 - "run_dashboard"
Cohesion: 0.19
Nodes (17): _dropping_enabled(), _InventsForever, Connection, MonkeyPatch, Path, Task 37 item 3: degradation. Shipped off, turned ON by Task 39.  If the advisor, Turning it off restores the old behaviour exactly., Enabling degradation does not make everything droppable. (+9 more)

### Community 7 - "Path"
Cohesion: 0.11
Nodes (27): _fit(), _offer(), Task 44 item 2: the CV title has a layout budget.  « Ingénieur en data - Optimis, The bug, and the reason step 2 exists at all: the head of that title is     a pe, Cutting keeps the head clause, which is the role only when the posting     is we, The floor must not swallow the case step 2 exists for., The template's own title ends 'Alternance M2 dès Septembre 2026'. Reused     ver, Step 3 is the floor, so it must never itself overflow — otherwise the     degrad (+19 more)

### Community 8 - "test_routing.py"
Cohesion: 0.09
Nodes (60): Cursor, _artifacts(), Path, Resolve the one route this application would go out by. Writes nothing., A route the offer qualified for, and the reason it cannot be used., The resolved plan for one application. Carries no state and stores none., Fingerprint of exactly the inputs that decided this route.          Stateless by, resolve_route() (+52 more)

### Community 9 - "mailer.py"
Cohesion: 0.08
Nodes (47): Show the email that would be sent for a ready application, then confirm (y/N)., send_cmd(), _as_utc(), _build_message(), build_sender(), ColdEmailPreparation, ColdSendDisabled, daily_cap_reached() (+39 more)

### Community 10 - "validate_cv.py"
Cohesion: 0.06
Nodes (53): check_orphans(), find_regressions(), Path, Return orphan metrics that are new or materially worse than the template., format_date(), main(), build_letter_html(), detect_github() (+45 more)

### Community 11 - "get_settings"
Cohesion: 0.07
Nodes (72): ExperienceFact, FactBankError, FactClaim, ValueError, Raised when the committed fact bank is malformed or ambiguous., One atomic statement that generated content may cite., GenerationWarning, One thing the reviewer is being asked to check by eye. (+64 more)

### Community 12 - "connect"
Cohesion: 0.10
Nodes (30): derive_fields(), _Derived, Re-derive alert card fields (company / city / workplace / easy-apply) in place., Re-derive one offer's card fields from the text that was stored for it.      Pur, _card_fields(), is_noise(), is_title_echo(), parse_card_line() (+22 more)

### Community 13 - "test_descriptions.py"
Cohesion: 0.10
Nodes (50): backfill_descriptions(), clear_match_scores(), is_synthesized(), Connection, Return an SQL fragment + params restricting a query to one source., Regenerate synthesised descriptions for stored offers whose text is thin.      I, Drop match_scores rows so the next `score` pass re-evaluates those offers., True when `description` was produced by this module. (+42 more)

### Community 14 - "test_generic_vocabulary.py"
Cohesion: 0.11
Nodes (34): extract_template_context(), pick_variant(), Pick the best of 21 variants from missions, then apply contract rules.      Sinc, Read all editable choices without altering the template., The model had never been told there was one., test_the_prompt_states_the_ceiling(), unsupported number 27001' was rejecting real, bank-backed vocabulary., test_the_observed_failure_no_longer_fails_a_generation() (+26 more)

### Community 15 - "apply_assist.py"
Cohesion: 0.17
Nodes (32): Any, Every offer application, optionally narrowed to one status.      ``include_stale, Export exactly the visible rows, in the visible column order., to_csv(), tracker_rows(), _application(), _client(), Connection (+24 more)

### Community 16 - "test_skim.py"
Cohesion: 0.10
Nodes (48): _create_application(), ignore_offer(), promote_offer(), Connection, datetime, Row, Offers that passed the hard filter and scored below the queue threshold.      An, The offer row, if it is genuinely one this page may act on. (+40 more)

### Community 17 - "contacts.py"
Cohesion: 0.07
Nodes (48): add_contact_cmd(), contacts_cmd(), draft_cold_cmd(), Resolve a company by numeric id or name; create by name if absent., Manually add a hiring contact for a company (default discovery path)., List stored contacts for a company, or the sourced outreach targets.      A targ, Draft a LinkedIn note + cold email and queue them for review (no send)., _resolve_company() (+40 more)

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
Cohesion: 0.09
Nodes (32): ConnectionFactory, Event, _production_connection(), Any, Connection, Single-flight ingest + score pass driven from the dashboard., Block until the running refresh finishes. Tests use this, not sleeps., Claim the single flight and hand the work to a background thread. (+24 more)

### Community 23 - "france_travail.py"
Cohesion: 0.15
Nodes (20): _first_nonempty(), _map_contact_email(), _map_contract(), _map_duration_months(), map_offer(), Any, Parse '... - 12 Mois' style durations from typeContratLibelle., Extract the offer contact email from FT's `contact.courriel`, defensively. (+12 more)

### Community 24 - "test_provenance_tiers.py"
Cohesion: 0.08
Nodes (33): SkillFact, _in_bank(), Three kinds of token, three different burdens of proof., Not even the widest scope can support it., The reader has to be able to search for it, or add it to the config., Task 26's handling survives as the digit-shaped corner of tier 2., Presence in the bank is necessary for tier 2, never sufficient., No fact anywhere carries these figures, so no scope can accept them. (+25 more)

### Community 25 - "launch_wttj_application"
Cohesion: 0.12
Nodes (19): approve_application(), Any, Connection, Path, Record human approval, transition, and generate through one shared path.      ``, Connection, Path, test_a_rejected_number_is_counted_separately_from_an_invented_id() (+11 more)

### Community 26 - "Dashboard"
Cohesion: 0.05
Nodes (40): Actualiser les offres (refresh from the page), Always up, without a terminal, Architecture (summary), ATS application assist (prefill only), Background scheduling, CI, Cold outreach sending (disabled by default), Commands (+32 more)

### Community 27 - "_FakePage"
Cohesion: 0.11
Nodes (19): ApplyAdapter, GreenhouseAdapter, LeverAdapter, Common adapter interface for a best-effort ATS prefill., SmartRecruitersAdapter, _FakeLauncher, _FakeLocator, _FakePage (+11 more)

### Community 28 - "cli.py"
Cohesion: 0.14
Nodes (25): Decision, RouteId, adapter_for_url(), Return the owning ATS adapter, if the saved offer URL is recognized., _applicant_reason(), _ats_prefill(), _email(), has_form_mapping() (+17 more)

### Community 29 - "test_desktop_shell.py"
Cohesion: 0.07
Nodes (40): CaptureFixture, dashboard_already_running(), Whether something is already listening on the dashboard's port.      A connect p, The menu bar text. Short: it competes with every other item up there., title(), _bound_port(), _fake_macos(), _module_level_imports() (+32 more)

### Community 30 - "generate_application"
Cohesion: 0.08
Nodes (24): date, _check_orphans(), _contains_generated_orphan(), DocumentToolchain, _french_date(), generate_application(), _load_offer(), _persist_variant() (+16 more)

### Community 31 - "test_contacts.py"
Cohesion: 0.10
Nodes (27): ModuleType, JobPilot: personal job application pipeline for the French IT/cybersecurity mark, _application(), _ConnectionProxy, Connection, Exception, Path, CLI coverage for offer document generation and cold-application approval. (+19 more)

### Community 32 - "test_email_alerts.py"
Cohesion: 0.09
Nodes (43): Message, GmailIMAP, html_of(), LinkedInAlertSource, Minimal read-only Gmail IMAP client., Fetch recent mail sent from `domains` (or any of their subdomains).          The, Return the best HTML (or plain-text) body of an email message., Return the lowercased domain of the address in a `From` header.      Parses the (+35 more)

### Community 33 - "test_labonnealternance.py"
Cohesion: 0.08
Nodes (54): get_or_create_company(), CompanyRecord, Normalized DTOs that every source emits, decoupled from source-specific JSON., _fixture(), _no_real_sleeping(), _NoWait, Connection, LogCaptureFixture (+46 more)

### Community 34 - "_Toolchain"
Cohesion: 0.07
Nodes (30): Path, Task 43 item 2: the browser extension, and the line it must not cross.  The exte, Two files naming the same three sites. A content script runs in the     page's o, Most of the time JobPilot is not running. The extension has to be     invisible, A rejected promise with no catch surfaces as an unhandled rejection,     which i, One obvious place, with the warning next to it., The requirement that matters most in a year: when LinkedIn changes its     gener, The biggest element on a page is a wrapper holding the whole page. (+22 more)

### Community 35 - "email_alerts.py"
Cohesion: 0.08
Nodes (28): Every id the advisor may cite, flattened out of the context it was given.      D, valid_fact_ids(), facts(), _nested_ids(), Task 37 item 1: tell the advisor the set of ids is closed.  `skill.rules.sigma`, Task 37 must not have quietly added Sigma to make the failure go away., Defensive: a template with no projects must not raise here., The exact mechanism that produced skill.rules.sigma. (+20 more)

### Community 36 - "test_alert_card_fields.py"
Cohesion: 0.09
Nodes (32): as_dicts(), clear_warnings(), _decode(), Any, Connection, What a generation had to degrade, recorded where the reviewer will see it.  Task, Gate names per application, for the library and tracker markers.      One query, Template-facing shape. (+24 more)

### Community 37 - "Settings"
Cohesion: 0.08
Nodes (43): FactBank, _advise_and_tailor(), _advisor_fact_context(), _fit_cv_title(), _interactive_structured_payload(), _offer_start(), _offered_fact_ids(), Raised when a citation matches no fact id, even after normalisation.      ``sect (+35 more)

### Community 38 - "Job Application Pipeline"
Cohesion: 0.06
Nodes (31): Alternance vs Stage, Edge Cases & Principles, Encoding note, Execution Flow, Flag once, then execute:, Generate with the bundled script:, GitHub Exception, Hard rejections (no output): (+23 more)

### Community 39 - "matcher.py"
Cohesion: 0.15
Nodes (28): bonus_score(), cosine(), hard_filter(), keyword_score(), norm(), pick_variant(), Profile, Connection (+20 more)

### Community 40 - "test_cv_completeness.py"
Cohesion: 0.12
Nodes (25): _category_skills(), _CompleteAdvisor, Any, Connection, Path, _Toolchain, _queued_application(), Structural completeness floor for AI-generated CVs (Task 22).  Selection freedom (+17 more)

### Community 41 - "OfferRecord"
Cohesion: 0.11
Nodes (21): Validate the one JSON contract shared by every advisor provider., _experience_content(), _gemini_shaped_payload(), _offer(), MonkeyPatch, AI-authored CV/letter content must be traceable to the fact bank., The observed real case: Gemini fills both structures, we keep the sourced one., A real Gemini answer fills the sourced structure AND the legacy fields. (+13 more)

### Community 42 - "test_dashboard_facts_scheduler.py"
Cohesion: 0.14
Nodes (27): age_in_days(), annotate(), describe(), drop_stale(), Freshness, _label(), max_offer_age_days(), _parse() (+19 more)

### Community 43 - ".from_mapping"
Cohesion: 0.13
Nodes (34): applications_by_status(), Offer applications in one status, newest first, with their age.      Returns the, _client(), _days_ago(), _offer_application(), Connection, MonkeyPatch, TestClient (+26 more)

### Community 44 - "test_cold_outreach.py"
Cohesion: 0.14
Nodes (9): BrowserLauncher, _ConfirmationBaseline, _Locator, _Page, Protocol, A launch seam: production opens Playwright, tests supply a stub page., Launch Playwright visibly and retain it until the human closes it., _scoped_selector() (+1 more)

### Community 45 - "_FakePage"
Cohesion: 0.19
Nodes (25): launch_wttj_application(), _open_for_human(), Auditable outcome of one approved WTTJ dashboard action., Fill a WTTJ inline form and submit only behind the explicit live gate., WTTJApplyResult, _events(), _FakeLauncher, _FakePage (+17 more)

### Community 46 - "MissingCredentialError"
Cohesion: 0.10
Nodes (46): ingest_source(), Run one source end to end. Commits once at the end for atomicity.      Two phase, _consecutive_failures(), _last_runs(), Any, Connection, Row, Leading failures only: one success resets the streak. (+38 more)

### Community 47 - "ats.py"
Cohesion: 0.15
Nodes (23): download_filename(), Download names an employer folder can still be read a week later.  ``output/appl, Reduce free text to ``[A-Za-z0-9-_]``, or to "" if nothing survives.      Accent, Build ``<Company>_<Type>_<Nom>.<ext>`` for one artefact.      Falls back to the, slugify(), _client(), Connection, Path (+15 more)

### Community 48 - "AnthropicTailoringAdvisor"
Cohesion: 0.21
Nodes (27): Send one approved cold draft after rechecking every legal rail., send_cold_email(), _cold_draft(), _configure_dashboard(), _dashboard_client(), _event_rows(), Connection, EmailMessage (+19 more)

### Community 49 - "OpenAITailoringAdvisor"
Cohesion: 0.16
Nodes (20): _all_template_paths(), _bullet_budget(), _claim_length(), _normalized(), _project_desc_budget(), _project_desc_rows(), An experience claim has to fit the CV's one line.  The renderer inserts a select, The widest project description any template already renders. (+12 more)

### Community 50 - "resolve_fact_id"
Cohesion: 0.12
Nodes (20): ApplicantProfile, Whether a stored selector still finds a control on the current page., The non-secret contact values entered into an ATS form., selector_matches_html(), build_prefill(), discard_mapping(), FormLearningError, FormMapping (+12 more)

### Community 51 - "test_tech_additions.py"
Cohesion: 0.15
Nodes (26): bank(), _offer(), LogCaptureFixture, Zone 3 may add a keyword, but only one he has and the offer asked for., Reorder-only remains the default and the common case., Genuinely his, but padding: the offer did not ask for it., Presence in the bank is necessary, never sufficient., Derived from the file, not a magic number. (+18 more)

### Community 52 - "load_fact_bank"
Cohesion: 0.10
Nodes (33): facts_cmd(), Print the provenance fact bank grouped for human review., _boolean(), CertificationFact, _claim_list(), EducationFact, _entry_claim(), format_fact_bank() (+25 more)

### Community 53 - "CompanyRecord"
Cohesion: 0.12
Nodes (38): clean_description(), Collapse the whitespace a copied page carries, and keep the rest., _client(), _fake_score(), _offer(), Connection, TestClient, Task 43 item 1: an offer description captured from an open page.  LinkedIn and I (+30 more)

### Community 54 - "labonnealternance.py"
Cohesion: 0.12
Nodes (17): _InteractiveShapedAdvisor, Human loop: always rejected, and never re-prompted automatically., _InventsThenRecovers, Connection, LogCaptureFixture, Path, Task 37 item 2: give the unknown-id retry something to work with.  An unknown fa, Cites an id that exists nowhere, for a chosen number of attempts. (+9 more)

### Community 55 - "ingest_source"
Cohesion: 0.14
Nodes (20): FormField, infer_profile_field(), One control's shape. Deliberately has nowhere to put a typed value., Everything naming this field, with separators folded to spaces.          Real fo, Name the reason this field may never be mapped, or None if it may.      Refused:, Which profile field this control wants, or None to leave it to the human., Every refusal category present in a form, for reporting to the human., refusal_category() (+12 more)

### Community 56 - "pick_variant"
Cohesion: 0.12
Nodes (9): _ControlParser, _Form, _FormParser, _forms_from_html(), HTMLParser, Strip a generated letter's markup down to what a human would paste., Tiny standard-library parser sufficient to test our simple CSS selectors., Collect controls by form so automation never targets the wrong form. (+1 more)

### Community 57 - "test_fact_id_resolution.py"
Cohesion: 0.21
Nodes (21): invention_report(), How often the advisor cites an id that does not exist, and whether it recovers., _Invents, Connection, MonkeyPatch, Path, Task 37 item 4: count invention, so the other three items are not guesswork.  Pr, Counting is about what the model invented, not about what was salvaged.      Dro (+13 more)

### Community 58 - "test_letter_locked_fields.py"
Cohesion: 0.18
Nodes (19): bank(), _letter(), _offer(), A letter is prose about a career; a CV is slots the renderer fills., Naming a real-sounding employer he never had is a fabrication, not prose., The renderer injects the address block; the body repeating it is a bug., Otherwise the test above would prove nothing about scope., The bank's own text names nothing it should not; selection is the check. (+11 more)

### Community 59 - "launch_application_assist"
Cohesion: 0.14
Nodes (19): _csv(), init_profile_cmd(), _langs(), Interactively fill the profile singleton and seed cv_variants., load_variants(), ProfileInput, Connection, Path (+11 more)

### Community 60 - "test_letter_quality.py"
Cohesion: 0.16
Nodes (21): _default_letter(), french_de_elision(), _omit_offending_paragraph(), _paragraph_offends(), Return « de <noun> » or « d'<noun> », applying French elision.      Elides befor, Whether this one paragraph is what _validate_letter_body refused.      Only the, Drop the one paragraph the letter gate refused, keeping the rest.      The retry, _render_sourced_letter() (+13 more)

### Community 61 - "test_mailer.py"
Cohesion: 0.04
Nodes (82): Logger, SentenceTransformer, apply_cmd(), apply_matching_profile_cmd(), backfill_descriptions_cmd(), init_db_cmd(), invention_report_cmd(), mark_sent_cmd() (+74 more)

### Community 62 - "models.py"
Cohesion: 0.29
Nodes (16): _client(), fixture_bank(), Connection, MonkeyPatch, Path, TestClient, Read-only fact bank page and honest scheduler reporting on the queue page., test_daemon_state_follows_the_recorded_heartbeat_age() (+8 more)

### Community 63 - "reparse_alerts"
Cohesion: 0.24
Nodes (15): _generation_failed_detail(), Any, Connection, LogCaptureFixture, Path, _queued_application(), One automatic advisor retry, fed only the validator's own error text., Re-calling on a 429 or a bad key is not feedback, it is a retry storm. (+7 more)

### Community 64 - "test_designation_numbers.py"
Cohesion: 0.04
Nodes (64): FastAPI, LookupError, Request, ApplicationGenerationError, ApplicationNotFoundError, ApplicationNotQueuedError, ApplyOutcome, archive_artifacts() (+56 more)

### Community 65 - "test_fact_id_consistency.py"
Cohesion: 0.20
Nodes (15): bank(), _bank_payload(), Path, Task 35 item 2: a fact bank whose claim ids do not extend their entry is invalid, The real bank must satisfy the rule the loader now enforces., This is the exact shape the Baïfall entry had., Projects have the same shape as experience, so they get the same rule., `experience.baifallX` starts with the entry id as a STRING but is a     differen (+7 more)

### Community 66 - "review.py"
Cohesion: 0.18
Nodes (18): _AlertSource, _ingest_then_import(), Connection, Row, Task 43 item 5: an imported description is never overwritten.  The user opens th, `force` exists to re-compose rows the normal pass skips. That widening     must, The guard must be `imported_at`, not an accident that stopped the     backfill w, A source that keeps offering the thin card, exactly as an alert does. (+10 more)

### Community 67 - "ingest_source"
Cohesion: 0.14
Nodes (22): apply_schema(), init_db(), Connection, Path, Ensure the sources rows exist. Idempotent via INSERT OR IGNORE on unique name., Full initialization: schema + migrations + source seeding., Apply schema.sql. Idempotent: uses CREATE TABLE ... only, so we guard reruns., Apply numbered .sql migrations not yet recorded. Returns count applied.      sch (+14 more)

### Community 68 - "_AnchorParser"
Cohesion: 0.08
Nodes (30): source_id(), _backfill_company_source(), _drain(), IngestResult, _insert_offer(), Connection, Ingestion orchestrator: pull normalized records from a Source into the DB.  Idem, INSERT OR IGNORE one offer. Returns True if a new row was created. (+22 more)

### Community 69 - "test_preview.py"
Cohesion: 0.23
Nodes (19): _fake_clone(), _git(), CompletedProcess, Path, Task 41: one command after a merge, and it refuses rather than half-updates.  sc, The loud refusal. A fast-forward carries uncommitted work with it., The point of the conditions: the two slow steps cost nothing here., Kickstarting the agents is unconditional: new code is only running once     the (+11 more)

### Community 70 - "vocabulary.py"
Cohesion: 0.17
Nodes (17): live_db(), _Observed, _offer(), Connection, Exception, Path, Task 41 follow-up: the write lock is not held across the network.  Task 41 put W, Draining buys the lock back without giving up atomicity — which is what     comm (+9 more)

### Community 71 - "UnknownFactIdError"
Cohesion: 0.12
Nodes (23): parse_linkedin(), Extract jobs from a LinkedIn job-alert email., _card_html(), LogCaptureFixture, Whatever position the chrome occupies, it must not be stored., None is strictly better: the hard filter reads it as "do not reject"., Observed verbatim: "Levallois-Perret (Sur site) Candidature simplifiée"., One LinkedIn job card: the anchor plus its sibling context chunks. (+15 more)

### Community 72 - "Baifall Dream Stage - Reference Document (v3)"
Cohesion: 0.17
Nodes (11): Baifall Dream Stage - Reference Document (v3), Bloc HTML de reference (3 bullets), Bullet 1 (commun, accompli) - 167 car., rendu sur 2 lignes, Bullet 2 (commun, nominal, perimetre complet) - 127 car., 1 ligne, Bullet 3 : declinaisons par variante, Context, Principe v3 : perimetre nominal complet, Regle pour la date (+3 more)

### Community 73 - "test_facts.py"
Cohesion: 0.14
Nodes (27): fields_from_html(), Read a page's controls as shapes. Values are stripped before we see them., Record mappings for one manually submitted form. Values are never stored.      C, Whether pressing submit is allowed on this domain. Default: no.      Prefill is, Flip the per-domain submit gate. Deliberately has no global counterpart., record_form_fields(), set_submit_enabled(), submit_enabled() (+19 more)

### Community 74 - "test_progress.py"
Cohesion: 0.06
Nodes (35): BackfillResult, enrich_offer(), is_thin(), Synthesise matchable text for offers that arrive with no description.  Job-alert, Replace a thin description in place; richer descriptions are left alone.      Ca, True when a description is too short to be worth embedding on its own., OfferRecord, One normalized offer, ready to insert into the offers table. (+27 more)

### Community 75 - "scheduler_status"
Cohesion: 0.17
Nodes (21): _alert_source_clause(), Connection, Restrict to one alert source, or to all of them when none is named., Re-derive company / city / workplace / easy-apply for stored alert offers., reparse_alerts(), ReparseResult, Connection, Structural parsing of job-alert cards (Task 20).  Every fixture here is shaped a (+13 more)

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
Cohesion: 0.20
Nodes (16): apply_matching_profile(), CvProfileError, MatchingProfile, MatchingProfileError, ValueError, Profile singleton + cv_variants seeding.  Persistence logic only (no prompting/p, Write the vocabulary onto the profile singleton. Returns {field: (before, after), Raised when the committed CV profile is missing or malformed. (+8 more)

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
Nodes (13): current_status(), ValueError, Recoverable, not fatal: a title that overflows is visible in two seconds     and, test_a_long_title_warns_and_still_generates(), End to end, on the exact string that reached application 37's PDF.      The advi, test_a_stage_generation_overwrites_a_placeholder_phrase_from_the_model(), _Advisor, _application() (+5 more)

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
Cohesion: 0.10
Nodes (33): HTTPStatusError, _city(), _company_name(), _contract_type(), _domain(), _first(), LaBonneAlternanceAuthError, LaBonneAlternanceError (+25 more)

### Community 110 - "test_designation_numbers.py"
Cohesion: 0.17
Nodes (16): bank(), _in_bank(), LogCaptureFixture, A standard's digits name a thing; a metric's digits measure one., The anti-fabrication guarantee is not weakened by designation handling., Only the designation's own span is exempt from the number rule., Judge as the letter is judged: no entry, so the whole bank answers., Looking like a standard is not evidence of holding one. (+8 more)

### Community 111 - "_AnchorParser"
Cohesion: 0.05
Nodes (77): _advisor_prompt(), allowed_numbers(), _bank_parts(), _correction_block(), _generated_bullets(), _guessed_section(), letter_scope(), nearest_entry_claim_ids() (+69 more)

### Community 112 - "Connection"
Cohesion: 0.14
Nodes (13): attempt(), describe(), fromSelectors(), hostKey(), largestTextBlock(), send(), textOf(), toast() (+5 more)

### Community 113 - "apply_matching_profile_cmd"
Cohesion: 0.15
Nodes (12): bank(), Task 35 item 3: a rejection that says what would have been valid.  Task 22c allo, The regression test for the failure that burned two generations., `experience.` is common to every experience entry. Matching on it would     list, A large entry must not blow the retry prompt., Existing callers and tests match on this prefix; item 3 appends, it does     not, test_a_bad_baifall_id_is_told_a_real_baifall_id(), test_an_unresolvable_id_says_so_plainly_instead_of_dumping_the_bank() (+4 more)

### Community 114 - "test_variant_selection.py"
Cohesion: 0.10
Nodes (29): _fact_id_key(), Fold separator and case differences, and nothing else, for comparison., Map a cited id onto a real fact id, accepting only unambiguous matches.      Mat, resolve_fact_id(), _advise(), bank(), _offer(), Any (+21 more)

### Community 115 - "labonnealternance.py"
Cohesion: 0.19
Nodes (14): event_history(), import_supersedes_documents(), outreach_drafts(), Any, Connection, queued_applications(), Navigation tabs with per-status counts for offer applications., Return application counts using the same grouping as ``jobpilot stats``. (+6 more)

### Community 116 - "test_profile_domain_anchor.py"
Cohesion: 0.31
Nodes (10): _offer(), Systemic recovery at the generated-prose and document-layout boundaries., Naming the employer is what a motivation letter does.      The rule was never lo, _selection_and_template(), test_a_valid_custom_profile_phrase_is_preserved_exactly(), test_an_invalid_profile_phrase_uses_the_variant_fallback(), test_an_unsupported_candidate_claim_remains_a_hard_failure(), test_model_prose_dashes_are_canonicalized_before_validation() (+2 more)

### Community 117 - "test_mailer.py"
Cohesion: 0.32
Nodes (15): _events(), Connection, EmailMessage, Exception, Path, Application email sending: rails, transitions, and events (mocked SMTP)., _ready_app(), _Sender (+7 more)

### Community 118 - "_application"
Cohesion: 0.27
Nodes (18): _application(), _client(), Connection, TestClient, Task 43 item 3: pasting the description is a first-class path.  Not a fallback f, The card is 113 characters and the CV was tailored against it. Saying so     is, A rejected paste must not look like a lost page, and must not have     replaced, One endpoint, two representations. The JSON caller sends no     application_id a (+10 more)

### Community 119 - "FormField"
Cohesion: 0.20
Nodes (21): _offer(), _openai_response(), _plan_payload(), Any, Connection, MonkeyPatch, Path, _queued_application() (+13 more)

### Community 120 - "_reject_placeholders"
Cohesion: 0.16
Nodes (17): No rendered CV may carry bracketed text. Task 44 item 1.      '[offer duration]', _reject_placeholders(), Task 44 item 1: no rendered CV may carry a bracketed placeholder.  « Stage de [o, If a hand-written template carried brackets, the guard would abort every     gen, The regression, quoted from application 37's rendered CV., Tier is the whole decision here: recoverable would mean retrying, and     the mo, Half the templates are entity-encoded, so the scan reads decoded text.     A pla, No template carries one today. This is about a future stylesheet edit     not fa (+9 more)

### Community 121 - "Any"
Cohesion: 0.18
Nodes (16): bank(), Connection, Path, _raised(), Task 39 item 3: one funnel, three outcomes.  152 raise sites all meant "abort",, validate_provenance delegates; the capability tier is what actually fired., The one gate stopping a CV experience entry at the offer's employer., Nothing is weakened: a fabrication ends the run exactly as before. (+8 more)

### Community 122 - "test_form_learning.py"
Cohesion: 0.21
Nodes (11): _css_attribute_value(), _identity(), _page_offer_identity(), PrefillPlan, Path, The actions selected from a page's current HTML fixture/markup., A safe, auditable pre-submit abort with a stable machine reason., WTTJ inline form adapter with explicit pre-submit assertions. (+3 more)

### Community 124 - "_reject_unsupported_tokens"
Cohesion: 0.18
Nodes (13): _BaseAdapter, _Control, _controls_from_html(), FillAction, _first_matching_selector(), One safe local-file upload; never a form submit action., Match the deliberately simple tag[attr=value] selectors used below., Shared plan building and non-submitting form interaction. (+5 more)

### Community 125 - "gate"
Cohesion: 0.21
Nodes (13): _plan(), Task 40 amendment: bullets had a floor and no ceiling.  _validate_experience_com, The ceiling does not soften the other direction., Floor beats ceiling; a template row count under it cannot make a bad CV., End to end: the renderer inserts what survived, not what was asked for., A plan whose most recent employer selects `facts_for_first` of its facts., The reproduction: nine facts into three rows., test_a_selection_within_the_ceiling_is_untouched() (+5 more)

### Community 126 - "Connection"
Cohesion: 0.24
Nodes (12): mapping_is_complete(), mappings_for(), put_mapping(), Connection, Write one mapping. Rejects a profile_field outside the closed enum., Whether ``domain`` has enough of a mapping to be worth calling a route., Falling back to manual_open is correct behaviour, not a bug., An arbitrary string is not acceptable — this decides what gets typed in. (+4 more)

### Community 128 - "Path"
Cohesion: 0.09
Nodes (30): _create_offer(), find_offer_by_url(), import_offer_description(), ImportResult, _is_tracking(), normalize_offer_url(), OfferImportError, Any (+22 more)

### Community 129 - "test_bullet_ceiling.py"
Cohesion: 0.16
Nodes (21): ATSSource, infer_contract(), load_targets(), map_greenhouse(), map_lever(), map_smartrecruiters(), _ms_to_iso(), Any (+13 more)

### Community 130 - "score"
Cohesion: 0.11
Nodes (28): load_matching_profile(), Load the committed matching vocabulary, failing loudly rather than defaulting., Path, Task 35 item 1: the city parse fix (1a) and the committed matching profile (1b)., role_hit is an unanchored substring test worth a flat +0.15. As bare     tokens, Item 1c withdrawn. These are load-bearing: France Travail writes     'Courbevoie, The old list was already French but multi-word, and substring matching     needs, len(hard_skills) is keyword_score's denominator, so a duplicate silently     low (+20 more)

### Community 131 - "apply_matching_profile"
Cohesion: 0.25
Nodes (15): _as_list(), build_profile_text(), _col(), Row, Build a natural-language candidate summary for embedding.      Phrased like the, _fake_embed(), _insert_offer(), Connection (+7 more)

### Community 132 - "observable_controls"
Cohesion: 0.09
Nodes (38): _application_for_assist(), _application_for_wttj(), ApplyAssistError, AssistResult, _fallback(), launch_application_assist(), letter_plain_text(), open_manually() (+30 more)

### Community 133 - "_FakeLocator"
Cohesion: 0.24
Nodes (10): counts(), Connection, datetime, The tracker: every application, one table, read-only.  Deliberately not a Google, Statuses that actually occur, so the filter offers no dead options., The four numbers worth seeing before the table itself., Monday 00:00 UTC of the current week, as ISO text.      Compared as text against, statuses() (+2 more)

### Community 134 - "test_dedup.py"
Cohesion: 0.13
Nodes (23): Apply the mechanical contract and encoding rules to a chosen slug.      These ar, The stage contract line, built from what is known.      Task 44 item 1: this is, The contract line for this plan, or None when the template owns it.      Replace, _renderer_contract_phrase(), _stage_contract_phrase(), variant_for_slug(), test_layout_fallback_restores_each_trusted_template_phrase(), _offer() (+15 more)

### Community 135 - "update.sh"
Cohesion: 0.60
Nodes (3): changed_since_pull(), die(), update.sh script

### Community 136 - "scheduler_status"
Cohesion: 0.14
Nodes (24): _at(), _offer(), Connection, Task 42: recency is first-class, and the age it reports is honest.  France Trava, Some postings state an availability date rather than a posting date., The filter hides what is provably old, not what is merely unlabelled., scraped_at is always after the real posting date, so this age understates     it, A lower bound that already exceeds the limit is proof of age, even though     st (+16 more)

### Community 138 - "mappings_for"
Cohesion: 0.15
Nodes (11): _plan(), Path, Task 41: the header location is found by its own marker, not by its neighbours., A template re-exported with a plain pin and a different separator.      Under th, The header is a fixed-width line; the span must not consume any of it., The header location is renderer-owned: it comes from the offer's city., The premise of the fix, asserted rather than assumed.      If this ever fails th, test_every_template_still_extracts_its_location() (+3 more)

### Community 139 - "vocabulary.py"
Cohesion: 0.33
Nodes (6): The tier this failure carries HERE.      An unclassified error is fatal. That de, tier_for(), The safety property of the whole task: forgetting to classify a gate     keeps t, The same capability refusal is fatal in the letter and recoverable in the     pr, test_an_unclassified_error_is_fatal(), test_tier_is_a_property_of_gate_and_position()

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

### Community 144 - "Any"
Cohesion: 0.50
Nodes (5): _offer(), A posting that asks for CrowdStrike does not mean the candidate has it., _tailor(), test_a_category_word_survives_the_full_generation_path(), test_a_tool_named_by_the_offer_is_still_refused()

### Community 145 - "CompletedProcess"
Cohesion: 0.50
Nodes (4): observable_controls(), Every fillable control's *shape*, for form learning. Never its contents.      ``, One enforcement point: values are stripped before this module sees them., test_observable_controls_never_expose_what_the_human_typed()

### Community 146 - "test_ingest_idempotent.py"
Cohesion: 0.38
Nodes (8): FakeSource, Connection, Re-running ingest must never duplicate rows (constitution idempotency rule)., _sample(), test_company_deduped_across_offers_and_runs(), test_first_run_inserts_all(), test_last_run_at_updated(), test_second_run_inserts_nothing()

### Community 147 - "Connection"
Cohesion: 0.67
Nodes (3): _F, gate(), Label what this function refuses, and what refusing costs.      Attached to the

### Community 149 - "test_registry.py"
Cohesion: 0.05
Nodes (51): daemon_cmd(), ingest_cmd(), Run ingest + score on a loop (Ctrl-C to stop)., Fetch offers from a source (or all sources) into the database., MissingCredentialError, RuntimeError, Remove configured secrets from exception text before display/logging., Raised when a required secret is absent. We ask; we never silently mock. (+43 more)

### Community 155 - "_approve"
Cohesion: 0.21
Nodes (15): It did not block, so the only thing standing between it and invisibility     is, « rien à signaler » is a claim worth being able to make., test_a_clean_generation_records_an_empty_set_not_null(), test_an_advisory_orphan_is_recorded_on_the_application(), _approve(), Connection, LogCaptureFixture, Path (+7 more)

### Community 157 - "test_renderer_owned_fields.py"
Cohesion: 0.11
Nodes (20): build_cv_title(), normalise_role_title(), Remove posting metadata while preserving the actual role wording., Build the deterministic CV title used after all advisor providers., load_cv_profile(), Load the committed CV profile, failing loudly rather than defaulting., _canonicalize_prose(), Normalize model punctuation that the document contract forbids.      This is a l (+12 more)

### Community 168 - "counts"
Cohesion: 0.67
Nodes (3): counts(), Connection, Ready and queued offer applications, the two numbers worth a glance.

## Knowledge Gaps
- **171 isolated node(s):** `manifest_version`, `name`, `version`, `description`, `https://*.linkedin.com/*` (+166 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `create_app()` connect `test_designation_numbers.py` to `Path`, `Request`, `test_downloads.py`, `_candidate_name`, `observable_controls`, `_FakeLocator`, `run_dashboard`, `test_routing.py`, `mailer.py`, `apply_assist.py`, `test_skim.py`, `RefreshRunner`, `SourcedBullet`, `launch_wttj_application`, `test_alert_card_fields.py`, `test_dashboard_facts_scheduler.py`, `.from_mapping`, `_FakePage`, `MissingCredentialError`, `ats.py`, `AnthropicTailoringAdvisor`, `load_fact_bank`, `CompanyRecord`, `test_mailer.py`, `models.py`, `CompanyRecord`, `labonnealternance.py`, `_application`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `test_mailer.py` to `observable_controls`, `dashboard.py`, `run_dashboard`, `test_routing.py`, `mailer.py`, `get_settings`, `test_registry.py`, `SourcedBullet`, `wttj.py`, `cli.py`, `generate_application`, `test_email_alerts.py`, `test_labonnealternance.py`, `Settings`, `test_dashboard_facts_scheduler.py`, `_FakePage`, `AnthropicTailoringAdvisor`, `test_fact_id_resolution.py`, `launch_application_assist`, `test_designation_numbers.py`, `ingest_source`, `test_mailer.py`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `Settings` connect `test_registry.py` to `test_bullet_ceiling.py`, `observable_controls`, `test_routing.py`, `mailer.py`, `_Toolchain`, `wttj.py`, `france_travail.py`, `_FakePage`, `cli.py`, `test_email_alerts.py`, `test_labonnealternance.py`, `test_cold_outreach.py`, `_FakePage`, `MissingCredentialError`, `AnthropicTailoringAdvisor`, `resolve_fact_id`, `pick_variant`, `test_mailer.py`, `test_progress.py`, `Path`, `test_form_learning.py`, `_reject_unsupported_tokens`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Are the 62 inferred relationships involving `Settings` (e.g. with `ApplicantProfile` and `ApplyAdapter`) actually correct?**
  _`Settings` has 62 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `current_status()` (e.g. with `test_a_long_title_warns_and_still_generates()` and `test_a_fatal_gate_still_aborts()`) actually correct?**
  _`current_status()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `TailoringError` (e.g. with `ExperienceFact` and `FactBank`) actually correct?**
  _`TailoringError` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `_payload()` (e.g. with `_plan()` and `_plan()`) actually correct?**
  _`_payload()` has 13 INFERRED edges - model-reasoned connections that need verification._