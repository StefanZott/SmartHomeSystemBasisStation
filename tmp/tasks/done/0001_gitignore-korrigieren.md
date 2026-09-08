---
status: done
priority: high
type: docs
created: 2026-06-02
completed: 2026-06-02
phase: A
jira: SHBS-1
---

# `.gitignore` korrigieren

## Ziel

Die `.gitignore` an die AGENTS.md-Vorgaben anpassen, sodass zentrale Projektdateien versioniert werden und temporäre/lokale Verzeichnisse ignoriert werden.

## Schritte

1. Eintrag `AGENTS.md` aus `.gitignore` entfernen (Datei muss versioniert sein).
2. `tmp/` hinzufügen (Scratchpad des Agenten).
3. `secrets/` hinzufügen (lokale Keys/Passwörter).
4. `sdkconfig.old` optional ignorieren.
5. Duplikat `.gitignore.txt` prüfen und ggf. löschen.
6. Bestehende Einträge (`build/`, KiCad-Backups) beibehalten.

## Done-Kriterien

- [x] `AGENTS.md` wird von Git nicht mehr ignoriert.
- [x] `tmp/` und `secrets/` sind in `.gitignore` eingetragen.
- [x] Keine widersprüchlichen oder doppelten Ignore-Dateien im Root.

## Referenz

[docs/project/struktur-anpassung-agents.md](../../../docs/project/struktur-anpassung-agents.md) — Abschnitt 7

## Ergebnis

- `.gitignore` aktualisiert: `AGENTS.md` entfernt; `tmp/`, `secrets/`, `sdkconfig.old` ergänzt; `build/` und KiCad-Backups beibehalten.
- `.gitignore.txt` gelöscht (Duplikat, von Git nicht verwendet).
