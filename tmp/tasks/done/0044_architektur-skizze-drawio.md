---
title: Architektur-Blockskizze als drawio neu erstellen und im Schaltplan einbetten
created: 2026-09-24
jira: SHBS-18
priority: low
type: docs
status: done
---

## Kontext

Die Blockskizze auf Seite 1 von `BasisStation.kicad_sch` (Stand 2025-02-20)
zeigte noch 24-V-Versorgung, Power-Taster, USB-Micro-B mit UART-Bridge und
JTAG-Header, aber kein Ethernet.

## Umsetzung

- `pcb/architektur_basisStation.drawio` neu erstellt: Versorgung (J_PWR1 → F1/D12
  → PS1 → +3V3), Debug (J1 → U1 → USB-Serial-JTAG), J6, S2, WLAN (ANT1/ANT2),
  Ethernet (U7 W5500, Y1, T1), LEDs über Q1–Q4 mit GPIO-Zuordnung.
- PNG-Export (draw.io Desktop headless, Faktor 1,5, 2190 × 1199 px) im Root-Blatt
  eingebettet, 265 × 145 mm, Position (148,5 / 88). ERC unverändert: nur die
  hinterlegte Ausnahme `pin_to_pin` an S2.
- `docs/project/hardware.md` und `docs/project/architecture.md` angepasst
  (Verweis auf drawio, nur `.drawio` versionieren; Power-Taster entfernt).

## Done-Bedingung

- [x] drawio-Datei nach aktuellem Schaltplanstand
- [x] Bild im Root-Blatt ersetzt, ERC ohne neue Befunde
- [x] Doku aktualisiert
