---
status: done
priority: low
type: feature
created: 2026-06-02
phase: D
jira: SHBS-1
---

# Code-Kommentare en-GB migrieren

## Ziel

Alle Code-Kommentare und Header-Beschreibungen auf British English (en-GB) umstellen gemäß AGENTS.md §1.

## Schritte

1. Inventar: deutsche Kommentare in `main/` (z. B. `ProjectConfig.h`).
2. Schrittweise Übersetzung bei Datei-Touch oder dedizierter Pass.
3. US-Englisch (`color`, `behavior`) auf en-GB prüfen.
4. Keine Umbenennung von Funktionen/Bezeichnern in diesem Task (separater Refactor-Task).

## Done-Kriterien

- [ ] Keine deutschen Kommentare mehr in `main/`.
- [ ] Neue/edtierte Kommentare folgen en-GB.
- [ ] Build bleibt erfolgreich.

## Referenz

[docs/project/struktur-anpassung-agents.md](../../../docs/project/struktur-anpassung-agents.md) — Abschnitt 8.3

## Hinweis

Optional / später — kann inkrementell erfolgen.
