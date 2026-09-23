---
type: analysis
created: 2026-09-23
jira: SHBS-17
status: final
---

# DigiKey: Zugang und Abdeckungsprüfung

## Ausgangslage

Der Bediener hat sich für DigiKey als Bestellquelle entschieden und den
API-Zugang eingerichtet. Diese Analyse beantwortet zwei Fragen: Funktioniert
der Zugang, und bekommen wir dort alle Teile?

Zugangsdaten liegen unter `secrets/digikey_api.json` (Rechte 600, über
`secrets/*` git-ignoriert). Client: [digikey.py](../bom/digikey.py).

## Ergebnis / Befunde

### B1 — Zugang funktioniert

| Prüfung | Ergebnis |
| ------- | -------- |
| Token-Endpunkt (`/v1/oauth2/token`) | HTTP 200, Bearer, **599 s gültig** |
| Product Information V4 | HTTP 200, deutscher Shop, **EUR-Preise**, deutsche Statustexte |
| Ein Kreditkonto war **nicht** nötig | die offene Frage aus Task 0040 ist damit beantwortet |

Der 2-legged-Flow (Client Credentials) genügt, wie erwartet. Die Token-Laufzeit
von rund zehn Minuten ist kürzer als ein vollständiger BOM-Lauf — der Client
holt das Token deshalb bei Bedarf neu, nicht einmal pro Lauf.

### B2 — Abdeckung der 17 identifizierten Positionen

Geprüft wurden alle Positionen mit bekannter Herstellerteilenummer. Die
übrigen 29 sind generische Passivteile ohne Teilenummer; für sie ist die Frage
nicht „führt DigiKey das", sondern „welches Teil nehmen wir" (Task 0041).

**Aktiv und bestellbar (14):**

| Position | DigiKey-Nr. | Lager | Preis |
| -------- | ----------- | ----- | ----- |
| `ANT1` CAB.6061 | `931-CAB.6061-ND` | 897 | 4,45 € |
| `ANT2` GW.20.A151 | `931-GW.20.A151-ND` | **59** | 8,42 € |
| `C7`/`C10`/`C12` | `732-5833-ND` | 2491 | 0,35 € |
| `C8` | `732-870235673001CT-ND` | 3000 | 1,35 € |
| `D7` | `732-5009-ND` | 3781 | 0,15 € |
| `J6` | `732-5394-ND` | 21047 | 0,43 € |
| `L1` | `SRN6045TA-100MCT-ND` | 4364 | 0,40 € |
| `T1` | `732-4509-5-ND` | 2678 | 5,92 € |
| `U6` ESP32-S3-WROOM-1U-N16R8 | `1965-…-ND` | **78** | 5,79 € |
| `U7` W5500 | `1278-W5500CT-ND` | 62872 | 2,97 € |
| `Y1` | `1923-830059532CT-ND` | 3667 | 0,75 € |
| `U1` **D3V3XA4B10LP-7** | `31-D3V3XA4B10LP-7TR-ND` | 11467 | — |
| `D11` SS34 | mehrere Hersteller, z. B. Comchip `SS34-HF` | 53701 | — |
| `D12` SMAJ5.0A | mehrere Hersteller, z. B. Littelfuse | 167866 | — |

**Eine echte Lücke (1):**

`S2` (Bourns `1543-650-149`) ist bei DigiKey **nicht zu bekommen** — weder über
die Teilenummer noch über drei verschiedene Stichwortsuchen. Mouser führt ihn:
`652-1543-650-149`, 412 ab Lager, 1,17 €.

**Abgekündigt, unabhängig vom Distributor (2):**

| Position | DigiKey-Status | Lager |
| -------- | -------------- | ----- |
| `J1`/`J_PWR1` Amphenol `12401548E4#2A` | **Obsolet** | 0 |
| `PS1` MPS `MP2359DJ-LF-Z` | **Nicht für Neukonstruktionen** | 0 (alle drei Verpackungsvarianten) |

Bei `PS1` ist auch die Schwestervariante `-P` NRND und bei 0. Das ist also kein
Beschaffungs-, sondern ein Abkündigungsproblem: **beide Teile brauchen Ersatz**,
und bei beiden hängt ein Footprint dran.

### B3 — Methodischer Hinweis, zum zweiten Mal

Die erste Durchsicht meldete vier Positionen als „nicht gefunden": `D11`,
`D12`, `S2`, `U1`. Drei davon waren **Suchartefakte**:

- `D11`/`D12` tragen generische Typbezeichnungen, die es von mehreren
  Herstellern gibt — die Teilenummernsuche verlangt aber eine exakte,
  herstellergebundene Nummer.
- `U1` war als `D3V3XA4B10LP` hinterlegt; bestellbar ist nur `D3V3XA4B10LP-7`.

Nur `S2` blieb nach der Gegenprobe übrig. Derselbe Fehler war zuvor schon bei
`ANT2` passiert (siehe [Mouser-Report](2026-09-22_mouser-abgleich-stueckliste.md),
Nachtrag). **Regel: Eine erfolglose Teilenummernsuche ist erst nach einer
Stichwortsuche über Hersteller und Serie ein Befund.**

### B4 — DigiKey ist nicht überall die bessere Quelle

Bei zwei Positionen ist Mouser deutlich besser bevorratet:

| Position | DigiKey | Mouser |
| -------- | ------- | ------ |
| `ANT2` | 59 | **650** |
| `U6` | 78 | **6174** |

Preislich nehmen sich beide wenig (`U6`: 5,79 € gegen 5,93 €). Für eine
Serienbestellung ist der Lagerbestand das stärkere Argument.

## Empfehlungen

1. **Bestellung überwiegend über DigiKey**, wie entschieden — 14 von 17
   identifizierten Positionen sind dort aktiv und verfügbar.
2. **`S2` über Mouser** beziehen oder auf einen bei DigiKey geführten Taster
   wechseln. Ein Wechsel berührt den Footprint `1543-650-149:1543650149`.
3. **`PS1` und `J1`/`J_PWR1` ersetzen** — das ist die dringendste Aufgabe. Beide
   sind abgekündigt beziehungsweise NRND und nirgends bevorratet, und beide
   hängen an einem Footprint, also am Layout.
4. **`U1` im Schaltplan auf `D3V3XA4B10LP-7` korrigieren**, sonst findet jede
   Abfrage weiterhin nur die nicht bestellbare Grundnummer.
5. **`ANT2` und `U6` bei Mouser bestellen**, wenn die Menge über den
   DigiKey-Lagerbestand hinausgeht.

## Nächste Schritte

- DigiKey-Client in `generate_bom.py` einhängen, damit die Mappe beide Anbieter
  nebeneinander ausweist (Task 0040, Rest).
- Ersatztypen für `PS1`, `J1`/`J_PWR1` und ggf. `S2` auswählen (Task 0041).
- `U1`-Teilenummer im Schaltplan nachziehen (Task 0042).
