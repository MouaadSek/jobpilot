-- Task 20.3: record whether an offer supports the provider's inline
-- application flow ("Candidature simplifiée" / "Easy Apply" on LinkedIn).
--
-- The marker was previously discarded as card chrome, or worse, stored as the
-- offer's city. It is real signal for the auto-apply work (Tasks 17/18), so it
-- gets its own flag rather than a text field.
--
-- Not folded into offers.stack_tags: that column is a *stack* keyword list
-- ("azure", "siem", ...) and matcher.py — frozen — reads it in keyword_score().
-- An application-method flag has no business in the frozen matcher's input.
--
-- Defaults to 0, so every existing row is "not known to support it", which is
-- the safe reading. Backfill via `jobpilot reparse-alerts`.

ALTER TABLE offers ADD COLUMN easy_apply INTEGER NOT NULL DEFAULT 0;
