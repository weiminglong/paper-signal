# Agent Instructions

This repository is a local-first paper reading pipeline. Keep implementation changes CLI-first and scheduler-agnostic.

## Development

- Use `paper_signal` as the Python package.
- Keep scheduler integrations as thin wrappers around `paper-signal run`.
- Do not commit personal configs, API keys, runtime state, or Obsidian vault contents.
- Prefer deterministic behavior and JSON-friendly intermediate data.
- Preserve Obsidian-compatible markdown:
  - Use wikilinks with aliases when linking generated paper notes.
  - Use `--` for missing data, not `---`.
  - Keep frontmatter valid YAML.

## Verification

Run:

```bash
python3 -m pytest
python3 -m ruff check .
```
