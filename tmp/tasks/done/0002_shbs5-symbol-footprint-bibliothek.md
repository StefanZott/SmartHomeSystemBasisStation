---
status: done
priority: high
type: feature
created: 2026-09-17
jira: SHBS-5
parent_jira: SHBS-3
---

# Symbole und Footprints für W5500 und RJ45 bereitstellen

## Ziel

Bauteilbibliothek für die Ethernet-Sektion anlegen, damit die Schaltplan-Tasks
`0003` und `0004` auf definierte Symbole und Footprints zugreifen können.

## Kontext

Das Projekt hält Symbole unter `pcb/Bauteile/<Gruppe>/` (neuere Teile, z. B.
`Power/power.kicad_sym`) bzw. `pcb/Symbol/` (ältere Einzeldateien) und
Footprints gesammelt in `pcb/Footprints/`. Registriert wird über
`pcb/BasisStation/sym-lib-table` und `fp-lib-table`.

Für Ethernet existiert bisher nichts.

## Aufgaben

1. Datenblätter beschaffen und unter `pcb/Datasheets/` ablegen:
   - WIZnet **W5500** (LQFP-48)
   - gewählte **RJ45-Buchse mit integrierten Magnetics**
2. Konkreten RJ45-Typ auswählen und im Task festhalten (Kriterien: integrierte
   Magnetics, 10/100BASE-TX, zwei Link-/Activity-LEDs, THT für mechanische
   Stabilität am Platinenrand, Verfügbarkeit bei Mouser/Würth).
3. Neue Symbolbibliothek `pcb/Bauteile/Ethernet/ethernet.kicad_sym` mit
   `W5500` und dem RJ45-Symbol anlegen — Namens- und Feldkonvention von
   `pcb/Bauteile/Power/power.kicad_sym` übernehmen.
4. Footprints nach `pcb/Footprints/` legen. LQFP-48 kann aus der
   KiCad-Standardbibliothek übernommen werden, wenn Pitch und Pad-Maße gegen
   das Datenblatt passen; die RJ45-Buchse braucht in der Regel einen eigenen
   Footprint aus dem Hersteller-Maßbild.
5. Beide Bibliotheken in `sym-lib-table` bzw. `fp-lib-table` eintragen
   (Lib-Name `ethernet`, Pfad über `${KIPRJMOD}`).

## Fortschritt

### Datenblätter (Aufgabe 1)

- **W5500:** erledigt — `pcb/Datasheets/Wiznet_W5500_DS_1 0 5.pdf` (Rev. 1.0.5).
  *Hinweis:* Dateiname enthält Leerzeichen; vor dem Eintrag ins KiCad-Feld
  `Datasheet` auf `W5500_DS_V1.0.5.pdf` umbenennen.
- **RJ45:** offen — abhängig von der Typauswahl unten.

### Entscheidung (Bediener, 17.09.2026)

**Würth 7499011121A** — 10/100BASE-T, 1 Port, THT, integrierte Magnetics,
gelb/grüne LEDs, Tab **unten**, geschirmt.

Damit ist auch die offene Tab-Orientierung entschieden: **Tab down**.

### Umgesetzt (Aufgaben 3–5)

