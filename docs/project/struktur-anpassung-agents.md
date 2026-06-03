---
status: active
last_updated: 2026-06-02
type: migration-plan
---

# Struktur-Anpassung an AGENTS.md

Gap-Analyse und Migrationsplan für das Repository **SmartHomeSystemBasisStation** gegenüber der überarbeiteten `AGENTS.md` (Stand 2026-06-02).

## Kurzfassung

Das Projekt ist ein **ESP32-S3 Embedded-Projekt** (ESP-IDF) mit KiCad-Hardware und SPIFFS-Web-UI. Die Firmware unter `main/` ist funktional angelegt, die Dokumentation existiert teilweise, folgt aber **nicht** der vorgeschriebenen `docs/`-Architektur. Mehrere Pflichtverzeichnisse und -dateien fehlen vollständig. Die `AGENTS.md` enthält noch **Textbausteine aus einem anderen Projekt** (WEM/NRT, CLAUDE.md) und muss projektspezifisch bereinigt werden.

**Empfohlene Vorgehensweise:** Zuerst `AGENTS.md` und `.gitignore` korrigieren, dann Verzeichnisstruktur und Doku-Migration, danach README und fehlende Pflichtdokumente, zuletzt Tests und Tooling.

---

## 1. Ist-Zustand vs. Soll-Zustand (Überblick)

| Bereich | Ist (Repository) | Soll (AGENTS.md) | Priorität |
|---------|------------------|------------------|-----------|
| Root-Doku | `README.md` (ESP-IDF-Beispieltext + BOM) | Onboarding mit 5 Pflichtabschnitten | Hoch |
| Versionsdatei | Nur `CMakeLists.txt` + `sdkconfig` | Zusätzlich `version` im Root | Mittel |
| Pflichtordner `docs/` | Vorhanden, falsche Unterstruktur | `general/`, `related-projects/`, `project/`, `userdoc/` | Hoch |
| Pflichtordner `tests/` | Fehlt | Automatisierte Test-Suites | Hoch |
| Pflichtordner `secrets/` | Fehlt | Lokale Keys (gitignored) | Mittel |
| Pflichtordner `tmp/` | Fehlt | Scratchpad + `tmp/tasks/{open,done}/` | Mittel |
| Firmware-Code | `main/` (ESP-IDF-Standard) | Optional `embedded/` | Niedrig (Ausnahme) |
| Hardware | `PCB/` (Großschreibung) | Kleingeschriebene Ordner | Mittel |
| Web-Assets | `spiffs/` | Kein Standardname; in Architektur dokumentieren | Niedrig |
| Code-Sprache | Deutsch in Kommentaren (`ProjectConfig.h`) | British English (en-GB) | Mittel |
| Linting | Keine `.clang-format` / `.clang-tidy` | Pflicht für C/C++ | Mittel |

---

## 2. Verzeichnisstruktur

### 2.1 Fehlende Pflichtverzeichnisse anlegen

```text
docs/
├── general/              # Read-only, ggf. als Submodule/Copy vom Unternehmens-Repo
├── related-projects/     # Schnittstellen zu verzahnten Projekten (z. B. NRT, Cloud)
├── project/              # Technische Projektdokumentation (Pflicht + Fachthemen)
└── userdoc/              # Anwenderdokumentation (factsheet, releases, …)

tests/                    # Unit-/Integrations-Tests (Unity/CppUTest o. ä.)
secrets/                  # .gitkeep + README-Hinweis, Inhalt nie committen
tmp/
└── tasks/
    ├── open/
    └── done/
```

### 2.2 Bestehende Verzeichnisse — Bewertung

| Verzeichnis | Aktion | Begründung |
|-------------|--------|------------|
| `main/` | **Beibehalten** | ESP-IDF erwartet die Komponente `main/` am Root. Ein Move nach `embedded/` würde den Build-Standard brechen. In `docs/project/architecture.md` als **bewusste Abweichung** dokumentieren. |
| `spiffs/` | **Beibehalten** (vorerst) | Web-Assets für SPIFFS; in Architektur-Doku als Frontend-Asset-Pfad beschreiben. Optional später `frontend/` nur bei Migration zu separatem Build (React/TS). |
| `PCB/` | **Umbenennen → `pcb/`** | AGENTS.md verlangt kleingeschriebene Ordner. KiCad-Pfade in Doku und ggf. relative Pfade prüfen. Alternativ: Ausnahme in Architektur-Doku festhalten, wenn Umbenennung zu aufwändig. |
| `.devcontainer/` | Beibehalten | Nicht in AGENTS.md definiert; in Toolchain-Abschnitt der README erwähnen. |
| `.vscode/` | Beibehalten | IDE-Konfiguration; nicht committen wenn teamintern anders gewünscht. |

