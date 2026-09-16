---
status: open
priority: medium
type: feature
created: 2026-06-08
jira: SHBS-6
parent_jira: SHBS-3
---

# J1 (USB-B-Micro) durch USB-C ersetzen

## Ziel

Den Debug-/Daten-USB-Anschluss **J1** (`Connector:USB_B_Micro` in `BasisStation_Debugging.kicad_sch`) durch eine **USB-C-Buchse** ersetzen.

## Ist-Stand (Analyse 2026-09-15)

Netze aus `BasisStation_Debugging.kicad_sch` zurückverfolgt:

| Netz | Pins |
| ---- | ---- |
| `USB+` | `J1.3` (D+), `U1.2`, `U1.9` (NC) → Layout → **`U6.14` (GPIO20/USB_D+)** |
| `USB-` | `J1.2` (D−), `U1.1`, `U1.10` (NC) → Layout → **`U6.13` (GPIO19/USB_D−)** |
| `5VUSB` | `J1.1` (VBUS), `U1.4`, `U1.7` (NC) |
| GND | `J1.5`, `J1.6` (Shield), `#PWR01` |

- **Datenpfad ist intakt:** `J1` → ESD-Array `U1` (D3V3XA4B10LP) → `U6` Pin 13/14. Das ist das native **USB-Serial-JTAG** des ESP32-S3 — Flashen und Debuggen über einen Anschluss.
- **`5VUSB` ist ein toter Netzname.** Das Label kommt projektweit genau einmal vor. `J1` Pin 1 geht nur ans ESD-Array, sonst nirgendwohin. Die Platine lässt sich über den Debug-Port **nicht** versorgen; umgekehrt gibt es dadurch kein Rückspeise-Risiko zwischen den Ports.
- `J1` hat **kein Footprint-Feld** gesetzt (gleiche Kategorie wie Befund B13 in [Task 0001](0001_usb-c-12v-stromversorgung.md)).
- `J1.4` (ID) ist unverbunden — entfällt mit USB-C ersatzlos.

## Entscheidungen

### Port-Konzept (2026-09-15, Bediener) — Aufgabe 4 erledigt

**Zwei getrennte Ports.** `J_PWR1` bleibt die Stromversorgung, `J1` wird ein reiner Datenanschluss; `VBUS` von `J1` bleibt wie bisher unbeschaltet (nur am ESD-Array). Verworfen wurden: ein gemeinsamer Port für Strom und Daten (hätte SHBS-4 teilweise zurückgebaut) sowie zwei Ports mit ORing-Diode.

**Konsequenz für die Praxis:** Zum Flashen sind immer zwei Kabel nötig — Versorgung an `J_PWR1`, Daten an `J1`.

### Bauteil (2026-09-15) — dieselbe Buchse wie die Stromversorgung

Die **Amphenol 12401548E4#2A** ist verwendbar. Beleg: `pcb/Footprints/USB_C_Receptacle_Amphenol_12401548E4-2A.kicad_mod` enthält **30 Pads** — die komplette A-Reihe `A1`–`A12` (SMD), die komplette B-Reihe `B1`–`B12` (THT), vier Schirmpins `S1` und zwei Montagebohrungen. Es ist eine **vollbestückte 24-polige** USB-C-Buchse, keine Power-only-Variante; `A6`/`A7` und `B6`/`B7` sind physisch vorhanden.

Die frühere Annahme „Amphenol 12401548E4-2A ist power-only, für Daten wird ein anderer Typ gebraucht" war ein Fehlschluss aus dem **Symbol** `shbs_power:USB_C_Receptacle_Power`, das nur 7 der 24 Pins abbildet (`A4`/`A9` VBUS, `A5`/`B5` CC, `A1`/`B1` GND, `S1`).

Vorteile: eine BOM-Position statt zwei, Footprint existiert bereits, beide Buchsen bauform- und höhengleich.

### Symbolquelle (16.09.2026) — entschieden

`Connector:USB_C_Receptacle_USB2.0_16P` ist in der KiCad-Installation vorhanden und wird verwendet. Kein eigenes Projektsymbol nötig.

Wichtig für spätere Arbeiten am Symbol: KiCad **stapelt** die redundanten VBUS-Pins (`A4`/`B4`/`A9`/`B9`) und GND-Pins (`A1`/`B1`/`A12`/`B12`) auf jeweils einer Position. Ein Draht an `A4` bzw. `A1` verbindet alle vier — in der Netzliste bestätigt.

Verworfen wurde die Alternative, ein eigenes Symbol in der Projektbibliothek zu pflegen — unnötiger Aufwand, da das Standardsymbol passt. Die acht SuperSpeed-Pads des Footprints bleiben netzlos; bei USB-2.0-Nutzung ist das normal.

### Nebenwirkung: GND ohne ERC-Treiber (16.09.2026)

Das alte Symbol `Connector:USB_B_Micro` hatte seinen GND-Pin (Pin 5) als **Power output** deklariert. Dieser Pin war — unbemerkt — der einzige ERC-Treiber des globalen GND-Netzes. Das USB-C-Symbol deklariert GND als `power_in`, wie alle übrigen GND-Pins im Projekt (`J_PWR1`, `PS1`, `U6`). Folge: `power_pin_not_driven` im Debugging-Blatt.

[Task 0028](../done/0028_erc-pwr-flag-layout-fehler.md) hatte das GND-`PWR_FLAG` seinerzeit entfernt — unter der Annahme, GND sei versorgt. Das war es auch, nur durch ein Steckersymbol. Diese Annahme ist mit dem Umbau entfallen.

