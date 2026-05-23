"""batchmark — Simple Python utility for benchmarking batch processing pipelines."""

from batchmark.timer import BatchTimer, TimingResult
from batchmark.reporter import BenchmarkReporter
from batchmark.comparator import ComparisonReport, ComparisonRow
from batchmark.runner import run_comparison, print_comparison
from batchmark.formatter import format_table
from batchmark.exporter import to_csv_string, to_json_string, save_csv, save_json
from batchmark.profiler import BatchProfiler, ProfileResult, ProfileSnapshot
from batchmark.profile_reporter import ProfileReporter

__all__ = [
    "BatchTimer",
    "TimingResult",
    "BenchmarkReporter",
    "ComparisonReport",
    "ComparisonRow",
    "run_comparison",
    "print_comparison",
    "format_table",
    "to_csv_string",
    "to_json_string",
    "save_csv",
    "save_json",
    "BatchProfiler",
    "ProfileResult",
    "ProfileSnapshot",
    "ProfileReporter",
]

__version__ = "0.1.0"
