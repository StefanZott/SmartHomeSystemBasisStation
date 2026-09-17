---
type: analysis
created: 2026-09-08
jira: SHBS-4
status: draft
---

# KiCad-Stromversorgung — Statusanalyse (Fortsetzung von SHBS-4)

## Ausgangslage

Der Jira-Kommentar zu SHBS-4 (06.09.2026) referenziert einen Report
`tmp/report/2026-09-06_kicad-power-netz-analyse.md`. Diese Datei existiert im
aktuellen Checkout **nicht** — `tmp/` ist laut `.gitignore` nicht versioniert,
die Vorarbeit blieb also lokal auf einer anderen Maschine/Session und ist hier
nicht verfügbar. Diese Datei ersetzt den fehlenden Report auf Basis einer
Neuanalyse des aktuellen Repository-Stands (Commit `1d263fa`, sauberer
Working Tree bis auf `~BasisStation.kicad_sch.lck`).

**Wichtige Einschränkung dieser Umgebung:** Der Devcontainer (`.devcontainer/`)
enthält ausschließlich ESP-IDF-Tooling, kein KiCad/`kicad-cli`. Änderungen an
`.kicad_sch`-Dateien erfolgen als reine Text-/S-Expression-Edits ohne ERC- oder
Netzlisten-Verifikation. Der Bediener muss nach jedem Schritt in KiCad ERC
laufen lassen und die Netzliste neu erzeugen.

## Ergebnis / Befunde

### B9 — Projektbibliothek „power" verdeckt KiCad-Standardbibliothek

**Status hier: offen**, entgegen der Kommentar-Angabe „erledigt".

- `PCB/BasisStation/sym-lib-table` registriert `PCB/Bauteile/Power/power.kicad_sym`
  weiterhin unter dem Nickname `power` — identisch zum Nickname der
  KiCad-Standardbibliothek `power` (GND, PWR_FLAG, +3V3, +5V, …).
- Da projektlokale Einträge in KiCad globale Einträge gleichen Namens
  überschreiben, lösen sich alle 28× `power:GND` sowie `power:PWR_FLAG`,
  `power:+3V3` im Projekt nicht auf — das erklärt die ERC-Warnungen
  `lib_symbol_issues: Symbol "GND" nicht in Bibliothek "power" gefunden`.
- Betroffen von der eigentlichen Umbenennung sind nur die beiden Symbole, die
  tatsächlich aus der Projektbibliothek stammen: `PS1` (`power:MP2359DJ`) und
  `J_PWR1` (`power:USB_C_Receptacle_Power`), beide auf
  `Stromversorgung.kicad_sch`.

**Fix:** Nickname in `sym-lib-table` von `power` auf `shbs_power` ändern,
`lib_id` von `PS1`/`J_PWR1` (Instanz + Cache-Eintrag in `lib_symbols`)
nachziehen. Alle `power:GND`/`power:PWR_FLAG`/`power:+3V3`-Referenzen bleiben
unverändert und lösen sich danach gegen die KiCad-Standardbibliothek auf.

### B1 — `+3V3` als lokales statt globales Power-Label

**Status: offen, bestätigt.**

Drei Vorkommen, alle als einfaches `(label "+3V3" …)` (blattlokal):

| Blatt | Zeile |
|-------|-------|
| `Stromversorgung.kicad_sch` | 1919 |
| `BasisStation_Layout.kicad_sch` | 4616 |
| `BasisStation_Layout.kicad_sch` | 4636 |

Lokale Labels sind blattlokal — der Buck-Ausgang auf `Stromversorgung.kicad_sch`
erreicht `U6` auf `BasisStation_Layout.kicad_sch` dadurch nicht (ERC:
`power_pin_not_driven` an U6 Pin 2). Fix: durch `power:+3V3`-Symbol
(globales Power-Symbol) ersetzen — voraussetzt B9, damit `power:+3V3` aus der
Standardbibliothek auflösbar ist.

### B3 — Kein PWR_FLAG vorhanden

**Status: offen, Umfang größer als im Kommentar beschrieben.**

