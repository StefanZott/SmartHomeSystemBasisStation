---
status: active
last_updated: 2026-06-02
type: related-project
---

# Produktscope — Verzahnte Projekte

## Entscheidung (SHBS-1, Task 0018)

Die SmartHome-Basisstation (**SmartHomeSystemBasisStation**) ist ein **eigenständiges Embedded-Gateway** mit ESP32-S3, KiCad-Hardware und Web-Konfiguration.

**Keine UART-/Protokoll-Schnittstelle zum NRT 1 XT** ist Teil dieses Repositories. Frühere WEM/NRT-Bezüge in der Projektdoku wurden entfernt bzw. neutral formuliert.

## Dokumentierte Schnittstellen in diesem Projekt

| Schnittstelle | Beschreibung | Referenz |
|---------------|--------------|----------|
| WLAN (SoftAP / Station) | Erstkonfiguration und Betrieb | [communication.md](../project/communication.md) |
| HTTP / Web-UI | Statische Seiten und Diagnose-URIs | [communication.md](../project/communication.md) |
| SPIFFS | Persistente `configuration.json` | [architecture.md](../project/architecture.md) |
| USB / PROG / JTAG | Entwicklung und Flash | [hardware.md](../project/hardware.md) |
| Ethernet (geplant) | Hardware-Roadmap, noch ohne Firmware | [hardware.md](../project/hardware.md) |

## Cloud / Backend

Kein verbindlicher Schnittstellenvertrag zu Cloud-Diensten in diesem Repository. Erweiterungen (OTA, MQTT, REST-Backend) sind architektonisch möglich — siehe [architecture.md](../project/architecture.md).

## Neue Schnittstellen

Verzahnte Projekte werden hier ergänzt, sobald ein fachlicher Schnittstellenvertrag existiert (Dateiname z. B. `nrt-1-xt.md`, `cloud-backend.md`).
