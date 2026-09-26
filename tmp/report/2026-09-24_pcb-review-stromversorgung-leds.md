---
type: code-review
created: 2026-09-24
status: draft
---

# PCB-Review: Stromversorgung und Status-LEDs

## Ausgangslage

Der Bediener hat im Leiterplatteneditor die Stromversorgung (J_PWR1, F1, D12,
PS1, L1, D11, C13–C15, R17–R20) und die Status-LEDs (D7–D10, Q1–Q4, R13–R16,
R23–R26) platziert und geroutet. Geprüft wurde
`pcb/BasisStation/BasisStation.kicad_pcb` (Stand 2026-09-24 19:55) mit
`kicad-cli pcb drc --schematic-parity --severity-all` (KiCad 9.0.9, CLI) und
einer Auswertung der Leiterbahnen direkt aus der Datei.

Die Zonen ließen sich per CLI nicht neu füllen: `kicad-cli` hat dafür keine
Option, und das Python-Modul `pcbnew` ist im Container nicht installiert.

## Ergebnis / Befunde

### DRC-Gesamtbild (561 Meldungen)

| Kategorie | Anzahl | Bewertung |
|-----------|-------:|-----------|
| `clearance` (Zone, Abstand 0 mm) | 268 | Artefakt: GND-Füllung stammt von vor dem Routing |
| `hole_clearance` (Zone) | 76 | dito |
| `solder_mask_bridge` (Zone) | 144 | dito |
| `unconnected_items` | 144 | Großteil: Bauteile noch außerhalb der Platine (x < 50 mm) |
| `silk_*`, `text_height` | 63 | Kosmetik, außerhalb des Review-Bereichs |
| `extra_footprint` / `duplicate_footprints` | 7 | 4 Montagelöcher `REF**` ohne Schaltplan-Symbol |
| `copper_edge_clearance` | 4 | USB-C-Buchsen J1/J_PWR1 am Rand — konstruktionsbedingt |
| `clearance` 0,15 < 0,2 mm | 5 | U1 (ESD-Array, Debug-USB) — Pad-Pitch des Footprints |

Die GND-Zonen (F.Cu und B.Cu) enthalten nur Aussparungen für die Montagelöcher.
Die Füllung ist also veraltet. Nach **`B`** (alle Zonen füllen) verschwinden
die rund 490 Zonenmeldungen oder werden zu echten Befunden.

### B1 — USB-C J_PWR1: B4/B9 (VBUS) und A12/B12 (GND) nicht angeschlossen — hoch

Das Symbol `shbs_power:USB_C_Receptacle_Power` hat nur die Pins A1, B1, A4,
A9, A5, B5 und S1. Auf dem PCB sind deshalb **B4, B9, A12 und B12 ohne Netz**.
In Standard-Steckern sind die VBUS- und GND-Kontakte zwar intern verbunden,
die Versorgung funktioniert also. Der Strom verteilt sich aber nur auf die
Hälfte der Kontakte, und das entspricht nicht der USB-C-Spezifikation.

Empfehlung: Im Symbol B4/B9 als gestapelte VBUS-Pins und A12/B12 als GND-Pins
ergänzen (oder die Pins als `passive` stacken), danach mit F8 übernehmen.

### B2 — Alle Leiterbahnen 0,2 mm, nur Netzklasse `Default` — hoch

VBUS, +5V, +3V3, GND und der Schaltknoten sind mit 0,2 mm geroutet. Die
Last liegt bei bis zu ca. 0,5 A (ESP32-S3 beim WLAN-Senden, dazu W5500
ca. 130 mA). Der AP3211 kann bis 1,5 A liefern. 0,2 mm bei 35 µm sind grenzwertig
und erzeugen unnötigen Spannungsabfall. Beim Buck-Wandler kommt die
Induktivität langer, dünner Leitungen hinzu.

Empfehlung: Netzklasse **`Power`** anlegen (0,6–0,8 mm, Abstand 0,2 mm) und
per Muster zuweisen: `/Stromversorgung/VBUS`, `/Stromversorgung/+5V`, `+3V3`,
`GND`, `Net-(D11-K)` (SW). Danach die Leiterbahnen neu verlegen oder
per *Bearbeiten → Leiterbahn- und Via-Eigenschaften bearbeiten* aufweiten.

