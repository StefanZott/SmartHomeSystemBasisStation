---
status: open
priority: high
type: feature
created: 2026-06-08
jira: SHBS-4
parent_jira: SHBS-3
---

# USB-C als Stromversorgung (5 V → 3,3 V)

## Ziel

Die bisherige virtuelle **+12-V-Versorgung** (`power:+12V`-Labels → PS2) wird durch einen **USB-C-Power-Eingang (5 V)** mit nachgeschaltetem **Buck-Wandler auf 3,3 V** ersetzt.

## Entscheidung (2026-06-12) — Option C

| Aspekt | Festlegung |
|--------|------------|
| USB-C | Standard **5 V** (CC1/CC2 mit 5,1 kΩ Rd → GND, Sink/UFP) |
| Wandler | **5 V → 3,3 V** Buck, ≥ 1 A (ersetzt PS2 / TSR 1-2433E) |
| +12-V-Netz | **entfällt** (PS2 wird entfernt) |
| +3,3-V-Netz | bleibt; neue Quelle = Buck statt PS2 |
| Debug-USB | bleibt separat (SHBS-6 / J1), kein VBUS-Parallelbetrieb ohne Freigabe |

**Hinweis:** ESP32-S3-WROOM benötigt **3,3 V** am Pin `3V3` — nicht 5 V. USB liefert 5 V; der Buck erzeugt die Modulspannung (wie auf DevKit-Boards üblich).

## Ist-Stand

- `BasisStation_Layout.kicad_sch`: Versorgung über `power:+12V`-Symbole → PS2 (TSR 1-2433E) → `/Layout/+3V3`.
- `+12V` hat keinen physischen Eingang (nur Labels + PWR_FLAG).
- Einziger Verbraucher von `+12V`: PS2 `+VIN`.

## Aufgaben

1. USB-C-Receptacle (power-only) + Buck 5→3,3 V auswählen; Symbol/Footprint ins Projekt aufnehmen.
2. ~~Entscheidung 5 V/PD/12 V~~ — **erledigt: Option C** (siehe Report `tmp/report/2026-06-12_shbs-4-usb-c-power-analyse.md`).
3. ~~Schaltplan anpassen: J_PWR USB-C, CC-Rd, Schutz (Polyfuse, TVS), Buck; PS2 und +12V-Labels entfernen; `+3V3` an Buck-Ausgang~~ — **erledigt 2026-09-15, ERC 0 Fehler**.
4. PCB-Layout: USB-C + Buck platzieren und routen; ~~PS2-Footprint entfernen~~ **erledigt**.
5. ERC ~~und Netlist-Export~~ ohne Fehler — **ERC erledigt** (0 Fehler), **Netzliste exportiert und verifiziert**; **DRC offen** (hängt an Aufgabe 4).

## Akzeptanzkriterien

- [x] USB-C-Eingang im Schaltplan als primäre Stromversorgung (5 V VBUS).
- [x] Buck liefert **3,3 V** an bestehendes `+3V3`-Netz (ehem. PS2-Ausgang) — erledigt 2026-09-15 (B1, B11, B12); in der Netzliste führen `L1.1` und `U6.2` dasselbe Netz `+3V3`.
- [x] PS2 und `+12V`-Netzlabels entfernt; keine verwaisten Power-Symbole.
- [x] BOM aktualisiert (USB-C, Buck, CC-Widerstände, Schutz); Strom ≥ 1 A @ 3,3 V.
- [x] `docs/project/power_supply.md` angelegt; Kurzverweis in `hardware.md`

## Vorschlag Task 1 (BOM — festgelegt 2026-06-12)

| Ref (Task 3) | Funktion | Teil | Bibliothek |
|--------------|----------|------|------------|
| J_PWR | USB-C Buchse (5 V power) | Amphenol **12401548E4#2A** | `power:USB_C_Receptacle_Power` |
| PS1 | Buck 5→3,3 V, 1,2 A | MPS **MP2359DJ-LF-Z** | `power:MP2359DJ` |

