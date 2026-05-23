"""Tests for batchmark.profile_reporter module."""

import json
import pytest
from batchmark.profiler import ProfileResult, ProfileSnapshot
from batchmark.profile_reporter import ProfileReporter


def _make_result(
    label: str = "op",
    elapsed: float = 1.0,
    mem_start: float = 10.0,
    mem_end: float = 12.0,
) -> ProfileResult:
    start = ProfileSnapshot(timestamp=0.0, peak_memory_mb=mem_start, cpu_user_seconds=0.1, cpu_system_seconds=0.05)
    end = ProfileSnapshot(timestamp=elapsed, peak_memory_mb=mem_end, cpu_user_seconds=0.2, cpu_system_seconds=0.08)
    return ProfileResult(label=label, start=start, end=end, elapsed_seconds=elapsed)


def test_reporter_add_and_results():
    reporter = ProfileReporter()
    r = _make_result("a")
    reporter.add(r)
    assert len(reporter.results) == 1
    assert reporter.results[0].label == "a"


def test_reporter_clear():
    reporter = ProfileReporter()
    reporter.add(_make_result())
    reporter.clear()
    assert reporter.results == []


def test_reporter_to_dict_structure():
    reporter = ProfileReporter()
    reporter.add(_make_result("x"))
    d = reporter.to_dict()
    assert "profile_results" in d
    assert d["count"] == 1
    assert d["profile_results"][0]["label"] == "x"


def test_reporter_to_json_valid():
    reporter = ProfileReporter()
    reporter.add(_make_result())
    raw = reporter.to_json()
    parsed = json.loads(raw)
    assert "profile_results" in parsed


def test_reporter_summary_empty():
    reporter = ProfileReporter()
    s = reporter.summary()
    assert s == {"count": 0}


def test_reporter_summary_values():
    reporter = ProfileReporter()
    reporter.add(_make_result(elapsed=2.0, mem_start=10.0, mem_end=14.0))
    reporter.add(_make_result(elapsed=4.0, mem_start=10.0, mem_end=16.0))
    s = reporter.summary()
    assert s["count"] == 2
    assert abs(s["total_elapsed_seconds"] - 6.0) < 1e-5
    assert abs(s["avg_elapsed_seconds"] - 3.0) < 1e-5
    assert abs(s["avg_memory_delta_mb"] - 5.0) < 1e-4


def test_reporter_results_is_copy():
    reporter = ProfileReporter()
    reporter.add(_make_result())
    copy = reporter.results
    copy.clear()
    assert len(reporter.results) == 1
