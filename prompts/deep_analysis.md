# Deep Analysis Prompt (per-paper note)

When the round-table verdict is **deep-read**, the Moderator compiles a standalone paper
note in the vault under `20_Research/Papers/<paper_id>.md`, linked from the daily note by
a `[[wikilink]]`. This is the durable artifact; the daily note is the digest.

Write it from the round-table discussion plus the paper's title, abstract, and metadata.

## Frontmatter

```yaml
---
title: "<paper title>"
arxiv_id: "<paper_id>"
arxiv_url: "<url>"
authors: ["…"]
categories: ["…"]
published: "<YYYY-MM-DD>"
tags: ["paper", "paper-signal", "claude-roundtable"]
verdict: "deep-read"
date_analyzed: "<YYYY-MM-DD>"
---
```

## Body

- **Core problem** — what gap or question the paper targets.
- **Main method** — the central mechanism, in your own words.
- **Evidence** — what the abstract claims as support. **Do not invent experimental
  results**; if the abstract is vague, write "evidence not detailed in abstract — verify
  in the PDF."
- **Novelty** — what is genuinely new vs. prior work, per the round-table.
- **Limitations / open questions** — the Skeptic's and Empiricist's strongest points.
- **Connections** — `[[wikilinks]]` to related notes/threads in the vault (the
  Connector's output); name concrete tags or notes to create if none exist yet.
- **Practical implications** — the Practitioner's read: cost, applicability, who benefits.
- **Reading recommendation** — what to read first in the PDF and what to verify.
- **Round-table transcript** *(optional)* — the full verbatim persona statements and
  rebuttals, if you want them preserved. The daily note only keeps the distilled version,
  so this note is where the raw debate lives.

Use Obsidian markdown, valid YAML frontmatter, wikilinks with aliases
(`[[note-name|Alias]]`), and `--` for genuinely missing data (never `---` inside the body).
Write the prose in the configured report language; keep the title, authors, and wikilinks
in their original form. Cite paper sections only when you actually know them; otherwise
say where to look.
