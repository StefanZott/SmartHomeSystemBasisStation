---
type: code-review
created: 2026-10-05
jira: SHBS-53
status: final
---

# Review: Leiterbahnbreite, Differenzpaare, Quarz-Kondensatoren

## Ausgangslage

Ein Hardwareentwickler hat `BasisStation.pdf` (Stand SHBS-52, Commit
`552dbeb`) gesichtet. Seine Punkte:

1. Was ist der Constraint für die Leiterbahnbreite (kleinste Breite)?
2. Die Datenleitungen von Ethernet und USB sollten als Differenzpaar geroutet
   werden.
3. Die Kondensatoren am Quarz sind nicht gut platziert.

## Ergebnis / Befunde

### 1. Leiterbahnbreite

**Es gibt keinen festen Mindestwert.** Die globalen Regeln in
`BasisStation.kicad_pro` stehen auf `min_track_width = 0` und
`min_clearance = 0`. Geregelt ist nur der Vorgabewert der Netzklassen:

| Netzklasse | Breite | Abstand | Via | Netze |
|------------|-------:|--------:|-----|-------|
| Default | 0,20 mm | 0,20 mm | 0,6 / 0,3 mm | alle Signale |
| Power | 0,60 mm | 0,20 mm | 0,8 / 0,4 mm | VBUS, +5V, SW, +3V3, GND |

Die Werte für Differenzpaare in der Netzklasse (0,20 / 0,25 mm) sind
KiCad-Vorgaben und werden nirgends genutzt.

Tatsächlich auf der Platine:

| Breite | Anzahl | Wo |
|-------:|-------:|----|
| 0,12 mm | 2 | +3V3A-Sammelleitung unter U7 (Handroute aus SHBS-10) |
| 0,15 mm | 47 | Einschnürungen an Fine-Pitch-Pads: U1 (0,5 mm), W5500-QFP (0,5 mm), USB-C, Quarz XI |
| 0,20 mm | 393 | Standard-Signale |
| 0,25–0,40 mm | 22 | GND-Stiche, +3V3-Hälse |
| 0,60 mm | 86 | Versorgung |

Kleinster Abstand: 0,15 mm, aber nur innerhalb von U1 (Regel in
`BasisStation.kicad_dru`, Landepattern des Herstellers). Sonst 0,20 mm.

**Bewertung:** Ohne festen Mindestwert prüft die DRC nicht gegen die
Fertigungsgrenzen. Die 0,12 mm unter U7 liegen unter dem, was viele
Standard-Fertiger ohne Aufpreis fertigen (meist 0,127–0,15 mm). Ein
Fertiger ist noch nicht festgelegt.

### 2. Differenzpaare

**USB D+/D− (90 Ω differenziell nach Spezifikation):**

- Nicht als Paar geroutet. Seit der Verlegung von U6 (SHBS-52) laufen D+ und
  D− getrennt (eine Leitung auf F.Cu, eine auf B.Cu), Länge 138 / 124 mm,
  Längenunterschied 14 mm, je 3 Vias.
- Full-Speed (12 Mbit/s) hat 4–20 ns Anstiegszeit. Die kritische Länge liegt
  bei ca. 100 mm (Anstiegszeit/6 bei ca. 170 mm/ns). 138 mm sind darüber.
  Funktionieren wird es sehr wahrscheinlich, sauber ist es nicht. Vor SHBS-52
  waren es 77 mm.

**Ethernet TX±/RX± (100 Ω differenziell):**

- Von Hand und paarweise geführt, sehr kurz (13–27 mm pro Netz einschließlich
  der Abzweige zu den Koppelkondensatoren und Abschlusswiderständen). Durch
  die versetzten Koppel-Cs C29/C30 und das Via-Paar an R36 sind die Paare
  aber nicht durchgehend gekoppelt und nicht längenabgeglichen.

**Impedanz auf 2 Lagen, 1,6 mm (Näherung IPC-2141, εr 4,5, 35 µm Kupfer):**

