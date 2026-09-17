---
status: active
last_updated: 2026-09-17
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
| Ethernet | Kabelgebundene Netzwerkverbindung über **WIZnet W5500** (SPI). Architektur und Begründung: [ethernet.md](ethernet.md). Schaltplan in Arbeit (SHBS-5), Layout offen (SHBS-10), Firmware offen (SHBS-11) |

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

## Status-LEDs (SHBS-9)

Vier Status-LEDs, je über einen NPN-Transistor als **Low-Side-Schalter** gegen GND geschaltet. Die LED-Anoden liegen gemeinsam auf +3V3, die Emitter aller Transistoren auf GND. Ein GPIO auf **High** schaltet die zugehörige LED **ein**.

| LED | Farbe | Transistor | GPIO (Modul-Pad) | Basiswiderstand | Vorwiderstand |
|-----|-------|------------|------------------|-----------------|---------------|
| `D7` | Gelb | `Q4` | GPIO21 (23) | `R23`, 4,7 kΩ | `R13`, 220 Ω |
| `D9` | Rot | `Q3` | GPIO38 (31) | `R24`, 4,7 kΩ | `R15`, 220 Ω |
| `D10` | Grün | `Q2` | GPIO47 (24) | `R25`, 4,7 kΩ | `R16`, 220 Ω |
| `D8` | Blau | `Q1` | GPIO48 (25) | `R26`, 4,7 kΩ | `R14`, 220 Ω |

Transistoren: **BC337** (NPN, TO-92, Pinbelegung 1=C, 2=B, 3=E).

**Dimensionierung:** Der Vorwiderstand stellt bei ca. 2 V Flussspannung rund 5 mA LED-Strom ein. Der Basiswiderstand begrenzt den Basisstrom auf ca. 0,55 mA — ausreichend für sichere Sättigung und unkritisch für den GPIO-Treiber. Ohne diesen Widerstand wirkt die Basis-Emitter-Strecke als Diode gegen GND und der Pin-Strom wäre nur durch die Treiberimpedanz begrenzt.

**Pinwahl:** Bewusst auf GPIOs **ohne** Strapping-, ADC- oder Touch-Funktion gelegt. Die Strapping-Pins GPIO3, GPIO45 und GPIO46 waren zuvor belegt und sind jetzt frei — ein an der Basis hängender Pegel hätte beim Reset die Boot-Konfiguration beeinflussen können (GPIO45 = VDD_SPI-Spannung, GPIO46 = ROM-Log, GPIO3 = JTAG-Quellenwahl, relevant wegen `J5`).

**Nicht verwenden:** GPIO35, GPIO36 und GPIO37 erscheinen in der Netzliste als frei, sind beim Modul **N16R8** aber intern vom Octal-PSRAM belegt.

Schaltplan: `pcb/BasisStation/BasisStation_Layout.kicad_sch`.

## Repository-Ist-Stand (KiCad)

| Bereich | Pfad / Artefakt |
|--------|------------------|
| Hauptprojekt | `pcb/BasisStation/BasisStation.kicad_pro` |
| Schaltpläne | u. a. `BasisStation.kicad_sch`, `BasisStation_Layout.kicad_sch`, `BasisStation_Debugging.kicad_sch`, `BasisStation_architektur.kicad_sch` |
| Leiterplatte | `BasisStation.kicad_pcb` |
| Bauteilbibliotheken | `pcb/Bauteile/<Bauteil>/` — **ein Ordner je Bauteil** mit Symbol, Footprint und 3D-Modell (SHBS-12) |
| Mechanische BOM-Teile | `pcb/Bauteile/Mechanical/mechanical.kicad_sym` (ANT1, ANT2) |
| Power (USB-C, Buck) | `pcb/Bauteile/Power/` (J_PWR, PS1) |
| Ethernet | `pcb/Bauteile/W5500/`, `pcb/Bauteile/wuerth_7499011121A/` (SHBS-5) |
| ERC-Bericht | `pcb/BasisStation/ERC.rpt` (Stand 17.09.2026 nach SHBS-12: **0 Fehler, 7 Warnungen**) |
| Architektur-Diagramm (extern) | `pcb/architektur_basisStation.drawio` |

## Abgrenzung Firmware

Die Firmware in `main/` beschreibt das **Laufzeitverhalten** (WLAN, Webserver, LEDs). In der aktuellen Firmware gibt es **keine** Ethernet-Treiber-Nutzung — die Anbindung über `esp_eth` ist als **SHBS-11** offen. Hintergrund: [ethernet.md](ethernet.md).

Netzwerk-Konfiguration über HTTP: [communication.md](communication.md).

## Bibliotheksstruktur (SHBS-12)

Symbol, Footprint und 3D-Modell eines Bauteils liegen **gemeinsam** in
`pcb/Bauteile/<Bauteil>/`. Die früheren Sammelordner `pcb/Symbol/`,
`pcb/Footprints/` und `pcb/3D-Model/` gibt es nicht mehr.

Je Bauteilordner ist ein Eintrag in `sym-lib-table` (falls ein eigenes Symbol
existiert) und in `fp-lib-table` gesetzt. Alle Pfade sind über `${KIPRJMOD}`
projektrelativ — absolute Pfade sind unzulässig, weil sie nur auf einem
Rechner funktionieren.

Neues Bauteil anlegen:

1. Ordner `pcb/Bauteile/<Bauteil>/` mit Symbol, Footprint und 3D-Modell.
2. 3D-Referenz im Footprint auf `${KIPRJMOD}/../Bauteile/<Bauteil>/<Datei>`.
3. Eintrag in `sym-lib-table` und `fp-lib-table` ergänzen.
4. Footprint-Vorgabe im Symbol auf `<Bibliothek>:<Footprint>` setzen.

## Pflege

Änderungen an Schaltplan, BOM oder Schnittstellen hier und in [communication.md](communication.md) nachziehen.
