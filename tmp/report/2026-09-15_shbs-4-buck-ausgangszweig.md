---
type: investigation
created: 2026-09-15
jira: SHBS-4
status: final
---

# Buck-Ausgangszweig MP2359 — Ist/Soll-Verdrahtung (Befund B12)

## Ausgangslage

Nach Behebung von B1, B3, B9, B10, B11 und C8 meldet der ERC-Lauf vom
2026-09-15 21:43 noch **einen** Fehler:

```
[pin_to_pin] Pins vom Typ Output und Power output sind verbunden ; error
    Symbol PS1 Pin 6 [SW, Output, Line]
    Symbol #FLG03 Pin 1 [Power output, Line]
```

Dieser Fehler ist ein Symptom, keine Ursache. Der Ausgangszweig des
MP2359-Buckwandlers in `pcb/BasisStation/Stromversorgung.kicad_sch` ist
falsch verdrahtet. Der Bericht hält die vollständige Ist-Verdrahtung fest,
damit die Korrektur in der KiCad-GUI zielgerichtet erfolgen kann.

Methode: Pinpositionen aus den eingebetteten `lib_symbols` mit der
Platzierungstransformation (`at`, Rotation, Spiegelung) in Blattkoordinaten
umgerechnet und gegen alle 48 Drahtsegmente geschnitten.

## Ergebnis / Befunde

### Der Knoten `SW` schluckt den halben Ausgangszweig

Alle folgenden Pins liegen auf **einem** Netz — dem Schaltknoten `SW`:

| Pin | Position (mm) | Soll-Netz |
| --- | ------------- | --------- |
| `PS1.6` (SW, Output) | 158,75 / 86,36 | SW ✅ |
| `PS1.1` (BST, Input) | 138,43 / 83,82 | **BST** |
| `C15.2` | 147,32 / 113,03 | SW ✅ |
| `L1.2` | 177,8 / 113,03 | SW ✅ |
| `C14.2` | 182,88 / 129,54 | **GND** |
| `R17.1` | 124,46 / 101,6 | **VOUT** |
| `#PWR100` (`+3V3`) | 190,5 / 138,43 | **VOUT** |
| `#FLG03` (PWR_FLAG) | 181,61 / 143,51 | **VOUT** |

Die Verbindung `PS1.1` → SW entsteht über den Draht
(138,43 / 83,82) → (109,22 / 83,82) → (109,22 / 113,03) und dort in die
horizontale Schiene bei y = 113,03.

### Hinter `L1` hängt nichts als die Diode

| Pin | Position (mm) | Ist |
| --- | ------------- | --- |
| `L1.1` | 185,42 / 113,03 | nur `D11.2` |
| `D11.2` (A, Anode) | 191,77 / 113,03 | `L1.1` |
| `D11.1` (K, Kathode) | 199,39 / 113,03 | GND (`#PWR013`) |

Der eigentliche Ausgangsknoten **existiert nicht**. Was als `+3V3` benannt
ist, ist elektrisch `SW`.

### Vier konkrete Defekte

1. **`D11` verpolt und am falschen Knoten.** Anode am Induktivitätsausgang,
   Kathode an GND. In dieser Lage leitet die Schottky-Diode vom Ausgang nach
   GND — Dauerkurzschluss, sobald der Wandler anläuft.
   *Soll:* Kathode an `SW`, Anode an GND.
2. **`C15` liegt gegen GND** (Pin 1 → `#PWR011`), statt zwischen `BST` und `SW`.
3. **`BST` liegt direkt auf `SW`.** Ohne Bootstrap-Kondensator kann der
   MP2359 sein High-Side-Gate nicht treiben — der Wandler schaltet nicht.
4. **`C14` und `R17` hängen am Schaltknoten.** Die Ausgangsglättung fehlt,
   und der Feedback-Teiler regelt auf die ungeglättete Rechteckspannung.

Der Spannungsteiler selbst ist korrekt aufgebaut: `R17.2` und `R18.2` treffen
sich mit `PS1.3` (FB) bei y = 86,36, `R18.1` geht auf GND. Nur sein oberer
Abgriff sitzt am falschen Knoten.

## Empfehlungen

Ziel-Topologie (asynchroner Buck, MP2359-Datenblatt):

```
PS1.6 SW ──┬── C15 ── PS1.1 BST
           ├── D11 Kathode (Anode → GND)
           └── L1 ──┬── C14 ── GND
                    ├── R17 ── FB ── R18 ── GND
                    └── +3V3  (#PWR100, #FLG03)
```

Daraus die Soll-Netze:

| Netz | Pins |
| ---- | ---- |
| `SW` | `PS1.6`, `C15.2`, `D11.1` (K), `L1.2` |
| `BST` | `PS1.1`, `C15.1` |
| `VOUT` = `+3V3` | `L1.1`, `C14.1`, `R17.1`, `#PWR100`, `#FLG03` |
| `GND` | `D11.2` (A), `C14.2`, `R18.1`, `PS1.2` |
| `FB` | `PS1.3`, `R17.2`, `R18.2` (bereits korrekt) |

