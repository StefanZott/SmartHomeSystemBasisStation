---
status: open
priority: high
type: docs
created: 2026-09-17
jira: SHBS-5
parent_jira: SHBS-3
---

# BOM, Netzlisten-Export und Dokumentation der Ethernet-Sektion

## Ziel

Abschluss von SHBS-5: Stückliste vervollständigen, Netzliste exportieren und
die Projektdokumentation auf den neuen Stand bringen.

Setzt Tasks `0002`–`0004` voraus.

## Aufgaben

1. **BOM-Felder** an allen neuen Bauteilen pflegen, Konvention aus
   `power_supply.md` übernehmen: Herstellernummer und Mouser-Referenz.
   Betrifft W5500, RJ45, 25-MHz-Quarz, Bias-Widerstand (1 %),
   HV-Kondensator, Terminierungswiderstände, Entkopplung.
2. **Netzliste** neu exportieren (`pcb/BasisStation/BasisStation.net`) und
   `pcb/BasisStation/BasisStation.csv` aktualisieren.
3. **ERC** abschliessend laufen lassen, `ERC.rpt` committen. Ziel: keine neuen
   Fehler gegenüber dem Stand 17.09.2026 (0 Fehler, 9 Warnungen).
4. **`docs/project/ethernet.md`** existiert bereits (angelegt 17.09.2026,
   Architektur und Begründung SPI statt RMII). Hier **ergänzen statt
   duplizieren**: finale Bauteilwerte, gewählter RJ45-Typ, Stand aktualisieren.
5. **`docs/project/hardware.md`:**
   - Zeile „Ethernet" in der Schnittstellen-Tabelle von „Ziel" auf den
     tatsächlichen Stand setzen
   - Neuer Abschnitt „Ethernet (SHBS-5)": W5500 über SPI, GPIO-Belegung als
     Tabelle, RJ45-Typ, Begründung SPI statt RMII (kein EMAC im ESP32-S3)
   - ERC-Stand in „Repository-Ist-Stand" nachziehen
   - Abschnitt „Abgrenzung Firmware" präzisieren: Schaltplan vorhanden,
     Layout offen (**SHBS-10**), Firmware offen (**SHBS-11**)
6. **`docs/project/communication.md`:** Abschnitt „Abgrenzung" korrigieren —
   Ethernet schaltplanseitig vorhanden, in der Firmware-Kommunikationsschicht
   noch nicht angebunden (**SHBS-11**). Erwarteten Durchsatz (15–20 Mbit/s über
   SPI) nennen.
7. **`docs/project/architecture.md`:** Systemüberblick-Diagramm — Ethernet ist
   kein blosses „Ziel" mehr; Abschnitt „Ethernet" am Dateiende auf den neuen
   Stand bringen.
8. **`docs/project/power_supply.md`:** Lastbudget-Tabelle ergänzen
   (ESP32-S3 WLAN-TX ~350 mA, W5500 inkl. LEDs ~150 mA, Status-LEDs ~20 mA →
   ~520 mA @ 3,3 V, entspricht ca. 400 mA am 5-V-Eingang; innerhalb `F1` 1,1 A
   und MP2359 1,2 A).
9. ~~`pcb/architektur_basisStation.drawio` um den Ethernet-Zweig ergänzen~~ —
   **entschieden 18.09.2026: Diagramm gestrichen.** Es lag in drei Dateien
   (`.drawio`, `.png`, `.pdf`) vor, war an vier Stellen veraltet (+24V,
   USB-UART-Bridge, JTAG-Header, fehlendes Ethernet) und duplizierte das
   Textdiagramm in `architecture.md`, das versioniert und im Diff sichtbar ist.
10. Erkenntnisse aus
   [tmp/report/2026-09-17_shbs-5-ethernet-architektur.md](../../report/2026-09-17_shbs-5-ethernet-architektur.md)
   sind damit in `docs/` überführt; Report auf `status: final` setzen.

## Fortschritt (18.09.2026)

### Erledigt — Dokumentation

| Datei | Änderung |
| ----- | -------- |
| `ethernet.md` | Bauteilliste (herstellerspezifisch + Beschaltung), toleranzkritische Werte, Schirmung, Stand je Ticket |
| `hardware.md` | Neuer Abschnitt „Ethernet (SHBS-5)" mit GPIO-Tabelle und Begründung SPI statt RMII; ERC-Stand; Abgrenzung Firmware auf SHBS-10/SHBS-11 präzisiert; Quarz-Bauteilordner ergänzt |
| `communication.md` | Abgrenzung korrigiert, Durchsatz 15–20 Mbit/s, MACRAW-Betrieb, offene Koexistenzfragen für SHBS-11 benannt |
| `architecture.md` | Systemdiagramm neu — Ethernet-Zweig statt „Ziel", JTAG-Header entfernt, `J1`/`J6` benannt; Ethernet-Abschnitt mit Ticket-Tabelle |
| `power_supply.md` | **Lastbudget** ergänzt: ~515 mA @ 3,3 V Worst Case, ~400 mA am 5-V-Eingang, ~36 % von `F1` und ~43 % von `PS1`. Kein Redesign nötig |

