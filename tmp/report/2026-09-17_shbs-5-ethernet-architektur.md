---
type: analysis
created: 2026-09-17
jira: SHBS-5
status: draft
---

# SHBS-5 — Ethernet-Anbindung: Architekturentscheidung

## Ausgangslage

Task `tmp/tasks/open/0002_ethernet-schnittstelle.md` fordert eine kabelgebundene
Ethernet-Schnittstelle auf der Basisstation. Die Task-Datei nennt als Ist-Stand:

> ESP32-S3-WROOM-1U-N16R8: RMII-fähig; externer PHY (z. B. LAN8720, IP101) + RJ45/Magnetics üblich.

Diese Annahme wurde vor der Planung überprüft.

## Ergebnis / Befunde

### B1 — Der ESP32-S3 hat keinen internen Ethernet-MAC (blockierend)

Die RMII-Annahme der Task-Datei trifft **nicht** zu. Der ESP32-S3 besitzt im
Gegensatz zum ursprünglichen ESP32 **keine EMAC-Peripherie** und damit keine
RMII-Schnittstelle. Ein externer RMII-PHY (LAN8720, IP101) lässt sich nicht
anbinden — es fehlt die Gegenstelle im SoC.

Nachweis im lokalen ESP-IDF (v5.5.2):

| Datei | Befund |
| ----- | ------ |
| `components/soc/esp32/include/soc/soc_caps.h:78` | `#define SOC_EMAC_SUPPORTED 1` |
| `components/soc/esp32s3/include/soc/soc_caps.h` | Symbol **nicht vorhanden** |

Folge: Aufgabenpunkte 1–4 und die Akzeptanzkriterien der Task-Datei müssen
umgeschrieben werden, bevor Schaltplanarbeit beginnt.

### B2 — Machbarer Weg: SPI-Ethernet-Controller mit integriertem MAC+PHY

ESP-IDF v5.5.2 liefert für SoCs ohne EMAC drei Treiber
(`components/esp_eth/src/spi/`), die über die reguläre `esp_eth`-API und
`esp_netif` eingebunden werden — aus Firmware-Sicht verhält sich das Ergebnis
wie ein normales Ethernet-Interface.

| Controller | Kconfig-Schalter | Bewertung |
| ---------- | ---------------- | --------- |
| **W5500** (WIZnet) | `ETH_SPI_ETHERNET_W5500` | Sehr gut verfügbar, breite Community, MAC+PHY integriert, SPI bis 80 MHz (praktisch 33–40 MHz). **Empfehlung.** |
| DM9051 (Davicom) | `ETH_SPI_ETHERNET_DM9051` | Funktional gleichwertig, im DACH-Raum schlechter beschaffbar. |
| KSZ8851SNL (Microchip) | `ETH_SPI_ETHERNET_KSZ8851SNL` | Ältestes der drei, Verfügbarkeit rückläufig. |

Der W5500 bringt zwar einen Hardware-TCP/IP-Stack mit; der ESP-IDF-Treiber
betreibt ihn im **MACRAW-Modus** als reinen MAC, sodass lwIP wie gewohnt
darüber läuft. Das ist der vom Hersteller unterstützte Standardfall.

Durchsatz-Erwartung über SPI: realistisch **ca. 15–20 Mbit/s** statt 100 Mbit/s.
Für Konfigurations-Web-UI und Smart-Home-Telemetrie unkritisch — als
Festlegung aber zu dokumentieren.

Nebeneffekt gegenüber RMII: statt ~9 belegten GPIOs werden nur **6** benötigt
(SCLK, MOSI, MISO, CS, INT, RST), und die kritische 50-MHz-RMII-Taktführung
im Layout entfällt vollständig.

### B3 — GPIO-Budget ist ausreichend

Laut Netzliste (`PCB/BasisStation/BasisStation.net`) sind aktuell frei:
GPIO1–GPIO18, GPIO45, GPIO46.

Einschränkungen bei der Auswahl:

- **GPIO35/36/37** erscheinen frei, sind beim Modul **N16R8** aber intern vom
  Octal-PSRAM belegt — nicht verwenden (bereits in `hardware.md` vermerkt).
- **GPIO3, GPIO45, GPIO46** sind Strapping-Pins und sollten frei bleiben,
  insbesondere GPIO3 wegen der JTAG-Quellenwahl (`J5`).
- **GPIO19/GPIO20** sind durch USB (`J1`) belegt.

Damit bleiben GPIO4–GPIO18 als unkritischer Pool — mehr als ausreichend für
sechs Signale.

### B4 — PCB-Layout ist noch nicht vollständig

Der Schaltplan führt ~41 Bauteile, die Leiterplatte
(`BasisStation.kicad_pcb`) enthält erst **21 platzierte Footprints**.
Platinenumriss: **160 × 135 mm** (Edge.Cuts 50/25 → 210/160) — für eine
RJ45-Buchse mit integrierten Magnetics reichlich Platz.

