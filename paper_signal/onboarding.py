from __future__ import annotations

import os
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from paper_signal.config import load_config
from paper_signal.obsidian.writer import init_vault
from paper_signal.sources.arxiv import ARXIV_API_URL
from paper_signal.state import PaperSignalState


def _wrong_os_vault(path: str) -> bool:
    """A Windows drive-letter path (C:\\... or C:/...) on a non-Windows system is almost
    always a typo. Scaffolding it would silently create a junk folder, so flag it."""
    return os.name != "nt" and re.match(r"^[A-Za-z]:[\\/]", path) is not None

DEFAULT_INTERESTS_YAML = """\
# PaperSignal interests. Edit the domains/keywords below to match your research.
# Docs: https://github.com/weiminglong/paper-signal

language: "en"
# Where to write daily notes. Leave "" to use the OBSIDIAN_VAULT_PATH env var instead.
vault_path: ""

daily:
  candidate_limit: 100      # how many recent papers to pull from arXiv
  recommendation_count: 10  # how many make it into the note
  deep_analysis_count: 3    # how many get the full round-table (Claude Code path)
  skip_seen: true           # don't re-recommend papers already seen

sources:
  arxiv:
    enabled: true
    categories:
      - "cs.AI"
      - "cs.CL"
      - "cs.LG"

research_domains:
  "Agents":
    priority: 5
    keywords:
      - "agent"
      - "multi-agent"
      - "tool use"
      - "planning"
    arxiv_categories:
      - "cs.AI"
      - "cs.CL"

  "Reasoning":
    priority: 4
    keywords:
      - "reasoning"
      - "chain-of-thought"
      - "verification"
    arxiv_categories:
      - "cs.AI"
      - "cs.LG"

excluded_keywords:
  - "workshop"
"""


@dataclass
class InitResult:
    config_path: Path
    created_config: bool = False
    vault: str | None = None
    scaffolded: bool = False
    notes: list[str] = field(default_factory=list)


def init_project(
    config_path: str | Path,
    vault: str | None = None,
    force: bool = False,
) -> InitResult:
    """Scaffold a config (and vault folders) so a first run works. Idempotent."""
    config_path = Path(config_path)
    result = InitResult(config_path=config_path)
    pre_existed = config_path.exists()
    wrong_os = bool(vault) and _wrong_os_vault(str(vault))
    usable_vault = bool(vault) and not wrong_os

    if pre_existed and not force:
        result.notes.append(f"Config already exists at {config_path} (use --force to overwrite).")
    else:
        content = DEFAULT_INTERESTS_YAML
        if usable_vault:
            # Serialize with yaml so paths containing quotes/backslashes/colons/unicode
            # (e.g. a vault named My "Cool" Vault) stay valid YAML.
            vault_line = yaml.safe_dump(
                {"vault_path": str(vault)},
                default_flow_style=False,
                allow_unicode=True,
                width=1_000_000,
            ).strip()
            content = content.replace('vault_path: ""', vault_line)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(content, encoding="utf-8")
        result.created_config = True
        verb = "Overwrote" if pre_existed else "Wrote"
        result.notes.append(f"{verb} config to {config_path}.")

    if wrong_os:
        result.notes.append(
            f"Vault path '{vault}' looks like a Windows path on a non-Windows system — "
            "ignored (no folders created). Use a path like /Users/you/Obsidian/Vault."
        )
    elif usable_vault:
        init_vault(vault)
        result.vault = str(vault)
        result.scaffolded = True
        result.notes.append(f"Scaffolded vault folders under {vault}.")
    else:
        result.notes.append(
            "No vault set. Pass --vault or export OBSIDIAN_VAULT_PATH, "
            "then run `paper-signal init-vault`."
        )
    return result


@dataclass
class Check:
    name: str
    status: str  # "ok" | "warn" | "fail"
    detail: str
    fix: str = ""


def doctor(
    config_path: str | Path,
    vault: str | None = None,
    offline: bool = False,
) -> tuple[bool, list[Check]]:
    """Preflight the setup. Returns (all_ok, checks). all_ok is False if any check fails."""
    checks: list[Check] = []
    config = None

    config_path = Path(config_path)
    if not config_path.exists():
        checks.append(
            Check("config", "fail", f"No config at {config_path}.", "Run `paper-signal init`.")
        )
    else:
        try:
            config = load_config(config_path)
            checks.append(
                Check(
                    "config",
                    "ok",
                    f"{config_path} parses; {len(config.research_domains)} domain(s).",
                )
            )
            empty = [d.name for d in config.research_domains if not d.keywords]
            if empty:
                checks.append(
                    Check(
                        "domains",
                        "warn",
                        f"Domains with no keywords: {', '.join(empty)}.",
                        "Add keywords so papers can match.",
                    )
                )
        except Exception as exc:  # noqa: BLE001 - surface any config error to the user
            checks.append(
                Check(
                    "config",
                    "fail",
                    f"Config error: {exc}",
                    "Fix the YAML, or re-run `paper-signal init --force`.",
                )
            )

    resolved_vault = (
        vault
        or (config.vault_path if config else "")
        or os.environ.get("OBSIDIAN_VAULT_PATH", "")
    )
    if not resolved_vault:
        checks.append(
            Check(
                "vault",
                "fail",
                "No vault path resolved.",
                "Set OBSIDIAN_VAULT_PATH, add vault_path to the config, or pass --vault.",
            )
        )
    elif _wrong_os_vault(resolved_vault):
        checks.append(
            Check(
                "vault",
                "fail",
                f"Vault path looks like a Windows path on this non-Windows system: {resolved_vault}.",
                "Use a path like /Users/you/Obsidian/Vault.",
            )
        )
    else:
        vault_dir = Path(resolved_vault)
        if not vault_dir.exists():
            checks.append(
                Check(
                    "vault",
                    "warn",
                    f"Vault path does not exist yet: {vault_dir}.",
                    "Run `paper-signal init-vault --vault <path>` (or `paper-signal init`).",
                )
            )
        elif not os.access(vault_dir, os.W_OK):
            checks.append(
                Check("vault", "fail", f"Vault not writable: {vault_dir}.", "Fix permissions.")
            )
        else:
            checks.append(Check("vault", "ok", f"Vault writable: {vault_dir}."))
            state_file = vault_dir / "99_System" / "PaperSignal" / "state.json"
            if state_file.exists():
                try:
                    seen = PaperSignalState.load(state_file).seen_paper_ids
                    checks.append(Check("state", "ok", f"State readable ({len(seen)} seen)."))
                except Exception as exc:  # noqa: BLE001
                    checks.append(
                        Check(
                            "state",
                            "warn",
                            f"State unreadable: {exc}",
                            "Delete state.json to reset dedup.",
                        )
                    )

    if offline:
        checks.append(Check("arxiv", "warn", "Skipped network check (--offline)."))
    else:
        reachable, detail = _check_arxiv()
        checks.append(
            Check(
                "arxiv",
                "ok" if reachable else "warn",
                detail,
                "" if reachable else "Check network/proxy; arXiv may be rate-limiting.",
            )
        )

    all_ok = not any(check.status == "fail" for check in checks)
    return all_ok, checks


def _check_arxiv() -> tuple[bool, str]:
    url = f"{ARXIV_API_URL}?" + urllib.parse.urlencode(
        {"search_query": "cat:cs.AI", "max_results": "1"}
    )
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            code = response.getcode()
        return code == 200, f"arXiv API reachable (HTTP {code})."
    except Exception as exc:  # noqa: BLE001 - reachability probe, any failure is a warning
        return False, f"arXiv API unreachable: {exc}"
