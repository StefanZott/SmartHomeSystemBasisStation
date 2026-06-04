---
status: active
last_updated: 2026-06-02
type: project-doc
---

# Speicher-Layout (Memory Map)

Flash-Partitionierung der SmartHome-Basisstation (ESP32-S3, **4 MB** Flash gemäß `sdkconfig`).

Quellen: `partitions.csv`, `sdkconfig` (`CONFIG_PARTITION_TABLE_*`, `CONFIG_ESPTOOLPY_FLASHSIZE_4MB`).

## Standard-Bereiche (ESP-IDF)

| Bereich | Offset | Größe | Hinweis |
|---------|--------|-------|---------|
| Bootloader | `0x1000` | variabel | `CONFIG_BOOTLOADER_OFFSET_IN_FLASH` |
| Partitionstabelle | `0x8000` | 4 KiB | `CONFIG_PARTITION_TABLE_OFFSET` |
| NVS | `0x9000` | 24 KiB (`0x6000`) | `partitions.csv` |
| PHY Init | `0xF000` | 4 KiB (`0x1000`) | Kalibrierungsdaten WiFi/BT |
| Factory App | `0x10000` | ~2,38 MiB (`0x262000`, 4-KiB-ausgerichtet) | Firmware-Binary |
| SPIFFS (storage) | `0x272000` | 960 KiB (`0xF0000`) | Web-Assets, `configuration.json` |

Ende der belegten Partitionen: `0x362000` — verbleibender Flash bis `0x400000` (4 MiB) ungenutzt.

## Partitionstabelle (`partitions.csv`)

```csv
# Name,   Type, SubType, Offset,  Size, Flags
nvs,      data, nvs,     0x9000,  0x6000,
phy_init, data, phy,     0xf000,  0x1000,
factory,  app,  factory, 0x10000, 0x262000,
storage,  data, spiffs,  ,        0xF0000,
```

| Name | Type | SubType | Verwendung |
|------|------|---------|------------|
| `nvs` | data | nvs | ESP-IDF NVS (u. a. WiFi-Stack) |
| `phy_init` | data | phy | PHY-Kalibrierung |
| `factory` | app | factory | Haupt-Firmware (`idf.py build`) |
| `storage` | data | spiffs | SPIFFS-Partition, Mount `/spiffs` |

**Hinweis:** Offset von `storage` leer in CSV → ESP-IDF legt Partition direkt nach `factory` an (`0x272000`). App-Partitionen müssen auf `0x1000` ausgerichtet sein (ESP-IDF 5.5+).

## Laufzeit-Mapping Firmware

| Logischer Pfad | Partition | Inhalt |
|----------------|-----------|--------|
| `/spiffs` | `storage` (SPIFFS) | HTML/CSS/JS, `configuration.json` |
| NVS (API) | `nvs` | Framework-intern |
| App-Code | `factory` | `main/` + eingebettete Assets |

SPIFFS-Konfiguration in `sdkconfig`: Page Size 256, `CONFIG_SPIFFS_MAX_PARTITIONS=3`.

## OTA

- **Kein OTA-Partition** in `partitions.csv` (`CONFIG_PARTITION_TABLE_TWO_OTA` nicht aktiv).
- Updates derzeit über **USB/PROG** (`idf.py flash`).

Geplante OTA-Erweiterung würde Partitionstabelle und [security.md](security.md) anpassen.

## Versionsbezug

Anwendungsversion: `version` / `PROJECT_VER` / `CONFIG_APP_PROJECT_VER` — siehe [architecture.md](architecture.md) und [struktur-anpassung-agents.md](struktur-anpassung-agents.md) §6.

## Pflege

Bei Änderung von `partitions.csv` oder Flash-Größe in `sdkconfig`:

1. Offsets/Größen hier aktualisieren.
2. Build und SPIFFS-Mount testen (`idf.py build`, `idf.py flash`).
3. [architecture.md](architecture.md) Deployment-Abschnitt prüfen.
