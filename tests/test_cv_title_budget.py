"""Task 44 item 2: the CV title has a layout budget.

« Ingénieur en data - Optimisation d'une base de données et suivi d'incidents
cyber - Stage dès septembre 2026 » is 108 characters against a row that accepts
70, and it rendered on three lines. Nothing budgeted it: Task 38 gave the title
to the renderer and Task 40 gave bullets and project descriptions their
budgets, but the title itself was built from the offer and never measured.

The bound comes from the templates the way _row_budget's does — the widest line
their designer accepted — pooled across all 21 because each contributes exactly
one title and one sample of a row's capacity is not the capacity.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

import pytest

from jobpilot.facts import build_cv_title
from jobpilot.tailoring import (
    _CV_TITLE_BUDGET,
    OfferContext,
    TemplateContext,
    _fit_cv_title,
    extract_template_context,
    variant_for_slug,
)

TEMPLATES = Path(__file__).resolve().parents[1] / "skill" / "assets" / "cv-templates"

#: The offer behind the bug, as stored.
COMCYBER_TITLE = (
    "Ingénieur en data - Optimisation d'une base de données et suivi "
    "d'incidents cyber"
)


def _template_titles() -> list[str]:
    titles = []
    for path in sorted(TEMPLATES.glob("*.html")):
        match = re.search(
            r'<div class="job-title">(.*?)</div>',
            path.read_text(encoding="utf-8"),
            re.DOTALL,
        )
        assert match, path.name
        titles.append(html.unescape(re.sub(r"<[^>]+>", "", match.group(1))).strip())
    return titles


def _offer(title: str, *, duration: int | None = None, description: str = "dès septembre 2026"):
    return OfferContext(
        title=title,
        company="Acme",
        description=description,
        contract_type="stage",
        duration_months=duration,
        city="Paris",
        url="https://example.test/jobs/44",
        source="france_travail",
    )


def _template(name: str = "*Cybersecurite__Alternance.html") -> TemplateContext:
    path = next(TEMPLATES.glob(name))
    return extract_template_context(path.read_text(encoding="utf-8"))


def _fit(title: str, *, contract: str = "stage", duration: int | None = None):
    selection = variant_for_slug("soc", contract_type=contract)
    return _fit_cv_title(
        _offer(title, duration=duration), selection=selection, template=_template()
    )


# ---- the budget is the templates' own, not a number someone liked ----


def test_the_budget_is_the_widest_title_the_templates_already_carry() -> None:
    """Pinned to the files so the constant cannot drift away from the layout."""

    assert _CV_TITLE_BUDGET == max(len(title) for title in _template_titles())


def test_every_template_renders_its_title_at_the_same_size() -> None:
    """Pooling 21 titles into one budget is only sound if they are 21 samples
    of the same row. A template that restyled its header would break that and
    is worth failing over."""

    sizes = set()
    for path in sorted(TEMPLATES.glob("*.html")):
        block = re.search(
            r"\.job-title\s*\{([^}]*)\}", path.read_text(encoding="utf-8")
        )
        assert block, path.name
        size = re.search(r"font-size:\s*([\d.]+)pt", block.group(1))
        assert size, path.name
        sizes.add(size.group(1))

    assert len(sizes) == 1, f"job-title font sizes differ across templates: {sizes}"


def test_no_shipped_template_title_exceeds_the_budget() -> None:
    for title in _template_titles():
        assert len(title) <= _CV_TITLE_BUDGET, title


# ---- the three steps ----


def test_a_title_that_fits_is_used_unchanged() -> None:
    fitted, reason = _fit("Analyste SOC")

    assert fitted == "Analyste SOC - Stage dès septembre 2026"
    assert reason is None


def test_the_overflowing_title_is_cut_back_to_its_role() -> None:
    """The bug, and the reason step 2 exists at all: the head of that title is
    a perfectly good CV title and the rest is a subtitle."""

    fitted, reason = _fit(COMCYBER_TITLE)

    assert fitted == "Ingénieur en data - Stage dès septembre 2026"
    assert len(fitted) <= _CV_TITLE_BUDGET
    # Not a degradation: the role survived, only the subtitle went.
    assert reason is None


@pytest.mark.parametrize(
    "junk_head",
    (
        "6mois - Chargé·e de création de contenus et gestion des réseaux sociaux "
        "pour l'émission Destination Francophonie",
        "école - Chargé de communication et de la gestion des réseaux sociaux "
        "pour une marque de prêt-à-porter",
        "Alternant - Chargé de développement commercial et marketing digital "
        "pour une jeune entreprise en croissance",
    ),
)
def test_a_title_leading_with_noise_is_not_cut_back_to_the_noise(junk_head) -> None:
    """Cutting keeps the head clause, which is the role only when the posting
    is well formed. « 6mois - Stage dès septembre 2026 » is the same class of
    bug as the placeholder — a machine-assembled string nobody would write."""

    fitted, reason = _fit(junk_head)

    assert not fitted.startswith(("6mois", "école", "Alternant -"))
    assert len(fitted) <= _CV_TITLE_BUDGET
    # It took the template's role instead, so it is reported.
    assert reason is not None


def test_a_substantial_role_is_still_cut_back_rather_than_replaced() -> None:
    """The floor must not swallow the case step 2 exists for."""

    fitted, reason = _fit(COMCYBER_TITLE)

    assert fitted.startswith("Ingénieur en data")
    assert reason is None


def test_an_unsplittable_overlong_title_falls_back_to_the_template() -> None:
    monster = "Responsable " + "de la coordination opérationnelle " * 4

    fitted, reason = _fit(monster)

    assert len(fitted) <= _CV_TITLE_BUDGET
    assert reason is not None
    assert "does not fit" in reason


def test_the_fallback_states_this_offers_contract_not_the_templates() -> None:
    """The template's own title ends 'Alternance M2 dès Septembre 2026'. Reused
    verbatim on a stage CV that is a false statement about the application, so
    the fallback rebuilds from the template's role instead."""

    monster = "Responsable " + "de la coordination opérationnelle " * 4

    fitted, _ = _fit(monster, contract="stage")

    assert "Alternance" not in fitted
    assert "Stage" in fitted


