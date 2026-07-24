#!/usr/bin/env python3
"""
generate_letter_pdf.py — Generate motivation letter PDF from components.

Rules 91-104: WeasyPrint, A4, margins 18mm/20mm, font 10pt, line-height 1.48.
Header extracted from tailored CV HTML. Clean isolated CSS.

Usage:
    python3 generate_letter_pdf.py \
        --cv <tailored_cv.html> \
        --body <letter_body.html> \
        --output <output.pdf> \
        --company "Company Name" \
        --location "Paris" \
        --date "10 juin 2026"

The body file should contain ONLY the letter paragraphs (no <html>, <head>, etc.).
Example body content:
    <p>Madame, Monsieur,</p>
    <p>Paragraph 1...</p>
    <p>Paragraph 2...</p>
    <p>Cordialement,<br/>Mouaad Sekkouri</p>
"""

import argparse
import html
import re
import sys
from pathlib import Path

from utf8_console import configure_utf8_output

ACCENT_COLOR = "#7bd3e9"

LETTER_CSS = """
@page {{
    size: A4;
    margin: 18mm 20mm 18mm 20mm;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{
    font-family: Arial, sans-serif;
    font-size: 10pt;
    line-height: 1.48;
    color: #1a252f;
    background: #fff;
}}
/* Header styles — matches CV layout exactly */
header {{
    display: flex;
    align-items: center;
    gap: 4mm;
    border-bottom: 2px solid {accent};
    padding-bottom: 1.5mm;
    margin-bottom: 5mm;
}}
.header-text {{
    flex: 1;
    text-align: center;
}}
h1 {{
    font-size: 19pt;
    font-weight: bold;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    color: #1a252f;
    margin-bottom: 1mm;
}}
.job-title {{
    font-size: 12.5pt;
    font-weight: bold;
    color: {accent};
    margin-bottom: 1mm;
}}
.job-subtitle {{
    display: none;
}}
.contact-info {{
    font-size: {contact_size};
    color: #34495e;
    display: block;
    line-height: 1.6;
    text-align: {contact_align};
}}
.contact-info a {{
    color: #34495e;
    text-decoration: none;
}}
.header-photo {{
    width: 28mm;
    height: 28mm;
    flex-shrink: 0;
}}
.header-photo img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 50%;
}}
/* Letter body styles */
.date-block {{
    text-align: right;
    margin: 6mm 0 4mm 0;
    font-size: 10pt;
    color: #34495e;
}}
.company-block {{
    margin-bottom: 6mm;
    font-size: 10pt;
    color: #1a252f;
}}
.company-block strong {{
    color: {accent};
}}
.letter-body p {{
    margin-bottom: 3mm;
    text-align: justify;
}}
"""


def extract_header(cv_html):
    """Extract the <header>...</header> block from the CV HTML."""
    match = re.search(r"<header>(.*?)</header>", cv_html, re.DOTALL)
    if not match:
        print("ERROR: Could not find <header> block in CV HTML", file=sys.stderr)
        sys.exit(1)
    return match.group(1)


def detect_github(cv_html):
    """Check if GitHub is present to determine contact format."""
    return "github.com/MouaadSek" in cv_html


def build_letter_html(header_content, body_content, company, location, date_str, has_github):
    """Build complete letter HTML with isolated CSS."""
    escaped_company = html.escape(company)
    escaped_location = html.escape(location)
    escaped_date = html.escape(date_str)

    # Unknown company: omit the addressee line entirely, keep the city if known.
    company_line = f"<strong>{escaped_company}</strong><br/>\n        " if company.strip() else ""

    contact_align = "center" if has_github else "left"
    contact_size = "9.2pt" if has_github else "8.5pt"

    css = LETTER_CSS.format(
        accent=ACCENT_COLOR,
        contact_align=contact_align,
        contact_size=contact_size,
    )

    # Replace any remaining #2980b9 in the header content
    header_content = header_content.replace("#2980b9", ACCENT_COLOR)

    document_html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8"/>
    <style>
{css}
    </style>
</head>
<body>
    <header>
{header_content}
    </header>

    <div class="date-block">{escaped_date}</div>

    <div class="company-block">
        {company_line}{escaped_location}
    </div>

    <div class="letter-body">
{body_content}
    </div>
</body>
</html>"""
    return document_html


def generate_pdf_with_playwright(html_content, output_path):
    """Render with Chromium when WeasyPrint's native libraries are unavailable."""

    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.set_content(html_content, wait_until="networkidle")
        page.emulate_media(media="print")
        page.pdf(
            path=str(output_path),
            format="A4",
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            prefer_css_page_size=True,
        )
        browser.close()


def generate_pdf(html_content, output_path):
    """Generate PDF with WeasyPrint, or Chromium when native libraries are absent."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    if sys.platform == "win32":
        generate_pdf_with_playwright(html_content, output)
        return

    try:
        from weasyprint import HTML
    except (ImportError, OSError) as exc:
        print(
            f"WARNING: WeasyPrint unavailable ({exc}); using Playwright.",
            file=sys.stderr,
        )
        generate_pdf_with_playwright(html_content, output)
        return

    HTML(string=html_content).write_pdf(str(output))


def verify_pages(pdf_path, expected=1):
    """Verify page count."""
    try:
        from pypdf import PdfReader
    except ImportError:
        from PyPDF2 import PdfReader
    reader = PdfReader(pdf_path)
    count = len(reader.pages)
    if count != expected:
        print(f"⚠️  WARNING: Letter is {count} page(s), expected {expected}", file=sys.stderr)
        return False
    return True


def main():
    configure_utf8_output()
    parser = argparse.ArgumentParser(description="Generate motivation letter PDF")
    parser.add_argument("--cv", required=True, help="Path to tailored CV HTML")
    parser.add_argument("--body", required=True, help="Path to letter body HTML file")
    parser.add_argument("--output", required=True, help="Output PDF path")
    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument("--location", required=True, help="Company location")
    parser.add_argument("--date", required=True, help='Date string (e.g. "10 juin 2026")')
    args = parser.parse_args()

    cv_html = Path(args.cv).read_text(encoding="utf-8")
    body_html = Path(args.body).read_text(encoding="utf-8")
    if "\u2014" in html.unescape(body_html):
        print(
            "ERROR: Motivation letter contains an em dash; use a hyphen or en dash.",
            file=sys.stderr,
        )
        sys.exit(1)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    header_content = extract_header(cv_html)
    has_github = detect_github(cv_html)

    letter_html = build_letter_html(
        header_content, body_html, args.company, args.location, args.date, has_github
    )

    # Save intermediate HTML for debugging
    html_path = output_path.with_suffix(".html")
    html_path.write_text(letter_html, encoding="utf-8")
    print(f"Letter HTML saved: {html_path}")

    generate_pdf(letter_html, output_path)
    print(f"Letter PDF generated: {output_path}")

    if verify_pages(output_path):
        print("✅ Page count: 1 — OK")
    else:
        print("❌ Page count check failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
