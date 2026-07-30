"""Three tiers of token, so a category word is not judged like a claim.

A sourced bullet mixes things that are wrong in very different ways. « 1 500 »
is a measurement of one job; « Concentrix » says whose job it was; « Wazuh »
says what the candidate can do; « SIEM » says only which corner of the industry
is being discussed. Treating all four as "must appear in the cited fact" is what
made the validator reject « supervision SIEM »: the facts name products, not
categories, so no fact contains the word at all.

This module owns the vocabulary of the model — the tiers, the wording of a
rejection, and the terms that assert nothing — so that the wording of an error
written months ago can still be read back and classified.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

import yaml

from jobpilot.config import PROJECT_ROOT

DEFAULT_VOCABULARY_PATH = PROJECT_ROOT / "config" / "generic_vocabulary.yaml"


class GenericVocabularyError(ValueError):
    """Raised when the committed generic vocabulary is malformed."""


class TokenTier(StrEnum):
    """How much a token has to be backed up before it may be written."""

    #: Must appear in the facts the bullet cites. Quantities and the names of
    #: employers, clients and schools: getting these wrong is a lie about
    #: results or about whose results they were.
    ATTRIBUTION = "attribution"
    #: Must appear somewhere in the verified bank. Products, tools, standards
    #: and certifications: a claim about what the candidate can do, which the
    #: bank as a whole answers, not one fact.
    CAPABILITY = "capability"
    #: Freely allowed. Category words and industry acronyms that assert nothing
    #: about the candidate.
    VOCABULARY = "vocabulary"


#: Each kind of refused token and the tier that refused it. This mapping is the
#: only place the two are tied together, so ``jobpilot vocab-misses`` can read a
#: tier back out of a message stored in the events table.
_KIND_TIERS: Mapping[str, TokenTier] = {
    "number": TokenTier.ATTRIBUTION,
    "organisation": TokenTier.ATTRIBUTION,
    "designation": TokenTier.CAPABILITY,
    "capability": TokenTier.CAPABILITY,
}

#: Wordings retired by the tier model, kept readable because the events table
#: outlives the code that wrote it. Both refused named things for a reason the
#: capability tier now owns, so that is where their history belongs. Read-only:
#: nothing may write these again, which is why they are not in _KIND_TIERS.
_LEGACY_KIND_TIERS: Mapping[str, TokenTier] = {
    "proper noun": TokenTier.CAPABILITY,
    "tool or skill": TokenTier.CAPABILITY,
}

#: Every wording a stored message may carry. Longest kind first, so "tool or
#: skill" is not shadowed by a shorter alternative that prefix-matches it.
_READABLE_KIND_TIERS: Mapping[str, TokenTier] = {**_KIND_TIERS, **_LEGACY_KIND_TIERS}

#: The scope a refusal blames. "in sourced content" is the pre-entry wording,
#: still read because the events table outlives the code that wrote it.
_SCOPE_RE = r"(?:in sourced content|for (?:entry '(?P<entry>[^']+)'|the whole bank))"

_REJECTION_RE = re.compile(
    r"unsupported (?P<kind>"
    + "|".join(sorted(_READABLE_KIND_TIERS, key=len, reverse=True))
    + r") '(?P<token>[^']+)' "
    + _SCOPE_RE
)


@dataclass(frozen=True, slots=True)
class TokenRejection:
    """One token a validator refused, why, and what it was judged against."""

    tier: TokenTier
    kind: str
    token: str
    #: The entry that could not support the token, or None for the whole bank
    #: (and for messages written before scopes were recorded).
    entry: str | None = None


def rejection_message(kind: str, token: str, *, entry: str | None = None) -> str:
    """The one wording for a refused token; every caller goes through here.

    Naming the scope makes a rejection self-explanatory: "unsupported number
    '93' for entry 'Concentrix'" says which claim was not supported and where,
    which is what a reader needs in order to fix it.
    """

    if kind not in _KIND_TIERS:
        raise KeyError(f"unknown rejection kind: {kind}")
    where = f"entry '{entry}'" if entry else "the whole bank"
    return f"unsupported {kind} '{token}' for {where}"


def tier_of(kind: str) -> TokenTier:
    """The tier that refused a token, current wordings and retired ones alike."""

    return _READABLE_KIND_TIERS[kind]


def parse_rejections(messages: Iterable[str]) -> tuple[TokenRejection, ...]:
    """Recover the refused tokens from stored validator messages.

    The events table keeps error strings, not structures, so this reads them
    back. Anything that does not match is simply not a token rejection.
    """

    found: list[TokenRejection] = []
    for message in messages:
        for match in _REJECTION_RE.finditer(message or ""):
            kind = match.group("kind")
            found.append(
                TokenRejection(
                    tier=_READABLE_KIND_TIERS[kind],
                    kind=kind,
                    token=match.group("token"),
                    entry=match.group("entry"),
                )
            )
    return tuple(found)


#: A term that is only digits and punctuation would be a quantity, and tier 1
#: must never be reachable through tier 3. Refused at load time, not at use.
_QUANTITY_ONLY_RE = re.compile(r"^[\d\s.,%+/-]+$")


def load_generic_vocabulary(path: Path | None = None) -> frozenset[str]:
    """Load the terms that assert nothing about the candidate.

    Kept in config rather than in code so that a category word the validator has
    not met yet is a two-minute edit informed by ``jobpilot vocab-misses``,
    instead of a release. Nothing here is ever sourced from an offer: offer text
    is untrusted, and a posting must not be able to license a claim.
    """

    chosen = Path(path or DEFAULT_VOCABULARY_PATH)
    try:
        raw = yaml.safe_load(chosen.read_text(encoding="utf-8"))
    except OSError as exc:
        raise GenericVocabularyError(
            f"could not read generic vocabulary: {chosen}"
        ) from exc
    except yaml.YAMLError as exc:
        raise GenericVocabularyError(
            f"generic vocabulary is invalid YAML: {exc}"
        ) from exc
    if not isinstance(raw, dict):
        raise GenericVocabularyError("generic_vocabulary must be an object")
    version = raw.get("version")
    if not isinstance(version, int) or version < 1:
        raise GenericVocabularyError(
            "generic_vocabulary.version must be a positive integer"
        )
    terms = raw.get("terms")
    if not isinstance(terms, list) or not terms:
        raise GenericVocabularyError("generic_vocabulary.terms must be a non-empty list")
    collected: set[str] = set()
    for index, term in enumerate(terms):
        if not isinstance(term, str) or not term.strip():
            raise GenericVocabularyError(
                f"generic_vocabulary.terms[{index}] must be a non-empty string"
            )
        cleaned = term.strip()
        if _QUANTITY_ONLY_RE.match(cleaned):
            raise GenericVocabularyError(
                f"generic_vocabulary.terms[{index}] is a quantity, not vocabulary: "
                f"{cleaned!r}"
            )
        collected.add(cleaned)
    return frozenset(collected)
