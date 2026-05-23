"""Memory and CPU profiling utilities for batch benchmarks."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Optional

try:
    import resource
    _HAS_RESOURCE = True
except ImportError:
    _HAS_RESOURCE = False


@dataclass
class ProfileSnapshot:
    """A snapshot of resource usage at a point in time."""

    timestamp: float
    peak_memory_mb: float
    cpu_user_seconds: float
    cpu_system_seconds: float

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "peak_memory_mb": round(self.peak_memory_mb, 4),
            "cpu_user_seconds": round(self.cpu_user_seconds, 6),
            "cpu_system_seconds": round(self.cpu_system_seconds, 6),
        }


@dataclass
class ProfileResult:
    """Resource usage delta between start and end of a profiled block."""

    label: str
    start: ProfileSnapshot
    end: ProfileSnapshot
    elapsed_seconds: float

    @property
    def memory_delta_mb(self) -> float:
        return self.end.peak_memory_mb - self.start.peak_memory_mb

    @property
    def cpu_total_seconds(self) -> float:
        user = self.end.cpu_user_seconds - self.start.cpu_user_seconds
        system = self.end.cpu_system_seconds - self.start.cpu_system_seconds
        return round(user + system, 6)

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "elapsed_seconds": round(self.elapsed_seconds, 6),
            "memory_delta_mb": round(self.memory_delta_mb, 4),
            "cpu_total_seconds": self.cpu_total_seconds,
            "start": self.start.to_dict(),
            "end": self.end.to_dict(),
        }


def _snapshot() -> ProfileSnapshot:
    """Capture current resource usage."""
    ts = time.perf_counter()
    if _HAS_RESOURCE:
        usage = resource.getrusage(resource.RUSAGE_SELF)
        peak_mb = usage.ru_maxrss / 1024.0
        user_s = usage.ru_utime
        sys_s = usage.ru_stime
    else:
        peak_mb = 0.0
        user_s = 0.0
        sys_s = 0.0
    return ProfileSnapshot(
        timestamp=ts,
        peak_memory_mb=peak_mb,
        cpu_user_seconds=user_s,
        cpu_system_seconds=sys_s,
    )


class BatchProfiler:
    """Context manager that captures resource usage around a block."""

    def __init__(self, label: str) -> None:
        self.label = label
        self._start: Optional[ProfileSnapshot] = None
        self.result: Optional[ProfileResult] = None

    def __enter__(self) -> "BatchProfiler":
        self._start = _snapshot()
        return self

    def __exit__(self, *args) -> None:
        end = _snapshot()
        assert self._start is not None
        elapsed = end.timestamp - self._start.timestamp
        self.result = ProfileResult(
            label=self.label,
            start=self._start,
            end=end,
            elapsed_seconds=elapsed,
        )
