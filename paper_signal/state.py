from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class PaperSignalState:
    seen_paper_ids: set[str] = field(default_factory=set)

    @classmethod
    def load(cls, path: Path) -> "PaperSignalState":
        if not path.exists():
            return cls()
        raw: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        return cls(seen_paper_ids=set(raw.get("seen_paper_ids", [])))

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"seen_paper_ids": sorted(self.seen_paper_ids)}
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def mark_seen(self, paper_ids: list[str]) -> None:
        self.seen_paper_ids.update(paper_ids)
