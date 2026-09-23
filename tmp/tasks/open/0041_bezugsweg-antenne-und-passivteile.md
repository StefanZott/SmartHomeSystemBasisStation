---
title: Bezugsweg fuer Antennenkette und Passivteile festlegen
created: 2026-09-22
jira: SHBS-17
priority: high
type: feature
---

## Kontext

Zwei Luecken in der Stueckliste brauchen eine Entscheidung, keine weitere
Recherche — die Fakten liegen vor
([Reichelt-Report](../../report/2026-09-22_reichelt-verfuegbarkeit.md),
[Mouser-Report](../../report/2026-09-22_mouser-abgleich-stueckliste.md)).

**Antennenkette:** `ANT2` (Taoglas GW.20.5150) ist abgekuendigt. Der
Seriennachfolger ist aber bei Mouser verfuegbar — die urspruengliche Annahme
„kein Bezugsweg" war zu weit gefasst und gilt nur fuer die alte Nummer.

Konkrete Optionen, alle 2 dBi / 2,4 GHz / RP-SMA(M) gerade und damit passend
zum Pigtail `CAB.6061`:

| Option | Quelle | Preis @1 | Lager |
| ------ | ------ | -------- | ----- |
| `960-GW.20.A151` (Taoglas, schwarz) | Mouser | 8,46 € | 650 |
| `960-GW.20.A151W` (Taoglas, weiss) | Mouser | 8,27 € | 480 |
| **DELOCK 88339** | Reichelt | **7,95 €** | ab Lager |
| DELOCK 12006 (baugleich, teurer) | Reichelt | 14,95 € | ab Lager |

Der Pigtail `ANT1` ist unkritisch: `960-CAB.6061`, 4,47 €, 845 ab Lager.

**Zusaetzlich abgekuendigt: `J1`/`J_PWR1`.** Die Amphenol-Buchse
`12401548E4#2A` ist laut DigiKey „no longer manufactured". Das erklaert den
Lagerbestand 0 bei Mouser. Anders als bei der Antenne haengt hier ein
**Footprint** dran — ein Ersatz muss pinkompatibel sein oder der Footprint wird
angepasst.

