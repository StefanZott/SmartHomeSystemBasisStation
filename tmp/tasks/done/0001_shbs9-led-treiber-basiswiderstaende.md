status: done
priority: high
type: bugfix
created: 2026-09-17
jira: SHBS-9

# LED-Treiber Q1–Q4: Basiswiderstände und unkritische GPIOs

## Kontext

Die vier Status-LED-Treiber Q1–Q4 (BC337, NPN) im Blatt
`BasisStation_Layout.kicad_sch` hingen ohne Basisvorwiderstand direkt an
GPIO-Pins des ESP32-S3. Die Basis-Emitter-Strecke klemmt den Pin auf ca.
0,7 V; ohne Serienwiderstand begrenzt nur die Treiberimpedanz den Strom,
was die zulässigen 20 mA je Pin deutlich überschreitet.

Zusätzlich lagen drei der vier Zweige auf Strapping-Pins (GPIO3, GPIO45,
GPIO46). Die Basis-Emitter-Diode wirkt beim Reset wie ein Pull-down und
kann die eingelesene Boot-Konfiguration verschieben — bei GPIO3 auch die
JTAG-Quellenwahl, relevant wegen des JTAG-Headers `J5`.

## Entscheidung

Basiswiderstände 4,7 kΩ (`R23`–`R26`) statt Direktansteuerung der LEDs
durch den GPIO: Der Transistorzweig bleibt erhalten, damit später auch
Lasten oberhalb der GPIO-Grenzen an diesen Zweigen möglich sind.

LED-GPIOs auf Pins ohne Strapping-, ADC- und Touch-Funktion umgelegt —
das sind beim verbauten Modul die einzigen freien Pins ohne Zusatzwert,
sodass ADC1 und die Touch-Kanäle vollständig verfügbar bleiben:

| LED | Transistor | alt | neu |
| --- | ---------- | --- | --- |
| `D7` gelb | `Q4` | GPIO3 | GPIO21 |
| `D9` rot | `Q3` | GPIO21 | GPIO38 |
| `D10` grün | `Q2` | GPIO45 | GPIO47 |
| `D8` blau | `Q1` | GPIO46 | GPIO48 |

GPIO35–37 blieben unbeschaltet — sie sind beim Modul N16R8 intern vom
Octal-PSRAM belegt.

## Ergebnis

Schaltplan und Netzliste vom Bediener umgesetzt, Kette
`GPIO → Rb → Basis` sowie `+3V3 → LED → Rv → Kollektor` und
`Emitter → GND` je Zweig gegen `BasisStation.net` verifiziert.
Footprints an `R23`–`R26` gesetzt (`R_Axial_DIN0617`, konsistent zu
`R13`–`R16`). ERC-Lauf 17.09.2026: 0 Fehler, 9 Warnungen — keine davon
aus dieser Änderung. GPIO3, GPIO45 und GPIO46 sind frei.

Pinbelegung in [hardware.md](../../../docs/project/hardware.md)
dokumentiert (Abschnitt „Status-LEDs"), ERC-Stand dort nachgezogen.

**Offen für den Bediener:**

- Loses Leitungsende bei (85,09 / 53,34) am EN-Netz entfernen — die
  einzige ERC-Warnung, die aus einem Editier-Überbleibsel stammt.
- Netzliste nach diesem Schritt neu exportieren und ins Layout
  übernehmen (`BasisStation.kicad_pcb` kennt `R23`–`R26` noch nicht).
- Bauform `R_Axial_DIN0617` (20,32 mm Raster) für 1,4 mW Verlustleistung
  prüfen — `R_Axial_DIN0207` wie bei `R9` spart Platinenfläche.

Keine Firmware-Änderung, daher keine Versionserhöhung und kein Eintrag in
`releases.md`.

## Commits

| Hash | Beschreibung |
| ---- | ------------ |
| `517e5e3` | `fix(SHBS-9)`: Schaltplan — R23–R26 ergänzt, LEDs auf GPIO21/38/47/48 |
| _(dieser Commit)_ | `docs(SHBS-9)`: Pinbelegung in `hardware.md`, Task-Datei |
