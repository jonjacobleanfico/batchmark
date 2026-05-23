"""Tests for pipeline benchmarking module."""

import pytest
from batchmark.pipeline import StageResult, PipelineResult, PipelineBenchmark, _try_len
from batchmark.timer import TimingResult
from batchmark.pipeline_reporter import PipelineReporter


def _make_stage(name: str = "load", elapsed: float = 1.0, items: int = 10, order: int = 0) -> StageResult:
    timing = TimingResult(elapsed=elapsed, num_items=items)
    return StageResult(stage_name=name, timing=timing, order=order)


def test_stage_result_to_dict_keys():
    stage = _make_stage()
    d = stage.to_dict()
    assert "stage_name" in d
    assert "order" in d
    assert "elapsed" in d
    assert "num_items" in d


def test_pipeline_result_total_elapsed():
    pr = PipelineResult(label="pipe")
    pr.stages.append(_make_stage("a", elapsed=1.5, order=0))
    pr.stages.append(_make_stage("b", elapsed=2.5, order=1))
    assert pr.total_elapsed == pytest.approx(4.0)


def test_pipeline_result_total_items_uses_last_stage():
    pr = PipelineResult(label="pipe")
    pr.stages.append(_make_stage("a", items=100, order=0))
    pr.stages.append(_make_stage("b", items=80, order=1))
    assert pr.total_items == 80


def test_pipeline_result_total_items_empty():
    pr = PipelineResult(label="pipe")
    assert pr.total_items == 0


def test_pipeline_result_stage_names():
    pr = PipelineResult(label="pipe")
    pr.stages.append(_make_stage("load", order=0))
    pr.stages.append(_make_stage("transform", order=1))
    assert pr.stage_names() == ["load", "transform"]


def test_pipeline_result_to_dict_structure():
    pr = PipelineResult(label="pipe")
    pr.stages.append(_make_stage(order=0))
    d = pr.to_dict()
    assert d["label"] == "pipe"
    assert "total_elapsed" in d
    assert "stages" in d
    assert isinstance(d["stages"], list)


def test_pipeline_benchmark_run_executes_stages():
    calls = []

    def stage_a(data):
        calls.append("a")
        return data

    def stage_b(data):
        calls.append("b")
        return data

    bench = PipelineBenchmark(label="test")
    bench.add_stage("a", stage_a).add_stage("b", stage_b)
    result = bench.run([1, 2, 3])
    assert calls == ["a", "b"]
    assert result.label == "test"
    assert len(result.stages) == 2


def test_pipeline_benchmark_stage_order():
    bench = PipelineBenchmark(label="ordered")
    bench.add_stage("first", lambda d: d).add_stage("second", lambda d: d)
    result = bench.run(list(range(5)))
    assert result.stages[0].stage_name == "first"
    assert result.stages[1].stage_name == "second"


def test_try_len_with_list():
    assert _try_len([1, 2, 3]) == 3


def test_try_len_with_non_sized():
    assert _try_len(42) == 0


def test_pipeline_reporter_add_and_results():
    reporter = PipelineReporter()
    bench = PipelineBenchmark(label="r")
    bench.add_stage("s", lambda d: d)
    res = bench.run([1, 2])
    reporter.add(res)
    assert len(reporter.results()) == 1


def test_pipeline_reporter_clear():
    reporter = PipelineReporter()
    bench = PipelineBenchmark(label="r")
    bench.add_stage("s", lambda d: d)
    reporter.add(bench.run([1]))
    reporter.clear()
    assert reporter.results() == []


def test_pipeline_reporter_stage_summary():
    reporter = PipelineReporter()
    bench = PipelineBenchmark(label="r")
    bench.add_stage("load", lambda d: d).add_stage("process", lambda d: d)
    reporter.add(bench.run(list(range(10))))
    reporter.add(bench.run(list(range(10))))
    summary = reporter.stage_summary()
    assert "load" in summary
    assert "process" in summary
    assert isinstance(summary["load"], float)


def test_pipeline_reporter_to_json_valid():
    import json
    reporter = PipelineReporter()
    bench = PipelineBenchmark(label="j")
    bench.add_stage("s", lambda d: d)
    reporter.add(bench.run([1, 2, 3]))
    parsed = json.loads(reporter.to_json())
    assert parsed["count"] == 1
    assert len(parsed["pipelines"]) == 1