| Aufbau | Breite / Abstand | Z diff |
|--------|------------------|-------:|
| 2 Lagen, Massefläche auf B.Cu (1,5 mm Abstand) | 0,20 / 0,20 mm | ca. 160 Ω |
| dito, für 100 Ω nötig | ca. 0,95 / 0,20 mm | 100 Ω |
| dito, für 90 Ω nötig | ca. 1,2 / 0,20 mm | 90 Ω |
| 4 Lagen, Masse auf L2 (0,2 mm Prepreg) | 0,20 / 0,20 mm | ca. 108 Ω |

Auf 2 Lagen sind 90/100 Ω mit vernünftigen Breiten nicht einstellbar. Die
Pads der USB-C-Buchse (0,3 mm) und des W5500 (0,5-mm-Raster) lassen 1 mm
breite Leitungen nicht zu. Eine Alternative ist koplanare Führung mit
GND-Fläche dicht neben dem Paar auf derselben Lage. Die genauen Werte sind
mit dem KiCad-Rechner (Coupled Microstrip / Coplanar) oder dem
Impedanzrechner des Fertigers zu bestätigen.

### 3. Quarz Y1 und Lastkondensatoren C25/C26

- Y1: 25 MHz, Würth 830059532, CL = 18 pF. C25/C26 = 27 pF passt
  rechnerisch (2 × (18 pF − ca. 4–5 pF Streukapazität)).
- **Platzierung schlecht:**
  - C25 (XI) sitzt ca. 9 mm, C26 (XO) ca. 6 mm vom Quarz entfernt, beide
    unterhalb von Y1. Mit der Abstandsvergrößerung in SHBS-42 sind sie noch
    etwas weiter gewandert, vorher waren es ca. 8 bzw. 4 mm. Gut platziert
    waren sie auch vorher nicht.
  - XI ist 17,7 mm lang (nur F.Cu), XO 27,7 mm mit 2 Vias und einem Stück
    auf B.Cu. Die Leitungen sind unsymmetrisch und lang. Die GND-Anbindung
    der Kondensatoren läuft nicht kurz zu den GND-Pads von Y1 und U7.
  - Folgen: Frequenzablage durch Streukapazität, schlechteres Anschwingen,
    Abstrahlung bzw. Einkopplung (SPI-Leitungen laufen in der Nähe).
- Üblich: Kondensatoren direkt an die Quarzpads, XI/XO kurz (< 5 mm),
  symmetrisch, ohne Vias und auf einer Lage. Die GND-Seite der Kondensatoren
  kurz an die GND-Pads von Y1 und mit Via in die Massefläche. Keine fremden
  Signale unter oder neben dem Quarz.

## Empfehlungen

1. **Design-Regeln festlegen**, am besten nach Wahl des Fertigers:
   - Mindestbreite und Mindestabstand 0,15 / 0,15 mm (auf Fine-Pitch-Pads
     angewiesen), Standard für Signale 0,20–0,25 mm.
   - Die 0,12-mm-Stücke unter U7 auf 0,15 mm bringen.
2. **USB als Differenzpaar** (KiCad-Differenzpaar-Router, Netzklasse `USB`):
   - Beide Leitungen auf einer Lage, durchgehend gekoppelt, Längendifferenz
     < 1 mm, höchstens 2 Vias pro Leitung, durchgehende Masse darunter.
   - Kürzer führen. Das hängt an der Lage von U6, siehe Entscheidung unten.
3. **Ethernet-Paare neu als Differenzpaar** führen (Netzklasse `ETH`),
   Längenabgleich innerhalb des Paars < 1 mm. C29/C30 und R36/R37 so
   anordnen, dass das Paar symmetrisch bleibt.
4. **Quarz-Bereich neu:**
   - Y1 so drehen, dass XI/XO zu den Pins 30/31 von U7 zeigen.
   - C25/C26 direkt an die Quarzpads, XI/XO ohne Vias auf F.Cu.
   - Unter Y1 eine durchgehende GND-Fläche, keine fremden Leitungen.