Der Kommentar nennt „4x im Layout, 0x auf Stromversorgung". Tatsächlich ist in
keinem Blatt eine PWR_FLAG-**Instanz** platziert — in
`BasisStation_Layout.kicad_sch` existiert nur ein verwaister
`lib_symbols`-Cache-Eintrag (Zeilen 3317–3402) ohne zugehörige Platzierung.
Die Zahl „4x" ließ sich aus dem reinen Textstand nicht nachvollziehen
(vermutlich Zählung aus einer KiCad-UI-Ansicht der vorherigen Session, die
hier nicht verfügbar ist).

ERC-Fehler `power_pin_not_driven` an PS1 Pin 5 (VIN) und J_PWR1 Pin A4 (VBUS)
bestehen, weil USB-C-Buchse (Power-Input-Pins) allein keinen Power-Output
treibt. Fix: `PWR_FLAG`-Symbol an VBUS (hinter F1, vor PS1 VIN) und am
3,3-V-Ausgangsnetz platzieren.

**Risikohinweis:** Platzierung erfolgt hier per Text-Edit anhand vorhandener
Wire-Endpunkt-Koordinaten, ohne visuelle/elektrische Verifikation. ERC-Lauf in
KiCad durch den Bediener zwingend erforderlich.

### Nicht betroffen (aus Kommentar bestätigt)

`PW_EN` (Enable MP2359) und `/Layout/EN` (Chip-Enable/Reset ESP32: R9, C7,
S2, J6, U6 Pin 3) sind unterschiedliche Signale und dürfen nicht
zusammengelegt werden — sonst würde der Reset-Taster S2 die eigene
Versorgung abschalten.

### Weitere offene Punkte

- **C8 Pin 1 unverbunden** (`BasisStation_Layout.kicad_sch`) — noch nicht
  untersucht in dieser Session, folgt als eigener Task.
- **`BasisStation.net` veraltet** — Export-Datum `2026-06-09`, liegt vor dem
  USB-C-Umbau (Commit `b89eb9c`, 29.08.2026). Enthält noch `PS2`/`+12V`.
  `BasisStation.kicad_pcb` ist ebenfalls älter als der aktuelle Schaltplan.
  Neuerzeugung der Netzliste und PCB-Abgleich sind Aufgabe des Bedieners in
  KiCad, nachdem B1/B3 gefixt sind (Abhängigkeit aus dem Ticket-Kommentar).

## Nachtrag 2026-09-08 (nach ERC-Lauf des Bedieners)

### Wirkung der Fixes B9 + B1

ERC vor den Änderungen: **53 Meldungen** (5 Fehler, 48 Warnungen).
ERC danach: **29 Meldungen** (6 Fehler, 23 Warnungen).

- Alle 28 Warnungen `Symbol "GND" nicht in Bibliothek "power" gefunden`
  sind entfallen (B9 wirkt).
- Der Fehler `[unannotated] J_PWR?` ist entfallen.
- Neu: 3× Warnung `lib_symbol_mismatch: Symbol "+3V3" stimmt nicht mit Kopie
  in Bibliothek "power" überein` — die hier per Text-Edit erzeugte
  Cache-Definition weicht geometrisch von der KiCad-Originaldefinition ab.
  **Behebung:** in KiCad *Werkzeuge → Symbole aus Bibliothek aktualisieren*.
  Rein kosmetisch, elektrisch ohne Wirkung.
- Neu und inzwischen behoben: `#PWR100` lag auf der Drahtmitte statt auf dem
  Drahtende (185,42 mm statt 190,5 mm). Ein Label darf mitten auf einem Draht
  sitzen, ein Symbolpin nicht. `#PWR100` wurde auf den freien Drahtendpunkt
  (190,5 / 138,43) verschoben — gleicher Draht, damit unverändertes Netz.

### Kritischer Befund: Buck-Ausgangszweig ist falsch verdrahtet

Aus der Geometrie rekonstruierte Ist-Netzliste (Pin-Transformation an den
ERC-Koordinaten kalibriert, 48/48 Pins liegen exakt auf Drahtendpunkten):

