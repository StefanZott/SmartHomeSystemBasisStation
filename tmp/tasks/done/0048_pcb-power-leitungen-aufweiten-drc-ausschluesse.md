---
title: PCB — Versorgungsleitungen aufweiten, DRC-Ausschlüsse J_PWR1
created: 2026-09-26
jira: SHBS-21
priority: medium
type: feature
status: done
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

- [x] VBUS ab J_PWR1 bis D12/F1 auf 0,6 mm aufweiten (Agent, KiCad geschlossen) — A4-Zweig nur 0,3 mm wegen CC1
- [x] +5V ab F1 bis C13/D12 auf 0,6 mm aufweiten — Grafiklinien zu D12 durch Leiterbahnen ersetzt
- [x] Bediener: `B` drücken, speichern, DRC prüfen
- [x] Bediener: DRC-Ausschlüsse an J_PWR1 im DRC-Fenster (Rechtsklick →
      Ausschließen): 2× `starved_thermal` (A1, rechtes S1), 2× Kantenabstand
      zum NPTH (A12, linkes S1)
- [x] `docs/project/power_supply.md` aktualisieren
- [x] Commit

## Fortschritt

- 2026-09-26: Task aus 0047 ausgelagert, noch nicht begonnen.
- 2026-09-27: Agent hat per Skript (KiCad geschlossen) aufgeweitet:
  VBUS-Hauptpfad A9 → F1 ab y 37,4 auf 0,6 mm (Segment im Pad-Feld geteilt),
  B.Cu-Brücke 0,6 mm, A4-Zweig ab y 37,4 auf 0,3 mm (CC1 im Abstand 0,5 mm
  parallel). +5V zu D12 bestand aus zwei `gr_line` auf F.Cu mit Netz → durch
  0,6-mm-Segmente ersetzt, Stich zum Pad ebenfalls 0,6 mm. DRC: keine neuen
  Abstandsfehler zwischen Leiterbahnen, offene Verbindungen unverändert 139.
  12 neue Meldungen nur gegen die veraltete GND-Füllung. Doku ergänzt.
  Nächster Schritt: Bediener `B`, speichern, DRC-Ausschlüsse J_PWR1.
- 2026-09-27: Bediener hat Zonen gefüllt und die vier Meldungen an J_PWR1
  ausgeschlossen (in `BasisStation.kicad_pro`, `drc_exclusions`). DRC: 71
  statt 75 Meldungen, J_PWR1 ohne Meldung, keine Zonen-Artefakte mehr.
  Außerhalb des Bereichs verbleiben u. a. 2× Kantenabstand an J1
  (Debug-USB, gleiches Landepattern-Thema), 5× Abstand an U1, Silkscreen,
  139 offene Verbindungen (überwiegend Ethernet/SHBS-10). Task abgeschlossen.

## Commits

- b0bc21b (unvollständig, nur Verschieben der Task-Datei)
- 6aa90d9 Versorgungsleitungen aufgeweitet, DRC-Ausschlüsse J_PWR1 (Nachtrag)

## Offene Fragen

- Keine.
