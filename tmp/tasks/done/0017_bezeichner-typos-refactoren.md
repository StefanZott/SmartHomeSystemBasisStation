---
status: done
priority: low
type: feature
created: 2026-06-02
phase: D
jira: SHBS-1
---

# Tippfehler in Bezeichnern refactoren

## Ziel

Bekannte Tippfehler in Funktions- und Dateinamen korrigieren — mit voller Codebase-Aktualisierung.

## Betroffene Bezeichner

| Ist | Soll |
|-----|------|
| `FileManagment.c/h` | `FileManagement.c/h` |
| `executeTaskCotrol` | `executeTaskControl` |

## Schritte

1. Rename durchführen in Quellcode, Headers, CMakeLists.txt.
2. Alle `#include`- und Aufruf-Stellen aktualisieren.
3. Doku-Referenzen anpassen (`architecture.md`, Kommentare).
4. Build + ggf. Tests ausführen.
5. **Keine** Firmware-Versionserhöhung ohne Bediener-Freigabe (Refactor zählt als Quellcode-Änderung — Version separat klären).

## Done-Kriterien

- [ ] Keine Vorkommen von `FileManagment` und `executeTaskCotrol` mehr im Code.
- [ ] `idf.py build` erfolgreich.
- [ ] Doku referenziert korrekte Bezeichner.

## Referenz

[docs/project/struktur-anpassung-agents.md](../../../docs/project/struktur-anpassung-agents.md) — Abschnitt 8.3

## Hinweis

Breaking Change für externe Referenzen — optional / später.
