#!/usr/bin/env python3
"""
check_orphan_lines.py - Detect orphan lines in CV HTML templates.

An orphan line is a paragraph/list-item whose last rendered line fills less than
35% of the available width. Uses Playwright/Chromium for accurate rendering.

Usage:
    python3 check_orphan_lines.py <html_file>

Exit codes:
    0 - No orphan lines detected
    1 - Orphan lines detected (prints details)

Requires: python -m pip install playwright
          python -m playwright install chromium
"""

import argparse
import sys
from pathlib import Path

from utf8_console import configure_utf8_output


def check_orphans(html_path: Path | str, threshold: float = 0.35) -> list[dict[str, object]]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "ERROR: playwright not installed. Run: python -m pip install playwright "
            "then python -m playwright install chromium"
        )
        sys.exit(2)

    orphans = []
    html_url = Path(html_path).resolve().as_uri()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_viewport_size({"width": 794, "height": 1123})  # A4 at 96dpi
        page.goto(html_url)
        page.wait_for_load_state("networkidle")

        # Check li, .project-desc, .profile elements
        selectors = ["li", ".project-desc", ".profile"]
        for selector in selectors:
            elements = page.query_selector_all(selector)
            for i, el in enumerate(elements):
                result = el.evaluate("""(el) => {
                    const range = document.createRange();
                    range.selectNodeContents(el);
                    const fragments = Array.from(range.getClientRects())
                        .filter((rect) => rect.width > 0 && rect.height > 0)
                        .sort((a, b) => a.top - b.top || a.left - b.left);
                    const lines = [];
                    for (const rect of fragments) {
                        let line = lines.find(
                            (candidate) => Math.abs(candidate.top - rect.top) < 1
                        );
                        if (line === undefined) {
                            line = {
                                top: rect.top,
                                left: rect.left,
                                right: rect.right
                            };
                            lines.push(line);
                        } else {
                            line.left = Math.min(line.left, rect.left);
                            line.right = Math.max(line.right, rect.right);
                        }
                    }
                    if (lines.length < 2) return null;
                    lines.sort((a, b) => a.top - b.top);
                    const lastLine = lines[lines.length - 1];
                    const containerWidth = el.getBoundingClientRect().width;
                    if (containerWidth === 0) return null;
                    const lastLineWidth = lastLine.right - lastLine.left;
                    return {
                        lines: lines.length,
                        lastLineWidth: lastLineWidth,
                        containerWidth: containerWidth,
                        ratio: lastLineWidth / containerWidth,
                        text: el.textContent.substring(0, 80)
                    };
                }""")

                if result and result["ratio"] < threshold:
                    orphans.append(
                        {
                            "selector": selector,
                            "index": i,
                            "lines": result["lines"],
                            "ratio": round(result["ratio"], 3),
                            "text": result["text"].strip(),
                        }
                    )

        browser.close()

    return orphans


def find_regressions(
    tailored: list[dict[str, object]],
    baseline: list[dict[str, object]],
    *,
    tolerance: float = 0.02,
) -> list[dict[str, object]]:
    """Return orphan metrics that are new or materially worse than the template."""

    regressions: list[dict[str, object]] = []
    selectors = {str(item["selector"]) for item in tailored}
    for selector in selectors:
        current = sorted(
            (item for item in tailored if item["selector"] == selector),
            key=lambda item: float(item["ratio"]),
        )
        original = sorted(
            (item for item in baseline if item["selector"] == selector),
            key=lambda item: float(item["ratio"]),
        )
        for index, item in enumerate(current):
            if index >= len(original):
                regressions.append(item)
                continue
            if float(item["ratio"]) + tolerance < float(original[index]["ratio"]):
                regressions.append(item)
    return regressions


if __name__ == "__main__":
    configure_utf8_output()
    parser = argparse.ArgumentParser(description="Detect rendered orphan-line regressions")
    parser.add_argument("html_file", type=Path)
    parser.add_argument(
        "--original",
        type=Path,
        help="Base template; when set, fail only for new or worsened orphans.",
    )
    args = parser.parse_args()

    html_path = args.html_file.resolve()
    if not html_path.exists():
        print(f"ERROR: File not found: {html_path}")
        sys.exit(2)

    orphans = check_orphans(html_path)
    baseline = []
    if args.original is not None:
        original_path = args.original.resolve()
        if not original_path.exists():
            print(f"ERROR: File not found: {original_path}")
            sys.exit(2)
        baseline = check_orphans(original_path)
        orphans = find_regressions(orphans, baseline)

    if orphans:
        label = "ORPHAN REGRESSIONS" if args.original is not None else "ORPHAN LINES DETECTED"
        print(f"{label}: {len(orphans)}")
        for o in orphans:
            print(
                f"  [{o['selector']}#{o['index']}] {o['lines']} lines, "
                f"last={o['ratio'] * 100:.1f}% width"
            )
            print(f'    "{o["text"]}..."')
        sys.exit(1)
    else:
        if args.original is None:
            print("OK: No orphan lines detected")
        else:
            print(f"OK: No new or worsened orphan lines (baseline had {len(baseline)})")
        sys.exit(0)
