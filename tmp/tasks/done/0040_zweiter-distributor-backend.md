---
title: DigiKey als zweiten Distributor in generate_bom.py anbinden
created: 2026-09-22
jira: SHBS-17
priority: high
type: feature
---

## Kontext

Die Stueckliste haengt an einem Distributor. Der Mouser-Abgleich (SHBS-15) hat
zwei Luecken gezeigt: `PS1` mit Lagerbestand 0 und zwei abgekuendigte Teile.

**Entscheidung des Bedieners vom 2026-09-23: DigiKey.** Konto ist angelegt.
TME entfaellt damit als Kandidat.

Die Abdeckung ist inzwischen geprueft, Ergebnis in
[digikey-abdeckung.md](../../report/2026-09-23_digikey-abdeckung.md). Kurzfassung
fuer die 17 Positionen mit bekannter Teilenummer: **14 aktiv und verfuegbar**,
**1 Luecke** (`S2`, Bourns `1543-650-149` — nur bei Mouser), **2 abgekuendigt**.

Zwei Annahmen aus der ersten Fassung dieses Tasks haben sich als falsch
erwiesen und sind hier korrigiert:

- `PS1` `MP2359DJ-LF-Z` loest DigiKey **nicht**. Der Regler steht dort auf
  „Nicht fuer Neukonstruktionen" und hat in allen drei Verpackungsvarianten
  Lagerbestand 0 — genau wie bei Mouser. Kein Beschaffungs-, sondern ein
  Abkuendigungsproblem.
- Bei `ANT2` (59 gegen 650) und `U6` (78 gegen 6174) ist **Mouser deutlich
  besser bevorratet**. DigiKey ist nicht pauschal die bessere Quelle.

`digikey.de` beantwortet Zugriffe aus dem Container mit HTTP 403 (Bot-Schutz),
genau wie `mouser.de` — Abfragen laufen daher ausschliesslich ueber die API.

## Ziel

`generate_bom.py` fragt je Position Mouser **und** DigiKey ab und weist in der
Mappe Preis, Lagerbestand und Quelle je Anbieter aus, sodass die guenstigste
bzw. ueberhaupt verfuegbare Bezugsquelle sichtbar wird.

## Schritte

- [x] **Bediener:** DigiKey-API-Zugang eingerichtet, `secrets/digikey_api.json`
      abgelegt (Rechte 600) *(2026-09-23)*
- [x] OAuth-2-legged-Flow implementiert in [digikey.py](../../bom/digikey.py):
      Client-Credentials, Token wird bei Bedarf erneuert (599 s Laufzeit ist
      kuerzer als ein voller BOM-Lauf) *(2026-09-23)*
- [x] Distributor-Abfrage hinter einer gemeinsamen Schnittstelle kapseln —
      `mouser_offer()` und `digikey_offer()` liefern ein einheitliches
      Angebotsformat (Nr., Preis, Staffel, Lager, Lebenszyklus, Link)
      *(2026-09-23)*
- [x] DigiKey-Client: Product Information V4, Suche ueber
      Herstellerteilenummer, EUR-Preis, Lagerbestand und Lebenszyklus-Status
      *(2026-09-23)*
- [x] Antworten cachen (`tmp/bom/digikey_cache.json`), in `.gitignore`
      aufgenommen wie der Mouser-Cache *(2026-09-23)*
- [x] Mappe erweitern: Preis und Lagerbestand je Anbieter, Lebenszyklus,
      waehlbare Bezugsquelle (guenstigster lieferbarer Anbieter, bei
      Gleichstand DigiKey — Bediener 2026-09-23), guenstigerer Preis fett,
      Teilsummen je Anbieter *(2026-09-23)*
- [x] **Abdeckungspruefung** der 17 Positionen mit bekannter Teilenummer
      *(2026-09-23)* — Ergebnis in
      [digikey-abdeckung.md](../../report/2026-09-23_digikey-abdeckung.md).
      Die restlichen 29 sind generische Passivteile ohne Teilenummer; fuer sie
      ist nicht die Abdeckung die Frage, sondern die Auswahl (Task 0041)
