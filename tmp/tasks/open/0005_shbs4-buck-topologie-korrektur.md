status: open
priority: critical
type: bugfix
created: 2026-09-08
jira: SHBS-4

# Buck-Ausgangszweig falsch verdrahtet — Topologie korrigieren

## Kontext

Befund aus der Netzlisten-Rekonstruktion, siehe
`tmp/report/2026-09-08_kicad-power-netz-status.md`, Abschnitt „Kritischer
Befund". Blockiert Task 0003 (PWR_FLAG).

Der Ausgangszweig von PS1 (MP2359DJ) weicht grundlegend von der in
[power_supply.md](../../../docs/project/power_supply.md) dokumentierten
Soll-Topologie ab.

## Ist-Zustand

| Knoten | Verbindungen |
| ------ | ------------ |
| A | `PS1.6 (SW)`, `PS1.1 (BST)`, `L1.1`, `C14.1`, `C15.2`, `R17.1`, `#PWR100 (+3V3)` |
| B | `L1.2`, `D11.2 (Anode)` |
| GND | `D11.1 (Kathode)`, `C14.2`, `C15.1`, `PS1.2` |

## Soll-Zustand

| Knoten | Verbindungen |
| ------ | ------------ |
| SW | `PS1.6`, `L1.1`, `D11` **Kathode**, `C15` (eine Seite) |
| BST | `PS1.1`, `C15` (andere Seite) |
| +3V3 (Ausgang) | `L1.2`, `C14.1`, `R17.1`, Power-Symbol `+3V3` |
| GND | `D11` **Anode**, `C14.2`, `PS1.2` |

## Kernpunkte

1. **D11 verpolt und am falschen Knoten** — derzeit Anode am Ausgang,
   Kathode an GND: die Diode würde die Ausgangsspannung kurzschließen.
2. **C15 (Bootstrap) liegt gegen GND** statt zwischen BST und SW.
3. **BST direkt auf SW** — ohne Bootstrap-Kondensator kein High-Side-Gate.
4. **C14 und R17 am SW-Knoten** statt am geglätteten Ausgang.
5. **`#PWR100 (+3V3)` muss nach der Korrektur an den Ausgangsknoten**
   (hinter L1) umziehen.

## Umsetzung

**In der KiCad-GUI durchführen, nicht per Text-Edit.** `power_supply.md`
Zeile 86 dokumentiert bereits, dass skriptgestütztes Einfügen von
Power-Teilen KiCad zum Absturz gebracht hat (defekte `lib_symbols`).

## Done-Bedingung

- Netzliste entspricht der Soll-Tabelle (per ERC und Netzlisten-Export
  geprüft).
- `docs/project/power_supply.md` gegengelesen, ggf. präzisiert.
- Danach Task 0003 (PWR_FLAG) entsperren.
