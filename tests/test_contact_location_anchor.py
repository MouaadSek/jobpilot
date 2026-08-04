"""Task 41: the header location is found by its own marker, not by its neighbours.

_CONTACT_LOCATION_RE used to anchor on the pin emoji before the location and on
the separator after it:

    (?:&#x1F4CD;|📍)\\s*(.*?)\\s*(?:&nbsp;\\|&nbsp;|<br\\s*/?>)

Both ends were an enumeration of the encodings the 21 templates happen to use —
two for the emoji, because half the templates are entity-encoded, and two for
the separator, because one template ends the contact line with <br/>. Task 40's
inventory filed it as Class C for that reason: the same shape as the profile
domain anchor, which was an enumeration of neighbouring prose and broke every
stage generation once one of its alternatives stopped existing.

Three sites read it and two of them read tailored output, where the encoding is
whatever the previous step wrote. The fix is the same as Task 40's: a marker we
emit ourselves, in all 21 templates, matched in one place.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from jobpilot.facts import load_fact_bank
from jobpilot.tailoring import (
    _CONTACT_LOCATION_RE,
    OfferContext,
    TailoringPlan,
    _plain,
    _validate_header_location,
    extract_template_context,
    tailor_cv_html,
    variant_for_slug,
)
from tests.test_tailoring_retry import _payload

TEMPLATES = sorted(
    (Path(__file__).resolve().parents[1] / "skill" / "assets" / "cv-templates").glob(
        "*.html"
    )
)

#: What the old pattern enumerated. Kept here as the thing the marker replaced,
#: so a template re-exported into a fifth encoding is no longer this test's
#: problem — or the tailorer's.
_OLD_ANCHOR = re.compile(
    r"(?:&#x1F4CD;|\U0001F4CD)\s*(.*?)\s*(?:&nbsp;\|&nbsp;|<br\s*/?>)"
)


def _plan(selection, city: str = "Paris"):
    """The header location is renderer-owned: it comes from the offer's city."""

    offer = OfferContext(
        title="Analyste SOC",
        company="Acme",
        description="SIEM dès septembre 2026",
        contract_type="alternance",
        duration_months=12,
        city=city,
        url="https://example.test/jobs/41",
        source="france_travail",
    )
    plan = TailoringPlan.from_mapping(_payload(), offer=offer, selection=selection)
    return offer, plan


def test_every_template_carries_the_marker_exactly_once() -> None:
    assert TEMPLATES, "no templates found"

    for path in TEMPLATES:
        source = path.read_text(encoding="utf-8")
        assert len(_CONTACT_LOCATION_RE.findall(source)) == 1, path.name


@pytest.mark.parametrize("path", TEMPLATES, ids=lambda p: p.stem[:28])
def test_every_template_still_extracts_its_location(path: Path) -> None:
    context = extract_template_context(path.read_text(encoding="utf-8"))

    assert context.location_region == "Lille / Île-de-France"


def test_the_templates_really_do_disagree_on_both_encodings() -> None:
    """The premise of the fix, asserted rather than assumed.

    If this ever fails the old anchor was not actually a list of four shapes and
    the reasoning above needs re-reading — it does not make the marker wrong,
    but it stops being self-evidently right.
    """

    shapes = set()
    for path in TEMPLATES:
        line = next(
            line
            for line in path.read_text(encoding="utf-8").splitlines()
            if "contact-location" in line
        )
        emoji = "entity" if "&#x1F4CD;" in line else "literal"
        separator = "br" if re.search(r"<br\s*/?>", line) else "pipe"
        shapes.add((emoji, separator))

    assert len(shapes) > 1


def test_extraction_survives_a_contact_line_in_neither_encoding() -> None:
    """A template re-exported with a plain pin and a different separator.

    Under the old anchor this raised "template contact location not found" —
    the failure mode Task 40 saw on the profile domain, one field over.
    """

    source = (TEMPLATES[0].parent / "Mouaad_Sekkouri_-_SOC__Alternance.html").read_text(
        encoding="utf-8"
    )
    mutated = source.replace(
        "&#x1F4CD; <span", "&#128205; <span"
    ).replace('contact-location">Lille / Île-de-France</span> &nbsp;|&nbsp;',
              'contact-location">Lille / Île-de-France</span> &#183;')

    assert _OLD_ANCHOR.search(mutated) is None  # the old pattern is now blind
    assert extract_template_context(mutated).location_region == "Lille / Île-de-France"


def test_the_tailored_cv_keeps_exactly_one_marker_carrying_the_new_location() -> None:
    """The rewrite site and the two read sites agree, on real tailored output."""

    selection = variant_for_slug("soc", contract_type="alternance")
    original = (TEMPLATES[0].parent / selection.template_name).read_text(
        encoding="utf-8"
    )
    offer, plan = _plan(selection)
    assert plan.location_region == "Île-de-France"

    tailored = tailor_cv_html(
        original,
        plan,
        selection,
        offer_description=offer.description,
        fact_bank=load_fact_bank(),
        offer=offer,
    )

    assert len(_CONTACT_LOCATION_RE.findall(tailored)) == 1
    assert extract_template_context(tailored).location_region == "Île-de-France"
    _validate_header_location(tailored)  # the gate reads the same marker


def test_the_marker_adds_no_visible_text() -> None:
    """The header is a fixed-width line; the span must not consume any of it."""

    source = (TEMPLATES[0].parent / "Mouaad_Sekkouri_-_SOC__Alternance.html").read_text(
        encoding="utf-8"
    )
    contact = source.split('<div class="contact-info">')[1].split("</div>")[0]

    assert "contact-location" not in _plain(contact)
