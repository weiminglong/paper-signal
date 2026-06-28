from __future__ import annotations

from datetime import datetime, timezone

from paper_signal.models import AppConfig, Paper, ScoredPaper


def score_papers(papers: list[Paper], config: AppConfig) -> list[ScoredPaper]:
    scored = [score_paper(paper, config) for paper in papers]
    filtered = [item for item in scored if item.score > 0 and not _is_excluded(item.paper, config)]
    return sorted(filtered, key=lambda item: item.score, reverse=True)


def score_paper(paper: Paper, config: AppConfig) -> ScoredPaper:
    text = f"{paper.title}\n{paper.abstract}".lower()
    matched_domains: list[str] = []
    matched_keywords: set[str] = set()
    reasons: list[str] = []
    score = 0.0

    for domain in config.research_domains:
        domain_score = 0.0
        for keyword in domain.keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in paper.title.lower():
                domain_score += 1.2
                matched_keywords.add(keyword)
            elif keyword_lower in text:
                domain_score += 0.7
                matched_keywords.add(keyword)

        category_matches = set(domain.arxiv_categories).intersection(paper.categories)
        if category_matches:
            domain_score += 0.5 * len(category_matches)

        if domain_score > 0:
            matched_domains.append(domain.name)
            weighted = domain_score * max(domain.priority, 1)
            score += weighted
            reasons.append(f"{domain.name}: {weighted:.1f} relevance points")

    days_old = _days_old(paper)
    if days_old <= 7:
        score += 2.0
        reasons.append("very recent")
    elif days_old <= 30:
        score += 1.2
        reasons.append("recent")
    elif days_old <= 90:
        score += 0.5
        reasons.append("fresh enough")

    return ScoredPaper(
        paper=paper,
        score=round(score, 2),
        matched_domains=matched_domains,
        matched_keywords=sorted(matched_keywords),
        reasons=reasons,
    )


def _is_excluded(paper: Paper, config: AppConfig) -> bool:
    text = f"{paper.title}\n{paper.abstract}".lower()
    return any(keyword.lower() in text for keyword in config.excluded_keywords)


def _days_old(paper: Paper) -> int:
    now = datetime.now(timezone.utc)
    published = paper.published
    if published.tzinfo is None:
        published = published.replace(tzinfo=timezone.utc)
    return max((now - published).days, 0)
