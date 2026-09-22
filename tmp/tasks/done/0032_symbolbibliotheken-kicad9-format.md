---
status: done
priority: medium
type: bugfix
created: 2026-09-22
jira: SHBS-14
---

# Symbolbibliotheken auf KiCad-9-Format heben

## Kontext

Vier ERC-Warnungen vom Typ `lib_symbol_mismatch` (`S2`, `C7`, `C10`, `C12`)
entstehen, weil Symbolbibliotheken noch im alten Dateiformat vorliegen,
waehrend der Symbol-Cache im Schaltplan KiCad-9-Format hat.

Ein Vergleich beider Fassungen (Report vom 2026-09-22) zeigt
**ausschliesslich Formatunterschiede**: `(id N)` in den Properties, `hide`
statt `(hide yes)`, fehlendes `exclude_from_sim`/`embedded_fonts`,
`Description` statt `Description_1`. **Pins und Geometrie sind identisch** —
elektrisch aendert sich nichts.

| Bibliothek | Format | meldet Mismatch |
| ---------- | ------ | --------------- |
| `1543-650-149` | 20211014 (v6) | ja (`S2`) |
| `WCAP-FTXX_P10` | 20211014 (v6) | ja (`C7`, `C10`, `C12`) |
| `WCAP-PT5H_6.3X5.2` | 20211014 (v6) | nein |
| `WL-TMRC_3MM` | 20211014 (v6) | nein |
| `wuerth_7499011121A` | 20220914 (v7) | nein |
| `wuerth_830059532` | 20220914 (v7) | nein |

Die vier ohne aktuelle Meldung werden mitgezogen, damit das Problem nicht
spaeter erneut auftaucht.

## Wichtig

`kicad-cli sym upgrade` allein raeumt die Warnung **nicht** ab. Ein Testlauf
auf `WCAP-FTXX_P10` liess drei Restunterschiede zum Schaltplan-Cache stehen
(Footprint-Feld, `justify bottom`, Zeilenumbrueche in `Description_1`).
Das Auffrischen des Caches ist deshalb ein eigener Task (0033).

## Schritte

- [ ] Vor dem Upgrade: Netzliste und Stueckliste als Referenz exportieren.
- [ ] `kicad-cli sym upgrade --force` auf die sechs Bibliotheken anwenden.
- [ ] Pruefen, dass in jeder Datei `version 20241209` steht.
- [ ] Pin-Ebene verifizieren: Pinnummern, -namen und -positionen jedes
      betroffenen Symbols vor/nach dem Upgrade vergleichen. Muss
      deckungsgleich sein.
- [ ] Netzliste erneut exportieren und gegen die Referenz diffen — **muss
      identisch sein**.
- [ ] `docs/project/hardware.md`: Hinweis auf das Bibliotheksformat
      ergaenzen.

## Done-Bedingung

Alle sechs Bibliotheken auf `20241209`, Netzliste bitweise unveraendert,
Pin-Ebene verifiziert.

## Fortschritt

- 2026-09-22: **Erledigt.** Alle sechs Bibliotheken per
  `kicad-cli sym upgrade --force` von `20211014`/`20220914` auf `20241209`
  gehoben.
- Verifikation auf Pin-Ebene: Fuer jedes Symbol wurden Pinnummer, Pinname,
  elektrischer Typ, Stil, Position (x/y/Rotation) und Laenge vor und nach
  dem Upgrade extrahiert und verglichen — **alle deckungsgleich**
  (52 Pins ueber 13 Symbole).
- Netzliste und Stueckliste gegen die Referenz vom selben Tag gediffed —
  **beide identisch**.
- ERC unveraendert bei 6 Warnungen. Die vier `lib_symbol_mismatch` stehen
  weiterhin — erwartungsgemaess, siehe Abschnitt "Wichtig". Sie fallen erst
  mit Task 0033 (Cache-Auffrischung in der GUI).
- `docs/project/hardware.md`: neuer Abschnitt "Dateiformat der
  Symbolbibliotheken (SHBS-14)" unter "Bibliotheksstruktur".
- Nicht umgestellt: zwei Archivdateien ohne `sym-lib-table`-Eintrag
  (`W5500/KiCADv6/...`, `wuerth_7499011121A/WE-RJ45_7499011121A.kicad_sym`).
  In der Doku vermerkt.
