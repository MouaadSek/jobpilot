"""The post-tailoring script accepts sourced structural edits, not empty content."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skill" / "scripts" / "validate_cv.py"


def _validator():
    sys.path.insert(0, str(SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("jobpilot_validate_cv", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_ai_tailoring_allows_one_to_three_rewritten_projects() -> None:
    validator = _validator()
    html = (
        "<section><h2>Projets Personnels</h2>"
        '<div class="project-item"><div class="project-desc">'
        + ("Description factuelle adaptée. " * 3)
        + "</div></div></section>"
    )

    count_ok, _ = validator.check_project_count(html)
    descriptions_ok, _ = validator.check_project_descs(html)

    assert count_ok is True
    assert descriptions_ok is True


def test_line_count_is_informational_after_structural_tailoring() -> None:
    validator = _validator()

    ok, message = validator.check_line_count("one\nline", "one\nline\nmore")

    assert ok is True
    assert "structural tailoring" in message


def test_empty_or_excessive_project_description_still_fails() -> None:
    validator = _validator()
    empty = '<div class="project-desc"></div>'
    excessive = f'<div class="project-desc">{"x" * 181}</div>'

    assert validator.check_project_descs(empty)[0] is False
    assert validator.check_project_descs(excessive)[0] is False
