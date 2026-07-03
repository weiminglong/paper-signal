# Codex Integration

Use `automation_prompt.md` as the prompt for a standalone Codex project automation.

Recommended schedule: daily in the morning. Recommended automation type:
standalone/project automation, not a thread heartbeat — each run is independent.

Requirements:

- Codex app is running and this repository is available on disk.
- `config/interests.yaml` exists (run `paper-signal init` once, or copy
  `config/interests.example.yaml`); keep it uncommitted.
- The vault path is set via `vault_path` in the config or `OBSIDIAN_VAULT_PATH`
  (resolution order: `--vault` → `OBSIDIAN_VAULT_PATH` → config `vault_path`).

The automation runs the quick list (English). For the richer AI-written
"full report", run the prompt interactively in Codex and follow
`claude-code/skills/paper-signal/SKILL.md` — the workflow is agent-agnostic
(fetch JSON → analyze → write the note → commit).
