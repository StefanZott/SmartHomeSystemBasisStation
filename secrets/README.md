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

### `.env`

Umgebungsvariablen für den Dev-Container, aktuell `GITHUB_PAT` für den
GitHub-MCP-Server (`.mcp.json`).

Format: `KEY=wert` je Zeile, **ohne Anführungszeichen**. Die Datei wird per
`--env-file` in `runArgs` (`.devcontainer/devcontainer.json`) direkt von Docker
geladen — und Docker entfernt keine Anführungszeichen, sondern übernimmt sie in
den Wert. Ein gequoteter PAT landet dadurch als `Bearer "ghp_..."` im
Authorization-Header und wird von GitHub mit
`Authorization header is badly formatted` abgewiesen.

Das Laden über `--env-file` stellt sicher, dass die Variablen in PID 1 und damit
in jedem Kindprozess liegen — insbesondere im VS-Code-Extension-Host, der Claude
Code startet. Der `postCreateCommand` hängt die Datei zusätzlich ins `~/.bashrc`
ein, das greift aber nur für interaktive Terminals.

Konsequenz: Fehlt `secrets/.env`, startet der Container nicht. Die Datei ist
Voraussetzung, nicht optional.

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

