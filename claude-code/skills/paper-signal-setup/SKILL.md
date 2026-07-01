---
name: paper-signal-setup
description: Set up PaperSignal from scratch for a non-technical user, through conversation. Use when the user wants to install, set up, get started with, configure, or onboard to PaperSignal — e.g. "set up PaperSignal for me", "help me get started", "install this", "configure my paper reports". Not for generating a report on an already-set-up project (use the paper-signal skill for that).
---

# PaperSignal — Conversational Setup

Your job is to set up PaperSignal for someone who may have **no coding experience**. Do all
the technical work yourself; the user only answers plain-English questions. Be warm, brief,
and reassuring. Never ask them to write YAML, run commands, or understand the terminal.

## Principles

- **You do the work.** Run every command yourself; explain results in one plain sentence.
- **Confirm before anything that installs software, touches the network, or writes files
  outside the project** — say what you're about to do and why, in plain terms.
- **Ask one thing at a time.** Short questions, examples included.
- **Fail gently.** If a step can't complete (e.g. no admin rights to install Python), say so
  plainly and offer the alternative, don't dump errors.
- **Instant gratification first, depth second.** Get them a real report fast, then offer the
  deeper AI analysis.

## Flow

### 1. Welcome & orient
One or two sentences: "PaperSignal reads new research papers every day and writes you a plain
summary in Obsidian. I'll set it up — I'll ask you a few questions and handle the rest."

### 2. Prerequisites
Check quietly, fix with permission:
- `command -v paper-signal` — if missing, install with `pip install -e .` from the repo root
  (confirm first). If `pip`/Python is missing, check `python3 --version`; if absent, tell them
  plainly they need Python 3.9+ and offer to install it (macOS: Homebrew `brew install python`;
  otherwise point to python.org) — get consent before installing.
- Confirm they have **Obsidian** and know (roughly) where their vault folder is. If unsure,
  offer to look in common spots (`~/Documents`, `~/Obsidian`, iCloud) and confirm with them
  before using anything.

### 3. Interview their interests (plain English)
Ask what fields/topics they follow. Give examples: "e.g. AI agents, robotics, cancer biology,
climate models." Then ask for a few specific keywords they'd want to catch, and which matter
most. Keep it conversational — 2 to 4 topics is plenty. Do **not** show them arXiv codes.

### 4. Confirm the vault
Ask for (or confirm the detected) Obsidian vault path. Set it for this session:
`export OBSIDIAN_VAULT_PATH="<their path>"` and plan to record it so future runs find it.

### 5. Scaffold + write the config for them
- Run `paper-signal init --vault "$OBSIDIAN_VAULT_PATH"` to create `config/interests.yaml`
  and the vault folders.
- Then **edit `config/interests.yaml` yourself** to encode the interview: turn each topic into
  a `research_domains` entry with a plain-English name, the user's keywords, a `priority`
  (1–5, higher = they care more), and the matching `arxiv_categories` from the cheat-sheet
  below. Remove the placeholder domains that don't apply.

### 6. Validate
Run `paper-signal doctor`. If anything is ⚠/✗, fix it and re-run. Report "all good" in plain
terms.

### 7. First report (fast + free)
Run the deterministic scan so they see something immediately:
`paper-signal run --config config/interests.yaml --vault "$OBSIDIAN_VAULT_PATH"`
Then open/summarize the note it wrote and tell them where it is in Obsidian
(`10_Daily/<date>-paper-recommendations.md`).

### 8. Offer the deep version
Explain there's a richer mode where AI agents debate each top paper and write a more insightful
report — but note it uses more of their Claude usage. If they want it, run the **paper-signal**
skill (the round-table). Otherwise leave it for later.

### 9. Hand off
Tell them how to use it from now on, in one line: *"Whenever you want a fresh report, just tell
me 'run my paper report'."* Mention scheduling exists (a daily automatic run) and offer to set
it up later if they'd like. Do not set up cron/launchd unless they ask.

## arXiv category cheat-sheet (plain topic → code)

- AI / agents / LLMs → `cs.AI`, `cs.CL`
- Machine learning / deep learning → `cs.LG`, `stat.ML`
- NLP / language → `cs.CL`
- Computer vision / images → `cs.CV`
- Robotics → `cs.RO`
- Multi-agent systems → `cs.MA`, `cs.AI`
- Speech / audio / music → `cs.SD`, `eess.AS`
- Security / cryptography → `cs.CR`
- Human-computer interaction → `cs.HC`
- Information retrieval / search / recsys → `cs.IR`
- Software engineering → `cs.SE`
- Systems / distributed → `cs.DC`, `cs.OS`
- Biology → `q-bio` (e.g. `q-bio.NC` neuroscience, `q-bio.GN` genomics)
- Physics / math / economics → `physics.*`, `math.*`, `econ.*`

If a topic isn't listed, pick the closest `cs.*` code or ask the user to clarify the field.

## Config shape (you fill this in; the user never sees it)

```yaml
language: "en"
vault_path: "<their vault>"     # already written by init
daily:
  candidate_limit: 100
  recommendation_count: 10
  deep_analysis_count: 3        # how many papers get the AI round-table
  skip_seen: true
research_domains:
  "<Plain topic name>":
    priority: 5                 # 1–5, higher = they care more
    keywords: ["<their words>", "..."]
    arxiv_categories: ["cs.AI", "..."]
excluded_keywords: []           # add terms they want filtered out
```

## Rules

- Get consent before installing anything or touching files outside the project.
- Never expose YAML, commands, or errors as the user's problem to solve — you solve them.
- Don't commit their personal config, vault contents, or state to git.
