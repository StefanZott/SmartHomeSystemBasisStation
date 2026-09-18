---
status: active
last_updated: 2026-09-17
type: project-doc
jira: SHBS-5
---

# Ethernet — Anbindung über W5500

Kabelgebundene Netzwerkanbindung der SmartHome-Basisstation. Diese Datei
erklärt das **Warum** der gewählten Architektur; die konkrete Pinbelegung und
der Bauteilstand stehen in [hardware.md](hardware.md), die logische
Kommunikationsschicht in [communication.md](communication.md).

## Warum überhaupt ein Zusatzbaustein?

Der ESP32-S3 hat **keinerlei Ethernet-Hardware**. Anders als der ursprüngliche
ESP32 besitzt er keine EMAC-Peripherie und damit auch keine RMII-Schnittstelle
— ein externer RMII-PHY wie LAN8720 oder IP101 findet im SoC keine Gegenstelle.

Nachweisbar in ESP-IDF: `SOC_EMAC_SUPPORTED` ist in
`components/soc/esp32/include/soc/soc_caps.h` definiert, im Pendant für den
ESP32-S3 fehlt das Symbol.

Was der ESP32-S3 kann, ist SPI. Der **WIZnet W5500** hängt als SPI-Slave daran
und ist die komplette Ethernet-Peripherie in einem Chip — er übersetzt
zwischen „Bytes über sechs Leitungen" und „Signale auf einem Twisted-Pair-Kabel".

```text
ESP32-S3                          W5500                        RJ45
┌──────────────┐  6 Leitungen  ┌────────────────────┐        ┌─────────┐
│ lwIP (TCP/IP)│               │   32 KB Puffer     │        │         │
│      │       │ SCLK ───────► │        │           │        │ Magne-  │
│  esp_eth     │ MOSI ───────► │   MAC (Frames)     │        │ tics    │
│      │       │ MISO ◄─────── │        │           │  TX±   │   │     │
│  SPI-Master  │ CS   ───────► │   PHY (analog) ────┼────────┤   ├─────┼─► Kabel
│              │ INT  ◄─────── │        │           │  RX±   │   │     │
│              │ RST  ───────► │   25-MHz-Quarz     │        │         │
└──────────────┘               └────────────────────┘        └─────────┘
```

## Die zwei Hälften des W5500

| Block | Funktion |
|-------|----------|
| **MAC** (Media Access Control) | Die digitale Hälfte: baut Ethernet-Frames, verwaltet die MAC-Adresse, filtert eingehende Frames, erkennt Kollisionen. Genau die Funktion, die beim originalen ESP32 als EMAC im SoC sitzt und dem S3 fehlt. |
| **PHY** (Physical Layer) | Die analoge Hälfte: erzeugt die Spannungspegel auf dem Kabel, macht die Leitungscodierung für 10BASE-T/100BASE-TX, handelt per Auto-Negotiation Geschwindigkeit und Duplex aus, erkennt den Link. |
| **32 KB Puffer** | Nimmt ankommende Frames auf, bis der ESP32 sie per SPI abholt — der SPI-Bus ist deutlich langsamer als die Leitung. |

## Der TCP/IP-Stack, den wir bewusst nicht nutzen

WIZnet vermarktet den W5500 als *hardwired TCP/IP controller*: Er beherrscht
TCP, UDP, IP und ICMP **selbst**, in acht unabhängigen Hardware-Sockets.
Gedacht ist das für kleine 8-Bit-Controller ohne eigenen Netzwerk-Stack.

Diese Betriebsart nutzen wir nicht. ESP-IDF schaltet den Baustein in den
**MACRAW-Modus** — Socket 0 wird zum reinen Frame-Durchreicher, alles darüber
macht lwIP auf dem ESP32.

Das ist kein Verzicht, sondern die richtige Wahl: So funktionieren `esp_netif`,
die BSD-Socket-API, DHCP und der bestehende `esp_http_server` unverändert
weiter. Die Web-UI merkt nicht, ob sie über WLAN oder Kabel erreicht wird.

Umgesetzt in `components/esp_eth/src/spi/w5500/esp_eth_mac_w5500.c` bei der
Socket-0-Initialisierung (`W5500_SMR_MAC_RAW`).

## Warum die Zusatzbauteile nötig sind

Drei Bauteile im Schaltplan erklären sich aus der Funktion des PHY:

| Bauteil | Wofür |
|---------|-------|
| **25-MHz-Quarz** | Taktreferenz des PHY. 100BASE-TX überträgt 125 MBaud auf der Leitung; der Chip leitet diesen Takt intern ab. Deshalb toleranzkritisch: verlangt sind ±30 ppm bei 25 °C und 18 pF Lastkapazität. Gewählt: Würth **830059532** (CFPX-104, ±20 ppm), Lastkondensatoren 2 × 27 pF in **C0G/NP0**. |
| **Bias-Widerstand an `EXRES1`** | Stellt den Bias-Strom der analogen Sendetreiber ein und bestimmt damit direkt die Signalamplitude auf dem Kabel. Zu grosse Toleranz verlässt die Ethernet-Spezifikation — daher 1 %. |
| **Magnetics in der RJ45-Buchse** | Galvanische Trennung zwischen Platine und Kabel plus Symmetrierung. Ethernet ist potentialfrei spezifiziert; ohne Übertrager bestünde eine leitende Verbindung zu jedem anderen Gerät im Netz. |

**Wichtig für das Layout:** Die sechs GPIOs zum ESP32 sind *keine*
Ethernet-Signale, sondern gewöhnliches SPI plus zwei Steuerleitungen — im
Layout unkritisch. Impedanzkontrolliert (100 Ω differenziell) müssen nur
`TX±` und `RX±` zwischen W5500 und Buchse geführt werden.

