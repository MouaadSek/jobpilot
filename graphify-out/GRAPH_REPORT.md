# Graph Report - jobpilot  (2026-08-04)

## Corpus Check
- 166 files · ~203,704 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3613 nodes · 9585 edges · 140 communities (121 shown, 19 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 574 edges (avg confidence: 0.53)
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
- _Advisor

## God Nodes (most connected - your core abstractions)
1. `Settings` - 117 edges
2. `current_status()` - 99 edges
3. `_payload()` - 92 edges
4. `TailoringError` - 90 edges
5. `load_fact_bank()` - 81 edges
6. `OfferRecord` - 77 edges
7. `FactBank` - 73 edges
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

## Communities (140 total, 19 thin omitted)

### Community 0 - "test_downloads.py"
Cohesion: 0.05
Nodes (41): BaseException, Operation, ProgressRegistry, Any, datetime, Update a running operation. A key that is not running is ignored., Close an operation. The first outcome recorded wins.          A handled failure, Everything running, plus anything that finished very recently. (+33 more)

### Community 1 - "Request"
Cohesion: 0.08
Nodes (55): Resolve one archived artefact, with the same discipline as the live one.      De, _safe_archive_path(), _archives_for(), Generation, is_archive_stamp(), library_entries(), LibraryEntry, _mtime_iso() (+47 more)

### Community 2 - "_candidate_name"
Cohesion: 0.07
Nodes (90): SimpleNamespace, _client(), _days_ago(), _events(), _no_advisor_client(), _offer_application(), Connection, MonkeyPatch (+82 more)

### Community 3 - "_client"
Cohesion: 0.12
Nodes (22): _application_for_assist(), _application_for_wttj(), ApplyAssistError, AssistResult, _fallback(), launch_application_assist(), launch_wttj_application(), _open_for_human() (+14 more)

### Community 4 - "create_app"
Cohesion: 0.11
Nodes (30): _advisor_fact_context(), AnthropicTailoringAdvisor, _interactive_structured_payload(), _offer_start(), _offered_fact_ids(), One of the 21 templates, including stage-adaptation metadata., Editable choices extracted from a selected template., The ids of that section that this generation's prompt actually offered.      Fee (+22 more)

### Community 5 - "dashboard.py"
Cohesion: 0.06
Nodes (92): Match, Pattern, FactBank, _add_tech_additions(), _add_tech_keywords(), _cap_experience_selection(), _contact_fields(), _contains() (+84 more)

### Community 6 - "run_dashboard"
Cohesion: 0.20
Nodes (16): drop_unknown_citation(), Remove one unusable citation, or refuse when removing it would weaken the CV., _plan(), Task 37 item 3: degradation. Shipped off, turned ON by Task 39.  If the advisor, The completeness floor is a hard failure, not a preference., The spec said "at least one remaining bullet" is enough. It is not: the     Task, Exactly three projects are required, each with its single fact., skill_order has no minimum, so losing one weakens nothing structural. (+8 more)

### Community 7 - "Path"
Cohesion: 0.10
Nodes (26): OfferRecord, One normalized offer, ready to insert into the offers table., Coerce enum-constrained fields to legal values (schema CHECK safety)., ATSSource, infer_contract(), load_targets(), map_greenhouse(), map_lever() (+18 more)

### Community 8 - "test_routing.py"
Cohesion: 0.09
Nodes (60): Cursor, _artifacts(), Path, Resolve the one route this application would go out by. Writes nothing., A route the offer qualified for, and the reason it cannot be used., The resolved plan for one application. Carries no state and stores none., Fingerprint of exactly the inputs that decided this route.          Stateless by, resolve_route() (+52 more)

### Community 9 - "mailer.py"
Cohesion: 0.09
Nodes (36): Show the email that would be sent for a ready application, then confirm (y/N)., send_cmd(), Remove configured secrets from exception text before display/logging., Settings, _build_message(), build_sender(), ColdEmailPreparation, ColdSendDisabled (+28 more)

### Community 10 - "validate_cv.py"
Cohesion: 0.06
Nodes (53): check_orphans(), find_regressions(), Path, Return orphan metrics that are new or materially worse than the template., format_date(), main(), build_letter_html(), detect_github() (+45 more)

### Community 11 - "get_settings"
Cohesion: 0.06
Nodes (76): ExperienceFact, FactClaim, One atomic statement that generated content may cite., GenerationWarning, One thing the reviewer is being asked to check by eye., CvProfile, Renderer-owned candidate facts injected into every generated CV., The location printed in the CV header when the offer yields none. (+68 more)

### Community 12 - "connect"
Cohesion: 0.15
Nodes (22): Apply the mechanical contract and encoding rules to a chosen slug.      These ar, The contract line an adapted alternance CV must carry., The stage contract line to fall back to, built from what is known.      Determin, Preserve a valid contract phrase; replace only a rejected one.      Same shape a, _resolve_stage_contract_phrase(), _stage_contract_fallback(), _validate_stage_contract_phrase(), variant_for_slug() (+14 more)

### Community 13 - "test_descriptions.py"
Cohesion: 0.08
Nodes (59): backfill_descriptions(), BackfillResult, clear_match_scores(), enrich_offer(), is_synthesized(), is_thin(), Connection, Synthesise matchable text for offers that arrive with no description.  Job-alert (+51 more)

### Community 14 - "test_generic_vocabulary.py"
Cohesion: 0.13
Nodes (21): Validate the one JSON contract shared by every advisor provider., _experience_content(), _gemini_shaped_payload(), _offer(), MonkeyPatch, AI-authored CV/letter content must be traceable to the fact bank., The observed real case: Gemini fills both structures, we keep the sourced one., A real Gemini answer fills the sourced structure AND the legacy fields. (+13 more)

### Community 15 - "apply_assist.py"
Cohesion: 0.13
Nodes (34): applications_by_status(), Offer applications in one status, newest first, with their age.      Returns the, _client(), _days_ago(), _offer_application(), Connection, MonkeyPatch, TestClient (+26 more)

### Community 16 - "test_skim.py"
Cohesion: 0.11
Nodes (48): available_sources(), _create_application(), ignore_offer(), promote_offer(), Connection, Row, Offers that passed the hard filter and scored below the queue threshold.      An, The offer row, if it is genuinely one this page may act on. (+40 more)

### Community 17 - "contacts.py"
Cohesion: 0.09
Nodes (41): contacts_cmd(), List stored contacts for a company, or the sourced outreach targets.      A targ, _candidate_name(), ContactCandidate, discover_and_store(), DiscoverySource, draft_cold_email(), draft_linkedin_note() (+33 more)

### Community 18 - "JobPilot — Codex Handoff (complete A-to-Z)"
Cohesion: 0.04
Nodes (45): 10. HARD REJECTIONS (offers the pipeline should auto-skip), 11. API REFERENCES, 12. DESIGN PRINCIPLES (non-negotiable), 13. ENV VARS (.env), 14. GITHUB PUSH (do this FIRST, before any Codex work), 15. CODEX TASK BREAKDOWN (suggested order), 16. BAIFALL DREAM STAGE REFERENCE, 17. SCRIPTS REFERENCE (+37 more)

### Community 19 - "RefreshRunner"
Cohesion: 0.07
Nodes (44): backfill_descriptions_cmd(), init_db_cmd(), Synthesise descriptions for stored offers whose text is too thin to score., Create the database from schema.sql, run migrations, seed sources., _env_bool(), get_settings(), _path(), apply_schema() (+36 more)

### Community 20 - "_payload"
Cohesion: 0.11
Nodes (43): _bullets(), _project(), The advisor selects; the renderer inserts the bank's wording unchanged., The pre-written variants from the skill asset, used as the asset intends., The contract has no field for prose, so a writing advisor fails loudly., Only the entry's own facts, so a skill id cannot become a bullet., Task 25's tolerance survives: ids are normalised before they are judged., The phrase is short, but it is still generated, so the tiers still read it. (+35 more)

### Community 21 - "wttj.py"
Cohesion: 0.10
Nodes (41): _city(), _contact_email(), _contract(), _first(), map_hit(), _org(), _prose(), Any (+33 more)

### Community 22 - "SourcedBullet"
Cohesion: 0.06
Nodes (49): ConnectionFactory, Event, ingest_cmd(), Fetch offers from a source (or all sources) into the database., Configuration and path resolution. Secrets come from .env only (never mocked)., _drain(), IngestResult, Pull everything the source has, before any write begins.      ``fetch_companies` (+41 more)

### Community 23 - "france_travail.py"
Cohesion: 0.07
Nodes (38): Logger, Put text on the system clipboard, or say plainly that it could not.  The manual_, get_logger(), Central logging setup. Library code logs here; it never uses print()., Idempotent: attaches a rotating file handler + console handler once., setup_logging(), What the dashboard is doing right now, readable while it does it.  ``RefreshRunn, _delay() (+30 more)

### Community 24 - "test_provenance_tiers.py"
Cohesion: 0.08
Nodes (37): bank(), _in_bank(), _offer(), Three kinds of token, three different burdens of proof., Not even the widest scope can support it., The reader has to be able to search for it, or add it to the config., Task 26's handling survives as the digit-shaped corner of tier 2., Presence in the bank is necessary for tier 2, never sufficient. (+29 more)

### Community 25 - "launch_wttj_application"
Cohesion: 0.22
Nodes (25): _cold_draft(), _configure_dashboard(), _dashboard_client(), _event_rows(), Connection, EmailMessage, Exception, MonkeyPatch (+17 more)

### Community 26 - "Dashboard"
Cohesion: 0.05
Nodes (39): Actualiser les offres (refresh from the page), Always up, without a terminal, Architecture (summary), ATS application assist (prefill only), Background scheduling, CI, Cold outreach sending (disabled by default), Commands (+31 more)

### Community 27 - "_FakePage"
Cohesion: 0.11
Nodes (19): _BaseAdapter, GreenhouseAdapter, LeverAdapter, Shared plan building and non-submitting form interaction., SmartRecruitersAdapter, _FakeLauncher, _FakeLocator, _FakePage (+11 more)

### Community 28 - "cli.py"
Cohesion: 0.11
Nodes (44): Gate names per application, for the library and tracker markers.      One query, warning_gates_by_application(), counts(), Any, Connection, datetime, The tracker: every application, one table, read-only.  Deliberately not a Google, Every offer application, optionally narrowed to one status.      ``include_stale (+36 more)

### Community 29 - "test_desktop_shell.py"
Cohesion: 0.06
Nodes (44): CaptureFixture, dashboard_cmd(), Launch the local review dashboard on 127.0.0.1., dashboard_already_running(), Whether something is already listening on the dashboard's port.      A connect p, Run the dashboard on an intentionally fixed loopback interface.      Returns a p, run_dashboard(), The menu bar text. Short: it competes with every other item up there. (+36 more)

### Community 30 - "generate_application"
Cohesion: 0.07
Nodes (33): date, _advise_and_tailor(), _check_orphans(), _contains_generated_orphan(), DocumentToolchain, _french_date(), generate_application(), _is_validator_rejection() (+25 more)

### Community 31 - "test_contacts.py"
Cohesion: 0.10
Nodes (27): ModuleType, JobPilot: personal job application pipeline for the French IT/cybersecurity mark, _application(), _ConnectionProxy, Connection, Exception, Path, CLI coverage for offer document generation and cold-application approval. (+19 more)

### Community 32 - "test_email_alerts.py"
Cohesion: 0.08
Nodes (48): Message, EmailAlertError, _EmailAlertSource, GmailIMAP, html_of(), IndeedAlertSource, LinkedInAlertSource, RuntimeError (+40 more)

### Community 33 - "test_labonnealternance.py"
Cohesion: 0.15
Nodes (29): _fixture(), _NoWait, LogCaptureFixture, La Bonne Alternance through the API Apprentissage: mapping, rails, ingestion.  E, The endpoint has no pagination, so this is the volume knob that exists., A full ingest reads both lists; it must not pay for the search twice., The live API really does repeat an offer inside one response., A company that has posted nothing must not appear in the review queue. (+21 more)

### Community 34 - "_Toolchain"
Cohesion: 0.10
Nodes (18): HTTPStatusError, MissingCredentialError, RuntimeError, Raised when a required secret is absent. We ask; we never silently mock., RateLimiter, Minimum-delay-per-domain limiter. Blocks until the next call is allowed., DaemonStatus, What can honestly be said about the daemon, and nothing more. (+10 more)

### Community 35 - "email_alerts.py"
Cohesion: 0.08
Nodes (30): Every id the advisor may cite, flattened out of the context it was given.      D, valid_fact_ids(), context(), _context_for(), facts(), _nested_ids(), Task 37 item 1: tell the advisor the set of ids is closed.  `skill.rules.sigma`, Task 37 must not have quietly added Sigma to make the failure go away. (+22 more)

### Community 36 - "test_alert_card_fields.py"
Cohesion: 0.12
Nodes (22): Every warning the current generation of this application carries., warnings_for(), application(), Connection, Task 39 item 2: a degraded document must not look like a clean one.  Warnings sh, It did not block, so the only thing standing between it and invisibility     is, « rien à signaler » is a claim worth being able to make., Amber, not red: the document is usable, it just needs a look. (+14 more)

### Community 37 - "Settings"
Cohesion: 0.12
Nodes (17): load_cv_profile(), Load the committed CV profile, failing loudly rather than defaulting., _canonicalize_prose(), _infer_region(), _justification(), Any, Normalize model punctuation that the document contract forbids.      This is a l, Renderer-owned CV header location; the advisor has no say in it.      Prefers th (+9 more)

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
Cohesion: 0.12
Nodes (10): CompletedProcess, Raised when a citation matches no fact id, even after normalisation.      ``sect, UnknownFactIdError, _BadSourceAdvisor, Cites a prefix-less unknown id first, then whatever the retry was told., Cites an unresolvable id in a letter paragraph, where no section is implied., _RecordingAdvisor, A rejection that buries the answer in a wall of ids is no more useful     than o (+2 more)

### Community 42 - "test_dashboard_facts_scheduler.py"
Cohesion: 0.07
Nodes (43): derive_fields(), _Derived, Re-derive alert card fields (company / city / workplace / easy-apply) in place., Re-derive one offer's card fields from the text that was stored for it.      Pur, _AlertAnchor, _AnchorParser, _anchors(), _Card (+35 more)

### Community 43 - ".from_mapping"
Cohesion: 0.17
Nodes (23): Decision, RouteId, _applicant_reason(), _ats_prefill(), _email(), has_form_mapping(), _learned_form(), _manual_open() (+15 more)

### Community 44 - "test_cold_outreach.py"
Cohesion: 0.32
Nodes (15): _events(), Connection, EmailMessage, Exception, Path, Application email sending: rails, transitions, and events (mocked SMTP)., _ready_app(), _Sender (+7 more)

### Community 45 - "_FakePage"
Cohesion: 0.24
Nodes (20): _events(), _FakeLauncher, _FakePage, Connection, Path, Row, WTTJ inline application stays human-approved and dry-run by default., _ready_wttj_application() (+12 more)

### Community 46 - "MissingCredentialError"
Cohesion: 0.08
Nodes (55): ingest_source(), Run one source end to end. Commits once at the end for atomicity.      Two phase, _consecutive_failures(), daemon_status(), heartbeat_path(), _last_runs(), Any, Connection (+47 more)

### Community 47 - "ats.py"
Cohesion: 0.15
Nodes (23): download_filename(), Download names an employer folder can still be read a week later.  ``output/appl, Reduce free text to ``[A-Za-z0-9-_]``, or to "" if nothing survives.      Accent, Build ``<Company>_<Type>_<Nom>.<ext>`` for one artefact.      Falls back to the, slugify(), _client(), Connection, Path (+15 more)

### Community 48 - "AnthropicTailoringAdvisor"
Cohesion: 0.10
Nodes (39): extract_template_context(), pick_variant(), Pick the best of 21 variants from missions, then apply contract rules.      Sinc, Read all editable choices without altering the template., The model had never been told there was one., test_the_prompt_states_the_ceiling(), The unwrapped second call that killed the Capgemini generation.      A degradati, test_the_profile_fallback_survives_its_own_fallback_failing() (+31 more)

### Community 49 - "OpenAITailoringAdvisor"
Cohesion: 0.16
Nodes (20): _all_template_paths(), _bullet_budget(), _claim_length(), _normalized(), _project_desc_budget(), _project_desc_rows(), An experience claim has to fit the CV's one line.  The renderer inserts a select, The widest project description any template already renders. (+12 more)

### Community 50 - "resolve_fact_id"
Cohesion: 0.13
Nodes (21): CvProfileError, load_variants(), MatchingProfileError, ProfileInput, Connection, Path, ValueError, Profile singleton + cv_variants seeding.  Persistence logic only (no prompting/p (+13 more)

### Community 51 - "test_tech_additions.py"
Cohesion: 0.15
Nodes (26): bank(), _offer(), LogCaptureFixture, Zone 3 may add a keyword, but only one he has and the offer asked for., Reorder-only remains the default and the common case., Genuinely his, but padding: the offer did not ask for it., Presence in the bank is necessary, never sufficient., Derived from the file, not a magic number. (+18 more)

### Community 52 - "load_fact_bank"
Cohesion: 0.12
Nodes (32): facts_cmd(), Print the provenance fact bank grouped for human review., _boolean(), CertificationFact, _claim_list(), EducationFact, _entry_claim(), FactBankError (+24 more)

### Community 53 - "CompanyRecord"
Cohesion: 0.20
Nodes (21): _offer(), _openai_response(), _plan_payload(), Any, Connection, MonkeyPatch, Path, _queued_application() (+13 more)

### Community 54 - "labonnealternance.py"
Cohesion: 0.11
Nodes (17): _InteractiveShapedAdvisor, Human loop: always rejected, and never re-prompted automatically., _InventsThenRecovers, Connection, LogCaptureFixture, Path, Task 37 item 2: give the unknown-id retry something to work with.  An unknown fa, Cites an id that exists nowhere, for a chosen number of attempts. (+9 more)

### Community 55 - "ingest_source"
Cohesion: 0.04
Nodes (76): FastAPI, LookupError, Request, ApplicationGenerationError, ApplicationNotFoundError, ApplicationNotQueuedError, ApplyOutcome, archive_artifacts() (+68 more)

### Community 56 - "pick_variant"
Cohesion: 0.16
Nodes (12): _ConfirmationBaseline, _css_attribute_value(), _identity(), _Locator, _Page, PrefillPlan, The actions selected from a page's current HTML fixture/markup., A safe, auditable pre-submit abort with a stable machine reason. (+4 more)

### Community 57 - "test_fact_id_resolution.py"
Cohesion: 0.21
Nodes (22): invention_report(), How often the advisor cites an id that does not exist, and whether it recovers., _Invents, Connection, MonkeyPatch, Path, Task 37 item 4: count invention, so the other three items are not guesswork.  Pr, Counting is about what the model invented, not about what was salvaged.      Dro (+14 more)

### Community 58 - "test_letter_locked_fields.py"
Cohesion: 0.18
Nodes (19): bank(), _letter(), _offer(), A letter is prose about a career; a CV is slots the renderer fills., Naming a real-sounding employer he never had is a fabrication, not prose., The renderer injects the address block; the body repeating it is a bug., Otherwise the test above would prove nothing about scope., The bank's own text names nothing it should not; selection is the check. (+11 more)

### Community 59 - "launch_application_assist"
Cohesion: 0.13
Nodes (18): ApplicantProfile, The non-secret contact values entered into an ATS form., build_prefill(), discard_mapping(), FormLearningError, FormMapping, PrefillOutcome, _profile_values() (+10 more)

### Community 60 - "test_letter_quality.py"
Cohesion: 0.16
Nodes (21): _default_letter(), french_de_elision(), _omit_offending_paragraph(), _paragraph_offends(), Return « de <noun> » or « d'<noun> », applying French elision.      Elides befor, Whether this one paragraph is what _validate_letter_body refused.      Only the, Drop the one paragraph the letter gate refused, keeping the rest.      The retry, _render_sourced_letter() (+13 more)

### Community 61 - "test_mailer.py"
Cohesion: 0.05
Nodes (43): add_contact_cmd(), apply_cmd(), _csv(), daemon_cmd(), draft_cold_cmd(), init_profile_cmd(), invention_report_cmd(), _langs() (+35 more)

### Community 62 - "models.py"
Cohesion: 0.29
Nodes (16): _client(), fixture_bank(), Connection, MonkeyPatch, Path, TestClient, Read-only fact bank page and honest scheduler reporting on the queue page., test_daemon_state_follows_the_recorded_heartbeat_age() (+8 more)

### Community 63 - "reparse_alerts"
Cohesion: 0.21
Nodes (15): current_status(), _generation_failed_detail(), Any, Connection, LogCaptureFixture, Path, One automatic advisor retry, fed only the validator's own error text., Re-calling on a 429 or a bad key is not feedback, it is a retry storm. (+7 more)

### Community 64 - "test_designation_numbers.py"
Cohesion: 0.19
Nodes (19): open_manually(), The manual_open route: open the offer, copy the letter, submit nothing.      A l, mark_application_sent(), Manual fallback: record an externally-submitted application as sent., log_event(), Connection, Append an audit event. Used for status_change, human_approved, email_sent, etc., Move an application to to_status if legal; log a status_change event.      Retur (+11 more)

### Community 65 - "test_fact_id_consistency.py"
Cohesion: 0.20
Nodes (15): bank(), _bank_payload(), Path, Task 35 item 2: a fact bank whose claim ids do not extend their entry is invalid, The real bank must satisfy the rule the loader now enforces., This is the exact shape the Baïfall entry had., Projects have the same shape as experience, so they get the same rule., `experience.baifallX` starts with the entry id as a STRING but is a     differen (+7 more)

### Community 66 - "review.py"
Cohesion: 0.14
Nodes (22): CatalogueEntry, default_catalogue(), load_variant_catalogue(), _parse_criteria(), _parse_shortcuts(), Path, The CV catalogue offered to the advisor when it selects a variant.  The selectio, Read the two-column selection table, skipping its header and separator. (+14 more)

### Community 67 - "ingest_source"
Cohesion: 0.11
Nodes (34): _answer(), _decision(), _offer(), Any, Connection, Exception, LogCaptureFixture, Path (+26 more)

### Community 68 - "_AnchorParser"
Cohesion: 0.14
Nodes (19): source_id(), _backfill_company_source(), _insert_offer(), Connection, Ingestion orchestrator: pull normalized records from a Source into the DB.  Idem, INSERT OR IGNORE one offer. Returns True if a new row was created., Append one row to source_runs. Does not commit; the caller owns that.      A fai, Teach an existing company row where it came from, once.      A company first see (+11 more)

### Community 69 - "test_preview.py"
Cohesion: 0.23
Nodes (19): _fake_clone(), _git(), CompletedProcess, Path, Task 41: one command after a merge, and it refuses rather than half-updates.  sc, The loud refusal. A fast-forward carries uncommitted work with it., The point of the conditions: the two slow steps cost nothing here., Kickstarting the agents is unconditional: new code is only running once     the (+11 more)

### Community 70 - "vocabulary.py"
Cohesion: 0.17
Nodes (17): live_db(), _Observed, _offer(), Connection, Exception, Path, Task 41 follow-up: the write lock is not held across the network.  Task 41 put W, Draining buys the lock back without giving up atomicity — which is what     comm (+9 more)

### Community 71 - "UnknownFactIdError"
Cohesion: 0.08
Nodes (47): _alert_source_clause(), Connection, Restrict to one alert source, or to all of them when none is named., Re-derive company / city / workplace / easy-apply for stored alert offers., reparse_alerts(), ReparseResult, parse_linkedin(), Extract jobs from a LinkedIn job-alert email. (+39 more)

### Community 72 - "Baifall Dream Stage - Reference Document (v3)"
Cohesion: 0.17
Nodes (11): Baifall Dream Stage - Reference Document (v3), Bloc HTML de reference (3 bullets), Bullet 1 (commun, accompli) - 167 car., rendu sur 2 lignes, Bullet 2 (commun, nominal, perimetre complet) - 127 car., 1 ligne, Bullet 3 : declinaisons par variante, Context, Principe v3 : perimetre nominal complet, Regle pour la date (+3 more)

### Community 73 - "test_facts.py"
Cohesion: 0.10
Nodes (29): FormField, infer_profile_field(), One control's shape. Deliberately has nowhere to put a typed value., Everything naming this field, with separators folded to spaces.          Real fo, Name the reason this field may never be mapped, or None if it may.      Refused:, Which profile field this control wants, or None to leave it to the human., Record mappings for one manually submitted form. Values are never stored.      C, Every refusal category present in a form, for reporting to the human. (+21 more)

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
Cohesion: 0.18
Nodes (20): get_or_create_company(), CompanyRecord, _no_real_sleeping(), Connection, MonkeyPatch, Backoff between retries is real seconds; the test suite must not spend them., Only fetch_companies() produces outreach targets, not offer side effects., Task 34.0: a NULL source is backfilled, so the row reaches --targets. (+12 more)

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
Cohesion: 0.33
Nodes (11): _approve(), Connection, LogCaptureFixture, Path, The asset file calls these false positives outside a full render., Task 39: the last hard position of the orphan gate went advisory.      It cost t, The reliable control, per the asset file, so it never becomes advisory., test_a_clean_generation_records_no_orphan_warning() (+3 more)

### Community 88 - "profile.py"
Cohesion: 0.07
Nodes (58): Return capability-tier tokens that have tripped generations, by frequency., vocabulary_misses(), GenericVocabularyError, load_generic_vocabulary(), parse_rejections(), Path, StrEnum, ValueError (+50 more)

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
Cohesion: 0.05
Nodes (80): Container, _advisor_prompt(), allowed_numbers(), _bank_parts(), _correction_block(), _guessed_section(), letter_scope(), _normalized_number() (+72 more)

### Community 112 - "Connection"
Cohesion: 0.17
Nodes (18): fields_from_html(), Connection, Read a page's controls as shapes. Values are stripped before we see them., Whether pressing submit is allowed on this domain. Default: no.      Prefill is, Flip the per-domain submit gate. Deliberately has no global counterpart., set_submit_enabled(), submit_enabled(), Connection (+10 more)

### Community 113 - "apply_matching_profile_cmd"
Cohesion: 0.19
Nodes (14): _extract_profile_domain(), _profile_of(), Path, Task 40: the domain phrase is found by its own marker, not by its neighbours.  _, Not just the wordings we ship: any of them, including ones nobody wrote yet., A rewrite that dropped it would break the next read instead of this one., The ±15-character layout budget must not shift under it., The bug. This raised "template profile domain phrase not found". (+6 more)

### Community 114 - "test_variant_selection.py"
Cohesion: 0.09
Nodes (30): _fact_id_key(), Fold separator and case differences, and nothing else, for comparison., Map a cited id onto a real fact id, accepting only unambiguous matches.      Mat, resolve_fact_id(), _advise(), ambiguous_bank(), _offer(), Any (+22 more)

### Community 115 - "labonnealternance.py"
Cohesion: 0.19
Nodes (14): bank(), _plan(), Task 40 amendment: bullets had a floor and no ceiling.  _validate_experience_com, The ceiling does not soften the other direction., Floor beats ceiling; a template row count under it cannot make a bad CV., End to end: the renderer inserts what survived, not what was asked for., A plan whose most recent employer selects `facts_for_first` of its facts., The reproduction: nine facts into three rows. (+6 more)

### Community 116 - "test_profile_domain_anchor.py"
Cohesion: 0.12
Nodes (20): approve_application(), Any, Connection, Record human approval, transition, and generate through one shared path.      ``, Connection, Path, test_a_rejected_number_is_counted_separately_from_an_invented_id(), _OneShotProfileOrphan (+12 more)

### Community 117 - "tracker.py"
Cohesion: 0.38
Nodes (8): FakeSource, Connection, Re-running ingest must never duplicate rows (constitution idempotency rule)., _sample(), test_company_deduped_across_offers_and_runs(), test_first_run_inserts_all(), test_last_run_at_updated(), test_second_run_inserts_nothing()

### Community 118 - "_TextParser"
Cohesion: 0.14
Nodes (5): letter_plain_text(), Path, Strip a generated letter's markup down to what a human would paste., The generated letter as plain text, or '' when it was never generated., _TextParser

### Community 119 - "FormField"
Cohesion: 0.10
Nodes (36): SentenceTransformer, apply_matching_profile_cmd(), Connection, _queue_snapshot(), Apply config/matching_profile.yaml and report what it changed.      Re-scoring i, Count what currently clears the bar, for an honest before/after., Re-evaluate every offer against the new vocabulary.      ``jobpilot score`` only, _rescore_all() (+28 more)

### Community 120 - "test_preview.py"
Cohesion: 0.67
Nodes (3): _F, gate(), Label what this function refuses, and what refusing costs.      Attached to the

### Community 121 - "Any"
Cohesion: 0.20
Nodes (14): mapping_is_complete(), mappings_for(), put_mapping(), Write one mapping. Rejects a profile_field outside the closed enum., Whether ``domain`` has enough of a mapping to be worth calling a route., LogCaptureFixture, Falling back to manual_open is correct behaviour, not a bug., An arbitrary string is not acceptable — this decides what gets typed in. (+6 more)

### Community 124 - "_reject_unsupported_tokens"
Cohesion: 0.27
Nodes (12): _dropping_enabled(), _InventsForever, Connection, MonkeyPatch, Path, Turning it off restores the old behaviour exactly., Enabling degradation does not make everything droppable., Nobody reviews what they were not told about. (+4 more)

### Community 125 - "gate"
Cohesion: 0.09
Nodes (25): as_dicts(), clear_warnings(), _decode(), Any, Connection, What a generation had to degrade, recorded where the reviewer will see it.  Task, Template-facing shape., Replace this application's warnings with the ones from this run. (+17 more)

### Community 126 - "Connection"
Cohesion: 0.17
Nodes (11): build_cv_title(), normalise_role_title(), Remove posting metadata while preserving the actual role wording., Build the deterministic CV title used after all advisor providers., Fact-bank loading, review CLI, and deterministic role-title cleaning., test_build_cv_title_uses_clean_role_and_contract_specific_suffix(), test_every_skill_is_explicitly_verified_or_unverified(), test_fact_bank_covers_every_cv_template_and_has_unique_claim_ids() (+3 more)

### Community 128 - "Path"
Cohesion: 0.32
Nodes (13): _as_utc(), daily_cap_reached(), _has_human_approval(), _last_cold_send(), prepare_cold_email(), Connection, datetime, Combined application + cold-mail sends recorded for today (UTC). (+5 more)

### Community 129 - "test_bullet_ceiling.py"
Cohesion: 0.13
Nodes (15): nearest_entry_claim_ids(), The entry a bad citation came closest to naming, and its real claim ids.      Ne, _shared_prefix(), bank(), Task 35 item 3: a rejection that says what would have been valid.  Task 22c allo, The regression test for the failure that burned two generations., `experience.` is common to every experience entry. Matching on it would     list, A large entry must not blow the retry prompt. (+7 more)

### Community 130 - "score"
Cohesion: 0.18
Nodes (7): adapter_for_url(), ApplyAdapter, BrowserLauncher, Protocol, A launch seam: production opens Playwright, tests supply a stub page., Common adapter interface for a best-effort ATS prefill., Return the owning ATS adapter, if the saved offer URL is recognized.

### Community 131 - "apply_matching_profile"
Cohesion: 0.38
Nodes (7): Connection, Path, Nothing is weakened: a fabrication ends the run exactly as before., An invented figure is recoverable — the retry is handed the real ones —     but, test_a_fatal_gate_still_aborts(), test_a_recoverable_gate_with_no_degradation_escalates_to_fatal(), test_an_advisory_gate_never_blocks()

### Community 132 - "observable_controls"
Cohesion: 0.11
Nodes (27): _Control, _ControlParser, _controls_from_html(), FillAction, _first_matching_selector(), _Form, _FormParser, _forms_from_html() (+19 more)

### Community 135 - "update.sh"
Cohesion: 0.60
Nodes (3): changed_since_pull(), die(), update.sh script

### Community 136 - "scheduler_status"
Cohesion: 0.09
Nodes (43): age_in_days(), annotate(), describe(), drop_stale(), _label(), max_offer_age_days(), _parse(), Any (+35 more)

### Community 138 - "mappings_for"
Cohesion: 0.14
Nodes (13): _plan(), Path, Task 41: the header location is found by its own marker, not by its neighbours., A template re-exported with a plain pin and a different separator.      Under th, The rewrite site and the two read sites agree, on real tailored output., The header is a fixed-width line; the span must not consume any of it., The header location is renderer-owned: it comes from the offer's city., The premise of the fix, asserted rather than assumed.      If this ever fails th (+5 more)

### Community 142 - "_Advisor"
Cohesion: 0.23
Nodes (7): _Advisor, _application(), Connection, Path, test_generation_failure_returns_application_to_queue(), test_generation_runs_quality_gates_before_pdfs_and_moves_to_ready(), _Toolchain

## Knowledge Gaps
- **158 isolated node(s):** `profile`, `contacts`, `suppression_list`, `offers`, `offers` (+153 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `mailer.py` to `Path`, `score`, `_client`, `observable_controls`, `Path`, `test_routing.py`, `RefreshRunner`, `wttj.py`, `SourcedBullet`, `france_travail.py`, `_FakePage`, `test_email_alerts.py`, `test_labonnealternance.py`, `_Toolchain`, `test_dashboard_facts_scheduler.py`, `.from_mapping`, `_FakePage`, `MissingCredentialError`, `pick_variant`, `launch_application_assist`, `test_designation_numbers.py`, `Path`, `_TextParser`, `_FakeLocator`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `RefreshRunner` to `Path`, `_client`, `observable_controls`, `dashboard.py`, `test_dedup.py`, `scheduler_status`, `mailer.py`, `test_routing.py`, `get_settings`, `test_skim.py`, `wttj.py`, `SourcedBullet`, `france_travail.py`, `launch_wttj_application`, `generate_application`, `test_email_alerts.py`, `.from_mapping`, `test_cold_outreach.py`, `MissingCredentialError`, `ingest_source`, `test_fact_id_resolution.py`, `test_mailer.py`, `test_designation_numbers.py`, `FormField`, `_reject_unsupported_tokens`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Why does `get_logger()` connect `france_travail.py` to `Request`, `observable_controls`, `dashboard.py`, `Path`, `scheduler_status`, `mailer.py`, `test_descriptions.py`, `contacts.py`, `RefreshRunner`, `wttj.py`, `SourcedBullet`, `cli.py`, `test_dashboard_facts_scheduler.py`, `.from_mapping`, `MissingCredentialError`, `resolve_fact_id`, `ingest_source`, `launch_application_assist`, `test_mailer.py`, `_AnchorParser`, `Path`, `FormField`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 62 inferred relationships involving `Settings` (e.g. with `ApplicantProfile` and `ApplyAdapter`) actually correct?**
  _`Settings` has 62 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `current_status()` (e.g. with `test_a_fatal_gate_still_aborts()` and `test_a_recoverable_gate_with_no_degradation_escalates_to_fatal()`) actually correct?**
  _`current_status()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `_payload()` (e.g. with `_plan()` and `_plan()`) actually correct?**
  _`_payload()` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `TailoringError` (e.g. with `ExperienceFact` and `FactBank`) actually correct?**
  _`TailoringError` has 24 INFERRED edges - model-reasoned connections that need verification._