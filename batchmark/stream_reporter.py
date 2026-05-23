"""Reporter that collects :class:`~batchmark.streamer.StreamResult` objects."""
from __future__ import annotations

import json
from typing import List

from batchmark.streamer import StreamResult


class StreamReporter:
    """Accumulate stream benchmark results and render them."""

    def __init__(self, label: str = "Stream Benchmark") -> None:
        self.label = label
        self._results: list[StreamResult] = []

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def add(self, result: StreamResult) -> None:
        """Append a :class:`StreamResult` to the collection."""
        self._results.append(result)

    def clear(self) -> None:
        """Remove all stored results."""
        self._results.clear()

    # ------------------------------------------------------------------
    # Access
    # ------------------------------------------------------------------

    def results(self) -> List[StreamResult]:
        """Return a shallow copy of collected results."""
        return list(self._results)

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "count": len(self._results),
            "results": [r.to_dict() for r in self._results],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def print_json(self) -> None:
        print(self.to_json())

    # ------------------------------------------------------------------
    # Summary helpers
    # ------------------------------------------------------------------

    def fastest(self) -> StreamResult | None:
        """Return the result with the highest items-per-second rate."""
        if not self._results:
            return None
        return max(self._results, key=lambda r: r.items_per_second())

    def slowest(self) -> StreamResult | None:
        """Return the result with the lowest items-per-second rate."""
        if not self._results:
            return None
        return min(self._results, key=lambda r: r.items_per_second())

    def summary(self) -> dict:
        """High-level summary dict suitable for display."""
        fastest = self.fastest()
        slowest = self.slowest()
        return {
            "label": self.label,
            "total_runs": len(self._results),
            "fastest": fastest.name if fastest else None,
            "slowest": slowest.name if slowest else None,
        }
