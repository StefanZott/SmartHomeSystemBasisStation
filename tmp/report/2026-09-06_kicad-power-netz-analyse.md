---
type: analysis
created: 2026-09-06
jira: SHBS-4
status: draft
---

# KiCad-Analyse: Stromversorgungsblatt und +3V3-Netz

## Ausgangslage

Prüfung, ob KiCad-Dateien maschinell auswertbar sind — verbunden mit einer
Bestandsaufnahme des Schaltplans zum offenen Ticket SHBS-4 (USB-C-Stromversorgung).

Ausgewertet wurden alle `*.kicad_sch`, `BasisStation.net` und `ERC.rpt` unter
`pcb/BasisStation/` mit einem eigenen S-Expression-Parser.

## Ergebnis / Befunde

### B1 — `+3V3` ist ein lokales Label, kein Power-Symbol (kritisch)

`+3V3` existiert als **lokales Label** (`(label "+3V3")`) sowohl in
`Stromversorgung.kicad_sch` als auch in `BasisStation_Layout.kicad_sch`.
Lokale Labels sind in KiCad blattlokal. Die beiden Netze sind damit **getrennt** —
der Buck-Ausgang (PS1) erreicht den ESP32 (U6) nicht.

Bestätigt durch ERC: `power_pin_not_driven` an `U6 Pin 2 [3V3]`.
Bestätigt durch Netzliste: das Netz heißt dort `/Layout/+3V3` (blattqualifiziert).

**Fix:** `+3V3` auf beiden Blättern durch ein Power-Symbol ersetzen — Power-Symbole
sind global. Achtung: setzt B9 voraus (siehe unten), sonst ist `power:+3V3` nicht
auflösbar.

### B2 — `PW_EN` unnötig global (Hygiene, nicht kritisch)

