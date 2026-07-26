"""Structural parsing of job-alert cards (Task 20).

Every fixture here is shaped after a value actually observed in the real
database, where positional field assignment had filled `offers.city` with
LinkedIn interface text and the hard filter rejected 85 of 112 alert offers on
location before scoring them.
"""

from __future__ import annotations

import sqlite3

import pytest

from jobpilot.models import REMOTE_POLICIES
from jobpilot.reparse import derive_fields, reparse_alerts
from jobpilot.sources.email_alerts import (
    is_noise,
    is_title_echo,
    parse_card_line,
    parse_linkedin,
    scrub_chunk,
    split_workplace,
)


def _card_html(anchor: str, *chunks: str, job_id: str = "3812345678") -> str:
    """One LinkedIn job card: the anchor plus its sibling context chunks."""
    divs = "".join(f"<div>{chunk}</div>" for chunk in chunks)
    return (
        "<html><body><table><tr><td>"
        f'<a href="https://www.linkedin.com/comm/jobs/view/{job_id}/?trk=eml">{anchor}</a>'
        f"{divs}"
        "</td></tr></table></body></html>"
    )


# ---- 20.1 the "Company · City (Workplace)" pattern ----


@pytest.mark.parametrize(
    ("line", "company", "city", "policy"),
    [
        # exact rows from the real offers table
        (
            "Dassault Systèmes · Vélizy-Villacoublay (Sur site)",
            "Dassault Systèmes",
            "Vélizy-Villacoublay",
            "onsite",
        ),
        ("AEROCONTACT.COM · Bourges", "AEROCONTACT.COM", "Bourges", None),
        ("Viveris · Massy (Hybride)", "Viveris", "Massy", "hybrid"),
        (
            "Viveris · Le Plessis-Robinson (Sur site)",
            "Viveris",
            "Le Plessis-Robinson",
            "onsite",
        ),
        ("Thales · Lambersart (Hybride)", "Thales", "Lambersart", "hybrid"),
        (
            "Deloitte · La Défense (Hybride)",
            "Deloitte",
            "La Défense",
            "hybrid",
        ),
        (
            "Davidson consulting · Île-de-France, France",
            "Davidson consulting",
            "Île-de-France, France",
            None,
        ),
        # English workplace wording
        ("Contoso · Dublin (On-site)", "Contoso", "Dublin", "onsite"),
        ("Contoso · Dublin (Hybrid)", "Contoso", "Dublin", "hybrid"),
        ("Contoso · Dublin (Remote)", "Contoso", "Dublin", "full_remote"),
        ("Contoso · Paris (À distance)", "Contoso", "Paris", "full_remote"),
        # bullet separator variant
        ("Inetum • Lille", "Inetum", "Lille", None),
        # a hyphen is honoured only when exactly one occurs
        ("Inetum - Lille", "Inetum", "Lille", None),
    ],
)
def test_card_line_splits_into_company_city_and_workplace(
    line: str, company: str, city: str, policy: str | None
) -> None:
    card = parse_card_line(line)

    assert card is not None
    assert card.company == company
    assert card.city == city
    assert card.remote_policy == policy


def test_hyphen_fallback_refuses_ambiguous_lines() -> None:
    """Hyphens are common inside real place names; only split when unambiguous."""
    assert parse_card_line("Roissy-en-France") is None
    assert parse_card_line("Acme - Lille - Hauts-de-France") is None


def test_workplace_maps_onto_the_existing_remote_policy_vocabulary() -> None:
    """The same four values models.REMOTE_POLICIES defines for every source."""
    for line in (
        "Acme · Lille (Sur site)",
        "Acme · Lille (Hybride)",
        "Acme · Lille (À distance)",
        "Acme · Lille (On-site)",
        "Acme · Lille (Hybrid)",
        "Acme · Lille (Remote)",
    ):
        card = parse_card_line(line)
        assert card is not None
        assert card.remote_policy in REMOTE_POLICIES
        assert card.remote_policy != "unknown"


def test_non_workplace_parenthetical_is_part_of_the_location() -> None:
    """Indeed writes "Villeneuve-d'Ascq (59)" — the postcode is not a workplace."""
    assert split_workplace("Villeneuve-d'Ascq (59)") == ("Villeneuve-d'Ascq (59)", None)
    assert split_workplace("Lille (Hybride)") == ("Lille", "hybrid")


