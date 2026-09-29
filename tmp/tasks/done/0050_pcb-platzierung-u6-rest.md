---
title: PCB — U6 nach rechts oben, EN/J6/Puffer-C und LED-Treiber platzieren
created: 2026-09-27
jira: SHBS-23
priority: high
type: feature
status: done
---

## Kontext

Bediener-Vorgabe 2026-09-27: T1, J1, J_PWR1, D7–D10 bleiben fest. U6 kommt
nach rechts oben (U.FL zur Ecke, Gehäuseantenne dort). LED-Treiber dürfen
verschoben werden. Stromversorgung und Debug-USB bleiben.

## Ziel

U6, S2/R9/C7, C8/C10/C12, J6, Q1–Q4, R13–R16, R23–R26 innerhalb des Umrisses,
ohne Courtyard-Überlappung, sinnvoll zum späteren Routing angeordnet.

## Schritte

- [x] Platzierung per `pcbnew`-Skript (KiCad geschlossen)
- [x] Alte Leiterbahnen zu U6 (USB, +3V3, LED-GPIOs) entfernen
- [x] Courtyard-/DRC-Prüfung
- [x] Sichtprüfung durch Bediener

## Fortschritt

- 2026-09-27: Task angelegt.

- 2026-09-27: 54 alte Leiterbahnen zur früheren U6-Position entfernt, U6 bei
  (188 / 42), U7 bei (144 / 46), übrige Teile platziert. Keine
  Courtyard-Überlappung (außer der bekannten PS1/C15). Montagelöcher in
  H1–H4 umbenannt. Nächster Schritt: Sichtprüfung durch Bediener.

- 2026-09-29: Sichtprüfung durch Bediener („sieht gar nicht so schlecht aus").
  Umplatzierung für Handlötung (Raster 3,5 mm) und Kantenverschiebung siehe
  Task 0052. Task abgeschlossen.

## Commits

- d2fd4e2 Gesamt-Layout platziert und geroutet, DRC sauber

## Offene Fragen

- Keine.
