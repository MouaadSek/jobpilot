# Graph Report - jobpilot  (2026-07-31)

## Corpus Check
- 135 files · ~165,183 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2833 nodes · 7441 edges · 124 communities (107 shown, 17 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 478 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `92234fad`
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
- _approve
- ApplicantProfile
- _AnchorParser
- test_preview.py
- vocabulary.py
- UnknownFactIdError
- Baifall Dream Stage - Reference Document (v3)
- test_facts.py
- test_progress.py
- test_refresh.py
- schema.sql
- test_packaging.py
- CLAUDE.md - JobPilot project constitution
- AGENTS.md - JobPilot project constitution
- parse_indeed
- JobPilot prompt pack
- JobPilot: kickoff prompt for Claude Code
- CV Template Manifest
- generate_cv_pdf.py
- test_validate_cv_ai.py
- Phase 06: Review interface (Telegram bot)
- mappings_for
- VariantDecision
- Phase 02: Scraper sources (run after phase 01 is green)
- Phase 03: Apply integration (CV/letter generation bridge)
- Phase 04: Cold mail module
- Phase 05: Reply detection + tracker automation
- format_fact_bank
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
- ProvenanceScope
- test_facts.py
- apply_matching_profile_cmd
- test_state.py
- vocabulary.py
- format_fact_bank
- parse_indeed
- Route
- observable_controls
- SendBlocked
- VisibleBrowserLauncher
- _RecordingSender
- seeded_application

## God Nodes (most connected - your core abstractions)
1. `Settings` - 117 edges
2. `current_status()` - 88 edges
3. `_payload()` - 75 edges
4. `TailoringError` - 73 edges
5. `OfferRecord` - 68 edges
6. `FactBank` - 62 edges
7. `get_settings()` - 59 edges
8. `load_fact_bank()` - 57 edges
9. `OfferContext` - 51 edges
10. `create_app()` - 47 edges

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

## Communities (124 total, 17 thin omitted)

### Community 0 - "test_downloads.py"
Cohesion: 0.11
Nodes (27): AnthropicTailoringAdvisor, _extract_profile_domain(), extract_template_context(), InteractiveTailoringAdvisor, Read all editable choices without altering the template., Claude Messages API adviser used when ``ANTHROPIC_API_KEY`` is set., Terminal prompts used when interactive tailoring is selected., _Client (+19 more)

### Community 1 - "Request"
Cohesion: 0.18
Nodes (19): application_detail(), applications_by_status(), event_history(), outreach_drafts(), Any, Connection, queued_applications(), Read-only queries shared by review surfaces. (+11 more)

### Community 2 - "_candidate_name"
Cohesion: 0.19
Nodes (42): _client(), _events(), _no_advisor_client(), _offer_application(), Connection, MonkeyPatch, Path, Row (+34 more)

### Community 3 - "_client"
Cohesion: 0.08
Nodes (40): ExperienceFact, FactClaim, One atomic statement that generated content may cite., CvProfile, load_cv_profile(), Renderer-owned candidate facts injected into every generated CV., The location printed in the CV header when the offer yields none., Load the committed CV profile, failing loudly rather than defaulting. (+32 more)

### Community 4 - "create_app"
Cohesion: 0.07
Nodes (74): Match, Pattern, FactBank, _add_tech_additions(), _add_tech_keywords(), _bank_parts(), _contact_fields(), _contains() (+66 more)

### Community 5 - "dashboard.py"
Cohesion: 0.15
Nodes (23): list_outreach_targets(), Companies an ingestion source flagged as likely to hire an alternant.      These, get_or_create_company(), CompanyRecord, Yield companies likely to hire (optional; default: none)., _no_real_sleeping(), Connection, MonkeyPatch (+15 more)

### Community 6 - "run_dashboard"
Cohesion: 0.06
Nodes (63): ApplyOutcome, approve_application(), Any, Connection, Path, Record human approval, transition, and generate through one shared path.      ``, The result shared by the CLI and dashboard approval surfaces., CatalogueEntry (+55 more)

### Community 7 - "Path"
Cohesion: 0.09
Nodes (39): apply_matching_profile(), load_matching_profile(), MatchingProfile, Path, Write the vocabulary onto the profile singleton. Returns {field: (before, after), The scoring vocabulary, committed to git rather than typed once.      These thre, Load the committed matching vocabulary, failing loudly rather than defaulting., Connection (+31 more)

### Community 8 - "test_routing.py"
Cohesion: 0.11
Nodes (55): Cursor, _artifacts(), Path, Resolve the one route this application would go out by. Writes nothing., resolve_route(), _client(), Connection, MonkeyPatch (+47 more)

### Community 9 - "mailer.py"
Cohesion: 0.09
Nodes (45): is_professional_address(), True only for well-formed addresses NOT on a personal free-provider domain., Whether a named mailbox on a professional domain needs extra approval., requires_personal_confirmation(), _as_utc(), _build_message(), build_sender(), ColdEmailPreparation (+37 more)

### Community 10 - "validate_cv.py"
Cohesion: 0.06
Nodes (53): check_orphans(), find_regressions(), Path, Return orphan metrics that are new or materially worse than the template., format_date(), main(), build_letter_html(), detect_github() (+45 more)

### Community 11 - "get_settings"
Cohesion: 0.09
Nodes (40): SentenceTransformer, apply_matching_profile_cmd(), Connection, _queue_snapshot(), Apply config/matching_profile.yaml and report what it changed.      Re-scoring i, Count what currently clears the bar, for an honest before/after., Re-evaluate every offer against the new vocabulary.      ``jobpilot score`` only, _rescore_all() (+32 more)

### Community 12 - "connect"
Cohesion: 0.07
Nodes (42): apply_cmd(), mark_sent_cmd(), queue_cmd(), Re-derive company / city / workplace / easy-apply for stored alert offers., Clear stored match_scores so the next `score` run re-evaluates those offers., List queued applications, highest final_score first., Approve an application and generate its tailored application documents., Pass on an application: move queued -> skipped. (+34 more)

### Community 13 - "test_descriptions.py"
Cohesion: 0.08
Nodes (59): backfill_descriptions(), BackfillResult, clear_match_scores(), enrich_offer(), is_synthesized(), is_thin(), Connection, Synthesise matchable text for offers that arrive with no description.  Job-alert (+51 more)

### Community 14 - "test_generic_vocabulary.py"
Cohesion: 0.19
Nodes (18): bank(), _check(), LogCaptureFixture, Path, The vocabulary tier is config, and its misses are countable., Tier 1 must not be reachable through tier 3, so the file may not try., Silently allowing nothing would look like a strict validator, not a bug., The whole point: a category word is a config edit, not a release. (+10 more)

### Community 15 - "apply_assist.py"
Cohesion: 0.10
Nodes (12): _ControlParser, _Form, _FormParser, _forms_from_html(), _identity(), _page_offer_identity(), HTMLParser, Strip a generated letter's markup down to what a human would paste. (+4 more)

### Community 16 - "test_skim.py"
Cohesion: 0.11
Nodes (45): _create_application(), ignore_offer(), promote_offer(), Connection, Row, Offers that passed the hard filter and scored below the queue threshold.      An, The offer row, if it is genuinely one this page may act on., Create the offer's application row in 'queued'.      matcher.score_new_offers ow (+37 more)

### Community 17 - "contacts.py"
Cohesion: 0.12
Nodes (31): _candidate_name(), ContactCandidate, discover_and_store(), DiscoverySource, draft_cold_email(), draft_linkedin_note(), _get_or_create_cold_application(), is_suppressed() (+23 more)

### Community 18 - "JobPilot — Codex Handoff (complete A-to-Z)"
Cohesion: 0.04
Nodes (45): 10. HARD REJECTIONS (offers the pipeline should auto-skip), 11. API REFERENCES, 12. DESIGN PRINCIPLES (non-negotiable), 13. ENV VARS (.env), 14. GITHUB PUSH (do this FIRST, before any Codex work), 15. CODEX TASK BREAKDOWN (suggested order), 16. BAIFALL DREAM STAGE REFERENCE, 17. SCRIPTS REFERENCE (+37 more)

### Community 19 - "RefreshRunner"
Cohesion: 0.09
Nodes (32): ConnectionFactory, Event, _production_connection(), Any, Connection, Single-flight ingest + score pass driven from the dashboard., Block until the running refresh finishes. Tests use this, not sleeps., Claim the single flight and hand the work to a background thread. (+24 more)

### Community 20 - "_payload"
Cohesion: 0.10
Nodes (45): _bullets(), _offer(), _project(), The advisor selects; the renderer inserts the bank's wording unchanged., The pre-written variants from the skill asset, used as the asset intends., The contract has no field for prose, so a writing advisor fails loudly., Only the entry's own facts, so a skill id cannot become a bullet., Task 25's tolerance survives: ids are normalised before they are judged. (+37 more)

### Community 21 - "wttj.py"
Cohesion: 0.08
Nodes (45): _delay(), Call fn(); retry on transient HTTP errors with full-jitter exponential backoff., with_backoff(), _city(), _contact_email(), _contract(), _first(), map_hit() (+37 more)

### Community 22 - "SourcedBullet"
Cohesion: 0.05
Nodes (52): AmbiguousFactIdError, _fact_id_key(), _guessed_section(), nearest_entry_claim_ids(), _organisation_names(), Raised when a citation could be several facts. Never guess between them., The names the bank knows structurally: employers, schools, diplomas.      Naming, The scope for the letter and the profile's domain phrase.      Attribution still (+44 more)

### Community 23 - "france_travail.py"
Cohesion: 0.10
Nodes (24): _first_nonempty(), FranceTravailSource, _map_contact_email(), _map_contract(), _map_duration_months(), map_offer(), Any, Parse '... - 12 Mois' style durations from typeContratLibelle. (+16 more)

### Community 24 - "test_provenance_tiers.py"
Cohesion: 0.08
Nodes (37): SkillFact, _in_bank(), _offer(), Three kinds of token, three different burdens of proof., Not even the widest scope can support it., The reader has to be able to search for it, or add it to the config., Task 26's handling survives as the digit-shaped corner of tier 2., Presence in the bank is necessary for tier 2, never sufficient. (+29 more)

### Community 25 - "launch_wttj_application"
Cohesion: 0.12
Nodes (14): BrowserLauncher, _ConfirmationBaseline, _css_attribute_value(), _Locator, _Page, PrefillPlan, Protocol, The actions selected from a page's current HTML fixture/markup. (+6 more)

### Community 26 - "Dashboard"
Cohesion: 0.05
Nodes (36): Actualiser les offres (refresh from the page), Always up, without a terminal, Architecture (summary), ATS application assist (prefill only), Background scheduling, CI, Cold outreach sending (disabled by default), Commands (+28 more)

### Community 27 - "_FakePage"
Cohesion: 0.10
Nodes (21): ApplyAdapter, _BaseAdapter, GreenhouseAdapter, LeverAdapter, Common adapter interface for a best-effort ATS prefill., Shared plan building and non-submitting form interaction., SmartRecruitersAdapter, _FakeLauncher (+13 more)

### Community 28 - "cli.py"
Cohesion: 0.14
Nodes (31): _archives(), _artifact_names(), Connection, Path, Task 34.A: the dashboard's Régénérer button.  The button re-runs the *existing*, Overwriting would destroy the evidence the button exists to produce., Back-to-back clicks land in the same UTC second; neither may be lost., ISO 8601 basic format: the extended form's colons are illegal on NTFS. (+23 more)

### Community 29 - "test_desktop_shell.py"
Cohesion: 0.07
Nodes (35): CaptureFixture, dashboard_already_running(), Whether something is already listening on the dashboard's port.      A connect p, counts(), Connection, Ready and queued offer applications, the two numbers worth a glance., The menu bar text. Short: it competes with every other item up there., title() (+27 more)

### Community 30 - "generate_application"
Cohesion: 0.08
Nodes (26): CompletedProcess, date, _check_orphans(), DocumentToolchain, _french_date(), generate_application(), _load_offer(), _persist_variant() (+18 more)

### Community 31 - "test_contacts.py"
Cohesion: 0.10
Nodes (27): ModuleType, JobPilot: personal job application pipeline for the French IT/cybersecurity mark, _application(), _ConnectionProxy, Connection, Exception, Path, CLI coverage for offer document generation and cold-application approval. (+19 more)

### Community 32 - "test_email_alerts.py"
Cohesion: 0.18
Nodes (27): html_of(), LinkedInAlertSource, Return the best HTML (or plain-text) body of an email message., _FakeIMAP, _fixture_message(), _msg(), Connection, EmailMessage (+19 more)

### Community 33 - "test_labonnealternance.py"
Cohesion: 0.13
Nodes (33): _fixture(), _NoWait, LogCaptureFixture, La Bonne Alternance through the API Apprentissage: mapping, rails, ingestion.  E, The endpoint has no pagination, so this is the volume knob that exists., A full ingest reads both lists; it must not pay for the search twice., The live API really does repeat an offer inside one response., A company that has posted nothing must not appear in the review queue. (+25 more)

### Community 34 - "_Toolchain"
Cohesion: 0.08
Nodes (43): _advise_and_tailor(), _advisor_fact_context(), _advisor_prompt(), _correction_block(), _default_letter(), _interactive_structured_payload(), _is_validator_rejection(), _json_object() (+35 more)

### Community 35 - "email_alerts.py"
Cohesion: 0.07
Nodes (36): Logger, Put text on the system clipboard, or say plainly that it could not.  The manual_, Ingestion orchestrator: pull normalized records from a Source into the DB.  Idem, get_logger(), Central logging setup. Library code logs here; it never uses print()., Idempotent: attaches a rotating file handler + console handler once., setup_logging(), Optional macOS menu bar item: ready / queued counts, click to open.  ``rumps`` i (+28 more)

### Community 36 - "test_alert_card_fields.py"
Cohesion: 0.22
Nodes (16): _alert_source_clause(), Connection, Restrict to one alert source, or to all of them when none is named., Re-derive company / city / workplace / easy-apply for stored alert offers., reparse_alerts(), ReparseResult, Connection, The card line survived in companies.name; the city held only chrome. (+8 more)

### Community 37 - "Settings"
Cohesion: 0.11
Nodes (31): Decision, RouteId, adapter_for_url(), Auditable outcome of one approved WTTJ dashboard action., Return the owning ATS adapter, if the saved offer URL is recognized., WTTJApplyResult, Remove configured secrets from exception text before display/logging., Settings (+23 more)

### Community 38 - "Job Application Pipeline"
Cohesion: 0.06
Nodes (31): Alternance vs Stage, Edge Cases & Principles, Encoding note, Execution Flow, Flag once, then execute:, Generate with the bundled script:, GitHub Exception, Hard rejections (no output): (+23 more)

### Community 39 - "matcher.py"
Cohesion: 0.15
Nodes (28): bonus_score(), cosine(), hard_filter(), keyword_score(), norm(), pick_variant(), Profile, Connection (+20 more)

### Community 40 - "test_cv_completeness.py"
Cohesion: 0.12
Nodes (24): _category_skills(), _CompleteAdvisor, Any, Connection, Path, _Toolchain, _queued_application(), Structural completeness floor for AI-generated CVs (Task 22).  Selection freedom (+16 more)

### Community 41 - "OfferRecord"
Cohesion: 0.12
Nodes (16): Message, GmailIMAP, Minimal read-only Gmail IMAP client., Fetch recent mail sent from `domains` (or any of their subdomains).          The, Return the lowercased domain of the address in a `From` header.      Parses the, True when the From address sits on one of `domains` or a subdomain of it., sender_allowed(), sender_domain() (+8 more)

### Community 42 - "test_dashboard_facts_scheduler.py"
Cohesion: 0.15
Nodes (26): daemon_status(), DaemonStatus, Any, Connection, Last recorded run per enabled source. ``last_run_at`` is all the DB keeps., Everything the queue page shows about scheduled ingestion., What can honestly be said about the daemon, and nothing more., Report daemon liveness from the heartbeat file, or admit it is unknown. (+18 more)

### Community 43 - ".from_mapping"
Cohesion: 0.12
Nodes (31): pick_variant(), Pick the best of 21 variants from missions, then apply contract rules.      Sinc, _plan_for(), _experience_content(), _gemini_shaped_payload(), _offer(), AI-authored CV/letter content must be traceable to the fact bank., The observed real case: Gemini fills both structures, we keep the sourced one. (+23 more)

### Community 44 - "test_cold_outreach.py"
Cohesion: 0.22
Nodes (25): _cold_draft(), _configure_dashboard(), _dashboard_client(), _event_rows(), Connection, EmailMessage, Exception, MonkeyPatch (+17 more)

### Community 45 - "_FakePage"
Cohesion: 0.21
Nodes (23): launch_wttj_application(), _open_for_human(), Fill a WTTJ inline form and submit only behind the explicit live gate., _events(), _FakeLauncher, _FakePage, Connection, Path (+15 more)

### Community 46 - "MissingCredentialError"
Cohesion: 0.15
Nodes (22): current_status(), ValueError, _generation_failed_detail(), _InteractiveShapedAdvisor, _offer(), Any, Connection, LogCaptureFixture (+14 more)

### Community 47 - "ats.py"
Cohesion: 0.15
Nodes (23): download_filename(), Download names an employer folder can still be read a week later.  ``output/appl, Reduce free text to ``[A-Za-z0-9-_]``, or to "" if nothing survives.      Accent, Build ``<Company>_<Type>_<Nom>.<ext>`` for one artefact.      Falls back to the, slugify(), _client(), Connection, Path (+15 more)

### Community 48 - "AnthropicTailoringAdvisor"
Cohesion: 0.15
Nodes (21): ATSSource, infer_contract(), load_targets(), map_greenhouse(), map_lever(), map_smartrecruiters(), _ms_to_iso(), Any (+13 more)

### Community 49 - "OpenAITailoringAdvisor"
Cohesion: 0.16
Nodes (26): SimpleNamespace, build_advisor(), OpenAITailoringAdvisor, OpenAI-compatible Chat Completions adviser., Select the configured provider without silently bypassing missing keys., _offer(), _openai_response(), _plan_payload() (+18 more)

### Community 50 - "resolve_fact_id"
Cohesion: 0.16
Nodes (23): parse_linkedin(), Extract jobs from a LinkedIn job-alert email., _card_html(), LogCaptureFixture, Structural parsing of job-alert cards (Task 20).  Every fixture here is shaped a, Whatever position the chrome occupies, it must not be stored., None is strictly better: the hard filter reads it as "do not reject"., Observed verbatim: "Levallois-Perret (Sur site) Candidature simplifiée". (+15 more)

### Community 51 - "test_tech_additions.py"
Cohesion: 0.15
Nodes (26): bank(), _offer(), LogCaptureFixture, Zone 3 may add a keyword, but only one he has and the offer asked for., Reorder-only remains the default and the common case., Genuinely his, but padding: the offer did not ask for it., Presence in the bank is necessary, never sufficient., Derived from the file, not a magic number. (+18 more)

### Community 52 - "load_fact_bank"
Cohesion: 0.18
Nodes (24): _boolean(), CertificationFact, _claim_list(), EducationFact, _entry_claim(), FactBankError, LanguageFact, load_fact_bank() (+16 more)

### Community 53 - "CompanyRecord"
Cohesion: 0.15
Nodes (19): FormField, infer_profile_field(), One control's shape. Deliberately has nowhere to put a typed value., Everything naming this field, with separators folded to spaces.          Real fo, Name the reason this field may never be mapped, or None if it may.      Refused:, Which profile field this control wants, or None to leave it to the human., Every refusal category present in a form, for reporting to the human., refusal_category() (+11 more)

### Community 54 - "labonnealternance.py"
Cohesion: 0.12
Nodes (16): HTTPStatusError, MissingCredentialError, RuntimeError, Raised when a required secret is absent. We ask; we never silently mock., RateLimiter, Minimum-delay-per-domain limiter. Blocks until the next call is allowed., LaBonneAlternanceAuthError, LaBonneAlternanceError (+8 more)

### Community 55 - "ingest_source"
Cohesion: 0.15
Nodes (18): source_id(), _backfill_company_source(), ingest_source(), IngestResult, _insert_offer(), Connection, INSERT OR IGNORE one offer. Returns True if a new row was created., Run one source end to end. Commits once at the end for atomicity. (+10 more)

### Community 56 - "pick_variant"
Cohesion: 0.14
Nodes (12): content_hash(), OfferRecord, sha256(lower(title + company + first 500 chars of description)).      This is th, One normalized offer, ready to insert into the offers table., Coerce enum-constrained fields to legal values (schema CHECK safety)., Yield normalized offers. Must apply rate limiting + backoff internally., EmailAlertError, _EmailAlertSource (+4 more)

### Community 57 - "test_fact_id_resolution.py"
Cohesion: 0.09
Nodes (27): _advise(), ambiguous_bank(), bank(), _offer(), Any, LogCaptureFixture, Path, Citation ids are matched tolerantly; what may be claimed is unchanged. (+19 more)

### Community 58 - "test_letter_locked_fields.py"
Cohesion: 0.18
Nodes (19): bank(), _letter(), _offer(), A letter is prose about a career; a CV is slots the renderer fills., Naming a real-sounding employer he never had is a fabrication, not prose., The renderer injects the address block; the body repeating it is a bug., Otherwise the test above would prove nothing about scope., The bank's own text names nothing it should not; selection is the check. (+11 more)

### Community 59 - "launch_application_assist"
Cohesion: 0.10
Nodes (31): _application_for_assist(), _application_for_wttj(), ApplyAssistError, AssistResult, _fallback(), launch_application_assist(), letter_plain_text(), open_manually() (+23 more)

### Community 60 - "test_letter_quality.py"
Cohesion: 0.24
Nodes (15): french_de_elision(), Return « de <noun> » or « d'<noun> », applying French elision.      Elides befor, _validate_letter_body(), _letter(), _offer(), Letter quality: French elision and the 'Entreprise' placeholder rejection., test_default_letter_elides_poste_before_vowel(), test_default_letter_uses_votre_entreprise_when_company_unknown() (+7 more)

### Community 61 - "test_mailer.py"
Cohesion: 0.32
Nodes (15): _events(), Connection, EmailMessage, Exception, Path, Application email sending: rails, transitions, and events (mocked SMTP)., _ready_app(), _Sender (+7 more)

### Community 62 - "models.py"
Cohesion: 0.05
Nodes (64): FastAPI, LookupError, Request, ApplicationGenerationError, ApplicationNotFoundError, ApplicationNotQueuedError, archive_artifacts(), generation_single_flight() (+56 more)

### Community 63 - "reparse_alerts"
Cohesion: 0.20
Nodes (10): menubar_cmd(), Show ready/queued counts in the macOS menu bar (optional extra)., MenubarUnavailable, Any, RuntimeError, Raised when the menu bar item cannot run on this machine., Import rumps or explain, in French, exactly how to get it., Run the menu bar item until quit. Blocks; opens the dashboard on click. (+2 more)

### Community 64 - "test_designation_numbers.py"
Cohesion: 0.24
Nodes (15): _approve(), Connection, LogCaptureFixture, Path, The asset file calls these false positives outside a full render., The reliable control, per the asset file, so it never becomes advisory., test_a_clean_generation_records_no_orphan_warning(), test_an_orphan_in_the_generated_profile_still_fails() (+7 more)

### Community 65 - "test_fact_id_consistency.py"
Cohesion: 0.20
Nodes (15): bank(), _bank_payload(), Path, Task 35 item 2: a fact bank whose claim ids do not extend their entry is invalid, The real bank must satisfy the rule the loader now enforces., This is the exact shape the Baïfall entry had., Projects have the same shape as experience, so they get the same rule., `experience.baifallX` starts with the entry id as a STRING but is a     differen (+7 more)

### Community 66 - "_approve"
Cohesion: 0.13
Nodes (18): ApplicantProfile, The non-secret contact values entered into an ATS form., build_prefill(), discard_mapping(), FormLearningError, FormMapping, PrefillOutcome, _profile_values() (+10 more)

### Community 68 - "_AnchorParser"
Cohesion: 0.17
Nodes (22): _city(), _company_name(), _contract_type(), _domain(), _first(), map_company(), map_offer(), Any (+14 more)

### Community 69 - "test_preview.py"
Cohesion: 0.09
Nodes (30): derive_fields(), _Derived, Re-derive alert card fields (company / city / workplace / easy-apply) in place., Re-derive one offer's card fields from the text that was stored for it.      Pur, is_noise(), is_title_echo(), parse_card_line(), True when `text` is card chrome that must never be stored as a field. (+22 more)

### Community 70 - "vocabulary.py"
Cohesion: 0.25
Nodes (13): ingest_cmd(), Fetch offers from a source (or all sources) into the database., enabled_sources(), _enablement(), is_enabled(), Read config/sources.yaml. Unlisted sources default to enabled., Registered sources that are enabled in config, in registration order., Path (+5 more)

### Community 71 - "UnknownFactIdError"
Cohesion: 0.38
Nodes (8): FakeSource, Connection, Re-running ingest must never duplicate rows (constitution idempotency rule)., _sample(), test_company_deduped_across_offers_and_runs(), test_first_run_inserts_all(), test_last_run_at_updated(), test_second_run_inserts_nothing()

### Community 72 - "Baifall Dream Stage - Reference Document (v3)"
Cohesion: 0.17
Nodes (11): Baifall Dream Stage - Reference Document (v3), Bloc HTML de reference (3 bullets), Bullet 1 (commun, accompli) - 167 car., rendu sur 2 lignes, Bullet 2 (commun, nominal, perimetre complet) - 127 car., 1 ligne, Bullet 3 : declinaisons par variante, Context, Principe v3 : perimetre nominal complet, Regle pour la date (+3 more)

### Community 73 - "test_facts.py"
Cohesion: 0.14
Nodes (26): fields_from_html(), Read a page's controls as shapes. Values are stripped before we see them., Record mappings for one manually submitted form. Values are never stored.      C, Whether pressing submit is allowed on this domain. Default: no.      Prefill is, Flip the per-domain submit gate. Deliberately has no global counterpart., record_form_fields(), set_submit_enabled(), submit_enabled() (+18 more)

### Community 74 - "test_progress.py"
Cohesion: 0.22
Nodes (12): daemon_cmd(), Run ingest + score on a loop (Ctrl-C to stop)., heartbeat_path(), datetime, Path, Background daemon: run ingest + score on a fixed interval (default 3h).  The dae, One ingest-all + score pass. Sources with missing creds are skipped., Record that a cycle completed. Never fatal: a daemon must not die on this. (+4 more)

### Community 75 - "test_refresh.py"
Cohesion: 0.17
Nodes (17): Container, _designation_spans(), ProvenanceScope, Everything true of the career the generated text is describing.      Generated t, Check every designation against the scope; return what it covers.      Designati, Blank out validated designations, keeping every other offset intact., Build the rejection and record it, so the misses can be counted later.      This, Tier 1. A measurement belongs to the entry it was measured in. (+9 more)

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

### Community 80 - "parse_indeed"
Cohesion: 0.25
Nodes (17): Return capability-tier tokens that have tripped generations, by frequency., vocabulary_misses(), The one wording for a refused token; every caller goes through here.      Naming, rejection_message(), _failure(), Connection, MonkeyPatch, No vocabulary entry may ever excuse a fabricated number or employer. (+9 more)

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

### Community 87 - "mappings_for"
Cohesion: 0.20
Nodes (13): _Control, _controls_from_html(), FillAction, _first_matching_selector(), One safe local-file upload; never a form submit action., Whether a stored selector still finds a control on the current page., Match the deliberately simple tag[attr=value] selectors used below., Raised when an adapter cannot safely map a required field. (+5 more)

### Community 88 - "VariantDecision"
Cohesion: 0.23
Nodes (7): _Advisor, _application(), Connection, Path, test_generation_failure_returns_application_to_queue(), test_generation_runs_quality_gates_before_pdfs_and_moves_to_ready(), _Toolchain

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

### Community 93 - "format_fact_bank"
Cohesion: 0.08
Nodes (38): add_contact_cmd(), contacts_cmd(), _csv(), dashboard_cmd(), draft_cold_cmd(), init_profile_cmd(), _langs(), Interactively fill the profile singleton and seed cv_variants. (+30 more)

### Community 110 - "test_designation_numbers.py"
Cohesion: 0.17
Nodes (16): bank(), _in_bank(), LogCaptureFixture, A standard's digits name a thing; a metric's digits measure one., The anti-fabrication guarantee is not weakened by designation handling., Only the designation's own span is exempt from the number rule., Judge as the letter is judged: no entry, so the whole bank answers., Looking like a standard is not evidence of holding one. (+8 more)

### Community 111 - "ProvenanceScope"
Cohesion: 0.21
Nodes (14): mapping_is_complete(), mappings_for(), put_mapping(), Connection, Write one mapping. Rejects a profile_field outside the closed enum., Whether ``domain`` has enough of a mapping to be worth calling a route., LogCaptureFixture, Falling back to manual_open is correct behaviour, not a bug. (+6 more)

### Community 112 - "test_facts.py"
Cohesion: 0.14
Nodes (14): parse_rejections(), Recover the refused tokens from stored validator messages.      The events table, How much a token has to be backed up before it may be written., One token a validator refused, why, and what it was judged against., TokenRejection, TokenTier, StrEnum, Events outlive the code that wrote them, so the wording is the contract. (+6 more)

### Community 113 - "apply_matching_profile_cmd"
Cohesion: 0.18
Nodes (10): build_cv_title(), normalise_role_title(), Remove posting metadata while preserving the actual role wording., Build the deterministic CV title used after all advisor providers., Fact-bank loading, review CLI, and deterministic role-title cleaning., test_build_cv_title_uses_clean_role_and_contract_specific_suffix(), test_every_skill_is_explicitly_verified_or_unverified(), test_fact_bank_covers_every_cv_template_and_has_unique_claim_ids() (+2 more)

### Community 114 - "test_state.py"
Cohesion: 0.42
Nodes (9): _app(), Connection, State machine transition tests: legality + event auditing., Constitution: no send/submit without a prior human_approved event., test_full_happy_path(), test_human_approved_event_recorded(), test_illegal_transition_raises_and_no_change(), test_legal_transition_updates_and_logs() (+1 more)

### Community 115 - "vocabulary.py"
Cohesion: 0.25
Nodes (8): GenericVocabularyError, load_generic_vocabulary(), Path, ValueError, Three tiers of token, so a category word is not judged like a claim.  A sourced, Load the terms that assert nothing about the candidate.      Kept in config rath, Raised when the committed generic vocabulary is malformed., test_the_committed_vocabulary_loads_and_covers_the_reported_token()

### Community 116 - "format_fact_bank"
Cohesion: 0.50
Nodes (4): facts_cmd(), Print the provenance fact bank grouped for human review., format_fact_bank(), Render the bank as plain UTF-8 text for human review in the CLI.

### Community 117 - "parse_indeed"
Cohesion: 0.29
Nodes (7): clean_job_url(), parse_indeed(), Return a stable detail URL with email/tracking parameters removed., Extract jobs from an Indeed job-alert email., test_clean_job_url_removes_tracking_parameters(), test_parse_ignores_non_job_links(), test_parse_indeed_extracts_jk_ids()

### Community 118 - "Route"
Cohesion: 0.40
Nodes (3): The resolved plan for one application. Carries no state and stores none., Fingerprint of exactly the inputs that decided this route.          Stateless by, Route

### Community 119 - "observable_controls"
Cohesion: 0.50
Nodes (4): observable_controls(), Every fillable control's *shape*, for form learning. Never its contents.      ``, One enforcement point: values are stripped before this module sees them., test_observable_controls_never_expose_what_the_human_typed()

### Community 120 - "SendBlocked"
Cohesion: 0.50
Nodes (4): ColdSendDisabled, A rail (suppression list or daily cap) refuses the send. Not a failure., Live cold sending is disabled by configuration., SendBlocked

## Knowledge Gaps
- **154 isolated node(s):** `profile`, `contacts`, `suppression_list`, `offers`, `offers` (+149 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `Settings` to `test_routing.py`, `mailer.py`, `apply_assist.py`, `wttj.py`, `france_travail.py`, `launch_wttj_application`, `_FakePage`, `test_email_alerts.py`, `test_labonnealternance.py`, `email_alerts.py`, `OfferRecord`, `test_dashboard_facts_scheduler.py`, `_FakePage`, `AnthropicTailoringAdvisor`, `labonnealternance.py`, `pick_variant`, `launch_application_assist`, `_approve`, `ApplicantProfile`, `_AnchorParser`, `vocabulary.py`, `test_progress.py`, `mappings_for`, `Route`, `SendBlocked`, `VisibleBrowserLauncher`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `launch_application_assist` to `create_app`, `test_routing.py`, `mailer.py`, `get_settings`, `connect`, `RefreshRunner`, `wttj.py`, `generate_application`, `test_labonnealternance.py`, `email_alerts.py`, `Settings`, `OfferRecord`, `test_cold_outreach.py`, `_FakePage`, `OpenAITailoringAdvisor`, `test_mailer.py`, `models.py`, `vocabulary.py`, `test_progress.py`, `format_fact_bank`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `current_status()` connect `MissingCredentialError` to `_candidate_name`, `create_app`, `run_dashboard`, `test_routing.py`, `mailer.py`, `connect`, `test_skim.py`, `_FakePage`, `cli.py`, `generate_application`, `test_contacts.py`, `test_cv_completeness.py`, `test_cold_outreach.py`, `_FakePage`, `OpenAITailoringAdvisor`, `test_mailer.py`, `models.py`, `test_designation_numbers.py`, `VariantDecision`, `format_fact_bank`, `test_state.py`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Are the 62 inferred relationships involving `Settings` (e.g. with `ApplicantProfile` and `ApplyAdapter`) actually correct?**
  _`Settings` has 62 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `TailoringError` (e.g. with `ExperienceFact` and `FactBank`) actually correct?**
  _`TailoringError` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `OfferRecord` (e.g. with `BackfillResult` and `RescoreResult`) actually correct?**
  _`OfferRecord` has 23 INFERRED edges - model-reasoned connections that need verification._
- **What connects `profile`, `contacts`, `suppression_list` to the rest of the system?**
  _154 weakly-connected nodes found - possible documentation gaps or missing edges._