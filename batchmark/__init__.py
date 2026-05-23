"""batchmark — Simple Python utility for benchmarking batch processing pipelines."""

from batchmark.timer import BatchTimer, TimingResult
from batchmark.reporter import BenchmarkReporter
from batchmark.comparator import ComparisonReport, ComparisonRow
from batchmark.runner import run_comparison, print_comparison

__all__ = [
    "BatchTimer",
    "TimingResult",
    "BenchmarkReporter",
    "ComparisonReport",
    "ComparisonRow",
    "run_comparison",
    "print_comparison",
]

__version__ = "0.2.0"
