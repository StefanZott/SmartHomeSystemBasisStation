---
status: active
last_updated: 2026-06-07
subject: KiCad Schaltplan BasisStation
sources:
  - pcb/BasisStation/BasisStation.kicad_sch
  - pcb/BasisStation/BasisStation_Layout.kicad_sch
  - pcb/BasisStation/BasisStation_Debugging.kicad_sch
  - pcb/BasisStation/BasisStation.kicad_pcb
  - pcb/BasisStation/ERC.rpt
  - main/LED.h
---

# KiCad-Schaltplan-Analyse — SmartHome-Basisstation

Analyse des KiCad-Projekts unter `pcb/BasisStation/`. Erstellt im Rahmen der Schaltplan-Review (Juni 2026).

## Methodik und Datenquellen

| Quelle | Verwendung |
|--------|------------|
| `*.kicad_sch` | **Primärquelle** für Bauteilbestand und Blattstruktur |
| `BasisStation.kicad_pcb` | Abgleich Schaltplan ↔ Leiterplatte |
| `main/LED.h` | Abgleich GPIO ↔ Firmware |
| `BasisStation.net` | **Nicht verwendet** — veralteter Export (21.02.2025); enthält Bauteile, die im aktuellen Schaltplan nicht mehr existieren |
| `ERC.rpt` | Electrical Rules Check — aktueller Stand siehe Abschnitt [ERC-Ergebnisse](#erc-ergebnisse) |

### Korrektur gegenüber Erstanalyse

In der ersten Analyse wurden **U2** (`TLV75801PDRV`) und **U3** (`CP2102N`) als vorhanden beschrieben. Diese Bauteile existieren **nur** in der alten Netliste, **nicht** in den aktuellen `.kicad_sch`-Dateien. Der Debugging-Entwurf wurde zwischenzeitlich reduziert.

---

## Projektstruktur

| Blatt | Datei | Inhalt |
|-------|--------|--------|
| Root | `BasisStation.kicad_sch` | Architektur-Übersicht (Diagramm) + hierarchische Unterblätter |
| Layout | `BasisStation_Layout.kicad_sch` | MCU, Versorgung, LEDs, Stecker, Taster |
| Debugging | `BasisStation_Debugging.kicad_sch` | USB-Eingang, ESD-Schutz, Übergabe `USB±` an Layout |
| (alt) | `BasisStation_architektur.kicad_sch` | Variante/Duplikat des Root-Blatts |

KiCad-Projektdatei: `BasisStation.kicad_pro` (Rev 0.0.1 im Netlist-Export).

---

## Blatt „Debugging“ — Ist-Stand

**Platzierte Bauteile (aus `BasisStation_Debugging.kicad_sch`):**

| Ref | Wert | Funktion |
|-----|------|----------|
| J1 | USB_B_Micro | USB-Micro-B-Buchse |
| U1 | D3V3XA4B10LP | 4-Kanal TVS/ESD-Schutz (Diodes Inc., DFN-10) |

Zusätzlich: Local-Label `5VUSB`, Global-Labels `USB+` / `USB-` (Richtung Layout-Blatt), GND-Symbole.

**Nicht vorhanden** (nur noch in veralteter `BasisStation.net`):

- CP2102N (USB-UART) — ehemals U3
- TLV75801 (LDO) — ehemals U2
- USB-Status-LED, Entkopplungskondensatoren, Widerstandsnetzwerk am LDO

```mermaid
flowchart LR
    J1["J1 USB Micro-B"] --> U1["U1 TVS D3V3XA4B10LP"]
    U1 --> GL["USB+ / USB- → Layout-Blatt"]
```

**Hinweis:** Ob `USB±` am Layout-Blatt an die Native-USB-Pins des ESP32-S3 (GPIO19/20) geführt werden, ist in KiCad visuell zu prüfen. In der alten Netliste waren diese Pins offen.

---

## Blatt „Layout“ — Bauteilbestand

| Ref | Wert / Typ | Anmerkung |
|-----|------------|-----------|
| U6 | ESP32-S3-WROOM-1 | Footprint: `ESP32-S3-WROOM-1U` (externe Antenne) |
| PS2 | TSR 1-2433E | DC/DC 12 V → 3,3 V, 1 A (Traco Power) |
| J5 | Conn 2×05 | Footprint Würth **61201021621** (10-pol, JTAG) |
| J6 | Conn 2×03 | Footprint Würth **61200621621** (6-pol, PROG/UART) |
| D7 | YELLOW | WL-TMRC 3 mm |
| D8 | BLUE | WL-TMRW 3 mm |
| D9 | RED | WL-TMRW 3 mm |
| D10 | GREEN | WL-TMRC 3 mm |
| R13–R16 | 220 Ω | LED-Vorwiderstände |
| R9 | 0 Ω | Taster-Netz |
| S2 | 1543-650-149 | Bourns Taster |
| C7, C10, C12 | WCAP-FTXX_P10 | 0,1 µF Film |
| C8 | WCAP-PT5H | 22 µF / 35 V Elko |
| Q1–Q4 | BC337 | NPN — platziert, Verdrahtung in KiCad prüfen (nicht in Netlist-Export) |

---

## Signalzuordnung (Layout)

Aus Netlist-Export vom 21.02.2025 — **nur Layout-Teil**, vor frischer Validierung in KiCad:

### PROG-Stecker J6 (6-pol)

| Pin | Signal (lt. Export) |
|-----|---------------------|
| 1 | EN |
| 2 | +3,3 V |
| 3 | U0TXD / GPIO43 |
| 4 | GND |
| 5 | U0RXD / GPIO44 |
| 6 | GPIO0 / BOOT |

### JTAG-Stecker J5 (10-pol)

| Pin | Signal |
|-----|--------|
| 1 | +3,3 V |
| 2 | MTMS / GPIO42 |
| 3, 5, 7, 9 | GND |
| 4 | MTCK / GPIO39 |
| 6 | MTDO / GPIO40 |
| 8 | MTDI / GPIO41 |
| 10 | NC |

### LEDs ↔ GPIO ↔ Firmware

| LED | Farbe | GPIO (Export) | `LED.h` |
|-----|-------|---------------|---------|
| D7 | Gelb | GPIO3 | `LED_GPIO_YELLOW` ✓ |
| D8 | Blau | GPIO46 | `LED_GPIO_BLUE` ✓ |
| D9 | Rot | GPIO21 | `LED_GPIO_RED` ✓ |
| D10 | Grün | GPIO45 | `LED_GPIO_GREEN` ✓ |

Schaltungsprinzip (Export): Anode an +3,3 V, Kathode über 220 Ω an GPIO → **active-low**.

Firmware: `ON = 4096`, `OFF = 0` (LEDC, 13 Bit). Polarität auf Platine verifizieren.

---

## Leiterplatte — Abgleich Schaltplan

Die PCB (`BasisStation.kicad_pcb`) weicht in der **Referenzvergabe** vom aktuellen Schaltplan ab:

| Schaltplan (Layout) | PCB |
|---------------------|-----|
| U6 | U1 |
| PS2 | PS1 |
| J5, J6 | J1, J2 |
| D7–D10 | D4, D5, D1, D2 |
| S2 | S1 |

**Debugging-Blatt:** J1, U1 (TVS) sind im Schaltplan, aber **nicht** auf der PCB platziert.

**Empfehlung:** In KiCad „Update PCB from Schematic“, Referenzen vereinheitlichen, ERC/DRC ausführen.

---

## Auffälligkeiten und offene Punkte

| # | Thema | Beschreibung | Priorität |
|---|--------|--------------|-----------|
| 1 | Veraltete Netliste | `BasisStation.net` nicht als Ist-Stand nutzen; neu exportieren oder löschen/archivieren | Hoch |
| 2 | Schaltplan ↔ PCB | Unterschiedliche Designatoren; Debugging-Teil fehlt auf PCB | Hoch |
| 3 | Kein CP2102 | Kein onboard USB-UART; UART nur über J6 / externen Adapter | Info |
| 4 | Ethernet | In Doku geplant, im Schaltplan nicht vorhanden | Planung |
| 5 | Taster S2 | Entprellung (C7, R9) laut Export ohne GPIO-Anbindung — in KiCad prüfen | Mittel |
| 6 | EN / J6 / +3V3 | EN-Korrektur, +3V3-Power-Symbol, PS2 +VOUT als **Power output** — ERC Layout **0 Fehler** (07.06.2026) | Erledigt |
| 7 | Q1–Q4 | BC337 platziert, nicht im Netlist-Export — Verdrahtungsstatus klären | Mittel |
| 8 | Symbol U6 | Wert „WROOM-1“, Footprint 1U; Beschreibung erwähnt PCB-Antenne | Niedrig |
| 9 | Native USB ESP32-S3 | GPIO19/20 laut altem Export offen; Debugging nur USB± weiterleiten | Klärung |
| 10 | PWR_FLAG / +3V3 ERC | `#FLG05`/`#FLG06` entfernt; `#FLG04` am +12V; PS2 Pin 3 **Power output**; siehe Task 0028 | Erledigt |
| 11 | ERC Bibliotheken | 28 Warnungen: projekteigene Symbol-/Footprint-Libs nicht eingebunden | Hoch |

---

## ERC-Ergebnisse

Quelle: `pcb/BasisStation/ERC.rpt`

### Vergleich Läufe

| Datum | Fehler | Warnungen | Gesamt | Anmerkung |
|-------|--------|-----------|--------|-----------|
| 06.06.2026 | 3 | 28 | 31 | Vor Korrekturen |
| 07.06.2026 16:20 | 1 | 30 | 31 | Nach EN-, PWR_FLAG- und +3V3-Symbol-Anpassungen |
| **07.06.2026 (final)** | **0** | **~30** | **~30** | Nach PS2 +VOUT → **Power output** (Symbol-Editor) |

### Behobene Fehler (06.06. → 07.06.)

| ERC-Meldung | Status |
|-------------|--------|
| `#PWR039` — EN als falsches Power-Symbol | **Behoben** (EN/J6-Korrektur) |
| `#FLG05` — PS2 `+VOUT` ↔ PWR_FLAG am +3V3 | **Behoben** (`#FLG05` entfernt) |
| `#FLG06` — GND ↔ PWR_FLAG / J1 GND | **Behoben** (`#FLG06` entfernt) |
| `#PWR07` / U6 Pin 2 — `power_pin_not_driven` | **Behoben** (+3V3-Power-Symbol + PS2 Pin 3 als **Power output**) |

### Fehler `/Layout/` — aktuell

**0 Fehler** (KiCad ERC, bestätigt nach Symbol-Korrektur `TSR_1-2433E`).

**Ursache der letzten Meldung:** KiCad ERC erkennt Regler-Ausgänge nur als Versorgungsquelle, wenn Pin 3 (+VOUT) den Typ **Power output** hat (nicht **Output**). Zusätzlich: `+3V3`-Power-Symbol auf der Schiene, `PWR_FLAG` am +12V-Eingang.

### Verbleibende Warnung (1) — `/Layout/`

```
[pin_to_pin]: S2 Pin 1 [Bidirectional] ↔ J1 Pin 5 [GND, Power output]
```

Taster **S2** am globalen GND; harmloser Pin-Typ-Hinweis. Optional: S2-Pin auf **passive** stellen.

### Warnungen Root `/` (28) — unverändert

Alle betreffen **Bibliotheks-Konfiguration**, keine Verdrahtung:

- Footprint-Bibliothek **`Footprints`** fehlt in der KiCad-Konfiguration (14×)
- Projekt-Symbolbibliotheken fehlen: `TSR_1-2433E`, `WCAP-*`, `1543-650-149`, `Espressif`, `WL-TMRC_3MM` (8×)
- Symbol-Mismatch eingebettete vs. Bibliothekskopie: J1, U1, D8–D10 (4×)
- Footprint U1 nicht in `Package_DFN_QFN` gefunden (1×)

**Nächster Schritt nach 0 ERC-Fehlern:** `sym-lib-table` / `fp-lib-table` für `pcb/Symbol/` und `pcb/Footprints/` anlegen (siehe Task-Idee in Analyse vom 06.06.).

### Debugging-Blatt

Keine eigenen Meldungen unter `/Debugging/` — elektrisch unverändert unauffällig.

---

## Reifegrad

| Bereich | Status |
|---------|--------|
| MCU + LEDs + Stecker (Layout) | Weitgehend ausgearbeitet |
| Firmware-Pinout LEDs | Abgestimmt |
| USB / Debugging | Reduziert: ESD + Durchleitung USB± |
| Onboard USB-UART (CP2102) | Entfernt / nicht im aktuellen Schema |
| Ethernet | Nicht begonnen |
| Schaltplan / PCB / Netlist | Synchronisation erforderlich |
| **ERC (Layout)** | **0 Fehler**; ~30 Lib-/Verdrahtungs-Warnungen Root |

**Gesamt:** Entwicklungsstand (~Rev 0.0.1); ERC Layout-Blatt bereinigt (Task 0028). Vor Fertigungsfreigabe: Bibliotheken, PCB-Sync, hängende Drahtenden.

---

## Empfohlene nächste Schritte

1. ~~KiCad → ERC auf allen Blättern~~ **Erledigt** (07.06.2026: 0 Fehler `/Layout/`)
2. ~~+3V3-Versorgung / PS2 Pin-Typ~~ **Erledigt** (Power output + +3V3-Symbol)
3. Projekt-Bibliotheken einbinden (`pcb/Symbol/`, `pcb/Footprints/`) → ~30 Warnungen reduzieren
4. Netliste neu exportieren; alte `BasisStation.net` archivieren oder ersetzen
5. PCB aus Schaltplan aktualisieren (Designatoren synchronisieren)
6. Klären: USB± am Layout → ESP32 Native USB (GPIO19/20) oder nur Durchleitung?
7. S2 an freien GPIO legen (falls Taster-Funktion gewünscht); Pin-Typ optional auf passive
8. Q1–Q4 entfernen oder Transistor-LED-Schaltung fertigstellen
9. Pinbelegung J5/J6 in `docs/project/hardware.md` nach Validierung eintragen

---

## Referenzen

- ERC-Bericht: [pcb/BasisStation/ERC.rpt](../../pcb/BasisStation/ERC.rpt)
- Task PWR_FLAG (erledigt): [tmp/tasks/done/0028_erc-pwr-flag-layout-fehler.md](../tasks/done/0028_erc-pwr-flag-layout-fehler.md)
- Projektdoku: [docs/project/hardware.md](../../docs/project/hardware.md)
- Firmware LEDs: [main/LED.h](../../main/LED.h)
- KiCad-Projekt: [pcb/BasisStation/BasisStation.kicad_pro](../../pcb/BasisStation/BasisStation.kicad_pro)
