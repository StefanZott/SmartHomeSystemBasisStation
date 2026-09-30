---
status: active
last_updated: 2026-09-30
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

**Layout (SHBS-22, 2026-09-27):**

- **U1 als Durchgangs-Bauteil:** Jede Leitung läuft gerade unter dem
  Gehäuse durch, von Pad 10→1 (USB−), 9→2 (USB+) und 7→4 (VBUS_J1). Neben
  den breiten GND-Pads 3/8 sind die Durchgänge für USB+ und VBUS_J1 nur
  0,15 mm breit. Der Footprint selbst hat nur 0,15 mm Padabstand; die
  5 DRC-Meldungen dazu sind footprint-bedingt und werden ausgeschlossen.
- **Brücken im Pad-Feld von J1:** D+ B6→A6 auf F.Cu. D− B7→A7 kreuzt D+
  geometrisch und läuft daher über ein Via oberhalb der B-Reihe
  (89,5 / 33,8) auf B.Cu zum USB−-Via (88,5 / 38,0). VBUS_J1: B4→A9 und
  B9→A4. Die Gruppe A4/B9 ist von CC1 eingeschlossen und geht über ein Via
  (90,85 / 37,6) auf B.Cu zu einem Via unter U1-Pin 4 (87,8 / 44,0).
- USB D+/D− haben je 4 Vias und ca. 77 mm Länge bis U6. Für USB
  Full-Speed (12 Mbit/s) ist das unkritisch.

## Stromversorgung (SHBS-4)

Primäre Versorgung: **USB-C 5 V → AP3211 Buck → 3,3 V** (bis SHBS-17: MP2359, abgekündigt). PS2/+12V entfernt.

Ausführliche Dokumentation (Schaltplan, BOM, Pinbelegung, Verdrahtung): **[power_supply.md](power_supply.md)**.

**Layout-Stand (2026-09-26, SHBS-21):** Buck-Wandler kompakt um PS1 platziert, +3V3 zu U6 und zu den LED-Anoden geroutet. Details und Begründung der Leitungsführung: [power_supply.md](power_supply.md), Abschnitt „Platzierung Buck-Wandler“.

## Status-LEDs (SHBS-9)

Vier Status-LEDs, **direkt vom GPIO getrieben**: GPIO → Vorwiderstand →
LED-Anode, Kathoden gemeinsam auf GND. Ein GPIO auf **High** schaltet die
zugehörige LED **ein**.

| LED | Farbe | GPIO (Modul-Pad) | Vorwiderstand (0805) |
|-----|-------|------------------|----------------------|
| `D7` | Gelb | GPIO21 (23) | `R13`, 220 Ω |
| `D9` | Rot | GPIO38 (31) | `R15`, 220 Ω |
| `D10` | Grün | GPIO47 (24) | `R16`, 220 Ω |
| `D8` | Blau | GPIO48 (25) | `R14`, 100 Ω |

**Warum ohne Transistoren (SHBS-40, 2026-09-30):** Bis dahin schaltete je
ein NPN-Transistor BC337 (Q1–Q4, Basiswiderstände R23–R26) die LED gegen
GND, Vor- und Basiswiderstände waren 2-W-THT-Typen (DIN0617, 17 mm). Ein
Hardware-Review hat beides als überdimensioniert bewertet. Ein GPIO des
ESP32-S3 liefert bei der Standard-Treiberstufe rund 20 mA, bei der höchsten
rund 40 mA. Eine LED braucht hier etwa 5 mA, alle vier zusammen 20 mA. Der
Treiber entfällt damit ersatzlos; an den Widerständen fallen nur einige mW
ab, 0805 reicht mit großer Reserve.

**Symbol und Polarität (SHBS-16, 2026-09-23):** Alle vier LEDs nutzen
`Device:LED` (Pin 1 = Kathode, Pin 2 = Anode). Die beiden Würth-Footprints
`WL-TMRC_3MM` (D7, D10) und `WL-TMRW_3MM` (D8, D9) sind gleich nummeriert:
Pad 1 = Kathode (abgeflachte Seite), Pad 2 = Anode (`+` im Bestückungsdruck).
Das war nicht immer so — `WL-TMRC_3MM` kam vom Hersteller mit vertauschter
Nummerierung (Pad 1 = Anode). Zusammen mit `Device:LED` war **D10 dadurch
verpolt** und hätte nie geleuchtet; D7 war nur deshalb richtig, weil es das
Würth-eigene Symbol nutzte. Der Footprint ist jetzt umnummeriert, das
Würth-Symbol `WL-TMRC_3MM` entsprechend mitgezogen. Die Platine nutzt die
korrigierte Nummerierung (beim PCB-Abgleich SHBS-42 geprüft).

