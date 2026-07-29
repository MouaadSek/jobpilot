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

_REJECTION_RE = re.compile(
    r"unsupported (?P<kind>" + "|".join(_KIND_TIERS) + r") "
    r"'(?P<token>[^']+)' in sourced content"
)


@dataclass(frozen=True, slots=True)
class TokenRejection:
    """One token a validator refused, and why."""

    tier: TokenTier
    kind: str
    token: str


def rejection_message(kind: str, token: str) -> str:
    """The one wording for a refused token; every caller goes through here."""

    if kind not in _KIND_TIERS:
        raise KeyError(f"unknown rejection kind: {kind}")
    return f"unsupported {kind} '{token}' in sourced content"


def tier_of(kind: str) -> TokenTier:
    return _KIND_TIERS[kind]


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
                    tier=_KIND_TIERS[kind],
                    kind=kind,
                    token=match.group("token"),
                )
            )
    return tuple(found)


#: Words that place a sentence in an industry without claiming anything in it.
#: Being on this list is not permission to claim a skill: « SIEM » says the
#: bullet is about log supervision, « Wazuh » says the candidate has run one.
GENERIC_VOCABULARY: frozenset[str] = frozenset(
    {
        # security operations
        "SIEM",
        "SOC",
        "SOAR",
        "EDR",
        "XDR",
        "NDR",
        "DLP",
        "IDS",
        "IPS",
        "WAF",
        "PKI",
        "MFA",
        "SSO",
        "RBAC",
        "IAM",
        "GRC",
        "CERT",
        "CSIRT",
        "threat intel",
        "phishing",
        "malware",
        "firewall",
        "pare-feu",
        "proxy",
        "endpoint",
        "logs",
        "journalisation",
        "supervision",
        "durcissement",
        "hardening",
        "pentest",
        "forensics",
        # networking and systems
        "VPN",
        "LAN",
        "WAN",
        "DMZ",
        "DNS",
        "DHCP",
        "TCP",
        "IP",
        "VLAN",
        "VM",
        "OS",
        "AD",
        "SI",
        "cloud",
        "on-premise",
        "datacenter",
        # engineering practice
        "API",
        "REST",
        "CI",
        "CD",
        "CI/CD",
        "QA",
        "SDLC",
        "SAST",
        "DAST",
        "IaC",
        "DevOps",
        "DevSecOps",
        "SRE",
        "MVP",
        "POC",
        "PoC",
        # governance and management
        "RGPD",
        "GDPR",
        "ITIL",
        "SLA",
        "SLO",
        "KPI",
        "KPIs",
        "ROI",
        "PDCA",
        "RSSI",
        "DSI",
        "PSSI",
        "PCA",
        "PRA",
        "MOA",
        "MOE",
        # contract and calendar words a French offer always uses
        "IT",
        "M1",
        "M2",
        "BTS",
        "DUT",
    }
)
