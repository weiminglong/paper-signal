# PaperSignal Setup

Set up PaperSignal from scratch for a non-technical user, through conversation. Do all the
technical work yourself; the user only answers plain-English questions.

Follow `claude-code/skills/paper-signal-setup/SKILL.md`. In brief:

1. Welcome them and explain what PaperSignal does in one sentence.
2. Check prerequisites and fix with their permission. If the CLI is missing, install it via a
   fallback ladder (`pip install -e .` → `--user` → venv → uvx/pipx → `python3 -m paper_signal`).
   If they have no Obsidian or no vault, point them to obsidian.md and/or offer to create a vault
   with `paper-signal init-vault`.
3. Interview them in plain English for their research topics and keywords (no arXiv codes).
4. Confirm the vault path (reject an obviously wrong one, e.g. a Windows path on a Mac). Pass
   `--vault` explicitly on each command — don't rely on an exported env var.
5. Run `paper-signal init`, then write `config/interests.yaml` for them from the interview.
6. Run `paper-signal doctor` and fix anything (an arXiv warning is just network — proceed).
7. Do a first `paper-signal run` so they see a real report, show them where it landed, and tune
   if it's empty (widen keywords) or noisy (tighten / exclude).
8. Offer the deeper AI round-table (note it uses more usage); set up scheduling only if asked.

Never ask the user to write YAML, run commands, or read errors, and never echo raw CLI output —
summarize outcomes in plain English. Get consent before installing software or touching files
outside the project.
