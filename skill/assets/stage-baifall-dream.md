# Baifall Dream Stage - Reference Document (v3)

## Context

Mouaad Sekkouri, stage chez Baifall Dream (Paris, 06/07/2026 - 03/09/2026).
Mission : etude et developpement d'une plateforme d'e-facturation.
**Regle absolue : ne jamais nommer le client final dans aucun document.**

**Alternance ecartee par l'entreprise (juillet 2026).** Le stage ira a son terme le
03/09/2026. Aucune mention de "Stage puis Alternance" nulle part.

## Principe v3 : perimetre nominal complet

Les bullets couvrent desormais l'integralite du perimetre de la mission (prototype
Factur-X, squelette applicatif, modele de donnees, socle securite) en **formulation
nominale**. Objectif : plus aucune mise a jour hebdomadaire a faire au fil des taches.

Ce qui est decrit est la mission conventionnee et la feuille de route reelle, jamais un
accompli non realise. La distinction se joue sur le verbe :
- "Redaction du ..." = accompli, uniquement si le livrable existe.
- "Conception et developpement de ..." = mission en cours, honnete par construction.

## Regles de formulation

1. Les bullets dans les templates sont la version "line-fit" (ajustee au rendu).
2. Bullet 1 : passe accompli (le cahier des charges est livre, 95 exigences est factuel).
3. Bullets 2 et 3 : formulation nominale, couvrent le perimetre a venir. Ne jamais les
   transformer en accompli chiffre avant que ce soit factuel.
4. Pas de tirets cadratins. Deux-points, virgules ou parentheses.
5. Les templates sont encodes de deux facons : accents bruts ou entites HTML
   (&eacute;, &egrave;, &agrave;, &iuml;...). **Toujours respecter l'encodage du fichier
   edite**, ne jamais injecter un accent brut dans un template a entites.
6. Apres toute edition de bullet : regenerer le PDF et verifier verify_page_count.py.
   Controle visuel du retour a la ligne via `pdftotext -layout`.
7. check_orphan_lines.py remonte des faux positifs hors environnement de rendu complet
   (largeur de conteneur mal mesuree). Le controle fiable est le PDF rendu.

## Bloc HTML de reference (3 bullets)

```html
<div class="experience-item">
  <div class="job-header">
    <div class="job-position"><span class="company-name">Baifall Dream</span> - Stage :
    Etude et Developpement d'une Plateforme d'e-Facturation,
    <span class="job-location">Paris</span></div>
    <div class="job-date">Juillet 2026 - Present</div>
  </div>
  <ul>
    <li>[BULLET_1 : cadrage, commun, accompli]</li>
    <li>[BULLET_2 : perimetre dev complet, commun, nominal]</li>
    <li>[BULLET_3 : decline selon la variante, nominal]</li>
  </ul>
</div>
```

## Bullet 1 (commun, accompli) - 167 car., rendu sur 2 lignes

> Redaction du cahier des charges d'une plateforme de facturation electronique
> (<strong>reforme B2B 2026</strong>) : benchmark de <strong>3 plateformes agreees</strong>,
> <strong>95 exigences</strong>, architecture cible.

## Bullet 2 (commun, nominal, perimetre complet) - 127 car., 1 ligne

> Conception et developpement de la plateforme : generation <strong>Factur-X/UBL</strong>,
> modele de donnees, <strong>API REST</strong>, cycle de vie des factures.

Couvre : prototype Factur-X, squelette applicatif, modele de donnees, API, cycle de vie.

## Bullet 3 : declinaisons par variante

| Variante | Bullet 3 |
|---|---|
| Cybersecurite (default) | Definition des exigences reglementaires et securite : immatriculation DGFiP, ISO 27001, authentification, chiffrement, RGPD art. 32. |
| GRC | Cadrage reglementaire : immatriculation DGFiP, certification ISO 27001 (perimetre SMSI), conformite RGPD art. 32. |
| DevSecOps | Specification d'une architecture secure by design : authentification, chiffrement, journalisation, integration API de plateformes agreees (Factur-X/UBL). |
| AppSec | Definition des exigences de securite applicative : authentification, gestion des acces, chiffrement, RGPD art. 32, formats normalises Factur-X/UBL. |
| CloudSec | Analyse des exigences d'hebergement (localisation UE, referentiel SecNumCloud) et specifications securite de l'infrastructure cible (ISO 27001). |
| SOC | Specification des exigences de journalisation et de tracabilite de la plateforme (ISO 27001, RGPD art. 32) en vue de sa supervision securite. |
| Chef de Projet IT | Cadrage complet du projet : benchmark, perimetre MVP vs V2, plan en deux volets (developpement et immatriculation DGFiP), presentation aux parties prenantes. |
| Consultant IT | Etude comparative de 3 solutions du marche et recommandation d'architecture : build interne connecte a une plateforme agreee via API, feuille de route reglementaire. |
| IAM | Specification de la gestion des identites et des acces de la plateforme : authentification, roles et permissions, tracabilite (ISO 27001, RGPD art. 32). |
| Backend / Fullstack | 2 bullets seulement (le bullet 2 couvre deja le dev). |
| Autres (Data, IA, QA, Reseaux, Infra, DevOps, Support, Pentest) | Bullet Cybersecurite default. |

## Selection selon l'offre (swap du bullet 3 lors du tailoring - Zone 6)

- Si l'offre mentionne ISO 27001, conformite, audit, RSSI : bullet GRC.
- Si l'offre mentionne developpement securise, SDLC, DevSecOps : bullet DevSecOps.
- Si l'offre mentionne cloud souverain, hebergement, SecNumCloud : bullet CloudSec.
- En cas de doute : conserver le bullet par defaut du template (aucune edition).
- Apres tout swap : regenerer le PDF et verifier verify_page_count.py.

## Seule mise a jour prevue d'ici la fin du stage

Le perimetre nominal couvre tout le reste de la mission. Une seule evolution merite une
edition, une fois le livrable reellement valide :

- [ ] Prototype Factur-X valide par un outil de controle externe : basculer la premiere
      partie du bullet 2 en accompli, en gardant la suite du perimetre en nominal.

Ne rien anticiper avant que ce soit factuel.

## Regle pour la date

- Jusqu'au 03/09/2026 : "Juillet 2026 - Present" (exact, Mouaad est en poste).
- A partir du 03/09/2026 : "Juillet 2026 - Septembre 2026", et les bullets nominaux
  passent en accompli factuel selon ce qui aura reellement ete livre.
- Jamais de date de debut anterieure a juillet 2026 : la convention et l'attestation de
  fin de stage portent le 06/07/2026.

Date de derniere mise a jour : 24/07/2026
