from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable

from paper_signal.agents.panel import add_panel_discussion
from paper_signal.config import load_config
from paper_signal.models import AppConfig, ScoredPaper
from paper_signal.obsidian.writer import (
    WriteResult,
    daily_note_path,
    init_vault,
    write_daily_note,
)
from paper_signal.scoring.deterministic import score_papers
from paper_signal.sources.arxiv import search_arxiv
from paper_signal.state import PaperSignalState


@dataclass(frozen=True)
class PipelineResult:
    fetched_count: int
    selected_count: int
    daily_note_path: Path
    wrote: bool


@dataclass(frozen=True)
class FetchResult:
    """Selected candidates plus the vault paths an external agent needs."""

    config: AppConfig
    vault_path: Path
    run_date: date
    fetched_count: int
    candidate_count: int
    selected: list[ScoredPaper]


def _resolve_vault(vault_path: str | None, config: AppConfig) -> Path:
    resolved = vault_path or config.vault_path
    if not resolved:
        raise ValueError(
            "Vault path is required via --vault, config.vault_path, or OBSIDIAN_VAULT_PATH"
        )
    return Path(resolved)


def _state_path(vault: Path) -> Path:
    return vault / "99_System" / "PaperSignal" / "state.json"


def _gather(config: AppConfig, state: PaperSignalState) -> tuple[int, int, list[ScoredPaper]]:
    """Fetch, dedup, score, and select. Shared by the deterministic and agent paths."""
    papers = search_arxiv(
        categories=config.arxiv_categories,
        max_results=config.daily.candidate_limit,
    )
    raw_count = len(papers)
    if config.daily.skip_seen:
        papers = [paper for paper in papers if paper.paper_id not in state.seen_paper_ids]
    candidate_count = len(papers)

    scored = score_papers(papers, config)
    selected = scored[: config.daily.recommendation_count]
    return raw_count, candidate_count, selected


def run_pipeline(config_path: str | Path, vault_path: str | None, dry_run: bool) -> PipelineResult:
    """Deterministic path: fetch, score, deterministic panel, write note (path A)."""
    config = load_config(config_path)
    vault = _resolve_vault(vault_path, config)
    state = PaperSignalState.load(_state_path(vault))

    _, candidate_count, selected = _gather(config, state)
    selected = add_panel_discussion(selected)

    write_result: WriteResult = write_daily_note(
        vault_path=vault,
        config=config,
        scored_papers=selected,
        run_date=date.today(),
        dry_run=dry_run,
    )

    if not dry_run:
        state.mark_seen([item.paper.paper_id for item in selected])
        state.save(_state_path(vault))

    return PipelineResult(
        fetched_count=candidate_count,
        selected_count=len(selected),
        daily_note_path=write_result.daily_note_path,
        wrote=write_result.wrote,
    )


def fetch_candidates(
    config_path: str | Path,
    vault_path: str | None,
    *,
    run_date: date | None = None,
    ensure_vault: bool = True,
) -> FetchResult:
    """Agent path (B): fetch, score, and select candidates without writing a note or state.

    The selected papers and vault paths are handed to Claude Code, which runs the
    multi-agent round-table analysis and authors the note itself.
    """
    config = load_config(config_path)
    vault = _resolve_vault(vault_path, config)
    if ensure_vault:
        init_vault(vault)
    state = PaperSignalState.load(_state_path(vault))

    raw_count, candidate_count, selected = _gather(config, state)
    return FetchResult(
        config=config,
        vault_path=vault,
        run_date=run_date or date.today(),
        fetched_count=raw_count,
        candidate_count=candidate_count,
        selected=selected,
    )


def commit_seen(vault_path: str | Path, paper_ids: Iterable[str]) -> int:
    """Mark paper ids as seen so they are not recommended again. Returns total seen."""
    state_path = _state_path(Path(vault_path))
    state = PaperSignalState.load(state_path)
    state.mark_seen(list(paper_ids))
    state.save(state_path)
    return len(state.seen_paper_ids)


def fetch_payload(result: FetchResult) -> dict[str, Any]:
    """Serialize a FetchResult to the JSON contract consumed by the Claude Code skill."""
    deep_n = result.config.daily.deep_analysis_count
    papers: list[dict[str, Any]] = []
    for index, item in enumerate(result.selected):
        paper = item.paper
        papers.append(
            {
                "rank": index + 1,
                "deep": index < deep_n,
                "paper_id": paper.paper_id,
                "title": paper.title,
                "authors": paper.authors,
                "abstract": paper.abstract,
                "categories": paper.categories,
                "published": paper.published.date().isoformat(),
                "updated": paper.updated.date().isoformat(),
                "arxiv_url": paper.arxiv_url,
                "pdf_url": paper.pdf_url,
                "score": item.score,
                "matched_domains": item.matched_domains,
                "matched_keywords": item.matched_keywords,
                "reasons": item.reasons,
            }
        )
    return {
        "run_date": result.run_date.isoformat(),
        "vault_path": str(result.vault_path),
        "daily_note_path": str(daily_note_path(result.vault_path, result.run_date)),
        "papers_dir": str(result.vault_path / "20_Research" / "Papers"),
        "state_path": str(_state_path(result.vault_path)),
        "language": result.config.language,
        "domains": [domain.name for domain in result.config.research_domains],
        "deep_analysis_count": deep_n,
        "recommendation_count": result.config.daily.recommendation_count,
        "fetched_count": result.fetched_count,
        "candidate_count": result.candidate_count,
        "selected_count": len(result.selected),
        "papers": papers,
    }
