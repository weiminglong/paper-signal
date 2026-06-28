from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from paper_signal.models import AppConfig, DailySettings, ResearchDomain


class ConfigError(ValueError):
    """Raised when a PaperSignal config is invalid."""


def load_config(path: str | Path) -> AppConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(f"Config file not found: {config_path}")

    raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    language = str(raw.get("language", "en"))
    vault_path = str(raw.get("vault_path") or os.environ.get("OBSIDIAN_VAULT_PATH", ""))

    daily_raw = raw.get("daily") or {}
    daily = DailySettings(
        candidate_limit=int(daily_raw.get("candidate_limit", 100)),
        recommendation_count=int(daily_raw.get("recommendation_count", 10)),
        deep_analysis_count=int(daily_raw.get("deep_analysis_count", 3)),
        skip_seen=bool(daily_raw.get("skip_seen", True)),
    )

    sources = raw.get("sources") or {}
    arxiv = sources.get("arxiv") or {}
    arxiv_categories = list(arxiv.get("categories") or [])

    domains = _parse_domains(raw.get("research_domains") or {})
    if not domains:
        raise ConfigError("At least one research domain is required")

    if not arxiv_categories:
        arxiv_categories = sorted(
            {
                category
                for domain in domains
                for category in domain.arxiv_categories
            }
        )

    return AppConfig(
        language=language,
        vault_path=vault_path,
        daily=daily,
        arxiv_categories=arxiv_categories,
        research_domains=domains,
        excluded_keywords=list(raw.get("excluded_keywords") or []),
    )


def _parse_domains(raw_domains: dict[str, Any]) -> list[ResearchDomain]:
    domains: list[ResearchDomain] = []
    for name, raw_domain in raw_domains.items():
        raw_domain = raw_domain or {}
        domains.append(
            ResearchDomain(
                name=str(name),
                priority=int(raw_domain.get("priority", 1)),
                keywords=[str(item) for item in raw_domain.get("keywords", [])],
                arxiv_categories=[
                    str(item) for item in raw_domain.get("arxiv_categories", [])
                ],
            )
        )
    return domains