Footprints: `pcb/Footprints/USB_C_Receptacle_Amphenol_12401548E4-2A.kicad_mod`, `MP2359DJ.kicad_mod`  
Symbol-Bibliothek: `pcb/Bauteile/Power/power.kicad_sym`  
Projekt: `sym-lib-table` + **`fp-lib-table`** (neu, behebt Footprints-Einträge)

**Hinweis USB4110-GF-A:** nicht im offiziellen KiCad-Footprint-Set; Amphenol 12401548E4-2A ist pin-/funktionsgleich für USB-2.0-Power (GCT USB4110 als Alternative nach Footprint-Review).

## Task 1 — erledigt

- [x] Teile ausgewählt (Option C: 5 V USB-C + MP2359 Buck)
- [x] Symbole in `pcb/Bauteile/Power/power.kicad_sym`
- [x] Footprints in `pcb/Footprints/`
- [x] `sym-lib-table` + `fp-lib-table` ergänzt
- [ ] Schaltplan/Layout (Task 3/4)

## Task 3 — Schaltplan Power — **gezeichnet** (Stand 2026-09-06)

Historie: Automatisches Einfügen per Skript hatte KiCad zum Absturz gebracht (fehlerhafte `lib_symbols`-Einbettung); der Schaltplan wurde am 2026-06-08 zurückgesetzt.

Inzwischen ist das Blatt `Stromversorgung.kicad_sch` **manuell gezeichnet** und in der Blatthierarchie eingebunden (Commit `b89eb9c`):

| Ref | Funktion |
|-----|----------|
| J_PWR1 | USB-C-Buchse 12401548E4-2A |
| PS1 | Buck MP2359DJ |
| F1 | Sicherung |
| D11 / D12 | SS34 / SMAJ5.0A (Verpolschutz / TVS) |
| L1, C13–C15 | Buck-Peripherie (10 µH, 10/22 µF, 100 nF) |
| R17, R18 | Feedback-Teiler (49,9 kΩ / 16,2 kΩ) |
| R19, R20 | CC-Rd 5,1 kΩ |

- [x] J_PWR, PS1, Schutz, CC-Rd manuell in KiCad eingezeichnet
- [ ] **Netzanbindung defekt — siehe Abschnitt „Offene Netz-Befunde"**
- [ ] PCB-Layout Task 4

## Offene Netz-Befunde (Analyse 2026-09-06)

Analyse: [`tmp/report/2026-09-06_kicad-power-netz-analyse.md`](../../report/2026-09-06_kicad-power-netz-analyse.md)

Reihenfolge zwingend: **B9 vor B1**. B9+B1+B3 lösen 3 der 5 ERC-Fehler und 28 der 48 Warnungen:

- [x] **B9 — Projektbibliothek `power` verdeckt die KiCad-Standardbibliothek.** *(erledigt 2026-09-06; durch Merge `d7a21e2` zurückgefallen, erneut behoben 2026-09-15 — siehe B10)* Die `sym-lib-table` registriert `pcb/Bauteile/Power/power.kicad_sym` unter dem Namen `power` und verdeckt damit die globale Standardbibliothek. `power:GND` (28x) und `power:PWR_FLAG` sind nicht mehr auflösbar (28 ERC-Warnungen); sie rendern nur noch aus dem eingebetteten `lib_symbols`-Cache. **Blocker für B1** — `power:+3V3` liesse sich aktuell nicht platzieren.
      *Umgesetzt:* Bibliothek in `sym-lib-table` auf `shbs_power` umbenannt; `lib_id` und eingebettete `lib_symbols` von J_PWR1 und PS1 in `Stromversorgung.kicad_sch` nachgezogen. Die 28 `power:GND`-Referenzen bleiben unverändert und lösen wieder gegen die KiCad-Standardbibliothek auf. **Per ERC-Lauf vom 2026-09-06 23:22 bestätigt.**
