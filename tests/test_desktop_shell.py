"""Task 34.C: reaching the dashboard without typing a command.

Nothing here bundles Python. The dashboard already runs; these tests cover the
three things that make it always-up and double-clickable, and the one rule that
keeps Windows CI green — no macOS-only module anywhere in the import graph.
"""

from __future__ import annotations

import ast
import os
import socket
import subprocess
import sys
import tomllib
from collections.abc import Iterator
from contextlib import closing, contextmanager
from pathlib import Path

import pytest
from typer.testing import CliRunner

from jobpilot.cli import app
from jobpilot.dashboard import dashboard_already_running, run_dashboard

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "jobpilot"
SCRIPTS = ROOT / "scripts"

#: Modules that exist only on macOS. Importing any of these at module level
#: breaks `import jobpilot.<anything>` on Sam's Windows box and in CI.
MACOS_ONLY_MODULES = frozenset(
    {"rumps", "AppKit", "Foundation", "objc", "PyObjCTools", "Quartz", "Cocoa"}
)

needs_posix_shell = pytest.mark.skipif(
    sys.platform == "win32", reason="POSIX shell scripts are not run on Windows"
)


@contextmanager
def _bound_port() -> Iterator[int]:
    """Hold a real listening socket, so the collision path is not mocked."""

    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        yield int(listener.getsockname()[1])


# ----- port collision must exit 0 -----


def test_a_free_port_is_not_reported_as_running() -> None:
    with _bound_port() as port:
        pass  # the socket is closed on exit, so the port is now free

    assert dashboard_already_running(port, timeout=0.2) is False


def test_a_bound_port_is_reported_as_running() -> None:
    with _bound_port() as port:
        assert dashboard_already_running(port, timeout=0.2) is True


