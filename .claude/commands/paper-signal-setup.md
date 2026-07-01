# PaperSignal Setup

Set up PaperSignal from scratch for a non-technical user, through conversation. Do all the
technical work yourself; the user only answers plain-English questions.

Follow `claude-code/skills/paper-signal-setup/SKILL.md`. In brief:

1. Welcome them and explain what PaperSignal does in one sentence.
2. Check prerequisites (the `paper-signal` CLI, Python 3.9+, Obsidian vault) and fix with
   their permission — `pip install -e .` if the CLI is missing.
3. Interview them in plain English for their research topics and keywords (no arXiv codes).
4. Confirm the Obsidian vault path and set `OBSIDIAN_VAULT_PATH`.
5. Run `paper-signal init`, then write `config/interests.yaml` for them from the interview.
6. Run `paper-signal doctor` and fix anything.
7. Do a first `paper-signal run` so they see a real report, and show them where it landed.
8. Offer the deeper AI round-table (note it uses more usage); set up scheduling only if asked.

Never ask the user to write YAML, run commands, or read errors — you handle all of it. Get
consent before installing software or touching files outside the project.
