---
name: github
description: Verwenden, wenn zu einem Jira-Subtask ein Commit erstellt werden
  soll (siehe task-Skill) — beim Abschluss (ein Subtask = ein finaler Commit)
  oder als WIP-Zwischenstand bei einer Unterbrechung. Committet nach
  Freigabe lokal, prüft vorher den Branch gegen die Branching-Konvention aus
  der CLAUDE.md, trägt den Hash als Kommentar am Subtask ein. Pusht nur nach
  erneuter Bestätigung.
---

# GitHub-Skill

Übernimmt das Committen (und ggf. Pushen) von Änderungen, die zu einem
Jira-Subtask gehören. Wird vom `task`-Skill beim Abschluss eines Subtasks
angestoßen — ein Subtask entspricht einem finalen, atomaren Commit — sowie
optional bei einer Unterbrechung (WIP-Commit).

## Branch prüfen

Vor dem Commit den aktuellen Branch feststellen (`git branch --show-current`).
Wird direkt auf `main` committet, obwohl die Arbeit nach der
Branching-Konvention der CLAUDE.md (`main`/`release/`/`fix/`/`feature/`)
einen eigenen `feature/`- oder `fix/`-Branch nahelegt: kurz nachfragen, ob
auf `main` committet oder vorher ein Branch angelegt wird. Wird ohnehin auf
einem passenden Branch gearbeitet: keine Rückfrage.

Wird ein Commit per Cherry-Pick auf einen anderen Branch übernommen,
`Cherry Pick <commit-hash>` in der Commit-Message vermerken.

## Commit erstellen

1. Relevante Änderungen prüfen (`git status`, `git diff`) — nur committen,
   was tatsächlich zum aktuellen Subtask gehört.
2. Commit-Message nach CLAUDE.md:
   `vX.YY.ZZZ <type>(<Subtask-ID>): <Beschreibung>` — Version aus
   `version`, Beschreibung auf Deutsch. Typ: `feat`, `fix`, `docs`,
   `test`, `refactor`, `chore` je nach Art der Änderung. Ohne Ticket
   (nur mit ausdrücklicher Freigabe) entfällt der Scope.
3. Commit-Vorschlag dem Bediener zeigen, nach Freigabe lokal committen.
4. Kurzen Hash + Kurzbeschreibung als **Kommentar am Subtask** eintragen
   (siehe `task`-Skill). Kein zusätzlicher Commit zum Nachtragen von Hashes.

## WIP-Commit bei Unterbrechung

Wird eine Sitzung mitten in einem offenen Subtask beendet: auf Wunsch einen
Zwischenstand committen, damit die Änderungen auf dem anderen Rechner
verfügbar sind.

- Commit-Message wie oben, aber mit `(WIP)` nach der Version:
  `vX.YY.ZZZ (WIP) <type>(<Subtask-ID>): <Beschreibung>`.
- Hash als Kommentar am Subtask, mit Hinweis „WIP, gepusht: ja/nein".
- Ein WIP-Commit ersetzt nicht den Abschluss-Commit. Frühere WIP-Commits
  bleiben unverändert in der Historie — kein `--amend` oder Rebase ohne
  ausdrückliche Anfrage.

## Pushen

- Push anbieten und erst nach Bestätigung durchführen; dabei nennen, welche
  Commits auf welchen Branch gehen. Die Freigabe gilt nur für diesen Push.
- Hängt `git push` (veralteter Anmeldehelfer nach VS-Code-Neustart):
  `GIT_TERMINAL_PROMPT=0 timeout 120 git push` verwenden bzw. den Bediener
  bitten, eine neue Shell zu öffnen.
- Ohne funktionierende Anbindung nicht pushen, sondern melden, dass lokal
  committet wurde und der Bediener selbst pushen muss.
