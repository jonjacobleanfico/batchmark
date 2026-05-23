"""Reporter that aggregates ProfileResult objects and serialises them."""

from __future__ import annotations

import json
from typing import List

from batchmark.profiler import ProfileResult


class ProfileReporter:
    """Collects ProfileResult entries and provides output helpers."""

    def __init__(self) -> None:
        self._results: List[ProfileResult] = []

    def add(self, result: ProfileResult) -> None:
        """Append a ProfileResult to the collection."""
        self._results.append(result)

    def clear(self) -> None:
        """Remove all stored results."""
        self._results.clear()

    @property
    def results(self) -> List[ProfileResult]:
        """Return a shallow copy of stored results."""
        return list(self._results)

    def to_dict(self) -> dict:
        """Serialise all results to a dict."""
        return {
            "profile_results": [r.to_dict() for r in self._results],
            "count": len(self._results),
        }

    def to_json(self, indent: int = 2) -> str:
        """Return JSON string representation."""
        return json.dumps(self.to_dict(), indent=indent)

    def print_json(self) -> None:
        """Print JSON to stdout."""
        print(self.to_json())

    def summary(self) -> dict:
        """Return aggregate statistics across all results."""
        if not self._results:
            return {"count": 0}
        elapsed = [r.elapsed_seconds for r in self._results]
        cpu = [r.cpu_total_seconds for r in self._results]
        mem = [r.memory_delta_mb for r in self._results]
        return {
            "count": len(self._results),
            "total_elapsed_seconds": round(sum(elapsed), 6),
            "avg_elapsed_seconds": round(sum(elapsed) / len(elapsed), 6),
            "total_cpu_seconds": round(sum(cpu), 6),
            "avg_memory_delta_mb": round(sum(mem) / len(mem), 4),
        }
