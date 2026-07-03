from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class StateError(RuntimeError):
    """Raised when the dedup state file exists but cannot be read."""


@dataclass
class PaperSignalState:
    seen_paper_ids: set[str] = field(default_factory=set)
    # One entry per selected paper: {"paper_id", "title", "score", "date", "run"}.
    # Powers `paper-signal history` and `unsee --last-run`.
    history: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> "PaperSignalState":
        if not path.exists():
            return cls()
        try:
            raw: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
            # Older state files carry only the flat id list; history is optional.
            return cls(
                seen_paper_ids=set(raw.get("seen_paper_ids", [])),
                history=list(raw.get("history", [])),
            )
        except (ValueError, TypeError, AttributeError) as exc:
            raise StateError(
                f"State file is corrupt: {path}. Move it aside (e.g. rename to "
                "state.json.bak) to reset — note this forgets seen papers and history."
            ) from exc

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "seen_paper_ids": sorted(self.seen_paper_ids),
            "history": self.history,
        }
        # Atomic write: a crash mid-save must never leave a truncated state file.
        tmp_path = path.with_name(path.name + ".tmp")
        tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        os.replace(tmp_path, path)

    def record(self, entries: list[dict[str, Any]]) -> None:
        """Mark papers seen AND remember what/when for history and unsee."""
        already = {entry.get("paper_id") for entry in self.history}
        for entry in entries:
            paper_id = entry.get("paper_id")
            if not paper_id:
                continue
            self.seen_paper_ids.add(paper_id)
            if paper_id not in already:
                self.history.append(entry)
                already.add(paper_id)

    def unsee(self, paper_ids: list[str]) -> int:
        """Forget papers so they can be recommended again. Returns how many were removed."""
        targets = set(paper_ids)
        removed = len(self.seen_paper_ids & targets)
        self.seen_paper_ids -= targets
        self.history = [e for e in self.history if e.get("paper_id") not in targets]
        return removed

    def last_run_marker(self) -> str | None:
        """Most recent run marker. Entries carry a per-run `run` timestamp; legacy
        entries fall back to their date, so old state still resolves sensibly."""
        markers = [_marker(e) for e in self.history if _marker(e)]
        return max(markers) if markers else None

    def ids_for_marker(self, marker: str) -> list[str]:
        return [e["paper_id"] for e in self.history if _marker(e) == marker]


def _marker(entry: dict[str, Any]) -> str:
    return str(entry.get("run") or entry.get("date") or "")
