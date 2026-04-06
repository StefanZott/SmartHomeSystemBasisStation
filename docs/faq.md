# FAQ

## Wo finde ich die Projektziele und Agent-Regeln?

In `AGENTS.md` im Repository-Root.

## Wo liegt die Hardware?

KiCad-Projekt unter `PCB/BasisStation/`. Stückliste und Links: `README.md` (Abschnitt Hardware).

## Wo liegt die Firmware?

Verzeichnis `main/` — Einstieg `main.c`.

## Wo ist die Web-Konfiguration?

- Dateien unter `spiffs/` (HTML, CSS, JS).
- Laufzeit: HTTP-Server bedient SPIFFS unter `/spiffs`; Details zu URIs: `docs/firmware/communication.md`.

## Unterstützt die Firmware Ethernet?

Laut Projektkontext (`AGENTS.md`) ist Ethernet ein Ziel. In der bisher analysierten Firmware gibt es **keine** Ethernet-Implementierung in `main/`.

## Welche WLAN-Konfigurationsdatei wird genutzt?

`/spiffs/configuration.json` (Konstante `wifiConfigFile` in `WLAN.c`).

## Widerspricht die README der Ziel-Hardware?

Die README enthält noch Text vom ESP-IDF-Beispielprojekt und eine BOM mit teils gemischten Modulreferenzen. Bei Arbeit an Hardware/README: auf **ESP32-S3-WROOM-1U-N16R8** laut `AGENTS.md` abstimmen.