def test_the_fallback_keeps_the_templates_own_role() -> None:
    monster = "Responsable " + "de la coordination opérationnelle " * 4
    template = _template()

    fitted, _ = _fit(monster)

    assert fitted.startswith(template.job_title.rsplit(" - ", 1)[0])


@pytest.mark.parametrize("contract,duration", (("stage", None), ("stage", 6), ("alternance", None)))
def test_every_templates_fallback_fits_the_budget(contract, duration) -> None:
    """Step 3 is the floor, so it must never itself overflow — otherwise the
    degradation reintroduces the bug it exists to avoid."""

    for title in _template_titles():
        built = build_cv_title(
            title.rsplit(" - ", 1)[0],
            contract_type=contract,
            duration_months=duration,
            start_date="septembre 2026",
        )
        assert len(built) <= _CV_TITLE_BUDGET, built


def test_the_result_is_within_budget_for_every_stored_title_shape() -> None:
    """Shapes taken from real stored offers, including the ones that made the
    normaliser raise on a clause ('6mois - ...', 'H/F')."""

    shapes = (
        COMCYBER_TITLE,
        "Apprenti Développement et configuration dans un outil de Gestion "
        "électronique des documents (GED) et d’automatisation de processus",
        "Consultant.e Stagiaire de fin d'études et césure - Management & "
        "Stratégie - Protection Sociale : Santé, Retraite, Emploi",
        "6mois - Chargé·e de création de contenus et gestion des réseaux "
        "sociaux pour l'émission Destination Francophonie",
        "Développeur Full Stack, pour contribuer à faire accélérer les projets "
        "à impact positif !",
        "Stagiaire Développeur d'Application & Assurance Qualité [QA] H/F",
        "Analyste SOC",
    )

    for shape in shapes:
        fitted, _ = _fit(shape)
        assert len(fitted) <= _CV_TITLE_BUDGET, (shape, fitted, len(fitted))
        assert fitted.strip(), shape


def test_a_bracketed_tag_in_the_title_never_reaches_the_result() -> None:
    """Item 1's guard is fatal over the rendered CV, so a title that kept a
    posting's '[QA]' tag would abort the generation."""

    fitted, _ = _fit("Stagiaire Développeur d'Application & Assurance Qualité [QA] H/F")

    assert "[" not in fitted and "]" not in fitted


# ---- end to end ----


