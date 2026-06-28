---
name: paper-signal
description: Run PaperSignal to fetch research papers, score them against user interests, and write daily Obsidian notes.
---

# PaperSignal Skill

Use this skill when the user asks Claude Code to fetch daily research papers, generate a daily read, update an Obsidian research vault, or run the PaperSignal workflow.

## Requirements

- The `paper-signal` CLI is installed in the active Python environment.
- `config/interests.yaml` exists in the repository.
- `OBSIDIAN_VAULT_PATH` points to the user's Obsidian vault.

## Workflow

1. Check the config and vault path:

   ```bash
   test -f config/interests.yaml
   test -n "$OBSIDIAN_VAULT_PATH"
   ```

2. Run a dry run first if the user is setting up the project:

   ```bash
   paper-signal run --config config/interests.yaml --vault "$OBSIDIAN_VAULT_PATH" --dry-run
   ```

3. Run the daily workflow:

   ```bash
   paper-signal run --config config/interests.yaml --vault "$OBSIDIAN_VAULT_PATH"
   ```

4. Report the generated daily note path and any failures.

## Rules

- Do not commit personal config, state, API keys, or vault files.
- Do not overwrite manual notes.
- Keep scheduler-specific behavior outside the core CLI.
