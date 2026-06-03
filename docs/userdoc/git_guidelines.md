---
status: active
last_updated: 2026-06-02
type: userdoc
---

# Git-Richtlinien — SmartHomeSystemBasisStation

Projektspezifische Git-Vorgaben für Entwickler und KI-Agenten. Ergänzt die globalen Regeln in `AGENTS.md` §6 und die unternehmensweiten Vorgaben (intern ggf. als PDF bei Zott-IT/TGE).

## Commit-Nachrichten

- **Format:** Conventional Commits, Beschreibung auf **Deutsch**.
- **Versionspräfix:** Wert aus Root-Datei `version` (Format `X.XX.XXX`, z. B. `0.00.001`) als Tag-Präfix `v0.00.001`.
- **JIRA-Scope:** Jedes Commit referenziert genau ein Ticket: `v0.00.001 <type>(SHBS-123): Beschreibung`.

**Typen:** `feat`, `fix`, `docs`, `test`, `chore`, …

**Beispiele:**

```text
v0.00.001 docs(SHBS-1): README als Onboarding-Dokument neu gefasst
v0.00.001 test(SHBS-1): Unity-Testgrundgerüst unter tests/ angelegt
v0.00.001 fix(SHBS-42): WLAN-Reconnect bei Timeout behoben
```

- **Atomar:** Ein Task / ein Problem = ein Commit.
- **WIP:** Erlaubt, in der Nachricht mit `(WIP)` markieren.

## Tagging und Versionsnummer

Jeder Stand, der **herausgegeben** wird (interne Tests, Release-Kandidaten, Produktions-Firmware), muss mit der **Versionsnummer** als Git-Tag gekennzeichnet werden.

| Tag | Bedeutung |
|-----|-----------|
| `v0.00.001` | Normale Versions-Freigabe (entspricht `version` / Firmware-Version) |
| `v0.00.005-kundexyz` | Kundenspezifische Test- oder Lieferversion |
| `release` | In jedem Projekt üblicher Marker für den aktuellen Release-Stand (siehe README) |

**Regeln:**

- Die **aktuellste Version** in Entwicklungs- bzw. Produktivumgebung soll als Tag im Repository nachvollziehbar sein — Hinweis dazu in der [README](../../README.md).
- **Alle veröffentlichten Versionen** müssen mit einem Versions-Tag versehen werden.
- Applikationsspezifische Zusatz-Tags (z. B. `release_pe`, `release_ta` bei Cloud-Komponenten) sind in der README zu dokumentieren, sofern sie für dieses Projekt genutzt werden. Für die reine Firmware-Basisstation gelten primär Versions-Tags (`vX.XX.XXX`) und ggf. `release`.

**Synchronisation Firmware (dieses Projekt):**

Bei Versionserhöhung zusätzlich pflegen: `version`, `CMakeLists.txt` (`PROJECT_VER`), `sdkconfig` (`CONFIG_APP_PROJECT_VER`) — nur nach Bediener-Freigabe bei ESP32-Quellcode-Änderung.

## Branching-Strategie

### Historisch: `develop` und `master`

Früher wurde ein `develop`-Branch (häufige, möglichst tägliche Commits) und ein `master`-Branch (veröffentlichte Versionen) gepflegt. Das ist für einfache Projekte tragfähig, stößt bei paralleler Pflege mehrerer Versionsstände (z. B. v1.3 und v1.4) an Grenzen.

### Aktuell: `main` und Release-Zweige

| Branch | Zweck |
|--------|--------|
| `main` | **Arbeitszweig** — laufende Entwicklung; veröffentlichte Versionen werden hier per **Tag** markiert |
| `release/x.y` | Pflege einer **bereits veröffentlichten** Minor-Version (Bugfixes, Sicherheitsupdates), während `main` weiterentwickelt wird |
| `fix/<name>` | Bugfixes, die mehrere Branches betreffen |
| `feature/<name>` | Größere, ausgekoppelte Funktionalitäten |

**Release-Zweige im Detail:**

- Spätestens kurz bevor eine Änderungsmitteilung geschlossen wird, wird für eine veröffentlichte Version ein Branch `release/x.y` angelegt (z. B. `release/0.0` für Versionslinie `0.0.x`).
- In `release/x.y` erfolgen **nur** Bugfixes und Pflege; in `main` die Weiterentwicklung.
- Eine **neue Release-Version** (neue Minor/Major-Linie) wird **immer aus `main`** erzeugt und getaggt.

## Fixes (`fix/`)

Fehler, die in mehreren `release/`-Branches behoben werden müssen, werden in einem **`fix/`-Branch** entwickelt.

1. **Startpunkt:** in der Regel `main`; in Ausnahmefällen der betroffene `release/`-Branch.
2. **Benennung:** aussagekräftig, z. B. `fix/nat-bug` oder `fix/SHBS-42` (JIRA-ID).
3. **Implementierung:** Fix im `fix/`-Branch fertigstellen.
4. **Merge:** Fix in `main` und ggf. alle betroffenen `release/`-Branches mergen.
5. **Branch behalten:** `fix/`-Branch zur Nachvollziehbarkeit **nicht löschen**.

**Einfache Fixes:** können als einzelner Commit direkt auf `main` landen und per **Cherry-Pick** auf weitere Branches übertragen werden. Das ist weniger nachvollziehbar als ein Merge, überschreibt den Code aber nicht vollständig. **Pflicht:** im Cherry-Pick-Commit vermerken:

```text
Cherry Pick <commit-hash>
```

## Features (`feature/`)

Analog zu komplexen Bugfixes für **neue Funktionalität**:

1. Entwicklung in `feature/<name>` (z. B. `feature/ethernet-driver`).
2. **Parallelarbeit:** jederzeit Merge von `main` in den `feature/`-Branch, um Konflikte früh zu erkennen.
3. **Abschluss:** fertiges Feature in `main` mergen; den `feature/`-Branch danach nicht weiterverwenden (Branch darf archiviert bleiben).

## Cherry-Picks

Übertragung eines Commits auf andere Branches ohne vollständigen Merge:

- Im Commit-Text **zwingend:** `Cherry Pick <commit-hash>`
- Typisch für kleine Fixes auf mehrere `release/`-Branches

## Projektspezifische Abweichungen

| Thema | Regel |
|-------|--------|
| **Firmware-Version** | Inkrement nur bei ESP32-Quellcode + Bediener-Freigabe |
| **Release Notes** | Nur bei Versionserhöhung: [releases.md](releases.md) |
| **Push** | Nur durch Bediener — Agent committet lokal nach Freigabe |
| **Agent-Commits** | Siehe `AGENTS.md` §9 und Pro-Prompt-Workflow |

## Pull / Review

- Änderungen vor Merge reviewen (Bediener).
- Kein Force-Push auf `main`.

## Referenzen

- [AGENTS.md](../../AGENTS.md) — globale und projektspezifische Agenten-Regeln
- [releases.md](releases.md) — Changelog
- [README.md](../../README.md) — aktuelle Release-/Versions-Tags
