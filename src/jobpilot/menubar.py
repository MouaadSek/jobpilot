"""Optional macOS menu bar item: ready / queued counts, click to open.

``rumps`` is a macOS-only dependency and lives in the ``menubar`` optional
extra, never in the base requirements. Nothing here imports it at module level:
this module must be importable on Windows and on Linux CI with rumps absent, and
a test asserts exactly that. The import happens inside ``run_menubar`` and a
missing package is a clear message, not a traceback.
"""

from __future__ import annotations

import sqlite3
import sys
import webbrowser
from typing import Any

from jobpilot.db import connect
from jobpilot.logging_conf import get_logger

log = get_logger("menubar")

#: How often the item re-reads the counts, in seconds.
REFRESH_SECONDS = 60


class MenubarUnavailable(RuntimeError):
    """Raised when the menu bar item cannot run on this machine."""


def counts(db: sqlite3.Connection) -> dict[str, int]:
    """Ready and queued offer applications, the two numbers worth a glance."""

    rows = db.execute(
        "SELECT status, count(*) AS n FROM applications "
        "WHERE kind = 'offer' AND status IN ('ready', 'queued') GROUP BY status"
    ).fetchall()
    tally = {row["status"]: int(row["n"]) for row in rows}
    return {"ready": tally.get("ready", 0), "queued": tally.get("queued", 0)}


def title(tally: dict[str, int]) -> str:
    """The menu bar text. Short: it competes with every other item up there."""

    return f"JP {tally['ready']}✓ {tally['queued']}·"


def _require_rumps() -> Any:
    """Import rumps or explain, in French, exactly how to get it."""

    if sys.platform != "darwin":
        raise MenubarUnavailable(
            "Le menu bar est spécifique à macOS. Sur Windows, utilisez "
            "scripts\\jobpilot-dashboard.bat."
        )
    try:
        import rumps  # noqa: PLC0415 - macOS-only optional extra, never top level
    except ImportError as exc:
        raise MenubarUnavailable(
            "rumps n'est pas installé. Installez l'extra optionnel : "
            "pip install -e '.[menubar]'"
        ) from exc
    return rumps


def run_menubar(*, port: int = 8787) -> None:
    """Run the menu bar item until quit. Blocks; opens the dashboard on click."""

    rumps = _require_rumps()
    url = f"http://127.0.0.1:{port}"

    class JobPilotStatus(rumps.App):  # type: ignore[misc, name-defined]
        def __init__(self) -> None:
            super().__init__("JobPilot", quit_button="Quitter")
            self.menu = ["Ouvrir le tableau de bord"]
            self.refresh(None)

        @rumps.clicked("Ouvrir le tableau de bord")  # type: ignore[misc]
        def open_dashboard(self, _: object) -> None:
            webbrowser.open(url)

        @rumps.timer(REFRESH_SECONDS)  # type: ignore[misc]
        def refresh(self, _: object) -> None:
            try:
                connection = connect()
                try:
                    self.title = title(counts(connection))
                finally:
                    connection.close()
            except Exception as exc:  # a dead menu bar must not be a mystery
                log.warning("menubar refresh failed: %s", exc)
                self.title = "JP ?"

    JobPilotStatus().run()
