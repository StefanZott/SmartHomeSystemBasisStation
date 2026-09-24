---
status: active
last_updated: 2026-09-24
type: project-doc
---

# Hardware — SmartHome-Basisstation

KiCad-Layout und physische Schnittstellen der SmartHome-Basisstation auf Basis **ESP32-S3-WROOM-1U-N16R8**.

## Zielbild

Smart-Home-Basisstation mit Tastern, USB-C-Debuganschluss, PROG-Header, WLAN-Antenne, vier LEDs (Rot, Grün, Blau, Gelb) und **Ethernet** über W5500.

## Physische Schnittstellen

| Schnittstelle | Zweck |
|---------------|--------|
| USB-C (`J1`) | Debug- und Datenanschluss: natives USB-Serial-JTAG des ESP32-S3. Flashen und On-Chip-Debugging über einen Stecker. Keine Stromversorgung über diesen Port. |
| PROG (`J6`) | 6-poliger Header: Firmware flashen über UART (alternativ über `J1`) |
| WLAN | Externe 2,4-GHz-Antenne über U.FL-Pigtail und RP-SMA-Gehäusebuchse (Modul **1U**) |
| Ethernet | Kabelgebundene Netzwerkverbindung über **WIZnet W5500** (SPI). Architektur und Begründung: [ethernet.md](ethernet.md). Schaltplan in Arbeit (SHBS-5), Layout offen (SHBS-10), Firmware offen (SHBS-11) |

**Separater JTAG-Header entfallen.** Der ESP32-S3 bringt USB-Serial-JTAG im Chip mit; On-Chip-Debugging läuft über `J1`. Der frühere 10-polige Header `J5` wurde deshalb aus dem Schaltplan entfernt — ein Steckverbinder und dessen Platinenfläche weniger.

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
| **ANT2** | Taoglas **GW.20.A151** (Nachfolger der abgekündigten GW.20.5150) | 2,4 GHz Dipol, 2 dBi, RP-SMA male |

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

Mouser-Referenzen: CAB.6061 → **`960-CAB.6061`** (845 ab Lager, Stand 2026-09-22). Alternativ gleichwertige U.FL→RP-SMA-Bulkhead- und 2,4-GHz-RP-SMA-Antennen-Kombinationen — **Polarität und Steckertyp beibehalten**.

`ANT2` ist seit 2026-09-23 (SHBS-16) der Taoglas-Seriennachfolger
**`GW.20.A151`** (`960-GW.20.A151`); der ursprünglich vorgesehene `GW.20.5150`
ist abgekündigt. Form, Anschluss und Gewinn sind gleich (2 dBi, 2,4 GHz,
RP-SMA(M) gerade), eine weiße Variante `960-GW.20.A151W` gibt es ebenfalls.
Taoglas führt bei Mouser inzwischen das Präfix `960-` statt `742-`. `ANT1` und
`ANT2` sind mit `on_board no` reine BOM-Einträge; kein Footprint betroffen.
Aktuelle Preise und Lager: bestellfähige Stückliste (Abschnitt unten).

Symbol-Bibliothek: `pcb/Bauteile/Mechanical/mechanical.kicad_sym` (`WLAN_Pigtail`, `WLAN_Antenna`).

## Debug-/Datenanschluss J1 (SHBS-6)