Umsetzung **in der KiCad-GUI**, nicht per Skript: der Eingriff verschiebt ein
Bauteil und ersetzt rund zehn Drahtsegmente. Ein Skript könnte das erzeugen,
das Ergebnis wäre aber visuell nicht mehr nachvollziehbar prüfbar — und bei
einem Topologiefehler ist genau die Sichtprüfung der Punkt.

Alle Koordinaten in mm, Blatt `Stromversorgung.kicad_sch`. Raster **1,27 mm**
einstellen, sonst rasten die Punkte nicht ein. Der Stand vor dem Eingriff ist
mit Commit `5cc0191` gesichert — bei einem Fehlgriff `git checkout` darauf.

### Schritt 1 — Löschen (8 Elemente)

Jeweils anklicken und `Entf`.

| # | Element | Von | Bis | Warum |
| - | ------- | --- | --- | ----- |
| L1 | Draht | 172,72 / 113,03 | 172,72 / 129,54 | Trunk, verbindet SW mit C14 |
| L2 | Draht | 172,72 / 129,54 | 182,88 / 129,54 | zu C14 Pin 2 |
| L3 | Draht | 172,72 / 129,54 | 172,72 / 138,43 | Trunk zur `+3V3`-Schiene |
| L4 | Draht | 109,22 / 113,03 | 147,32 / 113,03 | zieht BST auf die SW-Schiene |
| L5 | Draht | 147,32 / 120,65 | 147,32 / 125,73 | C15 gegen GND |
| L6 | GND-Symbol `#PWR011` | 147,32 / 125,73 | — | gehört zu L5 |
| L7 | Draht | 185,42 / 113,03 | 191,77 / 113,03 | L1-Ausgang zur D11-Anode |
| L8 | Draht | 199,39 / 113,03 | 204,47 / 113,03 | D11-Kathode nach GND |

Nach L1–L3 verschwindet der Knoten bei 172,72 / 129,54 vollständig. Die
`+3V3`-Schiene bei y = 138,43 (mit `R17`, `#PWR100`, `#FLG03`) hängt jetzt
frei — das ist beabsichtigt, sie wird in Schritt 4 zum Ausgangsknoten.

### Schritt 2 — `D11` an den Schaltknoten setzen

`D11` anklicken, `M` (verschieben), **einmal `R`** (dreht gegen den
Uhrzeigersinn: Kathode zeigt danach nach oben), absetzen bei:

| Pin | Ziel |
| --- | ---- |
| Kathode (`K`, Pin 1) | **160,02 / 113,03** — auf der SW-Schiene |
| Anode (`A`, Pin 2) | 160,02 / 120,65 |

Das freigewordene GND-Symbol `#PWR013` (204,47 / 113,03) nach
**160,02 / 123,19** verschieben und mit einem Draht an die Anode hängen
(N3 unten). Position ist frei: `C15` sitzt bei x = 147,32, der Trunk bei
x = 172,72.

### Schritt 3 — `C15` als Bootstrap zwischen BST und SW

`C15` bleibt, wo es ist. Pin 2 (oben, 147,32 / 113,03) liegt bereits auf der
SW-Schiene. Pin 1 (unten) bekommt eine Leitung zu `BST` — der Draht von
`PS1.1` nach unten existiert noch und endet nach L4 frei bei 109,22 / 113,03.

### Schritt 4 — Ausgangsknoten hinter `L1` bilden

Der neue Pfad führt links an `C14` vorbei nach unten auf die `+3V3`-Schiene.

### Neue Drähte (7 Segmente)

| # | Von | Bis | Netz |
| - | --- | --- | ---- |
| N1 | 147,32 / 120,65 | 109,22 / 120,65 | BST |
| N2 | 109,22 / 120,65 | 109,22 / 113,03 | BST (an den `PS1.1`-Draht) |
| N3 | 160,02 / 120,65 | 160,02 / 123,19 | GND (D11-Anode) |
| N4 | 185,42 / 113,03 | 185,42 / 116,84 | VOUT (aus `L1` Pin 1) |
| N5 | 185,42 / 116,84 | 182,88 / 116,84 | VOUT (links an `C14` vorbei) |
| N6 | 182,88 / 116,84 | 182,88 / 129,54 | VOUT (an `C14` Pin 2) |
| N7 | 182,88 / 129,54 | 182,88 / 138,43 | VOUT (auf die `+3V3`-Schiene) |

N5 liegt bei y = 116,84 knapp **unter** dem `L1`-Symbolkörper, N6 bei
x = 182,88 knapp **links** vom `C14`-Körper — beide Wege sind frei.

### Schritt 5 — Junctions prüfen

Punkte, an denen ein Pin oder Drahtende mitten auf einem Draht landet.
KiCad setzt den Punkt meist automatisch; fehlt er, mit `J` nachsetzen:

- **160,02 / 113,03** — D11-Kathode auf der SW-Schiene
- **182,88 / 129,54** — `C14` Pin 2 zwischen N6 und N7
- **182,88 / 138,43** — N7 trifft die `+3V3`-Schiene

### Soll-Ergebnis zur Kontrolle

Netzliste (Werkzeuge → Netzliste erzeugen) oder Hover über die Netze:

