# Scheduling

Unattended scheduling runs the **deterministic** path (`paper-signal run`) — no LLM, no
API key. The Claude Code round-table (path B) is interactive; to schedule *that*, use a
Claude Code routine/cron that invokes the `paper-signal` skill.

All local schedulers call one canonical runner, `scripts/run-daily.sh`, which loads a
project `.env`, resolves the executable, ensures the log directory exists, and passes the
vault explicitly (schedulers do not inherit your shell environment).

## Setup (once)

Create `<repo>/.env` from `.env.example`:

```bash
OBSIDIAN_VAULT_PATH="/path/to/your/Obsidian Vault"
# PAPER_SIGNAL_CONFIG="/path/to/config/interests.yaml"   # optional
# PAPER_SIGNAL_BIN="/path/to/paper-signal"               # optional override
```

Make sure the CLI is installed (`pip install -e .` creates `.venv/bin/paper-signal`, or set
`PAPER_SIGNAL_BIN`). Verify everything with `paper-signal doctor`.

## cron (Linux/macOS)

```bash
scripts/install_cron.sh          # daily at 07:00
scripts/install_cron.sh 9        # daily at 09:00
```

Logs: `data/cron.log`.

## launchd (macOS)

```bash
scripts/install_launchd.sh       # daily at 07:00
scripts/install_launchd.sh 9     # daily at 09:00
```

Logs: `data/launchd.out.log`, `data/launchd.err.log`.

## Codex Automations

Use `codex/automation_prompt.md` as a standalone project automation prompt. Codex
Automations are local to the user's Codex app: the machine must be on, Codex running, and
the project on disk.

## GitHub Actions

GitHub Actions can run the workflow in the cloud, but it cannot write to a local Obsidian
vault. Use it only when the target vault or markdown output lives in the repository or is
exported as an artifact.
