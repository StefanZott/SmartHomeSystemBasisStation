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