**Korrigiert am 06.09.2026.** Die ursprüngliche Einschätzung („Enable hängt in der Luft,
`PW_EN` und `EN` vereinheitlichen") war falsch — sie hätte zu einem echten
Konstruktionsfehler geführt.

`PW_EN` und `EN` sind **zwei verschiedene Signale**:

| Netz | Blatt | Funktion | Knoten |
|------|-------|----------|--------|
| `PW_EN` | Stromversorgung | Enable des MP2359 (Pin 4) | 2 Labels, beide auf demselben Blatt |
| `/Layout/EN` | Layout | Chip-Enable / Reset des ESP32 (U6 Pin 3) | R9 (10k Pull-up), C7, S2 (Reset-Taster), J6 Pin 1, U6 Pin 3 |

Beide `PW_EN`-Labels liegen auf dem Stromversorgungsblatt; das Enable-Netz ist dort
geschlossen. ERC meldet **keinen** unverbundenen EN-Pin.

Eine Zusammenlegung wäre schädlich: der Reset-Taster S2 würde die eigene
Versorgung abschalten.

**Fix:** Keiner zwingend. Optional `PW_EN` von *global* auf ein lokales Label
zurückstufen, da es blattintern bleibt — verhindert eine spätere versehentliche
Kollision mit einem gleichnamigen globalen Label.

### B3 — Kein PWR_FLAG auf dem Stromversorgungsblatt

`PWR_FLAG` kommt 4x in `BasisStation_Layout.kicad_sch` vor, **0x** in
`Stromversorgung.kicad_sch`. Daher meldet ERC `power_pin_not_driven` für
`PS1 Pin 5 [VIN]` und `J_PWR Pin A4 [VBUS]` — VBUS wird von keinem Power-Output
getrieben, weil die USB-Buchse selbst nur Power-*Input*-Pins hat.

**Fix:** PWR_FLAG an VBUS (hinter F1) und an den 3,3-V-Ausgang setzen.

### B9 — Projektbibliothek `power` verdeckt die KiCad-Standardbibliothek (Blocker für B1)

Die `sym-lib-table` registriert eine **projektlokale** Bibliothek unter dem Namen
`power` (`pcb/Bauteile/Power/power.kicad_sym`). Dieser Name kollidiert mit der
globalen KiCad-Standardbibliothek `power`; die Projektbibliothek gewinnt und enthält
nur zwei Symbole: `MP2359DJ` und `USB_C_Receptacle_Power`.

Folge: `power:GND` (28x) und `power:PWR_FLAG` sind über die Bibliothek **nicht
auflösbar**. Die Symbole werden nur noch aus dem eingebetteten `lib_symbols`-Cache
der jeweiligen `.kicad_sch` gerendert. Das erklärt die 28 ERC-Warnungen
„Symbol GND nicht in Bibliothek power gefunden".

Für B1 heisst das: `power:+3V3` liesse sich derzeit **nicht platzieren**. Die
Umbenennung ist damit Voraussetzung, nicht Kür — und behebt nebenbei 28 der
48 Warnungen.

**Fix:** Projektbibliothek in `sym-lib-table` umbenennen (z. B. `shbs_power`),
`lib_id` der beiden betroffenen Symbole (J_PWR1, PS1) in
`Stromversorgung.kicad_sch` nachziehen.

### B4 — Netzliste ist veraltet

`BasisStation.net` datiert auf 2026-06-09, die Schaltpläne auf 2026-06-17.
Die Netzliste enthält noch `PS2` und das Netz `+12V` und **kein einziges** Bauteil
des Stromversorgungsblatts (J_PWR1, PS1, F1, L1, D11, D12, R17–R20 fehlen).

**Fix:** Netzliste in KiCad neu exportieren, nachdem B1–B3 behoben sind.

### B5 — PCB hinkt dem Schaltplan hinterher

`BasisStation.kicad_pcb` ist von 20:09, die Schaltpläne von 21:46 desselben Tages.
Die Stromversorgungs-Bauteile sind im Layout noch nicht eingelesen.

### B6 — `BasisStation_architektur.kicad_sch` ist verwaist

Format `version 20231120` (KiCad 7/8) gegenüber `20250114` bei allen anderen Blättern.
Die Datei ist **nicht** in der Blatthierarchie von `BasisStation.kicad_sch` eingebunden
(dort nur: Layout, Debugging, Stromversorgung) und enthält keine platzierten Bauteile.

**Empfehlung:** klären, ob Altbestand → entfernen, oder bewusst als Doku-Blatt führen
und dann in `docs/project/hardware.md` erwähnen.

### B7 — Task-Datei 0001 ist nicht mehr aktuell

`tmp/tasks/open/0001_usb-c-12v-stromversorgung.md` führt Task 3 (Schaltplan Power)
als offen und vermerkt die Rücknahme des Skript-Ansatzes. Tatsächlich ist das Blatt
`Stromversorgung.kicad_sch` seit Commit `b89eb9c` vorhanden und manuell gezeichnet
(J_PWR1, PS1, F1, L1, D11, D12, R17–R20, C13–C15).

Die Akzeptanzkriterien 1 und 4 sind faktisch erfüllt, Kriterium 2 (Buck liefert 3,3 V
an `+3V3`) scheitert an B1.

### B8 — Repo-Hygiene: 104 der 108 geänderten Dateien sind reine Zeilenenden

`git diff --ignore-cr-at-eol` zeigt echte Inhaltsänderungen nur in
`.devcontainer/Dockerfile`, `.devcontainer/devcontainer.json`,
`.vscode/settings.json` und `README.md`. Alle KiCad-Dateien sind inhaltlich
unverändert gegenüber HEAD — der Rest ist CRLF-Churn mangels `.gitattributes`.

## Empfehlungen

| Prio | Befund | Massnahme |
| ---- | ------ | --------- |
| 1 | B9 | Projektbibliothek `power` umbenennen — **zuerst**, Voraussetzung für B1 |
| 1 | B1 | `+3V3` als Power-Symbol auf beiden Blättern |
| 4 | B2 | Optional: `PW_EN` auf lokales Label zurückstufen (kein Defekt) |
| 1 | B3 | PWR_FLAG an VBUS und 3V3 setzen |
| 2 | B4, B5 | Netzliste und PCB nach Fix neu erzeugen, ERC/DRC leer fahren |
| 3 | B6 | Verwaistes Architektur-Blatt klären |
| 3 | B7 | Task 0001 fortschreiben |
| 3 | B8 | `.gitattributes` (`* text=auto eol=lf`), Index normalisieren |

## Nächste Schritte

Reihenfolge ist zwingend: **B9 vor B1**, sonst fehlt das Symbol. B9→B1→B3 lösen
gemeinsam 3 der 5 ERC-Fehler sowie 28 der 48 Warnungen. Der vierte Fehler
(C8 Pin 1 unverbunden) ist unabhängig davon zu prüfen, der fünfte (`J_PWR?`
unannotiert) ist bereits erledigt. B2 ist optional. Danach Netzliste und PCB nachziehen (B4/B5).

Offen für den Bediener: ob die Änderungen manuell in KiCad erfolgen (nach der
Erfahrung aus Task 0001, Task 3) oder ob ein gezielter, minimaler Datei-Eingriff
akzeptabel ist — Power-Symbole einzusetzen ist deutlich risikoärmer als das
seinerzeit gescheiterte Einfügen kompletter `lib_symbols`.
