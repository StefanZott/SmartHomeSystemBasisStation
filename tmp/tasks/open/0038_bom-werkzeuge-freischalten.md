---
status: open
priority: high
type: feature
created: 2026-09-22
jira: SHBS-15
---

# Werkzeuge fuer die Stuecklisten-Erstellung freischalten

## Kontext

Fuer eine bestellfaehige Stueckliste fehlten zwei Dinge: Zugriff auf
Mouser-Daten und eine Moeglichkeit, erzeugte `.xlsx` durchzurechnen.

## Befund zur Erreichbarkeit

Die urspruengliche Annahme "Mouser ist nicht erreichbar" war zu pauschal.
Gemessen aus dem Container:

| Ziel | Ergebnis |
| ---- | -------- |
| `api.mouser.com` | **HTTP 302 in 0,25 s** — erreichbar |
| `www.mouser.de` | HTTP 000 — geblockt (Bot-Schutz) |
| `pypi.org` | HTTP 200 — erreichbar |

Geblockt ist also nur die **Webseite**, nicht die API. Eine
Firewall-Freigabe ist nicht noetig. Abfragen laufen ueber die Search-API,
nicht ueber Scraping der Produktseiten.

## Schritte

- [x] Mouser **Search**-API-Schluessel unter `secrets/mouser_api_key`
      abgelegt, Rechte `600`, per `.gitignore` (`secrets/*`) ausgeschlossen.
- [x] Funktionstest gegen `api.mouser.com/api/v2/search/partnumber` mit
      `652-1543-650-149` (Bourns-Taster `S2`): HTTP 200, 1 Treffer,
      **EUR-Preisstaffel**, Lagerbestand, deutsche Beschreibung,
      `mouser.de`-Produktlink. Der Schluessel haengt korrekt am deutschen Shop.
- [x] `.devcontainer/Dockerfile`: `libreoffice-calc`, `libreoffice-core` und
      `fonts-liberation` ergaenzt (vor dem `USER`-Wechsel).
- [x] `.devcontainer/Dockerfile`: `openpyxl` und `pandas` ins IDF-venv
      aufgenommen — ueber den `current`-Symlink, damit ein IDF-Versionswechsel
      es nicht bricht.
- [x] Paketnamen vorab gegen den Ubuntu-noble-Index geprueft (alle drei
      HTTP 200). Lehre aus SHBS-13, wo `kicad-templates` im PPA nicht
      existierte und den Build gebrochen haette.
- [ ] **Bediener: Container neu bauen.**
- [ ] Danach verifizieren: `soffice --version` und
      `python3 -c "import openpyxl, pandas"`.

## Groessenabschaetzung

Direkte Downloadgroesse der drei Pakete zusammen rund **51 MB**
(`libreoffice-core` 41 MB, `libreoffice-calc` 8,4 MB, `fonts-liberation`
1,5 MB). Die Abhaengigkeiten kommen obendrauf; ohne `apt` im Container laesst
sich der Baum hier nicht aufloesen, eine belastbare Gesamtzahl gibt es daher
erst nach dem Build. Bewusst **nicht** installiert wurde das Metapaket
`libreoffice` (zieht Writer, Impress und Java nach).

## Done-Bedingung

Nach dem Rebuild laufen `soffice --version` und der `openpyxl`-Import, und
die Mouser-API liefert mit dem hinterlegten Schluessel Treffer.
