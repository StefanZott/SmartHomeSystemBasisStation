---
status: done
priority: low
type: bugfix
created: 2026-09-22
jira: SHBS-14
---

# Verwaiste Schaltplan-Datei entfernen

## Kontext

`pcb/BasisStation/BasisStation_architektur.kicad_sch` (1271 Zeilen) ist in der
Schaltplan-Hierarchie **nicht referenziert**. Weder das Root-Blatt noch die
`sheets`-Sektion in `BasisStation.kicad_pro` fuehren sie. Sie geht damit in
kein ERC, keine Netzliste und keine Stueckliste ein.

Der Befund ist nicht neu: Schon der Report vom 2026-09-06 fuehrt sie als
Befund B6 ("ist verwaist"), die Analyse vom 2026-06-05 als
"Variante/Duplikat des Root-Blatts". Bediener-Entscheidung vom 2026-09-22:
Altlast, loeschen.

## Schritte

- [ ] `pcb/BasisStation/BasisStation_architektur.kicad_sch` entfernen.
- [ ] `docs/project/hardware.md` Zeile 148: Datei aus der Aufzaehlung der
      Schaltplaene streichen.
- [ ] `kicad-cli sch erc` gegenpruefen — Ergebnis muss unveraendert bleiben
      (7 Verstoesse, 0 Fehler), da die Datei nie Teil der Hierarchie war.

## Done-Bedingung

Datei entfernt, `hardware.md` aktualisiert, ERC-Ergebnis unveraendert.

## Fortschritt

- 2026-09-22: **Erledigt.** `BasisStation_architektur.kicad_sch` per `git rm`
  entfernt. `docs/project/hardware.md` Zeile 148 korrigiert — bei der
  Gelegenheit fiel auf, dass die Aufzaehlung `Stromversorgung.kicad_sch` und
  `ethernet.kicad_sch` gar nicht enthielt; die Zeile listet jetzt das
  Root-Blatt mit allen vier Unterblaettern.
- Verifikation: ERC-Report und Netzliste vor/nach dem Loeschen gediffed —
  **beide identisch**. Die Datei war nie Teil der Hierarchie.
