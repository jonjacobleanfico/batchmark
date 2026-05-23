"""Scheduled benchmark runner with interval-based sampling."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from batchmark.timer import BatchTimer, TimingResult


@dataclass
class ScheduledRun:
    """Result of a single scheduled benchmark execution."""

    run_index: int
    timestamp: float
    result: TimingResult

    def to_dict(self) -> dict:
        return {
            "run_index": self.run_index,
            "timestamp": self.timestamp,
            "result": self.result.to_dict(),
        }


@dataclass
class ScheduleReport:
    """Aggregated results from a scheduled benchmark session."""

    label: str
    runs: List[ScheduledRun] = field(default_factory=list)

    def total_runs(self) -> int:
        return len(self.runs)

    def avg_items_per_second(self) -> float:
        if not self.runs:
            return 0.0
        return sum(r.result.items_per_second() for r in self.runs) / len(self.runs)

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "total_runs": self.total_runs(),
            "avg_items_per_second": self.avg_items_per_second(),
            "runs": [r.to_dict() for r in self.runs],
        }


def run_scheduled(
    fn: Callable[[int], None],
    num_items: int,
    runs: int,
    interval_seconds: float = 0.0,
    label: str = "scheduled",
    on_run: Optional[Callable[[ScheduledRun], None]] = None,
) -> ScheduleReport:
    """Run *fn* a fixed number of times, optionally pausing between runs.

    Args:
        fn: Callable that accepts the batch size and performs the work.
        num_items: Number of items passed to *fn* on each invocation.
        runs: How many times to invoke *fn*.
        interval_seconds: Seconds to sleep between runs (default 0).
        label: Human-readable label for the report.
        on_run: Optional callback invoked after each run with the ScheduledRun.

    Returns:
        A :class:`ScheduleReport` containing all individual run results.
    """
    report = ScheduleReport(label=label)

    for i in range(runs):
        with BatchTimer() as timer:
            fn(num_items)
        result = timer.result(num_items)
        scheduled_run = ScheduledRun(
            run_index=i,
            timestamp=time.time(),
            result=result,
        )
        report.runs.append(scheduled_run)

        if on_run is not None:
            on_run(scheduled_run)

        if interval_seconds > 0 and i < runs - 1:
            time.sleep(interval_seconds)

    return report
