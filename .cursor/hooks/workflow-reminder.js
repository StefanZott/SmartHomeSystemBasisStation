#!/usr/bin/env node
/**
 * Injects the AGENTS.md Pro-Prompt workflow reminder at session start.
 * Cursor beforeSubmitPrompt does not support context injection; sessionStart does.
 */

const reminder =
  "Workflow-Reminder: Bei Code-, Konfigurations- oder Doku-Änderungen den AGENTS.md Pro-Prompt-Workflow befolgen " +
  "(Doku lesen → Code analysieren → JIRA-Entwurf → Plan + Freigabe → Tasks → Implementierung → Validierung → Doku → Commit-Vorschlag → Version/Release-Notes). " +
  "Bei trivialen Fragen verkürzen; bei Code-Änderungen keine direkten Edits ohne Freigabe.";

let input = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => {
  input += chunk;
});
process.stdin.on("end", () => {
  process.stdout.write(JSON.stringify({ additional_context: reminder }));
});
