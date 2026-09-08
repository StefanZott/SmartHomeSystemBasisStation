---
name: github
description: Verwenden, wenn zu einem Task ein Commit erstellt werden soll
  (siehe task-Skill) — beim Abschluss (ein Task = ein finaler Commit) oder
  als WIP-Zwischenstand bei einer Unterbrechung mitten in einem offenen
  Task. Unabhängig davon, ob ein Jira-Ticket existiert. Committet immer
  lokal, prüft vorher den Branch gegen die Branching-Konvention aus der
  CLAUDE.md. Pusht nur nach Bestätigung und nur, wenn eine GitHub-Anbindung
  (MCP oder funktionierender git push) vorhanden ist — sonst übernimmt das
  Pushen der Nutzer selbst.
---

# GitHub-Skill

Übernimmt das Committen (und ggf. Pushen) von Änderungen, die zu einem Task
gehören. Wird vom `task`-Skill beim Abschluss eines Tasks angestoßen — ein
Task entspricht einem finalen, atomaren Commit, nicht mehreren über den
Verlauf verteilten — sowie optional bei einer Session-Unterbrechung
(WIP-Commit) — und unabhängig davon, ob es zum Task ein Jira-Ticket gibt.

## Branch prüfen

Vor dem Commit den aktuellen Branch feststellen (`git branch --show-current`).
Folgt das Projekt der Branching-Konvention aus der CLAUDE.md
(`main`/`release/`/`fix/`/`feature/`) und wird direkt auf `main` committet,
obwohl der Task nach `type` (`feature` oder `bugfix`, siehe `task`-Skill)
einen eigenen `feature/`- oder `fix/`-Branch nahelegt: kurz nachfragen, ob
auf `main` committet werden soll oder vorher ein passender Branch angelegt
wird. Nutzt das Projekt die einfache Variante (nur `main` + `feature/`,
siehe CLAUDE.md) oder committet ohnehin schon auf einem passenden Branch:
keine Rückfrage.

Wird ein Commit per Cherry-Pick auf einen anderen Branch übernommen,
`Cherry Pick <commit-hash>` in der Commit-Message vermerken.

## Verfügbarkeit prüfen

Feststellen, ob eine echte GitHub-Anbindung fürs Pushen existiert:
- Verfügbare MCP-Tools nach "github" durchsuchen.
- Alternativ prüfen, ob `git push` mit hinterlegten Credentials
  funktionieren würde (Remote konfiguriert, kein offensichtliches
  Auth-Problem).

Das Committen selbst ist davon unabhängig — es passiert immer lokal, egal
ob eine Anbindung existiert.

## Commit erstellen

1. Relevante Änderungen prüfen (`git status`, `git diff`) — nur committen,
   was tatsächlich zum aktuellen Task gehört.
2. Commit-Message als Conventional Commit: `type: Beschreibung`, bzw. mit
   Jira-Ticket als Scope `type(PROJ-123): Beschreibung`, wenn im `jira`-Feld
   der Task-Datei eine Ticket-Nummer eingetragen ist. Üblicher Typ passend
   zum `type`-Feld der Task-Datei (siehe `task`-Skill): `feature` → `feat`,
   `bugfix` → `fix`, `test` → `test`, `docs` → `docs`. Sprache der
   Beschreibung nach Projekt-Konvention (siehe CLAUDE.md).
3. Immer lokal committen — unabhängig davon, ob im Anschluss gepusht wird.
4. Hash (kurz) und Kurzbeschreibung in die Commits-Liste der Task-Datei
   eintragen (siehe `task`-Skill).

## WIP-Commit bei Unterbrechung

Wird eine Session mitten in einem noch offenen Task beendet (Task nicht
abgeschlossen, siehe `task`-Skill): auf Wunsch einen Zwischenstand
committen, damit Änderungen nicht nur unversioniert im Arbeitsverzeichnis
liegen.

- Commit-Message wie gewohnt (Conventional Commit, ggf. mit Jira-Scope),
  aber mit vorangestelltem `(WIP)`: `(WIP) type(PROJ-123): Beschreibung`.
- Trotzdem in die Commits-Liste der Task-Datei eintragen (siehe
  `task`-Skill) — als vorläufiger Stand, nicht als finaler Task-Commit.
- Ein WIP-Commit ersetzt nicht den Abschluss-Commit: Beim späteren
  Abschluss des Tasks gilt weiterhin ein finaler, nicht-WIP-Commit. Frühere
  WIP-Commits bleiben unverändert in der Historie stehen — kein `--amend`
  oder Rebase ohne ausdrückliche Anfrage.

## Pushen

- **Mit Anbindung:** Push anbieten und erst nach Bestätigung durchführen —
  auch mit vorhandener Anbindung nie ungefragt pushen.
- **Ohne Anbindung:** Nicht pushen. Dem Nutzer mitteilen, dass lokal
  committet wurde und er selbst pushen muss, sobald er bereit ist.
