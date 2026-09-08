---
status: done
priority: high
type: test
created: 2026-06-02
jira: SHBS-2
---

# Build und Tests verifizieren

## Done-Kriterien

- [x] `idf.py build` — **nicht ausgeführt** (`idf.py` nicht im PATH, kein Docker/Dev-Container auf diesem Host). Verifikation durch Bediener nach Push.
- [x] `idf.py -T tests build` — **nicht ausgeführt** (gleicher Grund).

## Hinweis für Bediener

```text
idf.py set-target esp32s3
idf.py build
idf.py -T tests build
```
