"""Tests for batchmark.aggregator."""

import pytest

from batchmark.timer import TimingResult
from batchmark.aggregator import AggregateStats, aggregate


def _make_result(elapsed: float, items: int = 100) -> TimingResult:
    return TimingResult(elapsed_seconds=elapsed, num_items=items)


def test_aggregate_returns_aggregate_stats():
    results = [_make_result(1.0), _make_result(2.0), _make_result(3.0)]
    stats = aggregate("test", results)
    assert isinstance(stats, AggregateStats)


def test_aggregate_label():
    results = [_make_result(1.0)]
    stats = aggregate("my_label", results)
    assert stats.label == "my_label"


def test_aggregate_count():
    results = [_make_result(1.0), _make_result(2.0)]
    stats = aggregate("x", results)
    assert stats.count == 2


def test_aggregate_total_items():
    results = [_make_result(1.0, items=50), _make_result(2.0, items=75)]
    stats = aggregate("x", results)
    assert stats.total_items == 125


def test_aggregate_mean_duration():
    results = [_make_result(1.0), _make_result(3.0)]
    stats = aggregate("x", results)
    assert stats.mean_duration == pytest.approx(2.0)


def test_aggregate_median_duration():
    results = [_make_result(1.0), _make_result(2.0), _make_result(9.0)]
    stats = aggregate("x", results)
    assert stats.median_duration == pytest.approx(2.0)


def test_aggregate_min_max_duration():
    results = [_make_result(0.5), _make_result(1.5), _make_result(3.0)]
    stats = aggregate("x", results)
    assert stats.min_duration == pytest.approx(0.5)
    assert stats.max_duration == pytest.approx(3.0)


def test_aggregate_stdev_single_result_is_zero():
    results = [_make_result(2.0)]
    stats = aggregate("x", results)
    assert stats.stdev_duration == pytest.approx(0.0)


def test_aggregate_mean_items_per_second():
    results = [_make_result(1.0, items=100), _make_result(2.0, items=100)]
    stats = aggregate("x", results)
    # 100/1.0=100, 100/2.0=50 -> mean=75
    assert stats.mean_items_per_second == pytest.approx(75.0)


def test_aggregate_empty_raises():
    with pytest.raises(ValueError, match="empty"):
        aggregate("x", [])


def test_aggregate_to_dict_keys():
    results = [_make_result(1.0), _make_result(2.0)]
    d = aggregate("x", results).to_dict()
    expected_keys = {
        "label", "count", "total_items", "mean_duration_s",
        "median_duration_s", "stdev_duration_s", "min_duration_s",
        "max_duration_s", "mean_items_per_second",
    }
    assert expected_keys == set(d.keys())
