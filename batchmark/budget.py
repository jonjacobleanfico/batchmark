"""Budget enforcement for batch benchmarks.

Allows defining time and throughput budgets and checking whether
a TimingResult falls within those budgets.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from batchmark.timer import TimingResult


@dataclass
class BudgetViolation:
    """A single budget constraint that was violated."""
    field: str
    limit: float
    actual: float
    message: str

    def to_dict(self) -> dict:
        return {
            "field": self.field,
            "limit": self.limit,
            "actual": self.actual,
            "message": self.message,
        }


@dataclass
class BudgetReport:
    """Result of checking a TimingResult against a BudgetConfig."""
    label: str
    passed: bool
    violations: List[BudgetViolation] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "passed": self.passed,
            "violations": [v.to_dict() for v in self.violations],
        }


@dataclass
class BudgetConfig:
    """Defines budget constraints for a benchmark run.

    Attributes:
        max_elapsed_seconds: Upper bound on total elapsed time.
        min_items_per_second: Lower bound on throughput.
        max_seconds_per_item: Upper bound on per-item latency.
    """
    max_elapsed_seconds: Optional[float] = None
    min_items_per_second: Optional[float] = None
    max_seconds_per_item: Optional[float] = None

    def check(self, result: TimingResult, label: str = "") -> BudgetReport:
        """Check *result* against all configured budget constraints.

        Returns a :class:`BudgetReport` describing whether the result
        passed and any violations that were found.
        """
        violations: List[BudgetViolation] = []

        if self.max_elapsed_seconds is not None:
            if result.elapsed_seconds > self.max_elapsed_seconds:
                violations.append(BudgetViolation(
                    field="elapsed_seconds",
                    limit=self.max_elapsed_seconds,
                    actual=result.elapsed_seconds,
                    message=(
                        f"elapsed {result.elapsed_seconds:.4f}s exceeds "
                        f"budget of {self.max_elapsed_seconds:.4f}s"
                    ),
                ))

        if self.min_items_per_second is not None:
            ips = result.items_per_second()
            if ips < self.min_items_per_second:
                violations.append(BudgetViolation(
                    field="items_per_second",
                    limit=self.min_items_per_second,
                    actual=ips,
                    message=(
                        f"throughput {ips:.4f} items/s is below "
                        f"budget of {self.min_items_per_second:.4f} items/s"
                    ),
                ))

        if self.max_seconds_per_item is not None:
            spi = result.seconds_per_item()
            if spi > self.max_seconds_per_item:
                violations.append(BudgetViolation(
                    field="seconds_per_item",
                    limit=self.max_seconds_per_item,
                    actual=spi,
                    message=(
                        f"latency {spi:.6f}s/item exceeds "
                        f"budget of {self.max_seconds_per_item:.6f}s/item"
                    ),
                ))

        return BudgetReport(
            label=label,
            passed=len(violations) == 0,
            violations=violations,
        )