5. **Impedanz:**
   - Bei 2 Lagen auf Differenzpaar-Führung mit Kopplung und Längenabgleich
     setzen, die exakte Impedanz bewusst nicht einhalten (für USB-FS und
     100BASE-TX bei diesen Längen vertretbar).
   - Ist exakte Impedanz gewünscht: 4-Lagen-Aufbau.

## Nächste Schritte

Offene Entscheidungen für das Gespräch mit dem Hardwareentwickler:

- **Fertiger und Lagenzahl:** 2 Lagen (günstiger, Impedanz nur näherungsweise)
  oder 4 Lagen (90/100 Ω mit 0,2-mm-Leitungen machbar, Layout weitgehend neu)?
- **Mindestbreite und -abstand:** 0,15 / 0,15 mm in Ordnung?
- **Lage von U6:** Die USB-Länge ist durch SHBS-52 von 77 auf 138 mm
  gestiegen. U6 rechts lassen und USB als Paar führen, oder U6 wieder näher
  an J1?

## Nachtrag 2026-11-17: F1 und PWR_FLAG

Weitere Anmerkung des Hardwareentwicklers: „F1 ist bestimmt zu groß und
vermutlich überflüssig. Zumal PWR_FLAG die Sicherung überbrückt.“

### PWR_FLAG überbrückt F1 nicht

- PWR_FLAG ist ein reines ERC-Symbol ohne elektrische Funktion, es erzeugt
  keine Verbindung und keinen Footprint.
- Netzliste (aktueller Schaltplan): F1.1 liegt auf `VBUS` (J_PWR1), F1.2 auf
  `+5V` (D12, C13, PS1). Das sind zwei getrennte Netze, F1 liegt dazwischen.
- Es gibt zwei Flags, weil KiCad Leistung nicht durch passive Bauteile
  verfolgt: `#FLG01` auf VBUS vor F1, `#FLG02` auf +5V hinter F1 (siehe
  `power_supply.md`, Abschnitt „PWR_FLAG“). Im PDF kann das so aussehen, als
  verbänden die Flags beide Seiten.

### F1: Wert und Nutzen

- F1 = Bourns MF-NSMF110-2, PTC, 1,1 A Haltestrom, 2,2 A Auslösestrom, 1206.
- Last am 5-V-Eingang laut Lastbudget ca. 400 mA (Spitze). F1 löst erst bei
  über dem Fünffachen aus. **Der Wert ist zu groß gewählt.**
- Nutzen: zusammen mit dem TVS D12 (SMAJ5.0A) eine Crowbar-Schutzschaltung.
  Bei Überspannung leitet D12, der Strom steigt, F1 trennt. Ohne F1 brennt
  bei einer fehlerhaften Quelle der TVS oder die Leiterbahn. Bei Kurzschluss
  auf der Platine begrenzt F1 unabhängig vom Netzteil.
- Überflüssig wäre F1 nur, wenn man sich vollständig auf die Strombegrenzung
  des USB-Netzteils verlässt. Bei Markennetzteilen ist das meist gegeben,
  bei Billignetzteilen nicht.
- Vorschlag: F1 behalten, aber auf 0,5–0,75 A Haltestrom reduzieren (z. B.
  MF-NSMF050-2 bzw. MF-NSMF075-2, gleiche Bauform). 0,75 A gibt Reserve für
  Temperatur-Derating und Einschaltstrom. Alternativ F1 und D12 gemeinsam
  entfernen, dann gibt es keinen Überspannungsschutz mehr.

### Zusatzbefund: D12 verpolt (committeter Stand)

- Footprint `Diode_SMD:D_SMA`: Pad 1 = Kathode (KiCad-Konvention, Strich im
  Bestückungsdruck). Das Symbol `Diode:SMAJ5.0A` hat neutrale Pins A1/A2.
- Im committeten Stand (`552dbeb` ff.) liegt Pad 1 (Kathode) auf GND und Pad
  2 (Anode) auf +5V. Damit ist der TVS **in Durchlassrichtung** gepolt und
  schließt +5V über ca. 0,7 V kurz. F1 würde sofort auslösen, die Platine
  liefe nicht an.
