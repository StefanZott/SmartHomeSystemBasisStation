---
title: PCB — Ethernet (W5500, Quarz, Beschaltung) platzieren, kritische Leitungen routen
created: 2026-09-27
jira: SHBS-10
priority: high
type: feature
status: done
---

## Kontext

Ethernet-Sektion laut SHBS-10 (siehe `docs/project/ethernet.md`). T1 bleibt
an seiner Position. U6 wandert nach rechts oben (Task 0050).

## Ziel

U7 dicht an T1, Y1 dicht an U7, Abblockung an den Pins, TX±/RX± als
Paare kurz und gleich lang, Chassis-GND unter T1 getrennt (Kopplung nur über
R35 ‖ C28), SPI-Bündel zu U6 Pads 17–22.

## Schritte

- [x] Platzierung U7, Y1, C16–C32, R27–R40, FB1, C28/R35
- [x] TX±/RX± per Skript als Paare routen
- [x] Quarz- und Versorgungsleitungen, SPI zu U6
- [x] Chassis-Zone unter T1
- [x] DRC, Doku (`hardware.md`, Lagenaufbau)

## Fortschritt

- 2026-09-27: Task angelegt.

- 2026-09-27: TX/RX per Skript geroutet und gesperrt (RX durch den Kanal
  zwischen den T1-Pad-Reihen, C29/C30 versetzt). Chassis-Zone angelegt.
- 2026-09-29: R36/R37 angebunden (R36 über Via-Paar). Quarz, SPI und
  Versorgung per Freerouting. U7-GND-Pins 3/9/16/23 und +3V3A unter dem
  Gehäuse von Hand nachgearbeitet. Doku in `hardware.md` (Gesamt-Layout).
  Offen: Sichtprüfung und DRC-Ausschlüsse (Task 0052).

- 2026-09-29: Nach der Umplatzierung neu geroutet, U7-GND-Pins und RXN → R40
  von Hand. DRC sauber. Die PCB-Datei ist nicht teilbar, der Stand liegt daher
  im SHBS-23-Commit (siehe Commits). Task abgeschlossen.

## Commits

- d2fd4e2 (SHBS-23) Ethernet-Layout im Gesamt-Layout-Commit enthalten

## Offene Fragen

- Keine.
