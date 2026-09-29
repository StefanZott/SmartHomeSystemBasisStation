---
title: PCB — Restliches Routing mit Freerouting, Zonen, DRC-Schlussrunde
created: 2026-09-27
jira: SHBS-23
priority: high
type: feature
status: done
---

## Kontext

Nach Platzierung (0050) und kritischem Ethernet-Routing (0051) werden die
übrigen Netze mit Freerouting geroutet. Dazu gehören die gesammelten
DRC-Ausschlüsse aus Task 0049 (5× Padabstand U1, 2× Kantenabstand J1).

## Schritte

- [x] DSN-Export per `pcbnew`, Freerouting (vorhandene Leiterbahnen gesperrt)
- [x] SES-Import, Zonen füllen
- [x] DRC: keine offenen Verbindungen, keine Fehler
- [x] Bediener: Sichtprüfung, DRC-Ausschlüsse (U1, J1)
- [x] Doku, Commit

## Fortschritt

- 2026-09-27: Task angelegt.

- 2026-09-27: Erster Freerouting-Lauf (Timeout) ohne Ergebnis abgebrochen.
- 2026-09-29: Zweiter Lauf losgelöst gestartet, 8,5 min, 10 offen /
  13 Verstöße laut Freerouting. Nach dem Import: 20 offene Verbindungen, alle
  GND. Per Skript gut 20 GND-Vias und Stiche ergänzt, Inseln angebunden. DRC:
  **0 offene Verbindungen**, 52 Meldungen (Silkscreen, footprint-bedingte
  Abstände U1/J1, 4 Montagelöcher ohne Symbol, 6× starved_thermal).
  Nächster Schritt: Sichtprüfung, DRC-Ausschlüsse, Silkscreen.

- 2026-09-29: Auf Wunsch des Bedieners (Handlötung) Bauteile um U7 im Raster
  3,5 mm neu gesetzt, C7 nach unten. Alle nicht gesperrten Leitungen
  entfernt, Freerouting neu (8,5 min), zweiter Durchgang für USB−. GND-Pins
  von U7 und J1 sowie RXN → R40 von Hand (Via-Paar), 6 Insel-Vias. DRC:
  **0 offene Verbindungen**, 26 Meldungen (Silkscreen 7, U1/J1-Footprint,
  starved_thermal 9, Montagelöcher 4, Textgröße 1).
  Nächster Schritt: Sichtprüfung, DRC-Ausschlüsse, Commit.

- 2026-09-29: Gehäuse-Vorbereitung auf Wunsch des Bedieners: obere Kante
  von y 25,0 auf 27,45 (maximaler Überstand der USB-C-Buchsen bei 0,5 mm
  Randabstand), J_PWR1/J1/T1 stehen 1,2–1,3 mm über. H1/H2 und die
  Zonenoberkanten mitgezogen, R9-Beschriftung verschoben. DRC: 0 offene
  Verbindungen, keine neuen Kupferbefunde.

- 2026-09-29: Silkscreen bereinigt (Beschriftungen R36/R37/C25/C26/C12/C29
  verschoben, C8-Textgröße, doppelte Pin-1-Markierung U7 entfernt), H1–H4 als
  „nur Platine". DRC-Regel für U1 (`BasisStation.kicad_dru`) und 11 neue
  Ausschlüsse mit Begründung. DRC: 0 offen, 0 Parität, nur 15 Ausschlüsse.
  Task abgeschlossen.

## Commits

- (noch keine)

## Offene Fragen

- Keine.
