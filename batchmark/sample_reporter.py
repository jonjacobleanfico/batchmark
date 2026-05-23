"""Reporter for managing multiple SampleSeries across labeled benchmark runs."""

from __future__ import annotations

import json
from typing import Dict, List, Optional

from batchmark.sampler import SampleSeries


class SampleReporter:
    """Collects and reports SampleSeries grouped by label."""

    def __init__(self) -> None:
        self._series: Dict[str, SampleSeries] = {}

    def get_or_create(self, label: str) -> SampleSeries:
        """Return existing series for label, or create a new one."""
        if label not in self._series:
            self._series[label] = SampleSeries(label=label)
        return self._series[label]

    def add_series(self, series: SampleSeries) -> None:
        """Register a completed SampleSeries."""
        self._series[series.label] = series

    def labels(self) -> List[str]:
        """Return all registered labels."""
        return list(self._series.keys())

    def series_for(self, label: str) -> Optional[SampleSeries]:
        """Return the SampleSeries for a label, or None if not found."""
        return self._series.get(label)

    def clear(self) -> None:
        """Remove all stored series."""
        self._series.clear()

    def to_dict(self) -> dict:
        return {
            "series": [s.to_dict() for s in self._series.values()]
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def print_json(self, indent: int = 2) -> None:
        print(self.to_json(indent=indent))
