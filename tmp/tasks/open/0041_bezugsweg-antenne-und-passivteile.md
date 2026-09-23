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

- [ ] **Bediener:** Antennenkette entscheiden — Tabelle oben. Da die Bestellung
      ohnehin ueber DigiKey laufen soll, spricht viel fuer den
      Taoglas-Nachfolger `GW.20.A151`: eine Quelle statt zwei, und die Serie ist
      bereits im Schaltplan dokumentiert. Die Reichelt-Option DELOCK 88339 ist
      60 Cent guenstiger, verursacht aber eine zweite Bestellung
- [ ] **Bediener:** Ersatz fuer `J1`/`J_PWR1` waehlen (abgekuendigt). Zuerst
      pruefen, ob ein pinkompatibler Typ existiert — sonst muss der Footprint
      `shbs_power:USB_C_Receptacle_Amphenol_12401548E4-2A` angepasst werden,
      und das betrifft das PCB-Layout
- [~] Hausstandard fuer generische Passivteile — **Vorschlag erstellt**
      (2026-09-23, Bediener hat Vorgehen freigegeben), Einzelteile in
      `PROPOSED_PARTS` ([generate_bom.py](../../bom/generate_bom.py)),
      **Bestaetigung der Einzelteile steht aus**. Urspruenglich:
      Toleranz, Spannungsfestigkeit, Dielektrikum (X7R/C0G), Belastbarkeit.
      Vorrang: `C25`/`C26` am 25-MHz-Quarz (Lastkapazitaet gegen die
      Quarz-Spezifikation rechnen) und die 1-%-Widerstaende im Ethernet-Zweig
- [~] Nennstrom fuer `F1`: stand bereits in power_supply.md (Polyfuse 1,1 A,
      Last ~400 mA). Vorschlag Bourns `MF-NSMF110-2` (1206, 6 V) —
      Bestaetigung steht aus. Traegt im Schaltplan bisher nur den Wert „Fuse"
- [ ] Abgeleitete Teilenummern am Datenblatt bestaetigen: `D11`, `D12`, `U1`,
      `L1`, `J6`
- [ ] Entschiedene Teile als Felder in den Schaltplan eintragen (GUI), damit
      der naechste Export sie traegt
- [x] `generate_bom.py` erneut laufen lassen, Mappe pruefen *(2026-09-23:
      46/46 Positionen bepreist, 49,30 EUR, LibreOffice 0 Formelfehler)*
- [ ] Commit

**J1/J_PWR1 — Stand 2026-09-23:** Vorschlag Amphenol `12401598E4#2A`
(Mouser-Nachfolgeempfehlung, laut DigiKey gleiche Bauart 24P Hybrid).
Zeichnung von amphenol-cs.com aus dem Container nicht abrufbar (HTTP 403) —
**Bediener muss das Padbild gegen den Footprint pruefen**. GCT `USB4110-GF-A`
scheidet aus (16P, reine SMD-Buchse).

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

## Commits

- d1870af Befunde zu Abkuendigungen dokumentiert (Teilschritt, Task noch offen)

## Offene Fragen

- Soll die Mischbestueckung (22 THT-Teile) bei dieser Gelegenheit reduziert
  werden? Betrifft vor allem `Q1`-`Q4` und die Widerstaende im
  DIN0617-Footprint. Eigenes Thema, aber die Teileauswahl haengt daran.