def test_a_long_title_warns_and_still_generates(db, tmp_path) -> None:
    """Recoverable, not fatal: a title that overflows is visible in two seconds
    and the document is otherwise fine, so it degrades and says so."""

    import hashlib

    from jobpilot.apply_flow import approve_application
    from jobpilot.generation_warnings import warnings_for
    from jobpilot.state import current_status
    from jobpilot.tailoring import TailoringPlan
    from tests.test_tailoring import _Toolchain
    from tests.test_tailoring_retry import _payload

    monster = "Responsable " + "de la coordination opérationnelle " * 4
    source_id = db.execute(
        "SELECT id FROM sources WHERE name = 'france_travail'"
    ).fetchone()["id"]
    company_id = db.execute("INSERT INTO companies (name) VALUES ('Acme')").lastrowid
    offer_id = db.execute(
        "INSERT INTO offers (source_id, company_id, external_id, url, title, "
        "description, contract_type, duration_months, city, content_hash) "
        "VALUES (?, ?, 'title-44', 'https://example.test/44', ?, "
        "'Analyser les alertes SIEM dès septembre 2026', "
        "'alternance', NULL, 'Paris', ?)",
        (source_id, company_id, monster, hashlib.sha256(b"title-44").hexdigest()),
    ).lastrowid
    application_id = db.execute(
        "INSERT INTO applications (offer_id, company_id, kind, status) "
        "VALUES (?, ?, 'offer', 'queued')",
        (offer_id, company_id),
    ).lastrowid
    db.commit()

    class _Advisor:
        accepts_correction = True

        def advise(self, offer, selection, template, *, correction=None):
            return TailoringPlan.from_mapping(
                _payload(), offer=offer, selection=selection
            )

    approve_application(
        db,
        application_id,
        via="test",
        advisor=_Advisor(),
        toolchain=_Toolchain(),
        output_root=tmp_path,
    )

    assert current_status(db, application_id) == "ready"
    assert "_fit_cv_title" in [w.gate for w in warnings_for(db, application_id)]

    cv = (tmp_path / str(application_id) / "tailored_cv.html").read_text(
        encoding="utf-8"
    )
    rendered = re.search(r'<div class="job-title">(.*?)</div>', cv, re.DOTALL)
    assert rendered
    assert len(html.unescape(rendered.group(1)).strip()) <= _CV_TITLE_BUDGET


def test_the_warning_is_recorded_once_not_once_per_retry(db, tmp_path) -> None:
    """The title is built from the offer, the selection and the template, none
    of which a retry changes — so a per-attempt computation would stack the
    same warning up as many times as the model was re-asked."""

    import hashlib

    from jobpilot.apply_flow import approve_application
    from jobpilot.generation_warnings import warnings_for
    from jobpilot.tailoring import TailoringError, TailoringPlan
    from tests.test_tailoring import _Toolchain
    from tests.test_tailoring_retry import _payload

    monster = "Responsable " + "de la coordination opérationnelle " * 4
    source_id = db.execute(
        "SELECT id FROM sources WHERE name = 'france_travail'"
    ).fetchone()["id"]
    company_id = db.execute("INSERT INTO companies (name) VALUES ('Acme')").lastrowid
    offer_id = db.execute(
        "INSERT INTO offers (source_id, company_id, external_id, url, title, "
        "description, contract_type, duration_months, city, content_hash) "
        "VALUES (?, ?, 'title-44b', 'https://example.test/44b', ?, "
        "'Analyser les alertes SIEM dès septembre 2026', "
        "'alternance', NULL, 'Paris', ?)",
        (source_id, company_id, monster, hashlib.sha256(b"title-44b").hexdigest()),
    ).lastrowid
    application_id = db.execute(
        "INSERT INTO applications (offer_id, company_id, kind, status) "
        "VALUES (?, ?, 'offer', 'queued')",
        (offer_id, company_id),
    ).lastrowid
    db.commit()

    class _FailsOnce:
        accepts_correction = True

        def __init__(self) -> None:
            self.calls = 0

        def advise(self, offer, selection, template, *, correction=None):
            self.calls += 1
            if self.calls == 1:
                raise TailoringError("profile domain phrase must contain 3 to 7 words")
            return TailoringPlan.from_mapping(
                _payload(), offer=offer, selection=selection
            )

    advisor = _FailsOnce()
    approve_application(
        db,
        application_id,
        via="test",
        advisor=advisor,
        toolchain=_Toolchain(),
        output_root=tmp_path,
    )

    assert advisor.calls > 1, "fixture must exercise a retry"
    gates = [w.gate for w in warnings_for(db, application_id)]
    assert gates.count("_fit_cv_title") == 1
