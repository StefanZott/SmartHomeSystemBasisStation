---
status: done
priority: low
type: docs
created: 2026-06-02
phase: D
jira: SHBS-1
---

# `docs/related-projects/` mit NRT-/Cloud-Schnittstellen

## Ziel

Schnittstellenverträge zu verzahnten Projekten dokumentieren, sofern fachlich relevant.

## Schritte

1. Mit Bediener klären: Ist UART/Protokoll zum NRT 1 XT Teil dieses Projekts?
2. Falls ja: Markdown-Datei(en) unter `docs/related-projects/` anlegen (z. B. `nrt-1-xt.md`).
3. Protokoll, Timings, physische Schnittstelle beschreiben.
4. Querverweise in `docs/project/communication.md` und `AGENTS.md`-Index.
5. Falls nein: Platzhalter-README mit „keine verzahnten Projekte dokumentiert" oder Ordner leer lassen.

## Done-Kriterien

- [ ] Entscheidung NRT-Schnittstelle ist dokumentiert.
- [ ] Relevante Schnittstellenverträge liegen unter `docs/related-projects/`.
- [ ] AGENTS.md-Index aktualisiert.

## Referenz

[docs/project/struktur-anpassung-agents.md](../../../docs/project/struktur-anpassung-agents.md) — Abschnitt 13 (Offene Entscheidung 2)

## Hinweis

Optional / später — abhängig von Produktscope.
