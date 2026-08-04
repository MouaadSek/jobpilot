-- Task 43 item 1: an offer description captured from the page the user opened.
--
-- LinkedIn and Indeed alert emails carry ~113 characters of description — a
-- card, not a posting. All five applications sent so far come from that source,
-- so every CV that has reached an employer was tailored against almost nothing.
-- France Travail, LBA and WTTJ average ~1900 characters and tailor properly.
--
-- A column and not a description prefix. descriptions.py marks its synthesised
-- text with SYNTHESIZED_DESCRIPTION_PREFIX precisely to avoid a schema change,
-- and that works there because the marker is scaffolding the module wrote
-- itself. It does not work here: an imported description is the employer's real
-- prose, it is what the tailorer reads and what the semantic score embeds, and
-- prefixing it would put our bookkeeping inside the text that reaches a CV.
--
-- A timestamp and not a boolean, at the same storage cost: "imported" and "when"
-- are one question, and NULL is the honest value for an offer that never was.
-- is_imported is `imported_at IS NOT NULL` and nothing else tests for it.
--
-- Nullable with no default: every existing row predates the feature and none of
-- them was imported, which is exactly what NULL says.

ALTER TABLE offers ADD COLUMN imported_at TEXT;   -- ISO 8601 UTC, NULL if never

-- An offer imported from a page JobPilot had never seen needs a source row to
-- point at, and pinning it on linkedin_alert would be a lie: it did not come
-- from an alert email. kind='manual' is the schema's own word for this.
--
-- Registered in db._SEED_SOURCES too, so a fresh database gets it from
-- seed_sources rather than only from this migration. INSERT OR IGNORE because
-- both paths run on init-db and neither may fail on the other having gone first.
INSERT OR IGNORE INTO sources (name, kind, enabled, run_interval_min)
VALUES ('manual_import', 'manual', 1, 0);

-- Nothing in sources/registry.py builds a 'manual_import' Source, deliberately:
-- enabled_sources() iterates the registry, so the daemon can never try to ingest
-- from it and the Planification table never shows it as a silent source.
