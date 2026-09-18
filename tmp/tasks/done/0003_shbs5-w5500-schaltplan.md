---
status: done
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
| GPIO3, GPIO45, GPIO46 | Strapping-Pins; GPIO3 wählt zwischen internem USB-Serial-JTAG und externen JTAG-Pins |
| GPIO19, GPIO20 | USB D−/D+ am Debug-Port `J1` |
| GPIO1, GPIO2 | Frei, aber ADC1/Touch — für spätere Sensorik reservieren |

### Festgelegt (Bediener, 17.09.2026)

| Netz | W5500-Pin | GPIO | Modul-Pad | Begründung |
| ---- | --------- | ---- | --------- | ---------- |
| `ETH_RST` | **37** `RSTn` | **9** | 17 | FSPIHD, hier als Reset |
| `ETH_SCSn` | **32** `SCSn` | **10** | 18 | FSPICS0 |
| `ETH_MOSI` | **35** `MOSI` | **11** | 19 | FSPID |
| `ETH_SCLK` | **33** `SCLK` | **12** | 20 | FSPICLK |
| `ETH_MISO` | **34** `MISO` | **13** | 21 | FSPIQ |
| `ETH_INT` | **36** `INTn` | **14** | 22 | FSPIWP, hier als Interrupt |

> Die Pinnamen am W5500 heißen nicht wie die Netze. Chip-Select heißt am
> Baustein **`SCSn`**, nicht `CS`. Das angehängte `n` bedeutet **active low** —
> betrifft `SCSn`, `RSTn` und `INTn`.

Zwei Gründe für diesen Block:

- **IO-MUX statt GPIO-Matrix.** GPIO10–13 sind die nativen FSPI-Pins des
  ESP32-S3. SPI läuft darüber ohne Umweg über die GPIO-Matrix — bessere
  Signalintegrität bei den 20–40 MHz, die für den W5500 realistisch sind.
- **Zusammenhängende Modul-Pads 17–22.** Ergibt im Layout ein kompaktes
  Bündel zum W5500 statt Leitungen quer über die Platine.

Kosten: GPIO9 und GPIO10 belegen ADC1_CH8 und ADC1_CH9. GPIO11–14 hängen an
ADC2, das mit aktivem WLAN ohnehin kaum nutzbar ist. **GPIO1–GPIO8 bleiben
vollständig frei** für analoge Sensorik, GPIO15–GPIO18 für UART1 oder einen
32-kHz-Quarz.

Diese Belegung ist **verbindlich für die Firmware in SHBS-11**.

## Aufgaben

1. Blatt `Ethernet.kicad_sch` anlegen und in `BasisStation.kicad_sch` als
   Hierarchie-Blatt einhängen (Muster: `Stromversorgung.kicad_sch`).
2. ~~GPIO-Belegung festlegen und in dieser Datei dokumentieren.~~ **erledigt**
3. W5500 beschalten. Werte aus dem Datenblatt Rev. 1.0.5 (Tabelle 2,
   S. 9–12) verifiziert — siehe Pinbelegung unten.
4. ~~SPI-Netze zum Modul `U6` benennen~~ — **erledigt am 18.09.2026**, alle
   sechs Verbindungen gegen das Datenblatt geprüft.
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

### Zusatzbauteile

Vollständig mit Werten, Symbolen und Footprints in der **Stückliste** weiter
unten; wie sie angeschlossen werden, steht in der **Sollbeschaltung**.

## Arbeitsteilung

Der **Bediener zeichnet** das Blatt in KiCad. Der Agent liefert die
Sollbeschaltung unten und prüft anschliessend `BasisStation.net` Pin für Pin
gegen das Datenblatt — wie bei den LED-Treibern in SHBS-9.

## Sollbeschaltung W5500 (`U7`)

Alle Pinnummern nach Datenblatt Rev. 1.0.5, Tabelle 2.

### Versorgung

Versorgungspins direkt aufs Netz:

| W5500-Pin | Netz |
| --------- | ---- |
| 28 `VDD` | `+3V3` |
| 4, 8, 11, 15, 17, 21 `AVDD` | `+3V3` |
| 29 `GND` | `GND` |
| 3, 9, 14, 16, 19, 48 `AGND` | `GND` |

Abblockung — **ein Kondensator je Versorgungspin**, jeder unmittelbar an
seinem Pin platziert:

