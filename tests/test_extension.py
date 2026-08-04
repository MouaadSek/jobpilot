"""Task 43 item 2: the browser extension, and the line it must not cross.

The extension reads the posting the user is already looking at and sends it to
the JobPilot on this machine. Two properties matter more than the feature does:

**It has no autonomy.** No background service worker, no scheduled work, no
navigation, no fetching of any page. It reacts to a page the user opened and
looks at nothing else. That is what keeps constitution rule 11 intact — see
CLAUDE.md, "Scope of rule 11". Most of this file exists to hold that line.

**It is invisible when JobPilot is off.** Which is most of the time. A failed
request must produce no toast and no output of its own.

The selectors will rot; the tests are written so that rot shows up as a failed
capture on one site, never as a broken extension.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from jobpilot.dashboard import IMPORT_ALLOWED_ORIGIN_HOSTS, IMPORT_PATH
from jobpilot.offer_import import MIN_IMPORTED_DESCRIPTION_CHARS

ROOT = Path(__file__).resolve().parents[1]
EXTENSION = ROOT / "extension"
HARNESS = Path(__file__).resolve().parent / "extension_harness.js"

MANIFEST = json.loads((EXTENSION / "manifest.json").read_text(encoding="utf-8"))
CONTENT = (EXTENSION / "content.js").read_text(encoding="utf-8")

needs_node = pytest.mark.skipif(
    shutil.which("node") is None,
    reason="node is not installed; the extension's JS is exercised where it is",
)


def _run_case(case: str, hostname: str = "www.linkedin.com") -> dict:
    result = subprocess.run(
        [shutil.which("node") or "node", str(HARNESS), case, hostname],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


# ---------------------------------------------------------------------------
# No autonomy
# ---------------------------------------------------------------------------


def test_there_is_no_background_script() -> None:
    """A service worker runs when no page is open, which is the whole
    difference between reacting to the user and acting on your own."""

    assert "background" not in MANIFEST
    assert "service_worker" not in CONTENT


def test_the_extension_asks_for_nothing_but_the_three_job_sites() -> None:
    hosts = {
        pattern.split("://", 1)[1].split("/", 1)[0].removeprefix("*.")
        for pattern in MANIFEST["host_permissions"]
    }

    assert hosts == {"linkedin.com", "indeed.fr", "welcometothejungle.com"}
    # No tabs, no scripting, no storage, no alarms: an extension that cannot
    # open a tab cannot navigate, whatever its code says.
    assert "permissions" not in MANIFEST
    assert "optional_permissions" not in MANIFEST


def test_nothing_in_the_content_script_can_navigate_or_fetch_a_page() -> None:
    """The one fetch it makes goes to JobPilot on this machine, carrying text
    the user was already reading. It never requests a page."""

    forbidden = (
        "window.open",
        "location.assign",
        "location.replace",
        "location.href =",
        "chrome.tabs",
        "XMLHttpRequest",
        "document.write",
    )
    for pattern in forbidden:
        assert pattern not in CONTENT, pattern

    fetches = re.findall(r"fetch\(([^,)]+)", CONTENT)

    assert fetches == ["ENDPOINT"]


def test_it_only_ever_talks_to_the_local_dashboard() -> None:
    endpoint = re.search(r'const ENDPOINT = "([^"]+)"', CONTENT).group(1)

    assert endpoint == f"http://127.0.0.1:8787{IMPORT_PATH}"


def test_the_manifest_matches_the_server_origin_allowlist() -> None:
    """Two files naming the same three sites. A content script runs in the
    page's origin, so a site missing from the server allowlist is a site the
    extension silently cannot import from."""

    hosts = {
        pattern.split("://", 1)[1].split("/", 1)[0].removeprefix("*.")
        for pattern in MANIFEST["host_permissions"]
    }

    assert hosts <= IMPORT_ALLOWED_ORIGIN_HOSTS


# ---------------------------------------------------------------------------
# Silent when JobPilot is off
# ---------------------------------------------------------------------------


def test_the_content_script_never_writes_to_the_console() -> None:
    """Most of the time JobPilot is not running. The extension has to be
    invisible then, and a console line on every job page is not invisible."""

    assert not re.search(r"\bconsole\s*\.", CONTENT)


def test_every_failure_path_is_swallowed() -> None:
    """A rejected promise with no catch surfaces as an unhandled rejection,
    which is exactly the noise this must not make."""

    assert ".catch(" in CONTENT
    # The toast is the only user-visible output and it is on the success path.
    toast_calls = CONTENT.count("toast(")
    assert toast_calls >= 2  # the definition plus at least one call
    assert "toast(" not in CONTENT.split(".catch(")[-1]


# ---------------------------------------------------------------------------
# Extraction: selectors rot, the fallback does not
# ---------------------------------------------------------------------------


def test_the_selector_table_covers_the_three_sites_and_says_it_will_rot() -> None:
    """One obvious place, with the warning next to it."""

    table = re.search(r"const SELECTORS = \{(.*?)\n  \};", CONTENT, re.DOTALL).group(1)

    assert '"linkedin.com"' in table
    assert '"indeed.fr"' in table
    assert '"welcometothejungle.com"' in table
    assert "ROTS" in CONTENT


def test_the_minimum_length_agrees_with_the_server() -> None:
    minimum = int(re.search(r"const MIN_CHARS = (\d+)", CONTENT).group(1))

    assert minimum == MIN_IMPORTED_DESCRIPTION_CHARS


@needs_node
def test_a_matching_selector_is_used(tmp_path: Path) -> None:
    verdict = _run_case("selector_hit")

    assert verdict["host_key"] == "linkedin.com"
    assert verdict["described"] == "A" * 400
    assert verdict["domains"] == ["linkedin.com", "indeed.fr", "welcometothejungle.com"]


@needs_node
def test_a_rotted_selector_falls_through_to_the_text_block_heuristic() -> None:
    """The requirement that matters most in a year: when LinkedIn changes its
    generated class names, capture degrades rather than stopping."""

    verdict = _run_case("selector_rotted")

    assert verdict["described"] == "P" * 600
    assert verdict["described"] == verdict["fallback"]


@needs_node
def test_the_heuristic_picks_the_posting_and_not_the_navigation() -> None:
    verdict = _run_case("selector_rotted")

    assert "N" not in verdict["described"]
    assert "F" not in verdict["described"]


@needs_node
def test_the_heuristic_descends_to_the_tightest_wrapper() -> None:
    """The biggest element on a page is a wrapper holding the whole page."""

    verdict = _run_case("nested_wrappers")

    assert verdict["fallback"] == "T" * 800


@needs_node
def test_a_page_with_nothing_to_capture_yields_nothing() -> None:
    """Sending the navigation bar would replace a real description with chrome.
    The server would refuse it, but it should never be sent."""

    verdict = _run_case("nothing_to_find")

    assert verdict["described"] == ""


@needs_node
def test_an_unknown_host_is_not_captured_from() -> None:
    verdict = _run_case("selector_hit", hostname="example.test")

    assert verdict["host_key"] is None
    assert verdict["described"] == ""


@needs_node
def test_a_subdomain_of_a_matched_site_still_matches() -> None:
    """fr.indeed.com and www.linkedin.com are the normal cases."""

    verdict = _run_case("selector_hit", hostname="www.linkedin.com")

    assert verdict["host_key"] == "linkedin.com"


# ---------------------------------------------------------------------------
# Packaging
# ---------------------------------------------------------------------------


def test_the_extension_is_loadable_unpacked_and_nothing_more() -> None:
    """Not published, not submitted anywhere: two files and a README section."""

    assert MANIFEST["manifest_version"] == 3
    assert sorted(path.name for path in EXTENSION.iterdir()) == [
        "content.js",
        "manifest.json",
    ]


def test_the_readme_documents_the_install() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "chrome://extensions" in readme
    assert "Load unpacked" in readme or "Charger l'extension non empaquetée" in readme


@pytest.mark.skipif(sys.platform == "win32", reason="path separators differ")
def test_the_manifest_is_valid_json_with_no_trailing_comma() -> None:
    """Chrome refuses the whole extension on a malformed manifest, with an
    error the user only sees if they look."""

    assert MANIFEST["name"]
    assert MANIFEST["version"]
    assert MANIFEST["content_scripts"][0]["js"] == ["content.js"]
