# Injects the CLAUDE.md Pro-Prompt workflow reminder at session start.
# PowerShell is used because node is often not on PATH in the local dev environment on Windows.

$reminder = @(
    "Workflow-Reminder: Bei Code-, Konfigurations- oder Doku-Aenderungen den CLAUDE.md Pro-Prompt-Workflow befolgen ",
    "(Doku lesen -> Code analysieren -> JIRA-Entwurf -> Plan + Freigabe -> Tasks -> Implementierung -> Validierung -> Doku -> Commit-Vorschlag -> Version/Release-Notes). ",
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
