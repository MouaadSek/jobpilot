"""An experience claim has to fit the CV's one line.

The renderer inserts a selected fact verbatim, so a claim that is too long does
not fail anywhere: it silently wraps to a second line and pushes the CV toward a
second page. Nine of the eleven experience.baifall.* claims are 132-167
characters against a budget of 129.

The budget is not a magic number. It is read off the template, the way Task 32
read zone 3's row budget off the template's own widest tech row: the CV was
line-fit by hand, so what it already accepts is the honest bound.

One wrinkle forces the exclusion below. The template's own Baifall <li> rows ARE
those same over-long strings, pasted from skill/assets/stage-baifall-dream.md
rather than fitted like the rest of the CV. Letting them into the derivation
would make the budget whatever the worst claim happens to be, which is no bound
at all. Every other employer's rows were fitted by hand, and those are the
reference.
"""

from __future__ import annotations

import re

from jobpilot.facts import load_fact_bank
from jobpilot.tailoring import _EXPERIENCE_RE, _plain
from tests.test_fact_id_resolution import TEMPLATE_PATH

TEMPLATE = TEMPLATE_PATH.read_text(encoding="utf-8")

#: The one employer whose template rows were imported rather than line-fit, so
#: they describe the defect instead of bounding it. Remove this once those rows
#: are rewritten to fit and the whole template is a valid reference again.
UNFITTED_EMPLOYER = "Baïfall Dream"
#: The widest row that WAS fitted, located independently of the derivation.
FITTED_WIDEST = "experience.testronic.detection.de.90.anomalies.critiques"

_BULLET_RE = re.compile(r"<li>(.*?)</li>", re.DOTALL)
_COMPANY_RE = re.compile(r'<span class="company-name">(.*?)</span>', re.DOTALL)


def _template_bullets(source: str) -> list[tuple[str, str]]:
    """Every experience bullet the template ships, as (employer, plain text).

    Entities are resolved before comparing: the templates write the employer as
    both "Baïfall Dream" and "Ba&iuml;fall Dream".
    """

    bullets: list[tuple[str, str]] = []
    for block in _EXPERIENCE_RE.finditer(source):
        company = _COMPANY_RE.search(block.group(0))
        employer = _plain(company.group(1)).split(" - ")[0] if company else ""
        bullets.extend(
            (employer, _plain(bullet)) for bullet in _BULLET_RE.findall(block.group(0))
        )
    return bullets


def _bullet_budget(source: str) -> int:
    """The longest experience bullet the template itself already renders on one line."""

    return max(
        len(text)
        for employer, text in _template_bullets(source)
        if employer != UNFITTED_EMPLOYER
    )


def _claim_length(text: str) -> int:
    return len(" ".join(text.split()))


def test_the_budget_is_the_templates_own_widest_fitted_row() -> None:
    """Derived from the file, not a magic number."""

    claim = load_fact_bank().claims[FITTED_WIDEST]

    assert _bullet_budget(TEMPLATE) == _claim_length(claim.text)


def test_the_excluded_employer_is_still_the_one_in_the_template() -> None:
    """Without this the constant could go stale and quietly widen the budget."""

    employers = {employer for employer, _text in _template_bullets(TEMPLATE)}

    assert UNFITTED_EMPLOYER in employers
    assert employers - {UNFITTED_EMPLOYER}


def test_no_experience_claim_exceeds_the_one_line_budget() -> None:
    """The renderer inserts these verbatim, so a long one wraps in silence."""

    budget = _bullet_budget(TEMPLATE)
    bank = load_fact_bank()

    overlong = sorted(
        (_claim_length(fact.text), fact.id)
        for entry in bank.experience
        for fact in entry.facts
        if _claim_length(fact.text) > budget
    )

    assert not overlong, (
        f"experience claims over the {budget}-character one-line budget: "
        + ", ".join(f"{fact_id} ({length})" for length, fact_id in reversed(overlong))
    )


# ----- projects: the same question, a different answer -----
#
# Task 40 amendment 2 asked for a project-desc budget derived the same way, on
# the premise that the templates' project-desc rows are 29-66 characters while
# every bank claim is 130-134, so all 63 overflow. Measured, that premise does
# not hold: the 63 project-desc rows across the 21 templates are themselves
# 130-134, distributed exactly as the claims are, and the 55 distinct row
# strings ARE the 55 distinct claims. Nothing overflows.
#
# Which also means the requested derivation cannot work here. For experience
# there was a fitted subset to derive from once the imported Baifall rows were
# excluded; for projects there is no such subset, because every row in every
# template is a bank claim. A "widest project-desc row" ceiling is the worst
# claim measuring itself.
#
# So the ceiling below is kept, but the load-bearing guard is the one under it:
# the templates and the bank must not drift apart. That is what would actually
# break if a claim were lengthened without the layout following it.

_PROJECT_DESC_RE = re.compile(r'<div class="project-desc">(.*?)</div>', re.DOTALL)


def _project_desc_rows(source: str) -> list[str]:
    return [_plain(row) for row in _PROJECT_DESC_RE.findall(source)]


def _all_template_paths():
    return sorted(TEMPLATE_PATH.parent.glob("*.html"))


def _project_desc_budget() -> int:
    """The widest project description any template already renders."""

    return max(
        len(row)
        for path in _all_template_paths()
        for row in _project_desc_rows(path.read_text(encoding="utf-8"))
    )


def test_no_project_claim_exceeds_the_widest_shipped_project_row() -> None:
    budget = _project_desc_budget()
    bank = load_fact_bank()

    overlong = sorted(
        (_claim_length(fact.text), fact.id)
        for project in bank.projects
        for fact in project.facts
        if _claim_length(fact.text) > budget
    )

    assert not overlong, (
        f"project claims over the {budget}-character row: "
        + ", ".join(f"{fact_id} ({length})" for length, fact_id in reversed(overlong))
    )


def test_the_templates_and_the_bank_do_not_drift_apart() -> None:
    """The guard that has teeth.

    Every project description a template ships must be a claim the bank holds,
    and every claim must be one a template ships. Lengthening a claim without
    updating the layout — the failure amendment 2 was aimed at — breaks this,
    where a self-referential budget would not notice.
    """

    bank = load_fact_bank()
    claims = {_normalized(fact.text) for project in bank.projects for fact in project.facts}
    rows = {
        _normalized(row)
        for path in _all_template_paths()
        for row in _project_desc_rows(path.read_text(encoding="utf-8"))
    }

    assert rows - claims == set(), "template rows that no bank claim provides"
    assert claims - rows == set(), "bank claims no template renders"


def _normalized(value: str) -> str:
    return " ".join(value.split())