### 2.3 Dokumentations-Migration (Datei-Mapping)

| Aktuell | Ziel | Aktion |
|---------|------|--------|
| `docs/firmware/architecture.md` | `docs/project/architecture.md` | **Zusammenführen** mit Layout-Inhalten; eine zentrale Architektur-Datei |
| `docs/layout/architecture.md` | `docs/project/hardware.md` | Hardware-spezifische Teile auslagern |
| `docs/firmware/communication.md` | `docs/project/communication.md` | Verschieben + Frontmatter |
| `docs/layout/communication.md` | In `hardware.md` / `communication.md` integrieren | Physische vs. logische Schnittstellen trennen |
| `docs/release.md` | `docs/userdoc/releases.md` | Verschieben + umbenennen (Plural!) |
| `docs/faq.md` | `docs/userdoc/faq.md` | Verschieben |
| — | `docs/project/security.md` | **Neu anlegen** (Pflicht) |
| — | `docs/project/memory_map.md` | **Neu anlegen** aus `partitions.csv` + `sdkconfig` |
| — | `docs/userdoc/factsheet.md` | **Neu anlegen** (Pflicht, VERTRAULICH) |
| — | `docs/project/dev-claude-loop.md` | **Neu anlegen** oder Referenz aus AGENTS.md entfernen |
| — | `docs/userdoc/git_guidelines.pdf` | **Bereitstellen** oder Link in AGENTS.md anpassen |

**Nach Migration löschen:** `docs/firmware/`, `docs/layout/` (leere Ordner entfernen).

---

## 3. Pflicht-Dokumente — Detail-Checkliste

### 3.1 `docs/project/` (technisch)

| Datei | Status | Inhalt / Quelle |
|-------|--------|-----------------|
| `architecture.md` | Teilweise (`docs/firmware/` + `docs/layout/`) | Tech Stack (ESP-IDF 5.x), Modulübersicht (`main/`), SPIFFS-Web-UI, KiCad unter `pcb/`, Deployment (`idf.py flash`), Verzeichnisstruktur inkl. ESP-IDF-Ausnahmen |
| `security.md` | **Fehlt** | SoftAP-Passwort, HTTP ohne TLS, NVS/SPIFFS, OTA-Plan, Threat Model Basisstation |
| `hardware.md` | Teilweise (`docs/layout/architecture.md` + README-BOM) | Pinout, MCU ESP32-S3-WROOM-1U-N16R8, KiCad-Pfade, Stückliste, Debugger (ESP-PROG/JTAG) |
| `memory_map.md` | **Fehlt** | Inhalt aus `partitions.csv`: NVS, PHY, factory app, SPIFFS storage |
| `communication.md` | Vorhanden (`docs/firmware/communication.md`) | HTTP-URIs, WLAN, JSON-Konfiguration — Frontmatter ergänzen, ggf. NRT-Schnittstelle wenn relevant |

**Optionale Ergänzungen (empfohlen):**

- `docs/project/troubleshooting.md` — Build-/Flash-Probleme, NVS-Erase, SPIFFS-Mount
- `docs/project/adr/` — z. B. „Warum ESP-IDF main/ statt embedded/“, „SPIFFS statt LittleFS“

### 3.2 `docs/userdoc/` (Anwender)

| Datei | Status | Hinweis |
|-------|--------|---------|
| `factsheet.md` | **Fehlt** | Internes Datenblatt TGE; Stichpunkte zu SmartHome-Basisstation |
| `releases.md` | Als `docs/release.md` vorhanden | Verschieben, Format H2 pro Version mit Kategorien |
| `faq.md` | Als `docs/faq.md` vorhanden | Verschieben, Frontmatter ergänzen |
| `proweb.md` | Fehlt | Optional, für externe Produktwebsite |
| `git_guidelines.pdf` | Fehlt | In AGENTS.md referenziert — bereitstellen oder Referenz entfernen |

