"""Tests for batchmark.aggregate_reporter."""

import json
import pytest

from batchmark.timer import TimingResult
from batchmark.aggregate_reporter import AggregateReporter


def _make_result(elapsed: float, items: int = 100) -> TimingResult:
    return TimingResult(elapsed_seconds=elapsed, num_items=items)


def test_add_and_labels():
    reporter = AggregateReporter()
    reporter.add("alpha", _make_result(1.0))
    reporter.add("beta", _make_result(2.0))
    assert set(reporter.labels()) == {"alpha", "beta"}


def test_results_for_returns_copy():
    reporter = AggregateReporter()
    reporter.add("alpha", _make_result(1.0))
    copy = reporter.results_for("alpha")
    copy.clear()
    assert len(reporter.results_for("alpha")) == 1


def test_results_for_missing_label_returns_empty():
    reporter = AggregateReporter()
    assert reporter.results_for("missing") == []


def test_summary_aggregates_correctly():
    reporter = AggregateReporter()
    reporter.add("x", _make_result(1.0, items=100))
    reporter.add("x", _make_result(3.0, items=100))
    stats = reporter.summary("x")
    assert stats.count == 2
    assert stats.mean_duration == pytest.approx(2.0)


def test_summary_missing_label_raises():
    reporter = AggregateReporter()
    with pytest.raises(KeyError):
        reporter.summary("nonexistent")


def test_all_summaries_length():
    reporter = AggregateReporter()
    reporter.add("a", _make_result(1.0))
    reporter.add("b", _make_result(2.0))
    reporter.add("b", _make_result(3.0))
    summaries = reporter.all_summaries()
    assert len(summaries) == 2


def test_clear_removes_all():
    reporter = AggregateReporter()
    reporter.add("a", _make_result(1.0))
    reporter.clear()
    assert reporter.labels() == []


def test_to_dict_structure():
    reporter = AggregateReporter()
    reporter.add("run", _make_result(1.0))
    d = reporter.to_dict()
    assert "summaries" in d
    assert isinstance(d["summaries"], list)
    assert len(d["summaries"]) == 1


def test_to_json_valid():
    reporter = AggregateReporter()
    reporter.add("run", _make_result(1.0))
    parsed = json.loads(reporter.to_json())
    assert "summaries" in parsed


def test_to_json_empty_reporter():
    reporter = AggregateReporter()
    parsed = json.loads(reporter.to_json())
    assert parsed["summaries"] == []
