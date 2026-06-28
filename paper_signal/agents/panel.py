from __future__ import annotations

from paper_signal.models import ScoredPaper


def add_panel_discussion(scored_papers: list[ScoredPaper]) -> list[ScoredPaper]:
    for item in scored_papers:
        item.panel = {
            "relevance_agent": _relevance_view(item),
            "method_agent": _method_view(item),
            "skeptic_agent": _skeptic_view(item),
            "knowledge_base_agent": _knowledge_base_view(item),
            "moderator": _moderator_view(item),
        }
    return scored_papers


def _relevance_view(item: ScoredPaper) -> str:
    domains = ", ".join(item.matched_domains) or "configured interests"
    keywords = ", ".join(item.matched_keywords[:5]) or "no explicit keywords"
    return f"Matches {domains}; strongest keyword signals: {keywords}."


def _method_view(item: ScoredPaper) -> str:
    abstract = item.paper.abstract.lower()
    if any(term in abstract for term in ["benchmark", "state-of-the-art", "outperform"]):
        return "Likely includes empirical comparisons; inspect baselines and datasets."
    if any(term in abstract for term in ["framework", "architecture", "algorithm"]):
        return "Likely method-centric; inspect the core mechanism and assumptions."
    return "Method contribution is unclear from the abstract; skim before deep reading."


def _skeptic_view(item: ScoredPaper) -> str:
    abstract = item.paper.abstract.lower()
    if "survey" in abstract:
        return "Survey paper; useful for orientation but may not require deep note generation."
    if not any(term in abstract for term in ["experiment", "evaluation", "result", "benchmark"]):
        return "Evaluation signal is weak in the abstract; check rigor before prioritizing."
    return "Potentially worth reading, but verify whether claims are supported by strong baselines."


def _knowledge_base_view(item: ScoredPaper) -> str:
    if item.matched_keywords:
        return "Use matched keywords as Obsidian links to connect this paper to existing notes."
    return "No obvious link targets found yet; tag conservatively."


def _moderator_view(item: ScoredPaper) -> str:
    if item.score >= 10:
        return "Priority read."
    if item.score >= 6:
        return "Worth skimming."
    return "Keep only if the title looks strategically relevant."