**Passivteile:** 29 Positionen ohne Teilenummer. Bei Reichelt durchgaengig
verfuegbar (allein 632 Treffer fuer „Widerstand SMD 0805"), es fehlt nur die
Spezifikation.

## Ziel

Fuer jede offene Position steht fest, welches konkrete Teil bei welchem
Distributor bestellt wird. Danach genuegt ein Lauf von `generate_bom.py`, um
Preise und Lagerbestaende nachzuziehen.

## Schritte

- [x] Antennenkette: Schaltplan traegt bereits den Taoglas-Nachfolger
      `GW.20.A151` (Umstellung SHBS-16); in der Stueckliste bei beiden
      Distributoren ab Lager
- [x] Ersatz fuer `J1`/`J_PWR1`: Bediener hat `12401598E4#2A` gewaehlt
      (2026-09-23). **Nicht** pad-kompatibel (B-Reihe SMD statt THT) — neuer
      Footprint `shbs_power:USB_C_Receptacle_Amphenol_12401598E4-2A` angelegt,
      Schaltplan (J1, J_PWR1, Symbol-Cache, `power.kicad_sym`) umgestellt,
      ERC 0 Fehler. PCB-Layout ist aelter als der Schaltplan und muss ohnehin
      neu aus dem Schaltplan aktualisiert werden
- [x] Ersatz fuer `PS1` (MP2359 NRND, kein Lager): Diodes `AP3211KTR-G1`,
      pinkompatibel, gleicher Footprint, vom Bediener freigegeben
      (2026-09-23). Symbol `shbs_power:AP3211` (umbenannt), Felder im
      Schaltplan und in `power.kicad_sym` umgestellt, ERC 0 Fehler, Netzliste
      unveraendert. L1-Saettigung (4,6 A) gegen Strombegrenzung (max. 2,4 A)
      geprueft
- [x] Hausstandard fuer generische Passivteile — Vorschlag vom Bediener
      insgesamt freigegeben (2026-09-23, „alle aufeinmal freigeben"). Standard
      dokumentiert in [hardware.md](../../../docs/project/hardware.md).
      `C25`/`C26` gegen C_L 18 pF von `Y1` nachgerechnet (27 pF passt)
- [x] `F1`: Bourns `MF-NSMF110-2` (1206, 1,1 A, 6 V) gemaess power_supply.md,
      freigegeben; Wert im Schaltplan von „Fuse" auf „1.1A" gesetzt
- [ ] Abgeleitete Teilenummern am Datenblatt bestaetigen: `D11`, `D12`, `U1`,
      `L1`, `J6`
- [x] Entschiedene Teile als Felder in den Schaltplan eingetragen
      (2026-09-23, per Skript statt GUI): 29 Positionen / 58 Instanzen mit
      `Manufacturer`, `Manufacturer_Part_Number`, `Mouser Part Number`.
      Gegenprobe: keine Felder verloren, Pins und Positionen unveraendert,
      Netzliste identisch (102 Netze), ERC 0 Fehler. `PROPOSED_PARTS` geleert
- [x] `generate_bom.py` erneut laufen lassen, Mappe pruefen *(2026-09-23:
      Gruppierung jetzt nach Teilenummer → 44 Positionen, alle bepreist und
      lieferbar, 47,78 EUR, LibreOffice 0 Formelfehler)*
- [ ] Commit

**J1/J_PWR1 — Stand 2026-09-23:** Umgestellt auf Amphenol `12401598E4#2A`.
Die Zeichnung von amphenol-cs.com ist aus dem Container nicht abrufbar (HTTP
403); das Padbild wurde stattdessen aus dem Amphenol-STEP-Modell (via DigiKey)
ermittelt und deckt sich mit dem KiCad-Footprint der Schwester `12401610E4-2A`.
Details in [power_supply.md](../../../docs/project/power_supply.md).
GCT `USB4110-GF-A` scheidet aus (16P, reine SMD-Buchse).

## Nicht Teil dieses Tasks

`U6` bleibt bei `ESP32-S3-WROOM-1U-N16R8` ueber Mouser. Reichelt fuehrt nur die
`-1`-Variante mit PCB-Antenne; ein Wechsel waere eine Designaenderung, keine
Beschaffungsentscheidung, und muesste als eigenes Thema laufen.

## Fortschritt

- 2026-09-22: Task angelegt, noch nicht begonnen. Wartet auf die
  Entscheidungen des Bedieners (Schritte 1 bis 3).

- 2026-09-23 (2): Bediener hat den Hausstandard-Vorschlag freigegeben
  („mach das so"). 30 Positionen mit Teilevorschlag eingetragen und bei Mouser und DigiKey
  geprueft, jeweils auf Lagerbestand ausgewichen (u. a. 10 µF 0805: fast alle
  gaengigen Typen bei beiden Anbietern Lager 0 → Samsung CL21B106KOQNNNE).
  Quarz-Lastkondensatoren gegen Y1 (CL 18 pF) nachgerechnet: 27 pF passt.
  Offen: Bestaetigung der Vorschlaege, Padbild-Pruefung J1, Ersatz PS1,
  Uebernahme in den Schaltplan.

- 2026-09-23 (3): J1/J_PWR1 auf `12401598E4#2A` umgestellt (Footprint neu,
  Schaltplan angepasst). PS1-Ersatz `AP3211KTR-G1` gefunden, bei Mouser und
  DigiKey ab Lager — ein dritter Distributor ist nicht noetig. Stueckliste:
  46/46 Positionen lieferbar, 47,78 EUR.
- 2026-09-23 (4): PS1 im Schaltplan auf AP3211 umgestellt. Nebenbei
  Formelfehler in power_supply.md korrigiert (V_FB 0,81 V statt 0,6 V).
  Offen: Freigabe der 29 Teilevorschlaege, Uebernahme in den Schaltplan,
  abgeleitete Nummern (D11, D12, U1, L1, J6) am Datenblatt bestaetigen.

## Commits

- d1870af Befunde zu Abkuendigungen dokumentiert (Teilschritt, Task noch offen)
- 14ac68d Teilevorschlaege fuer alle offenen Stuecklistenpositionen (Teilschritt)
- 5f9b9d6 USB-C-Buchse auf 12401598E4#2A umgestellt (Teilschritt)
- 5547305 PS1 auf AP3211 umgestellt (Teilschritt)

## Offene Fragen

- Soll die Mischbestueckung (22 THT-Teile) bei dieser Gelegenheit reduziert
  werden? Betrifft vor allem `Q1`-`Q4` und die Widerstaende im
  DIN0617-Footprint. Eigenes Thema, aber die Teileauswahl haengt daran.
