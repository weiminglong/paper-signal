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


def test_short_keyword_does_not_match_inside_unrelated_word():
    config = AppConfig(
        language="en",
        vault_path="",
        daily=DailySettings(),
        arxiv_categories=["cs.AI"],
        research_domains=[
            ResearchDomain(
                name="Data Engineering",
                priority=5,
                keywords=["ELT"],
                arxiv_categories=["cs.AI"],
            )
        ],
        excluded_keywords=[],
    )
    paper = Paper(
        paper_id="2601.00002",
        title="A Delta Rule for Recurrent Models",
        authors=["A. Researcher"],
        abstract="We study a delta-rule architecture.",
        published=datetime.now(timezone.utc),
        updated=datetime.now(timezone.utc),
        categories=["cs.AI"],
        arxiv_url="https://arxiv.org/abs/2601.00002",
        pdf_url="https://arxiv.org/pdf/2601.00002",
    )

    assert score_papers([paper], config) == []


def test_category_only_match_does_not_select_domain():
    config = AppConfig(
        language="en",
        vault_path="",
        daily=DailySettings(),
        arxiv_categories=["cs.AI"],
        research_domains=[
            ResearchDomain(
                name="Data Engineering",
                priority=5,
                keywords=["data warehouse"],
                arxiv_categories=["cs.AI"],
            )
        ],
        excluded_keywords=[],
    )
    paper = Paper(
        paper_id="2601.00003",
        title="Reasoning in Language Models",
        authors=["A. Researcher"],
        abstract="We study reasoning in language models.",
        published=datetime.now(timezone.utc),
        updated=datetime.now(timezone.utc),
        categories=["cs.AI"],
        arxiv_url="https://arxiv.org/abs/2601.00003",
        pdf_url="https://arxiv.org/pdf/2601.00003",
    )

    assert score_papers([paper], config) == []
