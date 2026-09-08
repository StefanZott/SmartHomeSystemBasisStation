---
status: done
priority: high
type: docs
created: 2026-06-02
completed: 2026-06-02
phase: B
jira: SHBS-1
---

# `security.md`, `memory_map.md`, `factsheet.md` neu schreiben

## Ziel

Fehlende Pflichtdokumente gemäß AGENTS.md §7 anlegen und mit projektspezifischem Inhalt füllen.

## Done-Kriterien

- [x] Alle drei Dateien existieren an den korrekten Pfaden.
- [x] YAML-Frontmatter vorhanden.
- [x] Inhalt ist projektspezifisch (keine Platzhalter-Lorem-Ipsum).
- [x] `factsheet.md` als VERTRAULICH gekennzeichnet.

## Ergebnis

| Datei | Inhalt |
|-------|--------|
| `docs/project/security.md` | Angriffsfläche, Web-UI ohne Auth, SoftAP-Passwort, HTTP/TLS, SPIFFS/NVS, Risk Assessment, OTA-Plan |
| `docs/project/memory_map.md` | Partitionstabelle aus `partitions.csv`, Offsets, sdkconfig-Bezug, kein OTA |
| `docs/userdoc/factsheet.md` | Internes Datenblatt (confidential), Use-Cases, technische Eckdaten |

Frontmatter: `type: project-doc` bzw. `userdoc` + `confidential: true` für Factsheet.
