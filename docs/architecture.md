# Architecture

PaperSignal is a CLI-first pipeline with two analysis paths over a shared core.

```text
sources -> scoring -> select ┬─► deterministic panel -> Obsidian writer -> state   (path A: `run`)
                             └─► JSON candidates -> Claude Code round-table -> note  (path B: `fetch`)
```

## Shared core

1. **Sources** fetch candidate papers from arXiv (and future providers).
2. **Scoring** ranks papers against the user's YAML research interests.
3. **Select** keeps the top `recommendation_count`; the top `deep_analysis_count` are
   flagged for deep analysis.

## Path A — deterministic quick scan (`paper-signal run`)

A rule-based panel (`paper_signal/agents/panel.py`) adds a short discussion, the Obsidian
writer renders a Jinja2 note, and state records seen papers. No LLM; instant; reproducible.

## Path B — Claude Code round-table (`paper-signal fetch` + skill)

`paper-signal fetch` emits the selected candidates as JSON (with `deep` flags and the
exact note path) and writes nothing. Claude Code, acting as **Moderator**, runs a
multi-agent round-table — persona subagents debate each deep paper across two dialectical
rounds — then authors the daily note and per-paper notes itself. `paper-signal commit`
marks the papers seen. The model is the Claude Code session; no separate API key is used.

The round-table framework lives in `prompts/` (`roundtable.md`, `representative.md`,
`deep_analysis.md`, `daily_synthesis.md`) and is orchestrated by
`claude-code/skills/paper-signal/SKILL.md`.

## Why CLI-first

Schedulers should not own workflow logic. Codex Automations, cron, launchd, and GitHub
Actions call `paper-signal run`; Claude Code drives `paper-signal fetch` for the
round-table.

## Future Extension Points

- Semantic Scholar citation enrichment
- conference paper search
- PDF and figure extraction (round-table currently reads title + abstract + metadata)
- feedback-based preference learning
- genuine multi-turn cross-talk between persona subagents within a round
