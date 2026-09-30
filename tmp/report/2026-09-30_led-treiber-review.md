---
type: code-review
created: 2026-09-30
jira: SHBS-40
status: final
---

# Review LED-Treiber und Layout (Hinweise Hardwareentwickler)

## Ausgangslage

Ein Hardwareentwickler hat drei Punkte angemerkt:

1. R13–R16 und R23–R26 sind viel zu groß.
2. Das Layout ist trotzdem sehr gequetscht.
3. Q1–Q4 sind unnötig, weil die GPIOs genug Strom liefern. Das soll geprüft werden.

## Befunde

### 1. Widerstände R13–R16, R23–R26

- Footprint `Resistor_THT:R_Axial_DIN0617_L17.0mm_D6.0mm_P20.32mm_Horizontal`,
  Bauteil Vishay **PR02** (2-W-Metallschicht, 17 mm Körper, 20,32 mm Raster).
- Tatsächliche Verlustleistung: 220 Ω bei 5 mA ≈ 5,5 mW, 4,7 kΩ bei 0,55 mA
  ≈ 1,4 mW. Überdimensioniert um Faktor > 300.
- Alle übrigen 20 Widerstände sind SMD 0805. R9 (EN-Pull-up) ist als einziger
  weiterer THT-Widerstand (DIN0207) bestückt.
- **Bestätigt.** 0805 (125 mW) reicht mit großer Reserve und passt zum Rest.

### 2. Layout

Render der Oberseite: Die obere Hälfte (Versorgung, USB, Ethernet, U6) ist
dicht gepackt (Raster 3,5 mm, Beschriftungen überlappen teils). Die untere
Hälfte der Platine (160 × 132,55 mm) enthält nur die LED-Treiberkette und ist
sonst leer. Die Enge ist also eine Frage der Verteilung, nicht der Fläche.

- **Bestätigt.** Nach Wegfall der LED-Treiber wird zusätzlich Platz frei.

### 3. Transistoren Q1–Q4

- ESP32-S3 GPIO (Datenblatt ESP32-S3, DC-Kennwerte): Source-Strom bis ca.
  40 mA bei höchster Treiberstufe, Sink bis ca. 28 mA. Standard-Treiberstufe
  (Stufe 2) ca. 20 mA.
- Benötigt: ca. 5 mA je LED, 4 LEDs = 20 mA gesamt. Deutlich unter den Grenzen.
- Direktansteuerung `GPIO → Vorwiderstand → LED → GND` bleibt **aktiv High**,
  die Firmware-Logik ändert sich nicht.
- **Bestätigt: Q1–Q4 und R23–R26 können entfallen.**

### Nebenbefunde

- **Blaue LED D8 (151033BS03000):** Flussspannung blauer LEDs liegt typ. bei
  ca. 3 V. An 3,3 V (bisher über Q, künftig über GPIO-High ≈ 3,2 V) bleibt am
  Vorwiderstand kaum Spannung — D8 leuchtet mit 220 Ω nur sehr schwach. Das
  Problem besteht bereits im heutigen Entwurf. Vorwiderstand für Blau kleiner
  wählen (Wert nach Datenblatt, am Prototyp prüfen).
- **Firmware passt nicht zur Hardware:** `main/LED.h` nutzt noch GPIO46/3/45/21
  (alte Strapping-Pin-Belegung), der Schaltplan seit SHBS-9 GPIO48/21/47/38.
  Separates Ticket nötig.

## Empfehlungen

- Q1–Q4, R23–R26 entfernen, LEDs direkt über Vorwiderstand am GPIO.
- R13–R16 als 0805 SMD, Blau mit angepasstem Wert. Optional R9 ebenfalls 0805.
- Layout entzerren: Bauteilgruppen der oberen Hälfte in den freien Bereich
  verteilen; feste Positionen (T1, J1, J_PWR1, D7–D10) bleiben.

## Umsetzung (SHBS-41 bis SHBS-44)

- Schaltplan: Q1–Q4, R23–R26 entfernt, LEDs direkt am GPIO. R13/R15/R16
  220 Ω, R14 (blau) 100 Ω, R9 10 kΩ, alle YAGEO RC0805. ERC 0/0.
- Layout, erste Fassung: nur Abstände auf ≥ 1 mm gebracht. Der Bediener hat
  bemängelt, dass die Bauteile weiter in der oberen Hälfte sitzen.
- Layout, zweite Fassung: Blöcke über die Platine verteilt (Buck-Wandler
  links, C7/C10/C12/R9/J6 rechts unten). Oben bleiben nur Bauteile, die an
  Buchsen oder ICs gebunden sind. U7 und die MDI-Gruppe bleiben nach Wahl des
  Bedieners unverändert.
- LEDs D7–D10 liegend (Beine 90° gebogen), Linse bündig in der 2 mm dicken
  Gehäusewand an der Unterkante.
- DRC mit Schaltplanabgleich 0/0/0. 17 begründete Ausschlüsse (vorher 15:
  sechs starved_thermal entfallen, acht silk_edge_clearance für die LEDs neu).
- Draufsicht: [2026-09-30_layout-top-shbs42.png](2026-09-30_layout-top-shbs42.png)
- Doku: `docs/project/hardware.md`, `docs/project/power_supply.md`,
  Stückliste neu erzeugt.
- `pcb/export/BasisStation.pdf` neu erzeugt (nicht versioniert).

## Nachtrag SHBS-52: U6 in die rechte Hälfte

- U6 sitzt jetzt bei 185 / 90 und ist um 90° gedreht. Der U.FL-Stecker zeigt
  zur rechten Wand (Kabelweg ca. 18 mm).
- C8 und C7/R9 sitzen über U6, C10/C12 darunter.
- USB 124–138 mm, SPI 61–66 mm. Für USB Full-Speed ist das unkritisch, den
  SPI-Takt zunächst auf 20 MHz setzen.
- Neu entstandene GND-Inseln an U1 (USB+ auf B.Cu) sind behoben, J6-Pad 4
  ist über ein Via angebunden. DRC 0/0/0, 17 Ausschlüsse (unverändert).
- Draufsicht: [2026-09-30_layout-top-shbs52.png](2026-09-30_layout-top-shbs52.png)

## Offen

- Firmware `main/LED.h` nutzt noch GPIO46/3/45/21 (eigenes Ticket, vom
  Bediener zurückgestellt).
- Blaue LED D8 am Prototyp prüfen (Helligkeit, Exemplarstreuung der
  Flussspannung).
- Biegemaß und Länge der liegenden Würth-LEDs am Muster prüfen (Annahme:
  5,3 mm vom Kragen bis zur Linsenspitze).
- Gehäuse: RP-SMA-Buchse an die rechte Wand, auf Höhe des U.FL-Steckers.