| Knoten | Ist-Verbindungen |
| ------ | ---------------- |
| A | `PS1.6 (SW)`, `PS1.1 (BST)`, `L1.1`, `C14.1`, `C15.2`, `R17.1`, `#PWR100 (+3V3)` |
| B | `L1.2`, `D11.2 (A = Anode)` |
| GND | `D11.1 (K = Kathode)`, `C14.2`, `C15.1`, `PS1.2` |
| FB | `PS1.3 (FB)`, `R17.2`, `R18.2` ✔ korrekt |
| VIN | `PS1.5 (VIN)`, `F1.1`, `C13.2`, `D12.1` ✔ korrekt |

Soll laut [power_supply.md](../../docs/project/power_supply.md) (Zeilen 62–68, 158–164):

- SW-Knoten: `PS1.6`, `L1.1`, `D11` **Kathode**, `C15` (eine Seite)
- BST-Knoten: `PS1.1`, `C15` (andere Seite)
- Ausgang +3V3: `L1.2`, `C14.1`, `R17.1`
- GND: `D11` **Anode**, `C14.2`

**Abweichungen:**

1. **D11 ist verpolt und am falschen Knoten.** Ist: Anode an `L1.2`,
   Kathode an GND. Damit liegt die Schottky-Diode in Durchlassrichtung vom
   Ausgang nach GND — sie würde die Ausgangsspannung kurzschließen.
   Soll: Kathode an SW, Anode an GND.
2. **C15 (Bootstrap, 100 nF) liegt gegen GND** statt zwischen `BST` und `SW`.
3. **`BST` (PS1.1) ist direkt mit `SW` (PS1.6) verbunden**, ohne Kondensator.
   Der MP2359 kann sein High-Side-Gate so nicht treiben.
4. **`C14` (22 µF) und `R17` (FB-Teiler oben) hängen am SW-Knoten** statt am
   geglätteten Ausgang hinter `L1`. Die Regelung würde auf den Schaltknoten
   regeln, die Ausgangsglättung fehlt.
5. **`L1` liegt nicht im Ausgangspfad**, sondern zwischen SW-Knoten und Diode.
6. **`+3V3` (ursprüngliches Label, jetzt `#PWR100`) liegt am SW-Knoten**,
   nicht am Ausgang.

**Konsequenz für B3 (PWR_FLAG):** Ein PWR_FLAG am derzeitigen „+3V3"-Netz
würde ein Flag auf den Schaltknoten setzen und die ERC-Fehler kosmetisch
verdecken, ohne die Schaltung zu korrigieren. B3 ist deshalb **blockiert**,
bis die Topologie korrigiert ist (Task 0005).

**Umsetzungsempfehlung:** Die Umverdrahtung in der KiCad-GUI durchführen,
nicht per Text-Edit — `power_supply.md` Zeile 86 hält bereits fest, dass
skriptgestütztes Einfügen von Power-Teilen KiCad zum Absturz gebracht hat.
Nach der Korrektur sind zusätzlich **zwei** PWR_FLAGs nötig (nicht eines):
je eines vor und hinter `F1`, da die Sicherung passiv ist und KiCad Leistung
nicht durch passive Bauteile verfolgt.

### C8 Pin 1 (Layout-Blatt) — behoben

Ursache war ein Rasterversatz: `C8` Pin 1 liegt bei (66,04 / 25,40), der
zugehörige Draht endete bei (66,04 / 22,86) — exakt **2,54 mm** (ein
100-mil-Raster) daneben. Zielnetz ist die 3,3-V-Versorgung des ESP32
(`U6.2`, `C10.1`, `C12.1`, `J6.2`, `R9.1`), `C8` ist Stützkondensator.
Fix: Drahtsegment (66,04 / 22,86) → (66,04 / 25,40) eingefügt, Zugehörigkeit
per Netzrekonstruktion verifiziert.

### Methodenhinweis / Selbstkorrektur

