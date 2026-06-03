# Unit tests (ESP-IDF / Unity)

Smoke tests for the SmartHomeSystemBasisStation firmware project.

## Framework

[Unity](https://github.com/ThrowTheSwitch/Unity) via ESP-IDF component `unity`.

## Run (target ESP32-S3)

From the project root, with ESP-IDF environment active (e.g. Dev Container):

```text
idf.py set-target esp32s3
idf.py -T tests build
idf.py -T tests flash monitor
```

`-T tests` builds the `tests/` component as the application (instead of `main/`).

Expected output: all `[smoke]` tests pass via `unity_run_all_tests()`.

## Layout

| File | Purpose |
|------|---------|
| `CMakeLists.txt` | ESP-IDF test component registration |
| `test_smoke.c` | Unity test cases and `app_main` |
| `test_helpers.c/h` | Small testable helper (version patch validation) |

## Notes

- Production firmware: `idf.py build` (uses `main/` as usual).
- Tests are self-contained in `tests/` — no link to `main/` (avoids duplicate `app_main`).
