---
status: active
last_updated: 2026-09-23
type: project-doc
jira: SHBS-4
---

# Stromversorgung — USB-C 5 V → 3,3 V

Zentrale Referenz für die primäre Versorgung der SmartHome-Basisstation (JIRA **SHBS-4**, Parent **SHBS-3**).

Verwandte Dokumente: [hardware.md](hardware.md), Analyse [tmp/report/2026-06-12_shbs-4-usb-c-power-analyse.md](../../tmp/report/2026-06-12_shbs-4-usb-c-power-analyse.md).

## Kurzfassung

| Thema | Festlegung |
|-------|------------|
| Eingang | USB-C **5 V** (Standard-USB, kein PD) |
| Wandler | **AP3211** (Diodes) Buck **5 V → 3,3 V**, bis **1,5 A** — bis SHBS-17 MP2359DJ |
| Ausgang | Netz **`+3V3`** (ESP32-S3-WROOM U6, LEDs, Stecker, …) |
| Entfallen | **PS2** (Traco TSR 1-2433E), Netz **`+12V`** |
| Debug-USB | Separates Blatt `BasisStation_Debugging.kicad_sch` / **J1** (SHBS-6) |

Das ESP32-Modul benötigt **3,3 V** am Pin `3V3` — **nicht** 5 V direkt von USB.

---

## Architektur-Entscheidung (Option C, 2026-06-12)

| Option | Beschreibung | Entscheidung |
|--------|--------------|--------------|
| A | USB-PD 12 V → bestehende +12V-Kette | verworfen |
| B | 5 V → Boost 12 V → PS2 | verworfen |
| **C** | **5 V → Buck 3,3 V**, PS2 entfällt | **gewählt** |

Begründung: Kein physisches +12-V-Netz nötig; Modul und Peripherie laufen auf 3,3 V; einfachere BOM (kein PD-IC).

---

## Power-Kette (Soll)

```
USB-Netzteil / Kabel (5 V)
        │
        ▼
┌───────────────────┐
│ J_PWR  USB-C      │  VBUS (A4,A9,B4,B9) ──► Netz +5V
│ Amphenol          │  GND  (A1,A12,B1,B12, Shield)
│ 12401598E4#2A     │  CC1/CC2 ── 5,1 kΩ ── GND (UFP/Sink)
└───────────────────┘
        │
        ▼ +5V
      [ F1 ]  Polyfuse 1,1 A
        │
      [ D12 ] TVS SMAJ5.0A (→ GND)
        │
      [ C13 ] 10 µF (→ GND, nahe PS1 VIN)
        │
        ▼
┌───────────────────┐
│ PS1  AP3211       │  EN ── VIN (immer an)
│ SOT-23-6          │  BST ── C15 (100 nF) ── SW
└───────────────────┘  SW ── L1 ── + D11 (SS34) ── GND
        │                │
        │                ▼
        │           [ C14 ] 22 µF ── GND
        │                │
        │           R17 ─┴─ R18  (FB-Teiler → Pin FB)
        │                │
        └────────────────┴──► +3V3  (+ PWR_FLAG für ERC)
```

---

## Implementierungsstand (KiCad)

| Schritt | Status |
|---------|--------|
| Symbole/Footprints (`power.kicad_sym`, `pcb/Footprints/`) | erledigt |
| `sym-lib-table`, `fp-lib-table` | erledigt |
| PS2 / +12V aus Schaltplan und PCB entfernt | erledigt |
| Power-Block im Schaltplan (`Stromversorgung.kicad_sch`) | gezeichnet und verdrahtet |
| PWR_FLAG an VBUS, VIN und Ausgang | eingefügt 2026-09-15 (`#FLG01`–`#FLG03`) |
| `+3V3`-Symbol auf der U6-Schiene (`#PWR103`) | eingefügt 2026-09-15 |
| PCB-Platzierung/Routing | offen |
| Buck-Ausgangszweig korrigiert (B12) | erledigt 2026-09-15 |
| ERC ohne Fehler | **erreicht** (Lauf 2026-09-18 23:42: 0 Fehler, 7 unkritische Warnungen; Blatt `/Stromversorgung/` ohne jede Meldung) |
| DRC ohne Fehler | offen (PCB noch nicht nachgezogen) |

**Hinweis:** Automatisches Einfügen per Skript (2026-06-08) hat KiCad zum Absturz geführt (defekte `lib_symbols`). Power-Teile **nur über die KiCad-GUI** eintragen.

---

## Ist-Stand Schaltplan (Stand 2026-09-08)

