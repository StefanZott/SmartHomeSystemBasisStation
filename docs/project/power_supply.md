---
status: active
last_updated: 2026-09-08
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
| Wandler | **MP2359DJ** Buck **5 V → 3,3 V**, bis **1,2 A** |
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
│ 12401548E4#2A     │  CC1/CC2 ── 5,1 kΩ ── GND (UFP/Sink)
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
│ PS1  MP2359DJ     │  EN ── VIN (immer an)
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
| Power-Block im Schaltplan (`Stromversorgung.kicad_sch`) | gezeichnet; Ausgangszweig noch fehlerhaft (siehe unten) |
| PCB-Platzierung/Routing | offen |
| ERC/DRC ohne Fehler | offen (Stand 2026-09-08: 4 Fehler, 4 Warnungen) |

**Hinweis:** Automatisches Einfügen per Skript (2026-06-08) hat KiCad zum Absturz geführt (defekte `lib_symbols`). Power-Teile **nur über die KiCad-GUI** eintragen.

---

## Ist-Stand Schaltplan (Stand 2026-09-08)

ERC-Verlauf an diesem Tag: **53 → 11 Meldungen**. Bereinigt wurden die
Symbolbibliotheks-Auflösung, die `+3V3`-Netzverbindung und zwei
Verdrahtungsfehler (Commits `da60c97`, `1c1b027`, `0268e9a`, `217546d`).

### Offen: Buck-Ausgangszweig weicht von der Soll-Kette ab

Die aus der Schaltplangeometrie rekonstruierte Netzliste weicht von der
oben dokumentierten Power-Kette ab. **Das aktuelle Netz `+3V3` ist
tatsächlich der Schaltknoten `SW`**:

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

Die vier verbleibenden ERC-Fehler (`power_pin_not_driven` an `U6.2`,
`PS1.5`, `J_PWR1.A4`, `#PWR100`) hängen an diesem Punkt und an den noch
fehlenden PWR_FLAGs. **Korrektur in der KiCad-GUI durchführen**, nicht per
Skript (siehe Hinweis oben).

### PWR_FLAG — zwei am Eingang nötig

`F1` trennt zwei Netze, die beide ausschliesslich `power_in`-Pins
enthalten (`J_PWR1.A4/A9` vor der Sicherung, `PS1.5` dahinter). KiCad
verfolgt Leistung nicht durch passive Bauteile, deshalb braucht **jedes**
dieser Netze ein eigenes PWR_FLAG — zusammen mit dem am Ausgang also drei.

### Symbol- und Footprint-Bibliotheken

- Der Projekteintrag in `sym-lib-table` heisst seit SHBS-4 **`shbs_power`**
  (vorher `power`, was die KiCad-Standardbibliothek verdeckte).
- `WCAP-FTXX_P10`, `WCAP-PT5H_6.3X5.2`, `WL-TMRC_3MM` und `1543-650-149`
  sind ergänzt; ihre Symbole verweisen jetzt auf die Footprint-Bibliothek
  **`Footprints`** statt auf gleichnamige, nicht existierende Bibliotheken.
- **Wichtig:** Nach Änderungen an `sym-lib-table` oder an den
  `.kicad_sym`-Dateien das Projekt in KiCad **schliessen und neu öffnen**.
  Ein „Symbole aus Bibliothek aktualisieren" mit noch im Speicher
  gehaltenem Altstand überschreibt sonst korrekte Instanz-Referenzen.

### Weitere offene Punkte

- Zwei Drahtstummel ohne Anschluss: (85,09 / 53,34) → (95,25 / 53,34) am
  EN-Netz und (240,03 / 22,86) → (248,92 / 22,86) am 3,3-V-Netz. Beide
  bestehen seit vor dem USB-C-Umbau; Löschen ändert die Netzliste nicht.
- `BasisStation.net` stammt vom 2026-06-09 und enthält noch `PS2`/`+12V`;
  das PCB ist älter als der Schaltplan. Beides nach der Topologie-Korrektur
  neu erzeugen.

---

## Stückliste (Power)

