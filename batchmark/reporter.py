"""Structured output reporting for benchmark results."""

from __future__ import annotations

import json
import sys
from typing import IO, List, Optional

from batchmark.timer import TimingResult


class BenchmarkReporter:
    """Formats and outputs benchmark results in various structured formats."""

    def __init__(self, output: Optional[IO[str]] = None) -> None:
        self._output = output or sys.stdout
        self._results: List[TimingResult] = []

    def add(self, result: TimingResult) -> None:
        """Register a timing result for reporting."""
        self._results.append(result)

    def clear(self) -> None:
        """Remove all registered results."""
        self._results.clear()

    @property
    def results(self) -> List[TimingResult]:
        return list(self._results)

    def to_json(self, indent: int = 2) -> str:
        """Serialize all results to a JSON string."""
        return json.dumps([r.to_dict() for r in self._results], indent=indent)

    def print_json(self, indent: int = 2) -> None:
        """Write JSON output to the configured output stream."""
        print(self.to_json(indent=indent), file=self._output)

    def print_table(self) -> None:
        """Print a human-readable table of benchmark results."""
        if not self._results:
            print("No results to display.", file=self._output)
            return

        header = f"{'Label':<30} {'Items':>8} {'Elapsed (s)':>12} {'items/s':>10} {'s/item':>10}"
        separator = "-" * len(header)
        print(header, file=self._output)
        print(separator, file=self._output)

        for r in self._results:
            ips = f"{r.items_per_second:.2f}" if r.items_per_second is not None else "N/A"
            spi = f"{r.seconds_per_item:.6f}" if r.seconds_per_item is not None else "N/A"
            label = r.label or "(unlabeled)"
            print(
                f"{label:<30} {r.num_items:>8} {r.elapsed_seconds:>12.4f} {ips:>10} {spi:>10}",
                file=self._output,
            )

    def summary(self) -> dict:
        """Return aggregated summary statistics across all results."""
        if not self._results:
            return {"count": 0}

        total_items = sum(r.num_items for r in self._results)
        total_elapsed = sum(r.elapsed_seconds for r in self._results)
        avg_ips = total_items / total_elapsed if total_elapsed > 0 else None

        return {
            "count": len(self._results),
            "total_items": total_items,
            "total_elapsed_seconds": total_elapsed,
            "average_items_per_second": avg_ips,
        }
