-- Add a free-text professional summary to the profile singleton.
-- Feeds build_profile_text() so the profile embedding reads like the
-- "ideal candidate" section of a job posting (richer semantic signal).
ALTER TABLE profile ADD COLUMN headline TEXT;
