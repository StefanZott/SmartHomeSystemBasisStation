---
status: draft
last_updated: 2026-06-02
type: userdoc
lang: de-en
---

# SmartHome-Basisstation — Produktwebsite-Vorlage

## DE — Titel

**SmartHome-Basisstation** — das kompakte Konfigurations-Gateway für Ihr Smart Home

## DE — Meta

Smart Home | Basisstation | ESP32-S3 | WLAN-Konfiguration | Web-UI | Gateway | TGE

## DE — Beschreibung

Die SmartHome-Basisstation verbindet Hardware, Firmware und Web-Oberfläche in einem Gerät. Über den integrierten WLAN-Zugangspunkt richten Sie das Gerät im Browser ein — ohne separate App oder Desktop-Software.

Im Heimnetz arbeitet die Basisstation im Station-Modus und speichert Einstellungen dauerhaft. Vier Status-LEDs zeigen Betriebszustände an; Diagnose-Endpunkte unterstützen Entwicklung und Support.

Die KiCad-Hardware und ESP-IDF-Firmware sind im Repository dokumentiert und erweiterbar (Ethernet, OTA, Cloud-Anbindung).

## DE — Key-Facts

1. **Browser-Konfiguration** — Ersteinrichtung über SoftAP und Web-UI.
2. **ESP32-S3 1U** — Leistungsfähiger MCU mit externer Antenne.
3. **Persistente Einstellungen** — Konfiguration in SPIFFS (`configuration.json`).
4. **Status-LEDs** — Rot, Grün, Blau, Gelb für schnelle Diagnose.
5. **Modularer Stack** — ESP-IDF, FreeRTOS, `esp_http_server`.
6. **Open Hardware** — KiCad-Projekt im Repository (`pcb/BasisStation/`).
7. **Entwickler-Toolchain** — ESP-IDF, Dev-Container, Unity-Tests.
8. **Erweiterbar** — Ethernet und OTA als Roadmap-Punkte.
9. **Sicherheitsbewusst** — Konzept in Projektdokumentation (`security.md`).
10. **TGE-Entwicklung** — Integriertes Hardware-/Software-Design.

## DE — Details

- Versorgung über DC/DC (3,3 V) gemäß Schaltplan.
- Statische Web-Assets embedded in der Firmware (SPIFFS).
- USB / PROG / JTAG für Entwicklung und Wartung.

## DE — Informationen & Dokumente

- Internes Datenblatt: `docs/userdoc/factsheet.md` (VERTRAULICH)
- Architektur: `docs/project/architecture.md`
- Releases: `docs/userdoc/releases.md`

## DE — Technische Daten & Zubehör

| Merkmal | Angabe |
|---------|--------|
| MCU | ESP32-S3-WROOM-1U-N16R8 |
| Flash | 4 MB (Custom-Partitionstabelle) |
| Konnektivität | WLAN (802.11 b/g/n); Ethernet geplant |
| Firmware | ESP-IDF, Version siehe `version` |
| Gehäuse / Zubehör | Produktabhängig — siehe Stückliste KiCad |

---

## EN — Title

**SmartHome Base Station** — the compact configuration gateway for your smart home

## EN — Meta

smart home | base station | ESP32-S3 | Wi-Fi setup | web UI | gateway | TGE

## EN — Description

The SmartHome base station combines hardware, firmware, and a web interface in one device. Use the built-in Wi-Fi access point to configure the unit in your browser — no separate app or desktop software required.

In home operation the station runs in client mode and stores settings persistently. Four status LEDs indicate operating states; diagnostic HTTP endpoints support development and support teams.

KiCad hardware and ESP-IDF firmware are documented in the repository and ready for extension (Ethernet, OTA, cloud connectivity).

## EN — Key-Facts

1. **Browser configuration** — initial setup via SoftAP and web UI.
2. **ESP32-S3 1U** — capable MCU with external antenna.
3. **Persistent settings** — configuration stored in SPIFFS (`configuration.json`).
4. **Status LEDs** — red, green, blue, yellow for quick diagnostics.
5. **Modular stack** — ESP-IDF, FreeRTOS, `esp_http_server`.
6. **Open hardware** — KiCad project in the repository (`pcb/BasisStation/`).
7. **Developer toolchain** — ESP-IDF, dev container, Unity tests.
8. **Extensible** — Ethernet and OTA on the roadmap.
9. **Security-aware** — concept documented in `security.md`.
10. **TGE engineering** — integrated hardware and software design.

## EN — Details

- Power via DC/DC (3.3 V) per schematic.
- Static web assets embedded in firmware (SPIFFS).
- USB / PROG / JTAG for development and maintenance.

## EN — Information & Documents

- Internal factsheet: `docs/userdoc/factsheet.md` (CONFIDENTIAL)
- Architecture: `docs/project/architecture.md`
- Releases: `docs/userdoc/releases.md`

## EN — Technical Data & Accessories

| Feature | Value |
|---------|--------|
| MCU | ESP32-S3-WROOM-1U-N16R8 |
| Flash | 4 MB (custom partition table) |
| Connectivity | Wi-Fi (802.11 b/g/n); Ethernet planned |
| Firmware | ESP-IDF, version see `version` file |
| Enclosure / accessories | Product-specific — see KiCad BOM |
