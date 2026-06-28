from datetime import date, datetime, timezone

from paper_signal.agents.panel import add_panel_discussion
from paper_signal.models import AppConfig, DailySettings, Paper, ResearchDomain, ScoredPaper
from paper_signal.obsidian.writer import render_daily_note


def test_render_daily_note_contains_title():
    config = AppConfig(
        language="en",
        vault_path="",
        daily=DailySettings(),
        arxiv_categories=["cs.AI"],
        research_domains=[
            ResearchDomain(name="Agents", priority=5, keywords=["agent"], arxiv_categories=["cs.AI"])
        ],
        excluded_keywords=[],
    )
    paper = Paper(
        paper_id="2601.00001",
        title="Agent Systems for Research",
        authors=["A. Researcher"],
        abstract="An agent system for research workflows.",
        published=datetime.now(timezone.utc),
        updated=datetime.now(timezone.utc),
        categories=["cs.AI"],
        arxiv_url="https://arxiv.org/abs/2601.00001",
        pdf_url="https://arxiv.org/pdf/2601.00001",
    )
    scored = add_panel_discussion(
        [
            ScoredPaper(
                paper=paper,
                score=8.0,
                matched_domains=["Agents"],
                matched_keywords=["agent"],
                reasons=["Agents: 8.0 relevance points"],
            )
        ]
    )

    rendered = render_daily_note(config=config, scored_papers=scored, run_date=date(2026, 6, 28))

    assert "# Daily Paper Read - 2026-06-28" in rendered
    assert "Agent Systems for Research" in rendered