### B3 — Buck-Wandler zu weit auseinander platziert — hoch

Abstände zum Mittelpunkt von PS1 (66,0 / 53,5):

| Bauteil | Funktion | Abstand | Soll |
|---------|----------|--------:|------|
| C13 | Eingangskondensator VIN–GND | 10,7 mm | < 3 mm, direkt an VIN/GND |
| C15 | Bootstrap BST–SW | 9,0 mm | direkt an den Pins |
| D11 | Freilaufdiode | 10,3 mm | direkt an SW |
| L1 | Speicherdrossel | 17,7 mm | direkt neben SW/D11 |
| C14 | Ausgangskondensator | 16,1 mm | nahe L1 und D11-Anode (GND) |

Leiterbahnlänge des Schaltknotens `Net-(D11-K)` (SW): **40,7 mm**, BST 12,8 mm,
FB 15,5 mm. Der Schaltknoten ist die Hauptquelle für Störabstrahlung und
sollte nur wenige Millimeter lang, dafür breit sein. Die heiße Schleife
C13 → PS1 → D11 → GND muss möglichst klein ausfallen. Die FB-Leitung gehört
kurz und weg vom Schaltknoten (R17/R18 nahe am FB-Pin).

### B4 — +3V3 noch nicht vollständig geroutet — mittel (erwartet)

Offene Luftlinien: vom Buck-Ausgang (Track bei 73,5 / 66,5) zu `U6.2` sowie
zwischen den LED-Anoden D7, D10, D8 und D9 (je Pin 2) und zu U6.2.

### B5 — LED-Zweig — niedrig

- Die LED-Pins sind nach dem F8-Abgleich korrekt: GPIO21, GPIO47, GPIO48 und
  GPIO38 (Pads 23, 24, 25, 31). Die Leitungen R23–R26 → Q-Basis sowie
  Q-Kollektor → R13–R16 → LED-Kathode sind geroutet.
- Die Emitter hängen über THT-Pads an der GND-Zone. Nach dem Füllen prüfen,
  ob Thermal-Spokes entstehen.
- R13–R16 und R23–R26 sind laut Stückliste **Vishay PR02** (2 W) mit dem
  Footprint DIN0617 (Rastermaß 20,32 mm). Bei ca. 5 mA bzw. 0,55 mA sind
  0207/0,25 W oder SMD 0805 ausreichend und sparen viel Fläche. Die
  Mischbestückung steht bereits als offener Punkt in der Stückliste.

### B6 — Kosmetik / Hinweise

- Footprint von PS1 heißt noch `shbs_power:MP2359DJ`. Das Gehäuse (SOT-23-6)
  passt, der Schaltplan-Abgleich (Parity) ist fehlerfrei. Die Pad-Zuordnung
  sollte trotzdem einmal gegen das AP3211-Datenblatt geprüft und der
  Footprint für die Nachvollziehbarkeit umbenannt werden.
- Die vier Montagelöcher erzeugen `extra_footprint`: im Footprint
  *Nicht in Schaltplan* setzen oder Symbole `MountingHole` ergänzen.
- `track_dangling` GND bei (21,76 / 90,33): 0,07-mm-Stummel löschen.

## Empfehlungen

1. Zonen füllen (`B`), DRC erneut laufen lassen.
2. Symbol J_PWR1 um B4/B9/A12/B12 ergänzen (B1).
3. Netzklasse `Power` anlegen und Versorgungsleitungen aufweiten (B2).
4. Buck-Wandler kompakt um PS1 neu platzieren: C13 und C15 direkt an den
   Pins, D11/L1 am SW-Pin, C14 dicht dahinter (B3).
5. +3V3 zu U6 und zu den LED-Anoden routen (B4).

## Nächste Schritte

- Die Punkte B1 (Symboländerung) und B2 (Netzklasse) betreffen Projektdateien.
  Die Umsetzung erfolgt nach Freigabe über JIRA-Ticket und Task.
- Nach der Umplatzierung erneut reviewen.
