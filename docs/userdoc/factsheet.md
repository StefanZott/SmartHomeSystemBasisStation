---
status: active
last_updated: 2026-06-02
type: userdoc
confidential: true
---

# SmartHome-Basisstation — Internes Datenblatt

**VERTRAULICH / INTERN** — Zielgruppe: Mitarbeiter TGE Gruppe (Vertrieb, Marketing, Technik). Nicht für externe Veröffentlichung ohne Freigabe.

## Produkt

| Merkmal | Angabe |
|---------|--------|
| Bezeichnung | SmartHome-Basisstation (SmartHomeSystemBasisStation) |
| Geräteart | Embedded Gateway / Konfigurations-Basisstation |
| MCU | ESP32-S3-WROOM-1U-N16R8 |
| Firmware | ESP-IDF, Version `0.00.001` |
| Hardware | KiCad-Projekt `PCB/BasisStation/` |

## Kurzbeschreibung

Kompakte Basisstation zur Anbindung und Konfiguration von Smart-Home-Komponenten. Kombination aus **Hardware-Platine**, **ESP32-S3-Firmware** und **Web-Oberfläche** zur WLAN-Einrichtung und Gerätediagnose.

## Use-Cases

- Erstkonfiguration über **WLAN SoftAP** und Browser (Setup ohne separate App).
- Betrieb im Heim-WLAN (**Station-Modus**) mit persistenter Konfiguration.
- **Statusanzeige** über vier LEDs (Rot, Grün, Blau, Gelb).
- **Diagnose** über HTTP-Endpunkte (Verbindungsinfo, Firmware-Version, LED-Test).
- Entwicklung und Wartung über **USB / PROG / JTAG**.

## Technische Eckdaten

- **Versorgung:** DC/DC auf 3,3 V (z. B. TSR 1-2433E im Schaltplan).
- **Konnektivität:** WLAN (Antenne am 1U-Modul); **Ethernet geplant**, noch nicht in Firmware.
- **Konfigurationsspeicher:** SPIFFS (`configuration.json`).
- **Flash:** 4 MB, Custom-Partitionstabelle (App + SPIFFS).
- **Web-UI:** Statische Seiten unter `spiffs/` (Bootstrap, WLAN-, LED-, Info-Seiten).

## Vorteile / Nutzen

- Integrierte **Web-Konfiguration** ohne Desktop-Software.
- **Modularer ESP-IDF-Stack** — erweiterbar (Ethernet, OTA, Cloud-Anbindung).
- **KiCad-Hardware** im Repository — Nachvollziehbarkeit für Entwicklung und Produktion.
- **Dev-Container / VS Code** — einheitliche Toolchain für Entwickler.

## Alleinstellungsmerkmale (intern)

- Hardware + Firmware + UI als **ein Repository** dokumentiert (AGENTS.md-Struktur).
- Zielplattform **ESP32-S3 1U** mit externer Antenne — geeignet für Gehäuse mit Funk außerhalb Metallgehäuse.
- Vorbereitet auf **Ethernet-Erweiterung** (Hardware-Roadmap).

## Dokumentation & Support

| Thema | Dokument |
|-------|----------|
| Architektur | [architecture.md](../project/architecture.md) |
| Hardware | [hardware.md](../project/hardware.md) |
| Kommunikation | [communication.md](../project/communication.md) |
| Sicherheit | [security.md](../project/security.md) |
| FAQ | [faq.md](faq.md) |
| Releases | [releases.md](releases.md) |

## Status

Entwicklungsstand — **keine Produktions-Freigabe**. README und Produktname in Firmware (`productName`) noch nicht final auf Basisstation abgestimmt.