### 3.3 Markdown-Standards (alle Doku-Dateien)

Bestehende Dateien haben **kein YAML-Frontmatter**. Bei Migration ergänzen:

```yaml
---
status: active
last_updated: YYYY-MM-DD
---
```

Weitere Regeln: relative Links, genau ein H1 pro Datei.

---

## 4. README.md — Vollständige Neufassung

Aktuell: ESP-IDF-Beispielprojekt-Text + ausführliche Hardware-Stückliste.

**Pflicht gemäß AGENTS.md §8:**

1. **Kurzbeschreibung** — SmartHome-Basisstation auf ESP32-S3, Firmware + Web-Konfiguration (max. 2 Sätze).
2. **Architektur-Überblick** — `main/` (Firmware), `spiffs/` (Web-UI), `pcb/` (KiCad).
3. **Toolchain** — ESP-IDF, `idf.py`, VS Code / Dev Container, KiCad 8/9.
4. **Deep Dive** — Link zu `docs/project/architecture.md`.
5. **Deployment** — Link zu Deployment-Abschnitt in Architektur oder eigenes Kapitel in `docs/project/`.

**Aus README entfernen / verlagern:**

- Stückliste → `docs/project/hardware.md`
- ESP-IDF-Beispieltext → löschen
- Build-Anleitung (kurz) → kann in README als 3-Zeiler bleiben, Details in Doku

---

## 5. AGENTS.md — Projektspezifischer Teil anpassen

Die globale Vorlage (§1–§11) ist weitgehend übernommen. Der **projektspezifische Abschnitt** (ab Zeile 172) enthält Inkonsistenzen:

| Problem | Zeile(n) | Korrektur |
|---------|----------|-----------|
| Projektname „S2207 WEM Firmware V1" | 172 | → SmartHome-Basisstation / SmartHomeSystemBasisStation |
| WEM/NRT durchgängig | 214–218, 224 | Auf tatsächliche Schnittstellen des Projekts prüfen; ggf. NRT in `related-projects/` |
| Verweis auf `CLAUDE.md` | 141, 272 | → `AGENTS.md` |
| Verweis `dev-claude-loop.md` | 271 | Datei anlegen oder Referenz entfernen |
| `docs/userdoc/release.md` (Singular) | 285 | → `releases.md` |
| Leere Überschrift „Anwenderdokumentation" | 198 | Struktur bereinigen; Userdoc-Tabelle korrekt formatieren |
| Doppelte/fehlerhafte Markdown-Tabelle | 210–225 | Eine Tabelle für `docs/project/`, eine für `docs/userdoc/` |
| `git_guidelines.pdf` | 288 | Datei bereitstellen oder externen Link |

**Dokumentations-Index in AGENTS.md** muss nach Migration die **tatsächlichen Pfade** widerspiegeln (nicht mehr `docs/firmware/` / `docs/layout/`).

---

## 6. Versionierung

**Format:** `X.XX.XXX` (Major.Minor.Patch — z. B. `0.00.001`). Commit-Präfix: `v` + Wert aus `version` → `v0.00.001`.

| Quelle | Pfad / Schlüssel | Synchron halten |
|--------|------------------|-----------------|
| Root (Commit-Präfix) | `version` | führend bei Versionserhöhung |
| Build | `CMakeLists.txt` → `PROJECT_VER` | identisch zu `version` |
| UI / Laufzeit | `sdkconfig` → `CONFIG_APP_PROJECT_VER` | identisch zu `version` |

Versions-Inkrement nur bei ESP32-Quellcode-Änderung und nach Bediener-Freigabe (projektspezifische Abweichung in AGENTS.md).

**Hinweis:** `main.c` enthält noch `FW_Version = "V0.0.1"` — Abgleich mit `app_desc->version` / sdkconfig bei Firmware-Task optional.

---

## 7. `.gitignore` — Kritische Korrekturen

Aktueller Inhalt:

```text
build/
/PCB/BasisStation/BasisStation-backups
AGENTS.md
```

