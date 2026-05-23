"""Threshold checking for benchmark results."""

from dataclasses import dataclass, field
from typing import Optional, List
from batchmark.timer import TimingResult


@dataclass
class ThresholdViolation:
    label: str
    metric: str
    expected: float
    actual: float
    message: str

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "metric": self.metric,
            "expected": self.expected,
            "actual": self.actual,
            "message": self.message,
        }


@dataclass
class ThresholdConfig:
    min_items_per_second: Optional[float] = None
    max_seconds_per_item: Optional[float] = None
    max_total_seconds: Optional[float] = None


@dataclass
class ThresholdReport:
    violations: List[ThresholdViolation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "violation_count": len(self.violations),
            "violations": [v.to_dict() for v in self.violations],
        }


def check_thresholds(
    result: TimingResult,
    config: ThresholdConfig,
    label: str = "",
) -> ThresholdReport:
    """Check a TimingResult against a ThresholdConfig and return a ThresholdReport."""
    violations: List[ThresholdViolation] = []

    ips = result.items_per_second()
    if config.min_items_per_second is not None and ips < config.min_items_per_second:
        violations.append(
            ThresholdViolation(
                label=label,
                metric="items_per_second",
                expected=config.min_items_per_second,
                actual=ips,
                message=(
                    f"items_per_second {ips:.4f} is below minimum "
                    f"{config.min_items_per_second:.4f}"
                ),
            )
        )

    spi = result.seconds_per_item()
    if config.max_seconds_per_item is not None and spi > config.max_seconds_per_item:
        violations.append(
            ThresholdViolation(
                label=label,
                metric="seconds_per_item",
                expected=config.max_seconds_per_item,
                actual=spi,
                message=(
                    f"seconds_per_item {spi:.6f} exceeds maximum "
                    f"{config.max_seconds_per_item:.6f}"
                ),
            )
        )

    if (
        config.max_total_seconds is not None
        and result.elapsed > config.max_total_seconds
    ):
        violations.append(
            ThresholdViolation(
                label=label,
                metric="total_seconds",
                expected=config.max_total_seconds,
                actual=result.elapsed,
                message=(
                    f"total elapsed {result.elapsed:.4f}s exceeds maximum "
                    f"{config.max_total_seconds:.4f}s"
                ),
            )
        )

    return ThresholdReport(violations=violations)
