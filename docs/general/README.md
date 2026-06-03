---
status: active
last_updated: 2026-06-02
type: placeholder
---

# Allgemeine Unternehmensdokumentation

Dieses Verzeichnis ist für **read-only** Inhalte aus dem globalen Unternehmens-Repo vorgesehen (`docs/general/` gemäß AGENTS.md).

## Regeln für Agenten und Entwickler

- Inhalte hier **nicht editieren** — nur referenzieren.
- Projekt-spezifische Doku gehört nach `docs/project/` bzw. `docs/userdoc/`.
- Änderungen an Unternehmensvorgaben erfolgen im zentralen Repo, nicht in diesem Projekt.

## Einbindung (Task 0019)

| Variante | Vorgehen |
|----------|----------|
| **Git-Submodule** | Unternehmens-Repo als Submodule unter `docs/general/`; Commit nur bei Submodule-Pointer-Update. |
| **Manueller Copy** | Freigegebene Markdown/PDF aus dem Unternehmens-Repo kopieren; `last_updated` im Frontmatter pflegen. |
| **Nur Verweis** | Diese README belassen und zentrales Repo-URL im Team-Wiki dokumentieren. |

**Aktueller Stand:** Kein Submodule konfiguriert. Relevante Git-Vorgaben liegen projektlokal in [git_guidelines.md](../userdoc/git_guidelines.md).

## Erwartete Inhalte (Beispiele)

- Unternehmensweite Entwicklungsprozesse
- Qualitäts- und Review-Vorgaben
- Produktübergreifende Sicherheitsrichtlinien

Nach Einbindung die Tabelle in `AGENTS.md` (Abschnitt Projektdokumentation) ergänzen.
