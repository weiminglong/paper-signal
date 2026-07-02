"""Tests for the day-2/journey features: history, unsee, preview mode, overwrite
guard, and the server-side keyword search merge."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path

from paper_signal import pipeline
from paper_signal.models import AppConfig, DailySettings, Paper, ResearchDomain
from paper_signal.obsidian.writer import write_daily_note
from paper_signal.pipeline import commit_seen, recent_history, run_pipeline, unsee
from paper_signal.state import PaperSignalState


def _config(**overrides) -> AppConfig:
    defaults = dict(
        language="en",
        vault_path="",
        daily=DailySettings(candidate_limit=10, recommendation_count=5),
        arxiv_categories=["cs.AI"],
        research_domains=[
            ResearchDomain(name="Agents", priority=5, keywords=["agent"], arxiv_categories=["cs.AI"])
        ],
        excluded_keywords=[],
    )
    defaults.update(overrides)
    return AppConfig(**defaults)


def _paper(paper_id: str, title: str = "Agent paper", days_ago: int = 0) -> Paper:
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


def _write_config(tmp_path: Path) -> Path:
    config_file = tmp_path / "interests.yaml"
    config_file.write_text(
        "research_domains:\n  Agents:\n    keywords: [agent]\n    arxiv_categories: [cs.AI]\n",
        encoding="utf-8",
    )
    return config_file


# ---- state: history, unsee, back-compat ----


def test_state_back_compat_loads_old_flat_format(tmp_path):
    path = tmp_path / "state.json"
    path.write_text(json.dumps({"seen_paper_ids": ["a", "b"]}), encoding="utf-8")
    state = PaperSignalState.load(path)
    assert state.seen_paper_ids == {"a", "b"}
    assert state.history == []
    # Saving the upgraded shape round-trips.
    state.record([{"paper_id": "c", "title": "T", "score": 1.0, "date": "2026-07-02"}])
    state.save(path)
    reloaded = PaperSignalState.load(path)
    assert reloaded.seen_paper_ids == {"a", "b", "c"}
    assert reloaded.history[0]["title"] == "T"


def test_state_unsee_removes_ids_and_history():
    state = PaperSignalState()
    state.record(
        [
            {"paper_id": "a", "title": "A", "score": 2.0, "date": "2026-07-01"},
            {"paper_id": "b", "title": "B", "score": 1.0, "date": "2026-07-02"},
        ]
    )
    assert state.last_run_date() == "2026-07-02"
    assert state.ids_for_date("2026-07-02") == ["b"]
    removed = state.unsee(["b", "zz"])
    assert removed == 1
    assert state.seen_paper_ids == {"a"}
    assert [e["paper_id"] for e in state.history] == ["a"]


def test_unsee_last_run_and_history(tmp_path):
    vault = tmp_path / "vault"
    # Two separate commits = two runs; --last-run must only forget the second.
    commit_seen(vault, ["a"], entries=[{"paper_id": "a", "title": "A", "score": 3.0, "date": "2026-07-01"}])
    commit_seen(vault, ["b"], entries=[{"paper_id": "b", "title": "B", "score": 2.0, "date": "2026-07-02"}])
    entries = recent_history(vault, days=3650)
    assert [e["paper_id"] for e in entries] == ["b", "a"]

    removed = unsee(vault, last_run=True)
    assert removed == 1
    state = PaperSignalState.load(vault / "99_System" / "PaperSignal" / "state.json")
    assert state.seen_paper_ids == {"a"}

    assert unsee(vault, everything=True) == 1
    assert PaperSignalState.load(vault / "99_System" / "PaperSignal" / "state.json").seen_paper_ids == set()


def test_commit_ids_records_history_and_last_run_targets_it(tmp_path):
    """`commit --ids` (no metadata) must still be visible to history/unsee --last-run —
    otherwise --last-run silently deletes an OLDER run's memory instead."""
    vault = tmp_path / "vault"
    commit_seen(vault, ["old"], entries=[{"paper_id": "old", "title": "Old", "score": 5.0, "date": "2026-07-01"}])
    commit_seen(vault, ["x", "y"])  # ids-only commit, as `commit --ids x,y`

    entries = recent_history(vault, days=3650)
    assert {e["paper_id"] for e in entries} == {"old", "x", "y"}

    removed = unsee(vault, last_run=True)
    assert removed == 2  # forgets x and y — NOT the older run
    state = PaperSignalState.load(vault / "99_System" / "PaperSignal" / "state.json")
    assert state.seen_paper_ids == {"old"}
    assert [e["paper_id"] for e in state.history] == ["old"]


def test_same_day_runs_have_distinct_run_markers(tmp_path):
    vault = tmp_path / "vault"
    today = date.today().isoformat()
    commit_seen(vault, ["r1a"], entries=[{"paper_id": "r1a", "title": "R1", "score": 1.0, "date": today}])
    commit_seen(vault, ["r2a"], entries=[{"paper_id": "r2a", "title": "R2", "score": 1.0, "date": today}])
    removed = unsee(vault, last_run=True)
    assert removed == 1  # only the second same-day run
    state = PaperSignalState.load(vault / "99_System" / "PaperSignal" / "state.json")
    assert state.seen_paper_ids == {"r1a"}


