---
title: 3D-Modelle für C7/C10/C12, C8, J6, D7–D10 ergänzen, PS1-Pfad korrigieren
created: 2026-09-29
jira: SHBS-24
priority: medium
type: bugfix
status: done
---

## Kontext

Im 3D-Viewer fehlten die Modelle von S2, C8, C10, C12, C7 und J6 (Meldung
des Bedieners). Bei der Prüfung zeigte sich, dass auch D7–D10 ohne Modell
waren und PS1 auf die veraltete Variable `KISYS3DMOD` verwies.

## Ziel

Alle Bauteile im 3D-Viewer maßlich richtig, Modellpfade in Bibliothek und
Platine.

## Schritte

- [x] Vorhandene STEP-Dateien verknüpfen (C7/C10/C12, J6)
- [x] KiCad-Standardmodell für C8 mit Drehung/Versatz passend zur Pad-Lage; LEDs mit Würth-Originalmodellen
- [x] PS1 auf `${KICAD9_3DMODEL_DIR}/…/SOT-23-6.step`
- [x] Bibliotheken per `pcbnew.FootprintLoad` geprüft, DRC unverändert, Render geprüft
- [x] `docs/project/hardware.md` (Abschnitt 3D-Modelle)
- [x] S2: Bourns 1543-650-149 (laut Stückliste), Modell selbst aus dem Datenblatt erstellt

## Fortschritt

- 2026-09-29: Modelle eingetragen (6 Bibliotheks-Footprints, 9 Bauteile auf der
  Platine, PS1-Pfad). C7/C10/C12 und J6 im Render korrekt über den
  Footprints. KiCad-Standardmodelle nur unter Windows sichtbar (3D-Bibliothek
  fehlt im Container). S2 bleibt ohne Modell, bis der Hersteller bekannt ist.

- 2026-09-29: Bediener hat C7/C10/C12 (Z 6 mm) und J6 (Z 4,5 mm) im 3D-Viewer
  angehoben. Die Werte sind in die Bibliotheks-Footprints übernommen. S2 laut
  Stückliste Bourns 1543-650-149. Mouser nicht abrufbar, SnapEDA nur mit
  Anmeldung, daher STEP aus Datenblattmaßen mit `cadquery-ocp` erzeugt und im
  Render geprüft. LEDs auf die vorhandenen Würth-Originalmodelle umgestellt
  (vorher übersehen, KiCad-Ersatz verworfen), im Render geprüft. DRC
  unverändert. Task abgeschlossen.

## Commits

- 00b777d 3D-Modelle ergänzt (S2 offen)
- 438ef75 S2-Modell, Würth-LED-Modelle, Z-Versatz in Bibliothek

## Offene Fragen

- Keine.
