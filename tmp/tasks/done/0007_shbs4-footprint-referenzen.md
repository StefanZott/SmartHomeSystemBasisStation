status: done
priority: medium
type: bugfix
created: 2026-09-08
jira: SHBS-4

# Footprint-Referenzen der Projektsymbole auf `Footprints:` vereinheitlichen

## Kontext

Nach Task 0006 (Symbolbibliotheken registriert) verschwanden die 6
`lib_symbol_issues`, dafür erschienen 3 neue `footprint_link_issues`
(ERC 14:58): Die Footprint-Bibliotheken `WCAP-PT5H_6.3X5.2`,
`1543-650-149` und `WL-TMRC_3MM` seien nicht in der Konfiguration.

Ursache: Erst seit die Symbole auflösbar sind, prüft KiCad auch deren
Footprint-Verknüpfung. Die drei `.kicad_sym`-Dateien tragen in ihrer
Symboldefinition ein Footprint-Feld, das auf eine **gleichnamige
Footprint-Bibliothek** verweist — die es nicht gibt. `fp-lib-table`
kennt nur `Footprints` → `${KIPRJMOD}/../Footprints`, und dort liegen
alle `.kicad_mod`-Dateien.

`WCAP-FTXX_P10.kicad_sym` hat kein Footprint-Feld — daher dort keine
Meldung.

## Entscheidung

Footprint-Feld in den drei `.kicad_sym`-Dateien auf `Footprints:`
umgestellt, statt drei Alias-Einträge in `fp-lib-table` auf denselben
Ordner anzulegen:

| Datei | alt | neu |
| ----- | --- | --- |
| `WCAP-PT5H_6.3X5.2.kicad_sym` | `WCAP-PT5H_6.3X5.2:WCAP-PT5H_6.3X5.2_DXL_` | `Footprints:WCAP-PT5H_6.3X5.2_DXL_` |
| `1543-650-149.kicad_sym` | `1543-650-149:1543650149` | `Footprints:1543650149` |
| `WL-TMRC_3MM.kicad_sym` | `WL-TMRC_3MM:WL-TMRC_3MM` | `Footprints:WL-TMRC_3MM` |

Begründung: Die Schaltplan-Instanzen von C8, S2 und D7 verweisen bereits
auf `Footprints:…`. Damit sind Bibliothek und Instanz konsistent, und ein
künftiges „Symbole aus Bibliothek aktualisieren" überschreibt die
Instanz-Referenz nicht mehr mit einem toten Nickname. Eine einzige
Footprint-Bibliothek bleibt erhalten.

## Ergebnis

Umgesetzt und verifiziert: Zieldatei je Eintrag vorhanden
(`pcb/Footprints/*.kicad_mod`), alle drei `.kicad_sym` parsen sauber,
CRLF erhalten.

**Offen für den Bediener:** Projekt in KiCad neu laden, ERC erneut laufen
lassen — die 3 `footprint_link_issues` sollten entfallen.
