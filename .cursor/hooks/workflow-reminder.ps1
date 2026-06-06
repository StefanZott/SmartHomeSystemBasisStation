# Injects the AGENTS.md Pro-Prompt workflow reminder at session start.
# PowerShell is used because node is often not on PATH in Cursor's hook environment on Windows.

$reminder = @(
    "Workflow-Reminder: Bei Code-, Konfigurations- oder Doku-Aenderungen den AGENTS.md Pro-Prompt-Workflow befolgen ",
    "(Doku lesen -> Code analysieren -> JIRA-Entwurf -> Plan + Freigabe -> Tasks -> Implementierung -> Validierung -> Doku -> Commit-Vorschlag -> Version/Release-Notes). ",
    "Bei trivialen Fragen verkuerzen; bei Code-Aenderungen keine direkten Edits ohne Freigabe."
) -join ""

$null = [Console]::In.ReadToEnd()

$output = @{ additional_context = $reminder } | ConvertTo-Json -Compress
[Console]::Out.WriteLine($output)
