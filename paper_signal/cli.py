from __future__ import annotations

import argparse
import os
from pathlib import Path

from paper_signal import __version__
from paper_signal.obsidian.writer import init_vault
from paper_signal.pipeline import run_pipeline


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

    if args.command == "init-vault":
        vault = args.vault or os.environ.get("OBSIDIAN_VAULT_PATH")
        if not vault:
            raise SystemExit("Vault path is required via --vault or OBSIDIAN_VAULT_PATH")
        init_vault(Path(vault))
        print(f"Initialized vault folders under: {vault}")
        return

    parser.print_help()


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

    init = subparsers.add_parser("init-vault", help="Create required Obsidian directories")
    init.add_argument("--vault", default=os.environ.get("OBSIDIAN_VAULT_PATH"))

    return parser
