---
title: Stückliste unter pcb/ statt tmp/report/ ablegen, alte STL.xlsx entfernen
created: 2026-09-24
jira: SHBS-19
priority: low
type: docs
status: done
---

## Kontext

Die bestellfähige Stückliste landete in `tmp/report/` mit festem Datum im
Namen. Das ist ein Hardware-Artefakt, kein Analysebericht. Zusätzlich lag in
`pcb/` noch die alte Handliste `STL.xlsx` (u. a. mit dem entfallenen PS2).

## Umsetzung

- `OUTPUT_PATH` in `tmp/bom/generate_bom.py` auf
  `pcb/BasisStation_Stueckliste.xlsx` umgestellt (fester Name, ohne Datum).
- Bestehende Mappe per `git mv` dorthin verschoben und mit
  `--no-network` neu erzeugt (44 Positionen, alle mit Preis).
- `pcb/STL.xlsx` gelöscht.
- `docs/project/hardware.md`: Ablageort ergänzt.

## Done-Bedingung

- [x] Skript schreibt nach `pcb/`
- [x] Alte Mappe verschoben, `STL.xlsx` entfernt
- [x] Doku aktualisiert
