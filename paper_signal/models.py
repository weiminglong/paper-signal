from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class ResearchDomain:
    name: str
    priority: int
    keywords: list[str]
    arxiv_categories: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DailySettings:
    candidate_limit: int = 100
    recommendation_count: int = 10
    deep_analysis_count: int = 3
    skip_seen: bool = True


@dataclass(frozen=True)
class AppConfig:
    language: str
    vault_path: str
    daily: DailySettings
    arxiv_categories: list[str]
    research_domains: list[ResearchDomain]
    excluded_keywords: list[str]
    # Also query arXiv server-side with the domains' keywords (all: fields), so
    # thin-coverage fields aren't limited to a small per-category recency window.
    arxiv_keyword_search: bool = True


@dataclass
class Paper:
    paper_id: str
    title: str
    authors: list[str]
    abstract: str
    published: datetime
    updated: datetime
    categories: list[str]
    arxiv_url: str
    pdf_url: str


@dataclass
class ScoredPaper:
    paper: Paper
    score: float
    matched_domains: list[str]
    matched_keywords: list[str]
    reasons: list[str]
    panel: dict[str, str] = field(default_factory=dict)
