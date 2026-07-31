"""Learn the shape of an unknown application form once, reuse it forever.

An unknown domain costs effort once: the human fills the form and submits it
themselves, and what is recorded is the *mapping* — which selector holds which
profile field — so the next offer on that domain arrives prefilled.

Three rules govern everything here, because this table decides what gets typed
into a stranger's form:

* **Never record a value.** Only selectors, labels and profile-field names are
  stored. ``apply_assist.observable_controls`` strips ``value``/``placeholder``
  before this module ever sees a control, so there is one enforcement point
  rather than a discipline.
* **profile_field is a closed enum.** An arbitrary string is rejected at write
  time, not tidied up later.
* **Passwords, payment details and identity documents are never mapped.** They
  are detected, refused, logged, and left for the human permanently.

Selectors are brittle by nature. A stored mapping whose selector no longer
matches the page is discarded with a log rather than guessed around; falling
back to ``manual_open`` is correct behaviour, not a bug.
"""

from __future__ import annotations

import re
import sqlite3
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime

from jobpilot.apply_assist import (
    ApplicantProfile,
    observable_controls,
    selector_matches_html,
)
from jobpilot.logging_conf import get_logger

log = get_logger("form_learning")

#: The closed enum. Exactly what the profile genuinely holds, and nothing else.
PROFILE_FIELDS: frozenset[str] = frozenset(
    {
        "full_name",
        "first_name",
        "last_name",
        "email",
        "phone",
        "linkedin_url",
        "cv_path",
        "letter_path",
    }
)

#: Without these a prefill is not worth calling a route; see routing.learned_form.
REQUIRED_PROFILE_FIELDS: tuple[str, ...] = ("full_name", "email")

#: Input types that are refused outright, whatever they are labelled.
REFUSED_INPUT_TYPES: frozenset[str] = frozenset({"password"})

# Refusal patterns, grouped so a refusal can name its own category. Matched
# against the control's name, id, label, aria-label and autocomplete, folded to
# lowercase, in French and English because French forms are the common case.
REFUSAL_PATTERNS: tuple[tuple[str, str], ...] = (
    (
        "password",
        r"password|passwd|mot\s*de\s*passe|motdepasse|pwd|passphrase|"
        r"current\s*password|new\s*password|otp|code\s*secret|secret",
    ),
    (
        "payment",
        r"card\s*number|cardnumber|credit\s*card|debit\s*card|carte\s*bancaire|"
        r"\bcb\b|\biban\b|\bbic\b|\bswift\b|\brib\b|\bcvv\b|\bcvc\b|\bccv\b|"
        r"cc\s*number|cc\s*csc|cc\s*exp|expiry|expiration\s*date|paypal|"
        r"bank\s*account|compte\s*bancaire|coordonn[ée]es\s*bancaires",
    ),
    (
        "identity_document",
        r"\bssn\b|social\s*security|s[ée]curit[ée]\s*sociale|num[ée]ro\s*de\s*s[ée]cu|"
        r"\bnir\b|passport|passeport|carte\s*d.?identit[ée]|\bcni\b|id\s*card|"
        r"national\s*id|driver.?s?\s*licen[cs]e|permis\s*de\s*conduire|"
        r"titre\s*de\s*s[ée]jour|num[ée]ro\s*fiscal|tax\s*id",
    ),
)

_COMPILED_REFUSALS = tuple(
    (category, re.compile(pattern, re.IGNORECASE))
    for category, pattern in REFUSAL_PATTERNS
)

# Inference patterns, first match wins, checked in this order.
_INFERENCE: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("first_name", re.compile(r"first\s*name|pr[ée]nom|given\s*name", re.I)),
    (
        "last_name",
        re.compile(r"last\s*name|surname|family\s*name|\bnom\b(?!\s*complet)", re.I),
    ),
    ("email", re.compile(r"e-?mail|courriel", re.I)),
    ("phone", re.compile(r"phone|t[ée]l[ée]phone|\btel\b|mobile|portable", re.I)),
    ("linkedin_url", re.compile(r"linkedin", re.I)),
    ("cv_path", re.compile(r"\bcv\b|r[ée]sum[ée]|curriculum", re.I)),
    ("letter_path", re.compile(r"cover\s*letter|lettre|motivation", re.I)),
    ("full_name", re.compile(r"full\s*name|nom\s*complet|votre\s*nom|\bname\b", re.I)),
)


