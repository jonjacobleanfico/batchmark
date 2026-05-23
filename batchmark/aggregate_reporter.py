"""Reporter that collects TimingResults per label and produces aggregate summaries."""

from __future__ import annotations

import json
from collections import defaultdict
from typing import Dict, List, Optional

from batchmark.timer import TimingResult
from batchmark.aggregator import AggregateStats, aggregate


class AggregateReporter:
    """Accumulates TimingResult objects grouped by label and summarises them."""

    def __init__(self) -> None:
        self._buckets: Dict[str, List[TimingResult]] = defaultdict(list)

    def add(self, label: str, result: TimingResult) -> None:
        """Add a TimingResult under the given label."""
        self._buckets[label].append(result)

    def labels(self) -> List[str]:
        """Return all labels that have at least one result."""
        return list(self._buckets.keys())

    def results_for(self, label: str) -> List[TimingResult]:
        """Return raw results for a specific label."""
        return list(self._buckets.get(label, []))

    def summary(self, label: str) -> AggregateStats:
        """Return aggregate statistics for a single label."""
        if label not in self._buckets:
            raise KeyError(f"No results recorded for label: {label!r}")
        return aggregate(label, self._buckets[label])

    def all_summaries(self) -> List[AggregateStats]:
        """Return aggregate statistics for every label."""
        return [aggregate(label, runs) for label, runs in self._buckets.items()]

    def clear(self) -> None:
        """Remove all recorded results."""
        self._buckets.clear()

    def to_dict(self) -> dict:
        return {"summaries": [s.to_dict() for s in self.all_summaries()]}

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def print_json(self, indent: int = 2) -> None:  # pragma: no cover
        print(self.to_json(indent=indent))
