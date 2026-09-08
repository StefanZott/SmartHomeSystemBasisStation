---
status: done
priority: high
type: docs
created: 2026-06-02
completed: 2026-06-02
phase: B
jira: SHBS-1
---

# Doku-Dateien gemäß Mapping verschieben/zusammenführen

## Ziel

Bestehende Dokumentation aus `docs/firmware/` und `docs/layout/` in die AGENTS.md-konforme Struktur unter `docs/project/` und `docs/userdoc/` überführen.

## Schritte

1. `docs/firmware/architecture.md` + `docs/layout/architecture.md` → `docs/project/architecture.md` zusammenführen.
2. Hardware-Teile aus Layout-Architektur → `docs/project/hardware.md`.
3. `docs/firmware/communication.md` → `docs/project/communication.md`.
4. Physische Schnittstellen aus `docs/layout/communication.md` in `hardware.md` / `communication.md` integrieren.
5. `docs/release.md` → `docs/userdoc/releases.md`.
6. `docs/faq.md` → `docs/userdoc/faq.md`.
7. Relative Links in allen betroffenen Dateien aktualisieren.

## Done-Kriterien

- [x] Ziel-Dateien unter `docs/project/` und `docs/userdoc/` enthalten den migrierten Inhalt.
- [x] Keine broken Links zwischen Doku-Dateien.
- [x] Inhaltlich keine Informationsverluste gegenüber den Quelldateien.

## Referenz

[docs/project/struktur-anpassung-agents.md](../../../docs/project/struktur-anpassung-agents.md) — Abschnitt 2.3

## Ergebnis

| Neu | Quelle |
|-----|--------|
| `docs/project/architecture.md` | `docs/firmware/architecture.md` + Systemüberblick aus Layout |
| `docs/project/hardware.md` | `docs/layout/architecture.md` + physische Schnittstellen aus Layout-Communication |
| `docs/project/communication.md` | `docs/firmware/communication.md` + Verweis auf Hardware |
| `docs/userdoc/releases.md` | `docs/release.md` |
| `docs/userdoc/faq.md` | `docs/faq.md` |

Gelöscht: `docs/firmware/*`, `docs/layout/*`, `docs/release.md`, `docs/faq.md`. YAML-Frontmatter in allen Ziel-Dateien. Versionen auf `0.00.001` aktualisiert.

**Hinweis:** Leere Ordner `docs/firmware/`, `docs/layout/` — Task 0009.