**Dimensionierung:** Am GPIO liegen bei High und rund 5 mA Last etwa 3,2 V.
Rot, Gelb und Grün haben ca. 2,0–2,2 V Flussspannung, 220 Ω ergeben rund
5 mA. Die blaue LED `151033BS03000` hat typ. 2,8 V (max. 3,6 V). Mit 220 Ω
blieben nur etwa 1–2 mA, sie leuchtete kaum (das galt schon mit Transistor
an +3V3). Mit 100 Ω fließen typ. 3–5 mA. Die blaue LED ist mit 3,8 cd
trotzdem deutlich heller als die anderen. Helligkeit per PWM (LEDC) in der
Firmware angleichen. Liegt ein Exemplar nahe an der maximalen
Flussspannung, bleibt es dunkel. Am Prototyp prüfen.

**Pinwahl:** Bewusst auf GPIOs **ohne** Strapping-, ADC- oder Touch-Funktion gelegt. Die Strapping-Pins GPIO3, GPIO45 und GPIO46 waren zuvor belegt und sind jetzt frei — ein an der LED hängender Pegel hätte beim Reset die Boot-Konfiguration beeinflussen können (GPIO45 = VDD_SPI-Spannung, GPIO46 = ROM-Log, GPIO3 = JTAG-Quellenwahl). GPIO3 bleibt auch nach dem Wegfall von `J5` unbelegt: Das Strapping wählt zwischen internem USB-Serial-JTAG und externen JTAG-Pins und darf beim Reset nicht verzogen werden.

**Nicht verwenden:** GPIO35, GPIO36 und GPIO37 erscheinen in der Netzliste als frei, sind beim Modul **N16R8** aber intern vom Octal-PSRAM belegt.

**Firmware:** Die Pinzuordnung in `main/LED.h` entspricht noch der alten
Belegung (GPIO46/3/45/21) und muss nachgezogen werden. Die Logik (High = an)
bleibt gleich.

**Liegende Montage (SHBS-42, 2026-09-30):** Die LEDs schauen durch die
Gehäusewand an der Unterkante heraus. Dazu werden die Beine um 90° gebogen,
die LED liegt parallel zur Platine. Footprint:
`LED_THT:LED_D3.0mm_Horizontal_O1.27mm_Z2.0mm` aus der KiCad-Bibliothek, mit
3D-Modell.

| Maß | Wert |
|-----|------|
| Biegung | 1,27 mm hinter der Pad-Reihe (Abstand Pad – Kragen) |
| LED-Mitte über Platine | 2,0 mm |
| Pad-Reihe | y 155,43, Kathode (Pad 1, eckig) links |
| Linsenspitze | y 162,0 = 2,0 mm vor der Kante, bündig mit der Außenseite der 2 mm dicken Wand |
| Lichtaustritt (x) | 112,0 / 123,73 / 134,73 / 144,73 (unverändert) |
| Gehäusebohrung | je LED ca. 3,2 mm, Mitte 2,0 mm über der Platinenoberseite |

Die Würth-LEDs bleiben, nur die Beine werden gebogen. Die Maße gehen von
der üblichen Bauform aus (5,3 mm vom Kragen bis zur Linsenspitze). Am
Muster prüfen und die Pad-Reihe notfalls verschieben.

Schaltplan: `pcb/BasisStation/BasisStation_Layout.kicad_sch`. Layout: die
Vorwiderstände (0805) sitzen direkt über der jeweiligen LED-Anode, die
Kathoden hängen an der GND-Fläche (SHBS-42).

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

## Gesamt-Layout (SHBS-23, SHBS-10, SHBS-42 — Stand 2026-09-30)

