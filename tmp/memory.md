---
type: session-handover
created: 2026-09-26
status: active
---

# Session-Übergabe: PCB-Layout BasisStation

Stand für die Weiterarbeit auf einem anderen Rechner. In einer neuen
Agenten-Session diese Datei zuerst lesen, danach Task
[0047](tasks/done/0047_pcb-layout-stromversorgung-leds.md) und den
[Review-Report](report/2026-09-24_pcb-review-stromversorgung-leds.md).

## Stand 2026-09-29 (neueste Session)

- **Gesamt-Layout fertig** (SHBS-23, SHBS-10): U6 rechts oben, W5500 neben
  T1, alle Netze geroutet, GND nachgearbeitet. DRC: 0 offen, 0 Parität, nur
  15 begründete Ausschlüsse. Details: `docs/project/hardware.md`, Abschnitte
  „Gesamt-Layout" und „DRC: Regeln und Ausschlüsse".
- Obere Platinenkante bei y 27,45: J_PWR1, J1 und T1 stehen 1,2–1,3 mm über
  (Vorbereitung Gehäuse).
- Werkzeuge: Freerouting 2.4.1 und Java 25 lagen nur im Scratchpad der
  Session und sind auf einem neuen Rechner nicht vorhanden. `pcbnew` gibt es
  unter `/usr/bin/python3`, nicht im ESP-IDF-Python.
- Achtung: Das Projektverzeichnis liegt auf einem Windows-Laufwerk (Ordner
  heißt real `PCB/`). Neue Dateien immer als `pcb/...` zu git hinzufügen.
- **3D-Modelle vollständig** (SHBS-24): Würth-STEPs für C7/C10/C12/J6 mit
  Z-Versatz 6 / 4,5 mm, Würth-LEDs, KiCad-Modell für C8 und PS1.
- **S2 von außen bedienbar** (SHBS-25): liegender C&K PTS645VL58-2 LFS an der
  Buchsenseite, Stößel bündig mit 2-mm-Gehäusewand (Spitze 2,0 mm vor der
  Kante). Mouser 611-PTS645VL582.
- Schaltplan fertig (ERC 0 Fehler), PCB fertig (DRC 0 offen, 0 Parität),
  Stückliste aktuell. Alles auf `origin/main` gepusht.
- Offen: Fertigungsdaten (Gerber/Bohr/Bestückung), Gehäuse, Prototyp-Tests
  (Flashen über J1 = SHBS-6, Quarzfrequenz, Ethernet), Firmware Ethernet
  (SHBS-11). Optional: LED-Widerstände kleiner, Footprint-Name PS1.
- Git-Push aus der Agenten-Shell hängt, wenn VS Code seit Start der Shell neu
  gestartet wurde (veralteter Anmeldehelfer). Abhilfe: VS Code neu starten
  bzw. neue Shell, dann `GIT_TERMINAL_PROMPT=0 timeout 120 git push`.

## Git

- `fix/usb-c-jpwr1-pins` ist über PR #1 und #2 nach `main` gemergt.
  Weitergearbeitet wird auf `main` (Stand 2026-09-27).
- Auf einem anderen Rechner: `git switch main && git pull --ff-only`.

## Tickets

| Ticket | Thema | Status |
|--------|-------|--------|
| **SHBS-20** | USB-C J_PWR1: Pins B4/B9 (VBUS), A12/B12 (GND) fehlten im Symbol | erledigt, Abschlusskommentar in Jira. Ticket-Status setzt der Bediener. Task [0046](tasks/done/0046_usb-c-jpwr1-pins-ergaenzen.md) |
| **SHBS-21** | PCB-Layout Stromversorgung und Status-LEDs | erledigt 2026-09-27 (Tasks [0047](tasks/done/0047_pcb-layout-stromversorgung-leds.md), [0048](tasks/done/0048_pcb-power-leitungen-aufweiten-drc-ausschluesse.md)), Abschlusskommentar in Jira. Ticket-Status setzt der Bediener |
| SHBS-10 | Ethernet-Layout | unberührt, bewusst getrennt von SHBS-21 |

## Was in der Session passiert ist

1. **LED-Pinwahl:** Frage, ob Rot (GPIO38, Pad 31, rechte Modulseite) an die
   Unterseite wandern kann. Ergebnis: An der Unterseite sind nur noch die
   Strapping-Pins GPIO3/45/46 frei. **Entscheidung: GPIO38 bleibt**, die
   Leiterbahn wird um die Ecke geführt (Pads 28–30 sind PSRAM, dort ist frei).
2. **PWR_FLAG / KiCad-Bedienung:** `P` funktioniert nur im Schaltplan-Editor,
   nicht im PCB-Editor.
