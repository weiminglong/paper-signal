# Daily Synthesis Prompt

After the per-paper round-tables finish, the Moderator writes the **top of the note** — the
part most people read first and often only. Optimize it for a busy human skimming their
morning digest, not for a reviewer.

Produce, in this order:

- **TL;DR banner** — a 1–2 line blockquote: how many papers, how many worth a real read,
  and today's thread in one plain sentence. Example:
  `> **3 papers on LLM agents & reliability.** 2 worth a deep read, 1 to skim.`
  `> **Today's thread:** papers that grade themselves — when the metric and the target are`
  `> the same thing, a "win" can be an illusion.`

- **At a glance** — a scannable table so the whole day fits on one screen:

  | # | Paper | Topic | Read? | The gist |
  |---|-------|-------|-------|----------|
  | 1 | QVal | Scoring agent steps | 📖 Deep read | <=18-word plain one-liner |
  | 2 | RLMF | Honest AI uncertainty | 📖 Deep read | … |
  | 3 | Table errors | LLM table reliability | 👀 Skim | … |

  Use short paper nicknames, everyday topic labels, and verdict icons
  (📖 deep-read · 👀 skim · 📥 queue · ⏭️ skip). The gist must be jargon-free.

- **Today's thread** — one short, plain paragraph naming the one or two ideas connecting
  today's papers. No acronyms without expansion.

- **The map** *(optional, collapsible)* — if a genuine structure connects the papers, put a
  compact ASCII knowledge network inside a `<details><summary>🗺️ How today's papers connect</summary>`
  block (nodes = short titles or `[[notes]]`, edges = extends/contradicts/applies/same-method).
  Connect only what genuinely connects; skip the map if it would be forced.

Use Obsidian markdown, valid YAML frontmatter, `[[wikilinks]]` with aliases, and `--` for
missing data. The whole top section should be readable in under a minute and leave the
reader knowing exactly what to open first.
