---
type: analysis
created: 2026-09-18
jira: SHBS-5
status: final
---

# Abgleich der MDI-Sektion gegen das WIZnet-Referenzschaltbild

## Ausgangslage

Der W5500-Block im Blatt `ethernet.kicad_sch` ist vollständig beschaltet
(Task 0003, abgeschlossen). Auf der RJ45-Seite (Task 0004) sind Signalpaare,
LEDs und Schirmung gezeichnet; offen blieben die Mittelanzapfungen `CTD`
(`T1.2`) und `CRD` (`T1.5`).

Beim Beschaffen des Referenzschaltbilds fiel auf, dass WIZnet rund um die
MDI-Leitungen deutlich mehr Bauteile vorsieht als unser Entwurf. Dieser Bericht
gleicht beide ab.

**Quelle:** `pcb/Datasheets/wiznet_W5500_ref-schematic_RJ45-with-magnetics.pdf`
(WIZnet, *W5500-Ref-RJ45WithMag*, Rev. C, 25.09.2015). Die Topologie wurde aus
der gerenderten Zeichnung abgelesen, nicht aus der PDF-Textebene — die
Textkoordinaten stimmen dort nicht mit der Darstellung überein.

## Ergebnis / Befunde

### Referenz-Topologie

**Sendezweig**

| Bauteil | von | nach |
| ------- | --- | ---- |
| `R1` 49,9 Ω 1 % | `3V3A` | `TXN` |
| `R2` 49,9 Ω 1 % | `3V3A` | `TXP` |
| `R3` 10 Ω 1 % | `3V3A` | Knoten `TCT` |
| `C8` 22 nF | Knoten `TCT` | `GND` |

Der Sendetreiber des W5500 arbeitet stromgesteuert. Die Mittelanzapfung wird
deshalb aus `3V3A` **gespeist** — über 10 Ω, abgeblockt mit 22 nF. Die beiden
49,9 Ω an `TXP`/`TXN` bilden die Abschlussimpedanz.

**Empfangszweig**

| Bauteil | von | nach |
| ------- | --- | ---- |
| `C9` 6,8 nF | `RXP` (Chip) | `RD+` (Buchse) — **in Serie** |
| `C10` 6,8 nF | `RXN` (Chip) | `RD−` (Buchse) — **in Serie** |
| `R6` 49,9 Ω 1 % | `RXP` (Chip) | Knoten `RCT` |
| `R7` 49,9 Ω 1 % | `RXN` (Chip) | Knoten `RCT` |
| `C15` 10 nF | Knoten `RCT` | `GND` |

Der Empfänger arbeitet spannungsgesteuert und bringt seine Vorspannung selbst
mit. Deshalb **keine** Speisung der Mittelanzapfung, sondern zwei
Serienkondensatoren, die den Gleichanteil trennen. Der Mittelpunkt der beiden
49,9 Ω liegt auf `RCT` und ist über 10 nF wechselstrommässig auf Masse gelegt.

**Versorgung**

`3V3D` und `3V3A` sind **getrennt** und über die Ferritperle `L1`
(HH-1M1608-121JT) verbunden. Der EMV-Hinweis auf dem Blatt verlangt 100–2000 Ω
bei 100 MHz. Die Analogseite ist mit `C1`–`C6` (je 0,1 µF) und `C7` (10 µF)
abgeblockt.

**Schirm**

`GHs_GND` (8), `CH_GND1` (13) und `CH_GND2` (14) liegen auf `CGND`; `CGND` ist
über `C16` 1 nF/2 kV mit `GND` verbunden.

### Abgleich mit unserem Stand

