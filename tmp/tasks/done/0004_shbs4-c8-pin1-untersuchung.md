status: done
priority: low
type: bugfix
created: 2026-09-08
jira: SHBS-4

# C8 Pin 1 unverbunden — Untersuchung

## Kontext

ERC (Stand `ERC.rpt`, 2026-06-17, veraltet): `unconnected_wire_endpoint`
in Zusammenhang mit C8 (`WCAP-PT5H_6.3X5.2`) auf
`BasisStation_Layout.kicad_sch`.

## Schritte

1. C8 und angrenzende Wires/Nets in `BasisStation_Layout.kicad_sch`
   analysieren (Referenz: Zeilen ~2528, ~5995, ~6149 und Umgebung).
2. Ursache bestimmen (fehlende Verbindung, Altlast aus Vor-USB-C-Layout,
   o. ä.).
3. Fix nur umsetzen, wenn Ursache eindeutig aus dem Text hervorgeht —
   andernfalls als offenen Punkt für den Bediener (KiCad-GUI) dokumentieren.

## Done-Bedingung

- Ursache dokumentiert (Report ergänzt).
- Fix umgesetzt ODER begründet an Bediener übergeben.

## Ergebnis (2026-09-08)

**Ursache eindeutig:** Rasterversatz. `C8` sitzt bei (66,04 / 30,48) rot 90.

- `C8` Pin 2 → (66,04 / 33,02) → GND (`#PWR035`) — verbunden
- `C8` Pin 1 → (66,04 / 25,40) — war unverbunden
- Der zugehoerige Draht endete bei (66,04 / **22,86**) — Luecke von exakt
  **2,54 mm** (ein 100-mil-Raster)

Das Zielnetz ist die 3,3-V-Versorgung des ESP32: `U6.2`, `C10.1`, `C12.1`,
`J6.2`, `R9.1`. `C8` ist damit als Stuetzkondensator vorgesehen — Absicht
eindeutig.

**Fix umgesetzt:** Drahtsegment (66,04 / 22,86) → (66,04 / 25,40) in
`BasisStation_Layout.kicad_sch` eingefuegt. Verifiziert: `C8.1` liegt jetzt
im Netz `['C10.1', 'C12.1', 'C8.1', 'J6.2', 'R9.1', 'U6.2']`.

Behebt zwei ERC-Meldungen: `pin_not_connected C8 Pin 1` (Fehler) und
`unconnected_wire_endpoint @(2600 mils, 900 mils)` (Warnung).
