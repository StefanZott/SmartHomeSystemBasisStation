---
title: Stueckliste reproduzierbar erzeugen und mit Mouser-Daten anreichern
created: 2026-09-22
jira: SHBS-15
priority: high
type: feature
---

## Kontext

Der erste Stuecklisten-Export ([2026-09-22_stueckliste-basisstation.xlsx](../../report/2026-09-22_stueckliste-basisstation.xlsx),
Commit `5877d96`) entstand ad hoc; ein Skript dazu existiert nicht. Die Spalten
Mouser-Teilenummer und Einzelpreis blieben leer, weil zu dem Zeitpunkt kein
API-Schluessel vorlag. Seit Task 0038 sind Schluessel, LibreOffice und
`openpyxl` im Container verfuegbar.

Bei der Bestandsaufnahme fuer diesen Task kam ein Befund dazu, den der erste
Export uebersehen hat: **Teilenummern liegen im Schaltplan unter
uneinheitlichen Feldnamen**, je nachdem woher das Symbol stammt
(SnapEDA, Wuerth-Generator, handgepflegt):

| Bedeutung | Vorkommende Feldnamen |
| --------- | --------------------- |
| Mouser-Teilenr. | `Mouser Part Number`, `MOUSER_PART_NUMBER` |
| Hersteller-Teilenr. | `Manufacturer_Part_Number`, `MANUFACTURER_PART_NUMBER`, `MP`, `Part Number` |
| Hersteller | `Manufacturer`, `MANUFACTURER`, `MF`, `Manufacturer_Name`, `MANUFACTURER_NAME` |

`kicad-cli sch export bom --fields MPN` findet davon nichts, weil das Feld
`MPN` im Projekt gar nicht existiert. Deshalb wird der Schaltplan direkt
geparst statt ueber den CLI-Export.

Ausgangslage nach dem Feld-Abgleich (78 Instanzen):

- **9 mit Mouser-Teilenr.** — direkt abfragbar: `ANT1`, `ANT2`, `J1`,
  `J_PWR1`, `PS1`, `S2`, `T1`, `U6`, `Y1`
- **6 nur mit Hersteller-Teilenr.** — Suche ueber MPN: `C7`, `C8`, `C10`,
  `C12`, `D7`, `U7`
- **63 ohne Teilenummer** — davon rund 50 generische Passivteile; hier kann
  die API nichts liefern, die Felder bleiben zum Ausfuellen offen

## Ziel

Ein versioniertes Skript erzeugt die Stueckliste reproduzierbar aus dem
Schaltplan und fuellt Preis, Lagerbestand und Mouser-Teilenummer fuer alle
Positionen, zu denen eine Teilenummer bekannt ist. Die Mappe rechnet in
LibreOffice fehlerfrei durch.

## Schritte

- [x] S-Expression-Parser fuer KiCad-Dateien (`tmp/bom/sexp.py`)
- [x] Feld-Aliase ermittelt und dokumentiert (siehe Kontext)
- [x] Extraktion der 78 Instanzen inkl. Alias-Aufloesung, Gruppierung nach
      **Wert + Footprint** (nicht `lib_id`, siehe Fortschritt 2026-09-22)
- [x] Mouser-Client: Abfrage ueber Mouser-Teilenr. mit Rueckfall auf
      MPN-Stichwortsuche, Ergebnisse in `tmp/bom/mouser_cache.json`
- [x] xlsx-Erzeugung: Blaetter Stueckliste / Einzelpositionen / Offene Punkte,
      Preisstaffel und Lagerbestand aus der API, Formeln fuer Gesamtpreis
- [x] Gegenprobe: 78 Referenzen, jede in genau einer Gruppe, Mengensumme 78,
      beide Blaetter deckungsgleich
- [x] Mappe mit LibreOffice durchgerechnet — 0 Formelfehler, Summe 28,65 EUR
      stimmt mit den Zeilenwerten ueberein
- [x] Doku: `docs/project/hardware.md` aktualisiert (veraltete Mouser-Nummern,
      neuer Abschnitt zur bestellfaehigen Stueckliste)
- [x] Commit-Vorschlag an Bediener, nach Freigabe lokal committet

## Fortschritt

- 2026-09-22: Task angelegt. Vorarbeit bereits erledigt: Parser steht,
  Feld-Aliase sind ermittelt, Abfrage-Kandidaten (15 von 78) stehen fest.
  Naechster Schritt: Extraktion und Gruppierung im Skript.
- 2026-09-22 (2): Skript erstellt (`generate_bom.py`, `write_xlsx.py`,
  `sexp.py`). Erster Lauf: 13 von 47 Positionen mit Preis.
- 2026-09-22 (3): **Befund — vier Abfragen liefen ins Leere, Ursache waren
  veraltete Mouser-Nummern im Schaltplan**, nicht das Skript. Nachgefasst per
  Stichwortsuche: `742-CAB.6061` → `960-CAB.6061`; `640-12401548E42A` →
  `523-12401548E4#2A`; `GW.20.5150` wird von Mouser nicht mehr gefuehrt;
  `D3V3XA4B10LP` ist nur als `-7`-Variante (Tape & Reel) bestellbar.
  Daraufhin Rueckfall auf MPN-Stichwortsuche eingebaut, Abweichungen werden
  markiert statt still ueberschrieben. Ergebnis: 15 von 46 Positionen.
- 2026-09-22 (4): Gruppierung von `lib_id` auf Wert+Footprint umgestellt —
  `J1` (Symbol `USB_C_Receptacle_USB2.0_16P`) und `J_PWR1` (Symbol
  `USB_C_Receptacle_Power`) sind dieselbe Amphenol-Buchse und waren als zwei
  Positionen gefuehrt. `hardware.md` beschreibt sie ausdruecklich als *eine*
  BOM-Position. Dadurch 47 → 46 Positionen.
- 2026-09-22 (5): Validierung abgeschlossen. LibreOffice rechnet die Mappe
  fehlerfrei durch (0 Formelfehler), Teilsumme 28,65 EUR ueber 15 Positionen,
  78 Referenzen in beiden Blaettern deckungsgleich. Doku nachgezogen.
  **Naechster Schritt:** Commit-Vorschlag, dann Folgetask fuer die Korrektur
  der Schaltplan-Felder (FB1, J6, veraltete Mouser-Nummern).

## Commits

- 3021dc2 Stueckliste reproduzierbar erzeugt und mit Mouser-Daten angereichert

## Offene Fragen

- Keine blockierenden. Die inhaltlichen Entscheidungen zu den generischen
  Passivteilen (Toleranz, Spannung, Dielektrikum) sind bewusst **nicht** Teil
  dieses Tasks — sie gehoeren zum Bediener und stehen im Blatt
  "Offene Punkte".
