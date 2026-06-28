Run the daily PaperSignal pipeline for this repository.

Use:

```bash
paper-signal run --config config/interests.yaml --vault "$OBSIDIAN_VAULT_PATH"
```

If the editable install is missing, run:

```bash
pip install -e .
```

After the run:

- report how many papers were fetched and selected
- report the generated daily note path
- mention any failures or missing configuration
- do not overwrite manual notes outside PaperSignal output paths
- do not commit generated Obsidian notes unless explicitly asked
