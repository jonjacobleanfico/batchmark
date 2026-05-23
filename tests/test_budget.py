"""Tests for batchmark.budget."""
import pytest

from batchmark.timer import TimingResult
from batchmark.budget import BudgetConfig, BudgetReport, BudgetViolation


def _make_result(elapsed: float = 1.0, items: int = 100) -> TimingResult:
    return TimingResult(elapsed_seconds=elapsed, num_items=items)


# ---------------------------------------------------------------------------
# BudgetViolation.to_dict
# ---------------------------------------------------------------------------

def test_budget_violation_to_dict_keys():
    v = BudgetViolation(field="elapsed_seconds", limit=1.0, actual=2.0, message="too slow")
    d = v.to_dict()
    assert set(d.keys()) == {"field", "limit", "actual", "message"}


# ---------------------------------------------------------------------------
# BudgetReport.to_dict
# ---------------------------------------------------------------------------

def test_budget_report_to_dict_structure():
    report = BudgetReport(label="my_run", passed=True)
    d = report.to_dict()
    assert d["label"] == "my_run"
    assert d["passed"] is True
    assert d["violations"] == []


# ---------------------------------------------------------------------------
# BudgetConfig.check — passing cases
# ---------------------------------------------------------------------------

def test_check_passes_when_no_constraints():
    cfg = BudgetConfig()
    report = cfg.check(_make_result(), label="test")
    assert report.passed is True
    assert report.violations == []


def test_check_passes_max_elapsed():
    cfg = BudgetConfig(max_elapsed_seconds=2.0)
    report = cfg.check(_make_result(elapsed=1.0))
    assert report.passed is True


def test_check_passes_min_items_per_second():
    # 100 items / 1.0 s = 100 ips — budget is 50
    cfg = BudgetConfig(min_items_per_second=50.0)
    report = cfg.check(_make_result(elapsed=1.0, items=100))
    assert report.passed is True


def test_check_passes_max_seconds_per_item():
    # 1.0 / 100 = 0.01 s/item — budget is 0.05
    cfg = BudgetConfig(max_seconds_per_item=0.05)
    report = cfg.check(_make_result(elapsed=1.0, items=100))
    assert report.passed is True


# ---------------------------------------------------------------------------
# BudgetConfig.check — failing cases
# ---------------------------------------------------------------------------

def test_check_fails_max_elapsed():
    cfg = BudgetConfig(max_elapsed_seconds=0.5)
    report = cfg.check(_make_result(elapsed=1.0), label="slow")
    assert report.passed is False
    assert len(report.violations) == 1
    assert report.violations[0].field == "elapsed_seconds"
    assert report.label == "slow"


def test_check_fails_min_items_per_second():
    # 10 items / 1.0 s = 10 ips — budget requires 50
    cfg = BudgetConfig(min_items_per_second=50.0)
    report = cfg.check(_make_result(elapsed=1.0, items=10))
    assert report.passed is False
    assert report.violations[0].field == "items_per_second"


def test_check_fails_max_seconds_per_item():
    # 1.0 / 10 = 0.1 s/item — budget is 0.05
    cfg = BudgetConfig(max_seconds_per_item=0.05)
    report = cfg.check(_make_result(elapsed=1.0, items=10))
    assert report.passed is False
    assert report.violations[0].field == "seconds_per_item"


def test_check_multiple_violations():
    cfg = BudgetConfig(
        max_elapsed_seconds=0.5,
        min_items_per_second=200.0,
    )
    report = cfg.check(_make_result(elapsed=1.0, items=10))
    assert report.passed is False
    assert len(report.violations) == 2
    fields = {v.field for v in report.violations}
    assert fields == {"elapsed_seconds", "items_per_second"}


def test_violation_message_is_string():
    cfg = BudgetConfig(max_elapsed_seconds=0.1)
    report = cfg.check(_make_result(elapsed=5.0))
    assert isinstance(report.violations[0].message, str)
    assert len(report.violations[0].message) > 0
