---
type: analysis
created: 2026-09-22
jira: SHBS-15
status: final
---

# Mouser-Abgleich der Stückliste

## Ausgangslage

Der erste Stücklisten-Export (Commit `5877d96`) blieb ohne Preise und ohne
Mouser-Teilenummern — zu dem Zeitpunkt lag kein API-Schlüssel vor. Seit Task
0038 sind Schlüssel, LibreOffice und `openpyxl` im Container verfügbar. Dieser
Abgleich holt die Beschaffungsdaten nach und prüft dabei, ob die im Schaltplan
gepflegten Teilenummern überhaupt noch gültig sind.

## Ergebnis / Befunde

### B1 — Teilenummern liegen unter uneinheitlichen Feldnamen

Je nach Herkunft eines Symbols (SnapEDA, Würth-Generator, handgepflegt) heißt
dasselbe Feld anders:

| Bedeutung | Vorkommende Feldnamen |
| --------- | --------------------- |
| Mouser-Teilenr. | `Mouser Part Number`, `MOUSER_PART_NUMBER` |
| Hersteller-Teilenr. | `Manufacturer_Part_Number`, `MANUFACTURER_PART_NUMBER`, `MP`, `Part Number` |
| Hersteller | `Manufacturer`, `MANUFACTURER`, `MF`, `Manufacturer_Name`, `MANUFACTURER_NAME` |

`kicad-cli sch export bom --fields MPN` liefert dafür eine leere Spalte, ohne
zu warnen — das Feld `MPN` existiert im Projekt gar nicht. **Das ist die
Ursache, warum der erste Export ohne Teilenummern blieb.** Konsequenz: die
Schaltplanblätter werden direkt geparst statt über den CLI-Export.

### B2 — Vier im Schaltplan gepflegte Mouser-Nummern sind nicht mehr gültig

Das war der eigentliche Fund. Die Nummern wurden nicht blind übernommen,
sondern gegen die API geprüft:

| Bauteil | Im Schaltplan | Tatsächlich | Bewertung |
| ------- | ------------- | ----------- | --------- |
| `ANT1` | `742-CAB.6061` | `960-CAB.6061`, 845 ab Lager | Nummer gewechselt |
| `ANT2` | `742-GW.20.5150` | **kein Treffer** | Typ abgekündigt, Nachfolger siehe Nachtrag |
| `J1`, `J_PWR1` | `640-12401548E42A` | `523-12401548E4#2A`, nicht bevorratet | Nummer gewechselt |
| `U1` | *(keine)* | `D3V3XA4B10LP` ist `N/A`, bestellbar nur als `D3V3XA4B10LP-7` | Gurtvariante nötig |

`ANT2` sah zunächst nach dem kritischsten Punkt aus. Der Nachtrag unten
entschärft das.

### Nachtrag 2026-09-23 — Korrektur zu ANT2 und ein neuer Befund

**Die Aussage „für ANT2 gibt es bei Mouser keinen Bezugsweg" war zu weit
gefasst.** Sie galt für die exakte Nummer, nicht für das Bauteil. Eine
Stichwortsuche statt einer Teilenummernsuche zeigt: Taoglas ist bei Mouser auf
das `960-`-Präfix umgezogen, und der Seriennachfolger ist verfügbar.

| Position | Mouser-Nr. | Lager | Preis @1 |
| -------- | ---------- | ----- | -------- |
| ANT2 Nachfolger | `960-GW.20.A151` (2 dBi, 2,4 GHz, RP-SMA(M) gerade) | 650 | 8,46 € |
| dito, weiß | `960-GW.20.A151W` | 480 | 8,27 € |
| ANT1 Pigtail | `960-CAB.6061` | 845 | 4,47 € |

Form, Anschluss und Gewinn stimmen mit `GW.20.5150` überein. Die Antennenkette
ist damit **vollständig über Mouser beschaffbar** — es bleibt eine
Teilenummernpflege, keine Produktentscheidung.

**Lehre für die Methode:** Eine erfolglose Teilenummernsuche belegt nur, dass
*diese Nummer* nicht mehr gilt — nicht, dass das Bauteil fehlt. Vor dem Schluss
„nicht beschaffbar" gehört eine Stichwortsuche über Hersteller und Serie dazu.
Derselbe Fehler wäre bei Reichelt fast passiert (siehe
[Reichelt-Report](2026-09-22_reichelt-verfuegbarkeit.md), B5).

**Neuer Befund — `J1`/`J_PWR1` sind ebenfalls abgekündigt.** Die Amphenol-Buchse
`12401548E4#2A` ist laut DigiKey „no longer manufactured, substitute products
are available". Das erklärt den Lagerbestand 0 bei Mouser und ist kein
Distributorproblem, sondern ein Abkündigungsfall. **Hier ist wirklich ein Ersatz
zu wählen** — und anders als bei der Antenne hängt daran ein Footprint, der
möglicherweise angepasst werden muss.

### B3 — `PS1` ist gelistet, aber nicht verfügbar

Der Buck-Regler `MP2359DJ-LF-Z` (`946-MP2359DJLFZ`, 2,06 €) hat
**Lagerbestand 0**. Das betrifft den Termin für den Prototypenaufbau, nicht
die Schaltung.

### B4 — `J1` und `J_PWR1` waren als zwei Positionen geführt

Beide nutzen dieselbe Amphenol-Buchse und denselben Footprint, aber
verschiedene Symbole (`Connector:USB_C_Receptacle_USB2.0_16P` gegenüber
`shbs_power:USB_C_Receptacle_Power`). Eine Gruppierung nach `lib_id` trennt
sie deshalb künstlich. [hardware.md](../../docs/project/hardware.md) beschreibt
sie ausdrücklich als *eine* BOM-Position. Gruppierung auf Wert + Footprint
umgestellt: 47 → 46 Positionen.

### Abdeckung

| Kennzahl | Wert |
| -------- | ---- |
| Bestückte Referenzen | 78 |
| Bestellpositionen | 46 |
| Mit Preis aus der API | 15 |
| Ohne Teilenummer (überwiegend generische Passivteile) | 29 |
| Teilsumme der erfassten Positionen | 28,65 € |

Die Teilsumme ist **kein** Baugruppenpreis — zwei Drittel der Positionen sind
noch nicht spezifiziert.

## Empfehlungen

1. **Schaltplan-Felder korrigieren** (`ANT1`, `J1`, `J_PWR1`): veraltete
   Mouser-Nummern eintragen, sonst liefert jeder neue Export wieder die alte
   Nummer. Gleicher Zug: `FB1` auf ein Ferrit-Symbol, `J6`-Wert auf die
   Würth-Bestellbezeichnung.
2. **Ersatz für `ANT2` festlegen** — Bediener, weil es eine Produktentscheidung
   ist (Polarität und Steckertyp müssen bleiben).
3. **Generische Passivteile spezifizieren** — 29 Positionen. Vorrang haben
   `C25`/`C26` am 25-MHz-Quarz (Lastkapazität) und die 1-%-Widerstände im
   Ethernet-Zweig.
4. **Lieferzeit für `PS1` klären**, bevor ein Aufbautermin zugesagt wird.

## Nächste Schritte

- Commit der Stückliste und der Werkzeuge (Task 0039).
- Folgetask für die Schaltplan-Korrekturen aus Empfehlung 1 — eigenes Problem,
  eigenes Ticket.
- Entscheidungen zu Empfehlung 2 und 3 liegen beim Bediener; ohne sie bleibt
  die Stückliste unvollständig.
