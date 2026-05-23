"""Reporter that collects multiple ScheduleReport instances."""

from __future__ import annotations

import json
from typing import Dict, List, Optional

from batchmark.scheduler import ScheduleReport


class ScheduleReporter:
    """Accumulates :class:`~batchmark.scheduler.ScheduleReport` objects
    keyed by label and exposes summary utilities.
    """

    def __init__(self) -> None:
        self._reports: Dict[str, ScheduleReport] = {}

    def add(self, report: ScheduleReport) -> None:
        """Store *report* under its label, overwriting any previous entry."""
        self._reports[report.label] = report

    def labels(self) -> List[str]:
        """Return the labels of all stored reports."""
        return list(self._reports.keys())

    def get(self, label: str) -> Optional[ScheduleReport]:
        """Return the report for *label*, or ``None`` if not found."""
        return self._reports.get(label)

    def clear(self) -> None:
        """Remove all stored reports."""
        self._reports.clear()

    def summary(self) -> List[dict]:
        """Return a list of summary dicts (one per label), sorted by label."""
        return [
            {
                "label": label,
                "total_runs": report.total_runs(),
                "avg_items_per_second": report.avg_items_per_second(),
            }
            for label, report in sorted(self._reports.items())
        ]

    def to_dict(self) -> dict:
        return {
            "reports": {label: r.to_dict() for label, r in self._reports.items()}
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialise all reports to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def print_summary(self) -> None:
        """Print a compact human-readable summary to stdout."""
        for row in self.summary():
            print(
                f"{row['label']}: runs={row['total_runs']}, "
                f"avg_ips={row['avg_items_per_second']:.2f}"
            )
