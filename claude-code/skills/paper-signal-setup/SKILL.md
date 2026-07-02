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
- **Fail gently.** If a step can't complete, say so plainly and try the next fallback — never
  show the user a traceback or an error to solve.
- **Instant gratification first, depth second.** Get them a real report fast, then offer the
  deeper AI analysis.

## Flow

### 1. Welcome & orient
One or two sentences: "PaperSignal reads new research papers every day and writes you a plain
summary in Obsidian. I'll set it up — I'll ask you a few questions and handle the rest."

### 2. Prerequisites (fix everything for them, with consent)

**PaperSignal CLI.** Check `command -v paper-signal`. If it's missing, install it — try these in
order, stop at the first that works, and translate any error into one plain sentence (never show
a traceback):
1. `pip install -e .` from the repo root.
2. `pip install --user -e .` (if the system Python is "externally managed" / PEP 668).
3. a virtualenv: `python3 -m venv .venv && . .venv/bin/activate && pip install -e .`.
4. zero-install with uv/pipx (see the README), or simply run the CLI as
   `python3 -m paper_signal <args>` everywhere — it's equivalent and needs no install.

If `python3` itself is missing, tell them plainly they need Python 3.9+ and offer to install it
(macOS: `brew install python`; otherwise point to python.org) — get consent first.

**Obsidian + a vault.** Confirm they use Obsidian and roughly where their vault folder is.
- If they're unsure where it is, offer to look in common spots (`~/Documents`, `~/Obsidian`,
  iCloud) and confirm before using anything.
- **If they don't have Obsidian**, point them to https://obsidian.md to install it (it's free).
- **If they have no vault yet, or aren't sure, offer to create one for them.** Pick a clear
  location like `~/Documents/PaperSignal Vault`, confirm it in plain English, and create it with
  `paper-signal init-vault --vault "<that path>"`. Never assume a vault already exists.

### 3. Interview their interests (plain English)
Ask what fields/topics they follow. Give examples: "e.g. AI agents, robotics, cancer biology,
climate models." Then ask for a few specific keywords they'd want to catch, and which matter
most. Keep it conversational — 2 to 4 topics is plenty. Do **not** show them arXiv codes.

### 4. Confirm the vault
Read the path back in plain English ("I'll save your notes in *<folder>* — sound right?"). Sanity-
check it: reject an obviously wrong path (e.g. a Windows `C:\...` path on a Mac) and ask again.
Pass the path explicitly with `--vault "<path>"` on each command, or let `init` write it into the
config (next step) — do **not** rely on `export OBSIDIAN_VAULT_PATH`, because each command you run
is a fresh shell and the export won't carry over.

### 5. Scaffold + write the config for them
- Run `paper-signal init --vault "<their vault>"` from the repo root (or pass an absolute
  `--config`, since it defaults to a path relative to the current folder). This writes
  `config/interests.yaml` with the vault baked in and scaffolds the vault folders.
- Then **edit `config/interests.yaml` yourself** to encode the interview: turn each topic into a
  `research_domains` entry with a plain-English name, the user's keywords, a `priority` (1–5,
  higher = they care more), and the matching `arxiv_categories` from the cheat-sheet below. Remove
  the placeholder domains that don't apply.
- If the vault lives *inside* the repo folder, add its path to `.gitignore` so their notes and
  reading state are never committed (better still: keep the vault outside the repo).

### 6. Validate
Run `paper-signal doctor`. Fix any ✗/⚠ config or vault items and re-run. An arXiv **warning** is
environmental (network/rate-limit) — reassure and move on, don't loop trying to "fix" it. Report
"all set" in plain terms.

### 7. First report (fast + free)
Run the deterministic scan so they see something immediately:
`paper-signal run --config config/interests.yaml --vault "<their vault>"`
Summarize the note in plain English and tell them where it is in Obsidian
(`10_Daily/<date>-paper-recommendations.md`). Then react to what you actually got:
- **0 papers selected** → keywords are too narrow; add broader synonyms and re-run.
- **Off-topic picks** (a broad word like "evaluation" or "model" pulled in noise) → tighten the
  phrase or add an `excluded_keywords` entry, and re-run.
Don't leave them with an empty or noisy first note.

### 8. Offer the deep version
Explain there's a richer mode where AI agents debate each top paper and write a more insightful
report — but note it uses more of their Claude usage. If they want it, run the **paper-signal**
skill (the round-table). Otherwise leave it for later.

### 9. Hand off
Tell them how to use it from now on, in one line: *"Whenever you want a fresh report, just tell
me 'run my paper report'."* Mention scheduling exists (a daily automatic run) and offer to set it
up later if they'd like. Do not set up cron/launchd unless they ask.

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
- Biology → `q-bio.*`: neuroscience `q-bio.NC`, genomics & gene editing `q-bio.GN`, proteins &
  molecular structure (AlphaFold-style) `q-bio.BM`, quantitative methods `q-bio.QM`, molecular
  networks `q-bio.MN`, cell behavior `q-bio.CB`
- Economics / econometrics → `econ.EM` (econometrics), `econ.TH` (theory), `econ.GN` (general);
  causal inference often lives in `stat.ME`
- Finance / quant / markets → `q-fin.*`: trading & microstructure `q-fin.TR`, mathematical
  finance `q-fin.MF`, portfolio `q-fin.PM`, risk `q-fin.RM`, computational `q-fin.CP`
- Game theory / mechanism design / auctions → `cs.GT`, `econ.TH`
- Statistics / causal inference → `stat.ME` (methodology), `stat.AP` (applied), `stat.ML`
- Climate / earth science → `physics.ao-ph` (atmospheric & oceanic), `physics.geo-ph`
  (geophysics); attribution/impact methods often `stat.AP`
- Other physics / math → `physics.*`, `math.*`

If a topic isn't listed, pick the closest code or ask the user to clarify the field. For a
cross-cutting theme with no home category (e.g. "evaluation", "benchmarks"), model it as
**keywords** across the relevant categories rather than a category of its own. Papers are often
cross-posted, so listing 2–3 categories per domain (not one) catches more of the real work —
e.g. market microstructure lives under `q-fin.TR` far more than `econ.*`.

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

`sources.arxiv.categories` is optional — if you omit it, PaperSignal fetches the union of every
domain's `arxiv_categories`. Set it only to narrow the first run for speed.

## Rules

- Get consent before installing anything or touching files outside the project.
- Never expose YAML, commands, or errors as the user's problem to solve — you solve them.
- **Never surface raw CLI output.** `init`/`doctor`/`run` print developer-facing lines (config
  paths, "Next steps", `--dry-run` hints). Summarize the *outcome* in one plain sentence; never
  tell the user to edit a file or run a command themselves.
- Run commands from the repo root (or pass an absolute `--config`), and pass `--vault` explicitly
  rather than relying on an exported env var (each command is a fresh shell).
- Don't commit their personal config, vault contents, or reading state to git.