| Bauteil | von | nach | Platzierung |
| ------- | --- | ---- | ----------- |
| 100 nF | Pin 4 `AVDD` | `GND` | an Pin 4 |
| 100 nF | Pin 8 `AVDD` | `GND` | an Pin 8 |
| 100 nF | Pin 11 `AVDD` | `GND` | an Pin 11 |
| 100 nF | Pin 15 `AVDD` | `GND` | an Pin 15 |
| 100 nF | Pin 17 `AVDD` | `GND` | an Pin 17 |
| 100 nF | Pin 21 `AVDD` | `GND` | an Pin 21 |
| 100 nF | Pin 28 `VDD` | `GND` | an Pin 28 |
| 10 µF | `+3V3` | `GND` | einmal am Baustein, dort wo `+3V3` die Sektion erreicht |

Die sieben 100 nF sitzen elektrisch alle am selben Netz `+3V3`. Im Schaltplan
trotzdem **einzeln je Pin zeichnen** — sonst geht im Layout die Zuordnung
verloren, und genau die Kurzstrecke Pin-Kondensator-Masse ist der Zweck der
Abblockung.

### Analoge Stützbeschaltung

| Bauteil | von | nach | Hinweis |
| ------- | --- | ---- | ------- |
| 12,4 kΩ, **1 %** | Pin 10 `EXRES1` | `GND` | Das Datenblatt verlangt ausdrücklich **Analogmasse (AGND)**. Führt das Projekt nur ein `GND`-Netz, ist das schaltplanseitig dasselbe — im Layout aber an die Analogmasse anbinden. Toleranz nicht aufweichen, der Widerstand stellt die Sendeamplitude ein |
| 4,7 µF | Pin 20 `TOCAP` | `GND` | Leiterbahn so kurz wie möglich |
| 10 nF | Pin 22 `1V2O` | `GND` | Ausgang des internen 1,2-V-Reglers |

Zwei Pins bleiben **unbeschaltet**:

| W5500-Pin | Beschaltung |
| --------- | ----------- |
| 18 `VBG` | offen, **No-Connect-Flag setzen** |
| 7 `DNC` | offen lassen, **kein Flag nötig** |

`VBG` ist im Symbol vom Typ `passive` und braucht das Flag, sonst meldet ERC
ihn als unverbunden. `DNC` ist dagegen vom Typ `no_connect` — ebenso die Pins
12, 13, 46 und 47. Die meldet ERC ohnehin nicht.

### Takt

**Quarz `Y1`: Würth 830059532** (WE-XTAL, Bauform CFPX-104, 3,2 × 5,0 mm).

Pinbelegung des Quarzes — **Anschlüsse sind 1 und 3**, nicht 1 und 2:

| `Y1`-Pin | Name im Symbol | Funktion |
| -------- | -------------- | -------- |
| **1** | `1` | Quarzanschluss |
| **3** | `3` | Quarzanschluss |
| 2 | `GND` | Gehäuse |
| 4 | `GND1` | Gehäuse |

Die Pads 1 und 3 liegen im Footprint diagonal gegenüber, ebenso 2 und 4 — die
übliche Anordnung bei 4-Pad-SMD-Quarzen.

### Verdrahtung des Taktkreises

```text
  W5500 Pin 30                  Y1 Pin 1
  XI/CLKIN  ──────┬──────────────┤
                  │              │  Quarz
                 ═╪═ C? 27 pF    │  830059532
                  │              │  25 MHz
                 GND             │
                                 │
  W5500 Pin 31                  Y1 Pin 3
  XO        ──────┬──────────────┤
                  │
                 ═╪═ C? 27 pF
                  │
                 GND

  Y1 Pin 2 (GND)  ── GND        Gehäuse, beide Pins anschliessen
  Y1 Pin 4 (GND1) ── GND
```

Netzweise:

| Netz | Verbindet |
| ---- | --------- |
| `XTAL_IN` | W5500 Pin 30 `XI/CLKIN` ↔ `Y1` Pin 1 ↔ Lastkondensator 27 pF → `GND` |
| `XTAL_OUT` | W5500 Pin 31 `XO` ↔ `Y1` Pin 3 ↔ Lastkondensator 27 pF → `GND` |
| `GND` | `Y1` Pin 2 und Pin 4 (Gehäuse) |

