"""Packaging guards: the frozen root-level matcher.py must be importable.

`jobpilot score` imports `matcher` through `jobpilot.scoring`. matcher.py lives
at the repo root while the distribution installs `src/`, so the module has to be
declared in pyproject.toml (`[tool.setuptools] py-modules`) with a per-package
`package-dir` mapping. Without that, a clean `pip install -e .` yields
`ModuleNotFoundError: No module named 'matcher'` outside the repo root.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_matcher_is_importable() -> None:
    import matcher

    assert hasattr(matcher, "score_new_offers")


def test_matcher_importable_outside_repo_root(tmp_path: Path) -> None:
    """The real regression: importing from a cwd that is not the repo root.

    Run in a subprocess with PYTHONPATH scrubbed so we exercise the installed
    distribution rather than the implicit cwd entry on sys.path.
    """
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    proc = subprocess.run(
        [sys.executable, "-c", "import matcher; print(matcher.__file__)"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=env,
    )

    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip().endswith("matcher.py")


def test_pyproject_declares_matcher_as_a_top_level_module() -> None:
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    setuptools_cfg = config["tool"]["setuptools"]

    assert "matcher" in setuptools_cfg["py-modules"]
    # py-modules resolves relative to the implicit root package dir; mapping the
    # package explicitly (rather than rerooting everything at src/) keeps that
    # root at the repo root where matcher.py actually lives.
    assert setuptools_cfg["package-dir"] == {"jobpilot": "src/jobpilot"}
    assert set(setuptools_cfg["packages"]) == {"jobpilot", "jobpilot.sources"}


def test_declared_packages_cover_every_source_package() -> None:
    """Explicit `packages` replaced auto-discovery — keep it from drifting."""
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    declared = set(config["tool"]["setuptools"]["packages"])

    found = {
        ".".join(init.relative_to(ROOT / "src").parent.parts)
        for init in (ROOT / "src").rglob("__init__.py")
    }

    assert found == declared
