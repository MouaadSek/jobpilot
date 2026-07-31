"""Download names an employer folder can still be read a week later.

``output/applications/42/cv.pdf`` is the right shape on disk — keyed by
application id, stable, and what every other module already resolves — and
exactly the wrong shape in a Downloads folder. The two needs are separated by
naming the file in the ``Content-Disposition`` header instead of on disk, so
nothing that resolves an artefact path has to change and no migration is needed.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

#: What each artefact is called in a filename. Short, because the company and
#: the candidate name are the parts that actually disambiguate.
ARTIFACT_LABELS: dict[str, str] = {
    "cv.pdf": "CV",
    "motivation_letter.pdf": "LM",
    "tailored_cv.html": "CV",
    "letter_body.html": "LM",
    "motivation_letter.html": "LM",
    "tracker.tsv": "Tracker",
}

#: Company names run long ("Société Générale Corporate and Investment Banking").
MAX_COMPANY_CHARS = 40
MAX_CANDIDATE_CHARS = 60

_DISALLOWED = re.compile(r"[^A-Za-z0-9-]+")
_RUNS = re.compile(r"_+")


def slugify(value: str | None, *, max_chars: int = MAX_COMPANY_CHARS) -> str:
    """Reduce free text to ``[A-Za-z0-9-_]``, or to "" if nothing survives.

    Accents are folded rather than dropped mid-word, so "Société" becomes
    "Societe" and not "Socit". Everything else outside the allowed set becomes an
    underscore, which is what keeps a company named "Société Générale / IT" from
    contributing a path separator to a filename.
    """

    if not value:
        return ""
    folded = unicodedata.normalize("NFKD", value)
    ascii_only = folded.encode("ascii", "ignore").decode("ascii")
    cleaned = _RUNS.sub("_", _DISALLOWED.sub("_", ascii_only)).strip("_-")
    return cleaned[:max_chars].strip("_-")


def download_filename(
    artifact: str,
    *,
    application_id: int,
    company: str | None = None,
    candidate: str | None = None,
) -> str:
    """Build ``<Company>_<Type>_<Nom>.<ext>`` for one artefact.

    Falls back to the application id when the company name is missing or
    slugifies away entirely, so the name is always unique and never empty.
    """

    suffix = Path(artifact).suffix
    label = ARTIFACT_LABELS.get(artifact) or slugify(Path(artifact).stem) or "Document"
    parts = [slugify(company) or f"application_{application_id}", label]
    who = slugify(candidate, max_chars=MAX_CANDIDATE_CHARS)
    if who:
        parts.append(who)
    return "_".join(parts) + suffix
