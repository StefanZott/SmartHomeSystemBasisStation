---
status: done
priority: low
type: bugfix
created: 2026-09-22
jira: SHBS-14
---

# Scheinaenderung an ethernet.kicad_sch beseitigen

## Kontext

`pcb/BasisStation/ethernet.kicad_sch` stand dauerhaft als geaendert im
`git status`, obwohl `git diff` keinen Inhalt zeigte.

## Korrektur der urspruenglichen Diagnose

Der Task ging zunaechst von einer CRLF-Fassung im Index aus. **Das war
falsch.** Nachmessung:

- `git ls-files --eol` meldet fuer *alle* Schaltplan-Dateien `i/lf w/crlf` —
  Index LF, Arbeitsverzeichnis CRLF. Das ist der **korrekte** Zustand, den
  `.gitattributes` (`* text=auto eol=lf`) herstellt.
- Kein einziger Eintrag im Index hat CRLF (`git ls-files --eol` mit Filter
  auf `crlf` im Index: 0 Treffer).
- Blob-Hashes: HEAD, Index und Arbeitsverzeichnis sind mit
  `c4453bc1480f8520f3435841fc67e3e735765f8b` **identisch**.
- `git diff --numstat` liefert keine Zeile.

Tatsaechliche Ursache: ein **veralteter Stat-Cache** im Index. KiCad hatte
die Datei neu geschrieben, wodurch sich mtime und Groesse aenderten. Git
markiert sie daraufhin als "moeglicherweise geaendert"; erst der
Inhaltsvergleich zeigt Gleichheit. Deshalb tauchte sie in `git status` auf,
aber nie in `git diff --stat`.

## Loesung

`git update-index --refresh` allein genuegte nicht (Git bestaetigt den
Stat-Cache bei Dateien mit eol-Konvertierung nicht ohne Weiteres). Ein
`git add` auf die Datei hat den Cache aufgefrischt. Da der Blob mit HEAD
identisch ist, wurde dabei **nichts** gestaged.

## Schritte

- [x] Blob-Hashes von HEAD, Index und Arbeitsverzeichnis verglichen —
      identisch.
- [x] `git add pcb/BasisStation/ethernet.kicad_sch` — Scheinaenderung weg,
      Stage unveraendert.
- [x] Geprueft, dass kein weiterer Index-Eintrag CRLF fuehrt.

## Hinweis fuer die Zukunft

Der Effekt kann wiederkehren, sobald KiCad unter Windows die Datei erneut
schreibt. Er ist harmlos: Solange `git diff` leer bleibt, liegt keine
inhaltliche Aenderung vor. `.gitattributes` ist korrekt konfiguriert, hier
ist nichts zu aendern.

## Done-Bedingung

`git status` zeigt die Datei nicht mehr; Blob-Hashes nachweislich identisch.
