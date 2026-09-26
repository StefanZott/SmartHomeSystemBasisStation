---
title: PCB-Layout — Stromversorgung und Status-LEDs platzieren und routen
created: 2026-09-24
jira: SHBS-21
priority: high
type: feature
status: open
---

## Kontext

Stromversorgung und Status-LEDs sind im Schaltplan fertig, im PCB aber erst
teilweise umgesetzt. Das Review vom 2026-09-24
([Report](../../report/2026-09-24_pcb-review-stromversorgung-leds.md))
ergab mehrere Befunde (B2–B5). Ethernet läuft separat unter SHBS-10.

## Ziel

Stromversorgung und LEDs vollständig platziert und geroutet, mit eigener
Netzklasse für die Versorgungsnetze. DRC im Bereich ohne Fehler.

## Schritte

- [x] Erste Platzierung und Routing durch Bediener (WIP-Stand)
- [x] Netzklasse `Power` (0,6 mm, Via 0,8/0,4) für VBUS, +5V, +3V3, GND, SW anlegen (B2)
- [x] Schaltknoten im Schaltplan mit lokalem Label `SW` benennen
- [ ] Bediener: KiCad öffnen, im PCB-Editor F8 (Netz `Net-(D11-K)` → `/Stromversorgung/SW`)
- [ ] Versorgungsleitungen auf Netzklassenbreite aufweiten (außer Pad-Feld USB-C)
- [ ] Buck-Wandler kompakt um PS1 anordnen, Schaltknoten kurz halten (B3)
- [ ] +3V3 zu U6.2 und zu den LED-Anoden routen (B4)
- [ ] DRC-Restmeldungen an J_PWR1 ausschließen: 2× `starved_thermal`
      (A1, rechtes S1), 2× Kantenabstand NPTH (A12, linkes S1) —
      Hersteller-Landepattern, Pads per Leiterbahn angebunden (aus SHBS-20)
- [ ] `docs/project/power_supply.md` und `hardware.md` um Layout-Stand ergänzen
- [ ] Commit

## Fortschritt

- 2026-09-24: Task angelegt. Bediener hat Stromversorgung und LEDs erstmals
  platziert und geroutet, Zonen gefüllt. DRC gesamt: 75 Meldungen, davon
  144 offene Verbindungen überwiegend außerhalb dieses Bereichs. Stand wird
  als WIP-Commit gesichert, damit SHBS-20 separat committet werden kann.
  Nächster Schritt: Netzklasse `Power` (Punkt 2 des Reviews).

- 2026-09-25: Label `SW` in `Stromversorgung.kicad_sch` auf der Leitung ab
  PS1.6 gesetzt (Netzliste: `/Stromversorgung/SW` = C15.2, D11.1, L1.2,
  PS1.6; ERC unverändert). Netzklasse `Power` mit fünf Mustern in
  `BasisStation.kicad_pro` angelegt. Muster per DRC-Probe in Kopie geprüft
  (Abstand testweise 5 mm): GND, +3V3, VBUS, +5V greifen, SW erst nach F8.
  `power_supply.md` ergänzt. Nächster Schritt: F8 durch Bediener, dann
  Leitungen aufweiten.

## Commits

- c2ccc4a (WIP) Erster Layout-Stand Stromversorgung und LEDs

## Offene Fragen

- Keine.
