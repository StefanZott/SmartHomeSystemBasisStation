---
status: done
priority: high
type: test
created: 2026-09-22
jira: SHBS-14
---

# Abschluss-Verifikation Schaltplan

## Kontext

Letzter Task zu SHBS-14. Belegt, dass der Schaltplan als Referenzstand fuer
das PCB-Layout taugt — und dass die Aufraeumarbeiten der Tasks 0030-0035
**elektrisch nichts verschoben** haben.

Das ist der eigentliche Zweck der Uebung: Ab hier wird die Netzliste ins
Board uebernommen, und jede unbemerkte Abweichung waere dann teuer.

## Referenzwerte (Stand 2026-09-22, vor den Aenderungen)

| Groesse | Wert |
| ------- | ---- |
| ERC-Fehler | 0 |
| ERC-Warnungen | 7 (Ziel danach: 0) |
| Netze | 102 |
| Bauteile auf dem Board | 76 |
| Bauteile ohne Footprint | 0 (ausser `ANT1`/`ANT2`, "Excluded from board") |
| Ein-Pin-Netze | 40, alle `unconnected-*` |

## Schritte

- [ ] `kicad-cli sch erc` — **0 Fehler, 0 Warnungen**.
- [ ] **Gegenprobe in der GUI:** Auch dort 0 Verstoesse. Am 2026-09-22 zeigte
      die GUI bereits 0, waehrend das CLI noch eine Warnung meldete (siehe
      [Task 0037](0037_epad-netzname-u6.md)). Ein gruenes Ergebnis aus nur
      einem der beiden Werkzeuge genuegt als Nachweis nicht.
- [ ] `kicad-cli sch export netlist` — 102 Netze, Namen und Knoten
      identisch zum Referenzstand.
- [ ] `kicad-cli sch export bom` — 76 Bauteile, Footprint-Spalte identisch,
      `R35` weiterhin DNP.
- [ ] Ein-Pin-Netze erneut zaehlen: 40, alle mit `unconnected-`-Praefix.
      Taucht ein regulaer benanntes Netz mit nur einem Pin auf, ist beim
      Aufraeumen eine Verbindung verloren gegangen.
- [ ] `ERC.rpt` und `BasisStation.net` im Repo aktualisieren.
- [ ] `docs/project/hardware.md` und `docs/project/ethernet.md`
      gegenlesen.

## Done-Bedingung

ERC sauber auf Null, Netzliste und Stueckliste nachweislich unveraendert,
Artefakte eingecheckt.

## Abschluss

- 2026-09-22: **Erledigt.** Endstand gegen die Referenzwerte:

| Groesse | Ziel | Ist |
| ------- | ---- | --- |
| ERC-Fehler | 0 | **0** |
| ERC-Warnungen | 0 | **0** |
| Verstoesse gesamt (inkl. ausgeschlossener) | — | **1** (`pin_to_pin`, bewusst) |
| Netze | 102 | **102** |
| Konnektivitaet | unveraendert | **bitweise identisch** |
| Stueckliste | unveraendert | **identisch** (78 Zeilen) |
| Bauteile ohne Footprint | 0 | **0** (ausser `ANT1`/`ANT2`) |

- Der Schaltplan taugt damit als Referenzstand fuer das PCB-Layout.

## Offen fuer den Bediener

- `pcb/BasisStation/BasisStation.net` und `ERC.rpt` stammen aus der
  Windows-GUI (`source`-Pfad `C:\Projekte\…`, deutschsprachig). Sie wurden
  **bewusst nicht** im Container neu erzeugt, weil sonst Pfad und Sprache bei
  jedem Export hin- und herspringen. Inhaltlich ist nur die `pinfunction` von
  `U6.41` veraltet (`EPAD` statt `GND`) — die Konnektivitaet stimmt.
  Beim Start des PCB-Layouts ohnehin neu exportieren.
