# PaperSignal

Generate today's research read using the **round-table** workflow: fetch arXiv
candidates, run a multi-agent panel (Moderator + persona subagents) over the top papers,
and author an Obsidian daily note.

Follow `claude-code/skills/paper-signal/SKILL.md`. In brief:

1. Ensure `config/interests.yaml` and `OBSIDIAN_VAULT_PATH` exist; `pip install -e .` if the CLI is missing.
2. `paper-signal fetch --config config/interests.yaml --vault "$OBSIDIAN_VAULT_PATH"` → parse the JSON candidates.
3. For each `deep: true` paper, run the round-table protocol in `prompts/roundtable.md`
   (spawn persona subagents per `prompts/representative.md`, 2 rounds, synthesize a verdict).
4. Write the daily note yourself, plus per-paper deep notes for `deep-read` verdicts.
5. `paper-signal commit --vault "$OBSIDIAN_VAULT_PATH" --from-fetch <candidates.json>` to mark papers seen.
6. Summarize: fetched / selected / deep counts, the daily note path, and any failures.

For a fast deterministic list with no agents, run instead:

```bash
paper-signal run --config config/interests.yaml --vault "$OBSIDIAN_VAULT_PATH"
```

Do not overwrite manual notes, and do not commit personal config or vault files.
