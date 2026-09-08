---
status: done
priority: medium
type: docs
created: 2026-06-02
completed: 2026-06-02
phase: A
jira: SHBS-1
---

# Root-Datei `version` anlegen

## Ziel

Eine zentrale Versionsdatei im Repository-Root anlegen, die als Quelle für Commit-Präfixe dient und mit den bestehenden Versionsquellen synchron ist.

## Schritte

1. Datei `version` im Root anlegen (Format `X.XX.XXX`, z. B. `0.00.001`).
2. Abgleich mit `CMakeLists.txt` (`PROJECT_VER`).
3. Abgleich mit `sdkconfig` (`CONFIG_APP_PROJECT_VER`).
4. Sync-Mechanismus in `docs/project/struktur-anpassung-agents.md` dokumentiert (architecture.md folgt in Task 0005).

## Done-Kriterien

- [x] Datei `version` existiert im Root.
- [x] Wert ist identisch zu `PROJECT_VER` und `CONFIG_APP_PROJECT_VER`.
- [x] Dokumentation beschreibt den Sync-Mechanismus.

## Referenz

[docs/project/struktur-anpassung-agents.md](../../../docs/project/struktur-anpassung-agents.md) — Abschnitt 6

## Ergebnis

| Quelle | Wert |
|--------|------|
| `version` | `0.00.001` |
| `CMakeLists.txt` `PROJECT_VER` | `0.00.001` |
| `sdkconfig` `CONFIG_APP_PROJECT_VER` | `0.00.001` |

Commit-Präfix gemäß AGENTS.md: `v0.00.001`
