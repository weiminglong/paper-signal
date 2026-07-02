from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from importlib import resources
from pathlib import Path

from jinja2 import Environment, StrictUndefined

from paper_signal.models import AppConfig, ScoredPaper


@dataclass(frozen=True)
class WriteResult:
    daily_note_path: Path
    wrote: bool
    # True when an empty run was suppressed to protect an existing note for the day.
    kept_existing: bool = False


def init_vault(vault_path: str | Path) -> None:
    vault = Path(vault_path)
    for relative in [
        "10_Daily",
        "20_Research/Papers",
        "99_System/PaperSignal",
    ]:
        (vault / relative).mkdir(parents=True, exist_ok=True)


def daily_note_path(vault_path: str | Path, run_date: date) -> Path:
    """Canonical location of the dated daily note inside the vault."""
    return Path(vault_path) / "10_Daily" / f"{run_date.isoformat()}-paper-recommendations.md"


def write_daily_note(
    vault_path: str | Path,
    config: AppConfig,
    scored_papers: list[ScoredPaper],
    run_date: date,
    dry_run: bool,
) -> WriteResult:
    vault = Path(vault_path)
    init_vault(vault)
    note_path = daily_note_path(vault, run_date)
    # Guard: a re-run that matched nothing (e.g. everything already seen) must not
    # replace a note the user already has for today with "No matching papers".
    if not scored_papers and note_path.exists() and note_path.stat().st_size > 0:
        return WriteResult(daily_note_path=note_path, wrote=False, kept_existing=True)
    body = render_daily_note(config=config, scored_papers=scored_papers, run_date=run_date)
    if not dry_run:
        note_path.write_text(body, encoding="utf-8")
    return WriteResult(daily_note_path=note_path, wrote=not dry_run)


def render_daily_note(
    config: AppConfig,
    scored_papers: list[ScoredPaper],
    run_date: date,
) -> str:
    template_text = resources.files("paper_signal.obsidian.templates").joinpath(
        "daily_note.md.j2"
    ).read_text(encoding="utf-8")
    env = Environment(undefined=StrictUndefined, autoescape=False, trim_blocks=True)
    template = env.from_string(template_text)
    return template.render(
        config=config,
        papers=scored_papers,
        run_date=run_date,
        domains=", ".join(domain.name for domain in config.research_domains),
    )
