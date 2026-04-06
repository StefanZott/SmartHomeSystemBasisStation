# Layout / Hardware — Schnittstellen & Kommunikation

## Geplante / dokumentierte physische Schnittstellen (Projektkontext)

| Schnittstelle | Zweck |
|---------------|--------|
| USB | Debugging (Seriell/JTAG über USB, je nach Design) |
| PROG | Firmware flashen |
| JTAG | On-Chip-Debugging |
| WLAN | Funk, Antenne am Modul **1U** |
| Ethernet | Ziel: kabelgebundene Netzwerkverbindung (Umsetzung: Hardware + Firmware prüfen) |

## Steckverbinder (README / KiCad)

Im BOM werden u. a. Würth-Stecker **61201021621** (10-pol) und **61200621621** (6-pol) genannt — Details und Signalbelegung im jeweiligen KiCad-Schaltplan bzw. Datenblatt.

## Abgrenzung zur Firmware

- **Serielle Konsole:** typisch über USB-UART bzw. JTAG-Adapter; nicht in diesem Dokument duplizieren, sondern auf ESP-IDF-Standardfluss verweisen.
- **Konfiguration über Netz:** siehe `docs/firmware/communication.md` (HTTP im SoftAP/STA-Betrieb).

**Annahme (gekennzeichnet):** Die genaue Pinbelegung von PROG/JTAG/Ethernet folgt dem KiCad-Projekt; ohne geöffnetes Schema keine feste Signalzuordnung in dieser Doku.
