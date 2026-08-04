"""Capture an offer description from a page the user already had open.

LinkedIn and Indeed arrive as alert emails carrying ~113 characters of
description — a card, not a posting. All five applications sent so far come from
that source, so every CV that has reached an employer was tailored against
almost nothing, while France Travail / LBA / WTTJ offers average ~1900
characters and tailor properly.

The text exists; it is on the page the user opened. This module takes it,
matches it to the offer JobPilot already holds, and puts the offer back through
the normal scoring path so it is ranked on real text.

**This is not scraping.** Nothing here fetches a URL, follows a link, or decides
which page to look at. It receives text that a human was already reading, in a
browser they opened, on a page they chose. See CLAUDE.md, "Scope of rule 11".

Scoring is not reimplemented: the score row is deleted and ``scoring.score`` —
the same function ``jobpilot score`` and the dashboard refresh call — is what
recomputes it, through frozen matcher.py.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from jobpilot.db import source_id
from jobpilot.logging_conf import get_logger

log = get_logger("offer_import")

#: Below this many characters the payload is a card, a cookie banner or an
#: accident, and storing it would replace a real description with nothing.
#: Above the alert average (~113) on purpose: an import that lands in that range
#: has captured the same card the alert already gave us.
MIN_IMPORTED_DESCRIPTION_CHARS = 200

#: The source an imported offer is filed under when JobPilot has never seen it.
IMPORT_SOURCE = "manual_import"


class OfferImportError(ValueError):
    """The payload cannot be stored as an offer description."""


# ---------------------------------------------------------------------------
# URL normalisation
# ---------------------------------------------------------------------------
#
# The same posting reaches us by two routes that never produce byte-identical
# URLs: a LinkedIn alert email links to
#     https://www.linkedin.com/comm/jobs/view/4434968054?trackingId=xY&refId=abc
# and the browser the user actually opens it in shows
#     https://www.linkedin.com/jobs/view/4434968054/?alternateChannel=search
#
# The rule below is a **denylist** of tracking parameters, not an allowlist of
# identifying ones, and that choice is the important part. Indeed puts the job
# key in the query string (`?jk=1a2b3c`), so dropping the whole query — which is
# the obvious reading of "strip query strings" — would collapse every Indeed
# posting onto one URL and merge unrelated jobs into a single offer. A denylist
# fails the other way: an unrecognised tracking parameter survives, the two URLs
# do not match, and we create a second offer row. A spurious extra row is a
# nuisance; two different jobs merged into one is a wrong CV sent to an
# employer.
#
# These names rot as the sites change. They live here, next to that reasoning.

#: Dropped wherever they appear. Lowercase; matching is case-insensitive.
_TRACKING_PARAMS = frozenset(
    {
        # Cross-site analytics
        "fbclid", "gclid", "gclsrc", "dclid", "msclkid", "mc_cid", "mc_eid",
        "igshid", "ref", "ref_src", "referrer", "source",
        # LinkedIn
        "refid", "trackingid", "trk", "trkinfo", "originaltrk", "original_referer",
        "alternatechannel", "eboriginalurl", "savedsearchid", "position",
        "pagenum", "discover", "lipi", "licu", "midtoken", "midsig", "eid",
        # Indeed
        "from", "tk", "advn", "adid", "sjdu", "acatk", "pub", "vjs", "xkcb",
        "xpse", "xfps", "alid", "rgtk", "hidesearchbox",
        # Welcome to the Jungle / generic campaign tags
        "q", "hiring_managers", "utm", "cmpid", "campaign_id",
    }
)

#: Dropped by prefix, so a new utm_* or ut_* variant needs no maintenance.
_TRACKING_PREFIXES = ("utm_", "ut_", "pk_", "mtm_", "_hs", "hsa_", "at_")

#: Path segments some sites inject for their own routing and which address the
#: same posting. LinkedIn's alert links go through /comm/.
_PATH_NOISE = ("/comm",)


def _is_tracking(name: str) -> bool:
    lowered = name.lower()
    return lowered in _TRACKING_PARAMS or lowered.startswith(_TRACKING_PREFIXES)


def normalize_offer_url(url: str) -> str:
    """Canonical form of an offer URL, for matching one posting to itself.

    Scheme and host lowercased, ``www.`` and a default port dropped, the
    fragment dropped, tracking parameters removed (see above), the remaining
    parameters sorted so ordering cannot make two identical URLs differ, and a
    trailing slash removed.

    The path keeps its case: job identifiers live in it and are case-sensitive.
    A string that does not parse as a URL is returned stripped and lowercased
    rather than raising — matching simply fails and the offer is created.
    """

    text = (url or "").strip()
    if not text:
        return ""
    try:
        parts = urlsplit(text)
    except ValueError:  # pragma: no cover - urlsplit is extremely permissive
        return text.lower()
    if not parts.netloc:
        return text.lower().rstrip("/")

    host = parts.hostname or ""
    if host.startswith("www."):
        host = host[4:]
    # A default port is the same address written two ways.
    port = parts.port
    if port in (80, 443):
        port = None
    netloc = f"{host}:{port}" if port else host

    path = parts.path
    for noise in _PATH_NOISE:
        if path.startswith(f"{noise}/"):
            path = path[len(noise):]
    if len(path) > 1:
        path = path.rstrip("/")

    kept = sorted(
        (name, value)
        for name, value in parse_qsl(parts.query, keep_blank_values=False)
        if not _is_tracking(name)
    )
    return urlunsplit(
        ((parts.scheme or "https").lower(), netloc, path, urlencode(kept), "")
    )


# ---------------------------------------------------------------------------
# Importing
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ImportResult:
    """What one import did, in terms the caller can show a human."""

    offer_id: int
    application_id: int | None
    application_status: str | None
    created: bool          # the offer did not exist and was created
    replaced_chars: int    # length of the description this one displaced
    imported_chars: int
    rescored: bool
    score: float | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "offer_id": self.offer_id,
            "application_id": self.application_id,
            "application_status": self.application_status,
            "created": self.created,
            "replaced_chars": self.replaced_chars,
            "imported_chars": self.imported_chars,
            "rescored": self.rescored,
            "score": self.score,
        }


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def clean_description(raw: str | None) -> str:
    """Collapse the whitespace a copied page carries, and keep the rest."""

    lines = [line.strip() for line in (raw or "").replace("\r\n", "\n").split("\n")]
    # Blank runs become one blank line: pages are full of them and they inflate
    # the length check without adding anything to embed.
    out: list[str] = []
    for line in lines:
        if line or (out and out[-1]):
            out.append(line)
    return "\n".join(out).strip()


def find_offer_by_url(db: sqlite3.Connection, url: str) -> sqlite3.Row | None:
    """The stored offer whose URL is the same posting, or None.

    Compared in Python rather than SQL: normalisation is a denylist plus a sort,
    which SQLite cannot express, and materialising a normalised column would
    mean every writer of offers.url has to maintain it. At 669 offers the scan
    is immaterial; if this table ever reaches a size where it is not, the column
    is the answer and this is the place to change.
    """

    target = normalize_offer_url(url)
    if not target:
        return None
    for row in db.execute("SELECT * FROM offers ORDER BY id").fetchall():
        if normalize_offer_url(row["url"]) == target:
            return row
    return None


def _create_offer(
    db: sqlite3.Connection,
    *,
    url: str,
    title: str,
    company: str | None,
    description: str,
) -> int:
    """Insert an offer JobPilot had never seen. It enters the pipeline normally.

    No application is created here: the offer is scored like any other, and the
    scoring pass queues it if it clears the threshold. That keeps the one path
    that creates offer applications inside matcher.py.
    """

    from jobpilot.ingest import get_or_create_company
    from jobpilot.models import CompanyRecord, OfferRecord

    company_id: int | None = None
    if company and company.strip():
        company_id, _ = get_or_create_company(
            db, CompanyRecord(name=company.strip()), {}
        )
    record = OfferRecord(
        external_id=None,
        url=url,
        title=title,
        description=description,
        company_name=company,
    )
    # contract_type and remote_policy stay 'unknown' and city stays NULL: the
    # page gives us prose, not parsed fields, and matcher.hard_filter lets all
    # three through by design ("unknown location: let it through, semantic will
    # judge"). Guessing them here would be inventing data to satisfy a filter.
    cursor = db.execute(
        "INSERT INTO offers (source_id, company_id, external_id, url, title, "
        " description, contract_type, remote_policy, city, scraped_at, "
        " content_hash, imported_at) "
        "VALUES (?, ?, NULL, ?, ?, ?, ?, ?, NULL, ?, ?, ?)",
        (
            source_id(db, IMPORT_SOURCE),
            company_id,
            url,
            title,
            description,
            record.contract_type,
            record.remote_policy,
            _utc_now(),
            record.hash,
            _utc_now(),
        ),
    )
    return int(cursor.lastrowid)


def import_offer_description(
    db: sqlite3.Connection,
    *,
    url: str,
    description: str,
    title: str | None = None,
    company: str | None = None,
    score_pass: Any | None = None,
) -> ImportResult:
    """Store a description captured from an open page, and re-score the offer.

    Raises OfferImportError on a payload too short to be a posting, rather than
    replacing a real description with a cookie banner.

    ``score_pass`` is injectable for the same reason RefreshRunner's is: the real
    one imports torch. It defaults to ``jobpilot.scoring.score``.
    """

    text = clean_description(description)
    if len(text) < MIN_IMPORTED_DESCRIPTION_CHARS:
        raise OfferImportError(
            f"description trop courte ({len(text)} caractères, minimum "
            f"{MIN_IMPORTED_DESCRIPTION_CHARS}) : une carte d'alerte ou une "
            "bannière de cookies, pas une annonce."
        )
    if not (url or "").strip():
        raise OfferImportError("une URL est nécessaire pour rattacher l'annonce.")

    row = find_offer_by_url(db, url)
    created = row is None
    if row is None:
        heading = (title or "").strip() or "Offre importée"
        offer_id = _create_offer(
            db, url=url, title=heading, company=company, description=text
        )
        replaced = 0
    else:
        offer_id = int(row["id"])
        replaced = len(row["description"] or "")
        # The title and company are only filled in, never overwritten: what the
        # source recorded went through its own parser, and the page heading is
        # frequently "Postuler | Acme" or similar.
        db.execute(
            "UPDATE offers SET description = ?, imported_at = ?, "
            "       title = COALESCE(NULLIF(title, ''), ?) "
            "WHERE id = ?",
            (text, _utc_now(), (title or "").strip() or None, offer_id),
        )

    # Invalidate, then re-score through the normal path. Deleting the row is
    # what makes matcher.score_new_offers pick this offer up: it selects offers
    # with no match_scores row. This deliberately does NOT use
    # descriptions.clear_match_scores, which skips offers that already have an
    # application — that rail protects a bulk pass from rewriting under a human
    # decision, and here the human IS the one asking, on one offer they named.
    db.execute("DELETE FROM match_scores WHERE offer_id = ?", (offer_id,))
    db.commit()

    rescored, score = _rescore(db, offer_id, score_pass)

    application = db.execute(
        "SELECT id, status FROM applications WHERE offer_id = ?", (offer_id,)
    ).fetchone()
    result = ImportResult(
        offer_id=offer_id,
        application_id=int(application["id"]) if application else None,
        application_status=application["status"] if application else None,
        created=created,
        replaced_chars=replaced,
        imported_chars=len(text),
        rescored=rescored,
        score=score,
    )
    log.info("offer import: %s", result.as_dict())
    return result


def _rescore(
    db: sqlite3.Connection, offer_id: int, score_pass: Any | None
) -> tuple[bool, float | None]:
    """Run the existing scoring pass. A failure here must not lose the text.

    The description is already committed by the time this runs, so a missing
    embedding model or an unconfigured profile costs the offer its new score and
    nothing else — the next `jobpilot score` picks it up, because the
    match_scores row is gone.
    """

    try:
        if score_pass is None:
            from jobpilot.scoring import score as score_pass  # heavy: torch
        score_pass(db)
    except Exception:
        log.exception("re-scoring offer %d after import failed", offer_id)
        return False, None

    row = db.execute(
        "SELECT final_score FROM match_scores WHERE offer_id = ?", (offer_id,)
    ).fetchone()
    return True, (float(row["final_score"]) if row and row["final_score"] is not None else None)
