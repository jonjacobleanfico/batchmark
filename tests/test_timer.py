"""Tests for batchmark.timer module."""

import time
import pytest
from batchmark.timer import BatchTimer, TimingResult


def test_timing_result_items_per_second():
    result = TimingResult(
        label="test",
        elapsed_seconds=2.0,
        items_processed=100,
        start_time=0.0,
        end_time=2.0,
    )
    assert result.items_per_second == 50.0


def test_timing_result_seconds_per_item():
    result = TimingResult(
        label="test",
        elapsed_seconds=1.0,
        items_processed=4,
        start_time=0.0,
        end_time=1.0,
    )
    assert result.seconds_per_item == 0.25


def test_timing_result_zero_items():
    result = TimingResult(
        label="test",
        elapsed_seconds=1.0,
        items_processed=0,
        start_time=0.0,
        end_time=1.0,
    )
    assert result.seconds_per_item == float("inf")


def test_timing_result_to_dict_keys():
    result = TimingResult(
        label="pipeline",
        elapsed_seconds=0.5,
        items_processed=10,
        start_time=0.0,
        end_time=0.5,
        metadata={"batch_size": 10},
    )
    d = result.to_dict()
    assert d["label"] == "pipeline"
    assert d["items_processed"] == 10
    assert d["metadata"] == {"batch_size": 10}
    assert "elapsed_seconds" in d
    assert "items_per_second" in d


def test_batch_timer_context_manager():
    with BatchTimer("sleep_test", items_processed=5) as t:
        time.sleep(0.05)

    assert t.result is not None
    assert t.result.elapsed_seconds >= 0.04
    assert t.result.items_processed == 5
    assert t.result.label == "sleep_test"


def test_batch_timer_set_items_after_run():
    with BatchTimer("dynamic") as t:
        time.sleep(0.01)
    t.set_items(42)

    assert t.result.items_processed == 42
    assert t.items_processed == 42


def test_batch_timer_does_not_suppress_exceptions():
    with pytest.raises(ValueError):
        with BatchTimer("error_case", items_processed=1):
            raise ValueError("intentional error")
