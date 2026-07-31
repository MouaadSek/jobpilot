"""How a ready application would be sent, decided before anything runs.

``resolve_route`` is pure. It reads the offer row, the settings and the artefact
directory and returns the single route the Postuler button would take, together
with the higher-precedence routes that were eligible but unavailable and the
reason for each. It writes nothing, opens nothing, and makes no network call:
the entire point is that the human sees the plan before the plan runs.

A route whose availability requirement is unmet is never selected. Selecting a
route that then fails at click time is the failure mode this module exists to
prevent, so eligibility ("is the offer this kind of thing?") and availability
("is the machinery for it actually configured?") are kept apart and both are
reported.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from jobpilot.apply_assist import adapter_for_url
from jobpilot.config import Settings, get_settings
from jobpilot.logging_conf import get_logger

log = get_logger("routing")

RouteId = Literal[
    "wttj_inline",
    "ats_prefill",
    "learned_form",
    "email",
    "manual_open",
]

#: Fixed precedence. Higher routes are more automated; the last one always works.
ROUTE_PRECEDENCE: tuple[RouteId, ...] = (
    "wttj_inline",
    "ats_prefill",
    "learned_form",
    "email",
    "manual_open",
)

#: Artefacts an apply route may attach or upload, in the order a human reads them.
APPLY_ARTIFACTS: tuple[str, ...] = ("cv.pdf", "motivation_letter.pdf")

FRENCH_ROUTE_LABELS: dict[RouteId, str] = {
    "wttj_inline": "Formulaire WTTJ",
    "ats_prefill": "Formulaire ATS pré-rempli",
    "learned_form": "Formulaire appris",
    "email": "Envoi par email",
    "manual_open": "Ouverture manuelle",
}


class RouteError(RuntimeError):
    """Raised when an application cannot be routed at all."""


@dataclass(frozen=True, slots=True)
class UnavailableRoute:
    """A route the offer qualified for, and the reason it cannot be used."""

    id: RouteId
    reason: str

    def as_dict(self) -> dict[str, str]:
        return {"id": self.id, "label": FRENCH_ROUTE_LABELS[self.id], "reason": self.reason}


@dataclass(frozen=True, slots=True)
class Route:
    """The resolved plan for one application. Carries no state and stores none."""

    application_id: int
    id: RouteId
    target: str | None
    sentence: str
    artifacts: tuple[str, ...]
    unavailable: tuple[UnavailableRoute, ...] = ()

    @property
    def plan_hash(self) -> str:
        """Fingerprint of exactly the inputs that decided this route.

        Stateless by construction: no schema, no stored token, nothing to expire.
        Re-resolving between the plan and the click reproduces it, unless the
        offer was re-ingested or a contact was added in between — which is the
        one case the second click must not silently sail through.
        """

        payload = json.dumps(
            {
                "route": self.id,
                "target": self.target,
                "artifacts": list(self.artifacts),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]

    def as_dict(self) -> dict[str, object]:
        return {
            "application_id": self.application_id,
            "id": self.id,
            "label": FRENCH_ROUTE_LABELS[self.id],
            "target": self.target,
            "sentence": self.sentence,
            "artifacts": list(self.artifacts),
            "unavailable": [item.as_dict() for item in self.unavailable],
            "plan_hash": self.plan_hash,
        }


# ----- inputs -----


def _offer_row(db: sqlite3.Connection, application_id: int) -> sqlite3.Row:
    row = db.execute(
        "SELECT a.id, a.kind, a.status, o.url, o.contact_email, o.easy_apply, "
        "       s.name AS source, "
        "       (SELECT e.event FROM events e WHERE e.application_id = a.id "
        "        ORDER BY e.id DESC LIMIT 1) AS latest_event "
        "FROM applications a "
        "LEFT JOIN offers o ON o.id = a.offer_id "
        "LEFT JOIN sources s ON s.id = o.source_id "
        "WHERE a.id = ?",
        (application_id,),
    ).fetchone()
    if row is None:
        raise RouteError(f"no application with id={application_id}")
    if row["kind"] != "offer":
        # Cold outreach has its own queue, its own gates and its own daily cap.
        # It must not be reachable from the offer apply button.
        raise RouteError("only offer applications can be routed")
    if row["status"] != "ready":
        raise RouteError(
            f"application must be 'ready' to be routed (status: '{row['status']}')"
        )
    return row


def _artifacts(output_root: Path, application_id: int) -> tuple[str, ...]:
    application_dir = Path(output_root) / str(application_id)
    return tuple(
        name for name in APPLY_ARTIFACTS if (application_dir / name).is_file()
    )


def _missing_applicant_fields(settings: Settings) -> tuple[str, ...]:
    """Which APPLICANT_* values a form-filling route would find missing."""

    return tuple(
        name
        for name, value in (
            ("APPLICANT_FULL_NAME", settings.applicant_full_name),
            ("APPLICANT_EMAIL", settings.applicant_email),
            ("APPLICANT_PHONE", settings.applicant_phone),
            ("APPLICANT_LINKEDIN_URL", settings.applicant_linkedin_url),
        )
        if not value
    )


def _applicant_reason(settings: Settings) -> str | None:
    missing = _missing_applicant_fields(settings)
    if not missing:
        return None
    return f"{', '.join(missing)} manquant(s) dans .env"


def offer_domain(url: str | None) -> str | None:
    """The registrable-ish host a learned form mapping would be keyed by."""

    if not url:
        return None
    hostname = (urlparse(url).hostname or "").casefold()
    return hostname.removeprefix("www.") or None


def has_form_mapping(db: sqlite3.Connection, domain: str) -> bool:
    """Whether a *complete* learned mapping exists for ``domain``.

    Complete means it covers ``form_learning.REQUIRED_PROFILE_FIELDS``; a domain
    where only the phone field was ever learned is not worth routing to.
    Tolerates the table being absent so this module works both before and after
    migration 007.
    """

    table = db.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'form_mappings'"
    ).fetchone()
    if table is None:
        return False
    # Imported here rather than at module level: form_learning imports
    # apply_assist, which imports config, and routing is imported from
    # apply-time code paths that must not pay for that at import time.
    from jobpilot.form_learning import mapping_is_complete

    return mapping_is_complete(db, domain)


# ----- one function per route, in precedence order -----
#
# Each returns None when the offer is simply not that kind of thing, or
# (target, reason) where reason is None for "available" and a French string for
# "eligible but unusable, and here is why".

Decision = tuple[str | None, str | None] | None


def _wttj_inline(
    row: sqlite3.Row, settings: Settings, db: sqlite3.Connection, artifacts: Sequence[str]
) -> Decision:
    if row["source"] != "wttj" or not row["url"]:
        return None
    if row["latest_event"] == "submit_unconfirmed":
        # Same rule the WTTJ confirmation page already enforces: an unconfirmed
        # submission is never retried by machine.
        return None
    if not settings.wttj_api_key:
        return str(row["url"]), "WTTJ_API_KEY manquante"
    reason = _applicant_reason(settings)
    if reason is not None:
        return str(row["url"]), reason
    if "cv.pdf" not in artifacts:
        return str(row["url"]), "cv.pdf n'a pas été généré"
    return str(row["url"]), None


def _ats_prefill(
    row: sqlite3.Row, settings: Settings, db: sqlite3.Connection, artifacts: Sequence[str]
) -> Decision:
    url = str(row["url"] or "")
    adapter = adapter_for_url(url) if url else None
    # The prefill module refuses anything whose source is not 'ats', so matching
    # the URL alone would select a route that fails at click time.
    if adapter is None or adapter.name == "wttj" or row["source"] != "ats":
        return None
    reason = _applicant_reason(settings)
    if reason is not None:
        return url, reason
    if "cv.pdf" not in artifacts:
        return url, "cv.pdf n'a pas été généré"
    return url, None


def _learned_form(
    row: sqlite3.Row, settings: Settings, db: sqlite3.Connection, artifacts: Sequence[str]
) -> Decision:
    domain = offer_domain(row["url"])
    if domain is None or not has_form_mapping(db, domain):
        return None
    reason = _applicant_reason(settings)
    if reason is not None:
        return str(row["url"]), reason
    return str(row["url"]), None


def _email(
    row: sqlite3.Row, settings: Settings, db: sqlite3.Connection, artifacts: Sequence[str]
) -> Decision:
    address = str(row["contact_email"] or "").strip()
    if not address:
        return None
    if not (settings.smtp_username and settings.smtp_password):
        return address, "SMTP non configuré"
    if not artifacts:
        return address, "aucune pièce jointe générée"
    return address, None


def _manual_open(
    row: sqlite3.Row, settings: Settings, db: sqlite3.Connection, artifacts: Sequence[str]
) -> Decision:
    # Always available, and a legitimate terminal route rather than a failure.
    return (str(row["url"]) if row["url"] else None), None


_RESOLVERS = {
    "wttj_inline": _wttj_inline,
    "ats_prefill": _ats_prefill,
    "learned_form": _learned_form,
    "email": _email,
    "manual_open": _manual_open,
}


# ----- sentences -----


def _sentence(route_id: RouteId, target: str | None, artifacts: Sequence[str]) -> str:
    """Plain French for exactly what the second click will do. No hedging."""

    if route_id == "wttj_inline":
        return "Ouvre le formulaire WTTJ pré-rempli dans le navigateur. Ne soumet pas."
    if route_id == "ats_prefill":
        return "Ouvre le formulaire ATS pré-rempli dans le navigateur. Ne soumet pas."
    if route_id == "learned_form":
        domain = offer_domain(target) or "ce domaine"
        return (
            f"Ouvre le formulaire de {domain} pré-rempli depuis la correspondance "
            "apprise. Ne soumet pas."
        )
    if route_id == "email":
        count = len(artifacts)
        piece = "pièce jointe" if count == 1 else "pièces jointes"
        return f"Envoie un email à {target} avec {count} {piece}."
    return "Ouvre l'offre dans le navigateur et copie la lettre."


# ----- the resolver -----


def resolve_route(
    db: sqlite3.Connection,
    application_id: int,
    *,
    settings: Settings | None = None,
    output_root: Path | None = None,
) -> Route:
    """Resolve the one route this application would go out by. Writes nothing."""

    row = _offer_row(db, application_id)
    configured = settings or get_settings()
    artifacts = _artifacts(Path(output_root or configured.output_dir), application_id)
    unavailable: list[UnavailableRoute] = []

    for route_id in ROUTE_PRECEDENCE:
        decision = _RESOLVERS[route_id](row, configured, db, artifacts)
        if decision is None:
            continue
        target, reason = decision
        if reason is not None:
            unavailable.append(UnavailableRoute(route_id, reason))
            continue
        return Route(
            application_id=application_id,
            id=route_id,
            target=target,
            sentence=_sentence(route_id, target, artifacts),
            artifacts=artifacts,
            unavailable=tuple(unavailable),
        )

    # Unreachable: manual_open has no availability requirement.
    raise RouteError(f"application {application_id} resolved to no route at all")
