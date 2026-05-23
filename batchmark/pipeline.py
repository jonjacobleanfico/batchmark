"""Pipeline stage benchmarking for multi-step batch processing."""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from batchmark.timer import BatchTimer, TimingResult


@dataclass
class StageResult:
    """Timing result for a single pipeline stage."""

    stage_name: str
    timing: TimingResult
    order: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage_name": self.stage_name,
            "order": self.order,
            **self.timing.to_dict(),
        }


@dataclass
class PipelineResult:
    """Aggregated result for a full pipeline run."""

    label: str
    stages: List[StageResult] = field(default_factory=list)

    @property
    def total_elapsed(self) -> float:
        return sum(s.timing.elapsed for s in self.stages)

    @property
    def total_items(self) -> int:
        return self.stages[-1].timing.num_items if self.stages else 0

    def stage_names(self) -> List[str]:
        return [s.stage_name for s in self.stages]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "label": self.label,
            "total_elapsed": self.total_elapsed,
            "total_items": self.total_items,
            "stages": [s.to_dict() for s in self.stages],
        }


class PipelineBenchmark:
    """Benchmark a sequence of named pipeline stages."""

    def __init__(self, label: str) -> None:
        self.label = label
        self._stages: List[tuple] = []  # (name, callable)

    def add_stage(self, name: str, fn: Callable[[Any], Any]) -> "PipelineBenchmark":
        """Register a stage function. Returns self for chaining."""
        self._stages.append((name, fn))
        return self

    def run(self, data: Any, num_items: Optional[int] = None) -> PipelineResult:
        """Execute all stages in order, timing each one."""
        result = PipelineResult(label=self.label)
        current = data
        for order, (name, fn) in enumerate(self._stages):
            items = num_items if num_items is not None else _try_len(current)
            with BatchTimer(num_items=items) as t:
                current = fn(current)
            result.stages.append(StageResult(stage_name=name, timing=t.result, order=order))
        return result


def _try_len(obj: Any) -> int:
    try:
        return len(obj)
    except TypeError:
        return 0
