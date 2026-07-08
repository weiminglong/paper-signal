Run the daily PaperSignal pipeline for this repository.

From the repo root (this form always runs this checkout's code, no install needed):

```bash
python3 -m paper_signal run --config config/interests.yaml
```

If `python3` is unavailable, fall back to the console script:

```bash
paper-signal run --config config/interests.yaml
```

The vault resolves as `--vault` → `OBSIDIAN_VAULT_PATH` → the config's `vault_path` —
pass `--vault "<path>"` explicitly if neither is set.

When you report to the user:

- Use plain language. Call the two report styles the **quick list** (this automation)
  and the **full report** (the richer AI-written one). Do not repeat internal CLI terms
  such as "round-table", "deterministic", `--force`, or `unsee`; summarize instead of
  quoting raw output.
- Report how many papers were found and where the daily note is.
- If the output says the existing note was kept, that is intentional (today's note came
  from a full report or was hand-written) — say today's report already exists; do not
  force-overwrite it.
- Mention any failures or missing configuration plainly.
- Do not overwrite manual notes outside PaperSignal output paths, and do not commit
  generated notes or personal config.
