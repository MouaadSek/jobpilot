"""Task 34.D: form learning — what may be recorded, and what may never be.

This table decides what gets typed into a stranger's form, so the tests that
matter most are the negative ones: the fields that are refused, the values that
are never stored, and the submit gate that stays off until somebody decides
otherwise per domain.
"""

from __future__ import annotations

import logging
import sqlite3

import pytest

from jobpilot.apply_assist import ApplicantProfile
from jobpilot.form_learning import (
    PROFILE_FIELDS,
    REQUIRED_PROFILE_FIELDS,
    FormField,
    FormLearningError,
    build_prefill,
    fields_from_html,
    infer_profile_field,
    mapping_is_complete,
    mappings_for,
    put_mapping,
    record_form_fields,
    refusal_category,
    set_submit_enabled,
    submit_enabled,
)
from jobpilot.routing import has_form_mapping

DOMAIN = "carrieres.acme.fr"

APPLICANT = ApplicantProfile(
    full_name="Mouaad Sekkouri",
    email="mouaad@example.test",
    phone="+33600000000",
    linkedin_url="https://linkedin.example/in/mouaad",
)

# Sentinels: if any of these ever reaches the database, the design is wrong.
SENTINEL_VALUES = (
    "Mouaad Sekkouri",
    "mouaad@example.test",
    "+33600000000",
    "https://linkedin.example/in/mouaad",
    "hunter2",
    "4111111111111111",
    "FR7630006000011234567890189",
)


def _fields(**overrides: str) -> FormField:
    return FormField(**{"selector": 'input[name="x"]', **overrides})  # type: ignore[arg-type]


# ----- the closed enum -----


def test_profile_field_is_a_closed_enum_of_what_the_profile_holds() -> None:
    assert PROFILE_FIELDS == {
        "full_name",
        "first_name",
        "last_name",
        "email",
        "phone",
        "linkedin_url",
        "cv_path",
        "letter_path",
    }
    assert set(REQUIRED_PROFILE_FIELDS) <= PROFILE_FIELDS


@pytest.mark.parametrize(
    "value", ["salary_expectation", "", "FULL_NAME", "notes", "password"]
)
def test_an_unknown_profile_field_is_rejected_at_write_time(
    db: sqlite3.Connection, value: str
) -> None:
    """An arbitrary string is not acceptable — this decides what gets typed in."""

    with pytest.raises(FormLearningError, match="unknown profile_field"):
        put_mapping(
            db, domain=DOMAIN, selector='input[name="x"]', profile_field=value
        )

    assert mappings_for(db, DOMAIN) == ()


def test_every_allowed_profile_field_can_actually_be_written(
    db: sqlite3.Connection,
) -> None:
    for index, field in enumerate(sorted(PROFILE_FIELDS)):
        put_mapping(
            db, domain=DOMAIN, selector=f'input[name="f{index}"]', profile_field=field
        )
    db.commit()

    assert {mapping.profile_field for mapping in mappings_for(db, DOMAIN)} == (
        PROFILE_FIELDS
    )


# ----- the safety detector -----


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        (_fields(field_type="password"), "password"),
        (_fields(name="mot_de_passe"), "password"),
        (_fields(label="Mot de passe"), "password"),
        (_fields(autocomplete="new-password"), "password"),
        (_fields(name="card_number"), "payment"),
        (_fields(label="Numéro de carte bancaire"), "payment"),
        (_fields(name="cvv"), "payment"),
        (_fields(name="iban"), "payment"),
        (_fields(autocomplete="cc-number"), "payment"),
        (_fields(label="Expiration date"), "payment"),
        (_fields(name="ssn"), "identity_document"),
        (_fields(label="Numéro de sécurité sociale"), "identity_document"),
        (_fields(name="passport_number"), "identity_document"),
        (_fields(label="Carte d'identité"), "identity_document"),
        (_fields(name="permis_de_conduire"), "identity_document"),
        (_fields(label="Titre de séjour"), "identity_document"),
    ],
)
def test_sensitive_fields_are_detected_by_category(
    field: FormField, expected: str
) -> None:
    assert refusal_category(field) == expected


@pytest.mark.parametrize(
    "field",
    [
        _fields(name="first_name"),
        _fields(label="Adresse e-mail"),
        _fields(name="telephone"),
        _fields(name="linkedin_url"),
        _fields(name="cv", field_type="file"),
    ],
)
def test_ordinary_fields_are_not_refused(field: FormField) -> None:
    assert refusal_category(field) is None
    assert infer_profile_field(field) in PROFILE_FIELDS


