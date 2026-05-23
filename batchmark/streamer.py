"""Stream-based benchmarking for iterators and generators."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Iterable, Iterator, TypeVar

from batchmark.timer import TimingResult

T = TypeVar("T")


@dataclass
class StreamResult:
    """Timing result for a streamed / lazy pipeline."""

    name: str
    total_items: int
    elapsed_seconds: float
    chunk_times: list[float] = field(default_factory=list)

    # --- derived metrics ---

    def items_per_second(self) -> float:
        if self.elapsed_seconds == 0:
            return 0.0
        return self.total_items / self.elapsed_seconds

    def seconds_per_item(self) -> float:
        if self.total_items == 0:
            return 0.0
        return self.elapsed_seconds / self.total_items

    def avg_chunk_time(self) -> float:
        if not self.chunk_times:
            return 0.0
        return sum(self.chunk_times) / len(self.chunk_times)

    def to_timing_result(self) -> TimingResult:
        """Convert to a standard TimingResult for use with existing reporters."""
        from batchmark.timer import TimingResult  # local to avoid circular

        return TimingResult(
            name=self.name,
            total_items=self.total_items,
            elapsed_seconds=self.elapsed_seconds,
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "total_items": self.total_items,
            "elapsed_seconds": round(self.elapsed_seconds, 6),
            "items_per_second": round(self.items_per_second(), 4),
            "seconds_per_item": round(self.seconds_per_item(), 6),
            "avg_chunk_time": round(self.avg_chunk_time(), 6),
            "chunks": len(self.chunk_times),
        }


def benchmark_stream(
    name: str,
    source: Iterable[T],
    process: Callable[[T], object] | None = None,
) -> StreamResult:
    """Consume *source*, optionally applying *process* to each item, and
    return a :class:`StreamResult` with per-chunk timing.

    Each item emitted by *source* counts as one chunk.
    """
    chunk_times: list[float] = []
    total_items = 0
    wall_start = time.perf_counter()

    for item in source:
        t0 = time.perf_counter()
        if process is not None:
            process(item)
        chunk_times.append(time.perf_counter() - t0)
        total_items += 1

    elapsed = time.perf_counter() - wall_start
    return StreamResult(
        name=name,
        total_items=total_items,
        elapsed_seconds=elapsed,
        chunk_times=chunk_times,
    )


def benchmark_stream_batched(
    name: str,
    source: Iterable[list[T]],
    process: Callable[[list[T]], object] | None = None,
) -> StreamResult:
    """Like :func:`benchmark_stream` but *source* yields *batches* (lists).
    ``total_items`` reflects the sum of all batch sizes.
    """
    chunk_times: list[float] = []
    total_items = 0
    wall_start = time.perf_counter()

    for batch in source:
        t0 = time.perf_counter()
        if process is not None:
            process(batch)
        chunk_times.append(time.perf_counter() - t0)
        total_items += len(batch)

    elapsed = time.perf_counter() - wall_start
    return StreamResult(
        name=name,
        total_items=total_items,
        elapsed_seconds=elapsed,
        chunk_times=chunk_times,
    )
