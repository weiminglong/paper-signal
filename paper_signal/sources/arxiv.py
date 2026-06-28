from __future__ import annotations

import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

from paper_signal.models import Paper

ARXIV_API_URL = "https://export.arxiv.org/api/query"
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


def search_arxiv(categories: list[str], max_results: int) -> list[Paper]:
    query = _build_query(categories)
    params = {
        "search_query": query,
        "start": "0",
        "max_results": str(max_results),
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    url = f"{ARXIV_API_URL}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=30) as response:
        body = response.read()
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
