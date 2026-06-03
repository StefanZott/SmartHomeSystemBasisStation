---
status: active
last_updated: 2026-06-02
type: project-doc
---

# Sicherheitskonzept — SmartHomeSystemBasisStation

Grundlegendes Sicherheitsmodell für Firmware, Web-UI und lokale Speicherung (Stand Repository, Firmware-Version `0.00.001`).

Verwandte Dokumente: [communication.md](communication.md), [memory_map.md](memory_map.md), [architecture.md](architecture.md).

## Angriffsfläche (Überblick)

| Bereich | Technologie | Erreichbarkeit |
|---------|-------------|----------------|
| Konfiguration Web-UI | HTTP (`esp_http_server`) | SoftAP und LAN (Station) |
| WLAN-Einrichtung | SoftAP WPA2-PSK | Funkreichweite des Geräts |
| Persistente Konfiguration | SPIFFS (`configuration.json`) | Lokal am Gerät / über HTTP-API |
| System-/WiFi-Daten | NVS (ESP-IDF) | Lokal am Gerät |
| Firmware-Update | USB/PROG/JTAG | Physischer Zugriff |
| OTA | — | **Nicht implementiert** |

## Berechtigungsmodell Web-UI

- **Keine Benutzer-Authentifizierung** an den HTTP-Endpunkten (`WebServer.c`): Jeder Client im SoftAP oder im gleichen LAN wie die Station kann Konfigurations- und Diagnose-URIs aufrufen (z. B. `/newSSID`, `/getConnectionInfo`, `/ledTest`).
- Die Web-UI dient der **Gerätekonfiguration**, nicht der Mandantentrennung mehrerer Benutzer.
- **Empfehlung Betrieb:** Gerät nur in vertrauenswürdigen Netzwerken betreiben; SoftAP nach Ersteinrichtung deaktivieren bzw. nicht dauerhaft im Feld offen lassen.

## WLAN / SoftAP

| Aspekt | Ist-Stand (Quellcode) |
|--------|------------------------|
| SoftAP-Passwort | Fest im Code: `AP_ESP_WIFI_PASS` = `"telegaertner"` (`WLAN.c`, `WLAN.h`) |
| SoftAP-Kanal | Fest: Kanal `1` |
| Station | Credentials aus `configuration.json` (Klartext JSON auf SPIFFS) |
| Auth-Modus AP | WPA2-PSK (wenn Passwort gesetzt) |

**Risiko:** Bekanntes, geräteübergreifend gleiches SoftAP-Passwort — Angreifer in Funkreichweite können sich verbinden und die Konfigurations-UI nutzen.

**Mitigation (empfohlen, noch nicht umgesetzt):** Einzigartiges Passwort pro Gerät (Label/QR), zeitlich begrenzter Setup-Modus, Passwort über Kconfig/`secrets/` statt Hardcoding.

## Transport & Verschlüsselung

- **HTTP ohne TLS** — kein HTTPS, keine Zertifikatsprüfung.
- WLAN-Credentials und Konfigurations-JSON werden **unverschlüsselt** über HTTP übertragen, sobald ein Client die UI nutzt.
- **Empfehlung:** TLS (HTTPS) oder zumindest isoliertes Setup-Netz; für Produktion Security-Review vor Freigabe.

## Lokale Speicherung

### SPIFFS (`/spiffs/configuration.json`)

- Enthält u. a. SSID, Passwort, IP-Parameter als **Klartext-JSON**.
- Schreibzugriff über Firmware (`FileManagment.c`); lesbar über HTTP-Handler.
- Keine Datei-Verschlüsselung auf Application-Ebene.

### NVS

- ESP-IDF nutzt NVS u. a. für WiFi-Stack (`CONFIG_ESP_WIFI_NVS_ENABLED=y`).
- Kein anwendungsspezifisches Secrets-Management im Repository.

### Flash-Verschlüsselung

- `CONFIG_SECURE_FLASH_ENC_ENABLED` ist **nicht** aktiv — Flash-Inhalt bei physischem Auslesen grundsätzlich zugänglich (mit entsprechendem Equipment).

## Physische Schnittstellen

USB, PROG und JTAG ermöglichen Flash und Debug bei physischem Zugriff. Siehe [hardware.md](hardware.md).

**Empfehlung:** Produktgehäuse, Debug-Pins nur in Entwicklung, Secure Boot / Flash Encryption für Seriengeräte evaluieren.

## OTA (Over-the-Air Update)

- Partitionstabelle: **kein OTA-Slot** (`partitions.csv` — nur `factory`-App).
- Keine OTA-Implementierung in `main/`.
- **Plan (optional):** Zweite App-Partition, signierte Images, HTTPS-OTA — vor Umsetzung separates Security-Design und Threat Model Update.

## Risk Assessment (Kurz)

| ID | Risiko | Eintritt | Auswirkung | Priorität | Maßnahme |
|----|--------|----------|------------|-----------|----------|
| R1 | Fest codiertes SoftAP-Passwort | Mittel | Mittel | Hoch | Pro-Gerät-Secret, kein Hardcoding |
| R2 | Offene HTTP-API ohne Login | Hoch | Hoch | Hoch | Auth für Schreib-Operationen / Setup-Modus |
| R3 | Klartext WLAN-Credentials auf SPIFFS | Mittel | Hoch | Hoch | Verschlüsselung NVS/SPIFFS oder Credential-Store |
| R4 | Kein TLS | Mittel | Mittel | Mittel | HTTPS für Produktion |
| R5 | Physischer Flash-Zugriff | Niedrig | Hoch | Mittel | Gehäuse, Flash Encryption evaluieren |
| R6 | Kein OTA / manuelles Flash | — | Niedrig | Niedrig | OTA-Konzept bei Bedarf |

## Pflege

Bei Änderungen an `WLAN.c`, `WebServer.c`, `partitions.csv` oder Speicherlayout diese Datei und [memory_map.md](memory_map.md) prüfen.
