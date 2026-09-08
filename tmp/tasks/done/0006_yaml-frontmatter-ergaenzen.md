---
status: done
priority: medium
type: docs
created: 2026-06-02
completed: 2026-06-02
phase: B
jira: SHBS-1
---

# YAML-Frontmatter in alle Markdown-Dateien

## Ziel

Jede Markdown-Datei unter `docs/` erhält gemäß AGENTS.md §7 ein einheitliches YAML-Frontmatter.

## Schritte

1. Alle `.md`-Dateien unter `docs/` inventarisieren.
2. Frontmatter-Vorlage anwenden.
3. Pro Datei ggf. zusätzliche Metadaten (`type`, `confidential`) wo sinnvoll.
4. Prüfen: genau ein H1 (`#`) pro Datei.

## Done-Kriterien

- [x] Jede Datei unter `docs/` beginnt mit gültigem YAML-Frontmatter.
- [x] `last_updated` entspricht dem Migrationsdatum bzw. letzter inhaltlicher Änderung.
- [x] Keine doppelten H1-Überschriften pro Datei.

## Referenz

[docs/project/struktur-anpassung-agents.md](../../../docs/project/struktur-anpassung-agents.md) — Abschnitt 3.3

## Ergebnis

**8 Dateien** unter `docs/` geprüft:

| Datei | Frontmatter | H1 |
|-------|-------------|-----|
| `project/architecture.md` | `status`, `last_updated`, `type: project-doc` | 1 |
| `project/hardware.md` | `status`, `last_updated`, `type: project-doc` | 1 |
| `project/communication.md` | `status`, `last_updated`, `type: project-doc` | 1 |
| `project/struktur-anpassung-agents.md` | `status`, `last_updated`, `type: migration-plan` | 1 |
| `userdoc/faq.md` | `status`, `last_updated`, `type: userdoc` | 1 |
| `userdoc/releases.md` | `status`, `last_updated`, `type: userdoc` | 1 |
| `general/README.md` | `status`, `last_updated`, `type: placeholder` | 1 |
| `related-projects/README.md` | `status`, `last_updated`, `type: placeholder` | 1 |

Grund-Frontmatter (`status`, `last_updated`) war durch Task 0005 bereits gesetzt; `type`-Metadaten ergänzt.
