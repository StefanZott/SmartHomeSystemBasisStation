---
title: PCB — Versorgungsleitungen aufweiten, DRC-Ausschlüsse J_PWR1
created: 2026-09-26
jira: SHBS-21
priority: medium
type: feature
status: open
---

## Kontext

Restpunkte aus Task
[0047](../done/0047_pcb-layout-stromversorgung-leds.md), der auf Wunsch des
Bedieners vorzeitig abgeschlossen wurde. Buck-Wandler und +3V3-Verteilung
sind fertig. VBUS ab der USB-C-Buchse J_PWR1 und +5V ab F1 laufen aber noch
mit 0,2 mm statt der Netzklassenbreite `Power` (0,6 mm). Außerdem stehen
vier DRC-Meldungen an J_PWR1 aus dem Hersteller-Landepattern noch als
Fehler in der Liste.

## Ziel

Versorgungsleitungen auf 0,6 mm (außer im Pad-Feld der USB-C-Buchse:
0,2–0,3 mm, erst danach aufweiten). DRC-Meldungen an J_PWR1 bewusst
ausgeschlossen, DRC im Bereich Stromversorgung ohne Fehler.

## Schritte

- [ ] VBUS ab J_PWR1 bis D12/F1 auf 0,6 mm aufweiten (Agent, KiCad geschlossen)
- [ ] +5V ab F1 bis C13/D12 auf 0,6 mm aufweiten
- [ ] Bediener: `B` drücken, speichern, DRC prüfen
- [ ] Bediener: DRC-Ausschlüsse an J_PWR1 im DRC-Fenster (Rechtsklick →
      Ausschließen): 2× `starved_thermal` (A1, rechtes S1), 2× Kantenabstand
      zum NPTH (A12, linkes S1)
- [ ] `docs/project/power_supply.md` aktualisieren
- [ ] Commit

## Fortschritt

- 2026-09-26: Task aus 0047 ausgelagert, noch nicht begonnen.

## Commits

- (noch keine)

## Offene Fragen

- Keine.
