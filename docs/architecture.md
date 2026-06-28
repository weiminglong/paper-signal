# Architecture

PaperSignal is designed as a CLI-first pipeline with thin scheduler integrations.

```text
sources -> scoring -> agent panel -> Obsidian writer -> state
```

## Stages

1. Sources fetch candidate papers from arXiv and future providers.
2. Scoring ranks papers against the user's YAML research interests.
3. Agent panel adds a structured discussion over the shortlist.
4. Obsidian writer renders markdown into the vault.
5. State records seen papers to reduce repeated recommendations.

## Why CLI-first

Schedulers should not own workflow logic. Codex Automations, Claude Code, cron, launchd, and GitHub Actions all call `paper-signal run`.

## Future Extension Points

- Semantic Scholar citation enrichment
- conference paper search
- PDF and figure extraction
- LLM-backed agent panel
- deep paper notes
- feedback-based preference learning