Beide Gehäusepins anschliessen, nicht nur einen — das Metallgehäuse wirkt
sonst als Antenne und koppelt den 25-MHz-Takt in die Umgebung ein.

Anforderungen des W5500 (Datenblatt Rev. 1.0.5, Abschnitt 5.5.3) gegen das
gewählte Teil:

| Parameter | W5500 verlangt | 830059532 |
| --------- | -------------- | --------- |
| Frequenz | 25 MHz | 25 MHz |
| Toleranz bei 25 °C | ±30 ppm | **±20 ppm** |
| Lastkapazität | 18 pF | **18 pF** |
| Stabilität über Temperatur | — | 30 ppm (−40 … +85 °C) |
| Alterung | ±3 ppm/Jahr | typ. innerhalb |

**Lastkondensatoren: 2 × 27 pF**, nicht 22 pF. Rechnung:
`CL = C/2 + C_stray`, mit CL = 18 pF und rund 4 pF Streukapazität folgt
C = 28 pF, nächster Normwert 27 pF. Die Streukapazität ist eine Annahme —
bei stark abweichender Leiterbahnführung nachrechnen.

**Dielektrikum der Lastkondensatoren: C0G/NP0**, nicht X7R. X7R driftet über
Temperatur und Spannung um zweistellige Prozentsätze und verstimmt damit den
Oszillator — genau das, was die ±20 ppm des Quarzes zunichte macht.

Quarz im Layout dicht an den Baustein, Massefläche darunter gemäss
Herstellerangabe.

### SPI und Steuerung zum Modul `U6`

| W5500-Pin | Netz | U6-Pad | Zusatz |
| --------- | ---- | ------ | ------ |
| 32 `SCSn` | `ETH_SCSn` | 18 (GPIO10) | — |
| 33 `SCLK` | `ETH_SCLK` | 20 (GPIO12) | — |
| 35 `MOSI` | `ETH_MOSI` | 19 (GPIO11) | — |
| 34 `MISO` | `ETH_MISO` | 21 (GPIO13) | — |
| 36 `INTn` | `ETH_INT` | 22 (GPIO14) | siehe Pull-up unten |
| 37 `RSTn` | `ETH_RST` | 17 (GPIO9) | siehe Pull-up unten |

Zwei Pull-ups an dieser Gruppe:

| Bauteil | von | nach | Zweck |
| ------- | --- | ---- | ----- |
| 10 kΩ | Pin 36 `INTn` | `+3V3` | `INTn` ist ein Open-Drain-Ausgang und braucht den Pull-up, um überhaupt einen High-Pegel zu liefern |
| 10 kΩ | Pin 37 `RSTn` | `+3V3` | Hält den W5500 im Betrieb, solange der ESP32 beim Booten noch hochohmig ist |

### Betriebsart

| Bauteil | von | nach | Bestückung |
| ------- | --- | ---- | ---------- |
| 10 kΩ | Pin 43 `PMODE2` | `+3V3` | bestückt |
| 10 kΩ | Pin 44 `PMODE1` | `+3V3` | bestückt |
| 10 kΩ | Pin 45 `PMODE0` | `+3V3` | bestückt |
| 10 kΩ | Pin 43 `PMODE2` | `GND` | **unbestückt (DNP)** |
| 10 kΩ | Pin 44 `PMODE1` | `GND` | **unbestückt (DNP)** |
| 10 kΩ | Pin 45 `PMODE0` | `GND` | **unbestückt (DNP)** |

`PMODE[2:0] = 111` ergibt „All capable, Auto-negotiation enabled" — das Ziel.
Die Pins haben interne Pull-ups, offen lassen würde also auch `111` liefern.
Die externen Pull-ups machen die Betriebsart unabhängig vom Baustein eindeutig.

Die drei Pull-downs werden **mitgezeichnet, aber nicht bestückt**. Sie sind die
Rückfallebene: Sollte die Auto-Negotiation mit einem bestimmten Switch nicht
zustande kommen, lässt sich durch Umbestücken — Pull-up runter, Pull-down
drauf — eine feste Betriebsart erzwingen, ohne die Platine zu ändern. In KiCad
über das Feld **DNP** (Do Not Populate) am Bauteil kennzeichnen.

### Stückliste der Zusatzbauteile

