---
status: done
priority: medium
type: docs
created: 2026-06-02
completed: 2026-06-02
phase: B
jira: SHBS-1
---

# Index-Tabellen in `AGENTS.md` aktualisieren

## Done-Kriterien

- [x] Jede Markdown-Datei unter `docs/project/` und `docs/userdoc/` ist in AGENTS.md verlinkt.
- [x] Keine isolierten Doku-Dateien ohne Index-Eintrag (Boy Scout Rule §10).
- [x] Relative Links in Tabellen sind korrekt.

## Ergebnis

Index in `AGENTS.md` abgeglichen mit **11 vorhandenen** Markdown-Dateien unter `docs/`:

- `docs/project/`: 6 Dateien (architecture, security, hardware, memory_map, communication, struktur-anpassung-agents)
- `docs/userdoc/`: 3 Dateien (factsheet, releases, faq)
- `docs/general/README.md`, `docs/related-projects/README.md` — bereits indexiert

Anpassungen:
- Beschreibungen präzisiert (`memory_map`, `struktur-anpassung-agents`, factsheet VERTRAULICH)
- `faq.md` nicht mehr als „Optional" markiert (Datei existiert)
- `proweb.md`: kein Broken Link — als optional/ Task 0020 vermerkt (Datei fehlt noch)
- `dev-claude-loop.md` / `troubleshooting.md`: nicht eingetragen (noch nicht angelegt, Tasks 0013 ff.)

**Phase B (Tasks 0005–0010) abgeschlossen.**