| Problem | Aktion |
|---------|--------|
| `AGENTS.md` ist ignoriert | **Entfernen** — zentrale Agenten-Richtlinie muss versioniert sein |
| `tmp/` fehlt | Hinzufügen |
| `secrets/` fehlt | Hinzufügen (Inhalt), `secrets/.gitkeep` optional tracken |
| `sdkconfig.old` | Empfohlen ignorieren |
| `.gitignore.txt` | Duplikat/Altlast — prüfen und ggf. löschen |

---

## 8. Testing & Code Style

### 8.1 Tests (`tests/`)

**Status:** Verzeichnis fehlt komplett.

**Empfehlung für ESP-IDF:**

- Framework: **Unity** (in ESP-IDF enthalten) oder **CppUTest**
- Erste Kandidaten: JSON-Parsing (`cJSON`), Konfigurations-Lese-/Schreiblogik (`FileManagment.c`), reine Hilfsfunktionen ohne Hardware
- CI: Build + `idf.py test` oder separates Host-Test-Target

### 8.2 Linting / Formatting

**Status:** Keine Konfiguration im Repo.

Anlegen:

- `.clang-format` — an Espressif-/Projekt-Stil anlehnen
- `.clang-tidy` — Basis-Checks für `main/`
- Optional: Pre-commit-Hook (nur nach Absprache)

### 8.3 Code-Sprache (British English)

Bekannte Abweichungen:

