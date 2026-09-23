#!/usr/bin/env bash
# Injects the CLAUDE.md Pro-Prompt workflow reminder at session start.
# Plain bash so the hook runs inside the Linux dev container (no PowerShell there).
set -euo pipefail

# Drain the hook payload on stdin; it is not evaluated.
cat >/dev/null

read -r -d '' REMINDER <<'TXT' || true
Workflow-Reminder: Bei Code-, Konfigurations- oder Doku-Aenderungen den CLAUDE.md Pro-Prompt-Workflow befolgen (Doku lesen -> Code analysieren -> JIRA-Entwurf -> Plan + Freigabe -> Tasks -> Implementierung -> Validierung -> Doku -> Commit-Vorschlag -> Version/Release-Notes). Bei trivialen Fragen verkuerzen; bei Code-Aenderungen keine direkten Edits ohne Freigabe.
TXT

REMINDER=${REMINDER%$'\n'}

printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$REMINDER"
