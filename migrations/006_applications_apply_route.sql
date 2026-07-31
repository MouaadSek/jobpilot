-- Task 34.B: record which apply route an application actually went out by.
--
-- The unified Postuler button resolves one of wttj_inline / ats_prefill /
-- learned_form / email / manual_open. Which of those the pipeline really uses,
-- over months, is the only honest input to the eventual decision about how much
-- of the apply step to automate. Instinct has been wrong about this twice.
--
-- Nullable: every existing row predates the column, and manual_open is a
-- legitimate terminal route rather than a failure, so "not yet applied" and
-- "applied some other way" must stay distinguishable from each other.

ALTER TABLE applications ADD COLUMN apply_route TEXT;
