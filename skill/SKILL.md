---
name: job-application
description: >
  Mouaad Sekkouri's job application pipeline. Generates a tailored CV PDF,
  motivation letter PDF, tracker row, and token count from a pasted job offer.
  Triggers on job descriptions, "candidature", "postuler", "apply", "CV for this
  offer", or any request to tailor a CV to a job posting. Handles alternance
  (12-month) and stage (3-6 month) applications for IT/cybersecurity roles in France.
  Do NOT use for general CV advice, career coaching, or non-application tasks.
---

# Job Application Pipeline

Single response, no confirmations. User pastes a job link + description -> 5 outputs:
1. CV pick + tailoring rationale
2. Tailored CV PDF
3. Motivation letter PDF (skip if user says no letter)
4. Tracker TSV row (copyable)
5. Token count (~8-10k target)

## Templates are pre-compliant

All templates in `assets/cv-templates/` ship ready to use. These are already applied:
- Color `#7bd3e9` (not #2980b9)
- English `C1 Courant` (not C2)
- GitHub removed (except DevSecOps + DevOps/SRE which keep it)
- Contact: centered, no photo
- Header text: always centered
- Projects section: "Projets Personnels"
- Profil: <=250 chars, starts with "2 ans en securite", includes complete rhythm phrase
- Project descriptions: 95-134 chars, HR-friendly outcome-first, must fit ONE rendered line
- Certifications: only verified certs (no "en cours")
- **Baifall Dream stage entry v3** (Juillet 2026 - Present, Paris) in FIRST position of
  Experience Professionnelle, above Concentrix. 3 bullets: cadrage (common, accompli,
  "95 exigences"), dev scope (common, nominal, covers the whole remaining mission),
  variant-specific bullet 3. Backend/Fullstack variants have 2 bullets (dev is covered by
  bullet 2). Bullets 2 and 3 are deliberately scoped to the full mission so no weekly
  update is needed. See `assets/stage-baifall-dream.md`. Stage ends 03/09/2026, no
  alternance conversion: never write "Stage puis Alternance".
- **No "Demarrage anticipe" subtitle**: removed from all alternance templates. CVs are
  either alternance or stage, never mixed messaging. Never re-add it.
- **Orphan-free rendering**: `text-wrap: pretty` on li, .project-desc, .profile
- Photos removed from all templates; contact line CSS always centers

**Do NOT re-apply these fixes.** No color swap, no C2->C1, no GitHub removal (unless
restoring GitHub for a DevSecOps/DevOps role using a non-DevOps template). Just tailor.

---

## Profile summary

- **Name:** Mouaad Sekkouri
- **Contact:** mouaadsekkourii@gmail.com | +33 7 51 13 54 25 | linkedin.com/in/sekkouri
- **School:** M1 Cybersecurite, Supinfo Lille (2025-2026) -> M2 Sept 2026
- **Current:** Stage Baifall Dream, Paris (Juillet 2026 - Present) : plateforme
  d'e-facturation (cahier des charges, dev module Factur-X/UBL, exigences securite)
- **Experience:** ~2 years Network & Security Support, Concentrix (Netgear)
- **Certifications:** AZ-900 (held)
- **Languages:** French (bilingual), English C1, Arabic (native), German A2
- **Differentiator:** Daily user of Claude and ChatGPT for productivity

---

## Step 0 -- Pre-Check

### Hard rejections (no output):
- School/bootcamp requiring re-enrollment in their program (REDSUP-type)
- Non-IT / non-technical roles (market analysis, pure management, sales)
- Roles requiring 5+ years experience as CDI
- Level mismatches and non-hiring-manager recruitment paths

### Flag once, then execute:
- Academic level mismatch (offer requires a level Mouaad doesn't match)
- Duration incompatibility (offer says 24 months, Mouaad targets 12)
- Non-ideal role that Mouaad explicitly wants to apply to

---

## Step 1 -- CV Selection

### The rule: read missions, not the job title

| If missions focus on... | Use CV |
|---|---|
| SOC, SIEM, detection, incident response, blue team | SOC |
| Pentesting, red team, offensive security | Pentest |
| GRC, risk analysis, compliance, audit, ISO 27001, EBIOS | GRC |
| IAM, identity governance, Active Directory, access mgmt | IAM |
| Application security, OWASP, SAST/DAST, secure SDLC | AppSec |
| Cloud security, Azure/AWS hardening, CIS benchmarks | CloudSec |
| CI/CD security, DevOps + security, pipeline hardening | DevSecOps |
| Project management + IT/cyber context | Chef de Projet IT |
| Consulting, advisory, digital transformation | Consultant IT |
| Infrastructure, sysadmin, network + security | Infra/Cloud |
| Network engineering, telecom, routing/switching | Reseaux |
| Backend development (Python, Java, APIs) | Backend Dev |
| Full-stack development (front + back) | Fullstack Dev |
| DevOps, SRE, CI/CD (no security focus) | DevOps/SRE |
| IT support, helpdesk, sysadmin | Support IT |
| Data engineering, BI, ETL | Data/BI |
| Machine learning, AI development | IA/ML |
| QA, testing, automation testing | QA Testing |
| General cybersecurity (no specific domain) | Cybersecurite |

### Shortcuts and traps

- **Title contains "Consultant" -> always Consultant IT** (hard rule, no exceptions)
- "Cyber" + PM tasks -> Chef de Projet IT (not a cyber CV)
- "Ingenieur secu" + IAM tasks -> IAM (not general cyber)
- "Consultant cyber" + audit tasks -> GRC (read the missions)
- "DevOps" + CI/CD security -> DevSecOps (not plain DevOps)
- "Admin secu" + infra tasks -> Infra/Cloud (not SOC)

### Alternance vs Stage

- **Alternance:** 12-month contract starting September 2026. Filename: `*__Alternance.html`
- **Stage:** 3-6 months. Use `*__Stage.html` if available (Consultant IT Stage, Cybersecurite Stage)
- If no stage template exists for the domain: adapt the alternance template (see Stage Adaptation below)

### Resubmissions

Always re-derive CV choice from missions. Never carry forward a prior pick.

---

## Step 2 -- CV Tailoring (5 zones + conditional Zone 6)

Copy the selected template to `/home/claude/` and edit. **Only these zones change:**

### Zone 1: Title (`<div class="job-title">`)
- Match the offer's terminology
- Include contract type and start date
- Example: "Analyste SOC - Alternance M2 des Septembre 2026"

### Zone 2: Profil (`<section class="profile">`)
- **Swap only the domain phrase** (3-5 words after "Profil oriente")
- Do NOT touch "2 ans en securite", the rhythm phrase, or the alternance/stage line
- Keep total length within +-15 chars of original (~240-250)
- Use HR-friendly terms: "detection de menaces" not "supervision SIEM"

### Zone 3: Tech Stack (`<div class="tech-grid">`)
- Reorder rows by relevance to the offer (most relevant category first)
- Add 1-2 keywords from the offer if genuinely in Mouaad's skill set
- Never remove the Bachelor tech stack row

### Zone 4: Projects
- Reorder the 3 projects by relevance (most relevant first)
- Descriptions are pre-set to fit one rendered line (95-134 chars) -- don't rewrite unless necessary
- If a minor word swap improves relevance, verify 95-134 chars AND run check_orphan_lines.py

### Zone 5: Localisation (in contact-info)
- Change to the offer's region only (e.g., "Ile-de-France", "Nord")
- Never city + region (not "Paris / Ile-de-France")

### Zone 6 (conditional): Baifall Dream stage bullet 3
- If the offer mentions ISO 27001, conformite, audit, RSSI -> swap to GRC bullet
- If the offer mentions developpement securise, SDLC, DevSecOps -> swap to DevSecOps bullet
- If the offer mentions cloud souverain, hebergement, SecNumCloud -> swap to CloudSec bullet
- Otherwise: leave the template's default bullet untouched (most common case)
Never edit bullets 1-2 or the stage title/dates. Never mention the end client
or "marketplace". Entity templates require entity-encoded bullets. After any swap, run
check_orphan_lines.py.

### Encoding note
4 templates use HTML entities (`&eacute;`, `&ccedil;`, etc.): **CloudSec, Consultant IT
(both alternance and stage), GRC**. When tailoring these, use `str_replace` tool for all
edits -- never `sed`. All other templates are plain UTF-8.

### What NOT to touch
- Color (already #7bd3e9)
- English level (already C1)
- GitHub (already correct per template)
- Contact CSS (already correct)
- Projects section title (already "Projets Personnels")
- Certifications (already clean)
- Rhythm phrase (already complete)
- Baifall Dream entry position, title, dates, bullets 1-2 (bullet 3 only via Zone 6 rules)
- The removed "Demarrage anticipe" subtitle (never re-add)

---

## Stage Adaptation

When the offer is a stage and no dedicated stage template exists:

1. Copy the alternance template
2. Change the job-title to stage context (e.g., "Analyste SOC - Stage 6 mois")
3. Change the profil: replace "Alternance de 12 mois des septembre 2026. Rythme : 1 sem.
   ecole / 1 sem. entreprise jusqu'en fevrier, puis temps plein en entreprise" with
   "Stage de [X] mois des [date]" -- matching the offer's exact duration and start date
4. Keep everything else unchanged

When a dedicated stage template exists (Consultant IT Stage, Cybersecurite Stage):
- Just apply the tailoring zones, no structural changes needed

---

## Step 3 -- Motivation Letter

### Generate with the bundled script:
```bash
python3 scripts/generate_letter_pdf.py \
    --cv /home/claude/tailored_cv.html \
    --body /home/claude/letter_body.html \
    --output /home/claude/CompanyName_Lettre_Motivation_Poste.pdf \
    --company "Company Name" \
    --location "City" \
    --date "DD mois YYYY"
```

### Letter body content (`letter_body.html`)
Write ONLY the paragraphs (no HTML wrapper):

```html
<p>Madame, Monsieur,</p>
<p>[Opening: why this company + role. Reference something specific from the offer.]</p>
<p>[Optional, if relevant to the offer -- Baifall Dream current stage: cadrage reglementaire,
   dev module de facturation. Never name the end client.]</p>
<p>[Concentrix experience: 1,500+ incidents, 85% first-contact resolution, 20% MTTR reduction.
   Connect to the role's needs using HR-friendly language.]</p>
<p>[1-2 relevant projects using outcome-first language, not jargon.]</p>
<p>[AZ-900 cert + M1 Cybersecurite at Supinfo. Continuous learning trajectory.]</p>
<p>[Closing: enthusiasm, availability, match to contract type and duration.]</p>
<p>Cordialement,<br/>Mouaad Sekkouri</p>
```

### Rules:
- Language: match the offer (French or English)
- Duration: strictly match the offer's stated duration -- never substitute
- Tone: modern, natural, human -- not stiff corporate. Specific to this company.
- Never mention "en cours" certifications
- Use "2 ans en securite" framing (match the CV)
- Max 1 page (script auto-verifies)
- Never use em dashes in any output
- Letter page usable width (170mm) is narrower than CV (190mm); contact font sizes are
  pre-scaled in generate_letter_pdf.py. Shorten content rather than re-enabling wrapping.
- generate_letter_pdf.py has an em dash hard-fail check: the script will error if any em
  dash character is found in the body HTML.

---

## Step 4 -- Tracker Row

```bash
python3 scripts/format_tracker_row.py \
    --entreprise "Company" \
    --poste "Job Title" \
    --contrat "Alternance|Stage" \
    --type "ESN|Grand groupe|Startup|PME" \
    --localisation "Region" \
    --source "WTTJ|LinkedIn|Indeed|Aerocontact" \
    --cv "CV [Variant]" \
    --projets "Project 1, Project 2, Project 3" \
    --adaptations "Key tailoring summary" \
    --lien "https://offer-url"
```

18-column TSV. N blank. Statut = A postuler. Relance J+5/J+10 auto-computed.

---

## Step 5 -- Token Count

State the estimated token count. Target: ~8-10k per application.

---

## Scripts Reference

| Script | When | What it does |
|---|---|---|
| `generate_cv_pdf.py <html> <pdf>` | Step 2 | Playwright A4, margins 0, print_background |
| `generate_letter_pdf.py --cv --body --output --company --location --date` | Step 3 | WeasyPrint letter with CV header extraction. Em dash hard-fail. |
| `verify_page_count.py <pdf>` | After any PDF | Verify exactly 1 page |
| `check_orphan_lines.py <html>` | After any text edit | Playwright orphan detection (35% threshold) |
| `format_tracker_row.py --entreprise --poste ...` | Step 4 | 18-column TSV with computed relance dates |
| `validate_cv.py <html> [--original <base>]` | Safety net | 13 checks -- use if any manual desc editing done |

---

## Execution Flow

```
1. User pastes job offer
2. Pre-check (Step 0) -- reject or flag if needed
3. Select CV from routing table
4. cp template -> /home/claude/ -> apply zones
5. generate_cv_pdf.py -> verify_page_count.py
6. check_orphan_lines.py (if any text edits were made)
7. Write letter_body.html -> generate_letter_pdf.py
8. format_tracker_row.py
9. present_files + tracker row + token count
```

No color swaps. No C2 fixes. No GitHub removal. No photo removal. No subtitle removal.
Just tailor -> generate -> deliver.

---

## Edge Cases & Principles

- **Single response, no confirmations.** All 5 outputs in one message.
- **Always tailor.** Never send a generic CV. Validated by real callback results.
- **HR + Tech dual layer:** Project titles use outcome language HR understands.
  Stack lines keep technical depth for tech reviewers.
- **Flag once, then execute.** Don't repeatedly ask about the same concern.
- **Re-derive on resubmissions.** Always re-read missions fresh.
- **Offer rhythm differs from template ("3j/2j" instead of "1sem/1sem"):**
  Update the rhythm phrase in the profil to match the offer exactly.
- **Offer start date differs ("octobre 2026" instead of "septembre 2026"):**
  Update the date in the profil and title to match.
- **Offer in English:** Write the letter in English. CV stays French.
- **Platform handling:** LinkedIn / HelloWork / Beetween -> user must paste description.
- **Chain bash commands.** Minimize round-trips for efficiency.
- **File locations:** templates in skill assets, working files in `/home/claude/`,
  outputs to `/mnt/user-data/outputs/`.
- **LINE-COUNT mismatch (-1)** when GitHub is removed from the contact block is a known
  non-blocking validator artifact.
- **HTML entity substitution** matters for character counting: `&amp;` counts as 1 display
  character, not 5; use Python with `re.sub` and `html.unescape()` to simulate validator logic.

---

## GitHub Exception

DevSecOps and DevOps/SRE templates include GitHub (9.2pt centered, 2-line contact).
All other templates have GitHub removed (8.5pt left-aligned, 1-line contact).

If using a non-DevOps template for a DevOps-adjacent role, do NOT add GitHub back.
If using a DevOps template for a non-DevOps role, do NOT remove GitHub (template is correct
for its intended use -- pick a different template instead).
