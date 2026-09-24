---
title: USB-C J_PWR1 — fehlende Pins B4/B9 (VBUS) und A12/B12 (GND) im Symbol ergänzen
created: 2026-09-24
jira: SHBS-20
priority: high
type: bugfix
status: done
---

## Kontext

PCB-Review vom 2026-09-24 (Befund B1,
[Report](../../report/2026-09-24_pcb-review-stromversorgung-leds.md)): Das
Symbol `shbs_power:USB_C_Receptacle_Power` führte nur A1, B1, A4, A9, A5, B5
und S1. Die Footprint-Pads B4, B9, A12 und B12 von J_PWR1 lagen ohne Netz.

## Ziel

Alle vier VBUS- und alle vier GND-Kontakte sind im Schaltplan verbunden und
auf dem PCB angebunden.

## Schritte

- [x] Symbol in `pcb/Bauteile/Power/power.kicad_sym` um B4/B9 (VBUS) und
      A12/B12 (GND) ergänzen — unsichtbar, `passive`, gestapelt auf A4/A9 bzw.
      A1/B1
- [x] Symbol-Cache in `pcb/BasisStation/Stromversorgung.kicad_sch` nachziehen
- [x] ERC und Netzliste per `kicad-cli` prüfen
- [x] `docs/project/power_supply.md` aktualisieren
- [x] Bediener: Projekt in KiCad schließen/neu öffnen, im PCB-Editor F8
- [x] Bediener: Pads B4/B9 an VBUS und A12/B12 an GND anbinden
- [x] Rest-DRC an J_PWR1 klären — unkritisch, Ausschluss in Task 0047 (SHBS-21) übernommen
- [x] Commit

## Fortschritt

- 2026-09-24: Ticket SHBS-20 angelegt.
- 2026-09-24: Vier Pins in Bibliothek und Schaltplan-Cache ergänzt (Skript,
  keine weiteren Änderungen im Diff). ERC: unverändert 1 ausgenommene
  Warnung (S2/#FLG04). Netzliste: VBUS = A4, A9, B4, B9; GND = A1, A12, B1,
  B12, S1. Doku angepasst. Nächster Schritt: F8 im PCB-Editor durch Bediener.
- 2026-09-24: Bediener hat F8 ausgeführt und geroutet: B4→A9, B9→A4, B12→A1
  (je F.Cu 0,2 mm), B1→S1 links, B12→S1 rechts, A12 nach unten auf GND-Via
  (69,0 / 38,0). Zonen neu gefüllt. DRC: keine offene Verbindung mehr an
  J_PWR1. Rest: `starved_thermal` an A1 und rechtem S1 (je 1 statt 2 Stege,
  Pads sind zusätzlich per Leiterbahn angebunden), Kantenabstand 0,30 mm
  von A12 und linkem S1 zum ovalen NPTH (Hersteller-Landepattern).
  A12 → B1 direkt ist nicht routbar: Der ovale NPTH gilt in KiCad als
  Platinenkante (0,5 mm Abstand), der Router blockiert die Verbindung.
  Nächster Schritt: Umgang mit den Rest-Meldungen, dann Commit.
- 2026-09-24: Rest-Meldungen als unkritisch bewertet, Ausschluss im DRC in
  Task 0047 (SHBS-21) übernommen. PCB-Anteil liegt im WIP-Commit c2ccc4a
  (SHBS-21), da die PCB-Datei nicht teilbar ist. Branch
  `fix/usb-c-jpwr1-pins`. Task abgeschlossen.

## Commits

- (noch keine)

## Offene Fragen

- Keine.