- [x] **B1 — `+3V3` ist lokales Label.** *(erledigt 2026-09-08, Commit `da60c97`)* Auf beiden Blättern als `(label "+3V3")` statt Power-Symbol. Lokale Labels sind blattlokal → Buck-Ausgang erreicht U6 nicht. ERC: `power_pin_not_driven` an U6 Pin 2. Netzliste: `/Layout/+3V3`.
      *Umgesetzt:* auf beiden Blättern durch `power:+3V3`-Symbol ersetzt (global, wie GND). Verifiziert: `Stromversorgung.kicad_sch` enthält `#PWR100` als `power:+3V3` am Buck-Ausgang (190,5/138,43).
- [ ] **B2 — `PW_EN` unnötig global (optional, kein Defekt).** Korrigiert 2026-09-06: `PW_EN` (Enable MP2359) und `/Layout/EN` (Chip-Enable/Reset ESP32: R9, C7, S2, J6, U6 Pin 3) sind **verschiedene Signale**. Beide `PW_EN`-Labels liegen auf demselben Blatt, das Netz ist geschlossen, ERC meldet nichts. Eine Zusammenlegung wäre schädlich — S2 würde die eigene Versorgung abschalten.
      *Fix:* optional `PW_EN` auf lokales Label zurückstufen.
- [x] **C8 Pin 1 unverbunden** (ERC-Fehler, Layout) *(erledigt 2026-09-08, Commit `1c1b027`: an 3,3-V-Netz angeschlossen)*.
- [x] **B3 — Kein PWR_FLAG im gesamten Projekt.** *(erledigt 2026-09-15, per ERC bestätigt)* Korrigiert 2026-09-15: Die bisherige Notiz „4x im Layout" zählte Treffer in der `lib_symbols`-Definition, **nicht** platzierte Symbole. `BasisStation_Layout.kicad_sch` enthält nur die Symboldefinition, keine Instanz — projektweit gibt es **null** platzierte PWR_FLAGs. ERC-Fehler an PS1 Pin 5 [VIN] und J_PWR1 Pin A4 [VBUS].
      *Fix:* **drei** PWR_FLAGs nötig, da F1 und L1 als passive Bauteile keine Power-Quelle propagieren:
      1. **VBUS vor F1** — Netz J_PWR1 A4/B4 → F1; Stich an (226,06/78,74).
      2. **VIN hinter F1** — Netz F1 → PS1 Pin 5 (mit D12, C13); Stich an (190,5/83,82).
      3. **+3V3 hinter L1** — der 3,3-V-Rail wird nur über L1 (passiv) gespeist und hat gar keinen Power-Output-Pin; ohne Flag bliebe der Fehler an U6 Pin 2 [3V3] trotz B1 bestehen. Stich an (181,61/138,43).

Danach: Netzliste neu exportieren (`BasisStation.net` ist vom 2026-06-09 und enthält noch PS2 und `+12V`), PCB nachziehen, ERC/DRC leer fahren.

- [x] **B10 — `sym-lib-table`-Regression durch Merge `d7a21e2`.** *(behoben 2026-09-15)* Der Merge hat `(name "shbs_power")` wieder auf `(name "power")` zurückgesetzt und damit B9 rückgängig gemacht: 28× `power:GND`, 3× `power:+3V3`, 3× `power:PWR_FLAG` nicht auflösbar, dazu `shbs_power` unbekannt für `PS1` und `J_PWR1`. Zusätzlich waren `WCAP-FTXX_P10`, `WCAP-PT5H_6.3X5.2`, `WL-TMRC_3MM` und `1543-650-149` nie als Symbolbibliotheken registriert (6 Warnungen). Zusammen 42 der 46 Warnungen.
      *Umgesetzt:* Nickname zurückgesetzt, vier Bibliotheken mit Pfad `${KIPRJMOD}/../Symbol/` ergänzt.
