---
status: done
priority: high
type: docs
created: 2026-06-02
completed: 2026-06-02
phase: A
jira: SHBS-1
---

# `AGENTS.md` projektspezifischen Teil bereinigen

## Ziel

Den projektspezifischen Abschnitt der `AGENTS.md` (ab Zeile 172) auf das SmartHome-Basisstation-Projekt ausrichten und veraltete Referenzen entfernen.

## Schritte

1. Projektname „S2207 WEM Firmware V1" → SmartHome-Basisstation / SmartHomeSystemBasisStation.
2. WEM/NRT-Bezüge prüfen: nur behalten, wo fachlich zutreffend; sonst neutral formulieren.
3. Verweise `CLAUDE.md` → `AGENTS.md` (§10, Pro-Prompt-Workflow).
4. Leere Überschrift „Anwenderdokumentation" (Zeile 198) bereinigen.
5. Dokumentations-Tabellen korrigieren (getrennte Tabellen für `docs/project/` und `docs/userdoc/`).
6. Verweis `release.md` → `releases.md` in Abweichungen korrigieren.
7. Referenzen auf `dev-claude-loop.md` und `git_guidelines.pdf` prüfen (Datei anlegen oder Referenz anpassen — ggf. eigene Tasks).

## Done-Kriterien

- [x] Kein Verweis mehr auf `CLAUDE.md`.
- [x] Projektname und Rollenbeschreibung passen zum Repository.
- [x] Dokumentations-Index verweist auf korrekte Pfade unter `docs/project/` und `docs/userdoc/`.
- [x] Markdown-Tabellen sind syntaktisch korrekt gerendert.

## Referenz

[docs/project/struktur-anpassung-agents.md](../../../docs/project/struktur-anpassung-agents.md) — Abschnitt 5

## Ergebnis

- Projektüberschrift: `SmartHomeSystemBasisStation`
- WEM/NRT/UART-Bezüge neutral formuliert (keine NRT-Schnittstelle im Projekt)
- `CLAUDE.md` → `AGENTS.md` (§10, Pro-Prompt-Workflow)
- Doku-Index: getrennte Tabellen für `general/`, `project/`, `related-projects/`, `userdoc/`
- `release.md` → `releases.md`; Tippfehler in Release-Notes-Abweichung bereinigt
- Broken Links entfernt: `dev-claude-loop.md`, `git_guidelines.pdf`
- Commit enthält zudem die überarbeitete Unternehmensvorlage (§1–§11), die zuvor uncommitted war
