"""Put text on the system clipboard, or say plainly that it could not.

The manual_open route hands the human a browser tab and the letter; a clipboard
that silently does nothing turns that into a browser tab and a puzzle. Every
platform tool here is invoked with ``shell=False`` and an explicit argv, and a
missing tool is a logged False rather than an exception: failing to copy must
never abort an apply that already opened the offer.
"""

from __future__ import annotations

import subprocess
import sys

from jobpilot.logging_conf import get_logger

log = get_logger("clipboard")

#: argv per platform. Linux is best-effort; CI runs headless and copies nothing.
_COMMANDS: dict[str, tuple[str, ...]] = {
    "darwin": ("pbcopy",),
    "win32": ("clip",),
    "linux": ("xclip", "-selection", "clipboard"),
}


def copy_text(text: str, *, platform: str | None = None) -> bool:
    """Copy ``text``; return whether it actually landed on the clipboard."""

    command = _COMMANDS.get(platform or sys.platform)
    if command is None:
        log.info("no clipboard command known for platform %s", platform or sys.platform)
        return False
    try:
        completed = subprocess.run(  # noqa: S603 - fixed argv, shell=False
            command,
            input=text.encode("utf-8"),
            shell=False,
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        log.warning("clipboard copy via %s failed: %s", command[0], exc)
        return False
    if completed.returncode != 0:
        log.warning(
            "clipboard copy via %s exited %d", command[0], completed.returncode
        )
        return False
    return True