- [x] **B11 — U6-Versorgungsschiene ohne Netznamen.** *(behoben 2026-09-15)* Das Netz an `U6` Pin 2 (`C8.1`, `C10.1`, `C12.1`, `R9.1`, `J6.2`, `U6.2`, 15 Drähte) trug weder Label noch Power-Symbol. Der B1-Fix hatte `#PWR101`/`#PWR102` auf zwei **andere** 3,3-V-Inseln gesetzt — deshalb blieb `power_pin_not_driven` an `U6.2` trotz B1 und B3 bestehen.
      *Umgesetzt:* `#PWR103` (`power:+3V3`) am offenen Drahtende (248,92 / 22,86); löst zugleich eine `unconnected_wire_endpoint`-Warnung. Dieser Stummel darf nicht mehr gelöscht werden.
- [x] **B12 — Topologiefehler im Buck-Ausgangszweig** *(behoben 2026-09-15, ERC 0 Fehler)* (bereits in [power_supply.md](../../../docs/project/power_supply.md) dokumentiert). ERC macht ihn seit 2026-09-15 als `pin_to_pin` sichtbar: `PS1.6 [SW, Output]` und `#FLG03 [Power output]` auf einem Netz — der Draht mit dem `+3V3`-Label ist elektrisch der Schaltknoten `SW`.
      *Fix:* Vollständige Ist/Soll-Verdrahtung mit Schritt-für-Schritt-Anleitung im Report [2026-09-15_shbs-4-buck-ausgangszweig.md](../../report/2026-09-15_shbs-4-buck-ausgangszweig.md). **In der KiCad-GUI**, nicht per Skript. Danach prüfen, dass `#FLG03` hinter `L1` liegt.

- [x] **B13 — Acht Bauteile ohne Footprint-Zuweisung.** *(erledigt 2026-09-15)* Geprüft 2026-09-15 über alle Blätter: `F1`, `R17`–`R20` (Stromversorgung), `J1` (Debugging, wird in SHBS-6 ersetzt), `ANT1`/`ANT2` (Layout, BOM-only und bewusst leer). Ohne Zuweisung übernimmt der PCB-Abgleich (F8) die Power-Bauteile nicht.
      *Umgesetzt:* `F1` → `Fuse:Fuse_1206_3216Metric`, `R17`–`R20` → `Resistor_SMD:R_0805_2012Metric` (gemäss Stückliste in [power_supply.md](../../../docs/project/power_supply.md)). `J1` bleibt offen bis SHBS-6, `ANT1`/`ANT2` sind BOM-only.

### ERC-Verlauf

| Lauf | Meldungen | Fehler | Warnungen |
|------|-----------|--------|-----------|
| 2026-06-17 20:49 (vor B9) | 53 | 5 | 48 |
| 2026-09-06 23:22 (nach B9) | 24 | 4 | 20 |
| 2026-09-15 21:39 (nach B3, B1, C8) | 48 | 2 | 46 |
| 2026-09-15 21:43 (nach B10, B11) | 10 | 1 | 9 |
| 2026-09-15 22:27 (nach B12) | **9** | **0** | **9** |

Der Anstieg der Warnungen um 21:39 war keine Verschlechterung des Schaltplans, sondern die Bibliotheks-Regression B10 — mit deren Behebung fielen 42 Warnungen weg.

Die neun verbleibenden Warnungen sind unkritisch und liegen ausserhalb der Power-Kette: 6× `lib_symbol_mismatch` (nur Metadatenfelder, Pinzahl und -typen identisch), 1× Drahtstummel am EN-Netz, 1× `pin_to_pin` S2/J1, 1× `multiple_net_names` GND/EPAD. Details in [power_supply.md](../../../docs/project/power_supply.md).

Der fünfte ERC-Fehler (`J_PWR?` unannotiert) ist bereits erledigt — `ERC.rpt` ist von 20:49, der Schaltplan von 21:46 desselben Tages.