ERC-Verlauf an diesem Tag: **53 → 11 Meldungen**. Bereinigt wurden die
Symbolbibliotheks-Auflösung, die `+3V3`-Netzverbindung und zwei
Verdrahtungsfehler (Commits `da60c97`, `1c1b027`, `0268e9a`, `217546d`).

### Behoben 2026-09-15: Buck-Ausgangszweig wich von der Soll-Kette ab

Bis zum 2026-09-15 wich die aus der Schaltplangeometrie rekonstruierte
Netzliste von der oben dokumentierten Power-Kette ab. **Das Netz `+3V3` war
tatsächlich der Schaltknoten `SW`.** Der Abschnitt bleibt als Nachweis
stehen; der Ist-Stand nach der Korrektur steht unter „Ergebnis" am Ende.

Ist-Stand vor der Korrektur:

| Knoten | Ist | Soll |
| ------ | --- | ---- |
| SW | `PS1.6`, **`PS1.1 (BST)`**, `L1.1`, **`C14.1`**, **`C15.2`**, **`R17.1`**, **`+3V3`** | `PS1.6`, `L1.1`, `D11` Kathode, `C15` |
| BST | — (liegt auf SW) | `PS1.1`, `C15` |
| hinter `L1` | `L1.2`, `D11` **Anode** | `C14.1`, `R17.1`, `+3V3` |
| GND | `D11` **Kathode**, `C14.2`, `C15.1`, `PS1.2` | `D11` Anode, `C14.2`, `PS1.2` |

Daraus folgen vier Punkte:

