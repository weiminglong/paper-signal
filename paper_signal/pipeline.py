from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
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
from paper_signal.sources.arxiv import search_arxiv, search_arxiv_by_keywords
from paper_signal.state import PaperSignalState

# How many domain keywords (by domain priority) feed the server-side arXiv search.
KEYWORD_QUERY_LIMIT = 10


@dataclass(frozen=True)
class PipelineResult:
    fetched_count: int
    selected_count: int
    daily_note_path: Path
    wrote: bool
    kept_existing: bool = False


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


def _priority_keywords(config: AppConfig, limit: int = KEYWORD_QUERY_LIMIT) -> list[str]:
    """Top keywords across domains, highest-priority domains first."""
    keywords: list[str] = []
    for domain in sorted(config.research_domains, key=lambda d: d.priority, reverse=True):
        for keyword in domain.keywords:
            if keyword not in keywords:
                keywords.append(keyword)
            if len(keywords) >= limit:
                return keywords
    return keywords


def _gather(config: AppConfig, state: PaperSignalState) -> tuple[int, int, list[ScoredPaper]]:
    """Fetch, dedup, score, and select. Shared by the deterministic and agent paths."""
    papers = search_arxiv(
        categories=config.arxiv_categories,
        max_results=config.daily.candidate_limit,
    )
    if config.arxiv_keyword_search:
        # Server-side keyword search catches thin-coverage fields whose papers are
        # scattered across large categories (recency windows alone miss them).
        # Best-effort: if arXiv rate-limits this extra query, the category results stand.
        try:
            keyword_papers = search_arxiv_by_keywords(
                keywords=_priority_keywords(config),
                max_results=config.daily.candidate_limit,
            )
        except OSError:
            keyword_papers = []
        by_id = {paper.paper_id: paper for paper in papers}
        for paper in keyword_papers:
            by_id.setdefault(paper.paper_id, paper)
        papers = sorted(by_id.values(), key=lambda paper: paper.published, reverse=True)
    raw_count = len(papers)
    if config.daily.skip_seen:
        papers = [paper for paper in papers if paper.paper_id not in state.seen_paper_ids]
    candidate_count = len(papers)

    scored = score_papers(papers, config)
    selected = scored[: config.daily.recommendation_count]
    return raw_count, candidate_count, selected


def run_pipeline(
    config_path: str | Path,
    vault_path: str | None,
    dry_run: bool,
    mark_seen: bool = True,
) -> PipelineResult:
    """Deterministic path: fetch, score, deterministic panel, write note (path A).

    mark_seen=False writes the note but leaves dedup state untouched — the tuning
    mode: iterate on keywords without hiding this run's papers from the next one.
    """
    config = load_config(config_path)
    vault = _resolve_vault(vault_path, config)
    state = PaperSignalState.load(_state_path(vault))
    run_date = date.today()

    _, candidate_count, selected = _gather(config, state)
    selected = add_panel_discussion(selected)

    write_result: WriteResult = write_daily_note(
        vault_path=vault,
        config=config,
        scored_papers=selected,
        run_date=run_date,
        dry_run=dry_run,
    )

    if not dry_run and mark_seen and selected:
        run_marker = _new_run_marker()
        state.record(
            [
                {
                    "paper_id": item.paper.paper_id,
                    "title": item.paper.title,
                    "score": item.score,
                    "date": run_date.isoformat(),
                    "run": run_marker,
                }
                for item in selected
            ]
        )
        state.save(_state_path(vault))

    return PipelineResult(
        fetched_count=candidate_count,
        selected_count=len(selected),
        daily_note_path=write_result.daily_note_path,
        wrote=write_result.wrote,
        kept_existing=write_result.kept_existing,
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


def _new_run_marker() -> str:
    """Per-run identity for history entries, so `unsee --last-run` targets exactly
    one run even when several happen on the same day."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def commit_seen(
    vault_path: str | Path,
    paper_ids: Iterable[str],
    entries: list[dict[str, Any]] | None = None,
) -> int:
    """Mark paper ids as seen so they are not recommended again. Returns total seen.

    Every committed id gets a history entry (so `history` and `unsee --last-run` can
    see it); `entries` from a fetch payload add title/score/date metadata.
    """
    state_path = _state_path(Path(vault_path))
    state = PaperSignalState.load(state_path)
    run_marker = _new_run_marker()
    all_entries = [dict(entry) for entry in (entries or [])]
    for entry in all_entries:
        entry.setdefault("run", run_marker)
    covered = {entry.get("paper_id") for entry in all_entries}
    today = date.today().isoformat()
    all_entries.extend(
        {"paper_id": pid, "score": 0, "date": today, "run": run_marker}
        for pid in paper_ids
        if pid not in covered
    )
    state.record(all_entries)
    state.save(state_path)
    return len(state.seen_paper_ids)


def unsee(vault_path: str | Path, *, ids: list[str] | None = None, last_run: bool = False,
          everything: bool = False) -> int:
    """Forget papers so they can be recommended again. Returns how many were removed."""
    state_path = _state_path(Path(vault_path))
    state = PaperSignalState.load(state_path)
    if everything:
        removed = len(state.seen_paper_ids)
        state.seen_paper_ids = set()
        state.history = []
    elif last_run:
        marker = state.last_run_marker()
        removed = state.unsee(state.ids_for_marker(marker)) if marker else 0
    else:
        removed = state.unsee(ids or [])
    # Don't scaffold a fresh state tree under a typo'd vault path for a no-op.
    if removed or state_path.exists():
        state.save(state_path)
    return removed


def recent_history(vault_path: str | Path, days: int) -> list[dict[str, Any]]:
    """History entries from the last `days` days, newest first, best score first."""
    state = PaperSignalState.load(_state_path(Path(vault_path)))
    cutoff = (date.today() - timedelta(days=days)).isoformat()
    entries = [e for e in state.history if e.get("date", "") >= cutoff]
    # reverse=True already makes both components descending; no negation needed.
    return sorted(entries, key=lambda e: (e.get("date", ""), float(e.get("score", 0))), reverse=True)


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