| Ref | Funktion | Teil / Wert | KiCad-Symbol | Footprint (Vorschlag) |
|-----|----------|-------------|--------------|----------------------|
| **J_PWR** | USB-C Buchse | Amphenol **12401548E4#2A** | `shbs_power:USB_C_Receptacle_Power` | `Footprints:USB_C_Receptacle_Amphenol_12401548E4-2A` |
| **F1** | Überstrom | Polyfuse **1,1 A** | `Device:Fuse` | `Fuse:Fuse_1206_3216Metric` |
| **D12** | VBUS-Schutz | **SMAJ5.0A** (TVS) | `Device:D` | `Diode_SMD:D_SMA` |
| **D11** | Flyback | **SS34** (Schottky) | `Device:D` | `Diode_SMD:D_SMA` |
| **PS1** | Buck | **MP2359DJ-LF-Z** | `shbs_power:MP2359DJ` | `Footprints:MP2359DJ` |
| **L1** | Induktivität | **4,7 µH** (empf.) oder 10 µH | `Device:L` | `Inductor_SMD:L_5.7x5.7` oder `L_Bourns_SRN6045TA` |
| **C13** | VIN bulk | **10 µF / 16 V** X5R | `Device:C` | `Capacitor_SMD:C_0805_2012Metric` |
| **C14** | VOUT bulk | **22 µF** | `Device:C` | `Capacitor_SMD:C_0805_2012Metric` |
| **C15** | Bootstrap | **100 nF** | `Device:C` | `Capacitor_SMD:C_0805_2012Metric` |
| **R17** | FB oben | **49,9 kΩ** (1 %) | `Device:R` | `Resistor_SMD:R_0805_2012Metric` |
| **R18** | FB unten | **16,2 kΩ** (1 %) | `Device:R` | `Resistor_SMD:R_0805_2012Metric` |
| **R19** | CC1 Rd | **5,1 kΩ** | `Device:R` | `Resistor_SMD:R_0805_2012Metric` |
| **R20** | CC2 Rd | **5,1 kΩ** | `Device:R` | `Resistor_SMD:R_0805_2012Metric` |

### Empfohlene Einzelteile (Beispiele)

| Ref | MPN (Beispiel) | Anmerkung |
|-----|----------------|-----------|
| L1 | Würth **74405300470** (4,7 µH) | MP2359-Datenblatt Tabelle 2 |
| L1 | Bourns **SRN6045TA-100M** (10 µH) | Alternative bei 10 µH |
| C13 | Murata **GRM21BR61C106KE15** | 10 µF, 16 V, 0805 |

Alternative USB-C (pin-/funktionsgleich): GCT **USB4110-GF-A** — Footprint vor Swap prüfen.

---

## J_PWR — USB-C Pinbelegung (12401548E4#2A)

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

## PS1 — MP2359DJ Anschlüsse

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

Formel (Näherung): \( V_{OUT} \approx 0{,}6\,\text{V} \times (1 + R17/R18) \) — Werte laut **MP2359-Datenblatt** Tabelle 1 für **3,3 V**.

### Induktivität L1

Datenblatt: **1 µH … 10 µH**, Stromrating ≥ **1,5 A** (25 % über max. Last), **DCR < 200 mΩ**. Für 3,3 V / 1 A typisch **4,7 µH** (Tabelle 2).

---

## Netze

| Netz | Herkunft | Verbraucher |
|------|----------|-------------|
| **+5V** | J_PWR VBUS | F1, D12, C13, PS1 VIN |
| **+3V3** | PS1 via L1/C14 | U6, LEDs, Stecker, Entkopplung |
| **GND** | J_PWR, PS1, Passives | gemeinsame Masse |

Im Layout-Sheet: **`+3V3`** als globales Label oder `power:+3V3`-Symbol plus **PWR_FLAG** am Buck-Ausgang.

---

## KiCad — Bibliotheken und Pfade

| Artefakt | Pfad |
|----------|------|
| Symbolbibliothek | `pcb/Bauteile/Power/power.kicad_sym` |
| USB-C-Footprint | `pcb/Footprints/USB_C_Receptacle_Amphenol_12401548E4-2A.kicad_mod` |
| MP2359-Footprint | `pcb/Footprints/MP2359DJ.kicad_mod` |
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

1. [ ] Alle Power-Bauteile in `BasisStation_Layout.kicad_sch` platzieren und verdrahten
2. [ ] **F8** — PCB aus Schaltplan aktualisieren
3. [ ] VBUS/GND-Pads J_PWR vollständig routen
4. [ ] Buck-Bauteile dicht an PS1 layouten ( kurze Wege VIN, SW, GND )
5. [ ] ERC / DRC prüfen
6. [ ] BOM exportieren

---

## Pflege

Bei Änderungen an Schaltplan, BOM oder Teileauswahl diese Datei und den Kurzabschnitt in [hardware.md](hardware.md) aktualisieren.
