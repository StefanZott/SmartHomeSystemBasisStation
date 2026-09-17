---
status: open
priority: high
type: feature
created: 2026-09-17
jira: SHBS-5
parent_jira: SHBS-3
---

# RJ45-Buchse, Leitungsterminierung und Link-LEDs im Schaltplan

## Ziel

Buchsenseite der Ethernet-Sektion auf dem Blatt `Ethernet.kicad_sch`
ergänzen: RJ45 mit integrierten Magnetics, Terminierung, Schirmanbindung und
Link-/Activity-LEDs.

Setzt Tasks `0002` und `0003` voraus.

## Aufgaben

1. RJ45-Buchse (Typ aus Task `0002`) platzieren und differenzielle Paare
   `TXP`/`TXN` und `RXP`/`RXN` mit dem W5500 verbinden.
2. **Mittelanzapfungen** der Übertrager gemäss Datenblatt beschalten —
   üblicherweise über je einen Kondensator gegen GND oder gegen eine gefilterte
   Versorgung. Verbindlich ist das Applikationsbeispiel des Buchsen-Datenblatts
   in Kombination mit dem W5500-Referenzdesign.
   **Achtung (WIZnet-Referenz):** Sind die Mittelanzapfungen *innerhalb* des
   Übertragers bzw. der RJ45-Buchse bereits zusammengefasst, muss das
   Anpassnetzwerk der `RX±`-Seite (2 × 50 Ω) **galvanisch vom CT-Knoten
   (3,3 V) getrennt** werden. Vor dem Zeichnen im Datenblatt der gewählten
   Buchse prüfen, ob die CTs intern verbunden sind.
3. **Bob-Smith-Terminierung** auf der Leitungsseite: je 75 Ω von den vier
   ungenutzten Paaren bzw. den Mittelpunkten auf einen gemeinsamen Knoten,
   von dort über einen HV-Kondensator (mind. 2 kV) gegen Chassis-GND.
4. **Schirmanbindung:** Schirm der Buchse auf ein separates `CHASSIS`-Netz.
   Die Verbindung zu Signal-GND als **bestückbare Option** ausführen (0-Ω-Brücke
   plus paralleler HV-Kondensator), damit die Kopplung bei EMV-Problemen
   umkonfiguriert werden kann, ohne die Platine zu ändern.
5. **Link-/Activity-LEDs:** LED-Ausgänge des W5500 sind **active low** und
   treiben gegen GND. Vorwiderstände nach dem Muster der Status-LEDs
   dimensionieren (vgl. `R13`–`R16`, 220 Ω). Prüfen, ob die gewählte Buchse
   die LEDs bereits integriert — dann entfallen diskrete LEDs.
6. Referenzen fortlaufend zur bestehenden Nummerierung vergeben (aktuell
   höchste: `R26`, `D12`, `C15`, `J6`, `U6`).
7. ERC laufen lassen; auf dem `CHASSIS`-Netz ein `PWR_FLAG` setzen, sonst
   meldet KiCad ein nicht getriebenes Netz.

## Sollbeschaltung RJ45 (`J?`, Würth 7499011121A)

Der Bediener zeichnet in KiCad; der Agent prüft danach gegen die Netzliste.

**Die Buchse bringt Bob-Smith-Terminierung und den 2-kV-Kondensator bereits
mit** (4 × 75 Ω + 1 nF/2 kV, Datenblatt S. 2, an den Kabelkontakten 4, 5, 7 und 8 —
nicht zu verwechseln mit Schaltplan-Referenzen).
Extern ist dafür **nichts** zu bauen. Übertrager 1:1, 350 µH — deckt sich mit
der Forderung des W5500-Datenblatts (Abschnitt 5.5.5).

### Signalpaare

| Buchsen-Pin | Signal | Netz |
| ----------- | ------ | ---- |
| 1 | `TD+` | `ETH_TXP` |
| 3 | `TD−` | `ETH_TXN` |
| 4 | `RD+` | `ETH_RXP` |
| 6 | `RD−` | `ETH_RXN` |

