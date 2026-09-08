---
type: analysis
created: 2026-06-12
jira: SHBS-4
status: draft
---

# SHBS-4 — USB-C Power-Eingang: Ist-Analyse

## Ausgangslage

Task `tmp/tasks/open/0001_usb-c-12v-stromversorgung.md`: +12-V-Versorgung über globale `+12V`-Labels durch USB-C ersetzen.

## Power-Kette (Ist)

```
[+12V] (virtuell, 2× power:+12V + PWR_FLAG) ──► PS2 (+VIN)
                                                    │
                                              TSR 1-2433E
                                                    │
                                                    ▼
                                              +3V3 ──► U6, LEDs, J5/J6, …
```

| Netz | Verbraucher |
|------|-------------|
| `+12V` | **nur** PS2 Pin 1 (`+VIN`) |
| `/Layout/+3V3` | U6, LEDs, Stecker, Entkopplung |
| `/Debugging/5VUSB` | separater Pfad J1 → U1 (ESD), **nicht** Hauptversorgung |

**Fazit:** `+12V` hat heute **keinen physischen Eingang** — nur Netzlabels und `PWR_FLAG` (#FLG04 bei PS2).

## PS2 — TSR 1-2433E (Traco)

- Ausgang: **3,3 V / 1 A**
- Eingang laut Datenblatt Traco TSR-1-Serie: typ. **6,5–32 V DC** (wide input)
- **5 V USB-C allein reicht nicht** für PS2 ohne Zwischenstufe

## Task 1 — USB-C-Receptacle (Vorschlag)

| Merkmal | Wahl |
|---------|------|
| Stecker | **GCT USB4110-GF-A** (Mid-mount USB-C, USB 2.0, VBUS/CC) |
| KiCad | Standardbibliothek `Connector_USB:USB_C_Receptacle_USB2.0` (oder projektspezifischer Footprint-Klon unter `pcb/Footprints/`) |
| Rolle | **Nur Power** (kein USB-Daten auf diesem Port; Debug bleibt SHBS-6 / J1) |
| CC | Abhängig von Task-2-Entscheidung (Rd vs. PD-IC) |

Alternativen gleichwertig: Amphenol 12401598E4#2A, Molex 105444-0001.

## Task 2 — Architektur-Optionen

| Option | Pfad | PS2 | BOM | Ladegerät |
|--------|------|-----|-----|-------------|
| **A — USB-PD 12 V** | USB-C → PD-Sink (z. B. **CH224K**) → `+12V` | unverändert | PD-IC + USB-C | PD-Netzteil 12 V |
| **B — 5 V + Boost** | USB-C (Rd) → 5 V → Boost **5→12 V** → `+12V` | unverändert | Boost + USB-C | Jedes USB-Netzteil |
| **C — 5 V direkt** | USB-C → 5 V → neuer **5→3,3 V** Buck, PS2 entfällt | **ersetzen** | Buck statt PS2 | Jedes USB-Netzteil |

**Empfehlung:** ~~**Option A**~~ → **Entscheidung Bediener (2026-06-12): Option C**

## Entscheidung Option C (festgelegt)

- USB-C **5 V** (CC-Rd 5,1 kΩ), kein PD
- Buck **5 V → 3,3 V** ersetzt PS2 (TSR 1-2433E)
- Netz `+12V` entfällt; `+3V3` bleibt

## Nächste Tasks (nach Entscheidung Task 2)

3. Schaltplan: USB-C + PD/Boost + Schutz (Polyfuse, TVS, ggf. Verpolungsschutz) → `+12V`
4. PCB-Layout
5. ERC/DRC

## Offene Punkte

- Strombedarf Gesamtsystem auf 1 A @ 3,3 V prüfen (PS2-Limit)
- Abgrenzung SHBS-6: separater Debug-USB-C, kein VBUS-Parallelbetrieb ohne Konzept
