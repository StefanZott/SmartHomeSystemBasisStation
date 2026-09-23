---
title: Werkzeug-Freigaben und Agenten-Zustand ueberleben einen Container-Rebuild
created: 2026-09-23
jira: TBD
priority: medium
type: bugfix
---

## Kontext

Nach dem Container-Rebuild vom 2026-09-22 (ausgeloest durch die `--env-file`-
Umstellung in `.devcontainer/devcontainer.json`) fragt der Agent wieder bei
jedem einzelnen Bash-Befehl nach Bestaetigung.

Ursache: Die pro Projekt erteilten Freigaben ("nicht mehr fragen") stehen in
`~/.claude.json` unter dem Schluessel `projects`. Dieser Schluessel fehlt in der
Datei inzwischen vollstaendig. `/home/esp` liegt ohne Volume im
Container-Dateisystem (`mount | grep home` ist leer) und wurde beim Rebuild neu
aus dem Image erzeugt. Mit verloren gingen Login-Token und alle
Sitzungsprotokolle bis auf zwei.

Verschaerfend: `.claude/settings.json` fuehrt in der Allowlist nur die vier
Atlassian-MCP-Werkzeuge, kein einziges Bash-Muster. `.claude/settings.local.json`
existiert nicht. Es gab also gar keine versionierte Freigabe, die den Rebuild
haette ueberstehen koennen.

## Ziel

Zwei voneinander unabhaengige Absicherungen:

1. Die projektueblichen Bash-Befehle sind in `.claude/settings.json`
   freigegeben — versioniert, im Workspace-Mount, damit rebuild-fest und fuer
   alle Beteiligten identisch.
2. Der Agenten-Zustand unter `~/.claude` (Login, Protokolle) liegt in einem
   Named Volume und ueberlebt kuenftige Rebuilds.

## Schritte

- [ ] `.claude/settings.json`: Allowlist um lesende Shell-Befehle, lesende
      Git-Befehle, `idf.py build/size/fullclean/reconfigure`, `kicad-cli`,
      `soffice --headless` und `python3` erweitern.
      **Bewusst ausgenommen:** `git commit`, `git push`, `idf.py flash`, `rm` —
      CLAUDE.md §9 verlangt dafuer eine ausdrueckliche Freigabe des Bedieners.
      *Der Agent kann diese Datei nicht selbst schreiben (Selbstmodifikations-
      Schutz des Auto-Modus). Der Bediener fuegt den Inhalt ein oder erteilt
      die Freigaben ueber `/permissions`.*
- [x] `.devcontainer/devcontainer.json`: Named Volume `shbs-claude-state` auf
      `/home/esp/.claude` gemountet.
- [x] `.devcontainer/Dockerfile`: `~/.claude` bereits im Image anlegen, damit
      Docker das leere Volume mit korrektem Eigentuemer (`esp`) befuellt statt
      als `root:root`.
- [x] Doku: Abschnitt "Entwicklungsumgebung (Dev Container)" in
      [architecture.md](../../../docs/project/architecture.md) ergaenzt —
      was persistiert wird, was bewusst nicht, und warum die Freigaben in
      `.claude/settings.json` gehoeren.
- [ ] Rebuild durch den Bediener, danach Gegenprobe: Volume vorhanden,
      `~/.claude` dem User `esp` gehoerend, Freigaben greifen.
- [ ] Commit-Vorschlag an Bediener (JIRA-ID steht noch aus).

## Fortschritt

- 2026-09-23: Ursache eingegrenzt und belegt (fehlender `projects`-Schluessel,
  kein Home-Volume, leere Bash-Allowlist). Container-Konfiguration und Doku
  angepasst. Die Aenderung an `.claude/settings.json` blieb offen, weil der
  Auto-Modus dem Agenten das Schreiben der eigenen Rechtekonfiguration
  verweigert — der Vorschlag liegt dem Bediener vor.

## Offene Fragen

- JIRA-ID fuer diesen Task steht aus.
- `~/.claude.json` (Login-Konto, Projektzustand) wird weiterhin nicht
  persistiert. Ein Symlink ins Volume waere riskant, weil die Anwendung die
  Datei atomar per Rename schreibt und den Symlink dabei ersetzen wuerde; die
  Binary warnt ausserdem selbst vor dem Ueberschreiben dieser Datei
  (GH #3117). Solange die Freigaben versioniert im Workspace liegen, bleibt
  als Rest nur ein einmaliges Neu-Login nach einem Rebuild.
