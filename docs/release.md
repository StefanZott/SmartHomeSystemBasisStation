# Release-Notizen

## Initial-Dokumentation (Workflow)

- Angelegt: Ordnerstruktur `docs/` gemäß `AGENTS.md`.
- Inhalt: Ist-Analyse Stand Repository, keine Produktions-Freigabe.
- Initial-Workflow (Analyse, Verständnis, Dokumentation) erneut durchlaufen am **2026-04-06**: Architekturdiagramme (reines Text-Markdown in Code-Blöcken) in `docs/firmware/architecture.md` und `docs/layout/architecture.md` ergänzt (Vorgabe `AGENTS.md`: Diagramm in jeder `architecture.md`).

## Firmware-Version

- CMake: `PROJECT_VER` = **0.0.1** (`CMakeLists.txt`).
- Laufzeit-String: `FW_Version` = **V0.0.1** (`main.c`).

## Build (kurz)

Voraussetzung: installiertes [ESP-IDF](https://docs.espressif.com/projects/esp-idf/) passend zum Chip **ESP32-S3**.

```text
idf.py set-target esp32s3
idf.py build
idf.py flash monitor
```

Partitionierung und SPIFFS: siehe `partitions.csv` und Projekt-Konfiguration (`sdkconfig`).

## Nächste Schritte (kein Release)

- README vom ESP-IDF-Beispieltext auf dieses Projekt zuschneiden.
- Produktname (`productName`) und Versionsstrings abstimmen.
- Ethernet: Hardware-Freigabe und Firmware-Erweiterung dokumentieren, sobald umgesetzt.
