#!/usr/bin/env python3
"""
format_tracker_row.py — Generate an 18-column TSV tracker row.

Rules 105-114: Formatted with computed Relance J+5 and J+10 dates.

Usage:
    python3 format_tracker_row.py \
        --entreprise "Company" \
        --poste "Job Title" \
        --contrat "Alternance|Stage" \
        --type "ESN/Consulting" \
        --localisation "Île-de-France" \
        --source "LinkedIn" \
        --cv "CV SOC" \
        --projets "Project 1, Project 2, Project 3" \
        --adaptations "Key adaptations summary" \
        --lien "https://..." \
        [--date "DD/MM/YYYY"]  # defaults to today
"""

import argparse
from datetime import datetime, timedelta

from utf8_console import configure_utf8_output


def format_date(dt):
    return dt.strftime("%d/%m/%Y")


def main():
    configure_utf8_output()
    parser = argparse.ArgumentParser(description="Format tracker TSV row")
    parser.add_argument("--entreprise", required=True)
    parser.add_argument("--poste", required=True)
    parser.add_argument("--contrat", required=True)
    parser.add_argument("--type", required=True, dest="type_entreprise")
    parser.add_argument("--localisation", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--cv", required=True)
    parser.add_argument("--projets", required=True)
    parser.add_argument("--adaptations", required=True)
    parser.add_argument("--lien", required=True)
    parser.add_argument("--date", default=None, help="Application date DD/MM/YYYY (default: today)")
    args = parser.parse_args()

    if args.date:
        app_date = datetime.strptime(args.date, "%d/%m/%Y")
    else:
        app_date = datetime.now()

    relance_5 = app_date + timedelta(days=5)
    relance_10 = app_date + timedelta(days=10)

    columns = [
        "",  # N° (blank)
        format_date(app_date),  # Date
        args.entreprise,  # Entreprise
        args.poste,  # Poste
        args.contrat,  # Contrat
        args.type_entreprise,  # Type entreprise
        args.localisation,  # Localisation
        args.source,  # Source
        "🟡 À postuler",  # Statut
        args.cv,  # CV utilisé
        args.projets,  # Projets sélectionnés
        args.adaptations,  # Adaptations clés
        args.lien,  # Lien offre
        "",  # Contact (empty)
        format_date(relance_5),  # Relance J+5
        format_date(relance_10),  # Relance J+10
        "",  # Date entretien (empty)
        "",  # Notes (empty)
    ]

    row = "\t".join(columns)
    print(row)


if __name__ == "__main__":
    main()
