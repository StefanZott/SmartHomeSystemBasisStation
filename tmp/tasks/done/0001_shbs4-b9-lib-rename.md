status: done
priority: high
type: bugfix
created: 2026-09-08
jira: SHBS-4

# B9 — Projektbibliothek „power" auf „shbs_power" umbenennen

## Kontext

Siehe `tmp/report/2026-09-08_kicad-power-netz-status.md`, Abschnitt B9.
Projektbibliothek `power` verdeckt KiCad-Standardbibliothek `power`
(GND, PWR_FLAG, +3V3 nicht auflösbar → 28× ERC-Warnung).

## Schritte

1. `PCB/BasisStation/sym-lib-table`: `(lib (name "power") …)` →
   `(lib (name "shbs_power") …)`.
2. `PCB/BasisStation/Stromversorgung.kicad_sch`:
   - `lib_symbols`-Cache-Eintrag `"power:MP2359DJ"` → `"shbs_power:MP2359DJ"`
   - `lib_symbols`-Cache-Eintrag `"power:USB_C_Receptacle_Power"` →
     `"shbs_power:USB_C_Receptacle_Power"`
   - Instanz-`lib_id` von PS1: `"power:MP2359DJ"` → `"shbs_power:MP2359DJ"`
   - Instanz-`lib_id` von J_PWR1: `"power:USB_C_Receptacle_Power"` →
     `"shbs_power:USB_C_Receptacle_Power"`
3. Alle `power:GND` / `power:PWR_FLAG` / `power:+3V3`-Referenzen bleiben
   unverändert.

## Done-Bedingung

- Keine verbleibende Referenz auf Nickname `power` für Projekt-eigene Symbole.
- `docs/project/power_supply.md` auf Bibliotheks-Umbenennung geprüft, ggf.
  aktualisiert.
- Hinweis an Bediener: ERC-Lauf in KiCad zur Verifikation ausstehend.

## Ergebnis

Umgesetzt (2026-09-08). Alle Schritte durchgeführt, S-Expression-Integrität
per Skript verifiziert (vollständiges, gültiges Parsen beider Schaltplan-
Dateien). `docs/project/power_supply.md` noch nicht geprüft — offen, siehe
Abschluss-Hinweis im Prompt-Report.
