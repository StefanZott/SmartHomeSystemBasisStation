---
name: jira
description: Verwenden bei Jira-Interaktionen rund um ein Ticket — Titel und
  Beschreibung für ein neues Ticket vorschlagen und nach Freigabe anlegen,
  Status von Tickets/Subtasks wechseln, Fortschritts- oder
  Abschlusskommentare schreiben. Nutzt den Atlassian-MCP; Format und
  Lebenszyklus der Subtasks stehen im task-Skill.
---

# Jira-Skill

Übernimmt die Jira-Interaktionen auf Ticket-Ebene. Subtasks (Arbeitsschritte)
sind im `task`-Skill beschrieben; dieser Skill regelt Parent-Tickets,
Kommentare und Statuswechsel.

## Anbindung

- Atlassian-MCP (`mcp__atlassian__*`), Site `zott-it.atlassian.net`,
  Projekt `SHBS`. Cloud-ID über `getAccessibleAtlassianResources`.
- Ist der MCP nicht erreichbar: im **Text-Modus** arbeiten — Titel,
  Beschreibung bzw. Kommentar ausgeben, der Bediener trägt sie manuell ein
  und nennt die ID. Das ist die Ausnahme, nicht der Normalfall.

## Neues Ticket (Pro-Prompt-Schritt 4)

1. Erst per JQL prüfen, ob ein offenes Ticket bereits dasselbe Problem
   beschreibt — dann dieses verwenden. Ein Ticket bündelt ein Problem.
2. Entwurf vorlegen:
   - **Typ:** `Bug` (Fehler), `Story` (Nutzerfunktion) oder `Task` (sonstige
     Arbeit).
   - **Titel:** knapp, problemorientiert.
   - **Beschreibung:** Symptome, Reproduktion, erwartetes Verhalten.
3. Nach Freigabe per `createJiraIssue` anlegen und die ID melden.
4. Ohne Ticket nur mit ausdrücklicher Freigabe des Bedieners (z. B.
   trivialer Tippfehler in Doku).

## Statuswechsel

- Übergänge immer per `getTransitionsForJiraIssue` ermitteln, dann
  `transitionJiraIssue`.
- Subtasks setzt der Agent selbst (`In Arbeit` beim Beginn, `Erledigt` beim
  Abschluss, siehe `task`-Skill).
- Den Status des **Parent-Tickets** setzt der Bediener, es sei denn, er
  bittet ausdrücklich darum.

## Fortschritts-Kommentare

- Am **Subtask**: Stand, nächster Schritt, Commit-Hashes (siehe `task`-Skill).
- Am **Parent-Ticket** nur Zwischenstände, die über den einzelnen Schritt
  hinaus relevant sind (z. B. geänderte Entscheidung, Blocker).

## Abschlusskommentar

Ausgelöst vom `task`-Skill, wenn der letzte offene Subtask eines Tickets
erledigt ist. Dann einen Abschlusskommentar für das Parent-Ticket vorlegen,
der über **alle** Subtasks zusammenfasst:

- Was wurde geändert und warum.
- Betroffene Dateien bzw. Bereiche.
- Commits (Hash + Subtask-ID) und ggf. Version.
- Hinweise für Test/Verifikation.

Nach Freigabe per `addCommentToJiraIssue` am Parent hinterlegen.
