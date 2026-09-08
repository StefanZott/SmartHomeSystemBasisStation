---
status: done
priority: high
type: feature
created: 2026-06-08
completed: 2026-06-12
jira: SHBS-8
parent_jira: SHBS-3
---

# WLAN-Antenne hinzufügen

## Ziel

Eine **externe WLAN-Antenne** für das ESP32-S3-WROOM-**1U**-Modul (IPEX/U.FL-Anschluss) auf der Platine integrieren. Das Modul hat keine Onboard-PCB-Antenne; ohne externe Antenne ist WLAN nicht nutzbar.

## Lösung

**U.FL-Pigtail + externe RP-SMA-Antenne** (mechanische BOM-Einträge, kein RF-Routing auf der Platine):

| Referenz | MPN | Beschreibung |
|----------|-----|--------------|
| ANT1 | Taoglas CAB.6061 | U.FL → RP-SMA female bulkhead, 100 mm |
| ANT2 | Taoglas GW.20.5150 | 2,4 GHz Dipol, RP-SMA male |

Symbol-Bibliothek: `pcb/Bauteile/Mechanical/mechanical.kicad_sym`. Schaltplan: `BasisStation_Layout.kicad_sch` (Textbox zur RF-Kette).

## Akzeptanzkriterien

- [x] U.FL-Pigtail im Schaltplan (mechanisch, `on_board no`); Layout-Platzierung nicht erforderlich (Koax außerhalb PCB).
- [x] RF-Verbindung U6 IPEX ↔ Antenne über Pigtail/Koax dokumentiert (kein 50-Ω-Kupferpfad auf PCB).
- [x] BOM mit Mouser-Referenz (ANT1/ANT2 Felder im Schaltplan).
- [x] Keep-out/Placement in `docs/project/hardware.md` beschrieben.
- [x] Abhängigkeit Task 0004 erfüllt (U6 = ESP32-S3-WROOM-1U-N16R8).

## Geänderte Dateien

- `pcb/BasisStation/BasisStation_Layout.kicad_sch` — ANT1, ANT2, BOM-Felder
- `pcb/Bauteile/Mechanical/mechanical.kicad_sym` — Symbole WLAN_Pigtail, WLAN_Antenna
- `pcb/BasisStation/sym-lib-table` — mechanical-Lib (${KIPRJMOD})
- `docs/project/hardware.md` — Abschnitt WLAN-Antenne

## Hinweise

- `BasisStation.net` ggf. in KiCad neu exportieren (mechanische Teile erscheinen dort optional).
- Gehäusebohrung SMA (~6,5 mm) beim Gehäusedesign umsetzen — in hardware.md dokumentiert.
