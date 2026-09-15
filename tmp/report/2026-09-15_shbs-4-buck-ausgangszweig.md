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

Umsetzung **in der KiCad-GUI**, nicht per Skript: der Eingriff verschiebt
Bauteile (`D11` um 180° drehen und an `SW` setzen, `C15` zwischen BST und SW
umhängen) und ersetzt rund 15 Drahtsegmente. Ein Skript könnte das zwar
erzeugen, das Ergebnis wäre aber visuell nicht mehr nachvollziehbar
prüfbar — und automatisches Einfügen hat in diesem Projekt bereits einmal
KiCad zum Absturz gebracht (2026-06-08).

Konkrete Schritte:

1. Draht (138,43 / 83,82) → (109,22 / 83,82) → (109,22 / 113,03) **löschen**
   (verbindet BST fälschlich mit SW).
2. `C15` zwischen `PS1.1` (BST) und die SW-Schiene setzen; GND-Symbol
   `#PWR011` entfernen.
3. `D11` um 180° drehen, Kathode an die SW-Schiene, Anode an GND.
4. Die Schiene bei y = 113,03 **hinter `L1` auftrennen**: `L1.1` wird zum
   neuen Ausgangsknoten.
5. `C14.2` auf GND legen, `C14.1` an den Ausgangsknoten; `R17.1`,
   `#PWR100` und `#FLG03` ebenfalls an den Ausgangsknoten führen.
6. ERC — der `pin_to_pin`-Fehler muss entfallen.

## Nächste Schritte

1. B12 gemäß obiger Liste korrigieren.
2. ERC gegenprüfen (erwartet: 0 Fehler, 9 unkritische Warnungen).
3. Netzliste `BasisStation.net` neu exportieren — der aktuelle Stand ist vom
   2026-06-09 und enthält noch `PS2` und `+12V`.
4. PCB nachziehen (F8), Power-Bauteile platzieren, DRC.

Footprints für `F1` und `R17`–`R20` (Befund B13) sind am 2026-09-15
zugewiesen und blockieren Schritt 3 nicht mehr.
