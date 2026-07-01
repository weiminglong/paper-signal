# PaperSignal

A local-first research paper agent that turns new papers into daily Obsidian notes.

PaperSignal fetches recent papers, scores them against your research interests, and writes a daily read into your Obsidian vault. It runs two ways: a fast deterministic CLI, or a Claude Code **round-table** in which a Moderator and persona subagents debate each top paper and author the note. It is designed to run as a normal CLI first, with optional scheduling through Codex Automations, Claude Code, cron, launchd, Windows Task Scheduler, or GitHub Actions.

## No coding experience? Start here

You don't need to write any code, edit any files, or use the terminal. If you have
[Claude Code](https://claude.com/claude-code) and [Obsidian](https://obsidian.md), Claude Code
does the whole setup for you — you just answer a few plain-English questions.

1. **Get this project onto your computer.** Click the green **Code** button on GitHub →
   **Download ZIP**, then unzip it. (Or just ask Claude Code to download it for you.)
2. **Open Claude Code in that folder.**
3. **Paste this** and answer its questions:

   > Set up PaperSignal for me. I follow research on **_(your topics — e.g. AI agents, robotics)_**,
   > and my Obsidian vault is at **_(the folder path, or say "help me find it")_**.

Claude Code will install what's needed, ask about your interests, and generate your first daily
paper report. From then on, just say **“run my paper report”** whenever you want a fresh one.

> Under the hood this runs the `paper-signal-setup` skill (or the `/paper-signal-setup`
> command). Everything below is for people who want to run it themselves from the terminal.

## Status

Early scaffold. The current implementation includes:

- arXiv search
- YAML-based research interests
- deterministic paper scoring
- a deterministic quick-scan panel (`paper-signal run`)
- a Claude Code multi-agent round-table that authors deep daily notes (`paper-signal fetch` + skill)
- Obsidian daily note rendering
- local state for previously seen papers
- Codex and Claude Code integration prompts

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

export OBSIDIAN_VAULT_PATH="/path/to/your/Obsidian Vault"
paper-signal init        # scaffolds config/interests.yaml + vault folders
paper-signal doctor      # checks config, vault, and arXiv reachability
paper-signal run --dry-run
paper-signal run
```

`paper-signal init` writes a starter `config/interests.yaml` (edit the domains/keywords),
and `paper-signal doctor` tells you exactly what, if anything, is misconfigured.

### Zero-install (no clone)

Run it straight from GitHub with [uv](https://docs.astral.sh/uv/) or
[pipx](https://pipx.pypa.io/) — no clone, no manual venv. Run `init` first (it writes
`config/interests.yaml` into the current directory), then run from that same directory:

```bash
export OBSIDIAN_VAULT_PATH="/path/to/your/Obsidian Vault"

# uv (ephemeral):
uvx --from git+https://github.com/weiminglong/paper-signal paper-signal init
$EDITOR config/interests.yaml     # tune your domains/keywords
uvx --from git+https://github.com/weiminglong/paper-signal paper-signal run

# or pipx (persistent install):
pipx install git+https://github.com/weiminglong/paper-signal
paper-signal init && $EDITOR config/interests.yaml && paper-signal run
```

`init` and `run` must share a working directory — `init` writes the config there and
`run` reads it back (relative `config/interests.yaml`).

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
paper-signal init                                          # scaffold config + vault folders
paper-signal doctor                                        # verify config, vault, arXiv reachability
paper-signal run --config config/interests.yaml            # deterministic quick scan, writes the note
paper-signal run --config config/interests.yaml --dry-run  # render without writing
paper-signal fetch --config config/interests.yaml          # emit JSON candidates for the round-table (no writes)
paper-signal commit --ids 2601.00001,2601.00002            # mark papers seen after an agent writes the note
paper-signal init-vault --vault "$OBSIDIAN_VAULT_PATH"
```

Most commands default `--config` to `config/interests.yaml` (or `$PAPER_SIGNAL_CONFIG`)
and `--vault` to `$OBSIDIAN_VAULT_PATH`, so after `init` you can just run `paper-signal run`.

## Round-Table (Claude Code multi-agent analysis)

For deep analysis, Claude Code is the LLM brain — no separate API key. The CLI fetches and
scores; Claude Code runs a round-table over the top papers and writes the note.

The framework (adapted from Li Jigang's `圆桌讨论` / "Roundtable Seminar") seats a
**Moderator** and a panel of **persona subagents** — Methodologist (INTJ), Empiricist
(ISTJ), Skeptic (ENTP), Practitioner (ESTP), Theorist (INTP), Connector (ENFP). For each
top paper (`daily.deep_analysis_count`), the personas argue across two dialectical rounds;
the Moderator names the core contradiction, draws an ASCII framework chart, and issues a
`deep-read / skim / queue / skip` verdict with knowledge-network links. See
`claude-code/skills/paper-signal/SKILL.md` and `prompts/`.

```bash
# In Claude Code:
/paper-signal          # or invoke the paper-signal skill
```

See [`examples/sample-daily-note.md`](examples/sample-daily-note.md) for a real note the
round-table produced (2 papers deep-analyzed by the 4-persona panel, 1 triaged).

## Codex Automations

Use `codex/automation_prompt.md` as the prompt for a standalone project automation. Codex scheduling is user-local: the machine must be powered on, Codex must be running, and this project must be available on disk when the automation runs.

## Claude Code

This repo includes Claude Code entry points for both setup and daily use:

- **Setup** — `claude-code/skills/paper-signal-setup/SKILL.md` (or `/paper-signal-setup`)
  walks a non-technical user through the whole install/config by conversation. See
  [No coding experience? Start here](#no-coding-experience-start-here).
- **Daily report** — `claude-code/skills/paper-signal/SKILL.md` (or `/paper-signal`) drives
  the round-table workflow (`paper-signal fetch` → multi-agent analysis → note), and falls
  back to the deterministic `paper-signal run` for a quick scan.

## Inspiration

PaperSignal is inspired by [juliye2025/evil-read-arxiv](https://github.com/juliye2025/evil-read-arxiv), especially its arXiv search, paper analysis, and Obsidian note workflow ideas. This project reimplements the workflow as a portable CLI-first system with optional Codex and Claude Code orchestration.

## License

MIT