def test_port_collision_prints_the_message_and_returns_zero(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Under KeepAlive a non-zero exit here becomes a restart loop fighting
    whichever dashboard is already serving the page."""

    with _bound_port() as port:
        code = run_dashboard(port)

    assert code == 0
    assert f"JobPilot tourne déjà sur http://127.0.0.1:{port}" in capsys.readouterr().out


def test_the_cli_exits_zero_on_a_port_collision() -> None:
    with _bound_port() as port:
        result = CliRunner().invoke(app, ["dashboard", "--port", str(port)])

    assert result.exit_code == 0
    assert "tourne déjà" in result.output


# ----- LaunchAgent install / uninstall -----


@contextmanager
def _fake_launchctl(tmp_path: Path) -> Iterator[tuple[dict[str, str], Path]]:
    """A launchctl stub on PATH that records its calls, so the script can run."""

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "launchctl.d").mkdir()
    stub = bin_dir / "launchctl"
    stub.write_text(
        '#!/bin/sh\necho "$@" >> "$0.d/calls.log"\nexit 0\n', encoding="utf-8"
    )
    stub.chmod(0o755)

    home = tmp_path / "home"
    home.mkdir()
    env = dict(os.environ)
    env["HOME"] = str(home)
    env["PATH"] = f"{bin_dir}{os.pathsep}{env['PATH']}"
    yield env, home


@needs_posix_shell
def test_install_agent_writes_a_keepalive_plist_with_a_resolved_interpreter(
    tmp_path: Path,
) -> None:
    with _fake_launchctl(tmp_path) as (env, home):
        result = subprocess.run(
            ["sh", str(SCRIPTS / "install_agent.sh"), "8788"],
            capture_output=True,
            text=True,
            env=env,
            cwd=ROOT,
        )

    assert result.returncode == 0, result.stderr
    plist = home / "Library" / "LaunchAgents" / "com.jobpilot.dashboard.plist"
    content = plist.read_text(encoding="utf-8")
    assert "<key>RunAtLoad</key>" in content
    assert "<key>KeepAlive</key>" in content
    assert "<string>8788</string>" in content
    # The venv interpreter is resolved at install time, not left as a token.
    assert "__HOME__" not in content
    assert str(ROOT / ".venv") in content
    # stdout and stderr both go to ~/Library/Logs/jobpilot/.
    assert str(home / "Library" / "Logs" / "jobpilot") in content
    assert (home / "Library" / "Logs" / "jobpilot").is_dir()


@needs_posix_shell
def test_install_agent_is_idempotent(tmp_path: Path) -> None:
    """Running it twice leaves one agent, not two."""

    with _fake_launchctl(tmp_path) as (env, home):
        for _ in range(2):
            result = subprocess.run(
                ["sh", str(SCRIPTS / "install_agent.sh")],
                capture_output=True,
                text=True,
                env=env,
                cwd=ROOT,
            )
            assert result.returncode == 0, result.stderr

        agents = sorted((home / "Library" / "LaunchAgents").iterdir())
        calls = (tmp_path / "bin" / "launchctl.d" / "calls.log").read_text(
            encoding="utf-8"
        ).splitlines()

    assert [path.name for path in agents] == ["com.jobpilot.dashboard.plist"]
    # The second run unloads before loading, so launchd picks the new plist up
    # instead of keeping the old ProgramArguments until the next login.
    assert sum(1 for call in calls if call.startswith("load ")) == 2
    assert any(call.startswith("unload ") for call in calls)


@needs_posix_shell
def test_uninstall_agent_removes_it_and_tolerates_being_run_twice(
    tmp_path: Path,
) -> None:
    """An agent you cannot remove is a trap, especially under KeepAlive."""

    with _fake_launchctl(tmp_path) as (env, home):
        subprocess.run(
            ["sh", str(SCRIPTS / "install_agent.sh")], env=env, cwd=ROOT, check=True,
            capture_output=True,
        )
        plist = home / "Library" / "LaunchAgents" / "com.jobpilot.dashboard.plist"
        assert plist.is_file()

        first = subprocess.run(
            ["sh", str(SCRIPTS / "uninstall_agent.sh")],
            capture_output=True, text=True, env=env, cwd=ROOT,
        )
        second = subprocess.run(
            ["sh", str(SCRIPTS / "uninstall_agent.sh")],
            capture_output=True, text=True, env=env, cwd=ROOT,
        )

    assert first.returncode == 0
    assert not plist.exists()
    assert second.returncode == 0
    assert "Aucun agent installé" in second.stdout


# ----- JobPilot.app -----


@needs_posix_shell
def test_make_app_generates_a_bundle_that_only_opens_a_url(tmp_path: Path) -> None:
    """It hosts nothing; it is a bookmark with a Dock icon."""

    result = subprocess.run(
        ["sh", str(SCRIPTS / "make_app.sh"), str(tmp_path), "8787"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )

    assert result.returncode == 0, result.stderr
    bundle = tmp_path / "JobPilot.app"
    info = (bundle / "Contents" / "Info.plist").read_text(encoding="utf-8")
    launcher = bundle / "Contents" / "MacOS" / "JobPilot"
    body = launcher.read_text(encoding="utf-8")

    assert "<string>com.jobpilot.launcher</string>" in info
    assert "<string>JobPilot</string>" in info
    assert os.access(launcher, os.X_OK)
    assert 'exec open "http://127.0.0.1:8787"' in body
    # No Python is bundled. py2app plus torch 2.2.2 on Intel macOS is a
    # multi-day hole for no benefit.
    assert "python" not in body.lower()
    assert not (bundle / "Contents" / "Resources").exists()


@needs_posix_shell
def test_make_app_replaces_a_previous_bundle(tmp_path: Path) -> None:
    for port in ("8787", "9999"):
        subprocess.run(
            ["sh", str(SCRIPTS / "make_app.sh"), str(tmp_path), port],
            check=True, capture_output=True, cwd=ROOT,
        )

    launcher = tmp_path / "JobPilot.app" / "Contents" / "MacOS" / "JobPilot"
    assert "9999" in launcher.read_text(encoding="utf-8")
    assert sorted(p.name for p in tmp_path.iterdir()) == ["JobPilot.app"]


# ----- Windows -----


def test_the_windows_launcher_is_committed_and_port_aware() -> None:
    """Sam needs a double-click too, and it must not be a macOS script."""

    body = (SCRIPTS / "jobpilot-dashboard.bat").read_text(encoding="utf-8")

    assert "@echo off" in body
    assert r".venv\Scripts\python.exe" in body
    assert "dashboard --port" in body


# ----- the rule that keeps Windows CI green -----


def _module_level_imports(path: Path) -> set[str]:
    """Top-level (module scope) imported root module names, ignoring nested ones."""

    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in tree.body:  # module scope only: function-local imports are fine
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.add(node.module.split(".")[0])
    return names


def test_no_module_imports_a_macos_only_package_at_module_level() -> None:
    offenders = {
        path.relative_to(SRC).as_posix(): sorted(
            _module_level_imports(path) & MACOS_ONLY_MODULES
        )
        for path in sorted(SRC.rglob("*.py"))
        if _module_level_imports(path) & MACOS_ONLY_MODULES
    }

    assert offenders == {}


def test_the_whole_package_imports_with_rumps_absent() -> None:
    """Verified, not assumed: import every module in a subprocess where any
    attempt to import rumps raises, and check nothing did."""

    probe = (
        "import importlib, pkgutil, sys\n"
        "import jobpilot\n"
        "for _, name, _ in pkgutil.walk_packages(jobpilot.__path__, 'jobpilot.'):\n"
        "    importlib.import_module(name)\n"
        f"mac = {sorted(MACOS_ONLY_MODULES)!r}\n"
        "print('LEAKED=' + ','.join(sorted(set(mac) & set(sys.modules))))\n"
    )
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    result = subprocess.run(
        [sys.executable, "-c", probe],
        capture_output=True,
        text=True,
        env=env,
        cwd=ROOT,
    )

    assert result.returncode == 0, result.stderr
    assert "LEAKED=" in result.stdout
    assert result.stdout.strip().splitlines()[-1] == "LEAKED="


def test_the_menubar_module_imports_and_refuses_cleanly_off_macos() -> None:
    from jobpilot import menubar

    if sys.platform != "darwin":
        with pytest.raises(menubar.MenubarUnavailable, match="macOS"):
            menubar.run_menubar()


def test_menubar_counts_and_title_read_only_what_they_claim(db) -> None:
    from jobpilot.menubar import counts, title

    company_id = db.execute("INSERT INTO companies (name) VALUES ('Acme')").lastrowid
    for status, kind in (
        ("ready", "offer"),
        ("ready", "offer"),
        ("queued", "offer"),
        ("skipped", "offer"),
        ("ready", "cold"),  # outreach has its own surface; not counted here
    ):
        db.execute(
            "INSERT INTO applications (company_id, kind, status) VALUES (?, ?, ?)",
            (company_id, kind, status),
        )
    db.commit()

    tally = counts(db)

    assert tally == {"ready": 2, "queued": 1}
    assert title(tally) == "JP 2✓ 1·"


def test_rumps_is_an_optional_extra_and_not_a_base_dependency() -> None:
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    base = " ".join(config["project"]["dependencies"])
    extra = config["project"]["optional-dependencies"]["menubar"]

    assert "rumps" not in base
    assert any("rumps" in item for item in extra)
    # Platform-gated so `pip install -e '.[menubar]'` is harmless on Windows.
    assert all("sys_platform == 'darwin'" in item for item in extra)
