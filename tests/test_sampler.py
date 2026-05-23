"""Tests for batchmark.sampler module."""

import time
import pytest
from batchmark.sampler import Sample, SampleSeries


def _make_sample(items: int = 100, elapsed: float = 1.0) -> Sample:
    return Sample(timestamp=time.time(), items_processed=items, elapsed_seconds=elapsed)


def test_sample_instantaneous_rate_normal():
    s = _make_sample(items=200, elapsed=2.0)
    assert s.instantaneous_rate() == pytest.approx(100.0)


def test_sample_instantaneous_rate_zero_elapsed():
    s = _make_sample(items=50, elapsed=0.0)
    assert s.instantaneous_rate() == 0.0


def test_sample_to_dict_keys():
    s = _make_sample()
    d = s.to_dict()
    assert "timestamp" in d
    assert "items_processed" in d
    assert "elapsed_seconds" in d
    assert "instantaneous_rate" in d


def test_sample_series_add_increases_count():
    series = SampleSeries(label="test")
    series.add(items_processed=10, elapsed_seconds=1.0)
    series.add(items_processed=20, elapsed_seconds=2.0)
    assert len(series.samples) == 2


def test_sample_series_peak_rate_empty():
    series = SampleSeries(label="empty")
    assert series.peak_rate() is None


def test_sample_series_average_rate_empty():
    series = SampleSeries(label="empty")
    assert series.average_rate() is None


def test_sample_series_peak_rate():
    series = SampleSeries(label="peaktest")
    series.add(items_processed=100, elapsed_seconds=1.0)  # rate=100
    series.add(items_processed=50, elapsed_seconds=1.0)   # rate=50
    assert series.peak_rate() == pytest.approx(100.0)


def test_sample_series_average_rate():
    series = SampleSeries(label="avgtest")
    series.add(items_processed=100, elapsed_seconds=1.0)  # rate=100
    series.add(items_processed=200, elapsed_seconds=1.0)  # rate=200
    assert series.average_rate() == pytest.approx(150.0)


def test_sample_series_to_dict_structure():
    series = SampleSeries(label="myrun")
    series.add(items_processed=10, elapsed_seconds=0.5)
    d = series.to_dict()
    assert d["label"] == "myrun"
    assert d["sample_count"] == 1
    assert "peak_rate" in d
    assert "average_rate" in d
    assert isinstance(d["samples"], list)
    assert len(d["samples"]) == 1


def test_sample_series_to_dict_sample_contents():
    series = SampleSeries(label="check")
    series.add(items_processed=80, elapsed_seconds=2.0)
    sample_dict = series.to_dict()["samples"][0]
    assert sample_dict["items_processed"] == 80
    assert sample_dict["elapsed_seconds"] == pytest.approx(2.0)
    assert sample_dict["instantaneous_rate"] == pytest.approx(40.0)
