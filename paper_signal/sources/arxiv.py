from __future__ import annotations

import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from math import ceil
from time import sleep

from paper_signal.models import Paper

ARXIV_API_URL = "https://export.arxiv.org/api/query"
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
# arXiv asks API clients to identify themselves and rate-limits anonymous bursts.
USER_AGENT = "PaperSignal/0.2 (+https://github.com/weiminglong/paper-signal)"
RETRY_DELAY_SECONDS = 5.0


def search_arxiv(categories: list[str], max_results: int) -> list[Paper]:
    categories = categories or ["cs.AI"]
    per_category_limit = max(1, ceil(max_results / len(categories)))
    papers_by_id: dict[str, Paper] = {}

    for index, category in enumerate(categories):
        papers = _search_arxiv_query(
            query=_build_query([category]),
            max_results=per_category_limit,
        )
        for paper in papers:
            papers_by_id.setdefault(paper.paper_id, paper)
        if index < len(categories) - 1:
            sleep(0.5)

    return sorted(
        papers_by_id.values(),
        key=lambda paper: paper.published,
        reverse=True,
    )[:max_results]


def search_arxiv_by_keywords(keywords: list[str], max_results: int) -> list[Paper]:
    """Server-side keyword search (arXiv `all:` fields), OR-joined.

    Complements the category-recency fetch: for thin-coverage fields (e.g. digital
    humanities) the relevant papers are scattered across big categories, so asking
    arXiv to match the user's own keywords finds work a small recency window misses.
    """
    # Strip embedded quotes (they would corrupt the query string) and quote every
    # term unconditionally — valid for single words too, and neutralizes bare
    # AND/OR/colon tokens inside a phrase.
    cleaned = [" ".join(kw.replace('"', " ").split()) for kw in keywords]
    cleaned = [kw for kw in cleaned if kw]
    if not cleaned:
        return []
    sleep(0.5)  # politeness gap after the category queries
    terms = [f'all:"{kw}"' for kw in cleaned]
    return _search_arxiv_query(query=" OR ".join(terms), max_results=max_results)


def _search_arxiv_query(query: str, max_results: int) -> list[Paper]:
    params = {
        "search_query": query,
        "start": "0",
        "max_results": str(max_results),
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    url = f"{ARXIV_API_URL}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    body = b""
    for attempt in (1, 2):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read()
            break
        except urllib.error.HTTPError as exc:
            # Rate-limited or briefly unavailable: back off once, then give up.
            if attempt == 1 and exc.code in (429, 503):
                sleep(RETRY_DELAY_SECONDS)
                continue
            raise
    return parse_arxiv_feed(body)


def parse_arxiv_feed(feed: bytes) -> list[Paper]:
    root = ET.fromstring(feed)
    papers: list[Paper] = []
    for entry in root.findall("atom:entry", ATOM_NS):
        paper_id = _paper_id(entry.findtext("atom:id", default="", namespaces=ATOM_NS))
        title = _clean_text(entry.findtext("atom:title", default="", namespaces=ATOM_NS))
        abstract = _clean_text(entry.findtext("atom:summary", default="", namespaces=ATOM_NS))
        published = _parse_datetime(
            entry.findtext("atom:published", default="", namespaces=ATOM_NS)
        )
        updated = _parse_datetime(entry.findtext("atom:updated", default="", namespaces=ATOM_NS))
        authors = [
            _clean_text(author.findtext("atom:name", default="", namespaces=ATOM_NS))
            for author in entry.findall("atom:author", ATOM_NS)
        ]
        categories = [
            category.attrib.get("term", "")
            for category in entry.findall("atom:category", ATOM_NS)
            if category.attrib.get("term")
        ]
        arxiv_url = f"https://arxiv.org/abs/{paper_id}"
        pdf_url = f"https://arxiv.org/pdf/{paper_id}"
        papers.append(
            Paper(
                paper_id=paper_id,
                title=title,
                authors=authors,
                abstract=abstract,
                published=published,
                updated=updated,
                categories=categories,
                arxiv_url=arxiv_url,
                pdf_url=pdf_url,
            )
        )
    return papers


def _build_query(categories: list[str]) -> str:
    if not categories:
        return "cat:cs.AI"
    return " OR ".join(f"cat:{category}" for category in categories)


def _paper_id(url: str) -> str:
    return url.rstrip("/").split("/")[-1]


def _clean_text(value: str) -> str:
    return " ".join(value.split())


def _parse_datetime(value: str) -> datetime:
    if not value:
        return datetime.fromtimestamp(0)
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
