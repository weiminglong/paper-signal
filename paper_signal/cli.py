from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from paper_signal import __version__
from paper_signal.obsidian.writer import init_vault
from paper_signal.pipeline import commit_seen, fetch_candidates, fetch_payload, run_pipeline


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        result = run_pipeline(
            config_path=args.config,
            vault_path=args.vault,
            dry_run=args.dry_run,
        )
        action = "Would write" if args.dry_run else "Wrote"
        print(f"Fetched papers: {result.fetched_count}")
        print(f"Selected papers: {result.selected_count}")
        print(f"{action}: {result.daily_note_path}")
        return

    if args.command == "fetch":
        result = fetch_candidates(config_path=args.config, vault_path=args.vault)
        payload = fetch_payload(result)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return

    if args.command == "commit":
        vault = args.vault or os.environ.get("OBSIDIAN_VAULT_PATH")
        if not vault:
            raise SystemExit("Vault path is required via --vault or OBSIDIAN_VAULT_PATH")
        ids = _collect_ids(args.ids, args.from_fetch)
        if not ids:
            raise SystemExit("No paper ids to commit (use --ids or --from-fetch)")
        total = commit_seen(Path(vault), ids)
        print(f"Marked {len(ids)} paper(s) as seen; {total} total in state")
        return

    if args.command == "init-vault":
        vault = args.vault or os.environ.get("OBSIDIAN_VAULT_PATH")
        if not vault:
            raise SystemExit("Vault path is required via --vault or OBSIDIAN_VAULT_PATH")
        init_vault(Path(vault))
        print(f"Initialized vault folders under: {vault}")
        return

    parser.print_help()


def _collect_ids(ids_arg: str | None, from_fetch: str | None) -> list[str]:
    ids: list[str] = []
    if ids_arg:
        ids.extend(token.strip() for token in ids_arg.split(",") if token.strip())
    if from_fetch:
        raw = sys.stdin.read() if from_fetch == "-" else Path(from_fetch).read_text(encoding="utf-8")
        payload = json.loads(raw)
        ids.extend(
            paper["paper_id"]
            for paper in payload.get("papers", [])
            if paper.get("paper_id")
        )
    # Deduplicate while preserving order.
    seen: set[str] = set()
    unique: list[str] = []
    for paper_id in ids:
        if paper_id not in seen:
            seen.add(paper_id)
            unique.append(paper_id)
    return unique


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="paper-signal")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command")

    run = subparsers.add_parser("run", help="Fetch, score, discuss, and write daily note")
    run.add_argument(
        "--config",
        default=os.environ.get("PAPER_SIGNAL_CONFIG", "config/interests.yaml"),
        help="Path to interests YAML config",
    )
    run.add_argument(
        "--vault",
        default=os.environ.get("OBSIDIAN_VAULT_PATH"),
        help="Path to Obsidian vault",
    )
    run.add_argument("--dry-run", action="store_true", help="Render without writing state or notes")

    fetch = subparsers.add_parser(
        "fetch",
        help="Fetch and score candidates, emit JSON for an agent to analyze (does not write)",
    )
    fetch.add_argument(
        "--config",
        default=os.environ.get("PAPER_SIGNAL_CONFIG", "config/interests.yaml"),
        help="Path to interests YAML config",
    )
    fetch.add_argument(
        "--vault",
        default=os.environ.get("OBSIDIAN_VAULT_PATH"),
        help="Path to Obsidian vault",
    )

    commit = subparsers.add_parser(
        "commit",
        help="Mark papers as seen after an agent has written the note",
    )
    commit.add_argument(
        "--vault",
        default=os.environ.get("OBSIDIAN_VAULT_PATH"),
        help="Path to Obsidian vault",
    )
    commit.add_argument("--ids", help="Comma-separated paper ids to mark seen")
    commit.add_argument(
        "--from-fetch",
        help="Path to a saved 'fetch' JSON (or '-' for stdin); marks every paper in it seen",
    )

    init = subparsers.add_parser("init-vault", help="Create required Obsidian directories")
    init.add_argument("--vault", default=os.environ.get("OBSIDIAN_VAULT_PATH"))

    return parser
