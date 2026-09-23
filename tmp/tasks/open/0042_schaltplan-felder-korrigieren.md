---
title: Veraltete Teilenummern und irrefuehrende Symbole im Schaltplan korrigieren
created: 2026-09-22
jira: SHBS-16
priority: medium
type: bugfix
---

## Kontext

Der Mouser-Abgleich (SHBS-15) hat Fehler in den Schaltplan-Feldern selbst
zutage gefoerdert. Sie sind elektrisch folgenlos, reproduzieren sich aber bei
**jedem** Stuecklisten-Export, solange sie nicht im Schaltplan behoben sind.
Details: [Mouser-Report](../../report/2026-09-22_mouser-abgleich-stueckliste.md).

## Ziel

Ein Lauf von `tmp/bom/generate_bom.py` meldet im Blatt „Offene Punkte" keine
veralteten Mouser-Nummern mehr, und Symbol und Wert jedes Bauteils sagen
dasselbe wie sein Footprint.

## Schritte

- [x] `ANT1`: Mouser-Feld `742-CAB.6061` → `960-CAB.6061`, Produktlink
      aktualisiert *(2026-09-23)*
- [x] `ANT2`: auf den Seriennachfolger umgestellt *(2026-09-23)* — `Value` und
      `Manufacturer_Part_Number` von `GW.20.5150` auf `GW.20.A151`,
      Mouser-Nummer auf `960-GW.20.A151`, Produktlink aktualisiert.
      Kein Footprint betroffen (`on_board no`)
- [x] `J1` und `J_PWR1`: entfallen — die Buchse wurde in SHBS-17 (Task 0041,
      Commit 5f9b9d6) durch `12401598E4#2A` ersetzt, Mouser-Feld
      `523-12401598E4#2A` gesetzt *(2026-09-23)*
- [x] `U1`: `D3V3XA4B10LP-7` samt Hersteller und Mouser-Nummer als Feld
      eingetragen — erledigt in SHBS-17 (Task 0041) *(2026-09-23)*
- [ ] `FB1`: von `Device:R` auf ein Ferrit-Symbol wechseln (Wert bleibt
      `Ferrit 600R@100MHz`)
- [ ] `J6`: Wert von `Conn_02x03_Odd_Even` auf die Wuerth-Bestellbezeichnung
      `61200621621` aendern
- [ ] `D7`-`D10`: einheitliches Symbol verwenden — `D8`/`D9`/`D10` nutzen
      `Device:LED`, `D7` das spezifische `WL-TMRC_3MM`
- [ ] ERC laufen lassen: muss weiterhin **0 Fehler** melden
- [ ] `generate_bom.py` laufen lassen und gegenpruefen, dass die Meldung
      „veraltete Mouser-Nummern" verschwunden ist
- [ ] Doku: Warnhinweis in [hardware.md](../../../docs/project/hardware.md)
      (Abschnitt „BOM / Beschaffung") entfernen, sobald die Felder stimmen
- [ ] Commit

## Hinweis zur Umsetzung

Symbolwechsel bei `FB1` und den LEDs gehoeren in die KiCad-GUI, damit
Symbol-Cache und Bibliothek konsistent bleiben — siehe den Befund zu
`lib_symbol_mismatch` in
[Bestandsaufnahme](../../report/2026-09-22_schaltplan-abschluss-bestandsaufnahme.md).
Reine Feldaenderungen (Mouser-Nummern, `J6`-Wert) liessen sich zwar als
Textaenderung machen, sollten der Konsistenz halber aber denselben Weg gehen.

Die Serienentscheidung bei den LEDs (WL-TMRW gegen WL-TMRC) ist eine
Bauteilfrage und gehoert zu Task 0041, nicht hierher. Hier geht es nur um die
einheitliche Symbolverwendung.

## Fortschritt

- 2026-09-22: Task angelegt, noch nicht begonnen. Teilweise abhaengig von Task
  0041 (`ANT2`).
- 2026-09-23: **Antennenkette erledigt.** `ANT2` auf den Seriennachfolger
  `GW.20.A151` umgestellt, `ANT1` auf die neue Mouser-Nummer. Sechs Felder in
  `BasisStation_Layout.kicad_sch` geaendert — reine Property-Werte, weder
  `lib_id` noch Geometrie beruehrt, daher kein Symbol-Cache-Thema.
  Validiert: **ERC 0 Verstoesse** (0 Fehler, 0 Warnungen), Stueckliste neu
  erzeugt (16 statt 15 Positionen mit Preis), LibreOffice rechnet fehlerfrei
  durch. `hardware.md` nachgezogen.
  **Naechster Schritt:** `FB1`, `J6` und die LED-Symbole in der GUI. `J1`/
  `J_PWR1` warten auf Task 0041.

## Commits

- 05372f0 ANT2 auf Seriennachfolger GW.20.A151 umgestellt (Teilschritt, Task noch offen)

## Offene Fragen

- Keine blockierenden ausser `ANT2`, das an der Ersatzentscheidung haengt.
