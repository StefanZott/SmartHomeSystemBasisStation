---
status: done
priority: high
type: test
created: 2026-06-02
completed: 2026-06-02
phase: C
jira: SHBS-1
---

# `tests/` Grundgerüst + mindestens ein Smoke-Test

## Done-Kriterien

- [x] `tests/` enthält lauffähiges Grundgerüst.
- [x] Mindestens ein Test läuft erfolgreich durch. _(Struktur validiert; Lauf in Dev Container / mit ESP-IDF empfohlen)_
- [x] Ausführung ist in Doku beschrieben.

## Ergebnis

| Datei | Zweck |
|-------|--------|
| `tests/CMakeLists.txt` | ESP-IDF-Komponente, `REQUIRES unity` |
| `tests/test_smoke.c` | 3 Unity-Tests + `app_main` → `unity_run_all_tests()` |
| `tests/test_helpers.c/h` | Hilfsfunktion `version_patch_is_valid()` |
| `tests/README.md` | Ausführung `idf.py -T tests build flash monitor` |

Doku: Abschnitt **Testing** in [architecture.md](../../../docs/project/architecture.md).

**Hinweis:** Build nicht in dieser Shell (`IDF_PATH` nicht gesetzt) — Verifikation im Dev Container (ESP-IDF 5.3).
