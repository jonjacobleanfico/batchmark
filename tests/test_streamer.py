"""Tests for batchmark.streamer."""
from __future__ import annotations

import time

import pytest

from batchmark.streamer import (
    StreamResult,
    benchmark_stream,
    benchmark_stream_batched,
)


# ---------------------------------------------------------------------------
# StreamResult unit tests
# ---------------------------------------------------------------------------

def _make_result(
    total_items: int = 100,
    elapsed: float = 2.0,
    chunk_times: list[float] | None = None,
) -> StreamResult:
    return StreamResult(
        name="test",
        total_items=total_items,
        elapsed_seconds=elapsed,
        chunk_times=chunk_times or [0.01] * total_items,
    )


def test_stream_result_items_per_second():
    r = _make_result(total_items=50, elapsed=5.0)
    assert r.items_per_second() == pytest.approx(10.0)


def test_stream_result_seconds_per_item():
    r = _make_result(total_items=4, elapsed=2.0)
    assert r.seconds_per_item() == pytest.approx(0.5)


def test_stream_result_zero_items():
    r = _make_result(total_items=0, elapsed=1.0, chunk_times=[])
    assert r.items_per_second() == 0.0
    assert r.seconds_per_item() == 0.0


def test_stream_result_avg_chunk_time():
    r = StreamResult(name="x", total_items=3, elapsed_seconds=0.3, chunk_times=[0.1, 0.2, 0.3])
    assert r.avg_chunk_time() == pytest.approx(0.2)


def test_stream_result_avg_chunk_time_empty():
    r = StreamResult(name="x", total_items=0, elapsed_seconds=0.0, chunk_times=[])
    assert r.avg_chunk_time() == 0.0


def test_stream_result_to_dict_keys():
    r = _make_result()
    d = r.to_dict()
    for key in ("name", "total_items", "elapsed_seconds", "items_per_second",
                "seconds_per_item", "avg_chunk_time", "chunks"):
        assert key in d


def test_stream_result_to_dict_values_consistent():
    """Ensure to_dict values match the corresponding method return values."""
    r = _make_result(total_items=20, elapsed=4.0)
    d = r.to_dict()
    assert d["items_per_second"] == pytest.approx(r.items_per_second())
    assert d["seconds_per_item"] == pytest.approx(r.seconds_per_item())
    assert d["avg_chunk_time"] == pytest.approx(r.avg_chunk_time())
    assert d["total_items"] == r.total_items
    assert d["elapsed_seconds"] == pytest.approx(r.elapsed_seconds)


def test_stream_result_to_timing_result():
    r = _make_result(total_items=20, elapsed=4.0)
    tr = r.to_timing_result()
    assert tr.name == r.name
    assert tr.total_items == r.total_items
    assert tr.elapsed_seconds == pytest.approx(r.elapsed_seconds)


# ---------------------------------------------------------------------------
# benchmark_stream
# ---------------------------------------------------------------------------

def test_benchmark_stream_item_count():
    result = benchmark_stream("gen", range(30))
    assert result.total_items == 30
    assert result.name == "gen"


def test_benchmark_stream_with_process():
    acc: list[int] = []
    result = benchmark_stream("proc", range(10), process=acc.append)
    assert result.total_items == 10
    assert acc == list(range(10))


def test_benchmark_stream_chunk_count_matches_items():
    result = benchmark_stream("chunks", range(7))
    assert len(result.chunk_times) == 7


def test_benchmark_stream_elapsed_positive():
    result = benchmark_stream("elapsed", range(5))
    assert result.elapsed_seconds >= 0.0


# ---------------------------------------------------------------------------
# benchmark_stream_batched
# ---------
