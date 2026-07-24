#!/usr/bin/env python3
"""
validate_cv.py — Pre-PDF validation for tailored CV HTML files.

Checks all constraints from the rule inventory before PDF generation.
Returns exit code 0 if all checks pass, 1 if any fail.

Usage:
    python3 validate_cv.py <path_to_tailored_cv.html> [--original <path_to_base_cv.html>]
"""

import sys
import re
import argparse
import html


def strip_html_tags(text):
    """Remove HTML tags but keep text content."""
    return re.sub(r'<[^>]+>', '', text).strip()


def decode_entities(text):
    """Decode HTML entities like &amp; &eacute; etc."""
    return html.unescape(text)


def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def check_profil(content, original_content=None):
    """Rule 41-43: Profil should match base template length ±15 chars."""
    match = re.search(r'<section class="profile">\s*(.*?)\s*</section>', content, re.DOTALL)
    if not match:
        return False, "PROFIL: Section not found"
    raw = match.group(1).strip()
    text = strip_html_tags(raw)
    text = decode_entities(text)
    length = len(text)

    if original_content:
        orig_match = re.search(r'<section class="profile">\s*(.*?)\s*</section>', original_content, re.DOTALL)
        if orig_match:
            orig_text = decode_entities(strip_html_tags(orig_match.group(1).strip()))
            orig_len = len(orig_text)
            diff = length - orig_len
            if diff > 15:
                return False, f"PROFIL: {length} chars (base: {orig_len}, +{diff}) — OVER base by more than 15"
            elif diff < -15:
                return False, f"PROFIL: {length} chars (base: {orig_len}, {diff}) — UNDER base by more than 15"
            return True, f"PROFIL: {length} chars (base: {orig_len}, diff: {diff:+d}) — OK"

    # No original to compare — fallback to soft 350 ceiling
    if length > 350:
        return False, f"PROFIL: {length} chars — exceeds safety ceiling of 350"
    return True, f"PROFIL: {length} chars — OK (no base to compare)"


def check_project_descs(content):
    """Rules 49-52: Each project-desc ~130-134 chars (excl. HTML tags)."""
    descs = re.findall(r'<div class="project-desc">(.*?)</div>', content, re.DOTALL)
    if len(descs) == 0:
        return False, "PROJECTS: No project-desc found"
    results = []
    all_ok = True
    for i, desc in enumerate(descs, 1):
        text = strip_html_tags(desc.strip())
        text = decode_entities(text)
        length = len(text)
        if length > 134:
            results.append(f"  Project {i}: {length} chars — OVER by {length - 134}")
            all_ok = False
        elif length < 130:
            results.append(f"  Project {i}: {length} chars — SHORT (target 130-134)")
            all_ok = False
        else:
            results.append(f"  Project {i}: {length} chars — OK")
    header = "PROJECT-DESC: " + ("ALL OK" if all_ok else "ISSUES FOUND")
    return all_ok, header + "\n" + "\n".join(results)


def check_project_count(content):
    """Rule 48: Exactly 3 projects."""
    count = len(re.findall(r'<div class="project-item">', content))
    if count != 3:
        return False, f"PROJECT-COUNT: {count} projects (expected 3)"
    return True, f"PROJECT-COUNT: {count} — OK"


def check_projects_title(content):
    """Rule 53: Section title must be exactly 'Projets Personnels'."""
    # Handle both plain text and HTML-entity versions
    h2_tags = re.findall(r'<h2>(.*?)</h2>', content)
    for h2 in h2_tags:
        decoded = decode_entities(h2)
        if 'Projet' in decoded or 'projet' in decoded:
            if decoded.strip() == 'Projets Personnels':
                return True, "PROJECTS-TITLE: 'Projets Personnels' — OK"
            else:
                return False, f"PROJECTS-TITLE: '{decoded.strip()}' — should be 'Projets Personnels'"
    return False, "PROJECTS-TITLE: No projects section title found"


def check_accent_color(content):
    """Rules 55-59: Must be #7bd3e9, not #2980b9."""
    old_count = content.count('#2980b9')
    new_count = content.count('#7bd3e9')
    if old_count > 0:
        return False, f"COLOR: #2980b9 still present ({old_count} occurrences) — swap not applied"
    if new_count == 0:
        return False, "COLOR: #7bd3e9 not found — unexpected"
    return True, f"COLOR: #7bd3e9 present ({new_count} occurrences), #2980b9 absent — OK"


def check_english_level(content):
    """Rules 61-62: Must be C1 Courant, never C2."""
    if 'C2 Courant' in content or 'C2&nbsp;Courant' in content:
        return False, "ENGLISH: 'C2 Courant' found — must be 'C1 Courant'"
    if 'C1 Courant' in content or 'C1&nbsp;Courant' in content:
        return True, "ENGLISH: C1 Courant — OK"
    return False, "ENGLISH: Neither C1 nor C2 found — check languages line"


def check_languages_line(content):
    """Rule 60: Fixed language line content."""
    expected_parts = ['Bilingue', 'C1 Courant', 'Langue maternelle', 'A2']
    # Also accept HTML-entity versions
    decoded = decode_entities(content)
    all_found = all(part in decoded for part in expected_parts)
    if not all_found:
        missing = [p for p in expected_parts if p not in decoded]
        return False, f"LANGUAGES: Missing parts: {missing}"
    return True, "LANGUAGES: All expected parts present — OK"


