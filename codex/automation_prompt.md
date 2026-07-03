Run the daily PaperSignal pipeline for this repository.

From the repo root:

```bash
paper-signal run --config config/interests.yaml
```

If `paper-signal` is not on PATH, run `python3 -m paper_signal run --config
config/interests.yaml` instead (equivalent, no install needed); as a last resort,
`pip install -e .`. The vault resolves as `--vault` → `OBSIDIAN_VAULT_PATH` → the
config's `vault_path` — pass `--vault "<path>"` explicitly if neither is set.

After the run:

- Report how many papers were fetched and selected, and the daily note path.
- If the output says the existing note was kept, that is intentional (today's note was
  written by a richer AI report or by hand) — do not force-overwrite it.
- Mention any failures or missing configuration plainly.
- Do not overwrite manual notes outside PaperSignal output paths.
- Do not commit generated Obsidian notes or personal config.