Report `2026-09-17_shbs-5-ethernet-architektur.md` auf `status: final`.

### Erledigt — BOM-Felder

| Ref | Hersteller | Herstellernummer | Mouser |
| --- | ---------- | ---------------- | ------ |
| `T1` | Würth Elektronik | 7499011121A | `710-7499011121A` — **ungeprüft** |
| `Y1` | Würth Elektronik | 830059532 | `710-830059532` — **ungeprüft** |
| `U7` | WIZnet | W5500 | **fehlt** |

Die beiden Würth-Nummern sind aus dem üblichen Mouser-Präfix abgeleitet, nicht
verifiziert. Die W5500-Nummer konnte nicht ermittelt werden — Mouser blockiert
automatisierte Zugriffe (Zeitüberschreitung). **Alle drei vor der Bestellung
prüfen.**

Generische Passive (Widerstände, Kondensatoren) tragen projektkonform **keine**
Bestellnummern — wie `R13`, `R23`, `C13`, `C15` im übrigen Projekt auch.

### Erledigt — Footprints (18.09.2026)

Die BOM-Auswertung zeigte **13 Kondensatoren ohne Footprint**. Ohne den
kommen sie beim Übertragen der Netzliste nicht aufs Board.

| Referenzen | Wert | Footprint |
| ---------- | ---- | --------- |
| `C16`–`C22` | 100 nF | `Capacitor_SMD:C_0805_2012Metric` |
| `C23` | 4,7 µF | `Capacitor_SMD:C_0805_2012Metric` |
| `C24` | 10 nF | `Capacitor_SMD:C_0805_2012Metric` |
| `C25`, `C26` | 27 pF | `Capacitor_SMD:C_0805_2012Metric` |
| `C27` | 10 µF | `Capacitor_SMD:C_0805_2012Metric` |
| `C28` | 1 nF/2 kV | `Capacitor_SMD:C_1206_3216Metric` — **vorläufig** |

`C28` hat wegen der 2 kV bewusst die grössere Bauform 1206 bekommen. Der Wert
ist ein Platzhalter: Sobald der konkrete Typ feststeht, gegen dessen Datenblatt
prüfen — 2-kV-Typen verlangen je nach Hersteller 1210 oder grösser.

Alle **35 Bauteile** des Ethernet-Blatts tragen jetzt einen Footprint.

### Offen — nur in KiCad möglich

1. **Netzliste und BOM exportieren.** `BasisStation.net` ist noch vom
   17.09.2026 und kennt weder `U7` noch `T1`, `Y1` und die MDI-Beschaltung.
   Ebenso `BasisStation.csv`.
2. **ERC abschliessend laufen lassen** und `ERC.rpt` festhalten.
3. ~~Architektur-Diagramm~~ — erledigt durch Streichen, siehe oben.

### Offen — kosmetisch aus Task 0004

- `FB1` trägt ein Widerstandssymbol, sollte `Device:FerriteBead` werden.
- `+3V3A` ist ein lokales Label statt eines Power-Symbols.
- `C28` (1 nF / ≥ 2 kV) braucht einen konkreten Typ mit Bestellnummer.

## Akzeptanzkriterien

- [ ] Alle neuen Bauteile mit Herstellernummer und Mouser-Referenz in der BOM.
- [ ] `BasisStation.net` und `BasisStation.csv` neu exportiert.
- [ ] ERC ohne neue Fehler.
- [x] `ethernet.md`, `hardware.md`, `communication.md`, `architecture.md` und
      `power_supply.md` aktualisiert, `last_updated` gesetzt.
- [x] Architektur-Diagramm: drawio gestrichen, Textdiagramm in `architecture.md` zeigt den Ethernet-Zweig.
- [x] Report auf `status: final`.

## Hinweise

Keine Firmware-Änderung in SHBS-5 — daher **keine Versionserhöhung** und kein
Eintrag in `docs/userdoc/releases.md` (vgl. CLAUDE.md, Abweichungen).

## Betroffene Dateien

- `pcb/BasisStation/BasisStation.net`, `BasisStation.csv`, `ERC.rpt`
- `docs/project/ethernet.md`, `hardware.md`, `communication.md`,
  `architecture.md`, `power_supply.md`
- ~~`pcb/architektur_basisStation.drawio`, `.png`, `.pdf`~~ (gestrichen)
- `tmp/report/2026-09-17_shbs-5-ethernet-architektur.md`
