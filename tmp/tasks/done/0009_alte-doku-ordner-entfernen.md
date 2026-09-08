---
status: done
priority: medium
type: docs
created: 2026-06-02
completed: 2026-06-02
phase: B
jira: SHBS-1
---

# Alte Ordner `docs/firmware/` und `docs/layout/` entfernen

## Done-Kriterien

- [x] `docs/firmware/` existiert nicht mehr.
- [x] `docs/layout/` existiert nicht mehr.
- [x] Keine broken Referenzen auf alte Pfade (nur historische Erwähnung in Migrations-Doku).

## Ergebnis

- Leere Verzeichnisse `docs/firmware/` und `docs/layout/` vom Dateisystem entfernt.
- Dateien waren bereits in Task 0005 (Commit `005a31d`) aus Git gelöscht.
- `docs/faq.md` und `docs/release.md` am Root: nicht vorhanden (bereits migriert).
- Keine navigierenden Links auf alte Pfade im aktiven Code/Doku (Ausnahme: Mapping-Tabelle in `struktur-anpassung-agents.md`).
