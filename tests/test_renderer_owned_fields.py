"""The guarantees that made four _validate_plan branches unreachable.

Task 39 item 1 found that `job_title` and `location_region` are renderer-owned:
`_advise_and_tailor` overwrites both with `build_cv_title` and
`resolve_header_location` before any validation runs, so the plan-level checks
on them could only ever have failed on our own output, never on the model's.
The same is true of the letter's em-dash check — every path that builds
`letter_body_html` runs `_canonicalize_prose` first.

Deleting a gate is only safe if the property it asserted still holds. These
tests pin each property where the value is actually produced, which is where a
future edit would break it.
"""

from __future__ import annotations

import pytest

from jobpilot.facts import build_cv_title
from jobpilot.profile import load_cv_profile
from jobpilot.tailoring import (
    _BARE_COUNTRIES,
    _canonicalize_prose,
    _normalize,
    resolve_header_location,
)

#: What _validate_plan used to accept. The renderer may only ever produce one of
#: these, so the check on the plan was dead weight.
ALLOWED_REGIONS = frozenset(
    _normalize(region)
    for region in (
        "Auvergne-Rhône-Alpes",
        "Bourgogne-Franche-Comté",
        "Bretagne",
        "Centre-Val de Loire",
        "Corse",
        "Grand Est",
        "Hauts-de-France",
        "Île-de-France",
        "Normandie",
        "Nouvelle-Aquitaine",
        "Occitanie",
        "Pays de la Loire",
        "Provence-Alpes-Côte d'Azur",
        "Guadeloupe",
        "Martinique",
        "Guyane",
        "La Réunion",
        "Mayotte",
        "Nord",
    )
)

_START_SIGNALS = (
    "janvier",
    "fevrier",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "aout",
    "septembre",
    "octobre",
    "novembre",
    "decembre",
)


@pytest.mark.parametrize("contract_type", ("alternance", "stage"))
@pytest.mark.parametrize(
    "raw_title",
    (
        "Analyste SOC (H/F)",
        "Ingénieure / Ingénieur Production - Alternance",
        "Analyste Cybersécurité SecOps F/H",
        # An empty raw title is refused by normalise_role_title before this
        # function can build anything, so it is not a title-content case.
    ),
)
def test_the_built_title_always_carries_its_contract_type(
    raw_title: str, contract_type: str
) -> None:
    title = _normalize(
        build_cv_title(raw_title, contract_type=contract_type, duration_months=6)
    )

    assert contract_type in title


@pytest.mark.parametrize("contract_type", ("alternance", "stage"))
def test_the_built_title_always_carries_a_start_date(contract_type: str) -> None:
    """_offer_start falls back to « septembre 2026 », so there is always one."""

    title = _normalize(build_cv_title("Analyste SOC", contract_type=contract_type))

    assert any(month in title for month in _START_SIGNALS)


@pytest.mark.parametrize(
    "city",
    ("Paris", "Lille", "Cergy", "Toulouse", "", "   ", "Bruxelles", "95000"),
)
def test_the_resolved_header_location_is_always_one_allowed_region(city: str) -> None:
    resolved = _normalize(resolve_header_location(city))

    assert resolved in ALLOWED_REGIONS
    assert resolved not in _BARE_COUNTRIES


def test_the_profiles_own_fallback_is_itself_an_allowed_region() -> None:
    """The one input to resolve_header_location that comes from config."""

    assert _normalize(load_cv_profile().header_location) in ALLOWED_REGIONS


@pytest.mark.parametrize("dash", ("—", "–"))
def test_prose_canonicalization_removes_every_dash_the_letter_gate_looked_for(
    dash: str,
) -> None:
    canonical = _canonicalize_prose(f"Une mission {dash} centrée sur le SOC {dash} ici.")

    assert dash not in canonical
    assert " - " in canonical