> **Fallstrick:** Eine Textextraktion des Datenblatt-Schaltbilds liefert die
> Reihenfolge `RD+, CRD, RD−, TD+, CTD, TD−` — **Sende- und Empfangspaar
> vertauscht**. Die obige Zuordnung wurde über die Koordinaten der
> Beschriftung im PDF geprüft und stimmt mit dem offiziellen Würth-Symbol
> überein.

### Mittelanzapfungen — vor dem Zeichnen klären

| Buchsen-Pin | Signal |
| ----------- | ------ |
| 2 | `CTD` (Mittelanzapfung Sendepfad) |
| 5 | `CRD` (Mittelanzapfung Empfangspfad) |

Beide sind **getrennt herausgeführt**, nicht intern verbunden. Das ist
günstig: Der WIZnet-Hinweis, wonach bei intern verbundenen CT-Signalen das
Anpassnetzwerk der `RX±`-Seite vom CT-Knoten getrennt werden muss, greift
hier nicht.

**Offener Punkt:** Ob `CTD` und `CRD` auf `+3V3` (mit Abblockung) oder über
Kondensator auf `GND` gehen, ist gegen das **W5500-Referenzschaltbild** von
WIZnet zu prüfen — der Sendetreiber des W5500 arbeitet stromgesteuert, was
üblicherweise eine gespeiste Sende-Mittelanzapfung verlangt. Das
Chip-Datenblatt zeigt die Beschaltung nur als Grafik (Abbildung 24), nicht als
Text. **Vor dem Zeichnen im Referenzschaltbild nachsehen, nicht raten** — eine
falsch beschaltete Mittelanzapfung verschlechtert die Signalqualitaet, ohne
dass es beim Funktionstest auffällt.

### Schirm und unbenutzte Pins

| Buchsen-Pin | Beschaltung |
| ----------- | ----------- |
| `S1`, `S2` | Netz `CHASSIS` |
| 7, 8 | offen lassen, No-Connect-Flag |

Kopplung `CHASSIS` gegen `GND` als **bestückbare Option**: 0-Ω-Brücke parallel
zu einem HV-Kondensator (mind. 2 kV). So lässt sich das Verhalten bei
EMV-Problemen ohne Platinenänderung umkonfigurieren. `PWR_FLAG` auf `CHASSIS`
setzen, sonst meldet ERC ein nicht getriebenes Netz.

### Link- und Activity-LEDs

Die LEDs sitzen in der Buchse. Die LED-Ausgänge des W5500 sind **active low**
und ziehen gegen `GND` — die Anode liegt daher über den Vorwiderstand auf
`+3V3`.

| Buchsen-Pin | Funktion | Beschaltung |
| ----------- | -------- | ----------- |
| 11 | LED grün, Anode | über **220 Ω** nach `+3V3` |
| 12 | LED grün, Kathode | `ETH_LINKLED` → W5500 Pin 25 |
| 9 | LED gelb, Anode | über **220 Ω** nach `+3V3` |
| 10 | LED gelb, Kathode | `ETH_ACTLED` → W5500 Pin 27 |

Dimensionierung: Flussspannung laut Würth-Datenblatt 1,8–2,4 V bei 20 mA. Bei
3,3 V und 220 Ω stellen sich rund **6 mA** ein — konsistent zu den
Status-LEDs `D7`–`D10` des Projekts, die ebenfalls 220 Ω verwenden.

## Akzeptanzkriterien

- [ ] RJ45 im Schaltplan, alle acht Leitungspins und der Schirm beschaltet.
- [ ] Differenzielle Paare zum W5500 vollständig, Netznamen sprechend.
- [ ] Mittelanzapfungen und Bob-Smith-Terminierung gegen Datenblatt geprüft.
- [ ] Schirmanbindung als bestückbare Option (0 Ω ‖ HV-C) ausgeführt.
- [ ] Link-/Activity-Anzeige vorhanden (integriert oder diskret).
- [ ] ERC ohne neue Fehler.

## Betroffene Dateien

- `pcb/BasisStation/Ethernet.kicad_sch`
- `pcb/BasisStation/ERC.rpt`
