# SmartHomeSystemBasisStation

## Kurzbeschreibung

SmartHome-Basisstation auf Basis des **ESP32-S3** mit eigener Platine, ESP-IDF-Firmware und Web-Oberfläche zur WLAN-Konfiguration und Gerätediagnose. Das Repository bündelt Hardware (KiCad), Firmware und SPIFFS-Web-Assets in einem Projekt.

## Architektur-Überblick

| Pfad | Inhalt |
|------|--------|
| `main/` | Firmware (ESP-IDF), Einstieg `main.c` |
| `spiffs/` | Web-UI (HTML, CSS, JS) → SPIFFS-Image |
| `PCB/` | KiCad-Schaltplan und Layout der Basisstation |
| `docs/` | Projektdokumentation und Anwenderdoku |

Stückliste und Pinout: [docs/project/hardware.md](docs/project/hardware.md)

## Toolchain

- **Firmware:** [ESP-IDF](https://docs.espressif.com/projects/esp-idf/) für ESP32-S3, Build über `idf.py`
- **IDE:** VS Code mit ESP-IDF-Erweiterung; optional Dev Container (`.devcontainer/`)
- **Hardware:** KiCad 8/9 — Projekt unter `PCB/BasisStation/`

## Deep Dive

Technische Architektur, Module, Startablauf und Verzeichnisstruktur:

→ [docs/project/architecture.md](docs/project/architecture.md)

Weitere Themen: [Kommunikation](docs/project/communication.md) · [Sicherheit](docs/project/security.md) · [Speicher-Layout](docs/project/memory_map.md)

## Deployment

Build, Flash und Monitor (Kurzfassung):

```text
idf.py set-target esp32s3
idf.py build
idf.py flash monitor
```

Ausführliche Anleitung, Partitionierung und Voraussetzungen:

→ [docs/project/architecture.md#deployment](docs/project/architecture.md#deployment)

Agenten-Regeln und Workflow: [AGENTS.md](AGENTS.md)
