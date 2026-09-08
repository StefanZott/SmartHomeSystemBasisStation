---
status: done
priority: medium
type: docs
created: 2026-06-02
completed: 2026-06-02
phase: C
jira: SHBS-1
skipped: true
---

# `dev-claude-loop.md` oder Build-/Dev-Doku anlegen

## Status

**Entfällt** auf Anweisung des Bedieners (2026-06-02). Keine separate Dev-Loop-Datei.

Build, Flash, Monitor und Tests sind ausreichend dokumentiert in:
- [architecture.md](../../../docs/project/architecture.md) (Deployment, Testing)
- [tests/README.md](../../../tests/README.md)

AGENTS.md verweist in Schritt 7 des Pro-Prompt-Workflows direkt auf `` `idf.py build` `` (kein Link auf `dev-claude-loop.md`).

## Ursprüngliches Ziel

Entwickler-Schleife für Agenten dokumentieren — nicht umgesetzt.

## Done-Kriterien

- [x] Entscheidung dokumentiert (Dev-Loop entfällt).
- [x] Kein Broken Link in AGENTS.md.