Platine **160 × 132,55 mm** (Kontur x 50–210, y 27,45–160), 2 Lagen, 1,6 mm.
Fest vorgegeben waren T1, J1, J_PWR1 und D7–D10.

**Buchsen-Überstand für das Gehäuse:** Die obere Kante liegt so, dass
J_PWR1, J1 (Front bei y 26,22) und T1 (26,14) **1,2–1,3 mm über die
Platinenkante** hinausragen. Mehr lassen die USB-C-Buchsen nicht zu: Ihre
vorderen Befestigungslaschen (S1, Kupfer ab y 27,96) brauchen 0,5 mm
Randabstand. Mit 0,3 mm Randabstand (übliches Fertigungsminimum) wären
1,44 mm möglich, dafür müsste die Projektregel gelockert werden. Die
RJ45-Buchse allein könnte bis etwa 5,5 mm überstehen, bräuchte dafür aber
eine Stufe in der Kontur. Die Montagelöcher H1/H2 sind mit der Kante um
2,45 mm nach unten gewandert. Der Silkscreen-Umriss von T1 läuft über die
Kante und wird bei der Fertigung abgeschnitten.

| Bereich | Lage | Begründung |
|---------|------|------------|
| **U6** (ESP32-S3) | rechts oben, U.FL zur Ecke | Kurzer Pigtail zur Gehäuseantenne, weg von USB und Ethernet |
| **U7** (W5500) | rechts neben T1 | TX/RX-Pins zeigen zu T1, SPI und Quarz zu U6 |
| Y1, C25/C26 | rechts an U7 | Kurze XI/XO-Leitungen |
| Abblock-C, FB1 | unter U7 | Zwei Reihen, Spalten 4 mm, Reihen 5,5 mm (Handlötung), TOCAP/1V2O am nächsten an den Pins |
| Pull-ups R28–R32 | Reihe über U7 | Raster 4 mm |
| S2 | obere Kante zwischen T1 und U6, liegend | Reset von außen durch die Gehäusewand (SHBS-25, siehe unten) |
| R9 | links neben C7, Mitte rechts | Pull-up EN, seit SHBS-42 0805 statt THT |
| J6 | rechter Rand, untere Hälfte (203 / 110) | Programmierstecker, von außen gut erreichbar; Leitungen zu U6 auf B.Cu |
| C8 | direkt an U6 | Lokaler Puffer am 3V3-Pin des Moduls, bleibt deshalb oben |
| C10, C12 | Mitte rechts (184 / 84 und 97) | Puffer für +3V3, entlang der +3V3-Hauptleitung zum Wandler |
| C7 (EN-Kondensator) | Mitte rechts (160 / 97) | RC-Glied mit R9, zeitunkritisch |
| Buck-Wandler | linke Hälfte (PS1 bei 68 / 87,5) | Weg von den Buchsen, siehe [power_supply.md](power_supply.md) |
| R13–R16 | direkt über der LED-Anode | Vorwiderstände, seit SHBS-42 ohne Transistorstufe |
| D7–D10 | Unterkante, liegend | Schauen durch die Gehäusewand, siehe „Status-LEDs“ |

**Ethernet-Paare:** TX± und RX± sind von Hand geroutet und gesperrt. RX
verlässt T1 durch den Kanal zwischen den beiden Pad-Reihen, die
Koppel-Kondensatoren C30/C29 sitzen versetzt hintereinander. So kreuzen sich
die Paare nicht. Länge unter 20 mm. **Keine definierte Impedanz:** 100 Ω
differenziell ist auf 2 Lagen mit 1,6 mm Dielektrikum nicht einstellbar. Bei
diesen kurzen Wegen ist das für 100BASE-TX unkritisch, bei Problemen am
Prototyp wäre ein 4-Lagen-Aufbau die Abhilfe. Der Abschluss R36 (TD+) ist
über ein Via-Paar angebunden, weil TD− darüber liegt.

**Chassis-Fläche:** Zone `CHASSIS_RJ45` (beide Lagen, Priorität 5) unter der
Buchsenfront, x 104–130 / y 25,5–41,5. GND-Flächen halten 0,5 mm Abstand.
Die Kopplung erfolgt nur über R35 ‖ C28 links unter T1.

