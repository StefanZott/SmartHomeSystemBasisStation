---
name: task
description: Verwenden, wenn eine Task-Datei unter temp/tasks/ angelegt,
  fortgeschrieben oder abgeschlossen werden soll — z. B. beim Anlegen neuer
  Tasks während der Planung, beim Festhalten von Fortschritt während der
  Arbeit an einem Task, oder beim Abschließen eines Tasks. Legt Format,
  Namensschema und Lifecycle einer Task-Datei fest.
---

# Task-Skill

Definiert, wie eine einzelne Aufgabe als Datei unter `temp/tasks/`
festgehalten, fortgeschrieben und abgeschlossen wird. Andere Abläufe (z. B.
der `planen`-Skill) nutzen diese Konvention, statt das Format jeweils selbst
zu definieren — eine Task-Datei soll immer gleich aussehen, unabhängig davon,
wer sie angelegt hat.

## Eine Task-Datei anlegen

- Ort: `temp/tasks/open/`. Ordner anlegen, falls nicht vorhanden.
- Dateiname: `NNN-kurzer-slug.md`, `NNN` dreistellig fortlaufend. Höchste
  vorhandene Nummer sowohl in `temp/tasks/open/` als auch in
  `temp/tasks/done/` ermitteln und darauf aufbauen — verhindert Kollisionen
  mit bereits abgeschlossenen Tasks.
- Inhalt:

  ```markdown
  ---
  title: Kurzer, sprechender Titel
  created: YYYY-MM-DD
  jira: PROJ-123
  priority: medium
  type: feature
  ---

  ## Kontext
  Warum dieser Task, was ist der Hintergrund.

  ## Ziel
  Was am Ende erreicht sein soll.

  ## Schritte
  - [ ] ...
  - [ ] ...

  ## Fortschritt
  - YYYY-MM-DD: Task angelegt, noch nicht begonnen.

  ## Commits
  - (noch keine)

  ## Offene Fragen
  Was noch geklärt werden muss (falls vorhanden).
  ```

  `jira` ist das zugehörige Jira-Ticket (z. B. `PROJ-123`). Existiert kein
  Ticket, das Feld leer lassen (`jira:`) statt es wegzulassen — so bleibt
  klar, dass bewusst keins vergeben ist, nicht vergessen wurde. Ist das
  Feld leer und die Arbeit an dem Task beginnt, siehe `jira`-Skill. Ein
  Ticket bündelt ein Problem, nicht einen Task — mehrere Task-Dateien
  dürfen auf dieselbe Ticket-Nummer verweisen, wenn sie zusammen an
  demselben Problem arbeiten.

  `priority` ist eine von `critical`, `high`, `medium`, `low`. `type` ist
  eine von `feature`, `bugfix`, `test`, `docs`.

## Nächsten Task auswählen

Wird kein Task explizit genannt (z. B. "mach weiter", "arbeite am nächsten
Task"), gilt diese Reihenfolge:

1. Wird ein Task explizit genannt (Nummer, Slug oder Titel), gilt diese
   Nennung immer — der Rest dieses Abschnitts entfällt.
2. Liegt genau eine Datei in `temp/tasks/open/`, wird sie direkt genommen —
   keine Rückfrage nötig.
3. Bei mehreren offenen Tasks: einen bevorzugen, der bereits begonnen wurde
   (der Fortschritt-Abschnitt enthält mehr als nur "Task angelegt, noch
   nicht begonnen"). Laufende Arbeit zu Ende bringen schlägt Neues
   beginnen — das hält Kontext zusammen und vermeidet Fragmente.
4. Bleiben mehrere Kandidaten (mehrere begonnene, oder keiner begonnen),
   kurz nachfragen: je Kandidat Titel und letzten Fortschritt-Eintrag
   auflisten, der Nutzer entscheidet.

## Fortschritt festhalten

Zweck: Bei einem Session-Wechsel mitten in der Arbeit an einem Task muss
allein aus der Datei hervorgehen, wo man steht — ohne die vorherige Session
zu kennen.

- Lückenlos dokumentieren: **jeder** abgeschlossene Vorgang bekommt einen
  Log-Eintrag — ein erledigter Schritt, eine Änderung, ein Commit, eine
  wichtige Erkenntnis. Nicht erst kurz vor einer Unterbrechung, sondern
  laufend während der Arbeit.
- Neue Einträge ergänzen, bestehende nie überschreiben oder löschen — der
  Log ist eine Historie.
- Ein Eintrag beantwortet knapp: Was wurde erledigt? Wo stehen wir? Was ist
  der nächste konkrete Schritt?
- Beim Wiedereinstieg in einen Task zuerst den letzten Eintrag lesen, bevor
  irgendetwas anderes passiert.
- Bei einer Unterbrechung mitten in einem offenen Task kann zusätzlich zum
  Log-Eintrag ein WIP-Commit über den `github`-Skill sinnvoll sein, damit
  Änderungen nicht nur unversioniert im Arbeitsverzeichnis liegen.
- Erledigte Punkte in der Schritte-Liste abhaken.
- Neue Erkenntnisse, die die Schritte oder das Ziel betreffen, direkt dort
  einpflegen statt nur im Fortschritt-Log zu erwähnen — der Log ist die
  Historie, Schritte/Ziel sind der aktuelle Stand.

## Nennenswerte Zwischenstände

Commits passieren nicht hier, sondern einmal pro Task beim Abschluss (siehe
unten) — ein Task entspricht einem atomaren Commit. Ist im `jira`-Feld ein
Ticket eingetragen, kann bei einem nennenswerten Zwischenstand trotzdem
schon über den `jira`-Skill ein Fortschrittskommentar hinterlegt werden,
unabhängig vom späteren Commit.

## Commits dokumentieren

Der Commit, der zu diesem Task gehört, wird in der Commits-Liste
festgehalten — kurzer Hash plus Kurzbeschreibung:

```markdown
## Commits
- a1b2c3d Login-Validierung auf Server-Seite ergänzt
```

Damit lässt sich der Task jederzeit mit der Git-Historie abgleichen, auch
über mehrere Sessions hinweg. Das Committen selbst übernimmt der
`github`-Skill, der auch diesen Abschnitt pflegt. Mehr als ein Eintrag ist
die Ausnahme (z. B. nachträglicher Fixup-Commit), nicht die Regel.

## Einen Task abschließen

Ein Task gilt als erledigt, wenn alle Schritte abgehakt sind. Dann:

- Über den `github`-Skill den Commit für diesen Task erstellen —
  unabhängig davon, ob ein Jira-Ticket existiert. Ein Task = ein Commit.
- Ist ein `jira:`-Feld gesetzt: prüfen, ob noch andere Task-Dateien in
  `temp/tasks/open/` auf dieselbe Ticket-Nummer verweisen.
  - Ja: kein Abschlusskommentar, das Ticket ist noch nicht fertig.
  - Nein (letzter offener Task zu diesem Ticket): über den `jira`-Skill
    den Abschlusskommentar hinterlegen.
- Erst danach die Datei von `temp/tasks/open/` nach `temp/tasks/done/`
  verschieben.
- Kein Umbenennen nötig — die Nummer bleibt, damit sie bei künftiger
  Nummernvergabe weiterhin berücksichtigt wird.
