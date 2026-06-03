---
status: active
last_updated: 2026-06-02
---

# Hardware — SmartHome-Basisstation

KiCad-Layout und physische Schnittstellen der SmartHome-Basisstation auf Basis **ESP32-S3-WROOM-1U-N16R8**.

## Zielbild

Smart-Home-Basisstation mit Tastern, USB/PROG/JTAG, WLAN-Antenne, vier LEDs (Rot, Grün, Blau, Gelb) und **Ethernet** als geplante Schnittstelle.

## Physische Schnittstellen

| Schnittstelle | Zweck |
|---------------|--------|
| USB | Debugging (Seriell/JTAG über USB, je nach Design) |
| PROG | Firmware flashen |
| JTAG | On-Chip-Debugging |
| WLAN | Funk, Antenne am Modul **1U** |
| Ethernet | Ziel: kabelgebundene Netzwerkverbindung (Umsetzung: Hardware + Firmware prüfen) |

**Annahme (gekennzeichnet):** Die genaue Pinbelegung von PROG/JTAG/Ethernet folgt dem KiCad-Projekt; ohne geöffnetes Schema keine feste Signalzuordnung in dieser Doku.

## Steckverbinder (KiCad / BOM)

Im BOM werden u. a. Würth-Stecker **61201021621** (10-pol) und **61200621621** (6-pol) genannt — Details und Signalbelegung im jeweiligen KiCad-Schaltplan bzw. Datenblatt.

Ausführliche Stückliste mit Links: `README.md` (Abschnitt Hardware) — bei Änderungen auf **ESP32-S3-WROOM-1U-N16R8** abstimmen (README enthält teils gemischte Modulreferenzen).

## Repository-Ist-Stand (KiCad)

| Bereich | Pfad / Artefakt |
|--------|------------------|
| Hauptprojekt | `PCB/BasisStation/BasisStation.kicad_pro` |
| Schaltpläne | u. a. `BasisStation.kicad_sch`, `BasisStation_Layout.kicad_sch`, `BasisStation_Debugging.kicad_sch`, `BasisStation_architektur.kicad_sch` |
| Leiterplatte | `BasisStation.kicad_pcb` |
| Symbole / Footprints | `PCB/Symbol/`, `PCB/Footprints/` |
| Bauteilbibliothek MCU | `PCB/Bauteile/ESP32-S3-WROOM-1U-N16R8/` |
| Architektur-Diagramm (extern) | `PCB/architektur_basisStation.drawio` |

## Abgrenzung Firmware

Die Firmware in `main/` beschreibt das **Laufzeitverhalten** (WLAN, Webserver, LEDs). Ob und wie **Ethernet** auf der Platine angebunden ist, ergibt sich aus dem KiCad-Projekt; in der aktuellen Firmware gibt es **keine** Ethernet-Treiber-Nutzung.

Netzwerk-Konfiguration über HTTP: [communication.md](communication.md).

## Pflege

Änderungen an Schaltplan, BOM oder Schnittstellen hier und in [communication.md](communication.md) nachziehen.
