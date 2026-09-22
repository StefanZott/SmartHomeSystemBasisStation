---
status: open
priority: medium
type: docs
created: 2026-09-22
jira: SHBS-14
---

# ERC-Ausnahmen fuer PWR_FLAG und EPAD hinterlegen (GUI)

## Kontext

Zwei der sieben ERC-Warnungen sind **gewolltes Verhalten** und werden nicht
durch eine Schaltungsaenderung verschwinden:

**1. `pin_to_pin`** — `S2` Pin 1 (Bidirectional) + `#FLG04` (Power output)

Das GND-`PWR_FLAG`. Hintergrund: Mit dem Wechsel von `Connector:USB_B_Micro`
auf `Connector:USB_C_Receptacle_USB2.0_16P` (Task 0003, SHBS-6) entfiel der
einzige ERC-Treiber des globalen GND-Netzes — das alte Steckersymbol hatte
seinen GND-Pin als *Power output* deklariert, das neue als `power_in`.
`#FLG04` stellt den Treiber wieder her. Es ist der KiCad-Standardweg.

**2. `multiple_net_names`** — GND und EPAD an `U6`

Der versteckte Pin 41 (`EPAD`) des ESP32-S3-WROOM-Symbols traegt einen
eigenen Netznamen und liegt auf GND. KiCad nimmt GND in die Netzliste, was
korrekt ist.

Beide sollen als ERC-Ausnahme im Projekt hinterlegt werden, damit kuenftige
Laeufe eine saubere Null zeigen und echte Neubefunde sofort auffallen.

**Nur in der GUI moeglich:** Ausnahmen haengen an den UUIDs der beteiligten
Elemente und werden in `BasisStation.kicad_pro` unter `erc.erc_exclusions`
abgelegt. Aktuell ist diese Liste leer.

## Schritte (Bediener)

- [ ] ERC in der GUI laufen lassen.
- [ ] Beide Warnungen per Rechtsklick ausschliessen, jeweils mit
      Begruendung im Kommentarfeld.
- [ ] Projekt speichern.

## Schritte (Agent, danach)

- [ ] Pruefen, dass `erc.erc_exclusions` in `BasisStation.kicad_pro` genau
      **zwei** Eintraege hat — nicht mehr.
- [ ] Pruefen, dass `erc.rule_severities` unveraendert auf KiCad-Standard
      steht (es darf **keine** Regel auf `ignore` gedreht worden sein,
      um die Warnungen loszuwerden).
- [ ] `docs/project/hardware.md`: Abschnitt "Hinterlegte ERC-Ausnahmen" mit
      beiden Faellen und Begruendung ergaenzen.

## Done-Bedingung

Zwei Ausnahmen hinterlegt und dokumentiert, Schweregrade unveraendert.
