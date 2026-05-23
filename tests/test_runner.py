"""Tests for batchmark.runner module."""

import time
from batchmark.runner import run_comparison, print_comparison
from batchmark.comparator import ComparisonReport


def _noop():
    """Fast no-op batch function."""
    pass


def _slow():
    """Slightly slower batch function."""
    time.sleep(0.01)


def test_run_comparison_returns_report():
    report = run_comparison({"noop": _noop}, num_items=10, warmup=False)
    assert isinstance(report, ComparisonReport)
    assert len(report.rows) == 1
    assert report.rows[0].label == "noop"


def test_run_comparison_multiple_functions():
    fns = {"a": _noop, "b": _noop}
    report = run_comparison(fns, num_items=50, warmup=False)
    assert len(report.rows) == 2
    labels = [r.label for r in report.rows]
    assert "a" in labels
    assert "b" in labels


def test_run_comparison_items_recorded():
    report = run_comparison({"fn": _noop}, num_items=42, warmup=False)
    assert report.rows[0].num_items == 42


def test_run_comparison_with_baseline():
    fns = {"fast": _noop, "slow": _slow}
    report = run_comparison(fns, num_items=1, baseline_label="fast", warmup=False)
    assert report.baseline_label == "fast"
    report.compute_relative_speeds()
    fast_row = next(r for r in report.rows if r.label == "fast")
    assert fast_row.relative_speed == 1.0


def test_run_comparison_warmup_does_not_crash():
    called = []

    def fn():
        called.append(1)

    run_comparison({"fn": fn}, num_items=1, warmup=True)
    # warmup + timed call = 2 invocations
    assert len(called) == 2


def test_print_comparison_returns_report(capsys):
    report = print_comparison({"x": _noop}, num_items=5, warmup=False)
    assert isinstance(report, ComparisonReport)
    captured = capsys.readouterr()
    assert "x" in captured.out
