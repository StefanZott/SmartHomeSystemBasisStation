---
status: done
priority: high
type: bugfix
created: 2026-06-08
completed: 2026-06-09
jira: SHBS-7
parent_jira: SHBS-3
---

# U6: Symbol auf ESP32-S3-WROOM-1U-N16R8 korrigieren

## Ziel

Das MCU-Symbol **U6** soll das tatsächlich verwendete Modul **ESP32-S3-WROOM-1U-N16R8** repräsentieren — nicht `ESP32-S3-WROOM-1` (Onboard-PCB-Antenne).

## Ergebnis

| Eigenschaft | Stand |
|-------------|-------|
| `lib_id` | `ESP32-S3-WROOM-1U-N16R8:ESP32-S3-WROOM-1U-N16R8` |
| `Value` | `ESP32-S3-WROOM-1U-N16R8` (Schaltplan, Netlist, PCB) |
| Symbol | Espressif-Stil, 41 Pins, EPAD versteckt gestapelt |
| Footprint (PCB) | `Footprints:ESP32-S3-WROOM-1U` |
| Footprint (Schaltplan) | `RF_Module:ESP32-S3-WROOM-1U` |
| ERC | 0 Fehler |

- **Symbol-Bibliothek:** `pcb/Bauteile/ESP32-S3-WROOM-1U-N16R8/ESP32-S3-WROOM-1U-N16R8.kicad_sym`
- **sym-lib-table:** `pcb/BasisStation/sym-lib-table`
- **Regenerator:** `tmp/gen_symbol.py`

## Akzeptanzkriterien

- [x] U6 `Value` = `ESP32-S3-WROOM-1U-N16R8` im Schaltplan.
- [x] U6 nutzt Espressif-Stil-Symbol aus `pcb/Bauteile/.../ESP32-S3-WROOM-1U-N16R8.kicad_sym`.
- [x] Kein Verweis mehr auf `ESP32-S3-WROOM-1` für U6 (Schaltplan + Netlist + PCB).
- [x] Symbol-Beschreibung nennt IPEX-Antennenanschluss.
- [x] `docs/project/hardware.md` und README konsistent (waren bereits korrekt).

## Bewusst zurückgestellt (separates Ticket)

- fp-lib-table / Footprint-Bibliothek `Footprints` (14 F8-Fehler in `report.txt`)

## Geänderte Dateien

- `pcb/Bauteile/ESP32-S3-WROOM-1U-N16R8/ESP32-S3-WROOM-1U-N16R8.kicad_sym`
- `pcb/BasisStation/sym-lib-table`
- `pcb/BasisStation/BasisStation_Layout.kicad_sch`
- `pcb/BasisStation/BasisStation.kicad_pcb`
- `pcb/BasisStation/BasisStation.net`
- `pcb/BasisStation/ERC.rpt`
