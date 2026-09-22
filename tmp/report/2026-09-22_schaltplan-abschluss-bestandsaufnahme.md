---
type: analysis
created: 2026-09-22
status: draft
---

# Schaltplan-Abschluss: Bestandsaufnahme

## Ausgangslage

Der Bediener will den Schaltplan vollstaendig abschliessen, bevor das
PCB-Layout begonnen wird. Diese Analyse erfasst, was dafuer noch offen ist.

Werkzeug: `kicad-cli` 9.0.9 im Dev-Container (SHBS-13). Geprueft wurden ERC,
Netzliste, Stueckliste, Symbolbibliotheken und die Projekteinstellungen.

## Ergebnis / Befunde

### Gesamtbild: der Schaltplan ist elektrisch fertig

| Pruefung | Ergebnis |
| -------- | -------- |
| ERC | **0 Fehler**, 7 Warnungen |
| Netze | 102, davon 0 ohne Pin |
| Bauteile | 76 auf dem Board, alle mit Footprint |
| Werte | vollstaendig gesetzt |
| ERC-Schweregrade | KiCad-Standard, **keine Ausnahmen** hinterlegt |

Die 4 auf `ignore` gesetzten ERC-Regeln (`footprint_filter`,
`four_way_junction`, `simulation_model_issue`, `single_global_label`) sind
KiCad-9-Standardwerte. Es wurde nichts unterdrueckt, um Probleme zu
verstecken — die Null bei den Fehlern ist belastbar.

Alle 40 Ein-Pin-Netze tragen den automatisch vergebenen Namen
`unconnected-*`, sind also bewusst unbeschaltete Pins (freie GPIOs an `U6`,
NC/RSVD an `U7`, `SBU1`/`SBU2` an `J1`). Kein einziges regulaer benanntes Netz
haengt in der Luft.

### Die 7 ERC-Warnungen im Einzelnen

**A — 4x `lib_symbol_mismatch` (`S2`, `C7`, `C10`, `C12`)**

Ursache gefunden: Die Bibliotheken `1543-650-149` und `WCAP-FTXX_P10` liegen
noch im **KiCad-6-Dateiformat** (`version 20211014`), der Symbol-Cache im
Schaltplan dagegen im KiCad-9-Format. Ein Vergleich der beiden Fassungen
zeigt ausschliesslich Formatunterschiede — `(id N)` in den Properties,
`hide` statt `(hide yes)`, fehlendes `exclude_from_sim`/`embedded_fonts`,
`Description` statt `Description_1`. **Pins und Geometrie sind identisch**,
elektrisch aendert sich nichts.

Betroffen vom alten Format sind insgesamt sechs Bibliotheken:

| Bibliothek | Format | Meldet aktuell Mismatch |
| ---------- | ------ | ----------------------- |
| `1543-650-149` | 20211014 (v6) | ja (`S2`) |
| `WCAP-FTXX_P10` | 20211014 (v6) | ja (`C7`, `C10`, `C12`) |
| `WCAP-PT5H_6.3X5.2` | 20211014 (v6) | nein |
| `WL-TMRC_3MM` | 20211014 (v6) | nein |
| `wuerth_7499011121A` | 20220914 (v7) | nein |
| `wuerth_830059532` | 20220914 (v7) | nein |

Testlauf mit `kicad-cli sym upgrade --force` auf `WCAP-FTXX_P10`: das Ergebnis
deckt sich bis auf drei Restpunkte mit dem Cache im Schaltplan — das
`Footprint`-Feld (Cache leer, Bibliothek gefuellt), ein `justify bottom` und
umgebrochene Zeilenumbrueche im `Description_1`. Der Upgrade allein raeumt die
Warnung also **nicht** ab; der Cache im Schaltplan muss zusaetzlich aus der
Bibliothek aufgefrischt werden (GUI: *Werkzeuge > Symbole aus Bibliothek
aktualisieren*). Dabei darf das Footprint-Feld **nicht** ueberschrieben
werden, weil die Zuweisungen pro Instanz gewollt sind.

**B — 1x `unconnected_wire_endpoint`** in `BasisStation_Layout.kicad_sch`

