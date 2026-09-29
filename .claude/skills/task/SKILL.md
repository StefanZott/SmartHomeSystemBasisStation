---
name: task
description: Verwenden, wenn ein Arbeitsschritt als Jira-Subtask angelegt,
  ausgewählt, fortgeschrieben oder abgeschlossen werden soll — z. B. beim
  Anlegen der Subtasks während der Planung, bei "mach weiter" / "nächster
  Task", beim Festhalten von Fortschritt oder einer Unterbrechung, oder beim
  Abschließen eines Subtasks. Legt Format, Lebenszyklus und Auswahl von
  Subtasks fest. Keine Task-Dateien unter tmp/tasks/ mehr anlegen.
---

# Task-Skill

Arbeitsschritte leben als **Subtasks in Jira**, nicht als Dateien. Grund:
Gearbeitet wird von mehreren Rechnern, und Jira ist ohne Commit/Push überall
auf demselben Stand. Andere Abläufe (`planen`, `github`, `jira`) nutzen diese
Konvention, statt sie selbst zu definieren.

`tmp/tasks/open/` und `tmp/tasks/done/` sind ein eingefrorenes Archiv:
lesen erlaubt, keine neuen Dateien, keine Änderungen.

## Anbindung

- Atlassian-MCP (`mcp__atlassian__*`), Cloud-ID über
  `getAccessibleAtlassianResources` (Site `zott-it.atlassian.net`).
- Projekt `SHBS`. Parent-Tickets: `Task`, `Bug` oder `Story`. Arbeitsschritte:
  Vorgangstyp `Subtask` mit `parent` = Ticket-ID.
- Status-Workflow: `Zu erledigen` → `In Arbeit` → `Wird überprüft` →
  `Erledigt`. Übergänge per `getTransitionsForJiraIssue` ermitteln, nicht
  hart codieren.
- Ist der MCP nicht erreichbar: Arbeit anhalten und dem Bediener melden —
  kein Rückfall auf lokale Task-Dateien.

## Einen Subtask anlegen

Nur nach Freigabe durch den Bediener (Liste mit Titel + Kurzbeschreibung
vorher zeigen). Dann per `createJiraIssue`:

- **Summary:** kurzer, sprechender Titel (Deutsch).
- **Parent:** die Ticket-ID aus Pro-Prompt-Schritt 4.
- **Beschreibung** (Markdown):

  ```markdown
  ## Kontext
  Warum dieser Schritt, was ist der Hintergrund.

  ## Ziel
  Was am Ende erreicht sein soll.

  ## Schritte
  - [ ] ...
  - [ ] Doku (`docs/project/...`) aktualisieren

  ## Done-Bedingung
  Woran erkennbar ist, dass der Subtask fertig ist (Build, DRC, Test, Doku).
  ```

- Nach dem Anlegen die IDs an den Bediener melden.

Jeder Subtask muss in einer Sitzung erledigt werden können. Ist er größer,
feiner schneiden.

## Nächsten Subtask auswählen

1. Wird ein Subtask oder Ticket explizit genannt (ID oder Titel), gilt diese
   Nennung — der Rest entfällt.
2. Sonst per JQL suchen:
   `project = SHBS AND issuetype = Subtask AND statusCategory != Done ORDER BY status DESC, created ASC`
   (bei bekanntem Ticket zusätzlich `AND parent = SHBS-NN`).
3. Einen Subtask im Status `In Arbeit` bevorzugen — laufende Arbeit zu Ende
   bringen schlägt Neues beginnen.
4. Bleiben mehrere Kandidaten, kurz nachfragen: je Kandidat ID, Titel und
   letzter Kommentar; der Bediener entscheidet.

## Beginnen

- Beschreibung und die letzten Kommentare lesen, bevor irgendetwas anderes
  passiert — dort steht der Stand der letzten Sitzung, ggf. vom anderen
  Rechner.
- Vor dem Beginn `git pull --ff-only` auf dem Arbeitszweig, damit der Code
  zum Jira-Stand passt.
- Status auf `In Arbeit` setzen.

## Fortschritt festhalten

Zweck: Bei einem Rechner- oder Sitzungswechsel muss allein aus dem Subtask
hervorgehen, wo man steht.

- Nennenswerte Zwischenstände als **Kommentar** am Subtask: Was ist erledigt?
  Wo stehen wir? Was ist der nächste konkrete Schritt?
- Bei einer Unterbrechung mitten im Subtask immer einen Kommentar schreiben;
  zusätzlich kann ein WIP-Commit über den `github`-Skill sinnvoll sein
  (Hinweis im Kommentar, dass gepusht werden muss, damit der andere Rechner
  ihn sieht).
- Erledigte Schritte in der Checkliste der Beschreibung abhaken
  (`editJiraIssue`). Erkenntnisse, die Ziel oder Schritte ändern, direkt in
  der Beschreibung einpflegen — Kommentare sind die Historie, die
  Beschreibung ist der aktuelle Stand.
- Kommentare nie löschen oder überschreiben.

## Einen Subtask abschließen

Ein Subtask ist erledigt, wenn alle Schritte abgehakt und die
Done-Bedingung erfüllt ist. Dann:

1. Über den `github`-Skill den Commit erstellen (Scope = Subtask-ID). Ein
   Subtask = ein Commit.
2. Kommentar am Subtask: kurzer Commit-Hash + einzeilige Beschreibung, ggf.
   Prüfergebnis (Build, DRC, Tests). Das ersetzt das frühere Nachtragen von
   Hashes in Task-Dateien — **kein** eigener Commit dafür.
3. Status auf `Erledigt` setzen.
4. Prüfen, ob unter demselben Parent noch offene Subtasks existieren
   (JQL `parent = SHBS-NN AND statusCategory != Done`).
   - Ja: Parent bleibt offen, kein Abschlusskommentar.
   - Nein: über den `jira`-Skill den Abschlusskommentar am Parent vorlegen.
