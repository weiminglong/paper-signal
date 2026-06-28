# Scheduling

PaperSignal can be scheduled several ways. Every scheduler should call the same command:

```bash
paper-signal run --config config/interests.yaml --vault "$OBSIDIAN_VAULT_PATH"
```

## Codex Automations

Use `codex/automation_prompt.md` as a standalone project automation prompt.

Codex Automations are local to the user's Codex app. They require the machine to be on, Codex to be running, and the project to be available on disk.

## launchd

Use `scripts/install_launchd.sh` as a starting point on macOS.

## cron

Use `scripts/install_cron.sh` as a starting point on Linux/macOS.

## GitHub Actions

GitHub Actions can run the workflow in the cloud, but it cannot write directly to a local Obsidian vault. Use it only when the target vault or markdown output is available in the repository or as an artifact.
