---
status: done
priority: high
type: feature
created: 2026-06-08
jira: SHBS-5
parent_jira: SHBS-3
---

# Ethernet-Architektur festlegen: SPI statt RMII

## Kontext

Vorgängerfassung dieser Datei (`0002_ethernet-schnittstelle.md`, angelegt
2026-06-08) ging davon aus, der ESP32-S3 sei **RMII-fähig**, und plante einen
externen PHY (LAN8720, IP101) mit RJ45/Magnetics.

Die Prüfung am 2026-09-17 hat diese Annahme widerlegt.

## Befund

Der ESP32-S3 besitzt — anders als der ursprüngliche ESP32 — **keine
EMAC-Peripherie** und damit keine RMII-Schnittstelle. Ein externer RMII-PHY
findet keine Gegenstelle im SoC.

Nachweis im lokalen ESP-IDF v5.5.2:

| Datei | Befund |
| ----- | ------ |
| `components/soc/esp32/include/soc/soc_caps.h:78` | `#define SOC_EMAC_SUPPORTED 1` |
| `components/soc/esp32s3/include/soc/soc_caps.h` | Symbol **nicht vorhanden** |

## Entscheidung

Ethernet wird über einen **SPI-Controller mit integriertem MAC+PHY**
angebunden. ESP-IDF liefert dafür Treiber unter
`components/esp_eth/src/spi/` (`w5500`, `dm9051`, `ksz8851snl`), die über die
reguläre `esp_eth`/`esp_netif`-API laufen — firmwareseitig also ein normales
Ethernet-Interface.

Festgelegt vom Bediener am 2026-09-17:

| Punkt | Festlegung |
| ----- | ---------- |
| Controller | **WIZnet W5500** — beste Verfügbarkeit, breiteste Community, IDF-Treiber betreibt ihn im MACRAW-Modus als reinen MAC unter lwIP |
| Buchse | RJ45 mit **integrierten Magnetics** |
| Scope SHBS-5 | **Schaltplan + BOM**. Layout/Routing und Firmware als eigene Tickets |

### Konsequenzen

- **6 statt ~9 GPIOs** belegt (SCLK, MOSI, MISO, CS, INT, RST).
- Die kritische 50-MHz-RMII-Taktführung im Layout entfällt vollständig.
- Durchsatz realistisch **15–20 Mbit/s** statt 100 Mbit/s — für Web-UI und
  Smart-Home-Telemetrie unkritisch, aber als Festlegung zu dokumentieren.

## Ergebnis

Analyse abgelegt unter
[tmp/report/2026-09-17_shbs-5-ethernet-architektur.md](../../report/2026-09-17_shbs-5-ethernet-architektur.md).

Die konkrete Umsetzung ist in die Folge-Tasks `0002`–`0005` dieser Serie
zerlegt. Keine Code- oder Schaltplanänderung in diesem Task, daher keine
Versionserhöhung und kein Eintrag in `releases.md`.

### Jira-Stand (17.09.2026)

| Ticket | Änderung |
| ------ | -------- |
| **SHBS-5** | Titel und Beschreibung auf SPI/W5500 korrigiert, Scope auf Schaltplan + BOM eingegrenzt. Kommentar mit dem EMAC-Befund und den verworfenen Alternativen hinterlegt. |
| **SHBS-10** | Neu — *Ethernet-Sektion im PCB-Layout platzieren und routen*. Subtask von SHBS-3. |
| **SHBS-11** | Neu — *Ethernet-Anbindung in der Firmware (esp_eth über SPI, W5500)*. Eigenständiger Task, bewusst **kein** Subtask von SHBS-3 (dort geht es um das KiCad-Layout). |

Verlinkung: SHBS-5 *blocks* SHBS-10 und SHBS-11; SHBS-10 *relates to* SHBS-11.
