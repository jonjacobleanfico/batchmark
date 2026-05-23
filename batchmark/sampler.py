"""Sampler module for collecting periodic timing samples during batch runs."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Sample:
    """A single timing sample captured at a point in time."""

    timestamp: float
    items_processed: int
    elapsed_seconds: float

    def instantaneous_rate(self) -> float:
        """Items per second at this sample point."""
        if self.elapsed_seconds <= 0:
            return 0.0
        return self.items_processed / self.elapsed_seconds

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "items_processed": self.items_processed,
            "elapsed_seconds": self.elapsed_seconds,
            "instantaneous_rate": self.instantaneous_rate(),
        }


@dataclass
class SampleSeries:
    """A labeled collection of samples from a single benchmark run."""

    label: str
    samples: List[Sample] = field(default_factory=list)

    def add(self, items_processed: int, elapsed_seconds: float) -> None:
        self.samples.append(
            Sample(
                timestamp=time.time(),
                items_processed=items_processed,
                elapsed_seconds=elapsed_seconds,
            )
        )

    def peak_rate(self) -> Optional[float]:
        if not self.samples:
            return None
        return max(s.instantaneous_rate() for s in self.samples)

    def average_rate(self) -> Optional[float]:
        if not self.samples:
            return None
        rates = [s.instantaneous_rate() for s in self.samples]
        return sum(rates) / len(rates)

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "sample_count": len(self.samples),
            "peak_rate": self.peak_rate(),
            "average_rate": self.average_rate(),
            "samples": [s.to_dict() for s in self.samples],
        }
