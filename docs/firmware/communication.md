# Firmware — Kommunikation

## Persistente Konfiguration (SPIFFS)

| Pfad | Inhalt |
|------|--------|
| `/spiffs/configuration.json` | WLAN: SSID, Passwort, Kanal, RSSI, Auth-Modus, IP, Netmask, Gateway (Felder als JSON; siehe `main.c` / `WLAN.c`) |

Schreibzugriff erfolgt über `file_writeContentInFile()` (`FileManagment`).

## WLAN

- **SoftAP** für Ersteinrichtung / Konfiguration (u. a. festes AP-Passwort und Kanal in `WLAN.c` — siehe Quellcode `AP_ESP_WIFI_*`).
- **Station** für Betrieb im Heimnetz; Parameter aus `configuration.json` und Kconfig (`CONFIG_ESP_WIFI_*`).

## HTTP-Server (`WebServer.c`)

Basis: `esp_http_server`, u. a. Wildcard-Match für statische Dateien unter `/*`.

### Registrierte URI-Beispiele (Auszug)

Konfiguration und Diagnose (GET/POST je nach Handler im Quellcode):

- `/getConnectionInfo`, `/getWifiState`, `/disconnectWIFIHandler`
- `/getInfos`, `/FWversion`
- `/getSsidList`, `/newSSID`
- `/ledTest`, `/ledSingleTest`
- `/alexaTest`
- Statische UI: `/html/*.html`, `/css/*`, `/js/*`, `/img/*`, `/favicon.ico`

Für verbindliche Methoden (GET vs. POST) und Request-Bodies die Implementierung in `WebServer.c` heranziehen.

## Web-Assets

- Laufzeit: primär aus SPIFFS-Pfad `/spiffs` (vgl. `startWebServer`).
- Zusätzlich: `EMBED_FILES` in `main/CMakeLists.txt` für eingebettete Ressourcen.

## Abgrenzung

- Kein separates API-Schema (OpenAPI) im Repository; diese Datei ist die Einstiegsübersicht.
- **Ethernet:** nicht in der aktuellen Firmware-Kommunikationsschicht vorhanden.
