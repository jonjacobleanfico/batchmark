"""Timer utilities for measuring batch processing durations."""

import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TimingResult:
    """Holds the result of a timed operation."""

    label: str
    elapsed_seconds: float
    items_processed: int
    start_time: float
    end_time: float
    metadata: dict = field(default_factory=dict)

    @property
    def items_per_second(self) -> float:
        """Throughput in items per second."""
        if self.elapsed_seconds == 0:
            return float("inf")
        return self.items_processed / self.elapsed_seconds

    @property
    def seconds_per_item(self) -> float:
        """Average time per item in seconds."""
        if self.items_processed == 0:
            return float("inf")
        return self.elapsed_seconds / self.items_processed

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "elapsed_seconds": round(self.elapsed_seconds, 6),
            "items_processed": self.items_processed,
            "items_per_second": round(self.items_per_second, 4),
            "seconds_per_item": round(self.seconds_per_item, 6),
            "metadata": self.metadata,
        }


class BatchTimer:
    """Context manager for timing batch processing operations."""

    def __init__(self, label: str, items_processed: int = 0, metadata: Optional[dict] = None):
        self.label = label
        self.items_processed = items_processed
        self.metadata = metadata or {}
        self._start: float = 0.0
        self._end: float = 0.0
        self.result: Optional[TimingResult] = None

    def __enter__(self) -> "BatchTimer":
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self._end = time.perf_counter()
        self.result = TimingResult(
            label=self.label,
            elapsed_seconds=self._end - self._start,
            items_processed=self.items_processed,
            start_time=self._start,
            end_time=self._end,
            metadata=self.metadata,
        )
        return False

    def set_items(self, count: int) -> None:
        """Update item count after the context block if not known upfront."""
        self.items_processed = count
        if self.result is not None:
            self.result.items_processed = count