def test_a_sensitive_field_is_refused_recorded_nowhere_and_logged(
    db: sqlite3.Connection, caplog: pytest.LogCaptureFixture
) -> None:
    fields = [
        FormField(selector='input[name="email"]', name="email", label="E-mail"),
        FormField(selector='input[name="pwd"]', field_type="password", name="pwd"),
        FormField(selector='input[name="card_number"]', name="card_number"),
        FormField(selector='input[name="ssn"]', name="ssn"),
    ]

    with caplog.at_level(logging.WARNING, logger="jobpilot.form_learning"):
        result = record_form_fields(db, DOMAIN, fields)

    assert sorted(category for _, category in result.refused) == [
        "identity_document",
        "password",
        "payment",
    ]
    # Only the harmless field was recorded.
    assert [mapping.selector for mapping in mappings_for(db, DOMAIN)] == [
        'input[name="email"]'
    ]
    stored = db.execute("SELECT selector FROM form_mappings").fetchall()
    assert {row["selector"] for row in stored} == {'input[name="email"]'}

    messages = " ".join(record.getMessage() for record in caplog.records)
    for category in ("password", "payment", "identity_document"):
        assert category in messages
    assert "left to the human" in messages


def test_a_refused_field_stays_refused_on_every_later_visit(
    db: sqlite3.Connection,
) -> None:
    """Nothing is written for it, so the next pass re-detects and re-refuses —
    which is what 'left for the human permanently' means."""

    field = FormField(selector='input[name="iban"]', name="iban")

    for _ in range(3):
        result = record_form_fields(db, DOMAIN, [field])
        assert result.refused == (('input[name="iban"]', "payment"),)

    assert mappings_for(db, DOMAIN) == ()


# ----- never a value -----


def test_no_field_value_reaches_the_database_after_a_full_cycle(
    db: sqlite3.Connection,
) -> None:
    """Scan every column of the table for the sentinel values used above."""

    html = (
        '<form><input name="full_name" value="Mouaad Sekkouri">'
        '<input name="email" type="email" value="mouaad@example.test">'
        '<input name="phone" value="+33600000000">'
        '<input name="linkedin" value="https://linkedin.example/in/mouaad">'
        '<input name="password" type="password" value="hunter2">'
        '<input name="card_number" value="4111111111111111">'
        '<input name="iban" value="FR7630006000011234567890189">'
        "</form>"
    )

    fields = fields_from_html(html)
    record_form_fields(db, DOMAIN, fields)
    build_prefill(db, DOMAIN, html, APPLICANT, cv_path="/tmp/cv.pdf")

    rows = db.execute("SELECT * FROM form_mappings").fetchall()
    assert rows  # the cycle really did record something
    dumped = " | ".join(
        str(value) for row in rows for value in tuple(row) if value is not None
    )
    for sentinel in SENTINEL_VALUES:
        assert sentinel not in dumped, f"{sentinel!r} leaked into form_mappings"


def test_observable_controls_never_expose_what_the_human_typed() -> None:
    """One enforcement point: values are stripped before this module sees them."""

    from jobpilot.apply_assist import observable_controls

    controls = observable_controls(
        '<input name="email" value="mouaad@example.test" placeholder="votre email">'
    )

    assert controls[0]["name"] == "email"
    assert "value" not in controls[0]
    assert "placeholder" not in controls[0]


# ----- brittle selectors -----


def test_a_stale_selector_is_discarded_with_a_log_not_guessed_around(
    db: sqlite3.Connection, caplog: pytest.LogCaptureFixture
) -> None:
    put_mapping(
        db, domain=DOMAIN, selector='input[name="email"]', profile_field="email"
    )
    put_mapping(
        db, domain=DOMAIN, selector='input[name="candidate_name"]',
        profile_field="full_name",
    )
    db.commit()
    # The site renamed one field between visits.
    html = '<form><input name="email"><input name="applicant_name"></form>'

    with caplog.at_level(logging.WARNING, logger="jobpilot.form_learning"):
        outcome = build_prefill(db, DOMAIN, html, APPLICANT)

    assert outcome.discarded == ('input[name="candidate_name"]',)
    assert outcome.fills == (('input[name="email"]', "mouaad@example.test"),)
    assert [m.selector for m in mappings_for(db, DOMAIN)] == ['input[name="email"]']
    messages = " ".join(record.getMessage() for record in caplog.records)
    assert "discarded stale mapping" in messages


