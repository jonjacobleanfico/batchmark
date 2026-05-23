"""High-level runner for executing and comparing multiple batch functions."""

from typing import Any, Callable, Dict, List, Optional

from batchmark.comparator import ComparisonReport
from batchmark.timer import BatchTimer


def run_comparison(
    functions: Dict[str, Callable[[], Any]],
    num_items: int,
    baseline_label: Optional[str] = None,
    warmup: bool = True,
) -> ComparisonReport:
    """
    Run each function and collect timing results into a ComparisonReport.

    Args:
        functions: Mapping of label -> callable (no args). Each callable
                   should process ``num_items`` items internally.
        num_items:  Number of items each function processes (used for rate calc).
        baseline_label: Optional label to use as the comparison baseline.
        warmup: If True, call each function once before timing.

    Returns:
        A populated ComparisonReport.
    """
    report = ComparisonReport(baseline_label=baseline_label)

    for label, fn in functions.items():
        if warmup:
            fn()

        with BatchTimer(num_items=num_items) as timer:
            fn()

        report.add(label, timer.result)

    return report


def print_comparison(
    functions: Dict[str, Callable[[], Any]],
    num_items: int,
    baseline_label: Optional[str] = None,
    warmup: bool = True,
) -> ComparisonReport:
    """
    Run comparison and print a human-readable summary table.

    Returns the underlying ComparisonReport for further inspection.
    """
    report = run_comparison(
        functions=functions,
        num_items=num_items,
        baseline_label=baseline_label,
        warmup=warmup,
    )
    for line in report.summary_lines():
        print(line)
    return report
