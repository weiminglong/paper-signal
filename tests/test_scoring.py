from datetime import datetime, timezone

from paper_signal.models import AppConfig, DailySettings, Paper, ResearchDomain
from paper_signal.scoring.deterministic import score_papers


def test_scores_matching_keywords():
    config = AppConfig(
        language="en",
        vault_path="",
        daily=DailySettings(),
        arxiv_categories=["cs.AI"],
        research_domains=[
            ResearchDomain(
                name="Agents",
                priority=5,
                keywords=["multi-agent", "planning"],
                arxiv_categories=["cs.AI"],
            )
        ],
        excluded_keywords=[],
    )
    paper = Paper(
        paper_id="2601.00001",
        title="Multi-Agent Planning for Tool Use",
        authors=["A. Researcher"],
        abstract="We study planning with tool use.",
        published=datetime.now(timezone.utc),
        updated=datetime.now(timezone.utc),
        categories=["cs.AI"],
        arxiv_url="https://arxiv.org/abs/2601.00001",
        pdf_url="https://arxiv.org/pdf/2601.00001",
    )

    scored = score_papers([paper], config)

    assert len(scored) == 1
    assert scored[0].score > 0
    assert scored[0].matched_domains == ["Agents"]
    assert "multi-agent" in scored[0].matched_keywords
