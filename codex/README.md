# Codex Integration

Use `automation_prompt.md` for a standalone Codex project automation.

Recommended schedule: daily in the morning.

Recommended automation type: standalone/project automation, not a thread heartbeat. Each run should be independent and should report results to Triage.

Requirements:

- Codex app is running.
- This repository is available on disk.
- `OBSIDIAN_VAULT_PATH` points to your local vault.
- `config/interests.yaml` exists and is not committed.
