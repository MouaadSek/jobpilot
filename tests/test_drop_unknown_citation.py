"""Task 37 item 3: degradation. Shipped off, turned ON by Task 39.

If the advisor still cites an id that does not exist after every retry, that one
citation can be dropped and the CV generated without it — but only from a
position where losing it cannot weaken the CV, and never silently.

Task 37 shipped it disabled and asked for evidence. The evidence arrived: unknown
fact ids are the most common failure in the events history, and they are the
cheapest to recover from. The objection was that a silently weaker CV is worse
than a failed generation — so Task 39 item 2 made it visible first, in amber, on
the application page and with a marker in the library and the tracker, and item 3
turned the flag on. Setting it to false restores the old behaviour exactly.
"""

from __future__ import annotations

import dataclasses
import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest

from jobpilot.apply_flow import ApplicationGenerationError, approve_application
from jobpilot.config import get_settings
from jobpilot.facts import load_fact_bank
from jobpilot.state import current_status
from jobpilot.tailoring import (
    _OLDER_EMPLOYER_MIN_BULLETS,
    _RECENT_EMPLOYER_COUNT,
    _RECENT_EMPLOYER_MIN_BULLETS,
    DroppedCitation,
    TailoringPlan,
    _reverse_chronological_experiences,
    drop_unknown_citation,
)
from tests.test_tailoring import _Toolchain
from tests.test_tailoring_retry import _payload, _queued_application


@pytest.fixture
def bank():
    return load_fact_bank()


def _plan(**overrides) -> TailoringPlan:
    from jobpilot.tailoring import pick_variant
    from tests.test_selection_tailoring import _offer

    offer = _offer()
    selection = pick_variant(offer.description, title=offer.title)
    payload = {**_payload(), **overrides}
    return TailoringPlan.from_mapping(payload, offer=offer, selection=selection)


@contextmanager
def _dropping_enabled(monkeypatch, enabled: bool = True) -> Iterator[None]:
    from jobpilot import tailoring

    monkeypatch.setattr(
        tailoring,
        "get_settings",
        lambda: dataclasses.replace(
            get_settings(), tailoring_drop_unknown_citations=enabled
        ),
    )
    yield


# ----- the flag ships off -----


def test_the_flag_defaults_to_on_since_task_39() -> None:
    """The objection that kept it off was silence, and it is no longer silent.

    Unknown fact ids are the most common failure in the events history and the
    cheapest to recover from. Every drop now names the fact id it removed, in
    amber, on the application page and with a marker in the library.
    """

    assert get_settings().tailoring_drop_unknown_citations is True


def test_the_env_example_documents_it_as_on() -> None:
    example = (Path(__file__).resolve().parents[1] / ".env.example").read_text(
        encoding="utf-8"
    )

    assert "TAILORING_DROP_UNKNOWN_CITATIONS=true" in example


# ----- what may be dropped -----


def test_a_skill_can_be_dropped(bank) -> None:
    """skill_order has no minimum, so losing one weakens nothing structural."""

    plan = _plan(skill_order=["skill.rules.sigma", *_payload()["skill_order"]])

    reduced, dropped = drop_unknown_citation(plan, bank, "skill.rules.sigma")

    assert "skill.rules.sigma" not in reduced.skill_order
    assert set(reduced.skill_order) == set(_payload()["skill_order"])
    assert dropped.position == "skill_order"
    assert dropped.fact_id == "skill.rules.sigma"


def test_a_bullet_can_be_dropped_while_the_entry_stays_above_its_floor(bank) -> None:
    payload = _payload()
    entry = payload["experience_content"][0]
    real = load_fact_bank().experience
    by_id = {item.id: item for item in real}
    plenty = [fact.id for fact in by_id[entry["experience_id"]].facts]
    assert len(plenty) > _RECENT_EMPLOYER_MIN_BULLETS, "fixture needs spare bullets"
    entry["fact_ids"] = plenty

    plan = _plan(experience_content=payload["experience_content"])
    victim = plenty[-1]

    reduced, dropped = drop_unknown_citation(plan, bank, victim)

    kept = reduced.experience_content[0].fact_ids
    assert victim not in kept
    assert len(kept) == len(plenty) - 1
    assert dropped.position == "experience"
    assert dropped.entry_id == entry["experience_id"]


# ----- what may not -----


def test_the_last_bullet_the_floor_requires_is_never_dropped(bank) -> None:
    """The completeness floor is a hard failure, not a preference."""

    payload = _payload()
    order = [entry.id for entry in _reverse_chronological_experiences(bank)]
    for chosen in payload["experience_content"]:
        floor = (
            _RECENT_EMPLOYER_MIN_BULLETS
            if order.index(chosen["experience_id"]) < _RECENT_EMPLOYER_COUNT
            else _OLDER_EMPLOYER_MIN_BULLETS
        )
        chosen["fact_ids"] = chosen["fact_ids"][:floor]

    plan = _plan(experience_content=payload["experience_content"])

    for chosen in plan.experience_content:
        for fact_id in chosen.fact_ids:
            assert drop_unknown_citation(plan, bank, fact_id) is None


def test_a_recent_employer_may_not_fall_to_one_bullet(bank) -> None:
    """The spec said "at least one remaining bullet" is enough. It is not: the
    Task 22 floor requires TWO for each of the two most recent employers, and
    the same spec calls that a hard failure. The floor wins."""

    payload = _payload()
    recent = payload["experience_content"][0]
    real = {item.id: item for item in bank.experience}
    two = [fact.id for fact in real[recent["experience_id"]].facts][:2]
    assert len(two) == 2
    recent["fact_ids"] = two

    plan = _plan(experience_content=payload["experience_content"])

    # One bullet would remain, which the spec's wording permits and the floor
    # forbids. It must be refused.
    assert drop_unknown_citation(plan, bank, two[0]) is None


