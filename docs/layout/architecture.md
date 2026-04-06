# Layout / Hardware — Architektur

Dokumentationsstand: Initial-Workflow abgeschlossen (2026-04-06), Stand Repository.

## Architekturdiagramm

Logischer Systemüberblick (Zielbild laut `AGENTS.md`). **Nur Standard-Markdown:** Diagramm als Text im Code-Block (kein Mermaid).

```text
Stromversorgung              Rechenkern / Peripherie
─────────────────            ─────────────────────────────────────────

  [DC/DC, z. B. TSR 1-2433E
   auf 3,3 V] ──────────────► ESP32-S3-WROOM-1U-N16R8
                                      │
  [Power- / Reset-Taster] ────────────┤
                                      ├──► [4 LEDs, RGBY]
  [USB]  ─────────────────────────────┤
  [PROG] ─────────────────────────────┤
  [JTAG] ─────────────────────────────┤
                                      ├──► [WLAN-Antenne am Modul 1U]
                                      │
                                      └──► [Ethernet]  (Ziel laut Projektkontext; KiCad / Firmware-Stand siehe unten)
```

## Zielbild (laut Projektkontext)

Smart-Home-Basisstation auf Basis **ESP32-S3-WROOM-1U-N16R8** mit Tastern, USB/PROG/JTAG, WLAN-Antenne, vier LEDs und **Ethernet** als Schnittstelle.

## Repository-Ist-Stand (KiCad)

| Bereich | Pfad / Artefakt |
|--------|------------------|
| Hauptprojekt | `PCB/BasisStation/BasisStation.kicad_pro` |
| Schaltpläne | u. a. `BasisStation.kicad_sch`, `BasisStation_Layout.kicad_sch`, `BasisStation_Debugging.kicad_sch`, `BasisStation_architektur.kicad_sch` |
| Leiterplatte | `BasisStation.kicad_pcb` |
| Symbole / Footprints | `PCB/Symbol/`, `PCB/Footprints/` |
| Bauteilbibliothek MCU | `PCB/Bauteile/ESP32-S3-WROOM-1U-N16R8/` |
| Architektur-Diagramm (extern) | `PCB/architektur_basisStation.drawio` |

## Stückliste (README)

Die zentrale Stückliste mit Links und Preisen steht in `README.md` (Abschnitt „Hardware“). **Hinweis:** In der Tabelle sind teils unterschiedliche Modulbezeichnungen genannt (z. B. WROOM-2 vs. 1U-N16R8); die in `AGENTS.md` genannte Ziel-MCU ist **ESP32-S3-WROOM-1U-N16R8** — Abgleich BOM ↔ Schaltplan bei Änderungen empfohlen.

## Abgrenzung Firmware

Die Firmware in `main/` beschreibt das **Laufzeitverhalten** (WLAN, Webserver, LEDs). Ob und wie **Ethernet** auf der Platine angebunden ist, ergibt sich aus dem KiCad-Projekt; in der aktuellen Firmware (`main/`) gibt es **keine** Ethernet-Treiber-Nutzung (Stand Initial-Analyse).

## Pflege

Änderungen an Schaltplan, BOM oder Schnittstellen hier und in `communication.md` nachziehen.
