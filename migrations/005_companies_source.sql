-- Task 33.2: record where a company came from.
--
-- The API Apprentissage returns companies "likely to hire an alternant"
-- alongside offers. They are cold-outreach targets, not offers, and they need to
-- be separable from companies created as a side effect of ingesting an offer --
-- otherwise there is no way to list outreach candidates. `notes` already exists
-- but is free text for humans; provenance is machine-read, so it gets a column.
--
-- Nullable: companies created before this migration, and those created from an
-- offer's employer name, legitimately have no source.

ALTER TABLE companies ADD COLUMN source TEXT;