| Netz | Pins |
| ---- | ---- |
| `SW` | `PS1.6`, `C15.2`, `D11.1` (K), `L1.2` |
| `BST` | `PS1.1`, `C15.1` |
| `+3V3` | `L1.1`, `C14.2`, `R17.1`, `#PWR100`, `#FLG03` |
| `GND` | `D11.2` (A), `C14.1`, `R18.1`, `PS1.2` |
| `FB` | `PS1.3`, `R17.2`, `R18.2` — unverändert |

Danach ERC: der `pin_to_pin`-Fehler an `PS1.6`/`#FLG03` muss entfallen, weil
`#FLG03` dann auf `+3V3` liegt und dort kein Pin vom Typ *Output* mehr sitzt.
Erwartet: **0 Fehler**, 9 unkritische Warnungen.

### Optional, rein kosmetisch

`C14` ist als `Device:C` unpolarisiert — die Zuordnung Pin 1 = GND,
Pin 2 = `+3V3` ist elektrisch einwandfrei. Wird später ein polarisierter Typ
eingesetzt, das Symbol um 180° drehen, damit Pin 1 am Pluspol liegt.

## Ergebnis (2026-09-15 22:27)

Korrektur in der KiCad-GUI durchgeführt. Netzprüfung aus der Schaltplandatei:

| Netz | Pins | Status |
| ---- | ---- | ------ |
| `SW` | `PS1.6`, `C15.2`, `D11.1` (K), `L1.2` | wie geplant |
| `BST` | `PS1.1`, `C15.1` | wie geplant |
| `+3V3` | `L1.1`, `C14.2`, `R17.1`, `#PWR100`, `#FLG03` | wie geplant |
| `GND` | `D11.2` (A) über `#PWR013`, `C14.1`, `R18.1`, `PS1.2` | wie geplant |
| `FB` | `PS1.3`, `R17.2`, `R18.2` | unverändert |

Kein unverbundener Pin im Power-Zweig. **ERC: 0 Fehler, 9 unkritische
Warnungen.**

Abweichungen von den vorgeschlagenen Koordinaten (D11 bei 165,10 statt
160,02; `C15`-Anbindung anders geroutet) sind elektrisch ohne Belang — die
Netze sind identisch.

## Nächste Schritte

1. B12 gemäß obiger Liste korrigieren.
2. ERC gegenprüfen (erwartet: 0 Fehler, 9 unkritische Warnungen).
3. Netzliste `BasisStation.net` neu exportieren — der aktuelle Stand ist vom
   2026-06-09 und enthält noch `PS2` und `+12V`.
4. PCB nachziehen (F8), Power-Bauteile platzieren, DRC.

Footprints für `F1` und `R17`–`R20` (Befund B13) sind am 2026-09-15
zugewiesen und blockieren Schritt 3 nicht mehr.

## Verifikation (2026-09-19)

Unabhängig nachgerechnet, ohne auf den Eintrag vom 2026-09-15 zu vertrauen:
Pinkoordinaten erneut aus den `lib_symbols` mit Platzierungstransformation
(`at`, Rotation, `mirror`) in Blattkoordinaten umgerechnet, gegen alle
Drahtsegmente geschnitten, inklusive T-Verbindungen. Ergebnis identisch zur
Soll-Tabelle — alle fünf Netze (`SW`, `BST`, `+3V3`, `GND`, `FB`) stimmen,
alle sechs `PS1`-Pins sind belegt.

ERC-Stand `pcb/BasisStation/ERC.rpt` (Lauf 2026-09-18 23:42):
**0 Fehler, 7 Warnungen.** Das Blatt `/Stromversorgung/` erzeugt keine
einzige Meldung. Der frühere `pin_to_pin`-Fehler `PS1.6` ↔ `#FLG03` ist
entfallen.

**Befund B12 ist damit geschlossen.** Tasks `0005_shbs4-buck-topologie-korrektur`
und der davon blockierte `0003_shbs4-b3-pwrflag-platzierung` liegen in
`tmp/tasks/done/`.

### Nebenbefund — Netznamen der Eingangsseite

Bei der Rekonstruktion fiel auf, dass die 5-V-Schiene hinter `F1` im
Schaltplan das globale Label **`PW_EN`** trägt, nicht `+5V` wie in
`docs/project/power_supply.md` beschrieben. Ursache: `PS1.4` (EN) ist über
dasselbe Label an VIN gelegt, statt über einen Draht. Elektrisch ist das die
dokumentierte Absicht (Wandler dauerhaft aktiv), der Netzname beschreibt aber
den Enable-Pin statt der Leistungsschiene. Das VBUS-Netz vor `F1` ist
unbenannt.

Empfehlung: Schiene hinter `F1` in `+5V` umbenennen, EN separat als
kurzes Label `PW_EN` oder direkt per Draht an VIN führen, und vor `F1` ein
Label `VBUS` setzen. Rein kosmetisch — Topologie und ERC bleiben unberührt,
aber Netzliste, Routing-Ansicht und BOM werden lesbar. In
`power_supply.md`, Abschnitt „Netze", als Restposten festgehalten.
