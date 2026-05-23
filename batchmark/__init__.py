"""batchmark — Simple utility for benchmarking batch processing pipelines."""

from batchmark.reporter import BenchmarkReporter
from batchmark.timer import BatchTimer, TimingResult

__all__ = [
    "BatchTimer",
    "TimingResult",
    "BenchmarkReporter",
]

__version__ = "0.1.0"
