from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
from pathlib import Path

from paper_signal import __version__
from paper_signal.config import ConfigError
from paper_signal.obsidian.writer import init_vault
from paper_signal.onboarding import doctor, init_project
from paper_signal.pipeline import (
    commit_seen,
    fetch_candidates,
    fetch_payload,
    recent_history,
    run_pipeline,
    unsee,
)

_STATUS_ICON = {"ok": "✓", "warn": "⚠", "fail": "✗"}


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        _dispatch(args, parser)
    except ConfigError as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        print(
            "Run `paper-signal init` to create a starter config, or pass --config <path>.",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc
    except urllib.error.URLError as exc:
        # arXiv unreachable or rate-limiting (HTTP 429/503).
        print(f"Network error: {exc}", file=sys.stderr)
        print(
            "If arXiv is rate-limiting (HTTP 429), wait a few minutes and try again; "
            "`paper-signal doctor` checks reachability.",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc
    except OSError as exc:
        print(f"File or system error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


def _dispatch(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if args.command == "run":
        result = run_pipeline(
            config_path=args.config,
            vault_path=args.vault,
            dry_run=args.dry_run,
            mark_seen=not args.no_mark_seen,
        )
        print(f"Fetched papers: {result.fetched_count}")
        print(f"Selected papers: {result.selected_count}")
        if result.kept_existing:
            print(
                f"Kept existing note (this run matched 0 new papers): {result.daily_note_path}"
            )
            if args.no_mark_seen:
                print("Tip: preview runs don't hide papers — 0 matches means the config found nothing new.")
            else:
                print("Tip: papers already shown are skipped; `paper-signal unsee --last-run` re-allows them.")
        else:
            action = "Would write" if args.dry_run else "Wrote"
            print(f"{action}: {result.daily_note_path}")
        if args.no_mark_seen:
            print("(preview mode: papers were NOT marked seen; re-runs will show them again)")
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
        ids, entries = _collect_ids(args.ids, args.from_fetch)
        if not ids:
            raise SystemExit("No paper ids to commit (use --ids or --from-fetch)")
        total = commit_seen(Path(vault), ids, entries=entries)
        print(f"Marked {len(ids)} paper(s) as seen; {total} total in state")
        return

    if args.command == "unsee":
        vault = args.vault or os.environ.get("OBSIDIAN_VAULT_PATH")
        if not vault:
            raise SystemExit("Vault path is required via --vault or OBSIDIAN_VAULT_PATH")
        if not (args.all or args.last_run or args.ids):
            raise SystemExit("Nothing to unsee (use --last-run, --all, or --ids)")
        ids = [t.strip() for t in (args.ids or "").split(",") if t.strip()]
        removed = unsee(Path(vault), ids=ids, last_run=args.last_run, everything=args.all)
        print(f"Forgot {removed} paper(s); they can be recommended again")
        return

    if args.command == "history":
        vault = args.vault or os.environ.get("OBSIDIAN_VAULT_PATH")
        if not vault:
            raise SystemExit("Vault path is required via --vault or OBSIDIAN_VAULT_PATH")
        entries = recent_history(Path(vault), days=args.days)
        if not entries:
            print(f"No papers recorded in the last {args.days} day(s).")
            return
        current_date = None
        for entry in entries:
            if entry.get("date") != current_date:
                current_date = entry.get("date")
                print(f"\n{current_date}")
            score = entry.get("score", "--")
            print(f"  [{score}] {entry.get('title', entry.get('paper_id', '?'))}")
        return

    if args.command == "init":
        vault = args.vault or os.environ.get("OBSIDIAN_VAULT_PATH")
        result = init_project(config_path=args.config, vault=vault, force=args.force)
        for note in result.notes:
            print(note)
        steps = [f"Edit your research domains/keywords in {result.config_path}"]
        if not vault:
            steps.append('Set your vault: export OBSIDIAN_VAULT_PATH="/path/to/vault"')
        steps.append("Verify setup:   the `doctor` command")
        steps.append("First run:      the `run` command   (writes today's note)")
        print("\nNext steps:")
        for number, step in enumerate(steps, start=1):
            print(f"  {number}. {step}")
        return

    if args.command == "doctor":
        vault = args.vault or os.environ.get("OBSIDIAN_VAULT_PATH")
        all_ok, checks = doctor(config_path=args.config, vault=vault, offline=args.offline)
        for check in checks:
            icon = _STATUS_ICON.get(check.status, "?")
            print(f"{icon} {check.name}: {check.detail}")
            if check.fix and check.status != "ok":
                print(f"    → {check.fix}")
        if not all_ok:
            print("\nSome checks failed — see fixes above.")
            raise SystemExit(1)
        has_warnings = any(check.status == "warn" for check in checks)
        print("\nAll good (with warnings)." if has_warnings else "\nAll good.")
        return

    if args.command == "init-vault":
        vault = args.vault or os.environ.get("OBSIDIAN_VAULT_PATH")
        if not vault:
            raise SystemExit("Vault path is required via --vault or OBSIDIAN_VAULT_PATH")
        init_vault(Path(vault))
        print(f"Initialized vault folders under: {vault}")
        return

    parser.print_help()


def _collect_ids(ids_arg: str | None, from_fetch: str | None) -> tuple[list[str], list[dict]]:
    """Returns (ids, history_entries). Entries carry title/score/date when the source
    is a fetch payload, so committed papers show up in `paper-signal history`."""
    ids: list[str] = []
    entries: list[dict] = []
    if ids_arg:
        ids.extend(token.strip() for token in ids_arg.split(",") if token.strip())
    if from_fetch:
        raw = sys.stdin.read() if from_fetch == "-" else Path(from_fetch).read_text(encoding="utf-8")
        payload = json.loads(raw)
        run_date = payload.get("run_date", "")
        for paper in payload.get("papers", []):
            paper_id = paper.get("paper_id")
            if not paper_id:
                continue
            ids.append(paper_id)
            entries.append(
                {
                    "paper_id": paper_id,
                    "title": paper.get("title", ""),
                    "score": paper.get("score", 0),
                    "date": run_date,
                }
            )
    # Deduplicate while preserving order.
    seen: set[str] = set()
    unique: list[str] = []
    for paper_id in ids:
        if paper_id not in seen:
            seen.add(paper_id)
            unique.append(paper_id)
    return unique, entries


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="paper-signal")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command")

    run = subparsers.add_parser(
        "run", help="Fetch, score, and write the daily note (deterministic quick scan)"
    )
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
    run.add_argument(
        "--no-mark-seen",
        action="store_true",
        help="Write the note but don't mark papers seen (tuning mode: re-runs show them again)",
    )

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

    unsee_parser = subparsers.add_parser(
        "unsee", help="Forget seen papers so they can be recommended again"
    )
    unsee_parser.add_argument(
        "--vault",
        default=os.environ.get("OBSIDIAN_VAULT_PATH"),
        help="Path to Obsidian vault",
    )
    unsee_parser.add_argument(
        "--last-run", action="store_true", help="Forget the most recent run's papers"
    )
    unsee_parser.add_argument("--all", action="store_true", help="Forget everything (full reset)")
    unsee_parser.add_argument("--ids", help="Comma-separated paper ids to forget")

    history_parser = subparsers.add_parser(
        "history", help="Show recently recommended papers by day"
    )
    history_parser.add_argument(
        "--vault",
        default=os.environ.get("OBSIDIAN_VAULT_PATH"),
        help="Path to Obsidian vault",
    )
    history_parser.add_argument("--days", type=int, default=7, help="How many days back (default 7)")

    init = subparsers.add_parser("init", help="Scaffold config + vault for a first run")
    init.add_argument(
        "--config",
        default=os.environ.get("PAPER_SIGNAL_CONFIG", "config/interests.yaml"),
        help="Where to write the interests config",
    )
    init.add_argument("--vault", default=os.environ.get("OBSIDIAN_VAULT_PATH"))
    init.add_argument("--force", action="store_true", help="Overwrite an existing config")

    doctor_parser = subparsers.add_parser("doctor", help="Check that the setup is ready to run")
    doctor_parser.add_argument(
        "--config",
        default=os.environ.get("PAPER_SIGNAL_CONFIG", "config/interests.yaml"),
        help="Path to interests YAML config",
    )
    doctor_parser.add_argument("--vault", default=os.environ.get("OBSIDIAN_VAULT_PATH"))
    doctor_parser.add_argument(
        "--offline", action="store_true", help="Skip the arXiv reachability check"
    )

    init_vault_parser = subparsers.add_parser(
        "init-vault", help="Create required Obsidian directories"
    )
    init_vault_parser.add_argument("--vault", default=os.environ.get("OBSIDIAN_VAULT_PATH"))

    return parser