Quelle für die Würth-Teile: offizielle
[Würth-KiCad-Bibliothek](https://github.com/WurthElektronik/KiCad-Library)
(Branch `master`, Symbol-Erstelldatum 2025-07-24). Symbol und Footprint wurden
**nicht** von Hand gezeichnet, sondern aus der Herstellerbibliothek übernommen.

| Datei | Inhalt |
| ----- | ------ |
| `pcb/Bauteile/Ethernet/ethernet.kicad_sym` | **W5500**, selbst erstellt, 48 Pins nach Datenblatt Rev. 1.0.5 |
| `pcb/Bauteile/Ethernet/wurth_we-rj45lan.kicad_sym` | **7499011121A**, aus der Würth-Bibliothek extrahiert |
| `pcb/Footprints/T_Wurth_WE-RJ45LAN_7499011121A.kicad_mod` | Footprint aus der Würth-Bibliothek |
| `pcb/3D-Model/T_Wurth_WE-RJ45LAN_7499011121A.step` | 3D-Modell (3,4 MB) |
| `pcb/BasisStation/sym-lib-table` | Einträge `ethernet` und `wurth_rj45` |

**Abweichung vom ursprünglichen Plan:** Statt beider Symbole in *einer* Datei
liegen zwei Bibliotheken vor. Grund: Die Würth-Bibliothek nutzt das
Dateiformat `20220914` (KiCad 6/7), das Projekt `20241209` (KiCad 9).
Das Würth-Symbol bleibt dadurch unverändert gegenüber der Quelle und kann
später ohne Handarbeit neu gezogen werden.

### Korrekturen an den übernommenen Daten

1. **Footprint war als SMD markiert.** Die Würth-Datei enthält `(attr smd)`
   an einem reinen THT-Bauteil — auf `(attr through_hole)` geändert. Sonst
   landet das Teil in der Bestückungsdatei für den Automaten und KiCad meldet
   „footprint type doesn't match pads".
2. **3D-Pfad** von `${WE_3DMODEL_DIR}` auf
   `${KIPRJMOD}/../3D-Model/` umgestellt, damit das Modell ohne
   Umgebungsvariable aus dem Repository gefunden wird.
3. **Symbol-Footprintfeld** von `Transformer_THT_Wurth:` auf `Footprints:`
   umgebogen.
4. **BOM-Felder ergänzt** (`Manufacturer_Part_Number`, `Mouser Part Number`,
   `Notes`) nach der Konvention aus `power.kicad_sym`.

### Pinbelegung RJ45 — Vorsicht beim Ablesen

| Pin | Signal | | Pin | Signal |
| --- | ------ | --- | --- | ------ |
| 1 | `TD+` | | 7 | NC |
| 2 | `CTD` (Mittelanzapfung TX) | | 8 | unbenannt |
| 3 | `TD−` | | 9/10 | LED gelb (+/−) |
| 4 | `RD+` | | 11/12 | LED grün (+/−) |
| 5 | `CRD` (Mittelanzapfung RX) | | S1/S2 | Schirm |
| 6 | `RD−` | | | |

**Fallstrick:** Eine Textextraktion des Datenblatt-Schaltbilds liefert die
Reihenfolge `RD+, CRD, RD−, TD+, CTD, TD−` — also **TX und RX vertauscht**.
Die tatsächliche Zuordnung wurde über die Koordinaten der Beschriftung im PDF
geprüft und stimmt mit dem offiziellen Würth-Symbol überein. Wer die
Belegung aus einem Textdump übernimmt, dreht das Sendepaar.

### Wichtig für Task 0004

Die Buchse enthält **Bob-Smith-Terminierung und den 2-kV-Kondensator bereits
intern** (4 × 75 Ω + 1 nF/2 kV, siehe Datenblatt S. 2). Die entsprechende
Teilaufgabe in Task `0004` entfällt damit grösstenteils — extern bleibt nur
die Schirmanbindung über `S1`/`S2`. Übertrager sind 1:1.

### Endstand nach SHBS-12

Die Bibliotheksstruktur wurde mit **SHBS-12** auf Bauteilordner umgestellt.
Endgültige Ablage:

| Bauteil | Ordner |
| ------- | ------ |
| W5500 | `pcb/Bauteile/W5500/` — Symbol, Footprints (3 IPC-Dichtestufen), STEP |
| RJ45 | `pcb/Bauteile/wuerth_7499011121A/` — Symbol, Footprint, STEP |

Registriert als `W5500` und `wuerth_rj45` in `sym-lib-table` und
`fp-lib-table`. Der ursprünglich geplante Sammelordner
`pcb/Bauteile/Ethernet/` entfällt, ebenso die Ablage in `pcb/Footprints/`
und `pcb/3D-Model/`.

Der W5500-Footprint referenziert nicht mehr die KiCad-Standardbibliothek,
sondern den Hersteller-Footprint `W5500:48LQFP_W5500_WIZ` (nominale
IPC-Dichtestufe) samt lokalem STEP.

### Abnahme (Bediener, 17.09.2026)

- Projekt öffnet **ohne Bibliotheks-Warnung**.
- ERC 0 Fehler / 7 Warnungen — keine aus diesem Task.
- DRC meldet *„Found 0 Footprint errors"*.
- 3D-Ansicht zeigt die Modelle.

### Offen (nicht blockierend)

- **KiCad-Gegenprüfung durch den Bediener.** Im Container ist kein KiCad
  installiert; dass beide Bibliotheken fehlerfrei laden und das W5500-Symbol
  sauber aussieht, konnte **nicht** verifiziert werden.
- **W5500-Footprint:** referenziert die KiCad-Standardbibliothek
  `Package_QFP:LQFP-48_7x7mm_P0.5mm` (Gehäuse 7 × 7 mm, 0,5 mm Raster,
  bestätigt). Nicht ins Projekt kopiert — prüfen, ob das gewollt ist oder ob
  der Footprint wie die übrigen nach `pcb/Footprints/` gehört.
- **Mouser-Nummer `710-7499011121A`** ist aus dem üblichen Würth-Präfix
  abgeleitet und **nicht verifiziert**. Vor der Bestellung prüfen.
- **W5500 Mouser-Nummer** bewusst leer gelassen.
- Datenblatt-Dateiname `Wiznet_W5500_DS_1 0 5.pdf` enthält Leerzeichen.

### RJ45-Kandidaten (Aufgabe 2)

Recherche 17.09.2026. Filter: 10/100BASE-T, 1 Port, THT, integrierte
Magnetics, integrierte LEDs.

| Teil | Hersteller | LEDs | Tab | Schirm | Bewertung |
| ---- | ---------- | ---- | --- | ------ | --------- |
| **7499011121A** | Würth | gelb/grün | unten | ja | **Empfehlung** — passt zum bestehenden Würth-Anteil der BOM |
| 74990111217 | Würth | gelb/grün | oben | ja | Alternative, falls die Gehäuseausrichtung Tab-oben verlangt |
| 7499011222A | Würth | grün/grün | unten | ja | wie Empfehlung, andere LED-Farben |
| LPJ0012GDNL | LINK-PP | gelb/grün | unten | ja | Second Source zu 7499011121A |
| HR911105A | HanRun | gelb/grün | oben | ja | De-facto-Referenz bei W5500-Designs, aber schwache EU-Distribution |

**Verwechslungsgefahr:** `74990…` ist 10/100BASE-T, `74991…` ist
10/100/1000BASE-T. Die Nummern unterscheiden sich nur an der fünften Stelle.
Der W5500 kann kein Gigabit — die Gigabit-Variante wäre teurer ohne Nutzen.

**Offene Entscheidung:** Tab-Orientierung (oben/unten) hängt an der
Gehäusekonstruktion und ist vor der Footprint-Erstellung festzulegen.

## Akzeptanzkriterien

- [ ] Datenblätter W5500 und RJ45 liegen unter `pcb/Datasheets/`.
- [ ] `pcb/Bauteile/Ethernet/ethernet.kicad_sym` enthält beide Symbole, Pins
      vollständig und gegen Datenblatt geprüft (Pin-Nummern, Pintypen).
- [ ] Footprints in `pcb/Footprints/` vorhanden, 3D-Modelle wenn verfügbar
      unter `pcb/3D-Model/`.
- [ ] Bibliotheken in `sym-lib-table` und `fp-lib-table` registriert; KiCad
      öffnet das Projekt ohne Bibliotheks-Warnung.
- [ ] Gewählter RJ45-Typ mit Herstellernummer in dieser Datei dokumentiert.

## Betroffene Dateien

- `pcb/Bauteile/Ethernet/ethernet.kicad_sym` (neu)
- `pcb/Footprints/*.kicad_mod` (neu)
- `pcb/Datasheets/*.pdf` (neu)
- `pcb/BasisStation/sym-lib-table`, `pcb/BasisStation/fp-lib-table`
