---
status: open
priority: high
type: feature
created: 2026-06-08
jira: SHBS-5
parent_jira: SHBS-3
---

# Ethernet-Schnittstelle hinzufügen

## Ziel

Eine **kabelgebundene Ethernet-Schnittstelle** auf der Basisstation-Platine implementieren. Ethernet ist laut Projektziel (`docs/project/hardware.md`, `docs/project/architecture.md`) vorgesehen, im KiCad-Layout aber noch nicht umgesetzt.

## Ist-Stand

- Dokumentation listet Ethernet als Ziel-Schnittstelle.
- Firmware: keine `ETH_`-Nutzung in `main/` (rein Hardware-Task, Firmware-Follow-up separat).
- ESP32-S3-WROOM-1U-N16R8: RMII-fähig; externer PHY (z. B. LAN8720, IP101) + RJ45/Magnetics üblich.

## Aufgaben

1. Architektur festlegen: RMII-PHY + RJ45 mit integrierten Magnetics (oder RJ45 + discrete Magnetics).
2. GPIO-/RMII-Pinbelegung gegen ESP32-S3-Datenblatt und bestehende Belegung im Layout prüfen (Konflikte mit LEDs, Tastern, SPI, JTAG).
3. Schaltplan ergänzen: PHY, RJ45, Takt (25 MHz), Entkopplung, Strapping, Reset-Leitungen.
4. PCB-Layout: differenzielle Paare RMII, Impedanzkontrolle Ethernet-Leitungen, Antennen-/EMC-Abstand zum ESP32-Modul.
5. ERC/DRC und Netlist-Export ohne Fehler.

## Akzeptanzkriterien

- [ ] RJ45 (oder vergleichbarer Ethernet-Port) auf der Platine platziert und geroutet.
- [ ] RMII-Verbindung ESP32-S3 ↔ PHY vollständig im Schaltplan.
- [ ] PHY und Magnetics in BOM eingetragen.
- [ ] Pinbelegung in `docs/project/hardware.md` dokumentiert (inkl. Hinweis: Firmware noch offen).
- [ ] Architektur-Diagramm `pcb/architektur_basisStation.drawio` bei Bedarf aktualisiert.

## Betroffene Dateien

- `pcb/BasisStation/BasisStation_Layout.kicad_sch` (ggf. `BasisStation_architektur.kicad_sch`)
- `pcb/BasisStation/BasisStation.kicad_pcb`
- `pcb/BasisStation/BasisStation.net`
- `docs/project/hardware.md`
- `docs/project/communication.md` (kurzer Verweis auf Hardware-Stand)
