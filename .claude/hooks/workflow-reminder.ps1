# Injects the CLAUDE.md Pro-Prompt workflow reminder at session start.
# PowerShell is used because node is often not on PATH in the local dev environment on Windows.

$reminder = @(
    "Workflow-Reminder: Bei Code-, Konfigurations- oder Doku-Aenderungen den CLAUDE.md Pro-Prompt-Workflow befolgen ",
    "(Doku lesen -> Code analysieren -> JIRA-Ticket nach Freigabe anlegen -> Plan + Freigabe -> Jira-Subtasks nach Freigabe anlegen -> Subtask auf In Arbeit -> Implementierung -> Validierung -> Doku -> Commit mit Subtask-ID -> Hash als Jira-Kommentar, Subtask Erledigt -> Version/Release-Notes). Offene Arbeit steht in Jira, keine Task-Dateien unter tmp/tasks/ (Archiv). ",
    "Bei trivialen Fragen verkuerzen; bei Code-Aenderungen keine direkten Edits ohne Freigabe."
) -join ""

$null = [Console]::In.ReadToEnd()

$output = @{
    hookSpecificOutput = @{
        hookEventName    = "SessionStart"
        additionalContext = $reminder
    }
} | ConvertTo-Json -Compress -Depth 5
[Console]::Out.WriteLine($output)
