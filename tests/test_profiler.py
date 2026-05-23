"""Tests for batchmark.profiler module."""

import time
import pytest
from batchmark.profiler import (
    ProfileSnapshot,
    ProfileResult,
    BatchProfiler,
    _snapshot,
)


def _make_snapshot(ts: float = 0.0, mem: float = 10.0, user: float = 0.1, sys: float = 0.05) -> ProfileSnapshot:
    return ProfileSnapshot(
        timestamp=ts,
        peak_memory_mb=mem,
        cpu_user_seconds=user,
        cpu_system_seconds=sys,
    )


def test_profile_snapshot_to_dict_keys():
    snap = _make_snapshot()
    d = snap.to_dict()
    assert set(d.keys()) == {"timestamp", "peak_memory_mb", "cpu_user_seconds", "cpu_system_seconds"}


def test_profile_result_memory_delta():
    start = _make_snapshot(mem=10.0)
    end = _make_snapshot(mem=14.5)
    result = ProfileResult(label="test", start=start, end=end, elapsed_seconds=1.0)
    assert abs(result.memory_delta_mb - 4.5) < 1e-6


def test_profile_result_cpu_total():
    start = _make_snapshot(user=0.1, sys=0.05)
    end = _make_snapshot(user=0.3, sys=0.1)
    result = ProfileResult(label="test", start=start, end=end, elapsed_seconds=1.0)
    assert abs(result.cpu_total_seconds - 0.25) < 1e-5


def test_profile_result_to_dict_keys():
    start = _make_snapshot()
    end = _make_snapshot()
    result = ProfileResult(label="x", start=start, end=end, elapsed_seconds=0.5)
    d = result.to_dict()
    assert "label" in d
    assert "elapsed_seconds" in d
    assert "memory_delta_mb" in d
    assert "cpu_total_seconds" in d
    assert "start" in d
    assert "end" in d


def test_batch_profiler_context_manager_sets_result():
    with BatchProfiler("my_block") as prof:
        time.sleep(0.01)
    assert prof.result is not None
    assert prof.result.label == "my_block"
    assert prof.result.elapsed_seconds > 0


def test_batch_profiler_elapsed_is_positive():
    with BatchProfiler("timing_check") as prof:
        _ = sum(range(10_000))
    assert prof.result.elapsed_seconds >= 0.0


def test_snapshot_returns_profile_snapshot():
    snap = _snapshot()
    assert isinstance(snap, ProfileSnapshot)
    assert snap.timestamp > 0
    assert snap.peak_memory_mb >= 0


def test_profile_result_to_dict_label():
    start = _make_snapshot()
    end = _make_snapshot()
    result = ProfileResult(label="pipeline_a", start=start, end=end, elapsed_seconds=2.0)
    assert result.to_dict()["label"] == "pipeline_a"
