---
status: done
priority: high
type: feature
created: 2026-09-17
jira: SHBS-12
parent_jira: SHBS-3
---

# KiCad-Bibliotheken auf Bauteilordner umstellen

## Ziel

Ein Ordner pro Bauteil unter `pcb/Bauteile/`. Die Sammelordner `pcb/Symbol/`,
`pcb/Footprints/` und `pcb/3D-Model/` entfallen.

## Bestandsaufnahme (17.09.2026)

Referenzen gegen `*.kicad_sch`, `BasisStation.net` und `BasisStation.kicad_pcb`
geprüft.

| Ordner | gebraucht | verwaist |
| ------ | --------- | -------- |
| `Symbol/` | 4 von 10 | 6 |
| `Footprints/` | 10 von 14 | 4 |
| `3D-Model/` | 6 von 9 | 3 |

**Verwaist:** alles zu `TSR_1-2433E` (PS2 mit SHBS-4 entfallen),
`ESP32-S3-WROOM-2` (falsches Modul), `WL-TMRC_5MM`, `SOT-23-6` (Dublette zu
`MP2359DJ`), `Espressif.kicad_sym` (Modul kommt aus `Bauteile/`), beide
`6120XX21621_*.kicad_sym` (J5/J6 nutzen `Connector_Generic`).

## Zuordnung

| Bauteilordner | Inhalt |
| ------------- | ------ |
| `ESP32-S3-WROOM-1U-N16R8/` *(vorhanden)* | Modul-Footprint + STEP |
| `Power/` *(vorhanden)* | `MP2359DJ`, `USB_C_Receptacle_Amphenol…` |
| `1543-650-149/` | Taster `S2`: Symbol + Footprint |
| `WCAP-FTXX_P10/` | Symbol + Footprint + STEP |
| `WCAP-PT5H/` | Symbol + Footprint |
| `WL-TMRC_3MM/` | Symbol + Footprint + STEP |
| `WL-TMRW_3MM/` | Footprint + STEP (Symbol ist `Device:LED`) |
| `wuerth_6120XX21621/` | Stecker `J5`/`J6`: Footprints + STEPs |
| `W5500/`, `wuerth_7499011121A/` *(vorhanden)* | Ethernet, aus SHBS-5 |

## Aufgaben

1. Bauteilordner anlegen, benötigte Dateien verschieben.
2. Verwaiste Dateien entfernen.
3. `sym-lib-table` und `fp-lib-table` umstellen — je Bauteilordner eine
   Footprint-Bibliothek.
4. Footprint-Referenzen in Schaltplänen, Netzliste und Board umschreiben
   (18 Stück mit Präfix `Footprints:`).
5. Sechs absolute Windows-Pfade der 3D-Modelle im Board auf `${KIPRJMOD}`
   umstellen.
6. `Symbol/`, `Footprints/`, `3D-Model/` löschen.
7. Doku nachziehen.

## Ergebnis (17.09.2026)

20 Dateien verschoben, 13 verwaiste entfernt, `Symbol/`, `Footprints/` und
`3D-Model/` gelöscht.

| Umgeschrieben | Anzahl |
| ------------- | ------ |
| Footprint-Referenzen in Schaltplänen, Netzliste, Board | 63 |
| Footprint-Vorgaben in den Symbol-Dateien | 7 |
| Absolute 3D-Pfade im Board (`E:/Projekte/…`) | 10 |
| Bibliothekspfade in der Netzliste (`C:\Projekte\…`) | 4 |

Die absoluten Pfade standen auf **zwei verschiedenen Laufwerken** — im Board
auf `E:`, in der Netzliste auf `C:`. Beide sind jetzt `${KIPRJMOD}`-relativ.

### Nebenbei behoben

- Drei Footprint-Referenzen zeigten auf Bibliotheken, die gar nicht in der
  `fp-lib-table` standen (`WL-TMRC_3MM:…`, `WCAP-PT5H_6.3X5.2:…`,
  `1543-650-149:…`). Sie lösen jetzt aus dem Repository auf.
- `WCAP-FTXX_P10.kicad_sym` hatte **keine** Footprint-Vorgabe — ergänzt.
- Der ESP32-Footprint zeigte per `${KICAD8_3RD_PARTY}` auf eine
  Drittanbieter-Bibliothek; jetzt auf die lokale STEP-Kopie.
- Der W5500-Footprint hatte **keine** 3D-Referenz — ergänzt.

### Verifikation (textuell)

Automatisch geprüft, alles ohne Befund:

- Jede der 9 Symbol- und 10 Footprint-Bibliotheken zeigt auf einen
  existierenden Pfad.
- Alle 10 projektinternen Footprint-Referenzen lösen auf eine vorhandene
  `.kicad_mod` auf; die übrigen 11 sind KiCad-Standardbibliotheken.
- Alle 13 projektrelativen 3D-Pfade zeigen auf existierende Dateien.
- Keine Reste von `Footprints:`, `E:/Projekte`, `3D-Model/` oder `../Symbol/`
  in den KiCad-Dateien.

### ERC nach der Migration (17.09.2026, 22:15)

