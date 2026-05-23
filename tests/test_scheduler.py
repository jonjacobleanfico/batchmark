"""Tests for batchmark.scheduler."""

import pytest

from batchmark.scheduler import ScheduleReport, ScheduledRun, run_scheduled
from batchmark.timer import TimingResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_run(index: int = 0, elapsed: float = 1.0, items: int = 100) -> ScheduledRun:
    result = TimingResult(elapsed_seconds=elapsed, num_items=items)
    return ScheduledRun(run_index=index, timestamp=1000.0 + index, result=result)


def _noop(n: int) -> None:
    pass


# ---------------------------------------------------------------------------
# ScheduledRun
# ---------------------------------------------------------------------------

def test_scheduled_run_to_dict_keys():
    run = _make_run()
    d = run.to_dict()
    assert set(d.keys()) == {"run_index", "timestamp", "result"}


def test_scheduled_run_result_nested():
    run = _make_run(elapsed=2.0, items=50)
    d = run.to_dict()
    assert "elapsed_seconds" in d["result"]
    assert d["result"]["num_items"] == 50


# ---------------------------------------------------------------------------
# ScheduleReport
# ---------------------------------------------------------------------------

def test_schedule_report_total_runs_empty():
    report = ScheduleReport(label="test")
    assert report.total_runs() == 0


def test_schedule_report_total_runs():
    report = ScheduleReport(label="test", runs=[_make_run(i) for i in range(3)])
    assert report.total_runs() == 3


def test_schedule_report_avg_items_per_second_empty():
    report = ScheduleReport(label="test")
    assert report.avg_items_per_second() == 0.0


def test_schedule_report_avg_items_per_second():
    runs = [
        _make_run(0, elapsed=1.0, items=100),  # 100 ips
        _make_run(1, elapsed=2.0, items=100),  # 50 ips
    ]
    report = ScheduleReport(label="test", runs=runs)
    assert report.avg_items_per_second() == pytest.approx(75.0)


def test_schedule_report_to_dict_keys():
    report = ScheduleReport(label="demo", runs=[_make_run()])
    d = report.to_dict()
    assert set(d.keys()) == {"label", "total_runs", "avg_items_per_second", "runs"}


# ---------------------------------------------------------------------------
# run_scheduled
# ---------------------------------------------------------------------------

def test_run_scheduled_correct_run_count():
    report = run_scheduled(_noop, num_items=10, runs=4, label="x")
    assert report.total_runs() == 4


def test_run_scheduled_label_preserved():
    report = run_scheduled(_noop, num_items=5, runs=2, label="my_label")
    assert report.label == "my_label"


def test_run_scheduled_run_indices():
    report = run_scheduled(_noop, num_items=5, runs=3)
    indices = [r.run_index for r in report.runs]
    assert indices == [0, 1, 2]


def test_run_scheduled_on_run_callback():
    seen = []
    run_scheduled(_noop, num_items=5, runs=3, on_run=lambda r: seen.append(r.run_index))
    assert seen == [0, 1, 2]


def test_run_scheduled_items_recorded():
    report = run_scheduled(_noop, num_items=42, runs=2)
    for run in report.runs:
        assert run.result.num_items == 42
