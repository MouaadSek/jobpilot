-- Task 9.3: capture a per-offer contact email (e.g. France Travail's contact.courriel)
-- so a ready application can be sent by email after explicit human confirmation.
-- Nullable; backfill is not required.

ALTER TABLE offers ADD COLUMN contact_email TEXT;
