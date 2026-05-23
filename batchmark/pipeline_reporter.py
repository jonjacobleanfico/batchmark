"""Reporter for collecting and summarising PipelineResult objects."""

import json
from typing import Dict, List
from batchmark.pipeline import PipelineResult


class PipelineReporter:
    """Collect multiple PipelineResult instances and produce reports."""

    def __init__(self) -> None:
        self._results: List[PipelineResult] = []

    def add(self, result: PipelineResult) -> None:
        """Add a PipelineResult to the reporter."""
        self._results.append(result)

    def clear(self) -> None:
        """Remove all stored results."""
        self._results.clear()

    def results(self) -> List[PipelineResult]:
        """Return a shallow copy of stored results."""
        return list(self._results)

    def to_dict(self) -> Dict:
        return {
            "count": len(self._results),
            "pipelines": [r.to_dict() for r in self._results],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def print_json(self, indent: int = 2) -> None:  # pragma: no cover
        print(self.to_json(indent=indent))

    def stage_summary(self) -> Dict[str, Dict[str, float]]:
        """Return average elapsed time per stage name across all runs."""
        totals: Dict[str, float] = {}
        counts: Dict[str, int] = {}
        for pr in self._results:
            for stage in pr.stages:
                totals[stage.stage_name] = totals.get(stage.stage_name, 0.0) + stage.timing.elapsed
                counts[stage.stage_name] = counts.get(stage.stage_name, 0) + 1
        return {
            name: totals[name] / counts[name]
            for name in totals
        }