| Thema | Referenz | `ethernet.kicad_sch` | Bewertung |
| ----- | -------- | -------------------- | --------- |
| Abschluss `TXP`/`TXN` | 2 × 49,9 Ω nach `3V3A` | **fehlt** | ergänzen |
| Mittelanzapfung Sendezweig | 10 Ω nach `3V3A`, 22 nF nach `GND` | `T1.2` auf No-Connect | ergänzen |
| Serienkondensatoren `RXP`/`RXN` | 2 × 6,8 nF | **fehlt**, direkt verbunden | ergänzen |
| Abschluss `RXP`/`RXN` | 2 × 49,9 Ω auf `RCT`-Knoten | **fehlt** | ergänzen |
| Mittelanzapfung Empfangszweig | `RCT` auf 49,9-Ω-Mittelpunkt, 10 nF nach `GND` | `T1.5` auf No-Connect | ergänzen |
| Getrennte Analogversorgung | `3V3D`/`3V3A` über Ferritperle | ein einziges `+3V3` | prüfen |
| Schirmung | `CGND`, 1 nF/2 kV nach `GND` | `CHASSIS`, `C28` 1 nF/2 kV | **stimmt überein** |
| LED-Vorwiderstände | 330 Ω, kathodenseitig | 220 Ω, anodenseitig | unkritisch |
| Quarz-Lastkondensatoren | 18 pF | 27 pF | siehe unten |

### Bewertung

Die fehlende MDI-Beschaltung ist **kein Schönheitsfehler**. Ohne die
Abschlusswiderstände stimmt die Leitungsimpedanz nicht, ohne die
Serienkondensatoren liegt der Gleichanteil des Chips auf dem Übertrager. Beides
verschlechtert die Signalqualität, ohne dass ERC oder ein einfacher
Funktionstest darauf hinweist — Symptome wären sporadische Paketfehler oder
Verbindungsabbrüche bei längeren Kabeln.

Die getrennte Analogversorgung ist der zweitwichtigste Punkt. Sie hält die
Schaltströme des Digitalteils aus der analogen Sendeendstufe heraus und ist bei
PHYs Standard.

**Widerspruch bei den Quarz-Lastkondensatoren:** Das Referenzdesign nutzt
18 pF, unsere Rechnung ergibt 27 pF (CL = 18 pF, ca. 4 pF Streukapazität). Die
Rechnung ist die lehrbuchmässige; 18 pF im Referenzdesign würde bedeuten, dass
die effektive Lastkapazität nur etwa 13 pF beträgt und der Quarz zu schnell
läuft. Möglich, dass die Referenz einen Quarz mit anderer Lastkapazität
verwendet. **Entschieden am 18.09.2026: bei 27 pF bleiben.** Die Rechnung hat Vorrang vor
der Referenz; die Frequenz wird am ersten Prototyp gemessen und die
Kondensatoren bei Bedarf nachgezogen.

## Empfehlungen

1. MDI-Sektion nach der Referenz-Topologie ergänzen: 4 × 49,9 Ω 1 %,
   2 × 6,8 nF, 10 Ω 1 %, 22 nF, 10 nF.
2. Mittelanzapfungen entsprechend anschliessen — `T1.2` an den gespeisten
   Knoten, `T1.5` an den Mittelpunkt der Empfangs-Abschlusswiderstände.
3. Versorgung in `+3V3` (digital) und `+3V3A` (analog) trennen, verbunden über
   eine Ferritperle mit 100–2000 Ω bei 100 MHz. Die sieben Abblockkondensatoren
   des W5500 wandern dabei auf die Analogseite, soweit sie an `AVDD` liegen.
4. Quarz-Lastkondensatoren bei 27 pF belassen, am Prototyp verifizieren.

## Nächste Schritte

- Punkt 1 und 2 in Task `0004` als Sollbeschaltung ausformulieren.
- Punkt 3 **entschieden am 18.09.2026: Trennung erfolgt in SHBS-5.** Späteres
  Nachrüsten würde bedeuten, die sieben Abblockkondensatoren aus Task 0003 ein
  zweites Mal umzuhängen. Der Buck-Zweig aus SHBS-4 bleibt unberührt, die
  Ferritperle sitzt auf dem Ethernet-Blatt. Spezifikation in Task 0004.
- Offen bleibt die Auswahl des HV-Kondensators (`C28`, 1 nF/2 kV) als
  konkretes Bauteil mit Bestellnummer.

**Vorbehalt:** Das Referenzdesign nutzt die Buchse CETUS **J1B1211CCD**, wir
die Würth **7499011121A**. Die Topologie wird vom analogen Frontend des W5500
bestimmt und sollte übertragbar sein; die Würth-Buchse bringt die
Bob-Smith-Terminierung zusätzlich intern mit. Vor der Fertigung gegen das
Würth-Datenblatt gegenprüfen.
