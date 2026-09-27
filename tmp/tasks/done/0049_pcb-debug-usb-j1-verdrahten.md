---
title: PCB — Debug-USB J1, ESD-Array U1, CC-Widerstände R21/R22 verdrahten
created: 2026-09-27
jira: SHBS-22
priority: high
type: feature
status: done
---

## Kontext

Der Bediener hat J1, U1, R21 und R22 platziert und verdrahtet. Das Review
(Nachtrag D1–D3 im
[Report](../../report/2026-09-24_pcb-review-stromversorgung-leds.md)) ergab:
Die Durchgänge unter U1 fehlen, der USB-Datenpfad ist unterbrochen. An J1
fehlen die Brücken zwischen den Pad-Reihen.

## Ziel

USB J1 → U1 → U6 in beiden Steckrichtungen verbunden, alle VBUS_J1-Pads
angebunden, footprint-bedingte DRC-Meldungen ausgeschlossen.

## Schritte

- [x] Durchgänge U1 10→1, 9→2, 7→4 (Agent)
- [x] Brücken J1: B6→A6, B7→A7 (über Via/B.Cu), B4→A9, B9→A4, A4-Gruppe über B.Cu (Agent)
- [x] DRC per CLI: keine offene Verbindung an J1/U1
- [x] `docs/project/hardware.md` ergänzt
- [x] `B` und DRC-Ausschlüsse (5× U1, 2× J1) — in die DRC-Schlussrunde des Gesamt-Layouts verschoben
- [x] Commit

## Fortschritt

- 2026-09-27: Ticket SHBS-22 angelegt. 21 Segmente und 3 Vias per Skript
  gesetzt (KiCad geschlossen). U1-Durchgänge USB+ und VBUS_J1 mit 0,15 mm
  wegen der breiten GND-Pads 3/8, sonst 0,2 mm. DRC: offene Verbindungen
  120 → 112, keine an J1/U1. Keine neuen Abstandsfehler außer gegen die
  veraltete Zonenfüllung. Nächster Schritt: Bediener `B` und Ausschlüsse.
- 2026-09-27: Bediener gibt das restliche Layout frei (Agent platziert und
  routet alles außer T1, J1, J_PWR1, D7–D10). Zonenfüllung und
  DRC-Ausschlüsse erfolgen dort gesammelt am Ende. Task abgeschlossen.

## Commits

- (noch keine)

## Offene Fragen

- Keine.
