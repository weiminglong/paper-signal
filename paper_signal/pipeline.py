from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from paper_signal.agents.panel import add_panel_discussion
from paper_signal.config import load_config
from paper_signal.obsidian.writer import WriteResult, write_daily_note
from paper_signal.scoring.deterministic import score_papers
from paper_signal.sources.arxiv import search_arxiv
from paper_signal.state import PaperSignalState


@dataclass(frozen=True)
class PipelineResult:
    fetched_count: int
    selected_count: int
    daily_note_path: Path
    wrote: bool


def run_pipeline(config_path: str | Path, vault_path: str | None, dry_run: bool) -> PipelineResult:
    config = load_config(config_path)
    resolved_vault = vault_path or config.vault_path
    if not resolved_vault:
        raise ValueError("Vault path is required via --vault, config.vault_path, or OBSIDIAN_VAULT_PATH")

    state_path = Path(resolved_vault) / "99_System" / "PaperSignal" / "state.json"
    state = PaperSignalState.load(state_path)

    papers = search_arxiv(
        categories=config.arxiv_categories,
        max_results=config.daily.candidate_limit,
    )
    if config.daily.skip_seen:
        papers = [paper for paper in papers if paper.paper_id not in state.seen_paper_ids]

    scored = score_papers(papers, config)
    selected = scored[: config.daily.recommendation_count]
    selected = add_panel_discussion(selected)

    write_result: WriteResult = write_daily_note(
        vault_path=resolved_vault,
        config=config,
        scored_papers=selected,
        run_date=date.today(),
        dry_run=dry_run,
    )

    if not dry_run:
        state.mark_seen([item.paper.paper_id for item in selected])
        state.save(state_path)

    return PipelineResult(
        fetched_count=len(papers),
        selected_count=len(selected),
        daily_note_path=write_result.daily_note_path,
        wrote=write_result.wrote,
    )
