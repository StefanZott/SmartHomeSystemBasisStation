---
status: active
last_updated: 2026-06-02
type: userdoc
---

# Release-Notizen

## Initial-Dokumentation (Workflow)

- Angelegt: Ordnerstruktur `docs/` gemäß `AGENTS.md`.
- Inhalt: Ist-Analyse Stand Repository, keine Produktions-Freigabe.
- Initial-Workflow (Analyse, Verständnis, Dokumentation) durchlaufen am **2026-04-06**: Architekturdiagramme in `docs/project/architecture.md` und `docs/project/hardware.md`.
- **2026-06-02:** Doku-Migration nach `docs/project/` und `docs/userdoc/` (Task 0005, SHBS-1).

## Firmware-Version

- Root: `version` = **0.00.001** (Format `X.XX.XXX`).
- CMake: `PROJECT_VER` = **0.00.001** (`CMakeLists.txt`).
- UI/sdkconfig: `CONFIG_APP_PROJECT_VER` = **0.00.001**.
- HTTP `/FWversion`: ESP-IDF `app_desc->version` (aus `CONFIG_APP_PROJECT_VER`, synchron zu `version`).

## Build (kurz)

Voraussetzung: installiertes [ESP-IDF](https://docs.espressif.com/projects/esp-idf/) passend zum Chip **ESP32-S3**.

```text
idf.py set-target esp32s3
idf.py build
idf.py flash monitor
```

Partitionierung und SPIFFS: siehe `partitions.csv` und [architecture.md](../project/architecture.md).

## Nächste Schritte (kein Release)

- Ethernet: Hardware-Freigabe und Firmware-Erweiterung dokumentieren, sobald umgesetzt.
- Marketing: `proweb.md` Docshare-Links ergänzen.