Generische Passive nutzen die KiCad-Standardbibliotheken — konsistent zum
übrigen Projekt, das `Device:R`/`Device:C` mit `*_0805_2012Metric` verwendet.
Eigene Bauteilordner bekommen nur herstellerspezifische Teile.

| Bauart | Bauteil | Wert | Symbol | Footprint | Anzahl |
| ------ | ------- | ---- | ------ | --------- | ------ |
| Kondensator | Abblockung `AVDD`/`VDD` | 100 nF, 50 V, X7R | `Device:C` | `Capacitor_SMD:C_0805_2012Metric` | 7 |
| Kondensator | Stützkondensator | 10 µF, 16 V, X5R | `Device:C` | `Capacitor_SMD:C_0805_2012Metric` | 1 |
| Kondensator | `TOCAP` (Pin 20) | 4,7 µF, 16 V, X5R | `Device:C` | `Capacitor_SMD:C_0805_2012Metric` | 1 |
| Kondensator | `1V2O` (Pin 22) | 10 nF, 50 V, X7R | `Device:C` | `Capacitor_SMD:C_0805_2012Metric` | 1 |
| Kondensator | Quarz-Last | 27 pF, 50 V, **C0G/NP0** | `Device:C` | `Capacitor_SMD:C_0805_2012Metric` | 2 |
| **Widerstand** | `EXRES1` (Pin 10) | 12,4 kΩ, **1 %** | `Device:R` | `Resistor_SMD:R_0805_2012Metric` | 1 |
| **Widerstand** | Pull-ups `INTn`, `RSTn`, `PMODE0–2` | 10 kΩ, 5 % | `Device:R` | `Resistor_SMD:R_0805_2012Metric` | 5 |
| Quarz | `Y1` | 25 MHz, CL 18 pF | `wuerth_xtal:CFPX-104_830059532` | `wuerth_830059532:Y_Wurth_WE-XTAL_Quartz-CFPX-104` | 1 |

**Einheiten als Merkhilfe:** Farad (pF, nF, µF) = Kondensator, Ohm (Ω, kΩ) =
Widerstand. In dieser Sektion gibt es nur zwei Widerstände — den Bias an
`EXRES1` und die fünf Pull-ups. Alles andere mit F-Einheit ist Kondensator.

Zwei Toleranzen sind nicht verhandelbar: **1 % an `EXRES1`** (bestimmt die
Sendeamplitude) und **C0G/NP0 bei den Lastkondensatoren** (bestimmt die
Frequenzgenauigkeit).

### Reserviert

| W5500-Pin | Beschaltung |
| --------- | ----------- |
| 23 `RSVD` | **auf `GND` verdrahten** — kein No-Connect-Flag |
| 38, 39, 40, 41, 42 `RSVD` | offen, **No-Connect-Flag setzen** (Typ `input`) |
| 12, 13, 46, 47 (NC) | offen lassen, **kein Flag nötig** (Typ `no_connect`) |

> **Nicht verwechseln:** Pin 23 heisst im Datenblatt genauso `RSVD` wie die
> Pins 38–42, gehört aber auf Masse. Die anderen fünf bleiben offen.

### Zur RJ45-Seite (Details in Task 0004)

| W5500-Pin | Netz |
| --------- | ---- |
| 2 `TXP` | `ETH_TXP` |
| 1 `TXN` | `ETH_TXN` |
| 6 `RXP` | `ETH_RXP` |
| 5 `RXN` | `ETH_RXN` |
| 25 `LINKLED` | `ETH_LINKLED` |
| 27 `ACTLED` | `ETH_ACTLED` |
| 24 `SPDLED` | offen, **No-Connect-Flag** |
| 26 `DUPLED` | offen, **No-Connect-Flag** |

Die Würth-Buchse hat nur zwei LEDs, deshalb bleiben zwei der vier
LED-Ausgänge ungenutzt. Auch sie brauchen ein No-Connect-Flag, sonst meldet
ERC sie als unverbunden — wie `VBG` und `DNC`.

## Ergebnis (18.09.2026)

Blatt `ethernet.kicad_sch` vom Bediener gezeichnet, vom Agenten geometrisch
gegen die Sollbeschaltung nachgerechnet. **Alle 29 Pin-Prüfungen bestanden**,
18 Bauteile — Soll und Ist identisch.