- [x] Gegenprobe: 46 Positionen, Menge 78, 78 Referenzen je genau einmal;
      LibreOffice rechnet fehlerfrei (0 Formelfehler), Summe 35,59 EUR =
      Zeilensumme (DigiKey 34,42 + Mouser 1,17) *(2026-09-23)*
- [x] Doku: Abschnitt „Bestellfaehige Stueckliste" in
      [hardware.md](../../../docs/project/hardware.md) ergaenzt *(2026-09-23)*
- [ ] Commit

## Was der Bediener noch tun muss

Das blosse Kundenkonto reicht nicht — die API braucht eine registrierte
Anwendung:

1. Auf [developer.digikey.com](https://developer.digikey.com) mit dem
   DigiKey-Konto anmelden.
2. Eine **Organization** anlegen (einmalig).
3. Darin eine **App** erstellen.
4. Die App auf das API-Produkt **Product Information V4** abonnieren — und
   zwar in der **Production**-Umgebung, nicht nur Sandbox. Sandbox liefert
   Testdaten, keine echten Preise.
5. **Client ID** und **Client Secret** kopieren.
6. Als OAuth-Callback `https://localhost:8139/digikey_callback` eintragen. Das
   Feld ist Pflicht, obwohl wir es nicht nutzen: fuer die reine Produktsuche
   genuegt der **2-legged-Flow** (Client Credentials), es ist also kein
   Benutzer-Login und keine Weiterleitung noetig.

**Erledigt am 2026-09-23.** Ein Kreditkonto war entgegen der Befuerchtung
**nicht** noetig — der Produktivzugang funktioniert.

## Fortschritt

- 2026-09-22: Task angelegt (damals noch mit TME als Empfehlung).
- 2026-09-23: Auf DigiKey umgestellt, Bediener hat sich entschieden und das
  Konto angelegt. Stichproben zur Abdeckung ergaenzt, Einrichtungsschritte
  dokumentiert.
- 2026-09-23 (2): **Zugang eingerichtet und verifiziert.** Token HTTP 200,
  Product Information V4 liefert EUR-Preise aus dem deutschen Shop. Kein
  Kreditkonto noetig. `digikey.py` angelegt, Abdeckungspruefung der 17
  identifizierten Positionen durchgefuehrt: 14 aktiv, 1 Luecke (`S2`,
  Bourns — nur bei Mouser), 2 abgekuendigt (`J1`/`J_PWR1` obsolet, `PS1`
  NRND, beide Lager 0 bei beiden Distributoren).
  **Naechster Schritt:** `digikey.py` in `generate_bom.py` einhaengen, damit
  die Mappe beide Anbieter nebeneinander ausweist.
- 2026-09-23 (3): **Mappe mit beiden Anbietern erzeugt.** DigiKey-Client um
  Stichwortsuche erweitert (loest `D11` SS34, `D12` SMAJ5.0A und `U1`
  D3V3XA4B10LP-7 auf). Ergebnis: 16 von 46 Positionen bepreist, 15 ueber
  DigiKey, 1 ueber Mouser (`S2`). `PS1` steht mit Lager 0 auf DigiKey,
  `J1`/`J_PWR1` ohne Angebot (Rolle MOQ 6000, obsolet) — beides
  „Ersatz noetig", Task 0041. Hinweis: `ruff` ist im Container nicht
  installiert, Lint-Pruefung daher nicht gelaufen.

## Commits

- d1870af DigiKey-Zugang und Abdeckungspruefung (Teilschritt, Task noch offen)

## Offene Fragen

- Keine mehr zum Zugang. Offen ist die Ersatzwahl fuer `PS1` und `J1`/`J_PWR1`
  — das gehoert zu Task 0041 und blockiert diesen Task nicht.