1. **`D11` verpolt und am falschen Knoten** — Anode am Ausgang, Kathode an
   GND. In dieser Lage liegt die Schottky-Diode in Durchlassrichtung vom
   Ausgang nach GND und würde die Ausgangsspannung kurzschliessen.
   Soll: Kathode an `SW`, Anode an GND (siehe [Flyback-Diode D11](#flyback-diode-d11)).
2. **`C15` (Bootstrap) liegt gegen GND** statt zwischen `BST` und `SW`.
3. **`BST` direkt auf `SW`** — ohne Bootstrap-Kondensator kann der MP2359
   sein High-Side-Gate nicht treiben.
4. **`C14` und `R17` hängen am Schaltknoten** statt am geglätteten Ausgang.
   Die Regelung würde auf `SW` regeln, die Ausgangsglättung fehlt.

Die vier ERC-Fehler des Laufs vom 2026-09-08 (`power_pin_not_driven` an
`U6.2`, `PS1.5`, `J_PWR1.A4`, `#PWR100`) hängen an diesem Punkt und an den
damals fehlenden PWR_FLAGs — letztere sind seit 2026-09-15 gesetzt (siehe
unten). **Korrektur der Topologie in der KiCad-GUI durchführen**, nicht per
Skript (siehe Hinweis oben).

### PWR_FLAG — drei Stück, eingefügt 2026-09-15

`F1` trennt zwei Netze, die beide ausschliesslich `power_in`-Pins
enthalten (`J_PWR1.A4/A9` vor der Sicherung, `PS1.5` dahinter). KiCad
verfolgt Leistung nicht durch passive Bauteile, deshalb braucht **jedes**
dieser Netze ein eigenes PWR_FLAG — zusammen mit dem am Ausgang also drei.
Dasselbe gilt für den Ausgang: `L1` ist passiv, der 3,3-V-Rail hat also
gar keinen Power-Output-Pin.

| Ref | Netz | Anschlusspunkt (mm) |
| --- | ---- | ------------------- |
| `#FLG01` | VBUS **vor** `F1` (`J_PWR1.A4/B4`) | Stich ab (226,06 / 78,74) |
| `#FLG02` | VIN **hinter** `F1` (`PS1.5`, `D12`, `C13`) | Stich ab (190,5 / 83,82) |
| `#FLG03` | Buck-Ausgang, am selben Draht wie `#PWR100` (`+3V3`) | Stich ab (181,61 / 138,43) |

Vor dem Einfügen enthielt das Projekt **keine einzige** platzierte
PWR_FLAG — `BasisStation_Layout.kicad_sch` führt das Symbol nur in seinem
`lib_symbols`-Block, ohne Instanz.

> **Erledigt:** `#FLG03` hing ursprünglich an dem Draht, der zwar `+3V3`
> hiess, elektrisch aber `SW` war. Nach der Topologie-Korrektur liegt
> `#FLG03` **hinter** `L1` auf dem echten Ausgangsknoten — am 2026-09-19
> aus der Schaltplangeometrie gegengeprüft.

### ERC-Lauf 2026-09-15 — verbleibende Befunde

Der Lauf um 21:39 bestätigt `#FLG01` und `#FLG02`: die Fehler
`power_pin_not_driven` an `J_PWR1.A4 [VBUS]` und `PS1.5 [VIN]` sind weg.
Zwei Fehler blieben, beide mit eigener Ursache.

#### `U6.2 [3V3]` — Versorgungsschiene ohne Netznamen

Das Netz an `U6` Pin 2 (138,43 / 55,88) umfasst 15 Drähte mit `C8.1`,
`C10.1`, `C12.1`, `R9.1`, `J6.2` und `U6.2` — und trug **weder Label noch
Power-Symbol**. Es war damit ein eigenes, unbenanntes Netz und konnte
grundsätzlich nicht vom Buck gespeist werden.

Der B1-Fix hatte `#PWR101` (270,51 / 77,47) und `#PWR102` (34,29 / 92,71)
auf zwei **andere** 3,3-V-Inseln des Layout-Blatts gesetzt, nicht auf die
Schiene von U6. *Behoben 2026-09-15:* `#PWR103` (`power:+3V3`) am zuvor
offenen Drahtende (248,92 / 22,86); damit entfällt zugleich die Warnung
`unconnected_wire_endpoint` an diesem Stummel.

> Dieser Drahtstummel darf jetzt **nicht** mehr gelöscht werden — er trägt
> das Power-Symbol der Schiene (siehe „Weitere offene Punkte").

#### `pin_to_pin` PS1.6 `SW` ↔ `#FLG03` — Symptom des Topologiefehlers

`PS1` Pin 6 (`SW`, Typ *Output*) und `#FLG03` (*Power output*) liegen auf
einem Netz. Das ist kein Fehler der PWR_FLAG-Platzierung, sondern die
ERC-sichtbare Bestätigung des oben beschriebenen Topologiefehlers: der
Draht mit dem `+3V3`-Label **ist** elektrisch der Schaltknoten `SW`.
`#FLG03` blieb bewusst stehen; der Fehler entfiel mit der Korrektur des
Ausgangszweigs. Die vollständige Ist/Soll-Verdrahtung mit Schritt-für-Schritt-
Anleitung steht im Report
[2026-09-15_shbs-4-buck-ausgangszweig.md](../../tmp/report/2026-09-15_shbs-4-buck-ausgangszweig.md).

### Ergebnis — Ist-Stand nach der Korrektur (2026-09-15 22:27)

Aus der Schaltplangeometrie zurückverfolgt, alle Zielnetze erreicht, kein
unverbundener Pin im Power-Zweig:

| Netz | Pins |
| ---- | ---- |
| `SW` | `PS1.6`, `C15.2`, `D11.1` (K), `L1.2` |
| `BST` | `PS1.1`, `C15.1` |
| `+3V3` | `L1.1`, `C14.2`, `R17.1`, `#PWR100`, `#FLG03` |
| `GND` | `D11.2` (A) über `#PWR013`, `C14.1`, `R18.1`, `PS1.2` |
| `FB` | `PS1.3`, `R17.2`, `R18.2` |

`D11` sitzt jetzt senkrecht auf der `SW`-Schiene (Kathode oben) statt
hinter `L1`, `C15` liegt zwischen `BST` und `SW` statt gegen GND, und
`C14`/`R17` hängen hinter `L1` am geglätteten Ausgang.

**ERC: 0 Fehler, 9 Warnungen.** Die Warnungen sind unverändert die oben
beschriebenen unkritischen Befunde ausserhalb der Power-Kette.

#### Warnungen — Regression aus dem Merge `d7a21e2`

42 der 46 Warnungen gehen auf die Bibliothekskonfiguration zurück, nicht
auf den Schaltplan:

| Ursache | Anzahl |
| ------- | ------ |
| `power:GND` nicht auflösbar | 28 |
| `power:+3V3` / `power:PWR_FLAG` nicht auflösbar | 6 |
| Bibliothek `shbs_power` unbekannt (`PS1`, `J_PWR1`) | 2 |
| `WCAP-FTXX_P10`, `WCAP-PT5H_6.3X5.2`, `WL-TMRC_3MM`, `1543-650-149` nicht registriert | 6 |

Der Merge `d7a21e2` („Merge branch 'main' of …") hat **B9 rückgängig
gemacht**: in `sym-lib-table` stand wieder `(name "power")` statt
`shbs_power` — eine einzelne Zeile, von der Gegenseite überschrieben.
Damit verdeckte die Projektbibliothek erneut die KiCad-Standardbibliothek.
*Behoben 2026-09-15:* Nickname zurückgesetzt und die vier bis dahin nie
registrierten Bibliotheken aus `pcb/Symbol/` ergänzt.

> **Lehre für Merges:** `sym-lib-table` ist eine einzeilige Konfiguration
> pro Bibliothek und wird von Merges leicht still überschrieben. Nach jedem
> Merge, der `pcb/` berührt, prüfen: `grep shbs_power pcb/BasisStation/sym-lib-table`.

### ERC-Lauf 2026-09-15, 21:43 — Bestätigung

Nach B10 und B11: **48 → 10 Meldungen, 2 → 1 Fehler, 46 → 9 Warnungen.**

| Befund | Status |
| ------ | ------ |
| `U6.2 [3V3]` nicht angesteuert | **weg** (`#PWR103`) |
| `unconnected_wire_endpoint` am 3,3-V-Stummel | **weg** (`#PWR103` sitzt darauf) |
| 42 Bibliotheks-Warnungen | **weg** (`shbs_power` + vier registrierte Bibliotheken) |
| `pin_to_pin` PS1.6 `SW` ↔ `#FLG03` | **bleibt** — einziger Fehler, siehe Topologie oben |

Die neun verbleibenden Warnungen sind alle unkritisch und liegen ausserhalb
der Power-Kette:

- **6× `lib_symbol_mismatch`** (C7, C8, C10, C12, S2, D7). Neu sichtbar,
  weil die Bibliotheken jetzt überhaupt auflösen. Verglichen wurde der
  eingebettete Cache gegen `pcb/Symbol/WCAP-FTXX_P10.kicad_sym`: **Pinzahl
  und Pintypen identisch**, Abweichung nur in den Metadatenfeldern — KiCad 9
  legt im Schaltplan leere `Footprint`- und `Datasheet`-Felder an und
  verschiebt das SnapEDA-Feld `Description` nach `Description_1`. Rein
  kosmetisch, ohne Wirkung auf Netzliste oder BOM.
- **1× `unconnected_wire_endpoint`** am EN-Netz-Stummel (85,09 / 53,34) —
  bekannt, siehe „Weitere offene Punkte".
- **1× `pin_to_pin`** S2.1 (Bidirectional) ↔ J1.5 (GND, Power output) und
  **1× `multiple_net_names`** GND/EPAD an U6 — beide bestehen seit vor dem
  USB-C-Umbau.

> **`lib_symbol_mismatch` nicht vorschnell mit „Symbole aus Bibliothek
> aktualisieren" auflösen.** Genau diese Funktion hat schon einmal korrekte
> Instanz-Referenzen überschrieben (siehe Hinweis unten). Die Warnungen sind
> harmlos; falls sie stören, die SnapEDA-Symbole sauber neu importieren.

### Fehlende Footprint-Zuweisungen (blockiert den PCB-Abgleich)

Geprüft am 2026-09-15 über alle Blätter: acht Bauteile hatten **kein**
Footprint-Feld. Ohne Zuweisung übernimmt der PCB-Abgleich (F8) sie nicht.

| Ref | Blatt | Anmerkung |
| --- | ----- | --------- |
| `F1`, `R17`, `R18`, `R19`, `R20` | Stromversorgung | **zugewiesen 2026-09-15** gemäss Stückliste oben |
| `J1` | Debugging | wird in SHBS-6 auf USB-C umgestellt |
| `ANT1`, `ANT2` | Layout | BOM-only (Antenne/Pigtail), bewusst ohne Footprint |

### Symbol- und Footprint-Bibliotheken

- Der Projekteintrag in `sym-lib-table` heisst seit SHBS-4 **`shbs_power`**
  (vorher `power`, was die KiCad-Standardbibliothek verdeckte). Am
  2026-09-15 durch den Merge `d7a21e2` kurzzeitig auf `power` zurückgefallen
  und wieder korrigiert.
- Die Symbole von `WCAP-FTXX_P10`, `WCAP-PT5H_6.3X5.2`, `WL-TMRC_3MM` und
  `1543-650-149` verweisen auf die Footprint-Bibliothek **`Footprints`**
  statt auf gleichnamige, nicht existierende Bibliotheken. Als
  **Symbol**bibliotheken waren sie bis 2026-09-15 nicht in `sym-lib-table`
  eingetragen (6 ERC-Warnungen) — jetzt ergänzt, Pfad `${KIPRJMOD}/../Symbol/`.
- **Wichtig:** Nach Änderungen an `sym-lib-table` oder an den
  `.kicad_sym`-Dateien das Projekt in KiCad **schliessen und neu öffnen**.
  Ein „Symbole aus Bibliothek aktualisieren" mit noch im Speicher
  gehaltenem Altstand überschreibt sonst korrekte Instanz-Referenzen.

### Weitere offene Punkte

- Drahtstummel (85,09 / 53,34) → (95,25 / 53,34) am EN-Netz: ohne Anschluss,
  besteht seit vor dem USB-C-Umbau; Löschen ändert die Netzliste nicht.
- Der zweite Stummel (240,03 / 22,86) → (248,92 / 22,86) am 3,3-V-Netz trägt
  seit 2026-09-15 das Power-Symbol `#PWR103` und **muss bleiben**.
- `BasisStation.net` stammt vom 2026-06-09 und enthält noch `PS2`/`+12V`;
  das PCB ist älter als der Schaltplan. Beides nach der Topologie-Korrektur
  neu erzeugen.
- Netznamen der Eingangsseite: `PW_EN` auf der 5-V-Schiene, VBUS unbenannt
  (siehe Abschnitt „Netze"). Rein kosmetisch, ändert die Topologie nicht.

---

## Lastbudget (Stand 18.09.2026)

Nach Hinzunahme der Ethernet-Sektion (SHBS-5).

| Verbraucher | Annahme @ 3,3 V | Quelle |
|-------------|-----------------|--------|
| ESP32-S3, WLAN-Sendespitze | ~350 mA | Modul-Datenblatt |
| W5500, 100 Mbit/s sendend | **132 mA** | W5500-Datenblatt Abschnitt 5.4 |
| Link-LEDs der RJ45 (2 × 6 mA) | ~12 mA | 220 Ω an 3,3 V |
| Status-LEDs `D7`–`D10` (4 × 5 mA) | ~20 mA | 220 Ω an 3,3 V |
| **Summe Worst Case** | **~515 mA** | |

Bei rund 85 % Wandlerwirkungsgrad entspricht das etwa **400 mA am 5-V-Eingang**.

| Grenze | Wert | Auslastung |
|--------|------|------------|
| Polyfuse `F1` | 1,1 A | ~36 % |
| Wandler `PS1` AP3211 | 1,5 A | ~34 % |

**Kein Redesign nötig.** Die Ethernet-Sektion erhöht die Last um rund 145 mA;
beide Grenzen bleiben mit deutlichem Abstand eingehalten.

Die Werte sind Spitzenwerte und treten nicht zwingend gleichzeitig auf — WLAN
und Ethernet senden im Normalbetrieb selten zugleich mit voller Leistung.

**Hinweis zur Analogversorgung:** Die Ethernet-Sektion trennt intern `+3V3`
(digital) und `+3V3A` (analog) über eine Ferritperle. Beide speisen sich aus
derselben 3,3-V-Schiene; für das Lastbudget ist die Trennung ohne Belang, für
das Layout aber nicht (siehe [ethernet.md](ethernet.md)).

## Stückliste (Power)

| Ref | Funktion | Teil / Wert | KiCad-Symbol | Footprint (Vorschlag) |
|-----|----------|-------------|--------------|----------------------|
| **J_PWR** | USB-C Buchse | Amphenol **12401598E4#2A** | `shbs_power:USB_C_Receptacle_Power` | `shbs_power:USB_C_Receptacle_Amphenol_12401598E4-2A` |
| **F1** | Überstrom | Polyfuse **1,1 A** (MF-NSMF110-2) | `Device:Fuse` | `Fuse:Fuse_1206_3216Metric` |
| **D12** | VBUS-Schutz | **SMAJ5.0A** (TVS) | `Device:D` | `Diode_SMD:D_SMA` |
| **D11** | Flyback | **SS34** (Schottky) | `Device:D` | `Diode_SMD:D_SMA` |
| **PS1** | Buck | **AP3211KTR-G1** | `shbs_power:AP3211` | `shbs_power:MP2359DJ` (SOT-23-6-Landmuster, passt unverändert) |
| **L1** | Induktivität | **4,7 µH** (empf.) oder 10 µH | `Device:L` | `Inductor_SMD:L_5.7x5.7` oder `L_Bourns_SRN6045TA` |
| **C13** | VIN bulk | **10 µF / 16 V** X7R | `Device:C` | `Capacitor_SMD:C_0805_2012Metric` |
| **C14** | VOUT bulk | **22 µF** | `Device:C` | `Capacitor_SMD:C_0805_2012Metric` |
| **C15** | Bootstrap | **100 nF** | `Device:C` | `Capacitor_SMD:C_0805_2012Metric` |
| **R17** | FB oben | **49,9 kΩ** (1 %) | `Device:R` | `Resistor_SMD:R_0805_2012Metric` |
| **R18** | FB unten | **16,2 kΩ** (1 %) | `Device:R` | `Resistor_SMD:R_0805_2012Metric` |
| **R19** | CC1 Rd | **5,1 kΩ** | `Device:R` | `Resistor_SMD:R_0805_2012Metric` |
| **R20** | CC2 Rd | **5,1 kΩ** | `Device:R` | `Resistor_SMD:R_0805_2012Metric` |

### Bestellteile (Stand 2026-09-23, SHBS-17)

Im Schaltplan als Felder `Manufacturer` / `Manufacturer_Part_Number` /
`Mouser Part Number` hinterlegt; Preise und Verfügbarkeit liefert die
bestellfähige Stückliste ([hardware.md](hardware.md), Abschnitt
„Bestellfähige Stückliste“).

| Ref | Teil | Anmerkung |
|-----|------|-----------|
| PS1 | Diodes **AP3211KTR-G1** | siehe Abschnitt PS1 |
| J_PWR1 | Amphenol **12401598E4#2A** | siehe Abschnitt Buchsenwechsel |
| F1 | Bourns **MF-NSMF110-2** | Polyfuse 1206, 1,1 A Halte-, 2,2 A Auslösestrom, 6 V |
| C13 | Samsung **CL21B106KOQNNNE** | 10 µF, 16 V, X7R — die frühere Angabe Murata GRM21BR61C106KE15 ist bei Mouser und DigiKey ohne Lager |
| C14 | Samsung **CL21A226MOQNNNE** | 22 µF, 16 V, X5R — Kapazität sinkt unter DC-Vorspannung |
| C15 | YAGEO **CC0805KRX7R9BB104** | 100 nF, 50 V, X7R |
| R17 / R18 | YAGEO **RC0805FR-0749K9L** / **RC0805FR-0716K2L** | 1 %, 0805 |
| R19 / R20 | YAGEO **RC0805FR-075K1L** | 5,1 kΩ, 1 %, 0805 |
| L1 | Bourns **SRN6045TA-100M** | 10 µH, I<sub>sat</sub> 4,6 A — Nummer aus dem Wert abgeleitet, am Datenblatt zu bestätigen |
| D11 / D12 | **SS34** / **SMAJ5.0A** | herstellerneutrale Typen, am Datenblatt zu bestätigen |

**Buchsenwechsel (2026-09-23, SHBS-17):** Die ursprüngliche `12401548E4#2A` ist obsolet und bei
Mouser und DigiKey nicht mehr ab Lager. Ersetzt durch Amphenol **`12401598E4#2A`** (von Mouser als
Nachfolger genannt) — für `J_PWR1` **und** `J1`.

Die neue Buchse ist **nicht** pad-kompatibel zur alten, obwohl beide 24-polig und rechtwinklig sind:

| | alt `12401548E4#2A` | neu `12401598E4#2A` |
| --- | --- | --- |
| Reihe A1–A12 | SMD, Raster 0,5 mm | SMD, identisch |
| Reihe B1–B12 | **durchkontaktiert** | **SMD**, 1,7 mm vor Reihe A, um 0,25 mm versetzt |
| Schirmlaschen, Führungsstifte | 4 × THT, 2 × NPTH | identisch |

Ermittelt aus dem Amphenol-3D-Modell (STEP über DigiKey), weil die Zeichnung auf amphenol-cs.com
aus dem Container nicht abrufbar ist. Das Padbild deckt sich mit dem KiCad-Standard-Footprint der
Schwester `12401610E4#2A`; er ist als `shbs_power:USB_C_Receptacle_Amphenol_12401598E4-2A`
ins Projekt übernommen. **Folge fürs Layout:** Die B-Kontakte (`B1`/`B12` GND, `B4`/`B9` VBUS,
`B5` CC2, bei `J1` zusätzlich `B6`/`B7` D+/D−) liegen jetzt als SMD-Pads auf der Oberseite unter
dem Buchsenkörper und müssen dort angebunden werden — eine Entflechtung über die Unterseite wie bei
den bisherigen THT-Pins entfällt.

GCT **USB4110-GF-A** ist entgegen früherer Annahme **nicht** footprint-kompatibel: 16-polig, reine
SMD-Buchse zur Oberflächenmontage (Datenblatt USB4110 Rev. B2).

---

## J_PWR — USB-C Pinbelegung (12401598E4#2A)

Die Buchse ist **nur Power** (kein USB-Datenpfad). Strom kommt vom **Kabel** über **VBUS** rein; **kein Power-Output** an der Buchse — Ausgang ist **+3V3** nach PS1.

### Power-Pins (alle parallel schalten)

| Signal | Pins | Anschluss |
|--------|------|-----------|
| **VBUS (+5 V)** | **A4, A9, B4, B9** | Netz **+5V** → F1 → PS1 **VIN** |
| **GND** | **A1, A12, B1, B12** | GND |
| **Shield** | **S1** (4× Montage) | GND |

Im Projekt-Symbol sind derzeit **A4, A9** (VBUS) und **A1, B1** (GND) ausgeführt — auf dem **PCB alle VBUS- und GND-Pads** zum selben Netz führen.

### CC (Spannungsfestlegung Sink/UFP)

| Pin | Funktion | Anschluss |
|-----|----------|-----------|
| **A5** (CC1) | Configuration Channel | **R19** 5,1 kΩ → GND |
| **B5** (CC2) | Configuration Channel | **R20** 5,1 kΩ → GND |

Ohne Rd liefern viele USB-C-Netzteile **keinen** VBUS.

### Ungenutzte Pins

D+, D-, SuperSpeed (A2/A3, A6–A8, A10/A11, B2/B3, …) bleiben **offen**.

---

## PS1 — AP3211 Anschlüsse

> **Wandlerwechsel (2026-09-23, SHBS-17):** Der ursprüngliche MP2359DJ ist in allen Varianten
> (`DJ`, `DT`, `-Z`, `-P`) „nicht für Neukonstruktionen" und als `DJ` bei Mouser und DigiKey ohne
> Lager; der früher pinkompatible Richtek RT8259 ist abgekündigt. Ersetzt durch **Diodes
> `AP3211KTR-G1`** ([Datenblatt](https://www.diodes.com/assets/Datasheets/AP3211.pdf)) — gleiche
> Pinbelegung, SOT-23-6 auf demselben Footprint, V<sub>FB</sub> 0,81 V (R17/R18 bleiben), 1,4 MHz,
> asynchron mit D11, 1,5 A, V<sub>IN</sub> 4,5–18 V, UVLO 3,8 V typ. Die Strombegrenzung
> (1,8–2,4 A) liegt klar unter dem Sättigungsstrom von L1 (SRN6045TA-100M: 4,6 A); D11 (SS34, 3 A)
> passt ebenfalls. Das Datenblatt nennt 10 nF Bootstrap-Kapazität, `C15` bleibt bei 100 nF —
> unkritisch, der interne Bootstrap-Regler lädt ihn in jeder Aus-Phase nach. Pinname im Symbol
> bleibt `BST` (Datenblatt: `BS`).

| Pin | Name | Verbindung |
|-----|------|------------|
| **5** | **VIN** | Netz **+5V** (nach F1/D12/C13) |
| **2** | **GND** | GND |
| **4** | **EN** | mit **VIN** verbinden (Wandler an) |
| **6** | **SW** | → **L1** Pin 1; **C15** (100 nF) zu **BST**; **D11** Kathode |
| **1** | **BST** | **C15** (100 nF) → **SW** |
| **3** | **FB** | Mitte des Teilers **R17 / R18** |

### Flyback-Diode D11

**SS34:** Kathode an **SW**, Anode an **GND** (typisch für asynchronen Buck).

### FB-Teiler (3,3 V)

```
+3V3 ── R17 (49,9 kΩ) ──┬── FB (Pin 3)
                        │
                       R18 (16,2 kΩ)
                        │
                       GND
```

Formel: \( V_{OUT} = V_{FB} \times (1 + R17/R18) = 0{,}81\,\text{V} \times (1 + 49{,}9/16{,}2) \approx 3{,}30\,\text{V} \) — V<sub>FB</sub> = 0,81 V bei MP2359 und AP3211 gleich (die frühere Angabe 0,6 V war falsch). Das AP3211-Datenblatt nutzt in der Applikationsschaltung 49,9 kΩ / 16,3 kΩ.

### Induktivität L1

Datenblatt: **1 µH … 10 µH**, Stromrating ≥ **1,5 A** (25 % über max. Last), **DCR < 200 mΩ**. Für 3,3 V / 1 A typisch **4,7 µH** (Tabelle 2).

---

## Netze

| Netz | Name im Schaltplan | Herkunft | Verbraucher |
|------|--------------------|----------|-------------|
| VBUS (vor `F1`) | *unbenannt* | J_PWR VBUS (`A4`, `A9`) | `F1`, `#FLG01` |
| 5 V (hinter `F1`) | **`PW_EN`** | `F1` | `D12`, `C13`, `PS1.5` (VIN), `PS1.4` (EN), `#FLG02` |
| **`+3V3`** | `+3V3` | PS1 via `L1`/`C14` | U6, LEDs, Stecker, Entkopplung |
| **`GND`** | `GND` | J_PWR, PS1, Passives | gemeinsame Masse |

> **Namensabweichung:** Die 5-V-Schiene hinter `F1` trägt im Schaltplan das
> globale Label **`PW_EN`**, nicht `+5V`. Der Name stammt daher, dass `PS1.4`
> (EN) über dasselbe Label an VIN gelegt ist — das ist die dokumentierte
> Absicht („EN mit VIN verbinden, Wandler immer an"), aber der Name beschreibt
> den Enable-Pin, nicht die Leistungsschiene. Das VBUS-Netz vor `F1` ist
> unbenannt. Beides ist elektrisch korrekt; für Netzliste, Routing und BOM
> wäre `+5V` bzw. `VBUS` lesbarer. Umbenennung steht als Restposten aus.

Im Layout-Sheet: **`+3V3`** als globales Label oder `power:+3V3`-Symbol plus **PWR_FLAG** am Buck-Ausgang.

---

## KiCad — Bibliotheken und Pfade

| Artefakt | Pfad |
|----------|------|
| Symbolbibliothek | `pcb/Bauteile/Power/power.kicad_sym` |
| USB-C-Footprint | `pcb/Bauteile/Power/USB_C_Receptacle_Amphenol_12401598E4-2A.kicad_mod` (bis SHBS-17: `…12401548E4-2A.kicad_mod`, ungenutzt) |
| Wandler-Footprint (PS1) | `pcb/Bauteile/Power/MP2359DJ.kicad_mod` — Name historisch, genutzt für AP3211 |
| Schaltplan (Layout) | `pcb/BasisStation/BasisStation_Layout.kicad_sch` |
| Leiterplatte | `pcb/BasisStation/BasisStation.kicad_pcb` |
| `sym-lib-table` | Eintrag **`shbs_power`** |
| `fp-lib-table` | `${KIPRJMOD}/../Footprints` |

Symbole in KiCad: **Platzieren → Symbol** → Bibliothek **`shbs_power`** oder Standard **`Device:*`**.

> **Bibliotheksname:** Der Projekteintrag hiess ursprünglich `power` und
> verdeckte damit die gleichnamige KiCad-Standardbibliothek — `power:GND`,
> `power:PWR_FLAG` und `power:+3V3` waren dadurch projektweit nicht auflösbar
> (28 ERC-Warnungen). Seit SHBS-4 heisst der Projekteintrag **`shbs_power`**;
> der Nickname `power` bleibt der KiCad-Standardbibliothek vorbehalten.

---

## Abgrenzung Debug-USB (SHBS-6)

| Port | Blatt | Funktion |
|------|-------|----------|
| **J_PWR** | Layout | **Stromversorgung** (5 V) |
| **J1** | Debugging | Seriell/JTAG — **kein** paralleler VBUS zu J_PWR ohne Konzept |

---

## Alte Versorgung (entfernt)

```
[+12V] (virtuell) → PS2 (TSR 1-2433E) → +3V3
```

- **PS2**, **+12V**-Labels und TSR-Footprint auf PCB entfernt (2026-06-08).
- Traco **TSR 1-2433E** würde 6,5–32 V Eingang benötigen — für 5 V USB-C **unpassend**.

---

## Nächste Schritte (Checkliste)

1. [x] **Ausgangszweig korrigiert** (D11-Polung, C15 als Bootstrap, C14/R17 hinter L1) — 2026-09-15, unabhängig gegengeprüft 2026-09-19
2. [x] ERC erneut gelaufen — **0 Fehler** (2026-09-18 23:42: 0 Fehler, 7 Warnungen)
3. [x] Footprints für `F1`, `R17`–`R20` zuweisen — erledigt 2026-09-15
4. [ ] Netzliste `BasisStation.net` neu exportieren (aktuell vom 2026-06-09, enthält noch `PS2`/`+12V`)
5. [ ] Alle Power-Bauteile in `BasisStation_Layout.kicad_sch` platzieren und verdrahten
6. [ ] **F8** — PCB aus Schaltplan aktualisieren
7. [ ] VBUS/GND-Pads J_PWR vollständig routen
8. [ ] Buck-Bauteile dicht an PS1 layouten ( kurze Wege VIN, SW, GND )
9. [ ] DRC prüfen
10. [ ] BOM exportieren

---

## Pflege

Bei Änderungen an Schaltplan, BOM oder Teileauswahl diese Datei und den Kurzabschnitt in [hardware.md](hardware.md) aktualisieren.