class FormLearningError(ValueError):
    """Raised when a mapping would break one of this module's hard rules."""


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(frozen=True, slots=True)
class FormField:
    """One control's shape. Deliberately has nowhere to put a typed value."""

    selector: str
    field_type: str = "text"
    name: str = ""
    label: str = ""
    autocomplete: str = ""

    @property
    def haystack(self) -> str:
        """Everything naming this field, with separators folded to spaces.

        Real forms write ``card_number``, ``mot-de-passe``, ``user.ssn``. A
        pattern that only spanned whitespace would miss every one of them, and a
        missed payment field is the failure that matters here.
        """

        joined = " ".join(
            part for part in (self.name, self.label, self.autocomplete, self.selector)
        )
        return re.sub(r"[_\-.]+", " ", joined)


@dataclass(frozen=True, slots=True)
class FormMapping:
    """A stored selector -> profile field mapping. Never a stored value."""

    domain: str
    selector: str
    profile_field: str
    label: str | None = None
    uses: int = 0


@dataclass(frozen=True, slots=True)
class RecordResult:
    """What one learning pass did, including everything it refused."""

    domain: str
    recorded: tuple[FormMapping, ...] = ()
    refused: tuple[tuple[str, str], ...] = ()  # (selector, category)
    skipped: tuple[str, ...] = ()  # selectors no profile field could be inferred for


# ----- the safety detector -----


def refusal_category(field: FormField) -> str | None:
    """Name the reason this field may never be mapped, or None if it may.

    Refused: any ``input[type=password]``; anything whose name, id, label,
    aria-label or autocomplete looks like a password, a payment instrument
    (card number, CVV/CVC, IBAN/BIC/SWIFT/RIB, expiry, bank account, PayPal) or
    an identity document (SSN/NIR/numéro de sécurité sociale, passport, CNI or
    other national ID, driving licence, titre de séjour, tax number).
    """

    if field.field_type.strip().casefold() in REFUSED_INPUT_TYPES:
        return "password"
    haystack = field.haystack
    for category, pattern in _COMPILED_REFUSALS:
        if pattern.search(haystack):
            return category
    return None


def infer_profile_field(field: FormField) -> str | None:
    """Which profile field this control wants, or None to leave it to the human."""

    if refusal_category(field) is not None:
        return None
    haystack = field.haystack
    for profile_field, pattern in _INFERENCE:
        if pattern.search(haystack):
            return profile_field
    return None


def fields_from_html(html: str) -> tuple[FormField, ...]:
    """Read a page's controls as shapes. Values are stripped before we see them."""

    fields = []
    for control in observable_controls(html):
        tag = control.get("tag", "input")
        name = control.get("name", "") or control.get("id", "")
        if not name:
            continue
        fields.append(
            FormField(
                selector=f'{tag}[name="{name}"]'
                if control.get("name")
                else f'{tag}[id="{name}"]',
                field_type=control.get("type", "text"),
                name=name,
                label=control.get("aria-label", "") or control.get("title", ""),
                autocomplete=control.get("autocomplete", ""),
            )
        )
    return tuple(fields)


# ----- recording -----


def record_form_fields(
    db: sqlite3.Connection,
    domain: str,
    fields: Iterable[FormField],
) -> RecordResult:
    """Record mappings for one manually submitted form. Values are never stored.

    Called after the human has filled and submitted the form themselves. A field
    that trips the safety detector is refused and logged; nothing about it is
    written, so the next visit re-detects it and leaves it to the human again —
    which is what "permanently" means here.
    """

    recorded: list[FormMapping] = []
    refused: list[tuple[str, str]] = []
    skipped: list[str] = []

    for field in fields:
        category = refusal_category(field)
        if category is not None:
            log.warning(
                "refused to map %s field %r on %s: this class of field is never "
                "recorded and is left to the human",
                category,
                field.selector,
                domain,
            )
            refused.append((field.selector, category))
            continue
        profile_field = infer_profile_field(field)
        if profile_field is None:
            skipped.append(field.selector)
            continue
        recorded.append(
            put_mapping(
                db,
                domain=domain,
                selector=field.selector,
                profile_field=profile_field,
                label=field.label or None,
            )
        )

    db.commit()
    log.info(
        "learned %d mapping(s) on %s (%d refused, %d unrecognised)",
        len(recorded),
        domain,
        len(refused),
        len(skipped),
    )
    return RecordResult(domain, tuple(recorded), tuple(refused), tuple(skipped))


def put_mapping(
    db: sqlite3.Connection,
    *,
    domain: str,
    selector: str,
    profile_field: str,
    label: str | None = None,
) -> FormMapping:
    """Write one mapping. Rejects a profile_field outside the closed enum."""

    if profile_field not in PROFILE_FIELDS:
        raise FormLearningError(
            f"unknown profile_field {profile_field!r}; "
            f"allowed: {', '.join(sorted(PROFILE_FIELDS))}"
        )
    db.execute(
        "INSERT INTO form_mappings (domain, selector, label, profile_field) "
        "VALUES (?, ?, ?, ?) "
        "ON CONFLICT (domain, selector) DO UPDATE SET "
        "  label = excluded.label, profile_field = excluded.profile_field",
        (domain, selector, label, profile_field),
    )
    return FormMapping(domain, selector, profile_field, label)