`J1` ist eine **USB-C-Buchse** (Amphenol **12401598E4#2A**, dieselbe Bauform wie der Versorgungsport `J_PWR1` — eine BOM-Position für beide). Symbol: `Connector:USB_C_Receptacle_USB2.0_16P`, Footprint: `shbs_power:USB_C_Receptacle_Amphenol_12401598E4-2A`. Bis 2026-09-23 war die inzwischen abgekündigte `12401548E4#2A` vorgesehen; Unterschiede und Folgen fürs Layout siehe [power_supply.md](power_supply.md) (Abschnitt Buchsenwechsel).

| Eigenschaft | Umsetzung |
|-------------|-----------|
| Datenpfad | `J1` → ESD-Array `U1` (D3V3XA4B10LP-7) → `U6.14`/`U6.13` (GPIO20/GPIO19, USB_D+/USB_D−) |
| Steckrichtung | Beide Datenpaare gebrückt (`A6`+`B6` = D+, `A7`+`B7` = D−) — Stecker funktioniert in beiden Orientierungen |
| Rolle | **Sink/UFP**: je 5,1 kΩ **Rd** von `CC1` (`R21`) und `CC2` (`R22`) gegen GND |
| VBUS | Netz `VBUS_J1`, endet am ESD-Array. **Keine Versorgung über diesen Port** |
| SBU1/SBU2 | Unbeschaltet (No-Connect) |

**Zwei getrennte Ports.** Versorgung läuft ausschließlich über `J_PWR1` (siehe [power_supply.md](power_supply.md)), `J1` ist reiner Datenanschluss. Zum Flashen sind daher **zwei Kabel** nötig. Ein gemeinsamer Port und eine ORing-Lösung wurden verworfen; da `VBUS_J1` nirgends auf die Versorgungsschiene führt, besteht kein Rückspeise-Risiko zwischen den Ports.

Schaltplan: `pcb/BasisStation/BasisStation_Debugging.kicad_sch`.

## Stromversorgung (SHBS-4)

Primäre Versorgung: **USB-C 5 V → AP3211 Buck → 3,3 V** (bis SHBS-17: MP2359, abgekündigt). PS2/+12V entfernt.

Ausführliche Dokumentation (Schaltplan, BOM, Pinbelegung, Verdrahtung): **[power_supply.md](power_supply.md)**.

## Status-LEDs (SHBS-9)

Vier Status-LEDs, je über einen NPN-Transistor als **Low-Side-Schalter** gegen GND geschaltet. Die LED-Anoden liegen gemeinsam auf +3V3, die Emitter aller Transistoren auf GND. Ein GPIO auf **High** schaltet die zugehörige LED **ein**.

| LED | Farbe | Transistor | GPIO (Modul-Pad) | Basiswiderstand | Vorwiderstand |
|-----|-------|------------|------------------|-----------------|---------------|
| `D7` | Gelb | `Q4` | GPIO21 (23) | `R23`, 4,7 kΩ | `R13`, 220 Ω |
| `D9` | Rot | `Q3` | GPIO38 (31) | `R24`, 4,7 kΩ | `R15`, 220 Ω |
| `D10` | Grün | `Q2` | GPIO47 (24) | `R25`, 4,7 kΩ | `R16`, 220 Ω |
| `D8` | Blau | `Q1` | GPIO48 (25) | `R26`, 4,7 kΩ | `R14`, 220 Ω |

Transistoren: **BC337-40** (NPN, TO-92, Pinbelegung 1=C, 2=B, 3=E), bestellt
als onsemi **`BC33740BU`** mit **geraden** Anschlussbeinen. Der Footprint
`TO-92_Inline` hat 1,27 mm Raster; die Gurt-Variante `BC33740TA` hat auf
2,54 mm aufgebogene Beine und passt nicht (so bis 2026-09-24 in der
Stückliste, beim Footprint-Abgleich aufgefallen).

**Symbol und Polarität (SHBS-16, 2026-09-23):** Alle vier LEDs nutzen
`Device:LED` (Pin 1 = Kathode, Pin 2 = Anode). Die beiden Würth-Footprints
`WL-TMRC_3MM` (D7, D10) und `WL-TMRW_3MM` (D8, D9) sind gleich nummeriert:
Pad 1 = Kathode (abgeflachte Seite), Pad 2 = Anode (`+` im Bestückungsdruck).
Das war nicht immer so — `WL-TMRC_3MM` kam vom Hersteller mit vertauschter
Nummerierung (Pad 1 = Anode). Zusammen mit `Device:LED` war **D10 dadurch
verpolt** und hätte nie geleuchtet; D7 war nur deshalb richtig, weil es das
Würth-eigene Symbol nutzte. Der Footprint ist jetzt umnummeriert, das
Würth-Symbol `WL-TMRC_3MM` entsprechend mitgezogen. **Beim nächsten
PCB-Abgleich** den Footprint von D7/D10 aus der Bibliothek aktualisieren — die
Platinendatei enthält noch die alte Nummerierung.

**Dimensionierung:** Der Vorwiderstand stellt bei ca. 2 V Flussspannung rund 5 mA LED-Strom ein. Der Basiswiderstand begrenzt den Basisstrom auf ca. 0,55 mA — ausreichend für sichere Sättigung und unkritisch für den GPIO-Treiber. Ohne diesen Widerstand wirkt die Basis-Emitter-Strecke als Diode gegen GND und der Pin-Strom wäre nur durch die Treiberimpedanz begrenzt.

**Pinwahl:** Bewusst auf GPIOs **ohne** Strapping-, ADC- oder Touch-Funktion gelegt. Die Strapping-Pins GPIO3, GPIO45 und GPIO46 waren zuvor belegt und sind jetzt frei — ein an der Basis hängender Pegel hätte beim Reset die Boot-Konfiguration beeinflussen können (GPIO45 = VDD_SPI-Spannung, GPIO46 = ROM-Log, GPIO3 = JTAG-Quellenwahl). GPIO3 bleibt auch nach dem Wegfall von `J5` unbelegt: Das Strapping wählt zwischen internem USB-Serial-JTAG und externen JTAG-Pins und darf beim Reset nicht verzogen werden.

**Nicht verwenden:** GPIO35, GPIO36 und GPIO37 erscheinen in der Netzliste als frei, sind beim Modul **N16R8** aber intern vom Octal-PSRAM belegt.

Schaltplan: `pcb/BasisStation/BasisStation_Layout.kicad_sch`.

## Ethernet (SHBS-5)

Kabelgebundene Netzwerkanbindung über **WIZnet W5500** am SPI-Bus, RJ45-Buchse
**Würth 7499011121A** mit integrierten Magnetics. Schaltplanblatt
`pcb/BasisStation/ethernet.kicad_sch`.

**Warum SPI und nicht RMII:** Der ESP32-S3 besitzt — anders als der
ursprüngliche ESP32 — keine EMAC-Peripherie. Ein RMII-PHY findet im SoC keine
Gegenstelle. Der W5500 bringt MAC und PHY selbst mit und hängt am SPI-Bus.

| Netz | W5500-Pin | GPIO | Modul-Pad |
|------|-----------|------|-----------|
| `ETH_RST` | 37 `RSTn` | 9 | 17 |
| `ETH_SCSn` | 32 `SCSn` | 10 | 18 |
| `ETH_MOSI` | 35 `MOSI` | 11 | 19 |
| `ETH_SCLK` | 33 `SCLK` | 12 | 20 |
| `ETH_MISO` | 34 `MISO` | 13 | 21 |
| `ETH_INT` | 36 `INTn` | 14 | 22 |

Gewählt wurden die nativen **FSPI-Pins** (IO-MUX statt GPIO-Matrix), die am
Modul zudem auf den zusammenhängenden Pads 17–22 liegen. Dadurch belegt sind
ADC1_CH8 und ADC1_CH9; **GPIO1–GPIO8 bleiben frei** für analoge Sensorik.

Die Versorgung ist in `+3V3` (digital) und `+3V3A` (analog) getrennt,
verbunden über eine Ferritperle.

Architektur, Bauteilliste, Beschaltung und Begründungen: **[ethernet.md](ethernet.md)**.

## Repository-Ist-Stand (KiCad)

| Bereich | Pfad / Artefakt |
|--------|------------------|
| Hauptprojekt | `pcb/BasisStation/BasisStation.kicad_pro` |
| Schaltpläne | `BasisStation.kicad_sch` (Root) mit den Unterblättern `BasisStation_Layout.kicad_sch`, `BasisStation_Debugging.kicad_sch`, `Stromversorgung.kicad_sch`, `ethernet.kicad_sch` |
| Leiterplatte | `BasisStation.kicad_pcb` |
| Bauteilbibliotheken | `pcb/Bauteile/<Bauteil>/` — **ein Ordner je Bauteil** mit Symbol, Footprint und 3D-Modell (SHBS-12) |
| Mechanische BOM-Teile | `pcb/Bauteile/Mechanical/mechanical.kicad_sym` (ANT1, ANT2) |
| Power (USB-C, Buck) | `pcb/Bauteile/Power/` (J_PWR, PS1) |
| Ethernet | `pcb/Bauteile/W5500/`, `pcb/Bauteile/wuerth_7499011121A/`, `pcb/Bauteile/wuerth_830059532/` (SHBS-5) |
| ERC-Bericht | `pcb/BasisStation/ERC.rpt` (Stand 18.09.2026 nach SHBS-5: **0 Fehler, 7 Warnungen**) |
| Architektur-Diagramm | Als Textdiagramm in [architecture.md](architecture.md) — das frühere drawio-Diagramm wurde gestrichen, weil es in drei Dateien gepflegt werden musste und auseinandergelaufen war |

## Abgrenzung Firmware

Die Firmware in `main/` beschreibt das **Laufzeitverhalten** (WLAN, Webserver, LEDs). Ethernet ist **schaltplanseitig fertig** (SHBS-5); das **PCB-Layout** steht als **SHBS-10** aus, die **Firmware-Anbindung** über `esp_eth` als **SHBS-11**. In der aktuellen Firmware gibt es keine Ethernet-Nutzung. Hintergrund: [ethernet.md](ethernet.md).

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
5. Symbol im **aktuellen KiCad-Dateiformat** ablegen (siehe unten).

### Dateiformat der Symbolbibliotheken (SHBS-14)

Alle `.kicad_sym` im Projekt liegen im KiCad-9-Format (`version 20241209`).

Das ist keine Kosmetik: Liegt eine Bibliothek in einem älteren Format vor,
während der Symbol-Cache im Schaltplan schon KiCad 9 ist, meldet die ERC für
jedes betroffene Bauteil `lib_symbol_mismatch` — auch wenn Pins und Geometrie
identisch sind. Die Warnungen verdecken dann echte Befunde.

Von Herstellern oder SnapEDA bezogene Symbole kommen häufig im Format
`20211014` (KiCad 6) oder `20220914` (KiCad 7). Vor dem Einchecken umwandeln:

```
kicad-cli sym upgrade --force pcb/Bauteile/<Bauteil>/<Datei>.kicad_sym
```

Der Befehl ändert ausschliesslich die Syntax — Pins, Pinnummern, Pintypen und
Geometrie bleiben unangetastet. Bei der Umstellung der sechs Altbestände
(SHBS-14) wurden Netzliste und Stückliste vorher und nachher verglichen und
waren bitweise identisch.

**Nicht ausreichend:** Der Upgrade der Bibliothek allein räumt eine bereits
bestehende `lib_symbol_mismatch`-Warnung nicht ab. Der Symbol-Cache im
Schaltplan muss zusätzlich über *Werkzeuge > Symbole aus Bibliothek
aktualisieren* in der GUI aufgefrischt werden — dafür gibt es keinen
CLI-Befehl. Dabei darf das Footprint-Feld **nicht** zurückgesetzt werden,
sonst gehen die instanzweise gesetzten Footprint-Zuweisungen verloren.

Nicht umgestellt sind zwei Archivdateien, die in keiner `sym-lib-table`
registriert sind und nirgends verwendet werden:
`pcb/Bauteile/W5500/KiCADv6/2026-09-17_19-45-49.kicad_sym` und
`pcb/Bauteile/wuerth_7499011121A/WE-RJ45_7499011121A.kicad_sym`.

## ERC: hinterlegte Ausnahmen und Entwurfsregeln (SHBS-14)

Der Schaltplan ist so gebaut, dass `kicad-cli sch erc` **0 Fehler und
0 Warnungen** meldet. Nur so fällt ein neuer Befund sofort auf.

### Prüfe immer beide Werkzeuge

GUI und CLI können auseinanderlaufen. Am 22.09.2026 meldete die GUI 0
Verstöße, während das CLI noch eine Warnung führte — die GUI hatte schlicht
eine andere Instanz derselben Warnung erzeugt als das CLI. Ein grünes
Ergebnis aus nur einem der beiden Werkzeuge ist kein Nachweis.

Alle Verstöße einschließlich der ausgeschlossenen sichtbar machen:

```
kicad-cli sch erc --severity-all --format json -o erc.json BasisStation.kicad_sch
```

### Einzige hinterlegte Ausnahme

`pin_to_pin` an `S2` Pin 1 (Bidirectional) gegen `#FLG04` (Power output).
Das ist das GND-`PWR_FLAG`. Mit dem Wechsel von `Connector:USB_B_Micro` auf
`Connector:USB_C_Receptacle_USB2.0_16P` (SHBS-6) entfiel der einzige
ERC-Treiber des globalen GND-Netzes — das alte Steckersymbol deklarierte
seinen GND-Pin als *Power output*, das neue als `power_in`. `#FLG04` stellt
den Treiber wieder her; das ist der KiCad-Standardweg.

### Keine versteckten Power-Pins mit abweichendem Namen

Ein **versteckter** `power_in`-Pin verbindet sich in KiCad implizit mit einem
globalen Netz, das nach dem **Pinnamen** heißt. Ist derselbe Pin zusätzlich
explizit verdrahtet, kollidieren zwei Netznamen → `multiple_net_names`.

Aufgetreten an `U6` Pin 41, das Exposed Pad des ESP32-S3-WROOM-Moduls: Der
Pin hieß `EPAD` und war zugleich auf GND verdrahtet. Erschwerend erzeugte
KiCad **mehrere Instanzen** dieser Warnung, die den Pin je nach
Durchlaufreihenfolge mit unterschiedlichen GND-Power-Symbolen paarten —
ein Ausschluss per UUID hätte also nie dauerhaft getragen.

Behoben durch Umbenennung des Pins auf `GND` in
`pcb/Bauteile/ESP32-S3-WROOM-1U-N16R8/`. Das implizite Netz heißt seitdem
`GND` und deckt sich mit der Verdrahtung. Die Pin**nummer** 41 ist
unverändert, die Zuordnung zum Footprint-Pad also ebenfalls. Dass Pin 41 das
Exposed Pad ist, steht jetzt in der Symbolbeschreibung.

**Regel für neue Symbole:** Versteckte Power-Pins tragen den Namen des Netzes,
auf dem sie tatsächlich liegen. Ein abweichender, sprechender Name gehört in
die Symbolbeschreibung, nicht in den Pinnamen.

## KiCad-CLI im Dev-Container (SHBS-13)

`kicad-cli` ist das Kommandozeilen-Binary von KiCad. Es erzeugt ERC-, DRC-,
Netzlisten- und BOM-Ausgaben ohne GUI und macht damit prüfbar, ob eine
Schaltplan-Änderung tatsächlich fehlerfrei ist — vorher mussten diese
Artefakte manuell in der KiCad-GUI erzeugt und eingecheckt werden.

Installation und Versionsbindung stehen im [Dockerfile](../../.devcontainer/Dockerfile).
Zwei Punkte sind dort entscheidend:

- **KiCad 9 ist Pflicht.** Die Projektdateien tragen das Format
  `version 20250114`. Ubuntu 24.04 liefert nur KiCad 8, deshalb das PPA
  `kicad/kicad-9.0-releases`.
- **`kicad-packages3d` bleibt draußen.** Das Paket wiegt 3,2 GB und wird nur
  für STEP-/VRML-Export gebraucht. Symbole und Footprints sind installiert,
  weil ERC, Netzliste und BOM sie zum Auflösen der Bibliotheken benötigen.
- **Globale Bibliothekstabellen werden vorbelegt.** `kicad-cli` legt beim
  ersten Aufruf nur `fp-lib-table` selbst an, nicht `sym-lib-table`. Ohne diese
  Datei gelten sämtliche Standardbibliotheken (`power`, `Device`, …) als
  unbekannt und der ERC-Report füllt sich mit `lib_symbol_issues`. Das
  Dockerfile kopiert deshalb beide Vorlagen aus `/usr/share/kicad/template/`
  nach `~/.config/kicad/9.0/`.

Typische Aufrufe gegen `pcb/BasisStation/`:

| Zweck | Befehl |
|-------|--------|
| ERC prüfen | `kicad-cli sch erc --output ERC.rpt BasisStation.kicad_sch` |
| Netzliste | `kicad-cli sch export netlist --output BasisStation.net BasisStation.kicad_sch` |
| Stückliste | siehe unten (`sch export bom` mit Feldliste) |
| DRC prüfen | `kicad-cli pcb drc --output DRC.rpt BasisStation.kicad_pcb` |

Die Stückliste muss die GUI-Voreinstellungen explizit mitbekommen, sonst
weichen Spalten und Gruppierung von der eingecheckten `BasisStation.csv` ab:

```
kicad-cli sch export bom \
  --fields 'Reference,Value,Datasheet,Footprint,${QUANTITY},${DNP}' \
  --labels 'Reference,Value,Datasheet,Footprint,Qty,DNP' \
  --group-by 'Value,Footprint' --ref-range-delimiter '' \
  --output BasisStation.csv BasisStation.kicad_sch
```

Einziger verbleibender Unterschied zur GUI-Ausgabe ist die DNP-Spalte: die
deutschsprachige GUI schreibt dort `Nicht bestücken`, die CLI `DNP`.

### Bestellfähige Stückliste (`tmp/bom/`)

Für den Abgleich gegen den Schaltplan reicht der CLI-Export oben. Für eine
**bestellfähige** Stückliste reicht er nicht, aus einem Grund: Teilenummern
liegen in diesem Projekt unter uneinheitlichen Feldnamen, je nachdem woher ein
Symbol stammt (SnapEDA, Würth-Generator, handgepflegt). Dieselbe Information
heißt mal `Manufacturer_Part_Number`, mal `MP`, mal `Part Number`;
Mouser-Nummern mal `Mouser Part Number`, mal `MOUSER_PART_NUMBER`.
`--fields` nimmt aber nur einen festen Namen und liefert für die übrigen
still eine leere Spalte — der erste Export blieb deshalb ohne Teilenummern.

[`tmp/bom/generate_bom.py`](../../tmp/bom/generate_bom.py) liest die
Schaltplanblätter daher direkt (eigener S-Expression-Parser in
[`sexp.py`](../../tmp/bom/sexp.py)), löst die Feld-Aliase auf, fragt Preis,
Lagerbestand und Lebenszyklus **bei Mouser und DigiKey** ab
([`digikey.py`](../../tmp/bom/digikey.py), Product Information V4, 2-legged
OAuth) und schreibt die Mappe über
[`write_xlsx.py`](../../tmp/bom/write_xlsx.py). Zugangsdaten:
`secrets/mouser_api_key` und `secrets/digikey_api.json`.

```
python3 tmp/bom/generate_bom.py            # mit API-Abfrage
python3 tmp/bom/generate_bom.py --no-network   # nur aus dem lokalen Cache
```

Zwei Entwurfsentscheidungen, die beim Lesen sonst überraschen:

- **Gruppiert wird nach Herstellerteilenummer, nur ohne Nummer nach Wert +
  Footprint — nie nach `lib_id`.** `J1` und `J_PWR1` nutzen verschiedene
  Symbole für dieselbe Amphenol-Buchse; für eine Bestellung ist das eine
  Position mit Menge 2. Die Teilenummer hat Vorrang, weil Werte über die
  Blätter uneinheitlich geschrieben sind (`100 nF` / `100nF`, `10uF` / `10 µF`).
- **Antworten werden in `tmp/bom/mouser_cache.json` und
  `tmp/bom/digikey_cache.json` zwischengespeichert.** Das schont die
  Tageskontingente und macht Läufe ohne Netz reproduzierbar. `--refresh`
  verwirft die Caches.
- **Gerechnet wird mit dem günstigsten lieferbaren Angebot (SHBS-17).** Die
  Spalte „Bezugsquelle“ steht auf dem Anbieter mit dem niedrigeren Preis, der
  die Menge ab Lager liefern kann; bei Gleichstand auf DigiKey. Sie ist per
  Auswahlliste änderbar; Einzelpreis, Gesamtpreis und die Teilsummen je
  Anbieter rechnen sich daraus. Wer alles über einen Anbieter bestellen will,
  um Versandkosten zu sparen, stellt die Spalte entsprechend um. Dauerhafte Festlegungen, die
  die Preisregel übersteuern, stehen mit Begründung in `SOURCE_OVERRIDES` in
  `generate_bom.py` und erscheinen in der Hinweisspalte — derzeit `U6` →
  Mouser (DigiKey mit nur zweistelligem Lager, Mouser mehrere Tausend;
  Bediener 2026-09-24).
- **Beide Anbieter werden zweistufig abgefragt:** erst die exakte Nummer, dann
  eine Stichwortsuche, die Verpackungssuffixe (`D3V3XA4B10LP` → `-7`) und
  herstellerneutrale Typen (`SS34`) auflöst. Nennt der Schaltplan einen
  Hersteller, bevorzugt die DigiKey-Suche dessen Treffer — sonst landet bei
  Typen wie `SMAJ5.0A`, die ein Dutzend Hersteller fertigen, der billigste
  Doppelgänger in der Bestellung. Verpackungen, deren
  Mindestbestellmenge über der Stückzahl liegt (Rollen), zählen nicht als
  Angebot.
- **Teilevorschläge stehen im Skript, bis sie freigegeben sind.** Für
  Positionen, die im Schaltplan nur einen Wert oder ein abgekündigtes Teil
  tragen, kann `PROPOSED_PARTS` in `generate_bom.py` einen Vorschlag halten;
  die Mappe markiert ihn mit Status „Vorschlag“. Nach Freigabe wandern die
  Teile als Felder `Manufacturer`, `Manufacturer_Part_Number` und
  `Mouser Part Number` in den Schaltplan, und der Eintrag im Skript entfällt
  — der Schaltplan bleibt die maßgebliche Quelle. Die Liste ist seit
  2026-09-23 leer: alle 29 Vorschläge aus SHBS-17 sind übernommen.
- **Hausstandard für Passivteile (SHBS-17, freigegeben 2026-09-23):**
  Widerstände Dickschicht 0805, 1 %, 0,125 W; Kondensatoren bis 100 nF X7R
  50 V, ab 1 µF X5R/X7R 16–25 V; C0G für die Quarz-Lastkondensatoren
  `C25`/`C26` (27 pF, gegen C<sub>L</sub> = 18 pF von `Y1` nachgerechnet);
  `C28` 1 nF/2 kV in 1206 für den Ethernet-Schirmabschluss.

Gefundene Abweichungen überschreiben die Schaltplan-Felder **nicht**, sondern
landen als Befund im Blatt „Offene Punkte“ — eine veraltete Teilenummer gehört
im Schaltplan korrigiert, nicht bei jedem Export stillschweigend übertüncht.

Schlägt ein Export mit einem Display-Fehler fehl, hilft `xvfb-run kicad-cli …`
— einzelne Unterbefehle erwarten je nach Version noch einen X-Server.

### Stand der Verifikation

Gegen die eingecheckten Artefakte geprüft (2026-09-19):

| Artefakt | Ergebnis |
|----------|----------|
| ERC | deckungsgleich — 7 Verstöße, 0 Fehler, 7 Warnungen |
| Netzliste | deckungsgleich — 102 Netze, identische Namen |
| Stückliste | deckungsgleich bis auf die DNP-Beschriftung (Sprache) |
| DRC | **abweichend** — CLI meldet 418 Verstöße gegen 8 im eingecheckten Report |

Die DRC-Abweichung betrifft ausschließlich Konflikte mit den beiden
GND-Zonen (`clearance`, `solder_mask_bridge`, `hole_clearance`). Naheliegende
Ursache: die GUI füllt Zonen vor dem DRC neu, `kicad-cli` rechnet mit dem im
Board gespeicherten — inzwischen veralteten — Füllstand. Bis das geklärt ist,
bleibt der DRC in der GUI die verbindliche Quelle; die CLI wird für ERC,
Netzliste und Stückliste genutzt.

Nach einem Update des Dockerfiles muss der Container neu gebaut werden
(*Rebuild Container*), sonst fehlt das Binary weiterhin.

## Pflege

Änderungen an Schaltplan, BOM oder Schnittstellen hier und in [communication.md](communication.md) nachziehen.
