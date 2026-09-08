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

Den Debug-/Daten-USB-Anschluss **J1** (`Connector:USB_B_Micro` in `BasisStation_Debugging.kicad_sch`) durch einen **USB-C-Stecker** ersetzen.

## Ist-Stand

- `BasisStation_Debugging.kicad_sch`: J1 = `USB_B_Micro`, Footprint `61200621621` (6-poliger Würth-Stecker, nicht Micro-USB-Formfaktor — beim Umbau Footprint-Konsistenz prüfen).
- Globale Labels `USB+` / `USB-` verbinden Debugging-Blatt mit Layout.

## Aufgaben

1. USB-C-Receptacle für **USB-2.0-Daten** (D+/D−, CC-Pins, GND, VBUS) auswählen; ggf. gleichen Hersteller-Typ wie Power-USB-C aus Task 0001 für einheitliches Design.
2. J1 im Debugging-Schema ersetzen; CC-Widerstände (Rp) für Sink/Device-Modus setzen.
3. Footprint auf PCB aktualisieren und Leiterbahnen anpassen.
4. Abgrenzung zu Task 0001 klären: separater USB-C-Port für Debug/Flash vs. gemeinsamer Port mit Power-Delivery — im Schaltplan eindeutig trennen oder begründet zusammenführen.
5. ERC/DRC und Netlist-Export ohne Fehler.

## Akzeptanzkriterien

- [ ] J1 ist USB-C (kein USB-B-Micro mehr im Schaltplan/BOM).
- [ ] `USB+`/`USB-` (bzw. USB-2.0-Datenpfad) funktional an ESP32-S3 angebunden.
- [ ] `idf.py flash` / JTAG über den neuen Anschluss möglich (nach Hardware-Bestückung; Verifikation dokumentieren).
- [ ] `docs/project/hardware.md` Schnittstellen-Tabelle aktualisiert.

## Betroffene Dateien

- `pcb/BasisStation/BasisStation_Debugging.kicad_sch`
- `pcb/BasisStation/BasisStation_Layout.kicad_sch`
- `pcb/BasisStation/BasisStation.kicad_pcb`
- `pcb/BasisStation/BasisStation.net`
- `docs/project/hardware.md`
