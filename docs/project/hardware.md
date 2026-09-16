---
status: active
last_updated: 2026-09-16
type: project-doc
---

# Hardware — SmartHome-Basisstation

KiCad-Layout und physische Schnittstellen der SmartHome-Basisstation auf Basis **ESP32-S3-WROOM-1U-N16R8**.

## Zielbild

Smart-Home-Basisstation mit Tastern, USB/PROG/JTAG, WLAN-Antenne, vier LEDs (Rot, Grün, Blau, Gelb) und **Ethernet** als geplante Schnittstelle.

## Physische Schnittstellen

| Schnittstelle | Zweck |
|---------------|--------|
| USB-C (`J1`) | Debug- und Datenanschluss: natives USB-Serial-JTAG des ESP32-S3. Flashen und On-Chip-Debugging über einen Stecker. Keine Stromversorgung über diesen Port. |
| PROG | Firmware flashen (alternativ über `J1`) |
| JTAG | On-Chip-Debugging (alternativ über `J1`) |
| WLAN | Externe 2,4-GHz-Antenne über U.FL-Pigtail und RP-SMA-Gehäusebuchse (Modul **1U**) |
| Ethernet | Ziel: kabelgebundene Netzwerkverbindung (Umsetzung: Hardware + Firmware prüfen) |

**Annahme (gekennzeichnet):** Die genaue Pinbelegung von PROG/JTAG/Ethernet folgt dem KiCad-Projekt; ohne geöffnetes Schema keine feste Signalzuordnung in dieser Doku.

## Steckverbinder (KiCad / BOM)

Im BOM werden u. a. Würth-Stecker **61201021621** (10-pol) und **61200621621** (6-pol) genannt — Details und Signalbelegung im jeweiligen KiCad-Schaltplan bzw. Datenblatt.

Ausführliche Stückliste mit Links: `README.md` (Abschnitt Hardware) — bei Änderungen auf **ESP32-S3-WROOM-1U-N16R8** abstimmen (README enthält teils gemischte Modulreferenzen).

## WLAN-Antenne (U6, ESP32-S3-WROOM-1U-N16R8)

Das Modul **1U** hat **keine PCB-Antenne**; der RF-Anschluss ist ein **IPEX/U.FL**-Stecker am Modul. Ohne externe Antenne ist WLAN nicht nutzbar.

### RF-Kette (mechanisch, kein Kupfer-RF auf der Platine)

```
U6 (IPEX) ←steckt→ ANT1 Pigtail ←SMA-Bulkhead→ Gehäusewand ←schraubt→ ANT2 Antenne (außen)
```

| Referenz | Teil | Funktion |
|----------|------|----------|
| **ANT1** | Taoglas **CAB.6061** | U.FL → RP-SMA female bulkhead, 100 mm Koax, mit O-Ring |
| **ANT2** | Taoglas **GW.20.5150** | 2,4 GHz Dipol, 2 dBi, RP-SMA male |

Beide Teile sind im Schaltplan `BasisStation_Layout.kicad_sch` als **mechanische BOM-Einträge** (`on_board no`) dokumentiert — sie werden **nicht** auf die Leiterplatte gelötet.

**Polarität:** Pigtail und Antenne müssen **RP-SMA** (Reverse Polarity) sein — nicht mit Standard-SMA mischen.

### Montage

1. Nach SMD-Bestückung: U.FL-Stecker von ANT1 vorsichtig auf den IPEX am Modul U6 aufklicken (gerade, ohne Zug auf dem Kabel).
2. RP-SMA-Bulkhead von ANT1 durch die **Gehäusebohrung** führen und mit der mitgelieferten Mutter fixieren (O-Ring zur Dichtung).
3. ANT2 von außen auf die Bulkhead-Buchse schrauben.

### Gehäuse und PCB — Platzierung

| Thema | Empfehlung |
|-------|------------|
| **SMA-Bohrung** | Ca. **6,5 mm** Durchmesser für RP-SMA-Bulkhead (exakter Wert im Datenblatt CAB.6061 prüfen). |
| **Bulkhead-Position** | Gehäuserand, möglichst weit weg von Metallflächen und anderen HF-Quellen; Kabelweg vom Modul zur Buchse kurz halten. |
| **Abstand U6** | Kein dichtes Metall/Kupfer direkt am IPEX-Anschluss; Kabel nicht über USB-, Ethernet- oder Magnetics-Bereiche führen. |
| **PCB-Layout** | Kein RF-Routing auf der Platine nötig. Freiraum um U6 für Pigtail-Montage einplanen. |