def test_card_line_reaches_the_offer_record() -> None:
    records = parse_linkedin(
        _card_html(
            "Ingénieur support des solutions de Cybersécurité (F/H)",
            "Thales · Vélizy-Villacoublay (Hybride)",
            "Recrutement actif",
        )
    )

    assert len(records) == 1
    offer = records[0]
    assert offer.company_name == "Thales"
    assert offer.city == "Vélizy-Villacoublay"
    assert offer.remote_policy == "hybrid"


# ---- 20.2 UI noise never becomes a field ----

# Every string below was found in offers.city on the real database.
REAL_NOISE = [
    "Recrutement actif",
    "Actively recruiting",
    "Candidature simplifiée",
    "Easy Apply",
    "Promu",
    "Promoted",
    "Voir l'offre",
    "Postuler",
    "1 relation",
    "F/H",
    "H/F",
    "M/F",
    "F/H/X",
    "(F/H)",
    "F/H F/H",
    "82 anciens collègues",
    "9 anciens élèves",
    "1 ancien élève",
    "entre 46 k € et 70 k € par an",
    "entre 35 k € et 45 k € par an",
]


@pytest.mark.parametrize("noise", REAL_NOISE)
def test_known_noise_is_recognised(noise: str) -> None:
    assert is_noise(noise) is True
    assert scrub_chunk(noise)[0] is None


@pytest.mark.parametrize("noise", REAL_NOISE)
def test_noise_never_reaches_company_or_city(noise: str) -> None:
    """Whatever position the chrome occupies, it must not be stored."""
    records = parse_linkedin(_card_html("Analyste SOC", noise, noise))

    assert len(records) == 1
    offer = records[0]
    assert offer.city is None
    assert offer.company_name is None
    assert noise not in (offer.title or "")


@pytest.mark.parametrize("count", [1, 2, 4, 9, 13, 22, 82, 122])
def test_connection_counts_are_matched_by_pattern_not_literal(count: int) -> None:
    """No literal list can enumerate these; N varies freely."""
    for template in (
        "{n} relation",
        "{n} relations",
        "{n} connection",
        "{n} connections",
        "{n} anciens collègues",
        "{n} anciens élèves",
    ):
        assert is_noise(template.format(n=count)) is True


@pytest.mark.parametrize(
    "city",
    ["Lille", "Vélizy-Villacoublay", "Île-de-France, France", "Le Plessis-Robinson"],
)
def test_plausible_place_names_are_not_treated_as_noise(city: str) -> None:
    assert is_noise(city) is False
    assert scrub_chunk(city)[0] == city


def test_noise_leaves_the_field_none_rather_than_storing_junk() -> None:
    """None is strictly better: the hard filter reads it as "do not reject"."""
    records = parse_linkedin(_card_html("Ingénieur réseau h/f", "Recrutement actif"))

    assert records[0].city is None
    assert records[0].company_name is None


# ---- 20.3 Easy Apply is captured, not discarded ----


def test_easy_apply_is_captured_as_a_boolean() -> None:
    records = parse_linkedin(
        _card_html("Analyste SOC", "Inetum · Lille", "Candidature simplifiée")
    )

    assert records[0].easy_apply is True
    assert records[0].city == "Lille"


def test_easy_apply_recognised_in_english() -> None:
    records = parse_linkedin(_card_html("SOC Analyst", "Contoso · Dublin", "Easy Apply"))
    assert records[0].easy_apply is True


def test_easy_apply_absent_by_default() -> None:
    records = parse_linkedin(_card_html("Analyste SOC", "Inetum · Lille"))
    assert records[0].easy_apply is False


def test_easy_apply_is_stripped_out_of_a_mixed_chunk() -> None:
    """Observed verbatim: "Levallois-Perret (Sur site) Candidature simplifiée"."""
    usable, easy_apply = scrub_chunk("Levallois-Perret (Sur site) Candidature simplifiée")

    assert usable == "Levallois-Perret (Sur site)"
    assert easy_apply is True

    records = parse_linkedin(
        _card_html(
            "Ingénieur Sécurité AWS (H/F)",
            "Cyber Trust",
            "Levallois-Perret (Sur site) Candidature simplifiée",
        )
    )
    offer = records[0]
    assert offer.company_name == "Cyber Trust"
    assert offer.city == "Levallois-Perret"
    assert offer.remote_policy == "onsite"
    assert offer.easy_apply is True


