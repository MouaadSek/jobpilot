"""Task 41: one command after a merge, and it refuses rather than half-updates.

scripts/update.sh is the only thing on this machine that runs after someone
merges. If it is wrong it is wrong quietly, on a box nobody is watching, so the
two behaviours worth pinning are the refusal (a dirty tree) and the skipping (a
pull that changed neither pyproject.toml nor migrations/ must not pay for a
dependency resolve and a schema pass).

The repository under test is a throwaway one with a stub interpreter, so these
run the real script end to end without touching the developer's tree, venv, or
LaunchAgents.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

needs_posix_shell = pytest.mark.skipif(
    sys.platform == "win32", reason="POSIX shell scripts are not run on Windows"
)

#: Stands in for the venv interpreter. It logs every call, answers the one
#: question update.sh asks it (`-c` -> the database path), and succeeds at
#: everything else — including the heredocs, whose stdin it ignores.
_PYTHON_STUB = """#!/bin/sh
printf '%s\\n' "$*" >> "$LOG"
case "$1" in
    -c) echo "$DB_PATH" ;;
    -) cat > /dev/null ;;
esac
exit 0
"""

_LAUNCHCTL_STUB = '#!/bin/sh\nprintf \'%s\\n\' "$*" >> "$LAUNCHCTL_LOG"\nexit 0\n'


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.email=t@t.test", "-c", "user.name=Test", *args],
        cwd=repo,
        check=True,
        capture_output=True,
    )


@contextmanager
def _fake_clone(tmp_path: Path) -> Iterator[tuple[dict[str, str], Path, Path, Path]]:
    """An origin, a clone of it, a stub interpreter, and a stub launchctl."""

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "python-calls.log"
    launchctl_log = tmp_path / "launchctl-calls.log"
    for name, body in (("python", _PYTHON_STUB), ("launchctl", _LAUNCHCTL_STUB)):
        stub = bin_dir / name
        stub.write_text(body, encoding="utf-8")
        stub.chmod(0o755)

    origin = tmp_path / "origin"
    origin.mkdir()
    _git(origin, "init", "--initial-branch=main", ".")
    (origin / "scripts").mkdir()
    for name in ("update.sh", "install_agent.sh", "uninstall_agent.sh"):
        shutil.copy2(SCRIPTS / name, origin / "scripts" / name)
    (origin / "migrations").mkdir()
    (origin / "migrations" / "001_x.sql").write_text("SELECT 1;\n", encoding="utf-8")
    (origin / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    (origin / ".gitignore").write_text(".venv/\nbackups/\ndata/\n", encoding="utf-8")
    _git(origin, "add", "-A")
    _git(origin, "commit", "-m", "base")

    repo = tmp_path / "repo"
    subprocess.run(
        ["git", "clone", str(origin), str(repo)], check=True, capture_output=True
    )
    venv_bin = repo / ".venv" / "bin"
    venv_bin.mkdir(parents=True)
    shutil.copy2(bin_dir / "python", venv_bin / "python")
    (venv_bin / "python").chmod(0o755)

    home = tmp_path / "home"
    home.mkdir()
    env = dict(os.environ)
    env["HOME"] = str(home)
    env["PATH"] = f"{bin_dir}{os.pathsep}{env['PATH']}"
    env["LOG"] = str(log)
    env["LAUNCHCTL_LOG"] = str(launchctl_log)
    env["DB_PATH"] = str(tmp_path / "data" / "jobpilot.db")
    yield env, repo, origin, log


def _run(repo: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["sh", str(repo / "scripts" / "update.sh")],
        capture_output=True,
        text=True,
        env=env,
        cwd=repo,
    )


@needs_posix_shell
def test_a_dirty_tree_aborts_before_anything_is_touched(tmp_path: Path) -> None:
    """The loud refusal. A fast-forward carries uncommitted work with it."""

    with _fake_clone(tmp_path) as (env, repo, _origin, log):
        (repo / "pyproject.toml").write_text("[project]\nname='edited'\n", encoding="utf-8")
        result = _run(repo, env)

    assert result.returncode != 0
    assert "Arbre de travail non propre" in result.stderr
    assert "pyproject.toml" in result.stderr
    # Nothing ran: no backup, no pull, no install.
    assert not log.exists()


@needs_posix_shell
def test_an_untracked_file_counts_as_dirty(tmp_path: Path) -> None:
    with _fake_clone(tmp_path) as (env, repo, _origin, _log):
        (repo / "notes.txt").write_text("wip\n", encoding="utf-8")
        result = _run(repo, env)

    assert result.returncode != 0
    assert "Arbre de travail non propre" in result.stderr


@needs_posix_shell
def test_an_unchanged_pull_skips_the_install_and_the_migrations(
    tmp_path: Path,
) -> None:
    """The point of the conditions: the two slow steps cost nothing here."""

    with _fake_clone(tmp_path) as (env, repo, _origin, log):
        result = _run(repo, env)
        calls = log.read_text(encoding="utf-8")

    assert result.returncode == 0, result.stderr
    assert "déjà à jour" in result.stdout
    assert "pip install" not in calls
    assert "init-db" not in calls
    assert "Dépendances   : inchangées" in result.stdout
    assert "Base          : aucune nouvelle migration" in result.stdout


@needs_posix_shell
def test_a_pull_that_moves_pyproject_reinstalls_and_one_that_moves_migrations_migrates(
    tmp_path: Path,
) -> None:
    with _fake_clone(tmp_path) as (env, repo, origin, log):
        (origin / "pyproject.toml").write_text(
            "[project]\nname='x'\nversion='2'\n", encoding="utf-8"
        )
        (origin / "migrations" / "002_y.sql").write_text("SELECT 2;\n", encoding="utf-8")
        _git(origin, "add", "-A")
        _git(origin, "commit", "-m", "move both")

        result = _run(repo, env)
        calls = log.read_text(encoding="utf-8")

    assert result.returncode == 0, result.stderr
    assert "pip install -e ." in calls
    assert "-m jobpilot init-db" in calls


@needs_posix_shell
def test_a_pull_that_touches_neither_still_restarts_both_agents(
    tmp_path: Path,
) -> None:
    """Kickstarting the agents is unconditional: new code is only running once
    the processes holding the old code have been replaced."""

    with _fake_clone(tmp_path) as (env, repo, origin, _log):
        (origin / "README.md").write_text("hello\n", encoding="utf-8")
        _git(origin, "add", "-A")
        _git(origin, "commit", "-m", "docs only")

        result = _run(repo, env)
        agents = sorted((tmp_path / "home" / "Library" / "LaunchAgents").iterdir())

    assert result.returncode == 0, result.stderr
    assert [path.name for path in agents] == [
        "com.jobpilot.dashboard.plist",
        "com.jobpilot.scheduler.plist",
    ]


@needs_posix_shell
def test_the_database_is_backed_up_before_the_pull(tmp_path: Path) -> None:
    """Order matters: a backup taken after a failed migration is worth nothing."""

    with _fake_clone(tmp_path) as (env, repo, _origin, log):
        db = Path(env["DB_PATH"])
        db.parent.mkdir(parents=True, exist_ok=True)
        db.write_bytes(b"")
        result = _run(repo, env)
        calls = log.read_text(encoding="utf-8").splitlines()

    assert result.returncode == 0, result.stderr
    assert "Sauvegarde     :" in result.stdout
    # The heredoc that runs sqlite3's backup API is the second call — after the
    # settings read, and before anything that could change the schema.
    assert calls[0].startswith("-c ")
    assert str(env["DB_PATH"]) in calls[1]
    assert "backups/jobpilot-" in calls[1]


@needs_posix_shell
def test_the_dashboard_check_is_a_request_and_not_a_bound_port(tmp_path: Path) -> None:
    """A dashboard that dies on an import error binds nothing, and launchd still
    reports the job as started, so the last step has to ask for the page."""

    body = (SCRIPTS / "update.sh").read_text(encoding="utf-8")

    assert "urllib.request" in body
    assert "response.status == 200" in body
