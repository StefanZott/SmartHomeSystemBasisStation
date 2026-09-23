---
type: analysis
created: 2026-09-22
jira: SHBS-15
status: final
---

# Reichelt als Bezugsquelle: Abdeckungsprüfung

## Ausgangslage

Nach dem Mouser-Abgleich ([2026-09-22_mouser-abgleich-stueckliste.md](2026-09-22_mouser-abgleich-stueckliste.md))
blieben 29 Positionen ohne Teilenummer, dazu `ANT2` ohne Bezugsweg und `PS1`
mit Lagerbestand 0. Frage des Bedieners: Deckt Reichelt die fehlenden Teile ab,
und ist einer der Taoglas-Nachfolger dort gelistet?

Geprüft am 2026-09-22 über die Reichelt-Shopsuche aus dem Dev-Container.
Werkzeug: [check_reichelt.py](../bom/check_reichelt.py). Reichelt bietet keine
öffentliche API; die Prüfung liest die Trefferzahl aus dem Seitentitel und ist
damit eine **Abdeckungsprüfung, keine Preisquelle**.

## Ergebnis / Befunde

### B1 — Reichelt führt keine Taoglas-Produkte

Die Suche nach „Taoglas" liefert **einen** Treffer, und der ist ein
Video-Übertragungssystem, keine Antenne. Weder `GW.20.5150` noch die
Nachfolger `GW.20.A151` oder `GW.22.5151` sind gelistet.

Damit ist die Frage beantwortet: **Nein**, kein Taoglas-Nachfolger bei
Reichelt. Reichelt führt allerdings 147 Treffer unter „WLAN Antenne RP-SMA
2,4" — ein gleichwertiger Ersatz ist dort also beschaffbar, nur eben nicht von
Taoglas. Das ist eine Produktentscheidung, keine reine Beschaffungsfrage.

### B2 — Der ESP32 ist bei Reichelt die falsche Variante

Das ist der Befund mit der größten Tragweite. Reichelt führt zwei
ESP32-S3-Module:

| Artikel | Teilenummer | Preis |
| ------- | ----------- | ----- |
| WiFi-Modul 802.11/BT (364574) | `ESP32-S3-WROOM-1-N16R8` | 4,94 € |
| WiFi-Modul 802.11/BT (364571) | `ESP32-S3-WROOM-1-N16R2` | 5,12 € |

Beide sind die **`-1`-Variante mit PCB-Antenne**. Das Projekt verwendet
`ESP32-S3-WROOM-1U-N16R8`, also die Ausführung mit **U.FL-Anschluss für eine
externe Antenne** — daran hängt die gesamte Antennenkette `ANT1` (Pigtail) und
`ANT2` (RP-SMA-Antenne).

Ein Tausch auf die `-1`-Variante wäre keine Beschaffungsoptimierung, sondern
eine Designänderung: Pigtail und Antenne entfielen, dafür bräuchte die
Leiterplatte Freiraum für die PCB-Antenne und das Gehäuse dürfte an der Stelle
nicht abschirmen. **Nicht stillschweigend tauschen.**

### B3 — Herstellerspezifische Teile fehlen durchgängig

Keine Treffer für: Würth `890334023023`, `870235673001`, `151031YS05900`,
`7499011121A`, `830059532`, `61200621621`; Amphenol `12401548E4#2A`; Bourns
`1543-650-149`; MPS `MP2359`; Diodes `D3V3XA4B10LP`.

Das ist erwartbar — Reichelt ist kein Katalogdistributor im Sinne von Mouser
oder DigiKey. Für diese Positionen bleibt Mouser beziehungsweise eine
Zweitquelle nötig.

### B4 — Generische Passivteile und Standard-Halbleiter sind gut abgedeckt

Genau der Bereich, in dem die 29 offenen Positionen liegen:

| Suchbegriff | Treffer |
| ----------- | ------- |
| Widerstand SMD 0805 | 632 |
| X7R 0805 100n | 4 |
| WLAN Antenne RP-SMA 2,4 | 147 |
| RP-SMA | 442 |
| BC337 | 7 |
| SS34 | 4 |
| SMAJ5.0A | 2 |
| Quarz 25 MHz SMD | 7 |
| SMD Induktivität 10 µH | 1 |
| W5500 (Ethernet-IC, nicht nur Boards) | 11 |

### B5 — Methodischer Hinweis: die Suche erzeugt leicht Fehlalarme

Erste Durchläufe meldeten 0 Treffer für „SMD 0805 10k" und „SMD-Widerstand
0805 10K", während „Widerstand SMD 0805" 632 Treffer liefert. Reichelts Suche
versteht bei generischen Teilen keine Wertangaben in Kombination mit der
Bauform. **Eine Null ist erst nach einer zweiten, breiteren Formulierung
belastbar** — dieser Hinweis steht auch im Kopf des Prüfskripts.

## Empfehlungen

1. **Reichelt als Zweitquelle für Passivteile nutzen**, nicht als Hauptquelle.
   Die 29 offenen Positionen sind dort beschaffbar und in Prototypenmengen
   häufig günstiger.
2. **`U6` weiterhin über Mouser** (`356-ESP32S3WM1UN16R8`, 5,93 €, 6174 ab
   Lager) — die `-1U`-Variante gibt es bei Reichelt nicht, und ein Wechsel auf
   `-1` wäre eine Designänderung.
3. **Antennenkette bewusst entscheiden:** entweder Taoglas-Nachfolger über
   Mouser/DigiKey, oder ein gleichwertiges RP-SMA-Set von Reichelt. Beides ist
   möglich, aber es ist eine Produktentscheidung (Gewinn, Abstrahlverhalten,
   Zulassung).
4. **Keine Einquellen-Strategie.** Keiner der geprüften Distributoren deckt die
   Stückliste allein ab: Reichelt fehlen die Herstellerteile, Mouser fehlt die
   Antenne.

## Nächste Schritte

- Zweiten Distributor mit API anbinden (TME oder DigiKey), damit Preis- und
  Verfügbarkeitsvergleich automatisch läuft — siehe Folge-Ticket.
- Reichelt bleibt manuell: ohne öffentliche API ist nur die Abdeckungsprüfung
  automatisierbar, keine Preisübernahme.
