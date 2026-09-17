---
status: open
priority: high
type: feature
created: 2026-09-17
jira: SHBS-5
parent_jira: SHBS-3
---

# W5500-Block im Schaltplan: SPI-Anbindung, Takt, Bias, Versorgung

## Ziel

Neues Schaltplanblatt `Ethernet.kicad_sch` mit dem W5500-Controller und seiner
Anbindung an den ESP32-S3. Die Buchsenseite (RJ45, Magnetics, Link-LEDs) ist
Gegenstand von Task `0004`.

Setzt Task `0002` voraus (Symbole/Footprints).

## GPIO-Zuordnung

Sechs Signale werden benötigt. Laut `pcb/BasisStation/BasisStation.net` sind
GPIO1–GPIO18, GPIO45 und GPIO46 frei. Auszuwählen ist **ausschliesslich aus
GPIO4–GPIO18**:

| Gesperrt | Grund |
| -------- | ----- |
| GPIO35, GPIO36, GPIO37 | Beim Modul **N16R8** intern vom Octal-PSRAM belegt — erscheinen in der Netzliste fälschlich als frei |
| GPIO3, GPIO45, GPIO46 | Strapping-Pins; GPIO3 zusätzlich JTAG-Quellenwahl (relevant wegen `J5`) |
| GPIO19, GPIO20 | USB D−/D+ am Debug-Port `J1` |
| GPIO1, GPIO2 | Frei, aber ADC1/Touch — für spätere Sensorik reservieren |

Vorschlag (im Task nach Festlegung eintragen): SCLK, MOSI, MISO, CS, INT, RST
auf sechs Pins aus GPIO4–GPIO18. Die gewählte Belegung ist **verbindlich für
die Firmware-Umsetzung in SHBS-11** — nach der Festlegung hier dokumentieren
und im Ticket SHBS-11 nachtragen.

**Hinweis:** Der W5500 hängt an einem beliebigen GPIO-Satz — der ESP32-S3
routet SPI über die GPIO-Matrix. Oberhalb ca. 40 MHz SPI-Takt wären die
IO-MUX-Pins von FSPI vorzuziehen; das ist hier nicht zu erwarten und sollte
die Wahl unkritischer Pins nicht verdrängen.

## Aufgaben

1. Blatt `Ethernet.kicad_sch` anlegen und in `BasisStation.kicad_sch` als
   Hierarchie-Blatt einhängen (Muster: `Stromversorgung.kicad_sch`).
2. GPIO-Belegung festlegen und in dieser Datei dokumentieren.
3. W5500 beschalten. Werte aus dem Datenblatt Rev. 1.0.5 (Tabelle 2,
   S. 9–12) verifiziert — siehe Pinbelegung unten.
4. SPI-Netze zum Modul `U6` benennen (`ETH_SCLK`, `ETH_MOSI`, `ETH_MISO`,
   `ETH_CS`, `ETH_INT`, `ETH_RST`) — keine anonymen `Net-(…)`-Namen.
5. ERC auf dem neuen Blatt laufen lassen.

## W5500-Pinbelegung (LQFP-48, Datenblatt Rev. 1.0.5)

Verifiziert am 17.09.2026 gegen `pcb/Datasheets/Wiznet_W5500_DS_1 0 5.pdf`,
Tabelle 2 „W5500 Pin Description".