3. **PCB-Review** (Report, Befunde B1–B6). Die Zonenfüllung war veraltet,
   rund 490 DRC-Meldungen waren Artefakte. Nach `B` blieben 75 übrig.
4. **Punkt 1 / SHBS-20 erledigt:** Symbol ergänzt (gestapelt, unsichtbar,
   `passive`). Der Bediener hat im PCB angebunden: B4→A9, B9→A4, B12→A1,
   B1→S1 links, B12→S1 rechts, A12→GND-Via (69,0 / 38,0).
5. **Punkt 2 erledigt (SHBS-21):** Netzklasse `Power` (0,6 mm, Via 0,8/0,4)
   mit Mustern VBUS, +5V, SW, +3V3, GND. Schaltknoten per Label `SW` benannt,
   F8 im PCB ist erfolgt (`/Stromversorgung/SW`). Details siehe
   `docs/project/power_supply.md`, Abschnitt „Netzklasse `Power`".
6. **Punkt 3 erledigt (2026-09-26):** Der Agent hat den Buck-Wandler per
   Skript in der `.kicad_pcb` umplatziert und neu geroutet (Details in Task
   0047, Fortschritt 2026-09-26). SW-Leitung ca. 9,2 mm. Der Bediener muss
   im PCB-Editor noch `B` drücken und speichern, noch nicht committet.

## Referenz: Punkt 3 — Planung Buck-Wandler (umgesetzt, L1/C14 um 0,3/0,6 mm tiefer)

PS1 bei (66 / 53,5), Pins von oben gesehen: oben SW, IN, EN — unten BST,
GND, FB. Die heiße Schleife C13(+) → IN → SW → D11 → GND → C13(−) klein
halten.

| Bauteil | Ziel | Abstand zu PS1 vorher |
|---------|------|----------------------:|
| C13 | quer direkt über PS1, +5V-Pad nahe IN, GND-Via | 10,7 mm |
| D11 | links oben, Kathode zu SW, Anode (GND) Richtung C13-GND | 10,3 mm |
| C15 | **(63,3 / 53,5), Drehung 90°** — Pads liegen dann auf Höhe SW/BST | 9,0 mm |
| L1 | direkt an D11-Kathode | 17,7 mm |
| C14 | am L1-Ausgang, GND nahe D11/C13 | 16,1 mm |
| R17/R18 | am FB-Pin, weg von SW/L1; R17 an +3V3 hinter C14 | — |

GND-Vias an C13(−), D11-Anode, PS1-GND und C14(−). SW-Leitung vorher
40,7 mm, **Ziel < 10 mm**. Nach dem Speichern misst der Agent Abstände und
Leitungslängen per Skript aus der `.kicad_pcb` nach.

## Danach offen (aus dem Review / Task 0047)

- ~~+3V3 zu U6.2 und zu den LED-Anoden D7–D10 routen (B4)~~ erledigt 2026-09-26 durch den Agenten, Details in Task 0047.
- ~~Versorgungsleitungen aufweiten, DRC-Ausschlüsse J_PWR1~~ erledigt
  2026-09-27 (Task 0048).
- J1 (Debug-USB) hat dieselben 2 Kantenabstands-Meldungen zum NPTH wie
  J_PWR1 — noch nicht ausgeschlossen.
- Optional: LED-Widerstände R13–R16/R23–R26 sind 2-W-Typen (PR02, 20 mm
  Raster), 0207 oder 0805 würden reichen (Entscheidung Bediener).
- Kosmetik: Footprint PS1 heißt noch `MP2359DJ`, 4 Montagelöcher ohne
  Symbol, GND-Stummel bei (21,76 / 90,33), doppelte Referenz „J_PWR1".

## Hinweise für den Agenten

- **KiCad muss geschlossen sein**, bevor der Agent `.kicad_pro`,
  `.kicad_sch` oder `.kicad_sym` ändert. Kontrolle: keine `~*.lck`-Dateien
  in `pcb/BasisStation/`. Danach Projekt in KiCad neu öffnen.
- `kicad-cli` (9.0.9) kann Zonen **nicht** neu füllen, und das Python-Modul
  `pcbnew` ist im Container nicht installiert. Vor einem DRC per CLI muss der
  Bediener im PCB-Editor `B` drücken und speichern.
- Die Netzliste von `kicad-cli sch export netlist` zeigt keine
  Netzklassen-Muster an. Prüfen lassen sich die Muster per DRC-Probe in einer
  Kopie (Abstand der Klasse testweise groß setzen).
- Versionierung: Hardware-Änderungen → **keine** Versionserhöhung (bleibt
  `v0.00.001`), keine Release Notes.
