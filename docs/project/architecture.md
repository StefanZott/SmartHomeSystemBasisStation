---
status: active
last_updated: 2026-06-02
type: project-doc
---

# Architektur — SmartHomeSystemBasisStation

ESP-IDF-Firmware auf **ESP32-S3**, KiCad-Hardware und SPIFFS-Web-UI für die Konfiguration der SmartHome-Basisstation.

## Systemüberblick

```text
Stromversorgung              Rechenkern / Peripherie
─────────────────            ─────────────────────────────────────────

  [DC/DC, z. B. TSR 1-2433E
   auf 3,3 V] ──────────────► ESP32-S3-WROOM-1U-N16R8
                                      │
  [Power- / Reset-Taster] ────────────┤
                                      ├──► [4 LEDs, RGBY]
  [USB]  ─────────────────────────────┤
  [PROG] ─────────────────────────────┤
  [JTAG] ─────────────────────────────┤
                                      ├──► [WLAN-Antenne am Modul 1U]
                                      │
                                      └──► [Ethernet]  (Ziel; siehe [hardware.md](hardware.md))
```

Hardware-Details: [hardware.md](hardware.md). Kommunikation (WLAN, HTTP): [communication.md](communication.md).

## Verzeichnisstruktur (Repository)

| Pfad | Rolle |
|------|--------|
| `main/` | ESP-IDF-Firmware (Ausnahme: statt `embedded/` laut AGENTS.md) |
| `spiffs/` | Web-Assets (HTML, CSS, JS) → SPIFFS-Image |
| `pcb/` | KiCad-Projekt Basisstation |
| `docs/project/` | Technische Projektdokumentation |
| `docs/userdoc/` | Anwenderdokumentation |
| `partitions.csv` | Flash-Partitionen (App, SPIFFS, NVS) |
| `version` | Zentrale Versionsnummer (`X.XX.XXX`), Sync mit CMake und sdkconfig |
| `tests/` | Unity-Tests (ESP-IDF, `idf.py -T tests`) — siehe unten |

## Firmware — Laufzeitdiagramm

Startsequenz in `app_main`, persistente Konfiguration und Tasks. **Nur Standard-Markdown:** Diagramm als Text im Code-Block (kein Mermaid).

```text
app_main – Startsequenz (von oben nach unten)
──────────────────────────────────────────────
  NVS Flash
       |
       v
  esp_netif + Default Event Loop
       |
       v
  SPIFFS (/spiffs)
       |
       v
  startWebServer
       |-------------------------> WebServer.c --> FileManagement.c
       |                                                    |
       v                                                    v
  xTaskCreatePinnedToCore (3 Tasks)              configuration.json
       |
       +-- ledControlTask -----> LED.c
       +-- executeTaskControl --> TaskControl.c
       +-- wifiControlTask ---> WLAN.c --> FileManagement.c --> configuration.json
       |
       v
  configuration.json laden oder anlegen
       |
       v
  wifi_init_sta_and_softap()
```

## Build & Metadaten

- Root: `CMakeLists.txt` — `PROJECT_VER` aus `version` (aktuell **0.00.001**), `project(SmartHomeSystemBasisStation)`.
- UI/Laufzeit: `sdkconfig` — `CONFIG_APP_PROJECT_VER` (identisch zu `version`).
- Komponente: `main/CMakeLists.txt` — Quellen und eingebettete SPIFFS-Assets (HTML/CSS/JS/Icons).

Versions-Sync: siehe [struktur-anpassung-agents.md](struktur-anpassung-agents.md) §6.

## Deployment

Voraussetzung: [ESP-IDF](https://docs.espressif.com/projects/esp-idf/) für **ESP32-S3**.

```text
idf.py set-target esp32s3
idf.py build
idf.py flash monitor
```

Partitionierung und SPIFFS: `partitions.csv`, `sdkconfig`.

## Testing

Unity-Tests unter `tests/` (Smoke-Tests, eigenständige Test-Komponente ohne `main/`).

```text
idf.py set-target esp32s3
idf.py -T tests build
idf.py -T tests flash monitor
```

Details: [tests/README.md](../../tests/README.md).

## Code style (C/C++)

Formatting and static analysis: `.clang-format` and `.clang-tidy` in the project root (`main/`, excluding vendored `cJSON`).

## Startablauf (`main/main.c`)

1. **NVS** initialisieren (ggf. Erase bei Versions-/Seitenkonflikt).
2. **Netzwerk-Stack:** `esp_netif_init()`, Default-Event-Loop.
3. **Synchronisation:** Mutex und Binary-Semaphore für LED-Logik.
4. **SPIFFS** unter `/spiffs` mounten (`initSpiffs`).
5. **HTTP-Server** starten (`startWebServer("/spiffs")`).
6. **FreeRTOS-Tasks** (Core-Zuordnung über `PRO_CPU` / `APP_CPU` in `main.h`):
   - `ledControlTask` — LED-Steuerung
   - `executeTaskControl` — TaskControl
   - `wifiControlTask` — WLAN
7. **WLAN-Konfiguration:** Datei `/spiffs/configuration.json` anlegen oder laden, danach `wifi_init_sta_and_softap()`.

## Module (Überblick)

| Modul | Rolle |
|-------|--------|
| `main.c` | Einstieg, SPIFFS, Task-Start, Config-Bootstrap |
| `WLAN.c` / `WLAN.h` | Station + SoftAP, Scan, Persistenz in `configuration.json` |
| `WebServer.c` / `WebServer.h` | `esp_http_server`, statische Inhalte + REST-ähnliche URIs |
| `LED.c` / `LED.h` | LED modes (`led_mode_t` in `main.h`) |
| `TaskControl.c` / `TaskControl.h` | Steuerlogik (siehe Quellcode) |
| `FileManagement.c` | Dateizugriff auf SPIFFS (Existenz, Lesen, JSON schreiben) |
| `cJSON` | JSON für Konfiguration |
| `ProjectConfig.h` | Projektweite Schalter (derzeit u. a. `TaskListOutput`) |

## Globale Symbole (Auszug)

- `productName` in `main.c` (SoftAP SSID, z. B. `"SmartHome Basis"`). HTTP `/FWversion` liefert `app_desc->version` aus `CONFIG_APP_PROJECT_VER` / `version`.
- `config` (`cJSON*`) — WLAN-Konfiguration im RAM, synchron mit Datei.

## Bekannte Code-Stelle (Review-Hinweis)

In `main.c` wird nach `file_isExisting(wifiConfigFile)` zwischen `cJSON_IsNull(config)` und einem `else`-Zweig verzweigt. **Review empfohlen:** Logik und gewünschtes Verhalten bei fehlender/ungültiger Datei explizit festlegen.

## Ethernet

Laut Projektziel vorgesehen; in der analysierten Firmware **nicht** implementiert (keine `ETH_`-Nutzung in `main/`). Hardware-Stand: [hardware.md](hardware.md).