def test_a_fully_stale_mapping_drops_the_route_back_to_manual_open(
    db: sqlite3.Connection,
) -> None:
    """Falling back to manual_open is correct behaviour, not a bug."""

    put_mapping(db, domain=DOMAIN, selector='input[name="email"]', profile_field="email")
    put_mapping(db, domain=DOMAIN, selector='input[name="nom"]', profile_field="full_name")
    db.commit()
    assert has_form_mapping(db, DOMAIN) is True

    # The site was rebuilt; not one selector still matches.
    outcome = build_prefill(
        db, DOMAIN, '<form><input name="q"></form>', APPLICANT
    )

    assert len(outcome.discarded) == 2
    assert outcome.usable is False
    assert has_form_mapping(db, DOMAIN) is False


def test_an_incomplete_mapping_is_not_a_route(db: sqlite3.Connection) -> None:
    put_mapping(db, domain=DOMAIN, selector='input[name="tel"]', profile_field="phone")
    db.commit()

    assert mappings_for(db, DOMAIN)
    assert mapping_is_complete(db, DOMAIN) is False
    assert has_form_mapping(db, DOMAIN) is False


def test_a_learned_domain_becomes_routable(db: sqlite3.Connection) -> None:
    html = (
        '<form><input name="full_name"><input name="email" type="email">'
        '<input name="telephone"></form>'
    )

    record_form_fields(db, DOMAIN, fields_from_html(html))

    assert mapping_is_complete(db, DOMAIN) is True
    assert has_form_mapping(db, DOMAIN) is True


# ----- the submit gate -----


def test_the_per_domain_submit_gate_defaults_to_off(db: sqlite3.Connection) -> None:
    """Prefill is automatic; pressing submit is not."""

    record_form_fields(
        db,
        DOMAIN,
        fields_from_html('<form><input name="full_name"><input name="email"></form>'),
    )

    assert submit_enabled(db, DOMAIN) is False
    row = db.execute(
        "SELECT submit_enabled FROM form_domains WHERE domain = ?", (DOMAIN,)
    ).fetchone()
    # Learning a domain does not even create a gate row, let alone an open one.
    assert row is None


def test_the_submit_gate_default_is_off_in_the_schema_itself(
    db: sqlite3.Connection,
) -> None:
    db.execute("INSERT INTO form_domains (domain) VALUES (?)", (DOMAIN,))
    db.commit()

    row = db.execute(
        "SELECT submit_enabled FROM form_domains WHERE domain = ?", (DOMAIN,)
    ).fetchone()

    assert row["submit_enabled"] == 0
    assert submit_enabled(db, DOMAIN) is False


def test_the_submit_gate_is_respected_and_is_per_domain(
    db: sqlite3.Connection,
) -> None:
    other = "carrieres.autre.fr"
    html = '<form><input name="full_name"><input name="email"></form>'
    for domain in (DOMAIN, other):
        record_form_fields(db, domain, fields_from_html(html))

    set_submit_enabled(db, DOMAIN, True)

    assert build_prefill(db, DOMAIN, html, APPLICANT).submit_enabled is True
    assert build_prefill(db, other, html, APPLICANT).submit_enabled is False
    assert submit_enabled(db, other) is False


def test_the_submit_gate_can_be_closed_again(db: sqlite3.Connection) -> None:
    set_submit_enabled(db, DOMAIN, True)
    set_submit_enabled(db, DOMAIN, False)

    assert submit_enabled(db, DOMAIN) is False


# ----- migration shape -----


def test_migration_007_creates_the_table_the_spec_specified(
    db: sqlite3.Connection,
) -> None:
    columns = {
        row["name"]: row
        for row in db.execute("PRAGMA table_info(form_mappings)").fetchall()
    }

    assert set(columns) == {
        "id",
        "domain",
        "selector",
        "label",
        "profile_field",
        "created_at",
        "last_used_at",
        "uses",
    }
    assert columns["domain"]["notnull"] == 1
    assert columns["selector"]["notnull"] == 1
    assert columns["profile_field"]["notnull"] == 1
    assert columns["uses"]["notnull"] == 1
    indexes = db.execute("PRAGMA index_list(form_mappings)").fetchall()
    unique = [row for row in indexes if row["unique"]]
    assert unique, "UNIQUE (domain, selector) is what makes relearning idempotent"


def test_relearning_a_domain_does_not_duplicate_rows(db: sqlite3.Connection) -> None:
    html = '<form><input name="full_name"><input name="email"></form>'

    for _ in range(3):
        record_form_fields(db, DOMAIN, fields_from_html(html))

    assert len(mappings_for(db, DOMAIN)) == 2
