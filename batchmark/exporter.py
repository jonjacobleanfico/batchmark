"""Export benchmark results to various file formats (CSV, JSON)."""

from __future__ import annotations

import csv
import json
import io
from typing import List, Optional

from batchmark.comparator import ComparisonReport


def to_csv_string(report: ComparisonReport, baseline: Optional[str] = None) -> str:
    """Render a ComparisonReport as a CSV string."""
    rows = report.compute_relative_speeds(baseline=baseline)
    if not rows:
        return ""

    fieldnames = list(rows[0].to_dict().keys())
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row.to_dict())
    return buf.getvalue()


def to_json_string(report: ComparisonReport, baseline: Optional[str] = None, indent: int = 2) -> str:
    """Render a ComparisonReport as a JSON string."""
    rows = report.compute_relative_speeds(baseline=baseline)
    payload = [row.to_dict() for row in rows]
    return json.dumps(payload, indent=indent)


def save_csv(
    report: ComparisonReport,
    path: str,
    baseline: Optional[str] = None,
) -> None:
    """Write a ComparisonReport to a CSV file at *path*."""
    content = to_csv_string(report, baseline=baseline)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        fh.write(content)


def save_json(
    report: ComparisonReport,
    path: str,
    baseline: Optional[str] = None,
    indent: int = 2,
) -> None:
    """Write a ComparisonReport to a JSON file at *path*."""
    content = to_json_string(report, baseline=baseline, indent=indent)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
