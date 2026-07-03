---
name: paper-signal
description: Generate a daily research read by fetching arXiv papers and running a multi-agent round-table (Moderator + persona subagents) that analyzes each top paper and authors an Obsidian daily note. Use when the user asks for a daily paper read, paper-signal report, or research-vault update.
---

# PaperSignal — Daily Report

You produce the user's daily paper report. The Python CLI does the deterministic part
(fetch + score + select); **you** are the analysis and writing — your own session and
subagents, no separate API key.

## Which mode to run

Read `daily.report_mode` from `config/interests.yaml` (also echoed in the fetch payload):

- **`full`** (the user's "full report") — the round-table below. Default when unset.
- **`quick`** (the user's "quick list") — just run
  `paper-signal run --vault "<vault>"` and summarize the result plainly.

An explicit request overrides the config ("give me the deep report" / "just a quick
list"). To the user these are only ever "full report" and "quick list" — never say
deterministic, round-table, template, frontmatter, tag, `--force`, or `unsee` to them,
and never echo raw CLI output; summarize outcomes in plain sentences (e.g. "I read 27
papers; 2 are worth your time — the report is in today's daily note"), not
"fetched/selected counts".

## Requirements

- `config/interests.yaml` exists (else run the **paper-signal-setup** skill first).
- Every command resolves the vault the same way: `--vault` → `OBSIDIAN_VAULT_PATH` →
  `vault_path` in the config. Passing `--vault` explicitly is still safest.
- The CLI runs as `paper-signal` or `python3 -m paper_signal` (equivalent, no install
  needed). Run from the repo root.

## Reference prompts

- `prompts/roundtable.md` — the whole framework: personas, 2-round protocol, ASCII chart,
  per-paper output contract, daily synthesis, deep-note spec, and the language rule.
- `prompts/representative.md` — the template you fill to spawn each persona subagent.

## Workflow (full report)

### 1. Fetch candidates

```bash
paper-signal fetch --vault "<vault>" > /tmp/paper-signal-candidates.json
```

Parse the JSON: `papers[]` (each with `rank`, `deep`, `title`, `abstract`, `authors`,
`categories`, `score`, `matched_domains`, `matched_keywords`, `arxiv_url`, `pdf_url`,
`paper_id`), plus `daily_note_path`, `papers_dir`, `domains`, `deep_analysis_count`,
`run_date`, `language`, `report_mode`. Fetch creates vault folders and filters
previously-seen papers; it writes **nothing**.

Write all prose in the payload's `language` per the rule in `prompts/roundtable.md`.

- `papers` empty → if a non-empty note exists at `daily_note_path`, leave it and say so;
  else write a short "no new matching papers today" note. Stop (nothing to commit).
- Non-empty note already at `daily_note_path` (quick list ran earlier) → fold its papers
  in or confirm before replacing. The reverse is enforced in code: a later `run` refuses
  to replace your note (author with `claude-roundtable` in the frontmatter tags, never
  `deterministic-scan`).

### 2. Round-table each `deep: true` paper

Follow the protocol in `prompts/roundtable.md`. Claude-Code mechanics:

- Pick 4 personas from the roster (always The Skeptic + The Empiricist).
- Round 1: spawn the 4 persona subagents **in parallel** — one message, four `Task`
  calls (`subagent_type: general-purpose`), each filled from
  `prompts/representative.md` with `round_label: "Opening statement"`.
- Synthesize (core contradiction + ASCII chart), then Round 2 in parallel with
  `round_label: "Rebuttal"` and the other three's statements.
- Verdict per the contract. Run multiple papers' round-tables concurrently.

For each `deep-read` verdict, write the per-paper note at `<papers_dir>/<paper_id>.md`
per roundtable.md's "Deep note" section, linked as `[[<paper_id>|short title]]`.

### 3. Triage `deep: false` papers
One line each (inline or one quick Task per paper): title, plain gist, one-word verdict
(`skim`/`queue`/`skip`) + half-sentence why. Ground in the abstract; never fabricate.

### 4. Author the daily note

Write `daily_note_path` yourself, per roundtable.md's output contract and daily-synthesis
section:

```markdown
---
date: "<run_date>"
tags: ["daily-paper-read", "paper-signal", "claude-roundtable"]
paper_count: <n>
deep_count: <deep_analysis_count>
---

# Daily Paper Read — <run_date>

> <TL;DR banner + today's thread>

## At a glance
<table: # | Paper | Topic | Read? | The gist>

## The papers
<plain-English card per paper; deep papers get the collapsed <details> debate>

## Reading queue
- [ ] <title> — [[<paper_id>|short title]]   (deep-read first)
```

Obsidian conventions: `AGENTS.md`. Leave a blank line after `<summary>` and before
`</details>` so Obsidian renders the collapsibles.

### 5. Commit & report

```bash
paper-signal commit --vault "<vault>" --from-fetch /tmp/paper-signal-candidates.json
```

Then tell the user, plainly: how many papers you read, which 1–3 matter most and why,
and where the note is. Mention any failures honestly.

## Cost & scaling

Default depth: `deep_analysis_count` papers × 4 personas × 2 rounds. To cheapen: lower
`daily.deep_analysis_count`, drop Round 2, or use 3 personas. Tell the user how much
analysis ran in plain terms ("I had the AI panel debate the top 3 papers in depth") —
not in personas/rounds vocabulary.

## Rules

- Ground every claim in title/abstract/metadata; never invent results; mark inference.
- Strip stray persona preambles when assembling the note.
- Only write under `10_Daily/` and `20_Research/Papers/`; never touch manual notes.
- Don't commit personal config, state, or vault files to git.
