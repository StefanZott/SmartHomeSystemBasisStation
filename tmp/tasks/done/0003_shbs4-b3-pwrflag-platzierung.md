status: done
priority: medium
type: bugfix
created: 2026-09-08
jira: SHBS-4

# B3 — PWR_FLAG an VBUS und 3,3-V-Ausgang platzieren

## BLOCKIERT (2026-09-08)

Die Netzlisten-Rekonstruktion hat ergeben, dass der Buck-Ausgangszweig falsch
verdrahtet ist (Task 0005). Das derzeitige „+3V3"-Netz ist in Wirklichkeit der
Schaltknoten SW. Ein PWR_FLAG dort würde die ERC-Fehler kosmetisch verdecken,
ohne die Schaltung zu korrigieren.

Ausserdem korrigiert: Es sind **zwei** PWR_FLAGs für den Eingang nötig, nicht
eines — je eines vor und hinter `F1`. Beide Netze enthalten ausschliesslich
`power_in`-Pins (`J_PWR1.A4/A9` bzw. `PS1.5`), und KiCad verfolgt Leistung
nicht durch passive Bauteile wie die Sicherung.

## Kontext

Siehe `tmp/report/2026-09-08_kicad-power-netz-status.md`, Abschnitt B3.
Voraussetzung: Task 0001 (B9) abgeschlossen.

ERC: `power_pin_not_driven` an PS1 Pin 5 (VIN) und J_PWR1 Pin A4 (VBUS) —
USB-C-Buchse liefert nur Power-Input-Pins, kein Power-Output treibt VBUS.

## Schritte

1. `PWR_FLAG`-Symbol auf `Stromversorgung.kicad_sch` an VBUS platzieren
   (hinter F1, vor PS1 Pin 5 VIN) — auf vorhandenem Wire-Punkt, nicht neu
   verdrahten.
2. `PWR_FLAG`-Symbol am 3,3-V-Ausgangsnetz platzieren (am `power:+3V3`-Symbol
   aus Task 0002, gleicher Netzpunkt).
3. Verwaisten `lib_symbols`-Cache-Eintrag „PWR_FLAG" in
   `BasisStation_Layout.kicad_sch` (Zeilen ~3317–3402) nur behalten, falls
   dort ebenfalls eine Instanz nötig ist — sonst als toten Cache-Eintrag
   dokumentieren, nicht selbständig löschen (Risiko für andere Blattreferenzen
   ohne ERC-Verifikation).

## Risikohinweis

Platzierung erfolgt als Text-Edit ohne visuelle/elektrische Verifikation
(kein KiCad in dieser Umgebung). **Vor Weiterarbeit zwingend ERC-Lauf durch
Bediener.**

## Done-Bedingung

- PWR_FLAG an beiden Netzen (VBUS, +3V3) platziert.
- Report/Task-Notiz zum verwaisten Layout-Cache-Eintrag ergänzt.
- Hinweis an Bediener: ERC-Lauf + Netzliste-Neuerzeugung ausstehend.

## Ergebnis (2026-09-19)

Entsperrt durch den Abschluss von Task 0005. Bei der Prüfung zeigte sich,
dass die Platzierung bereits am 2026-09-15 in der KiCad-GUI erfolgt ist.

| Ref | Netz | Status |
| --- | ---- | ------ |
| `#FLG01` | VBUS vor `F1` (`J_PWR1.A4/A9`) | gesetzt |
| `#FLG02` | 5-V-Schiene hinter `F1` (`PS1.5` VIN) | gesetzt |
| `#FLG03` | Buck-Ausgang `+3V3` (hinter `L1`) | gesetzt, Lage nach der Topologie-Korrektur bestätigt |
| `#FLG04` | GND (Blatt Layout) | gesetzt |

Die beiden geforderten Flags an VBUS und `+3V3` liegen damit vor, `#FLG03`
sitzt nachweislich hinter `L1` am echten Ausgangsknoten und nicht mehr auf
`SW`. Die ERC-Fehler `power_pin_not_driven` an `PS1.5` und `J_PWR1.A4` sind
entfallen — Lauf 2026-09-18 23:42 meldet **0 Fehler**.

Zum verwaisten `lib_symbols`-Cache-Eintrag „PWR_FLAG" in
`BasisStation_Layout.kicad_sch`: Das Blatt führt mit `#FLG04` inzwischen eine
eigene Instanz, der Eintrag ist damit kein toter Cache mehr und bleibt.

## Commits

- `1145412` — PWR_FLAG-Platzierung verifiziert und Task geschlossen