## Restumfang (Stand 2026-09-15)

Schaltplanseitig ist der Task abgeschlossen. Offen bleiben nur noch:

- **Aufgabe 4 — PCB-Layout.** `BasisStation.kicad_pcb` hat den Stand von vor dem USB-C-Umbau; `J_PWR1`, `PS1`, `F1`, `D11`, `D12`, `L1`, `C13`–`C15` und `R17`–`R20` sind dort noch nicht platziert. Bewusst zurückgestellt, bis SHBS-6 (`J1` auf USB-C) durch ist — sonst muss die Netzliste zweimal ins PCB übernommen werden.
- **Aufgabe 5 — DRC.** Hängt an Aufgabe 4.

## Fortschritt

- 2026-09-15 (5): **B12 behoben — ERC 0 Fehler.** Der Ausgangszweig wurde in der KiCad-GUI korrigiert (D11 senkrecht auf die SW-Schiene mit Kathode oben, C15 als Bootstrap zwischen BST und SW, C14/R17 hinter L1). Netzprüfung aus der Datei: alle fünf Zielnetze (`SW`, `BST`, `+3V3`, `GND`, `FB`) exakt wie geplant, kein unverbundener Pin. Verbleibende 9 Warnungen sind unkritisch und liegen ausserhalb der Power-Kette. **Nächster Schritt:** Netzliste `BasisStation.net` neu exportieren, PCB nachziehen (F8), platzieren, DRC.
- 2026-09-15 (4): ERC-Lauf 21:47 inhaltlich identisch zum Lauf 21:43 (10 Meldungen, 1 Fehler, 9 Warnungen) — an den Schaltplänen wurde zwischen beiden Läufen nichts geändert. **B13 erledigt** (Footprints für `F1`, `R17`–`R20`). Für **B12** liegt jetzt die vollständige Ist/Soll-Verdrahtung als Report vor: [2026-09-15_shbs-4-buck-ausgangszweig.md](../../report/2026-09-15_shbs-4-buck-ausgangszweig.md). **Nächster Schritt:** B12 in der GUI, dann Netzliste und PCB.
- 2026-09-15 (3): **B10 und B11 per ERC bestätigt.** Lauf 21:43 gegen 21:39: Meldungen 48 → 10, Fehler 2 → 1, Warnungen 46 → 9. `U6.2 [3V3]` und die Stummel-Warnung am 3,3-V-Netz sind weg, die 42 Bibliotheks-Warnungen ebenfalls. **Einziger verbleibender Fehler ist B12** (Topologie Buck-Ausgang). Neu aufgenommen: **B13** (fehlende Footprints, blockiert den PCB-Abgleich). **Nächster Schritt:** B12 in der KiCad-GUI, dann B13, dann Netzliste und PCB.
- 2026-09-15 (2): **B3 per ERC bestätigt** — Fehler an `J_PWR1.A4 [VBUS]` und `PS1.5 [VIN]` entfallen, Fehler gesamt 4 → 2. Zwei neue Befunde aufgenommen und behoben: **B10** (sym-lib-table-Regression aus Merge `d7a21e2`) und **B11** (U6-Schiene ohne Netznamen, `#PWR103` gesetzt). Verbleibend: **B12** (Topologie Buck-Ausgang). **Nächster Schritt:** ERC erneut laufen lassen — erwartet 1 Fehler, ~4 Warnungen; danach B12 in der GUI, dann Netzliste und PCB.
- 2026-09-15: Ist-Stand gegen Repository verifiziert. **B1 und C8 sind erledigt** (Commits `da60c97`, `1c1b027`) — die Task-Datei war veraltet. **B3 offen und präzisiert:** projektweit null platzierte PWR_FLAGs, drei Stück nötig (VBUS, VIN, +3V3). `ERC.rpt` stammt vom 2026-09-06 23:22 und liegt damit **vor** den Fixes — die dort gelisteten 4 Fehler sind nicht mehr der aktuelle Stand. `BasisStation.net` ist weiterhin vom 2026-06-09 und enthält noch `+12V`. **Nächster Schritt:** B3 einfügen, ERC neu laufen lassen, Netzliste exportieren, PCB nachziehen.
- 2026-06-08: Task angelegt; PS2 und +12V entfernt.
- 2026-06-12: Option C festgelegt (5 V USB-C + MP2359), Symbole/Footprints/lib-tables ergänzt.
- 2026-06-17: Blatt `Stromversorgung.kicad_sch` manuell gezeichnet, ERC-Lauf (5 Fehler, 48 Warnungen).
- 2026-09-06: **B9 per ERC verifiziert.** Neuer Lauf (23:22) gegen den alten (2026-06-17 20:49): Meldungen 53 → 24, Fehler 5 → 4, Warnungen 48 → 20. Die 28 `lib_symbol_issues` zu `power:GND` sind verschwunden, ebenso der `unannotated`-Fehler an J_PWR. Die verbleibenden 4 Fehler sind exakt B1 (U6 Pin 2 [3V3]), B3 (PS1 Pin 5 [VIN], J_PWR1 Pin A4 [VBUS]) und C8 Pin 1. **Nächster Schritt:** B1 — `+3V3` auf beiden Blättern als Power-Symbol.
- 2026-09-06: B9 umgesetzt — `sym-lib-table` und `Stromversorgung.kicad_sch` angepasst (5 geänderte Zeilen, Zeilenenden erhalten). Restreferenzen projektweit geprüft: keine. **Nächster Schritt:** Schaltplan in KiCad öffnen, ERC laufen lassen — die 28 GND-Warnungen müssen verschwunden sein. Danach B1.
- 2026-09-06: Analyse der KiCad-Dateien. Task 3 ist entgegen dem bisherigen Vermerk gezeichnet und committet. Netzanbindung jedoch defekt — Befunde B1–B3 dokumentiert. **Nächster Schritt:** B1–B3 in KiCad beheben, dann Netzliste und PCB neu erzeugen.

