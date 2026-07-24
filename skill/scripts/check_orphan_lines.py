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

Requires: pip install playwright --break-system-packages
          python3 -m playwright install chromium
"""
import sys
import json

def check_orphans(html_path, threshold=0.35):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR: playwright not installed. Run: pip install playwright --break-system-packages && python3 -m playwright install chromium")
        sys.exit(2)

    orphans = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_viewport_size({"width": 794, "height": 1123})  # A4 at 96dpi
        page.goto(f"file://{html_path}")
        page.wait_for_load_state("networkidle")

        # Check li, .project-desc, .profile elements
        selectors = ["li", ".project-desc", ".profile"]
        for selector in selectors:
            elements = page.query_selector_all(selector)
            for i, el in enumerate(elements):
                result = el.evaluate("""(el) => {
                    const range = document.createRange();
                    range.selectNodeContents(el);
                    const rects = range.getClientRects();
                    if (rects.length < 2) return null;
                    const lastRect = rects[rects.length - 1];
                    const firstRect = rects[0];
                    const containerWidth = el.getBoundingClientRect().width;
                    if (containerWidth === 0) return null;
                    return {
                        lines: rects.length,
                        lastLineWidth: lastRect.width,
                        containerWidth: containerWidth,
                        ratio: lastRect.width / containerWidth,
                        text: el.textContent.substring(0, 80)
                    };
                }""")

                if result and result["ratio"] < threshold:
                    orphans.append({
                        "selector": selector,
                        "index": i,
                        "lines": result["lines"],
                        "ratio": round(result["ratio"], 3),
                        "text": result["text"].strip()
                    })

        browser.close()

    return orphans


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <html_file>")
        sys.exit(2)

    import os
    html_path = os.path.abspath(sys.argv[1])
    if not os.path.exists(html_path):
        print(f"ERROR: File not found: {html_path}")
        sys.exit(2)

    orphans = check_orphans(html_path)

    if orphans:
        print(f"ORPHAN LINES DETECTED: {len(orphans)}")
        for o in orphans:
            print(f"  [{o['selector']}#{o['index']}] {o['lines']} lines, last={o['ratio']*100:.1f}% width")
            print(f"    \"{o['text']}...\"")
        sys.exit(1)
    else:
        print("OK: No orphan lines detected")
        sys.exit(0)
