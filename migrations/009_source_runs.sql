-- Task 41 item 6: what a cycle actually did, per source, kept.
--
-- sources.last_run_at was the whole record of ingestion, so the Planification
-- table could only say « inconnu (non enregistré) » in its Résultat column. The
-- cost of that showed up as WTTJ returning nothing for a week: last_run_at kept
-- ticking forward on every cycle, the row looked healthy, and the only evidence
-- was in logs nobody reads.
--
-- A table and not columns on sources: "has this source errored on its last N
-- runs" is a question about a history, and last-value columns cannot answer it.
-- One row per source per run, appended, never updated.
--
-- error is NULL on a run that completed. A failed run records its fetched count
-- — the API really did return that many — and zero for the rest, because
-- ingest_source rolls its transaction back before writing this row, so no
-- offers and no companies survived it.
--
-- Nothing prunes this table. One row per source per cycle is roughly six rows a
-- day; it will not be the reason this database grows.

CREATE TABLE source_runs (
    id INTEGER PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    started_at TEXT NOT NULL,           -- ISO 8601 UTC
    finished_at TEXT NOT NULL,          -- ISO 8601 UTC
    fetched INTEGER NOT NULL DEFAULT 0,
    inserted INTEGER NOT NULL DEFAULT 0,
    duplicates INTEGER NOT NULL DEFAULT 0,
    companies_created INTEGER NOT NULL DEFAULT 0,
    error TEXT                          -- NULL when the run completed
);

-- The only read pattern: the newest runs of one source.
CREATE INDEX idx_source_runs_recent ON source_runs (source_id, id DESC);
