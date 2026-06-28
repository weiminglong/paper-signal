# PaperSignal

Run the local PaperSignal daily research workflow.

```bash
paper-signal run --config config/interests.yaml --vault "$OBSIDIAN_VAULT_PATH"
```

After the command completes, summarize:

- fetched paper count
- selected paper count
- daily note path
- failures or missing configuration

Do not edit generated Obsidian notes unless the user asks.