**0 Fehler, 7 Warnungen** — vorher 0 Fehler, 9 Warnungen.
**Keine neue Warnung.** Zwei sind entfallen:

| Entfallen | Ursache |
| --------- | ------- |
| `lib_symbol_mismatch` C8 (`WCAP-PT5H_6.3X5.2`) | Bibliothek und eingebettete Kopie wurden auf dieselbe Footprint-Vorgabe gezogen |
| `lib_symbol_mismatch` D7 (`WL-TMRC_3MM`) | ebenso |

Die verbliebenen sieben Warnungen bestanden alle schon vorher:

- 4 × `lib_symbol_mismatch` (S2, C7, C10, C12) — Abweichung zwischen der im
  Schaltplan eingebetteten Symbolkopie und der Bibliothek. Lässt sich in
  Eeschema über *Werkzeuge → Symbole aus Bibliothek aktualisieren* auflösen.
- 1 × `unconnected_wire_endpoint` bei (3350 / 2100 mils) — das bekannte lose
  Leitungsende am `EN`-Netz, bereits in Task `0001_shbs9` vermerkt.
- 1 × `pin_to_pin` S2 Pin 1 gegen `#FLG04` — PWR_FLAG an einem
  bidirektionalen Pin.
- 1 × `multiple_net_names` GND/EPAD an `U6` Pin 41 (versteckter EPAD).

### DRC nach der Migration (17.09.2026, 22:19)

**1 Fehler, 8 Warnungen.** Kein Befund geht auf die Migration zurück:

- **`unconnected_items` (Fehler)** — Routing-Lücke im `EN`-Netz zwischen zwei
  Segmenten auf F.Cu und B.Cu. Dasselbe Netz trägt im ERC das bekannte lose
  Leitungsende (Task `0001_shbs9`). Vom Bediener bewusst zurückgestellt.
- **5 × `lib_footprint_mismatch`** an `R1`–`R5` — allesamt `Resistor_THT` aus
  KiCads globaler Bibliothek, von der Migration nicht berührt.
- 2 × `track_dangling` (`+3V3`, `EN`), 1 × `text_height` an `C3`.

**Entscheidend:** KiCad meldet *„Found 0 Footprint errors"*. Damit ist
bestätigt, dass jeder Footprint auf der Platine in seiner neuen Bibliothek
gefunden wird.

*Einschränkung:* Ein älterer DRC-Bericht zum direkten Vergleich existiert
nicht — `report.txt` ist ein Netzlisten-Importlog. Die Bewertung stützt sich
auf die obigen Punkte.

### Abnahme durch den Bediener (17.09.2026)

| Prüfung | Ergebnis |
| ------- | -------- |
| Projekt öffnen — Bibliotheks-Warnungen | **keine** |
| Schaltplan, ERC | 0 Fehler, 7 Warnungen (vorher 9) |
| PCB öffnen, DRC | öffnet; 1 Fehler, bekannt und zurückgestellt |
| 3D-Ansicht | **Modelle werden angezeigt** — die umgestellten Pfade greifen |

### Offen (nicht blockierend)

- **KiCad-Gegenprüfung durch den Bediener** — im Container ist kein KiCad
  installiert. Projekt, Schaltplan und Board öffnen, auf Bibliotheks-Warnungen
  achten, ERC und DRC laufen lassen.
- `BasisStation.csv` und `report.txt` enthalten noch `Footprints:` — beides
  Export-Artefakte, die beim nächsten BOM- bzw. ERC-Lauf neu erzeugt werden.
- `Bauteile/ESP32-S3-WROOM-1U-N16R8/` enthält Altformate (`.lib`, `.dcm`,
  `.mod`, `.bak`) und den unbenutzten Footprint `ESP32S3WROOM1UN16R8.kicad_mod`
  — auf Wunsch separat aufräumen.
- `Bauteile/wuerth_7499011121A/` enthält **zwei** Symbole für dasselbe Teil
  (offizielles Würth-Symbol und die SnapEDA-Variante). Registriert ist nur das
  offizielle; die SnapEDA-Dateien können weg, sobald das bestätigt ist.

## Akzeptanzkriterien

- [ ] Kein Verweis mehr auf `Footprints:`, `pcb/Symbol/`, `pcb/3D-Model/` oder
      absolute Pfade.
- [ ] Jede Bibliothek in beiden Lib-Tables zeigt auf einen existierenden Pfad.
- [ ] Jeder referenzierte Footprint existiert in der genannten Bibliothek.
- [ ] KiCad öffnet Projekt, Schaltplan und Board ohne Bibliotheks-Warnung.
- [ ] ERC und DRC ohne neue Fehler gegenüber Stand 17.09.2026.

## Betroffene Dateien

- `pcb/Bauteile/**`, `pcb/Symbol/`, `pcb/Footprints/`, `pcb/3D-Model/`
- `pcb/BasisStation/sym-lib-table`, `fp-lib-table`
- `pcb/BasisStation/*.kicad_sch`, `BasisStation.net`, `BasisStation.kicad_pcb`
- `docs/project/hardware.md`, `docs/project/architecture.md`
