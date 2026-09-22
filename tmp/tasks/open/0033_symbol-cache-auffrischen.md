---
status: open
priority: medium
type: bugfix
created: 2026-09-22
jira: SHBS-14
---

# Symbol-Cache im Schaltplan auffrischen (GUI)

## Kontext

Folgetask zu 0032. Nachdem die Bibliotheken auf KiCad-9-Format gehoben sind,
muss der Symbol-Cache im Schaltplan aus den Bibliotheken neu geschrieben
werden — sonst bleiben die vier `lib_symbol_mismatch`-Warnungen stehen.

**Das geht nur in der KiCad-GUI.** `kicad-cli` bietet keinen Befehl, um den
`lib_symbols`-Block einer Schaltplandatei neu zu erzeugen.

## Achtung — Footprint-Zuweisungen

Beim Auffrischen darf das **Footprint-Feld nicht ueberschrieben** werden.
Die Zuweisungen sind pro Instanz gesetzt und in den Tasks 0001/0003/0005
muehsam erarbeitet worden. Im Dialog *Symbole aus Bibliothek aktualisieren*
die Option zum Zuruecksetzen von Feldern entsprechend abwaehlen.

Vor dem Schritt sichert Task 0032 die Stueckliste als Referenz — damit laesst
sich hinterher belegen, dass keine Footprint-Zuweisung verloren ging.

## Schritte (Bediener)

- [ ] `BasisStation.kicad_sch` in KiCad 9 oeffnen.
- [ ] *Werkzeuge > Symbole aus Bibliothek aktualisieren* fuer `S2`, `C7`,
      `C10`, `C12` (oder projektweit), **ohne** Ruecksetzen der
      Footprint-Felder.
- [ ] Speichern.

## Schritte (Agent, danach)

- [ ] Stueckliste exportieren und gegen die Referenz aus 0032 diffen —
      Footprint-Spalte muss identisch sein.
- [ ] Netzliste diffen — muss identisch sein.
- [ ] ERC: die vier `lib_symbol_mismatch` sind verschwunden.

## Done-Bedingung

Vier Warnungen weg, Footprint-Zuweisungen und Netzliste nachweislich
unveraendert.
