"""Task 44 item 1: no rendered CV may carry a bracketed placeholder.

« Stage de [offer duration] mois dès [offer start date] » reached two PDFs. The
root cause is fixed by making that line renderer-owned
(tests/test_stage_contract_phrase.py), but the class of bug is wider than one
field: any instruction that names a placeholder can be obeyed literally, and
every existing gate reads *meaning* — provenance, word counts, layout — while a
placeholder is wrong in its punctuation.

Fatal, which is the rarer half of Task 39's rule. A placeholder in a PDF is
unusable and advertises that nobody read the document, and there is no
degradation available: the renderer cannot know what the bracket stood for.
"""

from __future__ import annotations

import pytest

from jobpilot.tailoring import (
    TailoringError,
    Tier,
    _reject_placeholders,
)

CLEAN = '<div class="job-title">Analyste SOC - Alternance M2 dès Septembre 2026</div>'


def test_a_clean_document_passes() -> None:
    _reject_placeholders(CLEAN)


@pytest.mark.parametrize(
    "placeholder",
    (
        "[offer duration]",
        "[offer start date]",
        "[company]",
        "[à compléter]",
    ),
)
def test_a_placeholder_anywhere_in_the_document_is_refused(placeholder) -> None:
    source = f'<p class="profile">Stage de {placeholder} mois.</p>'

    with pytest.raises(TailoringError) as excinfo:
        _reject_placeholders(source)

    assert placeholder in str(excinfo.value)


def test_the_exact_string_that_shipped_is_refused() -> None:
    """The regression, quoted from application 37's rendered CV."""

    source = (
        '<div class="profile-contract">Stage de [offer duration] mois '
        "dès [offer start date]</div>"
    )

    with pytest.raises(TailoringError):
        _reject_placeholders(source)


def test_the_gate_is_fatal_and_names_itself() -> None:
    """Tier is the whole decision here: recoverable would mean retrying, and
    the model has nothing better to offer for a field it should not be writing."""

    with pytest.raises(TailoringError) as excinfo:
        _reject_placeholders("<p>[offer duration]</p>")

    assert excinfo.value.gate == "_reject_placeholders"
    assert excinfo.value.tier is Tier.FATAL


def test_an_entity_encoded_bracket_is_caught_too() -> None:
    """Half the templates are entity-encoded, so the scan reads decoded text.
    A placeholder that survived encoding would otherwise be invisible to it."""

    with pytest.raises(TailoringError):
        _reject_placeholders("<p>Stage de &#91;offer duration&#93; mois</p>")


def test_a_css_attribute_selector_is_not_a_placeholder() -> None:
    """No template carries one today. This is about a future stylesheet edit
    not failing a generation over text that never reaches the page."""

    source = (
        "<style>input[type=\"text\"] { color: red; } a[href] { color: blue; }</style>"
        f"{CLEAN}"
    )

    _reject_placeholders(source)


def test_brackets_far_apart_do_not_pair_into_a_false_positive() -> None:
    """The match is bounded, so an unmatched '[' cannot reach across the page
    to find an unrelated ']' and fail a document that is fine."""

    source = "<p>[</p>" + "<p>texte ordinaire</p>" * 40 + "<p>]</p>"

    _reject_placeholders(source)


def test_every_shipped_template_passes_the_guard() -> None:
    """If a hand-written template carried brackets, the guard would abort every
    generation using it. All 21 are checked rather than assumed."""

    from pathlib import Path

    templates = sorted(
        (Path(__file__).resolve().parents[1] / "skill" / "assets" / "cv-templates")
        .glob("*.html")
    )
    assert templates, "no CV templates found"

    for path in templates:
        _reject_placeholders(path.read_text(encoding="utf-8"))