**Routing:** Die übrigen Netze hat Freerouting 2.4.1 geroutet, vorhandene
Leitungen waren gesperrt. Ein zweiter Durchgang (alles andere gesperrt)
hat USB− ergänzt. RXN → R40 ist von Hand über ein Via-Paar auf B.Cu
angebunden, weil R40.1 auf F.Cu von RCT eingeschlossen ist. Isolierte GND-Pads und Flächeninseln (vor allem die
inneren GND-Pins des W5500) sind über kurze Stiche auf GND-Vias zur
durchgehenden Rückseitenmasse angebunden. Unter U7 verbindet eine
Sammelleitung die +3V3A-Pins. DRC: **keine offenen Verbindungen**, keine
Abstandsfehler außer den footprint-bedingten an U1/J1.

**Verteilung (SHBS-42, 2026-09-30):** Nach einem Hardware-Review war die
Bestückung zu gedrängt: Fast alles saß in der oberen Hälfte, 22
Bauteilpaare lagen enger als 1 mm, mehrere berührten sich. Jetzt:

- Die Blöcke sind über die Platine verteilt. Der Buck-Wandler sitzt in der
  linken Hälfte, C7/C10/C12, R9 und J6 in der rechten Hälfte darunter.
- Oben bleibt nur, was an Buchsen oder ICs gebunden ist: T1, J1, J_PWR1, S2,
  U6 mit C8, U7 mit Abblock-Cs, Quarz und Pull-ups.
- Zwischen den Bestückungsflächen sind überall mindestens 1 mm frei, meist
  1,5 mm und mehr. Die einzige Ausnahme außerhalb der MDI-Gruppe ist C16 an
  Y1 (1,03 mm): Er ist Abblock-C am W5500 und bleibt am Pin.
- Transistorstufe der LEDs entfallen, R9 und R13–R16 als 0805.

**Bewusst unverändert:** die Ethernet-MDI-Gruppe an T1 (R35–R40, C28–C30).
Dort liegen die von Hand gerouteten, gesperrten Paare. R36/R37 (0,2 mm) und
C29/C30 (0,45 mm) bleiben enger als 1 mm. Ein Verschieben hätte die
Paarführung aufgebrochen.

**Neu-Routing:** Die getrennten Netze (u. a. +3V3, +5V, SW, LED, EN, Quarz,
SPI zum W5500) hat Freerouting 2.4.1 neu geroutet. Die übrigen Leitungen des
alten Stands blieben erhalten, weil sie an unveränderten Bauteilen hängen.
Die GND-Stiche an U7 und J1/U1 sowie die +3V3A-Sammelleitung unter U7 sind
aus dem alten Stand übernommen. Unter U7 schloss die +3V3-Hauptleitung auf
B.Cu zusammen mit der XO-Leitung eine GND-Insel ein, in der Pin 29 und C16
hingen. Die Hauptleitung läuft deshalb dort auf y 53, das +3V3-Via für C16
und Pin 28 sitzt direkt unter C16. Pin 29 geht auf F.Cu an C16.2. Freerouting läuft im Dev-Container ohne
Installation: JRE 25 und das JAR in einem temporären Verzeichnis. Beim
Einlesen der SES-Datei ersetzt KiCad **alle** Leiterbahnen und verliert dabei
Handrouten. Deshalb wurden nur die neuen Leiterbahnen übernommen.

Montagelöcher heißen im PCB **H1–H4** (vorher alle `REF**`). Der
Specctra-Export braucht eindeutige Referenzen. Sie sind als
„nur Platine" markiert (kein Schaltplan-Symbol nötig).

### DRC: Regeln und Ausschlüsse (Stand 2026-09-30)

`kicad-cli pcb drc --schematic-parity`: **0 offene Verbindungen, 0
Schaltplan-Abweichungen, 0 offene Fehler.** Übrig sind 17 bewusst
ausgeschlossene Meldungen. Die Begründung steht jeweils als Kommentar in
`BasisStation.kicad_pro`:

