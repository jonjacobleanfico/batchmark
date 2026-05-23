"""Tests for BenchmarkReporter."""

from __future__ import annotations

import io
import json

import pytest

from batchmark.reporter import BenchmarkReporter
from batchmark.timer import TimingResult


def _make_result(label: str, num_items: int, elapsed: float) -> TimingResult:
    return TimingResult(label=label, num_items=num_items, elapsed_seconds=elapsed)


def test_reporter_add_and_results():
    reporter = BenchmarkReporter()
    r = _make_result("batch_a", 100, 2.0)
    reporter.add(r)
    assert len(reporter.results) == 1
    assert reporter.results[0].label == "batch_a"


def test_reporter_clear():
    reporter = BenchmarkReporter()
    reporter.add(_make_result("x", 10, 1.0))
    reporter.clear()
    assert reporter.results == []


def test_reporter_to_json_structure():
    reporter = BenchmarkReporter()
    reporter.add(_make_result("run1", 50, 1.0))
    reporter.add(_make_result("run2", 200, 4.0))
    data = json.loads(reporter.to_json())
    assert len(data) == 2
    assert data[0]["label"] == "run1"
    assert data[1]["num_items"] == 200


def test_reporter_print_json_output():
    buf = io.StringIO()
    reporter = BenchmarkReporter(output=buf)
    reporter.add(_make_result("run1", 10, 0.5))
    reporter.print_json()
    output = buf.getvalue()
    parsed = json.loads(output)
    assert parsed[0]["label"] == "run1"


def test_reporter_print_table_contains_label():
    buf = io.StringIO()
    reporter = BenchmarkReporter(output=buf)
    reporter.add(_make_result("my_pipeline", 300, 3.0))
    reporter.print_table()
    output = buf.getvalue()
    assert "my_pipeline" in output
    assert "300" in output


def test_reporter_print_table_empty():
    buf = io.StringIO()
    reporter = BenchmarkReporter(output=buf)
    reporter.print_table()
    assert "No results" in buf.getvalue()


def test_reporter_summary():
    reporter = BenchmarkReporter()
    reporter.add(_make_result("a", 100, 2.0))
    reporter.add(_make_result("b", 200, 2.0))
    s = reporter.summary()
    assert s["count"] == 2
    assert s["total_items"] == 300
    assert s["total_elapsed_seconds"] == pytest.approx(4.0)
    assert s["average_items_per_second"] == pytest.approx(75.0)


def test_reporter_summary_empty():
    reporter = BenchmarkReporter()
    assert reporter.summary() == {"count": 0}