def check_em_dashes(content):
    """Rule 63: No em dashes."""
    if '\u2014' in content:
        count = content.count('\u2014')
        return False, f"DASHES: {count} em dash(es) found — use '-' or '–' only"
    return True, "DASHES: No em dashes — OK"


def check_github_removed(content):
    """Rules 64-70: GitHub removed by default (unless DevSecOps/DevOps)."""
    has_github = 'github.com/MouaadSek' in content
    # Check if this looks like a DevSecOps/DevOps CV
    title_match = re.search(r'<div class="job-title">(.*?)</div>', content)
    is_devops = False
    if title_match:
        title = decode_entities(strip_html_tags(title_match.group(1))).lower()
        is_devops = 'devsecops' in title or 'devops' in title
    if has_github and not is_devops:
        return False, "GITHUB: Still present — should be removed (not DevSecOps/DevOps)"
    if has_github and is_devops:
        return True, "GITHUB: Present — OK (DevSecOps/DevOps role)"
    if not has_github:
        return True, "GITHUB: Removed — OK"
    return True, "GITHUB: OK"


def check_contact_format(content):
    """Rules 68-69: Contact block format depends on GitHub presence."""
    has_github = 'github.com/MouaadSek' in content
    if has_github:
        # Should be 9.2pt, centered, two lines
        if '9.2pt' not in content:
            return False, "CONTACT: GitHub present but font-size not 9.2pt"
        return True, "CONTACT: GitHub present, 9.2pt — OK"
    else:
        # Should be 8.5pt, contact left-aligned, but header-text stays centered
        if '8.5pt' not in content:
            return False, "CONTACT: GitHub removed but font-size not 8.5pt"
        # Verify header-text is still centered (not changed to left)
        header_match = re.search(r'\.header-text\s*\{[^}]*text-align:\s*(\w+)', content)
        if header_match and header_match.group(1) == 'left':
            return False, "CONTACT: .header-text was changed to left — must stay center"
        return True, "CONTACT: GitHub removed, 8.5pt, header centered — OK"


def check_stage_subtitle(content):
    """Rules 74-77: Stage CVs must not have 'Démarrage anticipé' subtitle."""
    title_match = re.search(r'<div class="job-title">(.*?)</div>', content)
    is_stage = False
    if title_match:
        title = decode_entities(strip_html_tags(title_match.group(1))).lower()
        is_stage = 'stage' in title
    has_subtitle = ('marrage anticip' in content or 
                    'marrage anticip' in decode_entities(content))
    if is_stage and has_subtitle:
        return False, "STAGE-SUBTITLE: 'Démarrage anticipé' still present on stage CV"
    if not is_stage and has_subtitle:
        return True, "STAGE-SUBTITLE: Present on alternance CV — OK"
    if is_stage and not has_subtitle:
        return True, "STAGE-SUBTITLE: Absent on stage CV — OK"
    return True, "STAGE-SUBTITLE: OK"


def check_line_count(content, original_content=None):
    """Rule 78: Line count should match original."""
    lines = content.count('\n') + 1
    if original_content:
        orig_lines = original_content.count('\n') + 1
        if lines != orig_lines:
            return False, f"LINE-COUNT: {lines} lines (original: {orig_lines}) — MISMATCH"
        return True, f"LINE-COUNT: {lines} lines — matches original"
    return True, f"LINE-COUNT: {lines} lines (no original to compare)"


def check_localisation(content):
    """Rule 54: Region only, not city + region."""
    # Check the contact-info for location patterns
    contact = re.search(r'<div class="contact-info">(.*?)</div>', content, re.DOTALL)
    if not contact:
        return True, "LOCALISATION: Contact block not found — skipping"
    text = decode_entities(contact.group(1))
    # Common city+region patterns to flag
    if re.search(r'Lille\s*/\s*Île-de-France', text):
        return True, "LOCALISATION: OK (multi-region)"
    # This is informational — hard to validate automatically
    return True, "LOCALISATION: Present — manual review recommended"


def main():
    parser = argparse.ArgumentParser(description='Validate tailored CV HTML')
    parser.add_argument('cv_path', help='Path to tailored CV HTML')
    parser.add_argument('--original', help='Path to original base CV for line count comparison')
    args = parser.parse_args()

    content = read_file(args.cv_path)
    original = read_file(args.original) if args.original else None

    checks = [
        check_profil(content, original),
        check_project_count(content),
        check_project_descs(content),
        check_projects_title(content),
        check_accent_color(content),
        check_english_level(content),
        check_languages_line(content),
        check_em_dashes(content),
        check_github_removed(content),
        check_contact_format(content),
        check_stage_subtitle(content),
        check_line_count(content, original),
        check_localisation(content),
    ]

    print(f"{'=' * 60}")
    print(f"CV VALIDATION: {args.cv_path}")
    print(f"{'=' * 60}")

    passed = 0
    failed = 0
    for ok, msg in checks:
        status = "✅" if ok else "❌"
        print(f"{status} {msg}")
        if ok:
            passed += 1
        else:
            failed += 1

    print(f"{'=' * 60}")
    print(f"RESULT: {passed} passed, {failed} failed")
    print(f"{'=' * 60}")

    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()
