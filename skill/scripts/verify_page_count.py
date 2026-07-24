#!/usr/bin/env python3
"""
verify_page_count.py — Verify PDF is exactly 1 page.

Rules 87, 97: CV and motivation letter must be exactly 1 page.

Usage:
    python3 verify_page_count.py <pdf_path>
"""

import sys
import argparse


def main():
    parser = argparse.ArgumentParser(description='Verify PDF page count')
    parser.add_argument('pdf_path', help='Path to PDF file')
    parser.add_argument('--expected', type=int, default=1, help='Expected page count (default: 1)')
    args = parser.parse_args()

    try:
        from pypdf import PdfReader
    except ImportError:
        from PyPDF2 import PdfReader

    reader = PdfReader(args.pdf_path)
    count = len(reader.pages)

    if count == args.expected:
        print(f"✅ PAGE COUNT: {count} page(s) — OK")
        sys.exit(0)
    else:
        print(f"❌ PAGE COUNT: {count} page(s) — expected {args.expected}")
        sys.exit(1)


if __name__ == '__main__':
    main()