- Im nicht committeten Schaltplan im Arbeitsverzeichnis liegt D12 Pin 1
  bereits auf +5V, die Platine ist noch nicht nachgezogen. Woher die
  Änderung stammt, ist offen (nicht vom Agenten).
- Vor der Fertigung zwingend prüfen: Kathode (Pad 1) an +5V, Anode an GND.

## Umsetzung (SHBS-53, 2026-11-17)

| Subtask | Ergebnis |
|---------|----------|
| SHBS-54 Eingangsschutz | D12 in der Platine um 180° gedreht, Kathode an +5V (Schaltplan durch den Bediener). F1 = Littelfuse 1206L075/16WR (0,75 A / 1,5 A, **16 V**). Die zunächst erwogene Bourns MF-NSMF075-2 hat wie die alte F1 nur 6 V. |
| SHBS-55 Design-Regeln | Mindestbreite und -abstand 0,15 / 0,15 mm, 0,12-mm-Stücke verbreitert. Netzklassen USB (0,45 / 0,15 mm) und ETH (0,30 / 0,15 mm). |
| SHBS-56 USB-Paar | ESD-Kanäle an U1 getauscht (Schaltplan), Paar U1 → U6 gekoppelt auf F.Cu ohne Vias, 111,3 mm, Längenunterschied 0,04 mm, 35 GND-Stitching-Vias, DRC-Regel für das Paar. |
| SHBS-57 Ethernet-Paare | TX und RX gekoppelt und längenabgeglichen (0,015 / 0,007 mm), Koppel-Cs nebeneinander, Abschlüsse auf der Leitung, Hilfsnetze nicht unter den Paaren. |
| SHBS-58 Quarz | Y1 direkt an U7, C25/C26 an den Pads, XI/XO 6,2 / 8,5 mm ohne Vias, GND unter dem Quarz durch eine B.Cu-Sperrfläche geschützt. |

**Korrektur zum Befund 2 (Impedanz):** Die obige Formelabschätzung nach
IPC-2141 (ca. 160 Ω für 0,2/0,2 mm) war zu pessimistisch. Ein 2D-Feldlöser
(`tmp/impedance/`, an der 50-Ω-Microstrip auf ca. 1 % validiert) liefert für
0,2/0,2 mm 127 Ω. Eng gekoppelte Paare erreichen 90/100 Ω auch auf 2 Lagen:

- USB 0,45/0,15 mm → 90–97 Ω
- Ethernet 0,30/0,15 mm → 100–107 Ω

Beide Werte gelten für εr 4,2–4,7, mit und ohne GND-Fläche auf F.Cu. Ein
4-Lagen-Aufbau ist nicht nötig.

**Hinweis zum Ablauf:** Für das SPI-Routing am Quarz war zunächst eine
vorübergehende Sperrfläche auf F.Cu geplant. Die automatische
Freigabeprüfung hat diesen Schritt abgelehnt. Das Routing lief deshalb nur
mit den bleibenden Regeln (B.Cu-Sperrfläche, Bauteile). Eine anschließende
Prüfung hat gezeigt, dass kein fremdes Kupfer im Quarzblock liegt.

Doku: `docs/project/hardware.md`, `docs/project/power_supply.md`,
`docs/project/ethernet.md`. DRC mit Schaltplanabgleich 0/0/0, ERC 0/0.
Draufsicht: [2026-11-17_layout-top-shbs53.png](2026-11-17_layout-top-shbs53.png)

## Offen nach SHBS-53

- Mindestbreite und -abstand beim ersten Auftrag mit dem Fertiger abgleichen,
  ebenso dessen Impedanzrechner für den Lagenaufbau.
- Das Platinen-STEP in `enclosure/reference/` hat noch den Stand SHBS-52.
  Seither haben sich nur flache SMD-Teile im Inneren geändert, für die
  Gehäusepassung ist das unerheblich.