Das Akzeptanzkriterium „RJ45 platziert **und geroutet**" aus der Task-Datei
greift damit der allgemeinen Layout-Phase vor. Empfehlung: Schaltplan +
Symbol/Footprint/BOM in SHBS-5 abschliessen, Platzierung und Routing im
gemeinsamen Layout-Durchgang für die gesamte Platine erledigen.

### B5 — Auswirkung auf das Leistungsbudget

Versorgung laut [power_supply.md](../../docs/project/power_supply.md):
MP2359DJ Buck bis **1,2 A**, eingangsseitig Polyfuse `F1` **1,1 A** bei 5 V.

| Verbraucher | Annahme 3,3 V |
| ----------- | ------------- |
| ESP32-S3 mit WLAN-TX (Spitze) | ~350 mA |
| W5500 inkl. Link-LEDs | ~150 mA |
| LEDs D7–D10 (4 × 5 mA) | ~20 mA |
| **Summe (Worst Case)** | **~520 mA** |

Bei ~85 % Wandlerwirkungsgrad entspricht das rund **400 mA** am 5-V-Eingang —
innerhalb der 1,1 A von `F1` und der 1,2 A des MP2359. Kein Redesign nötig,
der Wert gehört aber in `power_supply.md`.

**Abhängigkeit:** Der Ausgangszweig des Buck-Wandlers ist laut offenem Task
`0005_shbs4-buck-topologie-korrektur.md` noch fehlerhaft. Ethernet erhöht die
Last auf einer Schiene, die noch nicht verifiziert ist — SHBS-4 sollte vor dem
Hardware-Test abgeschlossen sein (für die Schaltplanarbeit an SHBS-5 aber
nicht blockierend).

## Empfehlungen

1. **RMII verwerfen.** Task-Datei `0002_ethernet-schnittstelle.md` auf
   SPI-Ethernet umschreiben, inkl. Akzeptanzkriterien.
2. **W5500** als Controller festlegen (Verfügbarkeit + IDF-Treiber + Community).
3. **RJ45 mit integrierten Magnetics** wählen — entkoppelt das Layout von
   diskreten Übertrager-Platzierungsregeln.
4. Schaltplan-Scope für SHBS-5: W5500-Block (25-MHz-Quarz, Entkopplung,
   Reset, INT, SPI), RJ45 inkl. Bob-Smith-Terminierung, ESD, Link-LEDs.
5. **Layout/Routing** als eigenen Task ausgliedern (siehe B4).
6. **Firmware** (`esp_eth` + `esp_netif`, Koexistenz mit WLAN-Station) als
   eigenen Task nach Abschluss der Hardware — die aktuelle
   `WLAN.c`/`WebServer.c`-Struktur kennt nur ein Netif.

## Nächste Schritte

### Entscheidungen (Bediener, 17.09.2026)

| Punkt | Festlegung |
| ----- | ---------- |
| Controller | **W5500** |
| Buchse | RJ45 mit integrierten Magnetics |
| Scope SHBS-5 | **Schaltplan + BOM** — Layout und Firmware als eigene Tickets |
| Alte Task-Datei | `0002_ethernet-schnittstelle.md` ersetzt durch Serie `shbs5` |

### Umgesetzt

**Jira:**

- **SHBS-5** — Titel und Beschreibung auf SPI/W5500 korrigiert, Scope
  eingegrenzt, Kommentar mit EMAC-Befund und verworfenen Alternativen.
- **SHBS-10** (neu, Subtask von SHBS-3) — Ethernet-Sektion im PCB-Layout
  platzieren und routen.
- **SHBS-11** (neu, eigenständiger Task) — Ethernet-Anbindung in der Firmware.
  Bewusst kein Subtask von SHBS-3, da dieses Ticket das KiCad-Layout bündelt.
- Verlinkung: SHBS-5 *blocks* SHBS-10 und SHBS-11; SHBS-10 *relates to* SHBS-11.

**Tasks** unter `tmp/tasks/`:

| Task | Status | Inhalt |
| ---- | ------ | ------ |
| `0001_shbs5-architektur-spi-ethernet.md` | done | Architekturentscheidung (dieser Report) |
| `0002_shbs5-symbol-footprint-bibliothek.md` | open | Datenblätter, RJ45-Auswahl, Symbole, Footprints |
| `0003_shbs5-w5500-schaltplan.md` | open | W5500-Block, GPIO-Belegung |
| `0004_shbs5-rj45-magnetics-schaltplan.md` | open | RJ45, Terminierung, Schirm, Link-LEDs |
| `0005_shbs5-bom-netzliste-doku.md` | open | BOM, Netzliste, ERC, Doku |

### Offen

- Task `0002`: Auswahl des konkreten RJ45-Typs — Beschaffungsentscheidung.
- Report auf `status: final` setzen, sobald die Erkenntnisse über Task `0005`
  nach `docs/project/` überführt sind.