| Meldung | Anzahl | Grund |
|---------|-------:|-------|
| `copper_edge_clearance` J_PWR1, J1 | 4 | Hersteller-Landepattern Amphenol: A12/S1 liegen 0,30 mm am ovalen NPTH, KiCad behandelt NPTH als Kante |
| `starved_thermal` J1, J_PWR1 | 3 | Pad hat nur einen Thermal-Steg, ist aber zusätzlich per Leiterbahn oder Via an GND angebunden. Sechs weitere Ausschlüsse sind mit SHBS-42 entfallen, weil die Bauteile verschoben oder anders angebunden sind |
| `silk_edge_clearance` T1 | 2 | Silkscreen-Umriss ragt mit der Buchse über die Kante, wird bei der Fertigung abgeschnitten |
| `silk_edge_clearance` D7–D10 | 8 | Liegende LEDs ragen mit der Linse 2 mm über die Kante in die Gehäusewand, die Kontur wird abgeschnitten |

**Regeln statt Ausschluss:** Die Thermal-Stege an S2 siehe „Reset-Taster S2". Die fünf Padabstände von 0,15 mm am ESD-Array U1
sind eine Eigenschaft seines Landepatterns. `BasisStation.kicad_dru` erlaubt
sie ausschließlich innerhalb von U1.

**Hinweis für Skripte:** Ausschlüsse greifen nur bei exakter Marker-Position.
Diese liegt nicht immer auf einer Pad-Position, bei `starved_thermal` aber
schon.

### Reset-Taster S2 von außen (SHBS-25, 2026-09-29)

S2 (EN, Reset) ist ein **liegender Taster C&K PTS645VL58-2 LFS** an der oberen
Kante, auf derselben Seite wie USB-C und RJ45. Sein Stößel zeigt zur Kante und
wird **bündig mit der Gehäuseaußenseite** gedrückt.

| Maß | Wert |
|-----|------|
| Wandstärke Gehäuse | 2,0 mm, Innenseite an der Platinenkante (y 27,45) |
| Stößelspitze | y 25,45 = 2,0 mm vor der Kante, also in der Außenwand |
| Pins | (169,5 / 31,35) und (174,0 / 31,35), Stößelspitze 5,9 mm vor den Pins |
| Gehäusefront des Tasters | 1,05 mm hinter der Platinenkante |

Vorher war S2 ein stehender Bourns 1543-650-149 mitten auf der Platine, im
Gehäuse nicht erreichbar. Der PTS645 wurde gewählt, weil es für ihn Footprint
und Herstellermodell in der KiCad-Bibliothek gibt und er breit lieferbar ist
(Mouser 611-PTS645VL582, DigiKey CKN9116-ND). Die Bibliothek liegt in
`pcb/Bauteile/PTS645VL58-2LFS/`. Das Schaltsymbol `1543-650-149` (Taster,
2 Pins) wird weiterverwendet, nur Footprint und Bestellfelder sind umgestellt.

Das GND-Pad hat auf F.Cu nur einen Thermal-Steg, weil EN und USB− dicht
daneben laufen. Es ist durchkontaktiert und auf B.Cu voll angebunden.
`BasisStation.kicad_dru` erlaubt deshalb für S2 einen Steg. Ein Ausschluss war
nicht möglich: Bei diesem Pad liegt der DRC-Marker nicht auf der Pad-Mitte.

### 3D-Modelle (SHBS-24, 2026-09-29)

Alle Bauteile haben ein 3D-Modell, eingetragen im Bibliotheks-Footprint unter
`pcb/Bauteile/` und in der Platine.

| Bauteile | Modell | Hinweis |
|----------|--------|---------|
| C7, C10, C12 | `Bauteile/WCAP-FTXX_P10/WCAP-FTXX_P10.step` | Hersteller-Modell, war vorhanden, aber nicht verknüpft. Ursprung in Bauteilmitte, daher **Z-Versatz 6 mm** (vom Bediener ermittelt) |
| J6 | `Bauteile/wuerth_6120XX21621/6120XX21621_61200621621.step` | dito, **Z-Versatz 4,5 mm** |
| S2 | `Bauteile/PTS645VL58-2LFS/SW_Tactile_SPST_Angled_PTS645Vx58-2LFS.step` | Herstellermodell aus der KiCad-3D-Bibliothek (seit SHBS-25). Das selbst erstellte Modell des früheren Bourns 1543-650-149 liegt weiter unter `Bauteile/1543-650-149/`, wird aber nicht mehr verwendet |
| C8 | KiCad `CP_Radial_D6.3mm_P2.50mm` | Ersatz mit passenden Maßen. Pin 1 (+) des Footprints liegt rechts, daher 180° gedreht und 1,25 mm versetzt |
| D7–D10 | `Bauteile/WL-TMRC_3MM/…step`, `Bauteile/WL-TMRW_3MM/…step` | Würth-Originalmodelle (waren vorhanden), ohne Versatz, mit ungekürzten Anschlussdrähten |
| PS1 | KiCad `SOT-23-6.step` | vorher veraltete Variable `KISYS3DMOD` mit `.wrl` |
| J1, J_PWR1 | KiCad `USB_C_Receptacle_Amphenol_12401610E4-2A` | Nachbarvariante, für die Gehäusepassung nur eine Näherung |

