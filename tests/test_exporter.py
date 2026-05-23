"""Tests for batchmark.exporter."""

from __future__ import annotations

import csv
import io
import json
import os
import tempfile

import pytest

from batchmark.comparator import ComparisonReport, ComparisonRow
from batchmark.timer import TimingResult
from batchmark.exporter import to_csv_string, to_json_string, save_csv, save_json


def _make_result(name: str, elapsed: float, n: int = 100) -> TimingResult:
    return TimingResult(name=name, elapsed=elapsed, num_items=n)


@pytest.fixture()
def report() -> ComparisonReport:
    r = ComparisonReport()
    r.add(_make_result("fast", 1.0))
    r.add(_make_result("slow", 4.0))
    return r


def test_to_csv_string_has_header(report: ComparisonReport) -> None:
    csv_str = to_csv_string(report)
    reader = csv.DictReader(io.StringIO(csv_str))
    assert reader.fieldnames is not None
    assert "name" in reader.fieldnames
    assert "items_per_second" in reader.fieldnames


def test_to_csv_string_row_count(report: ComparisonReport) -> None:
    csv_str = to_csv_string(report)
    reader = csv.DictReader(io.StringIO(csv_str))
    rows = list(reader)
    assert len(rows) == 2


def test_to_csv_string_empty_report() -> None:
    empty = ComparisonReport()
    assert to_csv_string(empty) == ""


def test_to_json_string_is_list(report: ComparisonReport) -> None:
    json_str = to_json_string(report)
    data = json.loads(json_str)
    assert isinstance(data, list)
    assert len(data) == 2


def test_to_json_string_contains_name(report: ComparisonReport) -> None:
    data = json.loads(to_json_string(report))
    names = {row["name"] for row in data}
    assert "fast" in names
    assert "slow" in names


def test_to_json_string_with_baseline(report: ComparisonReport) -> None:
    data = json.loads(to_json_string(report, baseline="fast"))
    baseline_row = next(r for r in data if r["name"] == "fast")
    slow_row = next(r for r in data if r["name"] == "slow")
    assert baseline_row["relative_speed"] is None
    assert slow_row["relative_speed"] is not None


def test_save_csv_creates_file(report: ComparisonReport) -> None:
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        path = tmp.name
    try:
        save_csv(report, path)
        assert os.path.exists(path)
        with open(path, encoding="utf-8") as fh:
            content = fh.read()
        assert "name" in content
    finally:
        os.unlink(path)


def test_save_json_creates_file(report: ComparisonReport) -> None:
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        path = tmp.name
    try:
        save_json(report, path)
        assert os.path.exists(path)
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        assert isinstance(data, list)
    finally:
        os.unlink(path)
