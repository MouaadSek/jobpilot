-- Task 39 item 2: a degraded document must not look like a clean one.
--
-- Generation is moving from "every gate aborts" to "fatal aborts, recoverable
-- degrades, advisory warns". That is only safe if the degradations are visible:
-- nobody reviews what they were not told about, and Mouaad reads every CV
-- before sending. A document that quietly lost a citation, fell back to the
-- template's profile wording, or shipped past an orphan warning has to say so.
--
-- JSON array rather than a warnings table: warnings have no identity, are never
-- queried across applications, are always read as a whole set, and are replaced
-- wholesale on every regeneration rather than accumulated. A table would buy
-- joins nobody needs and a delete-then-insert on every run. Each element is
-- {"gate": ..., "message": ..., "degraded": ...}.
--
-- Nullable: every existing row predates the column, and NULL is honestly
-- different from '[]' — "generated before warnings existed" is not the same
-- claim as "generated cleanly".

ALTER TABLE applications ADD COLUMN generation_warnings TEXT;
