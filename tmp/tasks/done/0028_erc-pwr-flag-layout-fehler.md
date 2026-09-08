---
status: done
priority: high
type: bugfix
created: 2026-06-06
jira: pending
requirement: hardware-erc
completed: 2026-06-07
---

# ERC-Fehler Layout-Blatt — PWR_FLAG und +3V3-Versorgung

## Ergebnis

ERC auf **`/Layout/`**: **0 Fehler** (bestätigt 07.06.2026 nach Pin-Typ-Korrektur PS2).

## Durchgeführte Maßnahmen

| Maßnahme | Variante |
|----------|----------|
| `#FLG05` vom +3V3-Netz entfernt | A |
| `#FLG06` vom GND-Netz entfernt | A |
| EN/J6: falsches Power-Symbol durch Label `EN` ersetzt | — |
| `PWR_FLAG` (#FLG04) am **+12V**-Eingang | A |
| **`+3V3`-Power-Symbol** auf der Versorgungsschiene | — |
| **PS2 Pin 3 (+VOUT)**: elektrischer Typ **Output → Power output** (Symbol-Editor, `TSR_1-2433E.kicad_sym`) | — |

## Done-Kriterien

- [x] ERC auf `/Layout/`: **0 Fehler** (Warnungen Bibliotheken separat).
- [x] `#FLG05` nicht mehr am +3V3-Ausgang in Konflikt mit PS2.
- [x] Kein `PWR_FLAG` mehr auf globalem **GND**-Netz neben `GND`-Symbolen.
- [x] Analyse-Report `tmp/report/kicad-schaltplan-analyse-2026-06-05.md` aktualisiert.
- [x] Variante **A** (Standard, ohne ERC-Ausnahmen).

## Offen (separater Task)

- 28 Bibliotheks-Warnungen Root `/` (`Footprints`, `Espressif`, …)
- Warnung S2 ↔ J1 GND (optional: S2-Pin **passive**)
- 2× `unconnected_wire_endpoint` im Layout-Schaltplan

## Referenzen

- Layout-Schaltplan: `pcb/BasisStation/BasisStation_Layout.kicad_sch`
- Symbol: `pcb/Symbol/TSR_1-2433E.kicad_sym`
- Analyse: `tmp/report/kicad-schaltplan-analyse-2026-06-05.md`
