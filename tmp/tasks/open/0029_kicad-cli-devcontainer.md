---
title: KiCad-CLI im Dev-Container bereitstellen
created: 2026-09-19
jira: SHBS-13
priority: medium
type: feature
---

## Kontext

Der Dev-Container basiert auf `espressif/idf:v5.5.2` und enthaelt nur
ESP-IDF-Tooling. `kicad-cli` fehlt, `/usr/lib/kicad` existiert nicht, und der
Container-User `esp` (uid 1001) hat kein `sudo` — eine Nachinstallation zur
Laufzeit ist nicht moeglich.

Folge: Aenderungen an den Schaltplaenen unter `pcb/BasisStation/` werden als
Textdateien bearbeitet, koennen im Container aber nicht verifiziert werden.
ERC-Report, Netzliste und Stueckliste muessen manuell in der KiCad-GUI erzeugt
und eingecheckt werden (zuletzt Commit b98c288).

Randbedingung: Die Projektdateien tragen Format `version 20250114` → KiCad 9
erforderlich. Auf Ubuntu 24.04 (noble) ueber PPA `kicad/kicad-9.0-releases`.

## Ziel

Nach einer Schaltplan-Aenderung lassen sich ERC, Netzliste und Stueckliste
direkt im Container per `kicad-cli` erzeugen und pruefen, bevor die Aenderung
dem Bediener vorgelegt wird.

## Schritte

- [x] `.devcontainer/Dockerfile`: KiCad-9-PPA und Paket `kicad` ergaenzen
      (inkl. Symbol-/Footprint-/3D-Bibliotheken), `xvfb` als Fallback fuer
      Export-Befehle, die einen X-Server verlangen. Installation vor dem
      `USER ${CONTAINER_USER}`-Wechsel, apt-Listen aufraeumen.
- [x] Bediener: Container neu bauen (Rebuild Container in VS Code).
- [x] Verifikation im neuen Container: `kicad-cli version`, danach
      `kicad-cli sch erc` und `kicad-cli sch export netlist` gegen
      `pcb/BasisStation/BasisStation.kicad_sch` — Ergebnis mit den
      eingecheckten `ERC.rpt` / `BasisStation.net` abgleichen.
- [x] `docs/project/hardware.md`: Abschnitt zur KiCad-CLI-Nutzung ergaenzen
      (welche Befehle, wofuer, welche Reports daraus entstehen).
- [x] Datei-Index in `CLAUDE.md` pruefen — nur noetig, falls eine neue
      Markdown-Datei entsteht.

## Fortschritt

- 2026-09-19: Task angelegt, noch nicht begonnen. Umgebung analysiert:
  kein `kicad-cli`, kein `sudo`, `/usr/local/bin` nicht beschreibbar →
  Loesung muss ueber das Dockerfile laufen. Jira-Ticket SHBS-13 angelegt.
- 2026-09-19: Dockerfile-Block ergaenzt (PPA `kicad/kicad-9.0-releases`,
  Pakete `kicad`, `kicad-symbols`, `kicad-footprints`, `xvfb`), eingefuegt vor
  dem `USER`-Wechsel. `DEBIAN_FRONTEND=noninteractive` im RUN-Block gesetzt,
  weil der vorhandene `ARG DEBIAN_FRONTEND=nointeractive` (Tippfehler) als
  ungueltiger Frontend-Name wirkungslos bleibt.
- 2026-09-19: PPA-Inhalt gegen `dists/noble/main/binary-amd64/Packages.gz`
  geprueft. Befund: `kicad-templates` existiert dort **nicht** (nur
  `kicad-nightly-templates`) — war zunaechst in der Paketliste und haette den
  Build brechen lassen, wurde entfernt. Verfuegbar ist KiCad `9.0.9`.
  Groessen: kicad 129 MB, kicad-symbols 212 MB, kicad-footprints 154 MB,
  kicad-packages3d 3214 MB (bewusst ausgelassen). Die urspruengliche
  Schaetzung von 1-2 GB Image-Zuwachs war zu hoch; realistisch sind knapp
  500 MB plus GUI-Abhaengigkeiten.
