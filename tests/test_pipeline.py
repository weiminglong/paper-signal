from __future__ import annotations

import json
from datetime import date, datetime, timezone

import pytest

from paper_signal import pipeline
from paper_signal.models import (
    AppConfig,
    DailySettings,
    Paper,
    ResearchDomain,
    ScoredPaper,
)
from paper_signal.obsidian.writer import daily_note_path
from paper_signal.pipeline import (
    FetchResult,
    commit_seen,
    fetch_candidates,
    fetch_payload,
)
from paper_signal.state import PaperSignalState


def _config(deep_analysis_count: int = 2) -> AppConfig:
    return AppConfig(
        language="en",
        vault_path="",
        daily=DailySettings(
            candidate_limit=10,
            recommendation_count=5,
            deep_analysis_count=deep_analysis_count,
            skip_seen=True,
        ),
        arxiv_categories=["cs.AI"],
        research_domains=[
            ResearchDomain(name="Agents", priority=5, keywords=["agent"], arxiv_categories=["cs.AI"])
        ],
        excluded_keywords=[],
    )


def _paper(paper_id: str, title: str) -> Paper:
    now = datetime.now(timezone.utc)
    return Paper(
        paper_id=paper_id,
        title=title,
        authors=["A. Researcher"],
        abstract="An agent system for research workflows.",
        published=now,
        updated=now,
        categories=["cs.AI"],
        arxiv_url=f"https://arxiv.org/abs/{paper_id}",
        pdf_url=f"https://arxiv.org/pdf/{paper_id}",
    )


def test_daily_note_path():
    path = daily_note_path("/vault", date(2026, 6, 30))
    assert path.as_posix() == "/vault/10_Daily/2026-06-30-paper-recommendations.md"


def test_fetch_payload_flags_deep_papers():
    config = _config(deep_analysis_count=2)
    selected = [
        ScoredPaper(
            paper=_paper(f"2601.0000{n}", f"Agent paper {n}"),
            score=float(10 - n),
            matched_domains=["Agents"],
            matched_keywords=["agent"],
            reasons=["Agents: x relevance points"],
        )
        for n in range(3)
    ]
    result = FetchResult(
        config=config,
        vault_path=pipeline.Path("/vault"),
        run_date=date(2026, 6, 30),
        fetched_count=9,
        candidate_count=7,
        selected=selected,
    )

    payload = fetch_payload(result)

    assert payload["run_date"] == "2026-06-30"
    assert payload["daily_note_path"].endswith("2026-06-30-paper-recommendations.md")
    assert payload["papers_dir"].endswith("20_Research/Papers")
    assert payload["deep_analysis_count"] == 2
    assert payload["fetched_count"] == 9
    assert payload["candidate_count"] == 7
    assert payload["selected_count"] == 3
    deep_flags = [p["deep"] for p in payload["papers"]]
    assert deep_flags == [True, True, False]
    assert payload["papers"][0]["rank"] == 1
    assert payload["papers"][0]["abstract"]
    # The payload must be JSON-serializable.
    json.dumps(payload)


def test_fetch_candidates_is_read_only(tmp_path, monkeypatch):
    config_file = tmp_path / "interests.yaml"
    config_file.write_text(
        "research_domains:\n  Agents:\n    keywords: [agent]\n    arxiv_categories: [cs.AI]\n",
        encoding="utf-8",
    )
    vault = tmp_path / "vault"

    monkeypatch.setattr(
        pipeline,
        "search_arxiv",
        lambda categories, max_results: [_paper("2601.00001", "Agent paper")],
    )
    monkeypatch.setattr(pipeline, "search_arxiv_by_keywords", lambda keywords, max_results: [])

    result = fetch_candidates(config_path=config_file, vault_path=str(vault))

    assert len(result.selected) == 1
    assert result.selected[0].paper.paper_id == "2601.00001"
    # Vault folders are created, but neither the note nor state.json is written.
    assert (vault / "10_Daily").is_dir()
    assert not (vault / "10_Daily" / "2026-06-30-paper-recommendations.md").exists()
    assert not (vault / "99_System" / "PaperSignal" / "state.json").exists()


def test_fetch_candidates_skips_seen(tmp_path, monkeypatch):
    config_file = tmp_path / "interests.yaml"
    config_file.write_text(
        "research_domains:\n  Agents:\n    keywords: [agent]\n    arxiv_categories: [cs.AI]\n",
        encoding="utf-8",
    )
    vault = tmp_path / "vault"
    commit_seen(vault, ["2601.00001"])

    monkeypatch.setattr(
        pipeline,
        "search_arxiv",
        lambda categories, max_results: [
            _paper("2601.00001", "Already seen agent paper"),
            _paper("2601.00002", "New agent paper"),
        ],
    )
    monkeypatch.setattr(pipeline, "search_arxiv_by_keywords", lambda keywords, max_results: [])

    result = fetch_candidates(config_path=config_file, vault_path=str(vault))

    ids = [item.paper.paper_id for item in result.selected]
    assert ids == ["2601.00002"]


def test_commit_seen_persists_state(tmp_path):
    vault = tmp_path / "vault"
    total = commit_seen(vault, ["a", "b", "a"])
    assert total == 2

    state_path = vault / "99_System" / "PaperSignal" / "state.json"
    state = PaperSignalState.load(state_path)
    assert state.seen_paper_ids == {"a", "b"}

    # Committing again accumulates rather than replacing.
    commit_seen(vault, ["c"])
    assert PaperSignalState.load(state_path).seen_paper_ids == {"a", "b", "c"}


def test_fetch_candidates_requires_vault(tmp_path):
    config_file = tmp_path / "interests.yaml"
    config_file.write_text(
        "research_domains:\n  Agents:\n    keywords: [agent]\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        fetch_candidates(config_path=config_file, vault_path=None)
