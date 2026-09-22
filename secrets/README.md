---
status: active
last_updated: 2026-09-22
---

# Local secrets (not for Git)

Store passwords, API keys, and certificates here only on your machine.

- Contents of this directory are ignored by Git (see root `.gitignore`).
- Never commit files from `secrets/` except `.gitkeep` and this README.
- Use project documentation under `docs/project/security.md` for handling credentials.

## Erwartete Dateien

| Datei | Inhalt | Verwendet von |
| ----- | ------ | ------------- |
| `mouser_api_key` | Mouser **Search**-API-Schlüssel (UUID, eine Zeile) | Stücklisten-Abfrage gegen `api.mouser.com` |
| `.env` | Lokale Umgebungsvariablen | Entwicklungsumgebung |

### `mouser_api_key`

Kostenlos über den [Mouser API Hub](https://www.mouser.com/en/api-hub/) anzufordern.
Mouser vergibt **zwei** Schlüssel — Cart/Order und Search. Benötigt wird der
**Search**-Schlüssel.

Den Schlüssel aus dem **deutschen** Mouser-Konto anfordern: Die API liefert
Beschreibungen, Preise und Produktlinks passend zum Shop, an dem der Schlüssel
hängt. Ein Schlüssel vom US-Shop liefert USD und `mouser.com`-Links.

Format: eine Zeile, reine UUID, keine Anführungszeichen. Dateirechte `600`.

Die Webseite `www.mouser.de` ist aus dem Dev-Container **nicht** erreichbar
(Bot-Schutz); `api.mouser.com` dagegen schon. Abfragen laufen deshalb
ausschliesslich über die API, nicht über Scraping.

