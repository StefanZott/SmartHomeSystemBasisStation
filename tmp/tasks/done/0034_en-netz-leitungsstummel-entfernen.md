---
status: done
priority: medium
type: bugfix
created: 2026-09-22
jira: SHBS-14
---

# Leitungsstummel am EN-Netz entfernen

## Kontext

ERC-Warnung `unconnected_wire_endpoint` in
`pcb/BasisStation/BasisStation_Layout.kicad_sch`.

Am Netz `EN` laeuft eine Leitung von (52,07 / 55,88) nach (62,23 / 55,88).
Das Label `EN` sitzt bei (59,69 / 55,88). Die letzten **2,54 mm** hinter dem
Label stehen ins Leere — an (62,23 / 55,88) liegt kein weiteres Element.

Elektrisch folgenlos: Das Netz `EN` ist korrekt verbunden
(`J6.1`, `S2.2`, `U6.3`). Es ist reine Zeichnungskosmetik.

## Schritte

- [ ] Endpunkt der Leitung von (62,23 / 55,88) auf die Label-Position
      (59,69 / 55,88) ziehen.
- [ ] Pruefen, dass das Label `EN` weiterhin am Leitungsende haengt.
- [ ] Netzliste exportieren: Netz `/Layout/EN` muss unveraendert
      `J6.1` + `S2.2` + `U6.3` enthalten.
- [ ] ERC: Warnung `unconnected_wire_endpoint` ist verschwunden.

## Done-Bedingung

Warnung weg, Netz `EN` unveraendert, keine weitere Warnung neu entstanden.

## Fortschritt

- 2026-09-22: **Erledigt.** Endpunkt der Leitung in
  `BasisStation_Layout.kicad_sch` von (62,23 / 55,88) auf die Label-Position
  (59,69 / 55,88) gezogen (UUID `1cc9662d-1911-486a-ba8e-4a0f9a1d2a4b`).
  CRLF-Zeilenenden der Datei dabei erhalten (8956 Zeilen, 0 nackte LF).
- Verifikation: ERC von 7 auf **6 Warnungen**, `unconnected_wire_endpoint`
  ist verschwunden, keine neue Warnung entstanden. Netzliste **identisch** —
  `/Layout/EN` weiterhin `J6.1` + `S2.2` + `U6.3`.
