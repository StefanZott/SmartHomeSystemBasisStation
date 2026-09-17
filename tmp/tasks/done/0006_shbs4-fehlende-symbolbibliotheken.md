status: done
priority: medium
type: bugfix
created: 2026-09-08
jira: SHBS-4

# Fehlende Symbolbibliotheken in sym-lib-table registrieren

## Kontext

`report.txt` (KiCad-Lauf „Symbole aus Bibliothek aktualisieren", 2026-09-08
14:38) meldete für 6 Symbole *** Symbol nicht gefunden ***. Ursache: Vier
Projektbibliotheken liegen als Datei unter `pcb/Symbol/` vor, sind aber nicht
in `sym-lib-table` registriert. Im ERC erschienen sie als 6×
`lib_symbol_issues`.

| Nickname | Datei | verwendet von |
| -------- | ----- | ------------- |
| `WCAP-FTXX_P10` | `pcb/Symbol/WCAP-FTXX_P10.kicad_sym` | C7, C10, C12 |
| `WCAP-PT5H_6.3X5.2` | `pcb/Symbol/WCAP-PT5H_6.3X5.2.kicad_sym` | C8 |
| `WL-TMRC_3MM` | `pcb/Symbol/WL-TMRC_3MM.kicad_sym` | D7 |
| `1543-650-149` | `pcb/Symbol/1543-650-149.kicad_sym` | S2 |

Alle übrigen nicht registrierten Nicknames (`Device`, `Diode`, `Connector`,
`Connector_Generic`, `Power_Protection`, `Transistor_BJT`, `power`) sind
KiCad-Standardbibliotheken — korrekt ohne Projekteintrag.

## Ergebnis

Vier Einträge in `pcb/BasisStation/sym-lib-table` ergänzt (Muster wie
bestehender `Espressif`-Eintrag, `${KIPRJMOD}/../Symbol/…`). Verifiziert:
Datei existiert je Eintrag und enthält das gleichnamige Symbol.

**Offen für den Bediener:** In KiCad Projekt neu laden (oder Bibliotheken
neu einlesen), dann erneut „Symbole aus Bibliothek aktualisieren" und ERC —
danach sollten die 6 `lib_symbol_issues` entfallen.
