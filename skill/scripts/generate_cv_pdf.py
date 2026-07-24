#!/usr/bin/env python3
"""Generate a one-page A4 CV PDF from tailored HTML with Playwright.

Usage:
    python3 generate_cv_pdf.py <html_path> <output_pdf_path>
"""

import argparse
import asyncio
import sys
from pathlib import Path


def configure_utf8_output():
    """Use UTF-8 for CLI output, including on Windows consoles."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


async def generate(html_path, output_path):
    """Render the HTML with Chromium using the skill's fixed PDF settings."""
    from playwright.async_api import async_playwright

    file_url = Path(html_path).resolve().as_uri()
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page()
        await page.goto(file_url, wait_until="networkidle")
        await page.pdf(
            path=str(output),
            format="A4",
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        )
        await browser.close()

    print(f"PDF generated: {output}")


def main():
    configure_utf8_output()
    parser = argparse.ArgumentParser(description="Generate CV PDF with Playwright")
    parser.add_argument("html_path", help="Path to tailored CV HTML")
    parser.add_argument("output_path", help="Output PDF path")
    args = parser.parse_args()

    asyncio.run(generate(args.html_path, args.output_path))


if __name__ == "__main__":
    main()
