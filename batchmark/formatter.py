"""Text table formatter for benchmark comparison reports."""

from typing import List, Optional
from batchmark.comparator import ComparisonRow


DEFAULT_COLUMNS = ["name", "total_time", "items_per_second", "seconds_per_item", "relative_speed"]


def _format_float(value: Optional[float], decimals: int = 4) -> str:
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}"


def _format_relative_speed(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    return f"{value:.2f}x"


def row_to_display(row: ComparisonRow) -> dict:
    """Convert a ComparisonRow to a display-friendly dict of strings."""
    return {
        "name": row.name,
        "total_time": _format_float(row.total_time, 4),
        "items_per_second": _format_float(row.items_per_second, 2),
        "seconds_per_item": _format_float(row.seconds_per_item, 6),
        "relative_speed": _format_relative_speed(row.relative_speed),
    }


def format_table(rows: List[ComparisonRow], columns: Optional[List[str]] = None) -> str:
    """Format a list of ComparisonRows as a plain-text table string."""
    if columns is None:
        columns = DEFAULT_COLUMNS

    headers = {col: col.replace("_", " ").title() for col in columns}
    display_rows = [row_to_display(r) for r in rows]

    col_widths = {col: len(headers[col]) for col in columns}
    for dr in display_rows:
        for col in columns:
            col_widths[col] = max(col_widths[col], len(dr.get(col, "")))

    def _fmt_row(values: dict) -> str:
        parts = [values.get(col, "").ljust(col_widths[col]) for col in columns]
        return "  ".join(parts)

    separator = "  ".join("-" * col_widths[col] for col in columns)
    lines = [
        _fmt_row(headers),
        separator,
    ]
    for dr in display_rows:
        lines.append(_fmt_row(dr))

    return "\n".join(lines)


def print_table(rows: List[ComparisonRow], columns: Optional[List[str]] = None) -> None:
    """Print a formatted table of ComparisonRows to stdout."""
    print(format_table(rows, columns))
