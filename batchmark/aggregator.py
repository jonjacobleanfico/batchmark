"""Aggregation utilities for summarizing multiple TimingResult objects."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, median, stdev
from typing import List, Optional

from batchmark.timer import TimingResult


@dataclass
class AggregateStats:
    """Statistical summary of a collection of TimingResult objects."""

    label: str
    count: int
    total_items: int
    mean_duration: float
    median_duration: float
    stdev_duration: float
    min_duration: float
    max_duration: float
    mean_items_per_second: float

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "count": self.count,
            "total_items": self.total_items,
            "mean_duration_s": round(self.mean_duration, 6),
            "median_duration_s": round(self.median_duration, 6),
            "stdev_duration_s": round(self.stdev_duration, 6),
            "min_duration_s": round(self.min_duration, 6),
            "max_duration_s": round(self.max_duration, 6),
            "mean_items_per_second": round(self.mean_items_per_second, 4),
        }


def aggregate(label: str, results: List[TimingResult]) -> AggregateStats:
    """Compute aggregate statistics from a list of TimingResult objects."""
    if not results:
        raise ValueError("Cannot aggregate an empty list of results.")

    durations = [r.elapsed_seconds for r in results]
    ips_values = [
        r.num_items / r.elapsed_seconds if r.elapsed_seconds > 0 else 0.0
        for r in results
    ]
    std = stdev(durations) if len(durations) > 1 else 0.0

    return AggregateStats(
        label=label,
        count=len(results),
        total_items=sum(r.num_items for r in results),
        mean_duration=mean(durations),
        median_duration=median(durations),
        stdev_duration=std,
        min_duration=min(durations),
        max_duration=max(durations),
        mean_items_per_second=mean(ips_values),
    )
