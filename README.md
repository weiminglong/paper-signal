# PaperSignal

A local-first research paper agent that turns new papers into daily Obsidian notes.

PaperSignal fetches recent papers, scores them against your research interests, runs a small review panel over the shortlist, and writes a daily read into your Obsidian vault. It is designed to run as a normal CLI first, with optional scheduling through Codex Automations, Claude Code, cron, launchd, Windows Task Scheduler, or GitHub Actions.

## Status

Early scaffold. The current implementation includes:

- arXiv search
- YAML-based research interests
- deterministic paper scoring
- lightweight agent-panel synthesis
- Obsidian daily note rendering
- local state for previously seen papers
- Codex and Claude Code integration prompts

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

cp config/interests.example.yaml config/interests.yaml
export OBSIDIAN_VAULT_PATH="/path/to/your/Obsidian Vault"

paper-signal run --config config/interests.yaml --dry-run
paper-signal run --config config/interests.yaml
```

The daily note is written to:

```text
$OBSIDIAN_VAULT_PATH/10_Daily/YYYY-MM-DD-paper-recommendations.md
```

## Configuration

PaperSignal reads a YAML config with research domains, keywords, arXiv categories, and daily run settings. Start from:

```text
config/interests.example.yaml
```

Keep your personal config out of git:

```text
config/interests.yaml
```

## Obsidian Layout

PaperSignal creates these directories when needed:

```text
10_Daily/
20_Research/Papers/
99_System/PaperSignal/
```

Runtime state is stored under:

```text
99_System/PaperSignal/state.json
```

## Commands

```bash
paper-signal run --config config/interests.yaml
paper-signal run --config config/interests.yaml --dry-run
paper-signal init-vault --vault "$OBSIDIAN_VAULT_PATH"
```

## Codex Automations

Use `codex/automation_prompt.md` as the prompt for a standalone project automation. Codex scheduling is user-local: the machine must be powered on, Codex must be running, and this project must be available on disk when the automation runs.

## Claude Code

This repo includes two Claude Code entry points:

- `.claude/commands/paper-signal.md` for a project slash command.
- `claude-code/skills/paper-signal/SKILL.md` for installing as a reusable skill.

Both call the same CLI instead of duplicating logic.

## Inspiration

PaperSignal is inspired by [juliye2025/evil-read-arxiv](https://github.com/juliye2025/evil-read-arxiv), especially its arXiv search, paper analysis, and Obsidian note workflow ideas. This project reimplements the workflow as a portable CLI-first system with optional Codex and Claude Code orchestration.

## License

MIT