Die Pin-Transformation wurde an zwei ERC-Koordinaten kalibriert
(`PS1.5`, `J_PWR1.A4`, beide Rotation 0) und ergab 48/48 Treffer auf
Drahtendpunkten. Dieser Test war jedoch **blind für Rotation 90/270**: Bei
symmetrischen Zweipolen (R, C, L, Sicherung) liefern die vertauschten
Formeln dieselben Punkte, nur die Pin-Nummern tauschen. Aufgefallen ist es
an der ERC-Koordinate von `C8` (Rotation 90).

Korrekte Formeln (Symbolkoordinate → Blattkoordinate, Delta zum
Symbolursprung): 0° → `(px, -py)`, 90° → `(-py, -px)`, 180° → `(-px, py)`,
270° → `(py, px)`.

Auswirkung auf die Befunde: **keine.** Betroffen waren nur `L1`, `C14`, `F1`
(symmetrisch) und `D12` (Symbol `SMAJ5.0A` mit Pins `A1`/`A2`, bidirektional).
`D11` hat Rotation 180 und ist daher nicht betroffen — der Polaritätsbefund
bleibt gültig. Die Netzzugehörigkeiten waren ohnehin unabhängig davon korrekt.

### Stand nach zweitem ERC-Lauf (14:39) und KiCad-Speicherung

ERC: **14 Meldungen** (4 Fehler, 10 Warnungen), vorher 29 / davor 53.

Entfallen: `pin_not_connected` an C8 und an `#PWR100`, beide zugehörigen
`unconnected_wire_endpoint`, sämtliche `lib_symbol_mismatch` (auch die drei
zu `+3V3`). `report.txt` bestätigt: `#PWR100`–`#PWR102` (`power:+3V3`), `PS1`
(`shbs_power:MP2359DJ`) und `J_PWR1` (`shbs_power:USB_C_Receptacle_Power`)
aktualisieren mit **OK**. KiCad hat beim Speichern die hier per Text-Edit
erzeugte `+3V3`-Cache-Definition durch das Original ersetzt (andere
Referenz-Position, Pfeil aus zwei Polylines) und die `lib_symbols`
alphabetisch sortiert. CRLF und alle Änderungen sind erhalten, alle drei
Schaltpläne parsen sauber.

**Verbleibende 4 Fehler** — alle `power_pin_not_driven`, alle abhängig von
Task 0005/0003: `U6.2 (3V3)`, `PS1.5 (VIN)`, `J_PWR1.A4 (VBUS)`, `#PWR100`.

### Zwei offene Drahtenden (Warnungen, vorbestehend)

| Draht | Netz |
| ----- | ---- |
| (85,09 / 53,34) → (95,25 / 53,34) | EN-Netz: `C7.1`, `R9.2`, `S2.2`, `U6.3` |
| (240,03 / 22,86) → (248,92 / 22,86) | 3,3 V: `C8.1`, `C10.1`, `C12.1`, `J6.2`, `R9.1`, `U6.2` |

Beide enden im Nichts — kein Pin im Umkreis von 5 mm, also **kein**
Rasterversatz wie bei C8. Beide existierten bereits vor dem USB-C-Umbau
(`b89eb9c^`), sind also keine Altlast aus dem PS2-Ausbau.

Entscheidung offen (Bediener): Löschen ändert die Netzliste nicht — an den
freien Enden hängt nichts, die Netze bleiben über die Junctions erhalten.
Falls dort Anschlusspunkte vorgesehen sind, sollten sie bestückt oder
dokumentiert werden.

## Empfehlungen

1. B9 und B1 als risikoarme, mechanische Text-Edits umsetzen (Tasks 0001/0002).
2. B3 als Text-Edit versuchen, aber mit expliziter Kennzeichnung "vor ERC-Lauf
   verifizieren" (Task 0003).
3. C8 gesondert untersuchen (Task 0004), ggf. ohne Fix hier, falls die Ursache
   nicht eindeutig aus dem Text hervorgeht.
4. Nach allen Fixes: Bediener führt ERC + Netzliste-Neuerzeugung in KiCad aus,
   aktualisiert `BasisStation.net` und gleicht `BasisStation.kicad_pcb` ab.

## Nächste Schritte

Siehe `tmp/tasks/open/0001…0004_*.md`.