## Commits

- `b89eb9c` USB-C-Stromversorgung mit MP2359-Buck auf 3,3 V
- `da60c97` +3V3 global verbunden, Symbolbibliothek entkoppelt
- `1c1b027` C8 Pin 1 an 3,3-V-Netz angeschlossen
- `6ea5c64` PWR_FLAG an VBUS, VIN und Buck-Ausgang ergänzt (B3)
- `8e8f3c9` shbs_power wiederhergestellt, +3V3 auf U6-Schiene (B10, B11)
- `5cc0191` Footprints für F1 und R17–R20 zugewiesen (B13)

## Entfernung PS2 / +12V — erledigt (2026-06-08)

Aus `BasisStation_Layout.kicad_sch` entfernt:

- PS2 (TSR 1-2433E)
- `#PWR022`, `#PWR023` (`power:+12V`)
- `#FLG04` (PWR_FLAG an +12V)
- `#PWR033` (GND-Symbol nur an PS2-VOUT)
- Zugehörige Drähte und eingebettete Lib-Symbole `TSR_1-2433E`, `power:+12V`

Aus `BasisStation.kicad_pcb` entfernt:

- Footprint `CONV_TSR_1-2433E` (Ref. PS1 im Layout)
- Netz `+12V`

**Hinweis:** `+3V3` hat vorübergehend keine Quelle — ERC-Fehler erwartet bis Task 3 (J_PWR + PS1 Buck). Netlist/BOM nach F8 in KiCad neu erzeugen.

## Betroffene Dateien

- `pcb/BasisStation/Stromversorgung.kicad_sch`
- `pcb/BasisStation/BasisStation_Layout.kicad_sch`
- `pcb/BasisStation/BasisStation.kicad_pcb`
- `pcb/BasisStation/BasisStation.net`
- `docs/project/hardware.md`