Am Netz `EN` haengt ein Leitungsstummel: Die Leitung laeuft von
(52,07 / 55,88) nach (62,23 / 55,88), das Label `EN` sitzt bei
(59,69 / 55,88). Die letzten 2,54 mm stehen ins Leere. Rein kosmetisch,
elektrisch folgenlos — als Textaenderung korrigierbar (Endpunkt auf die
Label-Position ziehen).

**C — 1x `pin_to_pin`: `S2` Pin 1 (Bidirectional) + `#FLG04` (Power output)**

Das ist das GND-`PWR_FLAG`, das in Task 0003 (SHBS-6) bewusst gesetzt wurde,
nachdem mit dem Wechsel von `USB_B_Micro` auf `USB_C_Receptacle` der einzige
ERC-Treiber des GND-Netzes entfallen war. Verhalten by design.

**D — 1x `multiple_net_names`: GND und EPAD an `U6`**

Der versteckte Pin 41 (`EPAD`) des ESP32-S3-Moduls traegt einen eigenen
Netznamen und liegt auf GND. KiCad nimmt GND in die Netzliste — korrekt.
Verhalten by design.

### Weitere Befunde (ausserhalb der ERC)

**E — verwaiste Schaltplan-Datei**

`pcb/BasisStation/BasisStation_architektur.kicad_sch` (1271 Zeilen) ist in
der Hierarchie **nicht referenziert**. Die Datei wurde zuletzt bei der
Verzeichnis-Umbenennung (`27de25b`, SHBS-1) mitgenommen. Sie geht weder in
ERC noch in Netzliste oder Stueckliste ein. Zu klaeren: Altlast (loeschen)
oder bewusst aufgehobener Entwurf (dann als solcher kennzeichnen).

**F — Zeilenenden `ethernet.kicad_sch`**

Die Datei steht im Arbeitsverzeichnis als geaendert, der Diff enthaelt
**keine inhaltliche Aenderung** — nur CRLF gegen LF. Alle sechs
Schaltplan-Dateien sind im Arbeitsverzeichnis CRLF (KiCad unter Windows);
`.gitattributes` normalisiert auf LF. Bei `ethernet.kicad_sch` liegt noch
eine CRLF-Fassung im Index. Ein `git add` normalisiert das einmalig.

**G — offene Detailfrage `U7` Pin 18 (`VBG`)**

Der Bandgap-Pin des W5500 ist unbeschaltet. In den WIZnet-Referenzdesigns ist
das ueblich, sollte vor dem Layout aber einmal gegen das Datenblatt
gegengeprueft werden — im Layout ist es nachtraeglich teurer.

**H — `R35` (0 Ohm) ist als DNP markiert**

Bewusst? Falls der Bestueckungsausschluss nicht mehr gewollt ist, jetzt
klaeren — die Stueckliste fuer die Fertigung haengt daran.

## Empfehlungen

Einzig **A** und **B** sind echte Restarbeiten am Schaltplan; **C** und **D**
sind gewolltes Verhalten und sollten als ERC-Ausnahme dokumentiert werden,
damit kuenftige Laeufe eine saubere Null zeigen. **E**–**H** sind
Klaerungen, keine Konstruktionsfehler.

Reihenfolge:

1. **A** — sechs Bibliotheken per `kicad-cli sym upgrade` auf v9 heben
   (Agent), danach Symbol-Cache in der GUI auffrischen (Bediener).
2. **B** — Leitungsstummel am `EN`-Netz kuerzen (Agent, Textaenderung).
3. **C**/**D** — als ERC-Ausnahme im Projekt hinterlegen, mit Begruendung in
   `docs/project/hardware.md` (Bediener in der GUI, da Ausnahmen an
   UUIDs haengen).
4. **E**–**H** — Entscheidungen des Bedieners einholen.
5. Abschluss-ERC: Ziel **0 Fehler, 0 Warnungen**.

## Naechste Schritte

Nach Freigabe: Jira-Ticket anlegen, Tasks unter `tmp/tasks/open/` erzeugen.
Erst danach beginnt das PCB-Layout — die Netzliste wird dann genau einmal
ins Board uebernommen.