Die KiCad-Standardmodelle lassen sich im Dev-Container nicht rendern
(3D-Bibliothek nicht installiert); geprüft werden sie im 3D-Viewer unter
Windows.

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
| Architektur-Diagramm | `pcb/architektur_basisStation.drawio` (Neuauflage 2026-09-24) als Blockskizze; Kurzfassung als Textdiagramm in [architecture.md](architecture.md). Nur die `.drawio` wird versioniert — PNG/PDF-Exporte nicht einchecken, sonst laufen die Kopien wieder auseinander (so geschehen bei der ersten Fassung). Das Bild im Root-Blatt `BasisStation.kicad_sch` ist ein Export davon und bei Änderungen neu einzufügen |

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
   Modelle aus der KiCad-Standardbibliothek werden über
   `${KICAD10_3DMODEL_DIR}/…` referenziert (SHBS-32).
3. Eintrag in `sym-lib-table` und `fp-lib-table` ergänzen.
4. Footprint-Vorgabe im Symbol auf `<Bibliothek>:<Footprint>` setzen.
5. Symbol im **aktuellen KiCad-Dateiformat** ablegen (siehe unten).

### Dateiformat der Symbolbibliotheken (SHBS-14)

Alle `.kicad_sym` im Projekt liegen im KiCad-9-Format (`version 20241209`).
Seit dem Umstieg auf KiCad 10 (SHBS-30) gilt die Regel sinngemäß für das
KiCad-10-Format: Sobald der Schaltplan in KiCad 10 gespeichert ist, die
Bibliotheken mit `kicad-cli sym upgrade` nachziehen.

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

- **KiCad 10 ist Pflicht (SHBS-30).** Nur KiCad 10 erzeugt PDFs mit
  eingebettetem 3D-Modell (siehe unten). Container und Arbeitsplätze müssen
  dieselbe Hauptversion haben: Eine in KiCad 10 gespeicherte Datei kann
  KiCad 9 nicht mehr lesen. Ubuntu 24.04 liefert nur KiCad 8, deshalb das
  PPA `kicad/kicad-10.0-releases`.
- **`kicad-packages3d` ist installiert.** Das Paket wiegt 3,2 GB, liefert
  aber die Standard-3D-Modelle (Widerstände, Kondensatoren, USB-C, …). Ohne
  es fehlen diese Bauteile im 3D-Export stillschweigend — `kicad-cli` meldet
  fehlende Modelle nicht. Symbole und Footprints werden für ERC, Netzliste
  und BOM benötigt.
- **Globale Bibliothekstabellen werden vorbelegt.** `kicad-cli` legt beim
  ersten Aufruf nur `fp-lib-table` selbst an, nicht `sym-lib-table`. Ohne diese
  Datei gelten sämtliche Standardbibliotheken (`power`, `Device`, …) als
  unbekannt und der ERC-Report füllt sich mit `lib_symbol_issues`. Das
  Dockerfile kopiert deshalb beide Vorlagen aus `/usr/share/kicad/template/`
  nach `~/.config/kicad/10.0/`. In KiCad 10 stammen die Vorlagen aus den
  Paketen `kicad-symbols` und `kicad-footprints`.

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
[`write_xlsx.py`](../../tmp/bom/write_xlsx.py) nach
`pcb/BasisStation_Stueckliste.xlsx` — fester Name neben `BasisStation.pdf`,
jeder Lauf überschreibt sie, der Verlauf steht in Git (bis SHBS-19 unter
`tmp/report/`; die frühere Handliste `pcb/STL.xlsx` ist entfernt). Zugangsdaten:
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

