---
status: active
last_updated: 2026-09-23
type: project-doc
---

# Architektur — SmartHomeSystemBasisStation

ESP-IDF-Firmware auf **ESP32-S3**, KiCad-Hardware und SPIFFS-Web-UI für die Konfiguration der SmartHome-Basisstation.

## Systemüberblick

```text
Stromversorgung              Rechenkern / Peripherie
─────────────────            ─────────────────────────────────────────

  [USB-C J_PWR1 → Buck
   AP3211 auf 3,3 V] ───────► ESP32-S3-WROOM-1U-N16R8
                                      │
  [Power- / Reset-Taster] ────────────┤
                                      ├──► [4 LEDs, RGBY]
  [USB-C J1, Debug] ──────────────────┤
  [PROG J6] ──────────────────────────┤
                                      ├──► [WLAN-Antenne am Modul 1U]
                                      │
                                      └─SPI─► [W5500] ──► [RJ45 T1] ──► Netzwerk
```

Der separate JTAG-Header ist entfallen — der ESP32-S3 bringt USB-Serial-JTAG
im Chip mit, On-Chip-Debugging läuft über `J1`.

Hardware-Details: [hardware.md](hardware.md). Kommunikation (WLAN, HTTP): [communication.md](communication.md).

## Verzeichnisstruktur (Repository)

| Pfad | Rolle |
|------|--------|
| `main/` | ESP-IDF-Firmware (Ausnahme: statt `embedded/` laut CLAUDE.md) |
| `spiffs/` | Web-Assets (HTML, CSS, JS) → SPIFFS-Image |
| `pcb/` | KiCad-Projekt Basisstation; Bauteildaten je Bauteil in `pcb/Bauteile/<Bauteil>/` (SHBS-12) |
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

## Entwicklungsumgebung (Dev Container)

Die Toolchain ist vollständig im Dev Container unter `.devcontainer/` beschrieben:
ESP-IDF 5.5.2, KiCad 9 (`kicad-cli` für ERC/DRC/BOM), LibreOffice Calc (headless,
rechnet erzeugte Mappen durch) und der Claude-Code-CLI.

**Persistenz über Rebuilds hinweg.** Das Home-Verzeichnis `/home/esp` liegt im
Container-Dateisystem und wird bei jedem Rebuild neu aus dem Image erzeugt.
Persistiert wird gezielt nur `/home/esp/.claude` über das Named Volume
`shbs-claude-state` — dort liegen Login-Token, Sitzungsprotokolle und
Shell-Snapshots des Agenten. Das übrige Home bleibt bewusst flüchtig, weil das
Dockerfile `~/.bashrc` und `~/.config/kicad/9.0/` seedet; diese Dateien müssen
bei Image-Änderungen neu entstehen dürfen.

Nicht persistiert wird `~/.claude.json`. Darin stehen unter anderem die pro
Projekt erteilten Werkzeug-Freigaben — diese gehören stattdessen versioniert in
`.claude/settings.json`, damit sie einen Rebuild überstehen und für alle
Beteiligten gleich sind. Secrets kommen über `secrets/.env` (git-ignoriert) per
`--env-file` in den Container.

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
5. **HTTP-Server** starten (`startWebServer("/spiffs", &http_server)` → `esp_err_t`).
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

- `productName` in `main.c` (SoftAP SSID: `"SmartHome-Basisstation"`). `CONFIG_LWIP_LOCAL_HOSTNAME` in `sdkconfig` identisch. HTTP `/FWversion` liefert `app_desc->version` aus `CONFIG_APP_PROJECT_VER` / `version`.
- `config` (`cJSON*`) — WLAN-Konfiguration im RAM, synchron mit Datei.

## Bekannte Code-Stelle (Review-Hinweis)

In `main.c` wird nach `file_isExisting(wifiConfigFile)` zwischen `cJSON_IsNull(config)` und einem `else`-Zweig verzweigt. **Review empfohlen:** Logik und gewünschtes Verhalten bei fehlender/ungültiger Datei explizit festlegen.

## Ethernet

Angebunden über **WIZnet W5500** am SPI-Bus — der ESP32-S3 hat keine
EMAC-Peripherie, RMII ist deshalb nicht möglich. ESP-IDF betreibt den Baustein
im MACRAW-Modus unter lwIP; firmwareseitig entsteht ein reguläres
`esp_netif`-Interface neben WLAN. Erwarteter Durchsatz 15–20 Mbit/s, begrenzt
durch den SPI-Bus.

| Thema | Ticket | Stand |
|-------|--------|-------|
| Schaltplan und BOM | SHBS-5 | fertig |
| PCB-Layout | SHBS-10 | offen |
| Firmware-Anbindung | SHBS-11 | offen — keine `ETH_`-Nutzung in `main/` |

Architektur und Begründung: **[ethernet.md](ethernet.md)**. Hardware-Stand:
[hardware.md](hardware.md).
