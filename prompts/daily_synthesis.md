# Daily Synthesis Prompt

After the per-paper round-tables finish, the Moderator writes the top of the daily note:
a cross-paper briefing that turns the day's papers into one structured read. This echoes
the round-table's closing move — `generate-knowledge-network` — at the level of the whole
day rather than a single paper.

Produce:

- **Today's signal** — the one or two threads connecting today's papers (a shared
  problem, a converging method, a disagreement between papers). One short paragraph.
- **Knowledge network** — a small **ASCII diagram** linking today's papers to each other
  and to existing vault notes/threads. Nodes are paper short-titles or `[[note]]` names;
  edges are the relationship (extends, contradicts, applies, same-method). Keep it dense
  and honest — connect only what genuinely connects.
- **Top 3 to read first** — ranked, each with one line of *why* (drawn from its verdict
  and the contradiction the round-table found), as `[[wikilinks]]` to the deep notes.
- **Skim / skip** — one line grouping the rest, so the reader knows what was considered
  and consciously set aside (no silent dropping).

Example knowledge network:

```
  [[Routing-MoE]] ──extends──► (Paper 1: cheap MoE routing)
        │ same-method
        ▼
  (Paper 3: router distillation) ──contradicts──► (Paper 2: dense > sparse)
```

Use Obsidian markdown, valid YAML frontmatter, `[[wikilinks]]` with aliases, and `--`
for missing data. Be concise: the synthesis should be readable in under a minute and make
the reader feel oriented, not buried.