- 2026-09-19: `docs/project/hardware.md` um Abschnitt
  "KiCad-CLI im Dev-Container (SHBS-13)" ergaenzt, `last_updated` auf
  2026-09-19 gesetzt. Kein neuer Doku-File → CLAUDE.md-Index unveraendert.
- 2026-09-19: **Verifikation steht aus.** Im Container ist kein Docker
  verfuegbar, der Build ist von hier aus nicht pruefbar. Geprueft wurde nur
  statisch: Zeilenfortsetzungen im Dockerfile intakt, alle Paketnamen im PPA
  bzw. in noble vorhanden. Naechster konkreter Schritt: Bediener baut den
  Container neu, danach `kicad-cli version` und ERC/Netzliste gegen die
  eingecheckten Artefakte abgleichen.

- 2026-09-19: **Container neu gebaut, Verifikation durchgefuehrt.**
  `kicad-cli version` → 9.0.9. Abgleich gegen die eingecheckten Artefakte:
  - ERC: deckungsgleich (7 Verstoesse, 0 Fehler, 7 Warnungen).
  - Netzliste: deckungsgleich (102 Netze, identische Namen).
  - Stueckliste: deckungsgleich bis auf die DNP-Spalte (`DNP` statt
    `Nicht bestuecken` — die GUI laeuft deutsch). Noetig sind dafuer
    `--fields`, `--labels`, `--group-by 'Value,Footprint'` und
    `--ref-range-delimiter ''`; ohne diese Optionen liefert die CLI
    ungruppierte Zeilen ohne Datasheet-Spalte.
  - DRC: **abweichend** — 418 statt 8 Verstoesse, siehe offene Fragen.
- 2026-09-19: Beim ersten ERC-Lauf 138 statt 7 Verstoesse, davon 131
  `lib_symbol_issues` ("library 'power' not included"). Ursache:
  `~/.config/kicad/9.0/sym-lib-table` fehlt — `kicad-cli` legt beim ersten
  Start nur `fp-lib-table` an. Nach Kopie von
  `/usr/share/kicad/template/sym-lib-table` stimmte der Report. Fix ins
  Dockerfile uebernommen (beide Vorlagen werden nach dem `USER`-Wechsel
  kopiert); im laufenden Container wurde er bereits manuell angewandt, die
  Dockerfile-Variante ist erst nach dem naechsten Rebuild verifiziert.
- 2026-09-19: `docs/project/hardware.md` um Bibliothekstabellen-Hinweis,
  vollstaendigen BOM-Befehl und Abschnitt "Stand der Verifikation" ergaenzt.

## Commits

- (noch keine)

## Offene Fragen

- Geklaert: Image-Zuwachs liegt bei knapp 500 MB (kicad + symbols +
  footprints) plus GUI-Abhaengigkeiten, nicht bei 1-2 GB. Ein AppImage waere
  damit kein nennenswerter Gewinn — PPA-Variante bleibt.
- Offen: DRC-Abweichung. `kicad-cli pcb drc` meldet 418 Verstoesse
  (229 `clearance`, 104 `solder_mask_bridge`, 78 `hole_clearance`), der
  eingecheckte `DRC.rpt` aus der GUI nur 8. Alle Zusatzmeldungen paaren sich
  mit einer der beiden GND-Zonen, Abstand jeweils `actual 0.0000 mm`.
  Vermutung: die GUI fuellt Zonen vor dem DRC neu, die CLI rechnet mit dem im
  Board gespeicherten, veralteten Fuellstand. `kicad-cli pcb drc` bietet keine
  Fuell-Option. Zu pruefen: Zonen in der GUI neu fuellen, Board speichern,
  CLI-DRC wiederholen. Eigener Task sinnvoll — ausserhalb des Scopes von
  SHBS-13, dessen Ziel ERC/Netzliste/Stueckliste war.
- Offen: `ARG DEBIAN_FRONTEND=nointeractive` in Zeile 3 des Dockerfiles ist
  ein Tippfehler (`noninteractive`). Hier nicht angefasst, weil ausserhalb
  des Scopes von SHBS-13 — eigener Task sinnvoll.
- Keine Versionserhoehung und kein Release-Notes-Eintrag: reine Aenderung der
  Build-Umgebung, kein ESP32-Quellcode (Abweichungs-Regel in CLAUDE.md).
