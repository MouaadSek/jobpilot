# CV Template Manifest

21 templates, organized by specialization. Each is pre-compliant (photo removed, color #7bd3e9,
English C1, GitHub removed except DevSecOps/DevOps, contact centered, subtitle removed,
Baifall Dream stage integrated, text-wrap: pretty applied).

## Alternance Templates (19)

| # | Filename | Domain | Entity-encoded |
|---|----------|--------|----------------|
| 1 | Mouaad_Sekkouri_-_SOC__Alternance.html | SOC / Blue Team | No |
| 2 | Mouaad_Sekkouri_-_GRC__Alternance.html | GRC / Compliance | Yes |
| 3 | Mouaad_Sekkouri_-_DevSecOps__Alternance.html | DevSecOps | No |
| 4 | Mouaad_Sekkouri_-CloudSec__Alternance.html | Cloud Security | Yes |
| 5 | Mouaad_Sekkouri_-_AppSec__Alternance.html | AppSec | No |
| 6 | Mouaad_Sekkouri_-_Cybersecurite__Alternance.html | General Cybersecurity | No |
| 7 | Mouaad_Sekkouri_-_IAM__Alternance.html | IAM | No |
| 8 | Mouaad_Sekkouri_-_Pentest__Alternance.html | Pentest / Red Team | No |
| 9 | Mouaad_Sekkouri_-_Consultant_IT__Alternance.html | IT Consulting | Yes |
| 10 | Mouaad_Sekkouri_-_Chef_de_Projet_IT__Alternance.html | IT Project Mgmt | No |
| 11 | Mouaad_Sekkouri_-_Backend_Dev__Alternance.html | Backend Dev | No |
| 12 | Mouaad_Sekkouri_-_Fullstack_Dev__Alternance.html | Fullstack Dev | No |
| 13 | Mouaad_Sekkouri_-_DevOps_SRE__Alternance.html | DevOps / SRE | No |
| 14 | Mouaad_Sekkouri_-_Infrastructure_Cloud__Alternance.html | Infra / Cloud | No |
| 15 | Mouaad_Sekkouri_-_Reseaux_Telecoms__Alternance.html | Networks / Telecom | No |
| 16 | Mouaad_Sekkouri_-_Data_Engineering_BI__Alternance.html | Data / BI | No |
| 17 | Mouaad_Sekkouri_-_IA_Machine_Learning__Alternance.html | AI / ML | No |
| 18 | Mouaad_Sekkouri_-_QA_Testing__Alternance.html | QA / Testing | No |
| 19 | Mouaad_Sekkouri_-_Support_IT_Sysadmin__Alternance.html | IT Support / Sysadmin | No |

## Stage Templates (2)

| # | Filename | Domain | Entity-encoded |
|---|----------|--------|----------------|
| 20 | Mouaad_Sekkouri_-_Cybersecurite__Stage.html | General Cybersecurity | No |
| 21 | Mouaad_Sekkouri_-_Consultant_IT__Stage.html | IT Consulting | Yes |

## Entity-Encoded Templates

4 templates use HTML entities (&eacute;, &ccedil;, etc.): CloudSec, Consultant IT (x2), GRC.
Always use `str_replace` for edits on these. Never use `sed`.

## Baifall Dream Bullet 3 Variants

- Backend Dev, Fullstack Dev: 2 bullets only (no bullet 3)
- SOC, Pentest, Cybersecurite, Data/BI, IA/ML, QA, Reseaux, Infra, DevOps, Support: default (regulatory/security)
- GRC, DevSecOps, AppSec, CloudSec, Chef de Projet IT, Consultant IT, IAM: specialized variant