| Gruppe | Umsetzung |
| ------ | --------- |
| Versorgung | `C16`–`C22`, je 100 nF an Pin 28, 4, 8, 11, 15, 17, 21, alle auf `+3V3`/`GND` |
| Stützkondensator | `C27` 10 µF zwischen `+3V3` und `GND` |
| Masse | Pins 3, 9, 14, 16, 19, 29, 48 sowie Pin 23 `RSVD` |
| Analog | `R27` 12,4 kΩ 1 % an `EXRES1`, `C23` 4,7 µF an `TOCAP`, `C24` 10 nF an `1V2O` |
| Takt | `Y1` (830059532) Pin 1 ↔ `U7.30` + `C25`, Pin 3 ↔ `U7.31` + `C26`, je 27 pF |
| SPI | sechs Netze an Pin 32–37, Gegenseite `U6` Pad 17–22 |
| Pull-ups | `R28`–`R30` an PMODE0–2, `R31` an `INTn`, `R32` an `RSTn`, alle nach `+3V3` |

ERC am 18.09.2026: **0 Fehler, 7 Warnungen** — alle sieben vorbestehend, das
Ethernet-Blatt selbst meldet nichts.

### Verlauf — was unterwegs korrigiert wurde

Die Prüfung lief in mehreren Durchgängen. Gefundene und behobene Punkte:

- **`+3V3` fehlte komplett.** Die sieben Versorgungspins hingen mit ihren
  Abblockkondensatoren auf unbenannten Netzen — der Baustein hatte keine
  Versorgung. Sieben ERC-Fehler.
- **Pin 23 `RSVD`** trug ein No-Connect-Flag statt der vom Datenblatt
  geforderten Masseverbindung.
- **Pull-ups** an `INTn` und `RSTn` fehlten, ebenso die drei an PMODE.
- **Referenz `R27` doppelt vergeben** nach dem Umbenennen von `R21`.
- **10-µF-Stützkondensator** fehlte.

### Fehler in der ursprünglichen Sollbeschaltung

Zwei Angaben des Agenten waren falsch und wurden korrigiert:

- **Quarzanschlüsse**: Die Vorgabe nannte `XO` an Quarz-Pin 2. Pin 2 ist
  jedoch ein Gehäusepin — die Anschlüsse sind **1 und 3**. So gezeichnet
  wäre der Oszillator nie angeschwungen, ohne dass ERC etwas gemeldet hätte.
- **Lastkondensatoren**: zunächst mit 22 pF angegeben. Das Datenblatt verlangt
  CL = 18 pF, daraus folgen **27 pF**.
- **No-Connect-Flags** wurden für die Pins 7, 12, 13, 46, 47 verlangt. Diese
  sind im Symbol vom Typ `no_connect` und brauchen keines.

### Bewusst weggelassen

Die drei DNP-Pull-downs an PMODE (Rückfallebene für eine feste Betriebsart)
wurden nicht gezeichnet. Kein Fehler — der Normalbetrieb mit
Auto-Negotiation funktioniert ohne sie.

## Akzeptanzkriterien

- [x] `ethernet.kicad_sch` existiert und ist hierarchisch eingebunden.
- [x] Alle W5500-Pins beschaltet oder bewusst als No-Connect markiert.
- [x] Quarz, Bias-Widerstand (12,4 kΩ 1 %), `TOCAP` (4,7 µF), `1V2O` (10 nF),
      Entkopplung und PMODE gemäss Pinbelegungstabelle umgesetzt.
- [x] Pin 23 `RSVD` **auf GND** — kein No-Connect-Flag, das Datenblatt
      verlangt eine echte Masseverbindung.
- [x] No-Connect-Flags an 18 `VBG`, 24 `SPDLED`, 26 `DUPLED`, 38–42 `RSVD`.
      Die Pins 7, 12, 13, 46 und 47 sind im Symbol vom Typ `no_connect` und
      brauchen **kein** Flag.
- [x] GPIO-Belegung festgelegt und dokumentiert.
- [x] SPI-Netze tragen sprechende Namen, Verdrahtung am 18.09.2026 geprüft.
- [x] ERC ohne neue Fehler (`pcb/BasisStation/ERC.rpt`).

## Betroffene Dateien

- `pcb/BasisStation/Ethernet.kicad_sch` (neu)
- `pcb/BasisStation/BasisStation.kicad_sch` (Blatt einhängen)
- `pcb/BasisStation/ERC.rpt`
