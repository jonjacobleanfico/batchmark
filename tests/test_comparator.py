"""Tests for batchmark.comparator module."""

import pytest
from batchmark.timer import TimingResult
from batchmark.comparator import ComparisonRow, ComparisonReport


def _make_result(num_items: int, elapsed: float) -> TimingResult:
    return TimingResult(num_items=num_items, elapsed=elapsed)


def test_comparison_row_to_dict_keys():
    row = ComparisonRow(
        label="fast",
        items_per_second=1000.0,
        seconds_per_item=0.001,
        total_time=1.0,
        num_items=1000,
        relative_speed=1.0,
    )
    d = row.to_dict()
    assert set(d.keys()) == {"label", "items_per_second", "seconds_per_item", "total_time", "num_items", "relative_speed"}


def test_comparison_report_add_and_rows():
    report = ComparisonReport()
    report.add("method_a", _make_result(100, 1.0))
    report.add("method_b", _make_result(100, 0.5))
    assert len(report.rows) == 2
    assert report.rows[0].label == "method_a"
    assert report.rows[1].label == "method_b"


def test_compute_relative_speeds_no_baseline():
    report = ComparisonReport()
    report.add("slow", _make_result(100, 2.0))
    report.add("fast", _make_result(100, 1.0))
    report.compute_relative_speeds()
    fast_row = next(r for r in report.rows if r.label == "fast")
    slow_row = next(r for r in report.rows if r.label == "slow")
    assert fast_row.relative_speed == pytest.approx(1.0)
    assert slow_row.relative_speed == pytest.approx(0.5)


def test_compute_relative_speeds_with_baseline():
    report = ComparisonReport(baseline_label="baseline")
    report.add("baseline", _make_result(100, 2.0))
    report.add("faster", _make_result(100, 1.0))
    report.compute_relative_speeds()
    baseline_row = next(r for r in report.rows if r.label == "baseline")
    faster_row = next(r for r in report.rows if r.label == "faster")
    assert baseline_row.relative_speed == pytest.approx(1.0)
    assert faster_row.relative_speed == pytest.approx(2.0)


def test_compute_relative_speeds_missing_baseline_raises():
    """Ensure a KeyError or ValueError is raised when the baseline label is not found."""
    report = ComparisonReport(baseline_label="nonexistent")
    report.add("method_a", _make_result(100, 1.0))
    with pytest.raises((KeyError, ValueError)):
        report.compute_relative_speeds()


def test_to_dict_structure():
    report = ComparisonReport()
    report.add("a", _make_result(50, 0.5))
    d = report.to_dict()
    assert "rows" in d
    assert "baseline" in d
    assert len(d["rows"]) == 1


def test_summary_lines_format():
    report = ComparisonReport()
    report.add("alpha", _make_result(200, 2.0))
    report.add("beta", _make_result(200, 1.0))
    lines = report.summary_lines()
    assert len(lines) >= 4  # header + separator + 2 rows
    assert "alpha" in lines[2]
    assert "beta" in lines[3]


def test_empty_report_to_dict():
    report = ComparisonReport()
    d = report.to_dict()
    assert d["rows"] == []
