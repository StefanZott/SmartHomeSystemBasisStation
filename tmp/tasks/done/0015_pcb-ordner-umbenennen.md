---
status: done
priority: low
type: docs
created: 2026-06-02
phase: D
jira: SHBS-1
---

# `PCB/` → `pcb/` umbenennen

## Ziel

Hardware-Verzeichnis an die AGENTS.md-Vorgabe kleingeschriebener Ordnernamen anpassen.

## Schritte

1. Mit Bediener klären: Umbenennung jetzt oder Ausnahme in `architecture.md` dokumentieren.
2. Ordner `PCB/` → `pcb/` umbenennen.
3. Alle Referenzen aktualisieren: Doku, README, KiCad-interne Pfade (falls betroffen).
4. `.gitignore`-Einträge für KiCad-Backups anpassen (`/pcb/BasisStation/...`).
5. Build und KiCad-Projekt öffnen/testen.

## Done-Kriterien

- [ ] Verzeichnis heißt `pcb/` (oder dokumentierte Ausnahme in Architektur-Doku).
- [ ] Keine broken Referenzen im Repository.
- [ ] KiCad-Projekt öffnet fehlerfrei.

## Referenz

[docs/project/struktur-anpassung-agents.md](../../../docs/project/struktur-anpassung-agents.md) — Abschnitte 2.2, 13 (Offene Entscheidung 3)

## Hinweis

Optional / später — nur nach Bediener-Freigabe.
