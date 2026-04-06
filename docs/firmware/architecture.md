# Firmware — Architektur

Dokumentationsstand: Initial-Workflow abgeschlossen (2026-04-06), ESP-IDF-Projekt `SmartHomeSystemBasisStation`.

## Architekturdiagramm

Überblick Laufzeit: Startsequenz in `app_main`, persistente Konfiguration und Tasks. **Nur Standard-Markdown:** Diagramm als Text im Code-Block (kein Mermaid).

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
       |-------------------------> WebServer.c --> FileManagment.c
       |                                                    |
       v                                                    v
  xTaskCreatePinnedToCore (3 Tasks)              configuration.json
       |
       +-- ledControlTask -----> LED.c
       +-- executeTaskCotrol --> TaskControl.c
       +-- wifiControlTask ---> WLAN.c --> FileManagment.c --> configuration.json
       |
       v
  configuration.json laden oder anlegen
       |
       v
  wifi_init_sta_and_softap()
```

Die Schreibweisen **executeTaskCotrol** und **FileManagment** entsprechen den tatsächlichen Bezeichnern im Quellcode.

## Build & Metadaten

- Root: `CMakeLists.txt` — `PROJECT_VER` **0.0.1**, `project(SmartHomeSystemBasisStation)`.
- Komponente: `main/CMakeLists.txt` — Quellen und eingebettete SPIFFS-Assets (HTML/CSS/JS/Icons).

## Startablauf (`main/main.c`)

1. **NVS** initialisieren (ggf. Erase bei Versions-/Seitenkonflikt).
2. **Netzwerk-Stack:** `esp_netif_init()`, Default-Event-Loop.
3. **Synchronisation:** Mutex und Binary-Semaphore für LED-Logik.
4. **SPIFFS** unter `/spiffs` mounten (`initSpiffs`).
5. **HTTP-Server** starten (`startWebServer("/spiffs")`).
6. **FreeRTOS-Tasks** (Core-Zuordnung über `PRO_CPU` / `APP_CPU` in `main.h`):
   - `ledControlTask` — LED-Steuerung
   - `executeTaskCotrol` — TaskControl
   - `wifiControlTask` — WLAN
7. **WLAN-Konfiguration:** Datei `/spiffs/configuration.json` anlegen oder laden, danach `wifi_init_sta_and_softap()`.

## Module (Überblick)

| Modul | Rolle |
|-------|--------|
| `main.c` | Einstieg, SPIFFS, Task-Start, Config-Bootstrap |
| `WLAN.c` / `WLAN.h` | Station + SoftAP, Scan, Persistenz in `configuration.json` |
| `WebServer.c` / `WebServer.h` | `esp_http_server`, statische Inhalte + REST-ähnliche URIs |
| `LED.c` / `LED.h` | LED-Modi (`LED_MODE_T` in `main.h`) |
| `TaskControl.c` / `TaskControl.h` | Steuerlogik (siehe Quellcode) |
| `FileManagment.c` | Dateizugriff auf SPIFFS (Existenz, Lesen, JSON schreiben) |
| `cJSON` | JSON für Konfiguration |
| `ProjectConfig.h` | Projektweite Schalter (derzeit u. a. `TaskListOutput`) |

## Globale Symbole (Auszug)

- `productName` / `FW_Version` in `main.c` (aktuell u. a. `"DoorLine Skill"`, `"V0.0.1"` — Abgleich mit Produktname Basisstation bei Bedarf).
- `config` (`cJSON*`) — WLAN-Konfiguration im RAM, synchron mit Datei.

## Bekannte Code-Stelle (Review-Hinweis)

In `main.c` wird nach `file_isExisting(wifiConfigFile)` zwischen `cJSON_IsNull(config)` und einem `else`-Zweig verzweigt. **Review empfohlen:** Logik und gewünschtes Verhalten bei fehlender/ungültiger Datei explizit festlegen (keine stillen Korrekturen in diesem Initial-Dokument).

## Ethernet

Laut Projektziel vorgesehen; in der analysierten Firmware **nicht** implementiert (keine `ETH_`-Nutzung in `main/`).
