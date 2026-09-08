---
status: done
priority: high
type: docs
created: 2026-06-02
completed: 2026-06-02
phase: A
jira: SHBS-1
---

# Pflichtverzeichnisse anlegen

## Ziel

Alle gemäß AGENTS.md §2 fehlenden Pflichtverzeichnisse im Repository anlegen.

## Schritte

1. `tests/` anlegen (ggf. mit Platzhalter-README oder `.gitkeep`).
2. `secrets/` anlegen (mit `.gitkeep`; Inhalt nie committen).
3. `tmp/tasks/open/` und `tmp/tasks/done/` — **bereits angelegt**.
4. `docs/project/` — **teilweise vorhanden** (`struktur-anpassung-agents.md`); Struktur vervollständigen.
5. `docs/userdoc/` anlegen.
6. `docs/general/` anlegen (Read-only, Platzhalter).
7. `docs/related-projects/` anlegen (Platzhalter).

## Done-Kriterien

- [x] Alle oben genannten Verzeichnisse existieren im Dateisystem.
- [x] `secrets/` und leere Ordner sind entweder via `.gitkeep` trackbar oder dokumentiert.

## Referenz

[docs/project/struktur-anpassung-agents.md](../../../docs/project/struktur-anpassung-agents.md) — Abschnitte 2.1, 14

## Hinweis

`tmp/tasks/` wurde bereits in diesem Schritt vom Bediener initiiert. **Keine Dateiverschiebungen** — siehe Task 0005.

## Ergebnis

| Verzeichnis | Angelegt | Trackbar |
|-------------|----------|----------|
| `tests/` | `.gitkeep` | ja |
| `secrets/` | `.gitkeep` | ja (`.gitignore`: `secrets/*`, Ausnahme `!secrets/.gitkeep`) |
| `tmp/tasks/` | bereits vorhanden | nein (`tmp/` ignoriert) |
| `docs/project/` | bereits vorhanden | ja |
| `docs/userdoc/` | `.gitkeep` | ja |
| `docs/general/` | `README.md` | ja |
| `docs/related-projects/` | `README.md` | ja |

Zusätzlich: `.gitignore` für `secrets/` angepasst, damit `.gitkeep` versioniert werden kann.
