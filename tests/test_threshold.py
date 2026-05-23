"""Tests for batchmark.threshold."""

import pytest
from batchmark.timer import TimingResult
from batchmark.threshold import (
    ThresholdConfig,
    ThresholdReport,
    ThresholdViolation,
    check_thresholds,
)


def _make_result(items: int = 100, elapsed: float = 1.0) -> TimingResult:
    return TimingResult(items=items, elapsed=elapsed)


def test_check_thresholds_passes_when_no_constraints():
    result = _make_result()
    config = ThresholdConfig()
    report = check_thresholds(result, config, label="test")
    assert report.passed is True
    assert len(report.violations) == 0


def test_check_thresholds_fails_min_items_per_second():
    result = _make_result(items=10, elapsed=1.0)  # 10 ips
    config = ThresholdConfig(min_items_per_second=50.0)
    report = check_thresholds(result, config, label="slow")
    assert report.passed is False
    assert any(v.metric == "items_per_second" for v in report.violations)


def test_check_thresholds_passes_min_items_per_second():
    result = _make_result(items=200, elapsed=1.0)  # 200 ips
    config = ThresholdConfig(min_items_per_second=100.0)
    report = check_thresholds(result, config)
    assert report.passed is True


def test_check_thresholds_fails_max_seconds_per_item():
    result = _make_result(items=1, elapsed=2.0)  # 2 spi
    config = ThresholdConfig(max_seconds_per_item=0.5)
    report = check_thresholds(result, config, label="sluggish")
    assert report.passed is False
    assert any(v.metric == "seconds_per_item" for v in report.violations)


def test_check_thresholds_fails_max_total_seconds():
    result = _make_result(items=100, elapsed=10.0)
    config = ThresholdConfig(max_total_seconds=5.0)
    report = check_thresholds(result, config, label="long")
    assert report.passed is False
    assert any(v.metric == "total_seconds" for v in report.violations)


def test_check_thresholds_multiple_violations():
    result = _make_result(items=1, elapsed=20.0)
    config = ThresholdConfig(
        min_items_per_second=100.0,
        max_seconds_per_item=0.01,
        max_total_seconds=5.0,
    )
    report = check_thresholds(result, config, label="bad")
    assert not report.passed
    assert len(report.violations) == 3


def test_violation_to_dict_keys():
    v = ThresholdViolation(
        label="x",
        metric="items_per_second",
        expected=100.0,
        actual=50.0,
        message="too slow",
    )
    d = v.to_dict()
    assert set(d.keys()) == {"label", "metric", "expected", "actual", "message"}


def test_threshold_report_to_dict_structure():
    result = _make_result(items=5, elapsed=1.0)
    config = ThresholdConfig(min_items_per_second=100.0)
    report = check_thresholds(result, config, label="r")
    d = report.to_dict()
    assert "passed" in d
    assert "violation_count" in d
    assert "violations" in d
    assert isinstance(d["violations"], list)
    assert d["violation_count"] == 1
    assert d["passed"] is False
