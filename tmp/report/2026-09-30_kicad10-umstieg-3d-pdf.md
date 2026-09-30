---
type: investigation
created: 2026-09-30
jira: SHBS-30
status: final
---

# Umstieg auf KiCad 10 und 3D-PDF-Export

## Ausgangslage

Gewünscht ist ein PDF mit Schaltplan, Leiterplatte und interaktivem 3D-Modell.
KiCad 9 kann kein 3D-PDF erzeugen; KiCad 10 bringt `pcb export 3dpdf` (U3D) mit.
Host läuft auf KiCad 10.0.6, der Devcontainer noch auf 9.0.9. Ohne Root-Rechte
im Container wurden die KiCad-10-Pakete aus dem PPA im Scratchpad entpackt und
`kicad-cli` 10.0.6 damit gegen das Projekt ausgeführt.

## Ergebnis / Befunde

- **PPA:** `ppa:kicad/kicad-10.0-releases` liefert für noble `10.0.6~ubuntu24.04.1`
  (= Host-Version). `kicad-packages3d`: 280 MB Download, 3,2 GB installiert.
- **Bibliothekstabellen:** `/usr/share/kicad/template/{sym,fp}-lib-table` kommen
  in KiCad 10 aus `kicad-symbols`/`kicad-footprints` — der Config-Seed im
  Dockerfile funktioniert unverändert (nur Pfad `10.0`).
- **Abhängigkeit:** `_eeschema.kiface` benötigt in KiCad 10 WebKitGTK
  (`libwebkit2gtk-4.1-0`); `apt` zieht das im Container automatisch nach.
- **Modellpfade:** KiCad 10 löst `${KICAD9_3DMODEL_DIR}` weiterhin auf
  (identisches 3D-PDF, 792 902 Byte). Umstellung auf `KICAD10_3DMODEL_DIR`
  daher nur Konsistenz. Vergleich: nur Platine 79 KB, ohne Standardmodelle
  612 KB, vollständig 793 KB. `kicad-cli` meldet fehlende Modelle **nicht**.
- **3D-PDF:** KiCad 10.0.6 schreibt xref-Einträge mit Offset 0 (`qpdf --check`
  warnt). `qpdf`-Merge repariert das; Exit-Code 3 → `--warning-exit-0`.
  3D-Annotation (`/3DA /A /PO`, Toolbar) und U3D-Stream mit 4 Ansichten bleiben
  erhalten, `/P` zeigt auf die richtige Seite. Gesamt-PDF: 12 Seiten, 1,8 MB.
- **ERC/DRC unter KiCad 10** (gegen unveränderten KiCad-9-Stand):
  - ERC: 1× `lib_symbol_mismatch` J1 (Standardsymbol USB-C geändert)
  - DRC: 2× `copper_edge_clearance` NPTH J1 ↔ GND-Zone 0,25 mm < 0,5 mm
  - DRC: 57× `footprint_symbol_field_mismatch` (fast alle `Datasheet` `~` vs. leer)

## Empfehlungen

- In KiCad 10: Zonen neu füllen, *Leiterplatte aus Schaltplan aktualisieren*,
  J1-Symbol aus Bibliothek aktualisieren; danach ERC/DRC erneut bewerten.
  Eigenes Ticket.
- Projektdateien erst in KiCad 10 speichern, wenn alle Rechner und der
  Container auf KiCad 10 stehen.

## Nächste Schritte

- Container-Rebuild durch Bediener, Done-Bedingung SHBS-31 prüfen.
- 3D-Seite in Acrobat Reader prüfen (SHBS-33).

## Nachtrag: Behebung (SHBS-35)

- Zonen per `kicad-cli pcb drc --refill-zones --save-board` neu gefüllt →
  `copper_edge_clearance` weg; Board jetzt Format `20260206`.
- Speichern über die `pcbnew`-Python-API verworfen: sortiert Segmente um
  (≈6400 Zeilen Diff) und schreibt KiCad-10-Defaults in `.kicad_pro`.
  Feldabgleich stattdessen textbasiert (389 Zeilen Diff).
- DRC meldet `footprint_symbol_field_mismatch` nur für das erste
  abweichende Feld je Footprint — S2 fehlten tatsächlich 22 Felder.
- **J1-Falle:** KiCad 10 nummeriert im Standardsymbol den Schirm-Pin
  `S1` → `SH`; der Footprint hat 4 Pads `S1`. Bibliotheks-Update hätte den
  Schirm von GND getrennt. Lösung: Symbol-Kopie mit `S1` in `shbs_power`.
  Netze vorher/nachher byte-identisch, `J1.S1` an GND.
- Endstand: ERC 0/0, DRC 0 Verstöße, 0 Paritätsabweichungen; mit
  `--severity-all` nur hinterlegte Ausnahmen (ERC 1, DRC 14; vorher 17).
