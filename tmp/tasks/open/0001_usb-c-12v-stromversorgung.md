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
3. Schaltplan anpassen: J_PWR USB-C, CC-Rd, Schutz (Polyfuse, TVS), Buck; ~~PS2 und +12V-Labels entfernen~~ **erledigt**; `+3V3` an Buck-Ausgang — **offen** (manuell in KiCad).
4. PCB-Layout: USB-C + Buck platzieren und routen; ~~PS2-Footprint entfernen~~ **erledigt**.
5. ERC/DRC und Netlist-Export ohne Fehler.

## Akzeptanzkriterien

- [x] USB-C-Eingang im Schaltplan als primäre Stromversorgung (5 V VBUS).
- [ ] Buck liefert **3,3 V** an bestehendes `+3V3`-Netz (ehem. PS2-Ausgang) — **blockiert durch B1**.
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

- [x] **B9 — Projektbibliothek `power` verdeckt die KiCad-Standardbibliothek.** *(erledigt 2026-09-06)* Die `sym-lib-table` registriert `pcb/Bauteile/Power/power.kicad_sym` unter dem Namen `power` und verdeckt damit die globale Standardbibliothek. `power:GND` (28x) und `power:PWR_FLAG` sind nicht mehr auflösbar (28 ERC-Warnungen); sie rendern nur noch aus dem eingebetteten `lib_symbols`-Cache. **Blocker für B1** — `power:+3V3` liesse sich aktuell nicht platzieren.
      *Umgesetzt:* Bibliothek in `sym-lib-table` auf `shbs_power` umbenannt; `lib_id` und eingebettete `lib_symbols` von J_PWR1 und PS1 in `Stromversorgung.kicad_sch` nachgezogen. Die 28 `power:GND`-Referenzen bleiben unverändert und lösen wieder gegen die KiCad-Standardbibliothek auf. **Per ERC-Lauf vom 2026-09-06 23:22 bestätigt.**
- [ ] **B1 — `+3V3` ist lokales Label.** Auf beiden Blättern als `(label "+3V3")` statt Power-Symbol. Lokale Labels sind blattlokal → Buck-Ausgang erreicht U6 nicht. ERC: `power_pin_not_driven` an U6 Pin 2. Netzliste: `/Layout/+3V3`.
      *Fix:* auf beiden Blättern durch `power:+3V3`-Symbol ersetzen (global, wie GND bereits gelöst).
- [ ] **B2 — `PW_EN` unnötig global (optional, kein Defekt).** Korrigiert 2026-09-06: `PW_EN` (Enable MP2359) und `/Layout/EN` (Chip-Enable/Reset ESP32: R9, C7, S2, J6, U6 Pin 3) sind **verschiedene Signale**. Beide `PW_EN`-Labels liegen auf demselben Blatt, das Netz ist geschlossen, ERC meldet nichts. Eine Zusammenlegung wäre schädlich — S2 würde die eigene Versorgung abschalten.
      *Fix:* optional `PW_EN` auf lokales Label zurückstufen.
- [ ] **C8 Pin 1 unverbunden** (ERC-Fehler, Layout) — unabhängig von B1/B3 prüfen.
- [ ] **B3 — Kein PWR_FLAG auf dem Stromversorgungsblatt** (4x im Layout, 0x dort). ERC-Fehler an PS1 Pin 5 [VIN] und J_PWR Pin A4 [VBUS].
      *Fix:* PWR_FLAG an VBUS (hinter F1) und an den 3,3-V-Ausgang.

Danach: Netzliste neu exportieren (`BasisStation.net` ist vom 2026-06-09 und enthält noch PS2 und `+12V`), PCB nachziehen, ERC/DRC leer fahren.

### ERC-Verlauf

| Lauf | Meldungen | Fehler | Warnungen |
|------|-----------|--------|-----------|
| 2026-06-17 20:49 (vor B9) | 53 | 5 | 48 |
| 2026-09-06 23:22 (nach B9) | 24 | 4 | 20 |

Verbleibende Warnungen betreffen andere Bibliotheken (LED, WCAP-FTXX, WCAP-PT5H, WL-TMRC, WLAN_Antenna/Pigtail, USB_B_Micro, D3V3XA4B10LP, 1543-650-149) — nicht Teil dieses Tasks.

Der fünfte ERC-Fehler (`J_PWR?` unannotiert) ist bereits erledigt — `ERC.rpt` ist von 20:49, der Schaltplan von 21:46 desselben Tages.

## Fortschritt

- 2026-06-08: Task angelegt; PS2 und +12V entfernt.
- 2026-06-12: Option C festgelegt (5 V USB-C + MP2359), Symbole/Footprints/lib-tables ergänzt.
- 2026-06-17: Blatt `Stromversorgung.kicad_sch` manuell gezeichnet, ERC-Lauf (5 Fehler, 48 Warnungen).
- 2026-09-06: **B9 per ERC verifiziert.** Neuer Lauf (23:22) gegen den alten (2026-06-17 20:49): Meldungen 53 → 24, Fehler 5 → 4, Warnungen 48 → 20. Die 28 `lib_symbol_issues` zu `power:GND` sind verschwunden, ebenso der `unannotated`-Fehler an J_PWR. Die verbleibenden 4 Fehler sind exakt B1 (U6 Pin 2 [3V3]), B3 (PS1 Pin 5 [VIN], J_PWR1 Pin A4 [VBUS]) und C8 Pin 1. **Nächster Schritt:** B1 — `+3V3` auf beiden Blättern als Power-Symbol.
- 2026-09-06: B9 umgesetzt — `sym-lib-table` und `Stromversorgung.kicad_sch` angepasst (5 geänderte Zeilen, Zeilenenden erhalten). Restreferenzen projektweit geprüft: keine. **Nächster Schritt:** Schaltplan in KiCad öffnen, ERC laufen lassen — die 28 GND-Warnungen müssen verschwunden sein. Danach B1.
- 2026-09-06: Analyse der KiCad-Dateien. Task 3 ist entgegen dem bisherigen Vermerk gezeichnet und committet. Netzanbindung jedoch defekt — Befunde B1–B3 dokumentiert. **Nächster Schritt:** B1–B3 in KiCad beheben, dann Netzliste und PCB neu erzeugen.

## Commits

- `b89eb9c` USB-C-Stromversorgung mit MP2359-Buck auf 3,3 V

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