| Pin | Name | Typ | Beschaltung |
| --- | ---- | --- | ----------- |
| 1, 2 | `TXN`, `TXP` | AO | Differenzielles Sendepaar → RJ45 |
| 5, 6 | `RXN`, `RXP` | AI | Differenzielles Empfangspaar ← RJ45 |
| 3, 9, 14, 16, 19, 48 | `AGND` | GND | Analogmasse |
| 4, 8, 11, 15, 17, 21 | `AVDD` | PWR | Analog 3,3 V — Abblockung je Pin |
| 7 | `DNC` | AI/O | **Do Not Connect** |
| 10 | `EXRES1` | AI/O | **12,4 kΩ ± 1 %** gegen `AGND` |
| 12, 13, 46, 47 | — | NC | unbeschaltet |
| 18 | `VBG` | AO | Bandgap 1,2 V — **muss offen bleiben** |
| 20 | `TOCAP` | AO | **4,7 µF** gegen GND, Leiterbahn kurz halten |
| 22 | `1V2O` | AO | Ausgang des internen **1,2-V**-Reglers, **10 nF** gegen GND |
| 23 | `RSVD` | I | **Auf GND legen** |
| 24 | `SPDLED` | O | Speed: low = 100 Mbit/s |
| 25 | `LINKLED` | O | Link: low = Link steht |
| 26 | `DUPLED` | O | Duplex: low = Full Duplex |
| 27 | `ACTLED` | O | Activity: low = Carrier Sense |
| 28 | `VDD` | PWR | Digital 3,3 V |
| 29 | `GND` | GND | Digitalmasse |
| 30 | `XI/CLKIN` | AI | 25-MHz-Quarz bzw. TTL-Oszillator |
| 31 | `XO` | AO | Quarz; bei externem Oszillator **offen lassen** |
| 32 | `SCSn` | I | SPI Chip Select, intern Pull-up |
| 33 | `SCLK` | I | SPI-Takt |
| 34 | `MISO` | O | SPI Daten zum ESP32 |
| 35 | `MOSI` | I | SPI Daten vom ESP32 |
| 36 | `INTn` | O | Interrupt, active low |
| 37 | `RSTn` | I | Reset, active low, intern Pull-up |
| 38–42 | `RSVD` | I | **NC** — nicht mit Pin 23 verwechseln |
| 43, 44, 45 | `PMODE2`, `PMODE1`, `PMODE0` | I | Betriebsart, intern Pull-up |

### Punkte, die leicht falsch gemacht werden

- **`RSVD` ist nicht gleich `RSVD`:** Pin 23 gehört auf GND, die Pins 38–42
  bleiben offen. Beide heissen im Datenblatt gleich.
- **`VBG` (18) nicht beschalten.** Das Datenblatt verlangt ausdrücklich
  „It must be left floating".
- **Alle vier LED-Ausgänge sind active low** — sie ziehen gegen GND, die
  Anode liegt also auf 3,3 V.
- **`PMODE[2:0]` = `111`** ergibt „All capable, Auto-negotiation enabled" —
  das Ziel. Alle drei Pins haben interne Pull-ups, offen lassen liefert also
  bereits `111`. Trotzdem Pads für Pull-down-Widerstände vorsehen, um die
  Betriebsart im Fehlerfall festnageln zu können.
- **`RSTn` mindestens 500 µs low halten** — relevant für die
  Firmware-Initialisierung in SHBS-11, hier nur als RC-Dimensionierung.

### Erforderliche Zusatzbauteile

| Bauteil | Wert | Pin |
| ------- | ---- | --- |
| Bias-Widerstand | 12,4 kΩ, 1 % | `EXRES1` (10) |
| Ladekondensator | 4,7 µF | `TOCAP` (20) |
| Reglerkondensator | 10 nF | `1V2O` (22) |
| Quarz | 25 MHz + Lastkondensatoren nach Quarz-Datenblatt | `XI`/`XO` (30/31) |
| Abblockung | je 100 nF an jedem `AVDD`/`VDD` | 4, 8, 11, 15, 17, 21, 28 |

## Akzeptanzkriterien

- [ ] `Ethernet.kicad_sch` existiert und ist hierarchisch eingebunden.
- [ ] Alle W5500-Pins beschaltet oder bewusst als No-Connect markiert.
- [ ] Quarz, Bias-Widerstand (12,4 kΩ 1 %), `TOCAP` (4,7 µF), `1V2O` (10 nF),
      Entkopplung und PMODE gemäss Pinbelegungstabelle umgesetzt.
- [ ] Pin 23 auf GND, Pins 38–42 offen, `VBG` (18) und `DNC` (7) offen.
- [ ] GPIO-Belegung festgelegt, aus GPIO4–GPIO18, in dieser Datei dokumentiert.
- [ ] SPI-Netze tragen sprechende Namen.
- [ ] ERC ohne neue Fehler (`pcb/BasisStation/ERC.rpt`).

## Betroffene Dateien

- `pcb/BasisStation/Ethernet.kicad_sch` (neu)
- `pcb/BasisStation/BasisStation.kicad_sch` (Blatt einhängen)
- `pcb/BasisStation/ERC.rpt`
