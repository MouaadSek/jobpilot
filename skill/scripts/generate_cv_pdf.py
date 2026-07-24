#!/usr/bin/env python3
"""
generate_cv_pdf.py — Generate CV PDF from tailored HTML using Playwright.

Rules 85-87: Chromium, A4, print_background=True, all margins=0, exactly 1 page.

Usage:
    python3 generate_cv_pdf.py <html_path> <output_pdf_path>
"""

import sys
import argparse
import asyncio
from pathlib import Path


async def generate(html_path, output_path):
    from playwright.async_api import async_playwright

    html_abs = str(Path(html_path).resolve())
    file_url = f'file://{html_abs}'

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(file_url, wait_until='networkidle')
        await page.pdf(
            path=output_path,
            format='A4',
            print_background=True,
            margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'}
        )
        await browser.close()

    print(f"PDF generated: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Generate CV PDF with Playwright')
    parser.add_argument('html_path', help='Path to tailored CV HTML')
    parser.add_argument('output_path', help='Output PDF path')
    args = parser.parse_args()

    asyncio.run(generate(args.html_path, args.output_path))


if __name__ == '__main__':
    main()
