"""batchmark — Simple Python utility for benchmarking batch processing pipelines."""

from batchmark.timer import TimingResult, BatchTimer
from batchmark.reporter import BenchmarkReporter
from batchmark.comparator import ComparisonReport, ComparisonRow
from batchmark.runner import run_comparison, print_comparison
from batchmark.exporter import (
    to_csv_string,
    to_json_string,
    save_csv,
    save_json,
)

__all__ = [
    "TimingResult",
    "BatchTimer",
    "BenchmarkReporter",
    "ComparisonReport",
    "ComparisonRow",
    "run_comparison",
    "print_comparison",
    "to_csv_string",
    "to_json_string",
    "save_csv",
    "save_json",
]