def test_recent_history_orders_best_score_first_within_day(tmp_path):
    vault = tmp_path / "vault"
    today = date.today().isoformat()
    commit_seen(
        vault,
        ["lo", "hi", "mid"],
        entries=[
            {"paper_id": "lo", "title": "Lo", "score": 1.0, "date": today},
            {"paper_id": "hi", "title": "Hi", "score": 9.0, "date": today},
            {"paper_id": "mid", "title": "Mid", "score": 5.0, "date": today},
        ],
    )
    entries = recent_history(vault, days=2)
    assert [e["paper_id"] for e in entries] == ["hi", "mid", "lo"]


def test_unsee_noop_does_not_scaffold_state_tree(tmp_path):
    vault = tmp_path / "typo-vault"
    removed = unsee(vault, last_run=True)
    assert removed == 0
    assert not (vault / "99_System").exists()


# ---- writer: overwrite guard ----


def test_empty_run_does_not_clobber_existing_note(tmp_path):
    vault = tmp_path / "vault"
    config = _config()
    good = write_daily_note(
        vault_path=vault,
        config=config,
        scored_papers=pipeline.add_panel_discussion(
            [
                pipeline.ScoredPaper(
                    paper=_paper("1"), score=5.0, matched_domains=["Agents"],
                    matched_keywords=["agent"], reasons=["r"],
                )
            ]
        ),
        run_date=date(2026, 7, 2),
        dry_run=False,
    )
    assert good.wrote
    before = good.daily_note_path.read_text(encoding="utf-8")

    empty = write_daily_note(
        vault_path=vault, config=config, scored_papers=[], run_date=date(2026, 7, 2), dry_run=False
    )
    assert empty.kept_existing is True
    assert empty.wrote is False
    assert good.daily_note_path.read_text(encoding="utf-8") == before


# ---- pipeline: preview mode + keyword merge ----


def test_no_mark_seen_leaves_state_untouched(tmp_path, monkeypatch):
    config_file = _write_config(tmp_path)
    vault = tmp_path / "vault"
    monkeypatch.setattr(pipeline, "search_arxiv", lambda categories, max_results: [_paper("1")])
    monkeypatch.setattr(pipeline, "search_arxiv_by_keywords", lambda keywords, max_results: [])

    result = run_pipeline(config_path=config_file, vault_path=str(vault), dry_run=False, mark_seen=False)
    assert result.selected_count == 1
    assert not (vault / "99_System" / "PaperSignal" / "state.json").exists()

    # A normal run records history with today's date.
    result2 = run_pipeline(config_path=config_file, vault_path=str(vault), dry_run=False)
    assert result2.selected_count == 1
    state = PaperSignalState.load(vault / "99_System" / "PaperSignal" / "state.json")
    assert state.seen_paper_ids == {"1"}
    assert state.history[0]["date"] == date.today().isoformat()


def test_keyword_query_sanitizes_quotes(monkeypatch):
    from paper_signal.sources import arxiv as arxiv_module

    captured = {}
    monkeypatch.setattr(arxiv_module, "sleep", lambda seconds: None)
    monkeypatch.setattr(
        arxiv_module, "_search_arxiv_query",
        lambda query, max_results: captured.update(query=query) or [],
    )
    arxiv_module.search_arxiv_by_keywords(['gene "editing"', "agent"], max_results=5)
    # Embedded quotes stripped; every term quoted unconditionally.
    assert captured["query"] == 'all:"gene editing" OR all:"agent"'


def test_keyword_search_failure_degrades_gracefully(tmp_path, monkeypatch):
    """arXiv rate-limiting the extra keyword query must not kill the run."""
    config_file = _write_config(tmp_path)
    vault = tmp_path / "vault"
    monkeypatch.setattr(pipeline, "search_arxiv", lambda categories, max_results: [_paper("1")])

    def raise_429(keywords, max_results):
        raise OSError("HTTP Error 429: Too Many Requests")

    monkeypatch.setattr(pipeline, "search_arxiv_by_keywords", raise_429)
    result = pipeline.fetch_candidates(config_path=config_file, vault_path=str(vault))
    assert [item.paper.paper_id for item in result.selected] == ["1"]


def test_keyword_search_merges_and_dedups(tmp_path, monkeypatch):
    config_file = _write_config(tmp_path)
    vault = tmp_path / "vault"
    calls = {}

    monkeypatch.setattr(
        pipeline, "search_arxiv",
        lambda categories, max_results: [_paper("1", "Agent paper one")],
    )

    def fake_kw(keywords, max_results):
        calls["keywords"] = keywords
        return [_paper("1", "Agent paper one"), _paper("2", "Agent paper two")]

    monkeypatch.setattr(pipeline, "search_arxiv_by_keywords", fake_kw)

    result = pipeline.fetch_candidates(config_path=config_file, vault_path=str(vault))
    assert calls["keywords"] == ["agent"]
    ids = sorted(item.paper.paper_id for item in result.selected)
    assert ids == ["1", "2"]          # merged
    assert result.fetched_count == 2  # deduped, not 3
