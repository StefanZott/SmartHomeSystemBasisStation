#!/usr/bin/env bash
# Injects the CLAUDE.md Pro-Prompt workflow reminder at session start.
# Plain bash so the hook runs inside the Linux dev container (no PowerShell there).
set -euo pipefail

# Drain the hook payload on stdin; it is not evaluated.
cat >/dev/null

read -r -d '' REMINDER <<'TXT' || true
Workflow-Reminder: Bei Code-, Konfigurations- oder Doku-Aenderungen den CLAUDE.md Pro-Prompt-Workflow befolgen (Doku lesen -> Code analysieren -> JIRA-Ticket nach Freigabe anlegen -> Plan + Freigabe -> Jira-Subtasks nach Freigabe anlegen -> Subtask auf In Arbeit -> Implementierung -> Validierung -> Doku -> Commit mit Subtask-ID -> Hash als Jira-Kommentar, Subtask Erledigt -> Version/Release-Notes). Offene Arbeit steht in Jira, keine Task-Dateien unter tmp/tasks/ (Archiv). Bei trivialen Fragen verkuerzen; bei Code-Aenderungen keine direkten Edits ohne Freigabe.
TXT

REMINDER=${REMINDER%$'\n'}

printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$REMINDER"