| Datei | Problem |
|-------|---------|
| `ProjectConfig.h` | Deutsche Kommentare |
| `FileManagment.c/h` | Tippfehler „Managment" (bestehend; Umbenennung = Breaking Change, separat planen) |
| `TaskControl.c` | `executeTaskCotrol` (Tippfehler „Cotrol") |
| Diverse `.c/.h` | Prüfen auf deutsche Kommentare und US-Englisch |

**Strategie:** Neue Dateien/Kommentare sofort en-GB; bestehende schrittweise bei Touching-Changes korrigieren.

---

## 9. Task-System (`tmp/tasks/`)

Für den Pro-Prompt-Workflow (AGENTS.md §11 + projektspezifisch):

1. `tmp/tasks/open/` und `tmp/tasks/done/` anlegen
2. Erste Task-Datei z. B. `0001_doku-struktur-migration.md` mit Frontmatter inkl. `jira:` (sobald Ticket existiert)
3. Task-Nummerierung fortlaufend 4-stellig

---

## 10. JIRA- und Git-Workflow

Ab AGENTS.md projektspezifisch verbindlich:

- Jeder Commit: `vX.YY.ZZZ <type>(<JIRA-ID>): Beschreibung auf Deutsch`
- Agent erstellt Ticket-Entwurf zu Beginn jeder nicht-trivialen Aufgabe
- Agent darf Commits nur nach **ausdrücklicher Freigabe** des Bedieners ausführen

**Für die Struktur-Migration:** JIRA-Ticket **SHBS-1** bündelt alle Migrations-Phasen (A–D) und Tasks 0001–0020. Ein Task = ein atomarer Commit; alle Commits referenzieren `SHBS-1` als Scope.

---

## 11. Migrations-Phasen (empfohlene Reihenfolge)

### Phase A — Grundlagen (ohne Code-Umbau)

- [ ] `.gitignore` korrigieren (`AGENTS.md` tracken, `tmp/`, `secrets/` ignorieren)
- [ ] Pflichtverzeichnisse anlegen (`tests/`, `secrets/`, `tmp/tasks/`, `docs/project/`, `docs/userdoc/`, …)
- [ ] `AGENTS.md` projektspezifischen Teil bereinigen (WEM→Basisstation, CLAUDE→AGENTS, Tabellen)
- [ ] Root-Datei `version` anlegen

### Phase B — Dokumentation

- [ ] Doku-Dateien gemäß Mapping verschieben/zusammenführen
- [ ] YAML-Frontmatter in alle Markdown-Dateien
- [ ] `security.md`, `memory_map.md`, `factsheet.md` neu schreiben
- [ ] `README.md` gemäß §8 neu fassen
- [ ] Alte Ordner `docs/firmware/`, `docs/layout/` entfernen
- [ ] Index-Tabellen in `AGENTS.md` aktualisieren

### Phase C — Tooling & Qualität

- [ ] `.clang-format` / `.clang-tidy` einführen
- [ ] `tests/` Grundgerüst + mindestens ein Smoke-Test
- [ ] `dev-claude-loop.md` oder Build-/Dev-Doku anlegen
- [ ] `git_guidelines.pdf` bereitstellen oder Referenz anpassen

### Phase D — Optional / später

- [ ] `PCB/` → `pcb/` umbenennen
- [ ] Code-Kommentare en-GB migrieren
- [ ] Tippfehler in Bezeichnern (`FileManagment`, `executeTaskCotrol`) refactoren
- [ ] `docs/related-projects/` mit NRT-/Cloud-Schnittstellen
- [ ] `docs/general/` aus Unternehmens-Repo einbinden
- [ ] `proweb.md` für Marketing

---

## 12. ESP-IDF-spezifische Sonderfälle

Diese Punkte sollten in `docs/project/architecture.md` festgehalten werden, damit künftige Agenten die Abweichung von der generischen Ordnerstruktur verstehen:

| Konvention | AGENTS.md generisch | Dieses Projekt |
|------------|---------------------|----------------|
| Applikationscode | `embedded/` | `main/` (ESP-IDF Pflicht) |
| Web-UI | `frontend/` (React/TS) | `spiffs/` (statisches HTML/CSS/JS, embedded in Firmware) |
| Build-System | CMakeLists.txt | Root + `main/CMakeLists.txt` + `sdkconfig` |
| Partitionen | `memory_map.md` | `partitions.csv` + sdkconfig-Optionen |
| Version in UI | `version` Datei | `CONFIG_APP_PROJECT_VER` in sdkconfig |

---

## 13. Offene Entscheidungen (Bediener)

Vor Umsetzung klären:

1. **Projektbezeichnung:** SmartHome-Basisstation, WEM, oder anderer Produktname in Doku/AGENTS.md?
2. **NRT-Schnittstelle:** Ist UART/Protokoll zum NRT 1 XT Teil dieses Projekts? Falls ja → `docs/related-projects/` und `communication.md` erweitern.
3. **PCB-Umbenennung:** `PCB/` → `pcb/` jetzt oder Ausnahme dokumentieren?
4. **JIRA-Projekt-ID:** **SHBS-1** — bündelt die gesamte Migration (Phasen A–D, Tasks 0001–0020). ~~z. B. `S2207-xxx` für Struktur-Migration-Ticket?~~
5. **git_guidelines.pdf:** Aus Unternehmens-Doku kopieren oder AGENTS.md-Referenz entfernen?
6. **Dev-Loop-Doku:** `dev-claude-loop.md` neu schreiben oder aus anderem Projekt übernehmen?

---

## 14. Referenz — Ziel-Verzeichnisbaum

```text
SmartHomeSystemBasisStation/
├── AGENTS.md
├── README.md
├── version
├── CMakeLists.txt
├── sdkconfig
├── partitions.csv
├── main/                    # ESP-IDF Firmware (Ausnahme: statt embedded/)
├── spiffs/                  # Web-Assets → SPIFFS
├── pcb/                     # KiCad (Zielname; aktuell PCB/)
├── docs/
│   ├── general/
│   ├── related-projects/
│   ├── project/
│   │   ├── architecture.md
│   │   ├── security.md
│   │   ├── hardware.md
│   │   ├── memory_map.md
│   │   ├── communication.md
│   │   └── struktur-anpassung-agents.md   # diese Datei (nach Abschluss optional nach tmp/ oder löschen)
│   └── userdoc/
│       ├── factsheet.md
│       ├── releases.md
│       ├── faq.md
│       └── git_guidelines.pdf             # falls vorhanden
├── tests/
├── secrets/
└── tmp/
    └── tasks/
        ├── open/
        └── done/
```

---

## 15. Nächster Schritt

Nach Freigabe durch den Bediener: **Phase A** fortsetzen (Task 0002). JIRA-Ticket: **SHBS-1** (gesamte Migration). Diese Datei dient als Checkliste; erledigte Punkte können hier abgehakt oder in Tasks unter `tmp/tasks/open/` ausgelagert werden.
