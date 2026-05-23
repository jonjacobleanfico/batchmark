"""Tests for batchmark.stream_reporter."""
from __future__ import annotations

import json

import pytest

from batchmark.streamer import StreamResult
from batchmark.stream_reporter import StreamReporter


def _make_result(name: str = "run", items: int = 100, elapsed: float = 1.0) -> StreamResult:
    return StreamResult(
        name=name,
        total_items=items,
        elapsed_seconds=elapsed,
        chunk_times=[elapsed / items] * items if items else [],
    )


# ---------------------------------------------------------------------------
# Basic CRUD
# ---------------------------------------------------------------------------

def test_reporter_add_and_results():
    rep = StreamReporter()
    r = _make_result("a")
    rep.add(r)
    assert len(rep.results()) == 1
    assert rep.results()[0].name == "a"


def test_reporter_results_is_copy():
    rep = StreamReporter()
    rep.add(_make_result("a"))
    copy = rep.results()
    copy.append(_make_result("b"))
    assert len(rep.results()) == 1  # original unaffected


def test_reporter_clear():
    rep = StreamReporter()
    rep.add(_make_result())
    rep.clear()
    assert rep.results() == []


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------

def test_reporter_to_dict_structure():
    rep = StreamReporter(label="MyPipeline")
    rep.add(_make_result("x", 50, 0.5))
    d = rep.to_dict()
    assert d["label"] == "MyPipeline"
    assert d["count"] == 1
    assert isinstance(d["results"], list)


def test_reporter_to_json_valid():
    rep = StreamReporter()
    rep.add(_make_result("j", 10, 0.1))
    parsed = json.loads(rep.to_json())
    assert "results" in parsed
    assert parsed["count"] == 1


# ---------------------------------------------------------------------------
# Summary helpers
# ---------------------------------------------------------------------------

def test_reporter_fastest_empty():
    rep = StreamReporter()
    assert rep.fastest() is None


def test_reporter_slowest_empty():
    rep = StreamReporter()
    assert rep.slowest() is None


def test_reporter_fastest_and_slowest():
    rep = StreamReporter()
    # fast: 100 items/s, slow: 10 items/s
    rep.add(_make_result("fast", items=100, elapsed=1.0))
    rep.add(_make_result("slow", items=10, elapsed=1.0))
    assert rep.fastest().name == "fast"
    assert rep.slowest().name == "slow"


def test_reporter_summary_keys():
    rep = StreamReporter(label="S")
    rep.add(_make_result("a"))
    s = rep.summary()
    for key in ("label", "total_runs", "fastest", "slowest"):
        assert key in s
    assert s["total_runs"] == 1