### Umstieg auf KiCad 10: Befunde und Behebung (SHBS-30, SHBS-35)

Mit KiCad 9 waren ERC und DRC ohne Befund. `kicad-cli` 10.0.6 meldete gegen
den unveränderten Stand neue Befunde; alle sind behoben, ERC und DRC stehen
wieder auf **0 Fehlern und 0 Warnungen**. Die Platine liegt seitdem im
KiCad-10-Format (`version 20260206`) und lässt sich mit KiCad 9 nicht mehr
öffnen.

| Befund unter KiCad 10 | Ursache | Behebung |
|-----------------------|---------|----------|
| 2× `copper_edge_clearance`: NPTH-Loch von J1 zur GND-Zone 0,25 mm statt 0,5 mm | KiCad 10 wertet NPTH-Bohrungen als Platinenkante; die Zonen waren noch mit KiCad 9 gefüllt | Zonen mit KiCad 10 neu gefüllt (`pcb drc --refill-zones --save-board`) |
| 56× `footprint_symbol_field_mismatch` `Datasheet` | Board `~`, Schaltplan leer | Board-Feld auf den Schaltplanwert gesetzt |
| 1× `footprint_symbol_field_mismatch` an S2 | Footprint trug keines der SnapEDA-Felder des Symbols | Felder aus dem Schaltplan übernommen (verborgen, F.Fab) |
| 1× `lib_symbol_mismatch` an J1 | Siehe unten | J1 auf projekteigenes Symbol umgestellt |

Die DRC meldet `footprint_symbol_field_mismatch` **nur für das erste
abweichende Feld** eines Bauteils. Nach jeder Korrektur erneut prüfen, bis
0 Abweichungen übrig sind.

#### J1: Schirm-Pin in KiCad 10 umnummeriert

KiCad 10 hat im Standardsymbol `Connector:USB_C_Receptacle_USB2.0_16P` den
Schirm-Pin von `S1` auf `SH` umnummeriert. Der Footprint
`shbs_power:USB_C_Receptacle_Amphenol_12401598E4-2A` hat vier Schirm-Pads
`S1`. *Symbol aus Bibliothek aktualisieren* hätte den Schirm von J1
stillschweigend von GND getrennt.

J1 verweist deshalb auf `shbs_power:USB_C_Receptacle_USB2.0_16P` — eine Kopie
des bisherigen Symbols mit Pin `S1` in
[`power.kicad_sym`](../../pcb/Bauteile/Power/power.kicad_sym). Netzliste vorher
und nachher identisch, `J1.S1` an GND.

**Regel:** Vor *Symbole aus Bibliothek aktualisieren* nach einem
KiCad-Update die Pinnummern von Standardsymbolen gegen die Footprints
prüfen. Ein Symbol, das eng an einen eigenen Footprint gebunden ist, gehört
in die Projektbibliothek.

## Dokumentations-PDF mit 3D-Modell (SHBS-30)

[`pcb/export_pdf.sh`](../../pcb/export_pdf.sh) erzeugt ein einziges PDF unter
`pcb/export/BasisStation.pdf` (git-ignoriert):

1. Schaltplan, alle Blätter (`sch export pdf`)
2. Leiterplatte, eine Seite je Lage (F.Cu, B.Cu, Bestückungsdruck, Fab),
   Platinenumriss auf jeder Seite (`pcb export pdf --mode-multipage`)
3. Interaktives 3D-Modell (`pcb export 3dpdf`, U3D) — ohne DNP-Bauteile

Zusammengeführt wird mit `qpdf`, das Seiten samt Annotationen kopiert; das
3D-Modell überlebt den Merge. KiCad 10.0.6 schreibt in die 3D-PDF fehlerhafte
xref-Einträge, die `qpdf` beim Merge repariert (Warnung, kein Fehler).

Das 3D-Modell lässt sich nur in **Adobe Acrobat Reader** oder **Foxit**
drehen. Browser, Poppler (Evince, Okular) und macOS Vorschau zeigen auf der
letzten Seite eine leere Fläche.

## Pflege

Änderungen an Schaltplan, BOM oder Schnittstellen hier und in [communication.md](communication.md) nachziehen.
