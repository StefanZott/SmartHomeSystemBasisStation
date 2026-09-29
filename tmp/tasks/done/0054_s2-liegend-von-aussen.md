---
title: Reset-Taster S2 von außen bedienbar — liegender PTS645VL58-2 LFS an der Buchsenseite
created: 2026-09-29
jira: SHBS-25
priority: medium
type: feature
status: done
---

## Kontext

S2 (EN/Reset) war ein stehender Bourns 1543-650-149 mitten auf der Platine,
im Gehäuse nicht erreichbar. Bediener: S2 seitlich neben USB/RJ45, Stößel
bündig mit der Gehäuseaußenseite, Wandstärke 2 mm.

## Ziel

Stößelspitze in der Ebene der Außenwand (2 mm vor der Platinenkante), DRC/ERC
ohne neue Fehler, Stückliste aktuell.

## Schritte

- [x] Bauteil: KiCad-Footprint und Herstellermodell (kicad-packages3D) nach `pcb/Bauteile/PTS645VL58-2LFS/`, `fp-lib-table`
- [x] Schaltplan: Footprint, Wert, Hersteller, Bestellfelder; Altfelder des Bourns-Imports bereinigt
- [x] Platine: S2 getauscht (Pins 169,5 / 31,35), EN neu geführt (USB− links, Befestigungsbein rechts umgangen)
- [x] DRC-Regel für einen Thermal-Steg am S2-GND-Pad (Ausschluss nicht zuordenbar)
- [x] Stückliste neu erzeugt (Mouser 611-PTS645VL582, DigiKey CKN9116-ND)
- [x] Doku `hardware.md`, Render

## Fortschritt

- 2026-09-29: Umgesetzt wie geplant. DRC: 0 offen, 0 Parität, nur die 15
  bekannten Ausschlüsse. ERC unverändert (1 ausgenommene Warnung). Die von mir
  zuerst eingetragene Mouser-Nr. 611-PTS645VL582LFS war falsch; der
  Stücklisten-Generator hat die gültige 611-PTS645VL582 gefunden. Erster
  Versuch der Thermal-Regel mit `(min 1)` hat die ganze `kicad_dru`
  ungültig gemacht, die korrekte Syntax ist `(constraint min_resolved_spokes 1)`.

## Commits

- (noch keine)

## Offene Fragen

- Keine.
