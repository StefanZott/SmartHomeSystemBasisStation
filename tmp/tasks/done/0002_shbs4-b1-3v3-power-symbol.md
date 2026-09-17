status: done
priority: high
type: bugfix
created: 2026-09-08
jira: SHBS-4

# B1 — `+3V3` von lokalem Label auf globales Power-Symbol umstellen

## Kontext

Siehe `tmp/report/2026-09-08_kicad-power-netz-status.md`, Abschnitt B1.
Voraussetzung: Task 0001 (B9) abgeschlossen, damit `power:+3V3` auflösbar ist.

Lokale Labels sind blattlokal — Buck-Ausgang auf `Stromversorgung.kicad_sch`
erreicht `U6` auf `BasisStation_Layout.kicad_sch` nicht (ERC:
`power_pin_not_driven` an U6 Pin 2).

## Schritte

Ersetze in allen drei Vorkommen `(label "+3V3" (at X Y ROT) …)` durch ein
platziertes `power:+3V3`-Symbol (`lib_symbols`-Cache-Eintrag + Instanz mit
korrekter Position/UUID) an derselben Koordinate:

1. `Stromversorgung.kicad_sch`, Zeile ~1919
2. `BasisStation_Layout.kicad_sch`, Zeile ~4616
3. `BasisStation_Layout.kicad_sch`, Zeile ~4636

## Done-Bedingung

- Keine `(label "+3V3" …)`-Vorkommen mehr im Projekt.
- `power:+3V3`-Symbol auf allen drei Positionen platziert, Pin deckt exakt
  den vorherigen Label-Anschlusspunkt.
- Hinweis an Bediener: ERC-Lauf in KiCad zur Verifikation ausstehend.

## Ergebnis

Umgesetzt (2026-09-08). Alle drei Labels durch `power:+3V3`-Instanzen ersetzt
(Referenzen #PWR100–#PWR102, Positionen/Rotationen identisch zu den
ursprünglichen Labels übernommen). Property-Textpositionen (Value/Reference)
sind kosmetisch approximiert, nicht pixelgenau aus KiCad — elektrisch ohne
Einfluss.