def test_a_project_fact_is_never_dropped(bank) -> None:
    """Exactly three projects are required, each with its single fact."""

    plan = _plan()
    victim = plan.project_content[0].fact_id

    assert drop_unknown_citation(plan, bank, victim) is None


def test_an_unrecognised_citation_is_never_dropped(bank) -> None:
    plan = _plan()

    assert drop_unknown_citation(plan, bank, "totalement.invente") is None
    assert drop_unknown_citation(plan, bank, plan.experience_content[0].experience_id) is None


# ----- end to end -----


class _InventsForever:
    accepts_correction = True

    def __init__(self, *, into: str = "skill_order") -> None:
        self.into = into
        self.corrections: list[str | None] = []

    @property
    def call_count(self) -> int:
        return len(self.corrections)

    def advise(self, offer, selection, template, *, correction: str | None = None):
        self.corrections.append(correction)
        payload = _payload()
        if self.into == "skill_order":
            payload["skill_order"] = ["skill.rules.sigma", *payload["skill_order"]]
        else:
            payload["project_content"][0]["fact_id"] = "project.rules.sigma"
        return TailoringPlan.from_mapping(payload, offer=offer, selection=selection)


def test_with_the_flag_off_an_invented_id_still_fails(
    db: sqlite3.Connection, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Turning it off restores the old behaviour exactly."""

    application_id = _queued_application(db, suffix="drop-off")

    with (
        _dropping_enabled(monkeypatch, enabled=False),
        pytest.raises(ApplicationGenerationError, match="skill.rules.sigma"),
    ):
        approve_application(
            db, application_id, via="test",
            advisor=_InventsForever(), toolchain=_Toolchain(), output_root=tmp_path,
        )

    assert current_status(db, application_id) == "queued"
    assert db.execute(
        "SELECT count(*) AS n FROM events WHERE application_id = ? "
        "AND event = 'citation_dropped'",
        (application_id,),
    ).fetchone()["n"] == 0


def test_with_the_flag_on_a_droppable_citation_is_dropped_and_recorded(
    db: sqlite3.Connection, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    application_id = _queued_application(db, suffix="drop-on")
    advisor = _InventsForever()

    with _dropping_enabled(monkeypatch):
        approve_application(
            db, application_id, via="test",
            advisor=advisor, toolchain=_Toolchain(), output_root=tmp_path,
        )

    assert current_status(db, application_id) == "ready"
    # Every retry was still spent trying to get a real id first.
    assert advisor.call_count == 3
    row = db.execute(
        "SELECT detail FROM events WHERE application_id = ? "
        "AND event = 'citation_dropped'",
        (application_id,),
    ).fetchone()
    assert row is not None
    detail = json.loads(row["detail"])
    assert detail["fact_id"] == "skill.rules.sigma"
    assert detail["position"] == "skill_order"
    assert "Relisez le CV" in detail["warning"]


def test_with_the_flag_on_an_undroppable_citation_still_fails(
    db: sqlite3.Connection, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Enabling degradation does not make everything droppable."""

    application_id = _queued_application(db, suffix="drop-refuse")

    with _dropping_enabled(monkeypatch), pytest.raises(ApplicationGenerationError):
        approve_application(
            db, application_id, via="test",
            advisor=_InventsForever(into="project"), toolchain=_Toolchain(),
            output_root=tmp_path,
        )

    assert current_status(db, application_id) == "queued"


def test_the_warning_is_visible_on_the_application_page(
    dashboard_db: sqlite3.Connection, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Nobody reviews what they were not told about."""

    from fastapi.testclient import TestClient

    from jobpilot.apply_flow import APPLICATION_LOCK
    from jobpilot.dashboard import create_app, database_connection

    with APPLICATION_LOCK:
        application_id = _queued_application(dashboard_db, suffix="drop-visible")

    with _dropping_enabled(monkeypatch):
        approve_application(
            dashboard_db, application_id, via="test",
            advisor=_InventsForever(), toolchain=_Toolchain(), output_root=tmp_path,
        )

    app = create_app(output_root=tmp_path)

    def connection() -> Iterator[sqlite3.Connection]:
        with APPLICATION_LOCK:
            yield dashboard_db

    app.dependency_overrides[database_connection] = connection
    with TestClient(app) as client:
        page = client.get(f"/application/{application_id}")

    assert "skill.rules.sigma" in page.text
    assert "Relisez le CV" in page.text
    # role="status", not role="alert": Task 39 made this amber rather than red.
    # The document exists and is usable — it is "check this before sending", not
    # "this failed" — and an assertive live region for every degraded generation
    # is how a reviewer learns to dismiss the banner without reading it.
    assert 'role="status"' in page.text
    assert 'class="warn"' in page.text


def test_the_warning_names_where_the_citation_was_removed_from() -> None:
    skill = DroppedCitation(fact_id="skill.x", position="skill_order")
    bullet = DroppedCitation(
        fact_id="experience.a.b", position="experience", entry_id="experience.a"
    )

    assert "compétences" in skill.warning
    assert "experience.a" in bullet.warning
    for warning in (skill.warning, bullet.warning):
        assert "Relisez le CV avant de l'envoyer." in warning