### BOM / Beschaffung

Mouser-Referenzen (Schaltplan-Felder): CAB.6061 (`742-CAB.6061`), GW.20.5150 (`742-GW.20.5150`). Alternativ gleichwertige U.FL→RP-SMA-Bulkhead- und 2,4-GHz-RP-SMA-Antennen-Kombinationen — **Polarität und Steckertyp beibehalten**.

Symbol-Bibliothek: `pcb/Bauteile/Mechanical/mechanical.kicad_sym` (`WLAN_Pigtail`, `WLAN_Antenna`).

## Debug-/Datenanschluss J1 (SHBS-6)

`J1` ist eine **USB-C-Buchse** (Amphenol **12401548E4-2A**, dieselbe Bauform wie der Versorgungsport `J_PWR1` — eine BOM-Position für beide). Symbol: `Connector:USB_C_Receptacle_USB2.0_16P`, Footprint: `Footprints:USB_C_Receptacle_Amphenol_12401548E4-2A`.

| Eigenschaft | Umsetzung |
|-------------|-----------|
| Datenpfad | `J1` → ESD-Array `U1` (D3V3XA4B10LP) → `U6.14`/`U6.13` (GPIO20/GPIO19, USB_D+/USB_D−) |
| Steckrichtung | Beide Datenpaare gebrückt (`A6`+`B6` = D+, `A7`+`B7` = D−) — Stecker funktioniert in beiden Orientierungen |
| Rolle | **Sink/UFP**: je 5,1 kΩ **Rd** von `CC1` (`R21`) und `CC2` (`R22`) gegen GND |
| VBUS | Netz `VBUS_J1`, endet am ESD-Array. **Keine Versorgung über diesen Port** |
| SBU1/SBU2 | Unbeschaltet (No-Connect) |

**Zwei getrennte Ports.** Versorgung läuft ausschließlich über `J_PWR1` (siehe [power_supply.md](power_supply.md)), `J1` ist reiner Datenanschluss. Zum Flashen sind daher **zwei Kabel** nötig. Ein gemeinsamer Port und eine ORing-Lösung wurden verworfen; da `VBUS_J1` nirgends auf die Versorgungsschiene führt, besteht kein Rückspeise-Risiko zwischen den Ports.

Schaltplan: `pcb/BasisStation/BasisStation_Debugging.kicad_sch`.

## Stromversorgung (SHBS-4)

Primäre Versorgung: **USB-C 5 V → MP2359 Buck → 3,3 V**. PS2/+12V entfernt.

Ausführliche Dokumentation (Schaltplan, BOM, Pinbelegung, Verdrahtung): **[power_supply.md](power_supply.md)**.

## Repository-Ist-Stand (KiCad)

| Bereich | Pfad / Artefakt |
|--------|------------------|
| Hauptprojekt | `pcb/BasisStation/BasisStation.kicad_pro` |
| Schaltpläne | u. a. `BasisStation.kicad_sch`, `BasisStation_Layout.kicad_sch`, `BasisStation_Debugging.kicad_sch`, `BasisStation_architektur.kicad_sch` |
| Leiterplatte | `BasisStation.kicad_pcb` |
| Symbole / Footprints | `pcb/Symbol/`, `pcb/Footprints/` |
| Bauteilbibliothek MCU | `pcb/Bauteile/ESP32-S3-WROOM-1U-N16R8/` |
| Mechanische BOM-Teile | `pcb/Bauteile/Mechanical/mechanical.kicad_sym` (ANT1, ANT2) |
| Power (USB-C, Buck) | `pcb/Bauteile/Power/power.kicad_sym` (J_PWR, PS1) |
| ERC-Bericht | `pcb/BasisStation/ERC.rpt` (Stand 16.09.2026: 0 Fehler, 9 Warnungen) |
| Architektur-Diagramm (extern) | `pcb/architektur_basisStation.drawio` |

## Abgrenzung Firmware

Die Firmware in `main/` beschreibt das **Laufzeitverhalten** (WLAN, Webserver, LEDs). Ob und wie **Ethernet** auf der Platine angebunden ist, ergibt sich aus dem KiCad-Projekt; in der aktuellen Firmware gibt es **keine** Ethernet-Treiber-Nutzung.

Netzwerk-Konfiguration über HTTP: [communication.md](communication.md).

## Pflege

Änderungen an Schaltplan, BOM oder Schnittstellen hier und in [communication.md](communication.md) nachziehen.
