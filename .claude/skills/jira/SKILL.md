---
name: jira
description: Verwenden bei Jira-Interaktionen rund um einen Task — beim
  Beginn eines Tasks ohne Ticket-Nummer klären, ob mit oder ohne Ticket
  gearbeitet wird, Titel/Beschreibung für ein neues Ticket vorschlagen,
  Fortschritts- oder Abschlusskommentare auf ein bestehendes Ticket
  schreiben. Nutzt eine vorhandene Jira-Anbindung (MCP-Server oder CLI),
  falls verfügbar, sonst wird der Text zum manuellen Eintragen vorbereitet.
---

# Jira-Skill

Übernimmt alle Jira-Interaktionen rund um einen Task aus `temp/tasks/`. Ob
in einem Projekt ein MCP-Server oder eine CLI zur Verfügung steht,
unterscheidet sich — dieser Skill funktioniert in beiden Fällen, nur mit
unterschiedlicher Tiefe.

## Verfügbarkeit prüfen

Vor jeder Aktion feststellen, ob eine echte Jira-Anbindung existiert:
- Verfügbare MCP-Tools nach "jira" durchsuchen.
- Alternativ ein CLI-Tool prüfen (z. B. `command -v jira`).

Ist nichts davon vorhanden, im **Text-Modus** arbeiten: Statt eine Aktion
auszuführen, den nötigen Text (Titel, Beschreibung, Kommentar) ausgeben,
den der Nutzer manuell in Jira einträgt.

## Bei Task-Beginn ohne Ticket

Wenn das `jira`-Feld einer Task-Datei leer ist und die Arbeit an dem Task
beginnt:

1. Nachfragen: "Mit oder ohne Jira-Ticket bearbeiten?"
2. Bei "ohne": `jira:`-Feld bleibt leer, keine weitere Aktion.
3. Bei "mit":
   - Erst prüfen, ob eine andere Task-Datei in `temp/tasks/open/` oder
     `temp/tasks/done/` bereits an demselben Problem arbeitet und ein
     `jira:`-Feld gesetzt hat — falls ja, diese Ticket-Nummer übernehmen
     statt ein neues Ticket anzulegen. Ein Ticket bündelt ein Problem,
     nicht einen Task.
   - Sonst: Titel und Beschreibung aus Kontext und Ziel der Task-Datei
     ableiten und vorschlagen.
   - **Mit Anbindung:** Ticket anlegen, Ticket-Nummer ins `jira:`-Feld der
     Task-Datei eintragen.
   - **Ohne Anbindung:** Titel/Beschreibung ausgeben, Nutzer um manuelles
     Anlegen bitten. Sobald die Ticket-Nummer genannt wird, ins
     `jira:`-Feld eintragen.

## Fortschritts-Kommentare

Während der Arbeit an einem Task mit Ticket können nennenswerte
Zwischenstände als Kommentar aufs Ticket geschrieben werden — nicht bei
jedem einzelnen Eintrag im Fortschritt-Abschnitt der Task-Datei (siehe
`task`-Skill), sondern bei Zwischenständen, die auch außerhalb der Task-Datei
sichtbar sein sollten.

- **Mit Anbindung:** Kommentar direkt am Ticket hinterlegen.
- **Ohne Anbindung:** Kommentartext vorschlagen, den der Nutzer manuell
  einträgt.

## Abschlusskommentar

Ausgelöst vom `task`-Skill, aber erst, wenn es der **letzte** offene Task
ist, der auf ein bestimmtes Ticket verweist (der `task`-Skill prüft das).
Dann einen Abschlusskommentar vorschlagen bzw. hinterlegen, der
zusammenfasst, was insgesamt umgesetzt wurde — über alle Tasks hinweg, die
auf dieses Ticket verwiesen haben, nicht nur den zuletzt abgeschlossenen.
