---
name: planen
description: Verwenden, wenn eine bevorstehende Aufgabe geplant oder vorbereitet
  werden soll — etwa bei "plane X", "bereite Y vor", "lass uns das für später
  vorbereiten". Recherchiert den nötigen Kontext und zerlegt die Aufgabe in
  einzelne Task-Dateien. Nicht für die Umsetzung selbst, nur für die
  Vorbereitung davor.
---

# Planungs-Skill

Bereitet eine kommende Aufgabe vor: Kontext recherchieren, die Aufgabe in
einzelne, abarbeitbare Tasks zerlegen und als Dateien ablegen — ohne selbst
mit der Umsetzung zu beginnen.

## Ablauf

1. **Aufgabe verstehen.** Kurz in eigenen Worten zusammenfassen, was geplant
   werden soll. Bei Unklarheiten lieber nachfragen als zu raten — das spart
   spätere Fehlplanung.

2. **Recherchieren.** Je nach Aufgabe:
   - Codebase durchsuchen (betroffene Dateien, bestehende Muster, Abhängigkeiten)
   - Relevante Docs in `docs/` und die CLAUDE.md lesen
   - Bei externen Fragen (Bibliotheken, APIs, Best Practices) gezielt recherchieren

   Ziel ist genug Kontext, um die Aufgabe in konkrete, umsetzbare Schritte zu
   zerlegen — nicht erschöpfende Recherche um ihrer selbst willen.

3. **In Tasks zerlegen.** Jeder Task ist ein in sich abgeschlossener, einzeln
   abarbeitbarer Schritt. Faustregel: Wenn ein Task nicht in einer Sitzung
   erledigt werden kann, ist er zu grob geschnitten.

4. **Task-Dateien anlegen.** Für jeden Task eine Datei anlegen. Ort,
   Namensschema, Format und Fortschritts-Konvention einer Task-Datei sind
   im `task`-Skill festgelegt — dort nachschlagen statt das Format hier
   erneut zu definieren.

5. **Zusammenfassen.** Am Ende kurz auflisten, welche Task-Dateien angelegt
   wurden. Keine Umsetzung starten, auch wenn ein Task trivial wirkt.
