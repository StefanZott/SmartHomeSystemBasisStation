---
name: planen
description: Verwenden, wenn eine bevorstehende Aufgabe geplant oder vorbereitet
  werden soll — etwa bei "plane X", "bereite Y vor", "lass uns das für später
  vorbereiten". Recherchiert den nötigen Kontext und zerlegt die Aufgabe in
  Jira-Subtasks unter einem Ticket. Nicht für die Umsetzung selbst, nur für
  die Vorbereitung davor.
---

# Planungs-Skill

Bereitet eine kommende Aufgabe vor: Kontext recherchieren, die Aufgabe in
einzelne, abarbeitbare Schritte zerlegen und als Jira-Subtasks anlegen —
ohne selbst mit der Umsetzung zu beginnen.

## Ablauf

1. **Aufgabe verstehen.** Kurz in eigenen Worten zusammenfassen, was geplant
   werden soll. Bei Unklarheiten lieber nachfragen als zu raten — das spart
   spätere Fehlplanung.

2. **Recherchieren.** Je nach Aufgabe:
   - Codebase durchsuchen (betroffene Dateien, bestehende Muster, Abhängigkeiten)
   - Relevante Docs in `docs/` und die CLAUDE.md lesen
   - Bestehende Jira-Tickets prüfen, ob das Problem schon erfasst ist
   - Bei externen Fragen (Bibliotheken, APIs, Best Practices) gezielt recherchieren

   Ziel ist genug Kontext, um die Aufgabe in konkrete, umsetzbare Schritte zu
   zerlegen — nicht erschöpfende Recherche um ihrer selbst willen.

3. **Ticket klären.** Gibt es noch kein Ticket für das Problem: über den
   `jira`-Skill Titel und Beschreibung vorschlagen und nach Freigabe
   anlegen.

4. **In Subtasks zerlegen.** Jeder Subtask ist ein in sich abgeschlossener,
   einzeln abarbeitbarer Schritt mit Done-Bedingung. Faustregel: Wenn er
   nicht in einer Sitzung erledigt werden kann, ist er zu grob geschnitten.

5. **Subtasks anlegen.** Liste (Titel + Kurzbeschreibung) dem Bediener
   zeigen, nach Freigabe in Jira anlegen. Format und Felder sind im
   `task`-Skill festgelegt — dort nachschlagen statt sie hier erneut zu
   definieren. Keine Dateien unter `tmp/tasks/` anlegen.

6. **Zusammenfassen.** Am Ende die angelegten IDs mit Titel auflisten.
   Keine Umsetzung starten, auch wenn ein Subtask trivial wirkt.
