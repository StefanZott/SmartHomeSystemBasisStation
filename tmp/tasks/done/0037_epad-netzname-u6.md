---
status: done
priority: medium
type: bugfix
created: 2026-09-22
jira: SHBS-14
---

# multiple_net_names an U6.41: Ursache statt Symptom beheben

## Kontext

Nach der GUI-Sitzung vom 2026-09-22 meldet die KiCad-GUI **0 Verstoesse**,
`kicad-cli sch erc` aber weiterhin **1 Warnung**:

```
[multiple_net_names]: Both GND and EPAD are attached to the same items
    Symbol #PWR04 Pin 1 [Power input, Line]
    Symbol U6 Hidden pin 41 [EPAD, Power input, Line]
```

## Befund

Ein JSON-Export der ERC (`--severity-all --format json`) zeigt, dass es
**zwei getrennte Instanzen** dieser Warnung gibt:

| Instanz | Partner-Symbol | UUID | ausgeschlossen |
| ------- | -------------- | ---- | -------------- |
| 1 | `#PWR06` @ (222,25 / 111,76) | `b0c4c90b-…` | **ja** |
| 2 | `#PWR04` @ (241,30 / 139,70) | `9468f463-…` | **nein** |

Ein aelterer GUI-Report nannte zusaetzlich `#PWR05`. Welches
GND-Power-Symbol KiCad mit dem EPAD-Pin paart, ist also **nicht stabil** —
es haengt von der Durchlaufreihenfolge ab und unterscheidet sich zwischen
GUI und CLI.

**Folge: Ausschliessen per UUID ist hier untauglich.** Die in Task 0035
hinterlegte Ausnahme deckt genau eine Instanz ab. Sobald Power-Symbole neu
nummeriert werden oder ein anderes Werkzeug die ERC faehrt, taucht die
Warnung wieder auf. Die GUI zeigte nur deshalb 0, weil ihr Lauf lediglich
die bereits ausgeschlossene Instanz erzeugte.

## Ursache

`U6` Pin 41 ist ein **versteckter** `power_in`-Pin mit dem Namen `EPAD`
(so in Bibliothek und Schaltplan-Cache uebereinstimmend; in SHBS-7 bewusst
"versteckt gestapelt" angelegt).

Versteckte Power-Pins verbinden sich in KiCad implizit mit einem globalen
Netz, das **nach dem Pinnamen** heisst — hier also `EPAD`. Gleichzeitig ist
Pin 41 physisch verdrahtet (Leitung von (105,41 / 139,70) nach
(105,41 / 144,78)) und landet damit auf `GND`. Zwei Netznamen an denselben
Elementen → `multiple_net_names`.

Sachlich ist die Verdrahtung korrekt: Das Exposed Pad des
ESP32-S3-WROOM-Moduls **ist** GND. Nur der Pinname weicht ab.

## Loesungsoptionen

**A — Pin 41 in der Bibliothek von `EPAD` auf `GND` umbenennen (empfohlen)**

Das implizite Netz heisst dann `GND` und deckt sich mit der expliziten
Verdrahtung, der Konflikt entfaellt ersatzlos. Die Pin**nummer** bleibt 41,
die Zuordnung zum Footprint-Pad aendert sich also nicht. Die Pins 1 und 40
heissen bereits `GND`.
Nachteil: Der Name `EPAD` als Hinweis auf das Exposed Pad geht im Symbol
verloren — laesst sich ueber die Symbolbeschreibung auffangen.

**B — Pin 41 sichtbar machen**

Sichtbare Power-Pins erzeugen kein implizites Netz; Pin 41 haengt dann nur
noch an der vorhandenen Leitung. Widerspricht aber der Festlegung aus
SHBS-7 ("EPAD versteckt gestapelt") und aendert das Schaltplanbild.

**C — zweite Ausnahme nachtragen**

Nur Symptombehandlung, siehe oben. Nicht empfohlen.

## Schritte

- [ ] Entscheidung des Bedieners zu A / B / C einholen.
- [ ] Umsetzung in `pcb/Bauteile/ESP32-S3-WROOM-1U-N16R8/…kicad_sym`.
- [ ] Symbol-Cache fuer `U6` in der GUI auffrischen.
- [ ] Bei A oder B: die jetzt gegenstandslose `multiple_net_names`-Ausnahme
      aus `BasisStation.kicad_pro` entfernen.
- [ ] `kicad-cli sch erc` — 0 Fehler, 0 Warnungen.
- [ ] Netzliste gegenpruefen: `U6.41` muss weiterhin auf `GND` liegen.
- [ ] `docs/project/hardware.md` ergaenzen.

## Done-Bedingung

CLI und GUI melden beide 0 Verstoesse, Konnektivitaet unveraendert.

## Fortschritt

- 2026-09-22: **Erledigt — Option A** (Bediener-Entscheidung).
  Pin 41 in `pcb/Bauteile/ESP32-S3-WROOM-1U-N16R8/…kicad_sym` von `EPAD` auf
  `GND` umbenannt, Symbolbeschreibung um den Hinweis auf das Exposed Pad
  ergaenzt. Derselbe Stand im Symbol-Cache von
  `BasisStation_Layout.kicad_sch` nachgezogen, damit kein neuer
  `lib_symbol_mismatch` entsteht — dadurch war keine GUI-Sitzung noetig.
- Die gegenstandslos gewordene `multiple_net_names`-Ausnahme aus
  `BasisStation.kicad_pro` entfernt. Verbleibt genau **eine** Ausnahme
  (`pin_to_pin`).
- Verifikation: `kicad-cli sch erc` meldet **0 Fehler, 0 Warnungen**. Der
  JSON-Export mit `--severity-all` zeigt insgesamt nur noch **einen**
  Verstoss, den bewusst ausgeschlossenen `pin_to_pin`. Beide Instanzen von
  `multiple_net_names` sind an der Wurzel verschwunden.
- Konnektivitaet der Netzliste **bitweise identisch** zum Stand vor SHBS-14
  (102 Netze), Stueckliste identisch. `U6.41` liegt weiterhin auf `GND`,
  nur die `pinfunction` lautet jetzt `GND` statt `EPAD`.
