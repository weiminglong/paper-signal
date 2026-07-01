---
name: paper-signal
description: Generate a daily research read by fetching arXiv papers and running a multi-agent round-table (Moderator + persona subagents) that analyzes each top paper and authors an Obsidian daily note. Use when the user asks for a daily paper read, paper-signal report, or research-vault update.
---

# PaperSignal — Round-Table Daily Read

You are the **Moderator** of a research round-table. Each day you fetch candidate papers,
convene a panel of **persona subagents** to argue over the most important ones, synthesize
their debate, and write a structured daily note into the user's Obsidian vault.

The Python CLI does the deterministic part (fetch + score + select). **You** are the LLM
brain that does the analysis and writing — using your own session and subagents, with **no
separate API key**.

## Modes

- **Round-table (default)** — this document. Deep multi-agent analysis, you author the note.
- **Quick scan** — `paper-signal run --config config/interests.yaml --vault "$OBSIDIAN_VAULT_PATH"`.
  Deterministic, no agents, instant. Use when the user wants a fast list, not analysis.

## Requirements

- `config/interests.yaml` exists; `OBSIDIAN_VAULT_PATH` is set.
- The `paper-signal` CLI is installed. If `paper-signal` is missing, run `pip install -e .` first.

```bash
test -f config/interests.yaml || echo "MISSING config/interests.yaml (copy config/interests.example.yaml)"
test -n "$OBSIDIAN_VAULT_PATH" || echo "MISSING OBSIDIAN_VAULT_PATH"
command -v paper-signal >/dev/null || pip install -e .
```

## Reference prompts

Read these before orchestrating; they define the framework you are executing:

- `prompts/roundtable.md` — the Moderator's framework, persona roster, round protocol, ASCII chart, verdict + output contract.
- `prompts/representative.md` — the template you fill to spawn each persona subagent.
- `prompts/deep_analysis.md` — the per-paper deep note written for `deep-read` verdicts.
- `prompts/daily_synthesis.md` — the cross-paper briefing + knowledge network at the top of the daily note.

## Workflow

### 1. Fetch candidates

```bash
paper-signal fetch --config config/interests.yaml --vault "$OBSIDIAN_VAULT_PATH" > /tmp/paper-signal-candidates.json
```

Parse the JSON. Key fields: `papers[]` (each with `rank`, `deep`, `title`, `abstract`,
`authors`, `categories`, `score`, `matched_domains`, `matched_keywords`, `arxiv_url`,
`pdf_url`, `paper_id`), `daily_note_path`, `papers_dir`, `domains`, `deep_analysis_count`,
`run_date`. The CLI has already created the vault folders and filtered out previously seen
papers; it did **not** write anything.

If `papers` is empty: write a short daily note at `daily_note_path` saying no new matching
papers were found today, then stop (nothing to commit).

### 2. Round-table each deep paper

For every paper with `"deep": true` (the top `deep_analysis_count`), run the protocol in
`prompts/roundtable.md`. You are the Moderator:

1. **Convene** — pick 4 personas from the roster best suited to the paper (always include
   The Skeptic and The Empiricist). Frame the opening question around the paper's claim.
2. **Round 1 (opening)** — spawn the 4 persona subagents **in parallel** (one message,
   four `Task` calls, `subagent_type: general-purpose`). Fill `prompts/representative.md`
   for each with the persona + paper + `round_label: "Opening statement"`. Collect their
   statements.
3. **Synthesis 1** — name the core contradiction, draw the ASCII framework chart, pose the
   deeper question.
4. **Round 2 (rebuttal)** — spawn the same 4 personas again in parallel, this time passing
   the other three's Round-1 statements + the core contradiction (`round_label: "Rebuttal"`,
   `rebuttal: true`). Collect rebuttals.
5. **Verdict** — resolve or honestly leave open the contradiction; assign verdict
   (`deep-read` / `skim` / `queue` / `skip`), confidence, one-line rationale, and 2–5
   `[[wikilink]]` knowledge-network targets.

Run the deep papers' round-tables **concurrently** where possible (batch the subagent
calls) to keep the whole job fast.

For each `deep-read` verdict, also write a standalone note at
`<papers_dir>/<paper_id>.md` following `prompts/deep_analysis.md`, and link it from the
daily note with `[[<paper_id>|<short title>]]`.

### 3. Triage the rest

For papers with `"deep": false`, do a lightweight pass (no full panel) — either inline as
Moderator or one quick `Task` per paper — producing a single line each: title, score,
matched domains, and a one-word verdict (`skim` / `queue` / `skip`) with a half-sentence
why. Ground it in the abstract; do not fabricate.

### 4. Synthesize the day

Write the cross-paper briefing per `prompts/daily_synthesis.md`: today's signal, an ASCII
knowledge network, top-3 to read first (with why, as wikilinks to the deep notes), and a
skim/skip group.

### 5. Write the daily note

Author the file at `daily_note_path` yourself (Write tool). Optimize for a human skimming
at breakfast: plain-English cards up top, the dense debate collapsed. Structure:

```markdown
---
date: "<run_date>"
tags: ["daily-paper-read", "paper-signal", "claude-roundtable"]
paper_count: <selected_count>
deep_count: <deep_analysis_count>
---

# Daily Paper Read — <run_date>

> **<TL;DR banner: N papers on <theme>. X deep reads, Y to skim.>**
> **Today's thread:** <one plain sentence>

## At a glance
<the scannable table from daily_synthesis.md — nickname, topic, verdict icon, plain gist>

## The papers
<one plain-English card per paper, per the roundtable.md output contract: Topic / In plain
terms / Why it matters / The catch / Verdict, with the round-table debate inside a
<details> block. Deep papers get the full debate; triaged papers get just the card (no
<details>). Order by verdict: deep-read first.>

## Reading queue
- [ ] <title> — [[<paper_id>|short title]]   (deep-read verdicts first)
```

Readability is the point: no unexplained acronyms in the cards, verdict icons
(📖 deep-read · 👀 skim · 📥 queue · ⏭️ skip), and the ASCII charts / round-by-round debate
live inside `<details>` so the note reads clean but the depth is one click away. Obsidian
conventions (see `AGENTS.md`): valid YAML frontmatter, wikilinks with aliases, `--` for
missing data (not `---` inside the body), accurate tags. `<details>`/`<summary>` render in
Obsidian's reading view — leave a blank line after `<summary>` and before `</details>`.

### 6. Commit & report

After the note is written, mark the selected papers seen so they are not re-recommended:

```bash
paper-signal commit --vault "$OBSIDIAN_VAULT_PATH" --from-fetch /tmp/paper-signal-candidates.json
```

Then report: fetched / selected / deep counts, the daily note path, the per-paper notes
created, and any failures.

## Cost & scaling

The default is deep: `deep_analysis_count` papers × 4 personas × 2 rounds of subagents.
To tune:

- Lower `daily.deep_analysis_count` in the config to analyze fewer papers deeply.
- Drop Round 2 (opening statements only) for a cheaper pass.
- Use 3 personas instead of 4 for narrow papers.

State the panel size, rounds, and number of deep papers you used so the cost is visible.

## Rules

- You are the analyst — do not fall back to `paper-signal run` unless the user asks for the
  quick deterministic scan.
- Ground every claim in title/abstract/metadata. Never invent experimental results,
  numbers, or datasets. Mark inference as inference.
- When assembling the note, strip any stray persona preamble ("as the Skeptic…", "no
  tools needed") so each statement opens on its substance.
- Do not overwrite manual notes; only write under `10_Daily/` and `20_Research/Papers/`.
- Do not commit personal config, state, API keys, or vault files to git.
