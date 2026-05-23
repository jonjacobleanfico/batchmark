"""Utilities for comparing multiple benchmark results side by side."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from batchmark.timer import TimingResult


@dataclass
class ComparisonRow:
    """A single row in a benchmark comparison table."""

    label: str
    items_per_second: float
    seconds_per_item: float
    total_time: float
    num_items: int
    relative_speed: Optional[float] = None  # ratio vs baseline

    def to_dict(self) -> Dict:
        return {
            "label": self.label,
            "items_per_second": round(self.items_per_second, 4),
            "seconds_per_item": round(self.seconds_per_item, 6),
            "total_time": round(self.total_time, 6),
            "num_items": self.num_items,
            "relative_speed": round(self.relative_speed, 4) if self.relative_speed is not None else None,
        }


@dataclass
class ComparisonReport:
    """Holds comparison data for multiple benchmark runs."""

    rows: List[ComparisonRow] = field(default_factory=list)
    baseline_label: Optional[str] = None

    def add(self, label: str, result: TimingResult) -> None:
        """Add a named timing result to the comparison."""
        row = ComparisonRow(
            label=label,
            items_per_second=result.items_per_second,
            seconds_per_item=result.seconds_per_item,
            total_time=result.elapsed,
            num_items=result.num_items,
        )
        self.rows.append(row)

    def compute_relative_speeds(self) -> None:
        """Compute relative speed of each row vs the baseline (or fastest)."""
        if not self.rows:
            return

        if self.baseline_label:
            baseline = next((r for r in self.rows if r.label == self.baseline_label), None)
        else:
            baseline = max(self.rows, key=lambda r: r.items_per_second)

        if baseline is None or baseline.items_per_second == 0:
            return

        for row in self.rows:
            row.relative_speed = row.items_per_second / baseline.items_per_second

    def to_dict(self) -> Dict:
        self.compute_relative_speeds()
        return {
            "baseline": self.baseline_label,
            "rows": [r.to_dict() for r in self.rows],
        }

    def summary_lines(self) -> List[str]:
        """Return a list of human-readable summary lines."""
        self.compute_relative_speeds()
        lines = []
        header = f"{'Label':<20} {'items/s':>12} {'s/item':>12} {'total(s)':>10} {'rel':>8}"
        lines.append(header)
        lines.append("-" * len(header))
        for row in self.rows:
            rel = f"{row.relative_speed:.3f}x" if row.relative_speed is not None else "N/A"
            lines.append(
                f"{row.label:<20} {row.items_per_second:>12.2f} "
                f"{row.seconds_per_item:>12.6f} {row.total_time:>10.4f} {rel:>8}"
            )
        return lines
