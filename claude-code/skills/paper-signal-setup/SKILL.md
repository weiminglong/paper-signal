---
name: paper-signal-setup
description: Set up PaperSignal from scratch for a non-technical user, through conversation. Use when the user wants to install, set up, get started with, configure, or onboard to PaperSignal — e.g. "set up PaperSignal for me", "help me get started", "install this", "configure my paper reports". Not for generating a report on an already-set-up project (use the paper-signal skill for that).
---

# PaperSignal — Conversational Setup

Set up PaperSignal for someone who may have **no coding experience**. You do all the
technical work; the user only answers plain-English questions. Be warm, brief, reassuring.

## User-facing vocabulary

The product has two report styles. To the user they are only ever **"quick list"** (fast,
plain, English-only) and **"full report"** (AI-written, richer, in their language). Never
say: deterministic, quick-scan, round-table, template, frontmatter, tag, seen-state,
`--force`, `unsee`, or any flag/command name. Never surface raw CLI output, YAML, or
errors — summarize outcomes in one plain sentence; you solve every problem yourself.

## Flow

### 1. Welcome & consent
One line: "PaperSignal reads new research papers every day and writes you a plain summary
in Obsidian. I'll set it up — a few questions, I handle the rest." Then one upfront
consent: "I'll need to install one small program and create a settings file in this
folder — okay?" Re-ask only for genuinely new scope (e.g. installing Python itself).

### 2. Prerequisites (fix everything for them)

**CLI.** Check `command -v paper-signal`. If missing, try in order, stopping at the first
that works: `pip install -e .` → `pip install --user -e .` (PEP 668) → venv
(`python3 -m venv .venv && . .venv/bin/activate && pip install -e .`) → just run
`python3 -m paper_signal <args>` everywhere (equivalent, no install). If `python3` is
missing, they need Python 3.9+ (macOS: `brew install python`; else python.org) — consent
first.

**Obsidian + a vault.** If they don't have Obsidian, point to https://obsidian.md (free).
If they have no vault or aren't sure where it is, offer to look in common spots
(`~/Documents`, `~/Obsidian`, iCloud) — or create one at a clear location like
`~/Documents/PaperSignal Vault` via `paper-signal init-vault --vault "<path>"`. Never
assume a vault exists. Read the chosen path back in plain English and sanity-check it
(reject a Windows `C:\...` path on a Mac).

### 3. Interview (plain English)
- Topics they follow (2–4 is plenty; examples: "AI agents, robotics, cancer biology").
- A few keywords per topic, and which topics matter most.
- Which language they want reports in.
- Quick list or full report as their daily default? (Full report = richer and in their
  language, but uses more Claude usage. If they chose a non-English language, mention the
  quick list is English-only.)

Do **not** show them arXiv codes. Keyword facts to apply silently: matching is exact
word-boundary with no stemming (list plurals and hyphen/space variants: "manuscripts",
"gravitational-wave"); prefer field-qualified phrases over generic terms ("galaxy
classification", not "machine learning" — generic keywords pull junk from all of arXiv).

### 4. Scaffold + write the config
- From the repo root: `paper-signal init --vault "<their vault>"` (pass `--vault`
  explicitly — env exports don't persist across the fresh shell each command runs in).
- Then edit `config/interests.yaml` yourself: one `research_domains` entry per topic
  (plain name, their keywords, `priority` 1–5), with `arxiv_categories` mapped via
  `references/arxiv-categories.md` (read it now). Set `language:` and
  `daily.report_mode:` (`full` or `quick`) from the interview. Remove placeholder domains.
- If the vault lives inside the repo, add its path to `.gitignore` (better: keep it
  outside).

Config shape (`sources.arxiv.categories` is optional — it defaults to the union of the
domains' categories):

```yaml
language: "en"
vault_path: "<their vault>"     # written by init
daily:
  report_mode: "full"           # their day-2 default: full | quick
  candidate_limit: 100
  recommendation_count: 10
  deep_analysis_count: 3        # papers that get the full AI treatment
  skip_seen: true
research_domains:
  "<Plain topic name>":
    priority: 5
    keywords: ["<their words>", "..."]
    arxiv_categories: ["cs.AI", "..."]
excluded_keywords: []
```

### 5. Validate
`paper-signal doctor`. Fix any ✗/⚠ config or vault items and re-run. An arXiv warning is
environmental (network/rate-limit) — reassure and move on. Report "all set" plainly.

### 6. First report — tune in preview mode
Tune with `paper-signal run --vault "<vault>" --no-mark-seen` (preview: papers stay
eligible between iterations; a normal run would hide everything it shows — recover with
`paper-signal unsee --last-run` if that happened). Summarize the note plainly and tell
them where to find it ("in Obsidian, in the 10_Daily folder — today's date"). Then tune:

- Few papers / niche field → raise `daily.candidate_limit` to ~300 first (it's split
  across categories; keyword search also reaches outside them).
- 0 papers → broaden keywords, add plural/variant forms.
- Off-topic picks → tighten phrases or add `excluded_keywords`. (Server-side keyword
  search uses only the top ~10 keywords by domain priority — must-hits go in
  high-priority domains.)
- "Too academic / dry" → that's abstracts; the fix is the full report, not keyword
  surgery. Use `excluded_keywords` sparingly (hard drop: "survey" also kills surveys
  they'd want).

Iterate until genuinely useful — never leave them with an empty or noisy first note.

### 7. Finalize per their chosen mode
- **Full report**: run the **paper-signal** skill now. Preview tuning left today's papers
  eligible, so it gets the full candidate pool; its commit step records them as seen.
- **Quick list**: one normal run (no `--no-mark-seen`) so today's papers are recorded.

Never do a normal quick run and *then* offer the full report the same day — it would only
see leftovers.

### 8. Hand off
One line: *"Whenever you want a fresh report, just tell me 'run my paper report'."* Give
them the mental model: *"You won't be shown the same paper twice — ask me 'what did you
find this week?' anytime, and I can bring papers back if you ever want a redo."* (Those
map to `paper-signal history --days 7` and `paper-signal unsee`, which you run for them.)
Offer scheduling later if they ask; if their reports are non-English, note the automatic
daily version can only write the English quick list (it will never replace a same-day
full report — that's protected).

## Rules

- One upfront consent (step 1); re-ask only for new scope. Never install or write outside
  the project without it.
- Run commands from the repo root; pass `--vault` explicitly.
- Everything in "User-facing vocabulary" above: plain names, no jargon, no raw output, no
  tracebacks — you solve errors, silently trying the next fallback.
- Don't commit their personal config, vault contents, or reading state to git.