def mappings_for(db: sqlite3.Connection, domain: str) -> tuple[FormMapping, ...]:
    rows = db.execute(
        "SELECT domain, selector, profile_field, label, uses FROM form_mappings "
        "WHERE domain = ? ORDER BY id",
        (domain,),
    ).fetchall()
    return tuple(
        FormMapping(
            row["domain"],
            row["selector"],
            row["profile_field"],
            row["label"],
            int(row["uses"]),
        )
        for row in rows
    )


def mapping_is_complete(db: sqlite3.Connection, domain: str) -> bool:
    """Whether ``domain`` has enough of a mapping to be worth calling a route."""

    have = {mapping.profile_field for mapping in mappings_for(db, domain)}
    return all(field in have for field in REQUIRED_PROFILE_FIELDS)


def discard_mapping(db: sqlite3.Connection, domain: str, selector: str) -> None:
    """Drop a mapping whose selector no longer matches. Logged, never guessed."""

    db.execute(
        "DELETE FROM form_mappings WHERE domain = ? AND selector = ?",
        (domain, selector),
    )
    log.warning(
        "discarded stale mapping %s on %s: the selector no longer matches the page",
        selector,
        domain,
    )


# ----- using what was learned -----


@dataclass(frozen=True, slots=True)
class PrefillOutcome:
    """What a learned prefill produced, and what it threw away doing so."""

    fills: tuple[tuple[str, str], ...] = ()  # (selector, value)
    discarded: tuple[str, ...] = ()
    submit_enabled: bool = False

    @property
    def usable(self) -> bool:
        return bool(self.fills)


def _profile_values(
    applicant: ApplicantProfile,
    cv_path: str | None,
    letter_path: str | None,
) -> dict[str, str]:
    return {
        "full_name": applicant.full_name,
        "first_name": applicant.first_name,
        "last_name": applicant.last_name,
        "email": applicant.email,
        "phone": applicant.phone,
        "linkedin_url": applicant.linkedin_url,
        "cv_path": cv_path or "",
        "letter_path": letter_path or "",
    }


def build_prefill(
    db: sqlite3.Connection,
    domain: str,
    html: str,
    applicant: ApplicantProfile,
    *,
    cv_path: str | None = None,
    letter_path: str | None = None,
) -> PrefillOutcome:
    """Resolve stored mappings against the page as it is now.

    Every mapping whose selector no longer matches is discarded here, with a
    log. If that empties the mapping, the caller falls back to ``manual_open``,
    which is correct behaviour rather than a bug.
    """

    values = _profile_values(applicant, cv_path, letter_path)
    fills: list[tuple[str, str]] = []
    discarded: list[str] = []

    for mapping in mappings_for(db, domain):
        if not selector_matches_html(html, mapping.selector):
            discard_mapping(db, domain, mapping.selector)
            discarded.append(mapping.selector)
            continue
        value = values.get(mapping.profile_field, "")
        if not value:
            continue
        fills.append((mapping.selector, value))
        db.execute(
            "UPDATE form_mappings SET uses = uses + 1, last_used_at = ? "
            "WHERE domain = ? AND selector = ?",
            (_utc_now(), domain, mapping.selector),
        )

    db.commit()
    return PrefillOutcome(
        fills=tuple(fills),
        discarded=tuple(discarded),
        submit_enabled=submit_enabled(db, domain),
    )


# ----- the per-domain submit gate -----


def submit_enabled(db: sqlite3.Connection, domain: str) -> bool:
    """Whether pressing submit is allowed on this domain. Default: no.

    Prefill is automatic; pressing submit is not. Flipping this is a separate
    decision with its own evidence, per domain, never globally.
    """

    row = db.execute(
        "SELECT submit_enabled FROM form_domains WHERE domain = ?", (domain,)
    ).fetchone()
    return bool(row and row["submit_enabled"])


def set_submit_enabled(db: sqlite3.Connection, domain: str, enabled: bool) -> None:
    """Flip the per-domain submit gate. Deliberately has no global counterpart."""

    db.execute(
        "INSERT INTO form_domains (domain, submit_enabled) VALUES (?, ?) "
        "ON CONFLICT (domain) DO UPDATE SET submit_enabled = excluded.submit_enabled",
        (domain, int(enabled)),
    )
    db.commit()
    log.warning("submit gate for %s set to %s", domain, enabled)


def refused_categories(fields: Sequence[FormField]) -> tuple[str, ...]:
    """Every refusal category present in a form, for reporting to the human."""

    categories = {
        category
        for category in (refusal_category(field) for field in fields)
        if category is not None
    }
    return tuple(sorted(categories))