def test_easy_apply_is_never_stored_in_a_text_field() -> None:
    records = parse_linkedin(
        _card_html("Analyste SOC", "Inetum · Lille", "Candidature simplifiée")
    )
    offer = records[0]

    for value in (offer.city, offer.company_name, offer.description, offer.title):
        assert "andidature simplifi" not in (value or "")


# ---- unparseable cards degrade to None, never to a wrong value ----


def test_unparseable_card_yields_none_and_warns(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level("WARNING"):
        records = parse_linkedin(_card_html("Analyste SOC", "Recrutement actif"))

    assert records[0].city is None
    assert records[0].company_name is None
    assert "yielded no company or city" in caplog.text


def test_card_with_no_context_does_not_crash() -> None:
    records = parse_linkedin(_card_html("Analyste SOC"))
    assert records[0].title == "Analyste SOC"
    assert records[0].city is None


# ---- a title echoed into another field is not a company or a place ----


@pytest.mark.parametrize(
    ("city", "title"),
    [
        # verbatim from the real offers table: the card appended the company to
        # the title anchor and repeated the bare title as the next chunk.
        ("Ingénieur Cloud Security H/F", "Ingénieur Cloud Security H/F Inetum"),
        ("Ingénieur Cyber Réseau H/F", "Ingénieur Cyber Réseau H/F SUEZ"),
        (
            "Security Engineer, AWS CIRT",
            "Security Engineer, AWS CIRT Amazon Web Services (AWS)",
        ),
        (
            "Security Engineer (DevSecOps / Code Security)",
            "Security Engineer (DevSecOps / Code Security) Owkin",
        ),
        (
            "Job Dating : Rejoignez nos équipes Systèmes & Cyberdéfense",
            "Job Dating : Rejoignez nos équipes Systèmes & Cyberdéfense Airbus",
        ),
    ],
)
def test_title_echo_is_refused_as_a_location(city: str, title: str) -> None:
    assert is_title_echo(city, title) is True
    assert derive_fields(None, city, title=title).city is None


def test_a_real_city_that_merely_opens_the_title_is_kept() -> None:
    """The length guard must not sacrifice a genuine place name."""
    assert is_title_echo("Paris", "Paris Saint-Germain — Analyste Cybersécurité") is False
    assert derive_fields(
        None, "Paris", title="Paris Saint-Germain — Analyste Cybersécurité"
    ).city == "Paris"


def test_title_echo_chunk_is_not_stored_at_ingest() -> None:
    records = parse_linkedin(
        _card_html(
            "Ingénieur Cloud Security H/F Inetum",
            "Ingénieur Cloud Security H/F",
            "Saint-Ouen",
        )
    )

    offer = records[0]
    assert offer.city != "Ingénieur Cloud Security H/F"
    assert offer.company_name != "Ingénieur Cloud Security H/F"


def test_no_city_is_ever_inferred_from_a_company_name() -> None:
    """"Paris Saint-Germain" is a company; it must not become a city."""
    records = parse_linkedin(_card_html("Analyste SOC", "Paris Saint-Germain"))
    assert records[0].city is None


# ---- 20.4 reparse over already-stored offers ----


def _seed_alert_offer(
    db: sqlite3.Connection,
    *,
    offer_id: int,
    company: str | None,
    city: str | None,
    description: str = "",
) -> None:
    sid = db.execute(
        "SELECT id FROM sources WHERE name = 'linkedin_alert'"
    ).fetchone()["id"]
    company_id = None
    if company is not None:
        cur = db.execute("INSERT INTO companies (name) VALUES (?)", (company,))
        company_id = cur.lastrowid
    db.execute(
        "INSERT INTO offers (id, source_id, company_id, external_id, url, title, "
        " description, contract_type, city, remote_policy, content_hash) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, 'unknown', ?, 'unknown', ?)",
        (
            offer_id,
            sid,
            company_id,
            str(offer_id),
            f"https://www.linkedin.com/jobs/view/{offer_id}",
            "Analyste SOC",
            description,
            city,
            f"hash-{offer_id}",
        ),
    )
    db.commit()


def test_reparse_recovers_company_and_city_from_the_stored_card_line(
    db: sqlite3.Connection,
) -> None:
    """The card line survived in companies.name; the city held only chrome."""
    _seed_alert_offer(
        db,
        offer_id=1,
        company="Thales · Vélizy-Villacoublay (Hybride)",
        city="Recrutement actif",
    )

    result = reparse_alerts(db)

    row = db.execute(
        "SELECT o.city, o.remote_policy, c.name AS company FROM offers o "
        "LEFT JOIN companies c ON c.id = o.company_id WHERE o.id = 1"
    ).fetchone()
    assert row["company"] == "Thales"
    assert row["city"] == "Vélizy-Villacoublay"
    assert row["remote_policy"] == "hybrid"
    assert result.updated == 1
    assert result.noise_cleared == 1


def test_reparse_clears_noise_it_cannot_replace_and_reports_it(
    db: sqlite3.Connection,
) -> None:
    _seed_alert_offer(db, offer_id=2, company="Cyber Trust", city="1 relation")

    result = reparse_alerts(db)

    row = db.execute("SELECT city FROM offers WHERE id = 2").fetchone()
    assert row["city"] is None  # junk cleared, nothing invented in its place
    assert result.unrecoverable == 1


def test_reparse_recovers_easy_apply(db: sqlite3.Connection) -> None:
    _seed_alert_offer(
        db,
        offer_id=3,
        company="Inetum · Lille",
        city="Candidature simplifiée",
    )

    reparse_alerts(db)

    row = db.execute("SELECT easy_apply, city FROM offers WHERE id = 3").fetchone()
    assert row["easy_apply"] == 1
    assert row["city"] == "Lille"


def test_reparse_skips_offers_that_already_have_an_application(
    db: sqlite3.Connection,
) -> None:
    _seed_alert_offer(
        db,
        offer_id=4,
        company="Thales · Vélizy-Villacoublay (Hybride)",
        city="Recrutement actif",
    )
    db.execute(
        "INSERT INTO applications (offer_id, kind, status) VALUES (4, 'offer', 'queued')"
    )
    db.commit()

    result = reparse_alerts(db)

    row = db.execute("SELECT city FROM offers WHERE id = 4").fetchone()
    assert row["city"] == "Recrutement actif"  # untouched
    assert result.skipped_with_application == 1
    assert result.scanned == 0


def test_reparse_does_not_touch_applications_statuses_or_events(
    db: sqlite3.Connection,
) -> None:
    _seed_alert_offer(db, offer_id=5, company="Inetum · Lille", city="Recrutement actif")
    _seed_alert_offer(db, offer_id=6, company="Acme · Paris", city="1 relation")
    db.execute(
        "INSERT INTO applications (offer_id, kind, status) VALUES (6, 'offer', 'ready')"
    )
    db.commit()
    before_apps = db.execute("SELECT id, status FROM applications").fetchall()
    before_events = db.execute("SELECT count(*) AS n FROM events").fetchone()["n"]

    reparse_alerts(db)

    after_apps = db.execute("SELECT id, status FROM applications").fetchall()
    assert [tuple(r) for r in after_apps] == [tuple(r) for r in before_apps]
    assert db.execute("SELECT count(*) AS n FROM events").fetchone()["n"] == before_events


def test_reparse_is_idempotent(db: sqlite3.Connection) -> None:
    _seed_alert_offer(
        db, offer_id=7, company="Thales · Lambersart (Hybride)", city="Recrutement actif"
    )

    first = reparse_alerts(db)
    second = reparse_alerts(db)

    assert first.updated == 1
    assert second.updated == 0
    assert second.unchanged == 1


def test_reparse_rejects_a_non_alert_source(db: sqlite3.Connection) -> None:
    with pytest.raises(ValueError, match="not an alert source"):
        reparse_alerts(db, "france_travail")


def test_derive_fields_invents_nothing_when_there_is_nothing_to_read() -> None:
    derived = derive_fields("Recrutement actif", "1 relation")

    assert derived.company is None
    assert derived.city is None
    assert derived.remote_policy == "unknown"
    assert derived.unrecoverable is True