## GPIO-Belegung (SHBS-5)

Sechs Leitungen verbinden Modul und Controller. Es sind **keine**
Ethernet-Signale, sondern gewöhnliches SPI plus Reset und Interrupt.

| Netz | W5500-Pin | GPIO | Modul-Pad | Funktion am ESP32-S3 |
|------|-----------|------|-----------|----------------------|
| `ETH_RST` | 37 `RSTn` | 9 | 17 | FSPIHD |
| `ETH_SCSn` | 32 `SCSn` | 10 | 18 | FSPICS0 |
| `ETH_MOSI` | 35 `MOSI` | 11 | 19 | FSPID |
| `ETH_SCLK` | 33 `SCLK` | 12 | 20 | FSPICLK |
| `ETH_MISO` | 34 `MISO` | 13 | 21 | FSPIQ |
| `ETH_INT` | 36 `INTn` | 14 | 22 | FSPIWP |

Die Netznamen folgen den Pinnamen des W5500, deshalb `ETH_SCSn` und nicht
`ETH_CS`. Das `n` steht für *active low* und betrifft ebenso `RSTn` und
`INTn` — alle drei Signale sind im Ruhezustand High.

Gewählt wurden die nativen **FSPI-Pins**: SPI läuft darüber über das IO-MUX
statt über die GPIO-Matrix, was bei den realistischen 20–40 MHz die
Signalintegrität verbessert. Die sechs Pins liegen am Modul ausserdem auf den
**zusammenhängenden Pads 17–22**, was im Layout ein kompaktes Bündel ergibt.

Belegt werden dadurch ADC1_CH8 und ADC1_CH9 (GPIO9/10) sowie vier
ADC2-Kanäle, die bei aktivem WLAN ohnehin kaum nutzbar sind. **GPIO1–GPIO8
bleiben frei** für analoge Sensorik, GPIO15–GPIO18 für UART1 oder einen
32-kHz-Quarz.

Diese Belegung ist verbindlich für die Firmware-Umsetzung (**SHBS-11**).

## Versorgung: digital und analog getrennt

`+3V3` (digital) und `+3V3A` (analog) sind getrennte Netze, verbunden über eine
Ferritperle mit 100–2000 Ω bei 100 MHz. Das hält die Schaltströme des
Digitalteils aus der analogen Sendeendstufe des PHY heraus und entspricht dem
WIZnet-Referenzdesign.

| Netz | Versorgt |
|------|----------|
| `+3V3A` | alle `AVDD`-Pins des W5500 samt Abblockung, Stützkondensator, Abschlusswiderstände und Speisung der Sende-Mittelanzapfung |
| `+3V3` | `VDD` des W5500, Pull-ups, LED-Vorwiderstände |

## Quarz-Lastkondensatoren: 27 pF

Der Quarz verlangt **CL = 18 pF**. Mit `CL = C/2 + C_stray` und rund 4 pF
Streukapazität folgt C = 28 pF, also der Normwert **27 pF**.

Das WIZnet-Referenzschaltbild zeigt an dieser Stelle 18 pF. Dem folgen wir
bewusst **nicht**: 18-pF-Kondensatoren ergäben eine effektive Last von etwa
13 pF, der Quarz liefe zu schnell. Wahrscheinlich nutzt die Referenz einen
Quarz mit anderer Lastkapazität. Die Frequenz ist am ersten Prototyp zu messen
und die Kondensatoren bei Bedarf nachzuziehen.

## Kein Auto-MDIX

Der W5500 beherrscht **kein Auto-MDIX** (Datenblatt Rev. 1.0.5, Abschnitt
5.5.6). Er vertauscht Sende- und Empfangspaar also nicht selbständig.

| Gegenstelle | Kabel |
|-------------|-------|
| Switch, Router, Access Point | **normales Patchkabel** (straight-through) |
| Direkt an PC, Server oder eine zweite Basisstation | **Crossover-Kabel** |

In der Praxis unkritisch: Nahezu jeder aktuelle Switch beherrscht Auto-MDIX
auf seiner Seite und gleicht die Verdrahtung aus. Relevant wird es nur beim
direkten Anschluss an ein Gerät, das ebenfalls kein Auto-MDIX hat.

## Grenzen

- Ein Port, kein Switch und kein Router.
- 10/100 Mbit/s, kein Gigabit.
- Kein PoE.
- **Kein Auto-MDIX** — siehe oben.
- **Durchsatz real 15–20 Mbit/s.** Begrenzend ist der SPI-Bus, nicht die
  Leitung — unabhängig davon, dass die Gegenstelle 100 Mbit/s aushandelt. Für
  Konfigurations-Web-UI und Smart-Home-Telemetrie unkritisch.

## Vergleich zur verworfenen RMII-Lösung

| | RMII + externer PHY | **SPI + W5500** |
|---|---|---|
| Machbar auf ESP32-S3 | **nein** (kein EMAC) | ja |
| GPIOs | ~9 | **6** |
| Layout | 50-MHz-Taktführung, enge Timing-Vorgaben | nur ein differenzielles Paarpaar |
| Durchsatz | 100 Mbit/s | 15–20 Mbit/s |

Entscheidungsgrundlage: `tmp/report/2026-09-17_shbs-5-ethernet-architektur.md`.

## Stand

Schaltplan und BOM: **SHBS-5** (in Arbeit). PCB-Layout: **SHBS-10** (offen).
Firmware-Anbindung: **SHBS-11** (offen) — in `main/` gibt es derzeit keine
Ethernet-Nutzung.

Datenblatt: `pcb/Datasheets/` (W5500 v1.0.5).