**Behoben** durch `PWR_FLAG` (`#FLG04`) am GND-Draht von `J_PWR1.A1` in `Stromversorgung.kicad_sch`. Bleibt Variante A aus Task 0028 (KiCad-Standardweg, keine ERC-Ausnahmen).

## Aufgaben

1. [x] ~~Prüfen, ob `Connector:USB_C_Receptacle_USB2.0_16P` vorhanden ist~~ — vorhanden, verwendet.
2. [x] `J1` im Debugging-Blatt ersetzt:
   - **`A6`+`B6` (D+) und `A7`+`B7` (D−) jeweils zusammenführen.** Bei USB-C liegen die Datenpaare doppelt an; ohne diese Brücke funktioniert der Stecker nur in **einer** von zwei Steckrichtungen. Klassischer Fehler bei USB-2.0-Designs.
   - `CC1`/`CC2` je **5,1 kΩ Rd gegen GND** (`R21`, `R22` — beide Bezeichner sind frei).
   - `SHIELD` an GND, `SBU1`/`SBU2` offen, `VBUS` unverändert nur am ESD-Array.
3. [x] Footprint `Footprints:USB_C_Receptacle_Amphenol_12401548E4-2A` an `J1` zugewiesen.
4. [x] ~~Abgrenzung zu Task 0001 klären~~ — erledigt, siehe Entscheidung oben.
5. [x] ERC und Netzlisten-Export ohne Fehler (16.09.2026: 0 Fehler, 9 Warnungen).

**Verbleibend:** Akzeptanzkriterium „`idf.py flash` / JTAG über den neuen Anschluss" lässt sich erst nach Bestückung der Hardware prüfen. Alles andere ist erledigt.

**Nicht in diesem Task:** PCB-Layout und DRC. Wird zusammen mit dem Layout aus [Task 0001](0001_usb-c-12v-stromversorgung.md) nachgezogen, damit die Netzliste nur einmal ins Board übernommen werden muss.

## Korrektur am ursprünglichen Task

Die frühere Formulierung „CC-Widerstände (**Rp**) für Sink/Device-Modus" war fachlich falsch. Ein Sink/UFP braucht **Rd** — 5,1 kΩ von `CC1` und `CC2` **gegen GND**. `Rp` ist die Bestückung einer Source/DFP; damit würde der Port als Host auftreten und kein Hostgerät würde die Verbindung aufbauen. Rd ist auch dann nötig, wenn `VBUS` unbenutzt bleibt — ohne Rd erkennt der Host das Gerät gar nicht und der Datenpfad kommt nicht zustande.

## Akzeptanzkriterien

- [x] `J1` ist USB-C (kein USB-B-Micro mehr im Schaltplan/BOM).
- [x] Beide Datenpaare (`A6`/`B6`, `A7`/`B7`) gebrückt — Stecker funktioniert in beiden Orientierungen.
- [x] `CC1`/`CC2` mit je 5,1 kΩ **Rd** gegen GND.
- [x] `USB+`/`USB-` weiterhin funktional an `U6.14`/`U6.13` angebunden.
- [x] `J1` hat einen Footprint zugewiesen.
- [x] ERC ohne Fehler, Netzliste exportiert.
- [ ] `idf.py flash` / JTAG über den neuen Anschluss möglich (nach Hardware-Bestückung; Verifikation dokumentieren).
- [x] `docs/project/hardware.md` Schnittstellen-Tabelle aktualisiert.

## Fortschritt

- 2026-09-16: **Schaltplan umgesetzt.** `J1` durch `Connector:USB_C_Receptacle_USB2.0_16P` ersetzt, beide Datenpaare gebrückt, `R21`/`R22` als Rd gesetzt, Footprint zugewiesen, `5VUSB` → `VBUS_J1` umbenannt. Netzliste verifiziert: `USB+` = `J1.A6`+`J1.B6`+`U1.2`+`U6.14`, `USB-` = `J1.A7`+`J1.B7`+`U1.1`+`U6.13`, `VBUS_J1` = alle vier VBUS-Pins + `U1.4`, GND = alle vier GND-Pins + `S1`. GND-Treiber über `#FLG04` wiederhergestellt. **ERC: 0 Fehler, 9 Warnungen** (alle Altbestand). `hardware.md` aktualisiert. **Offen:** nur noch die Flash-/JTAG-Verifikation nach Hardware-Bestückung.
- 2026-09-15: Ist-Stand analysiert (Netze, Datenpfad zu `U6`, toter `5VUSB`-Netzname, fehlender Footprint). Port-Konzept entschieden (zwei getrennte Ports). Bauteilfrage geklärt — die vorhandene Amphenol-Buchse ist vollbestückt und wiederverwendbar, es fehlt nur ein Symbol mit Datenpins. Rp/Rd-Fehler im Task korrigiert. **Nächster Schritt:** Aufgabe 1 (Symbolverfügbarkeit in KiCad prüfen).
- 2026-06-08: Task angelegt.

## Betroffene Dateien

- `pcb/BasisStation/BasisStation_Debugging.kicad_sch`
- `pcb/BasisStation/BasisStation.net`
- `pcb/BasisStation/Stromversorgung.kicad_sch` (PWR_FLAG `#FLG04`)
- `pcb/BasisStation/ERC.rpt`
- `docs/project/hardware.md`
- ggf. Projekt-Symbolbibliothek (falls kein KiCad-Standardsymbol passt)
