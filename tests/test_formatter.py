"""Tests for batchmark.formatter module."""

import pytest
from batchmark.formatter import format_table, row_to_display, print_table
from batchmark.comparator import ComparisonRow


def _make_row(
    name="baseline",
    total_time=1.0,
    items_per_second=100.0,
    seconds_per_item=0.01,
    relative_speed=None,
) -> ComparisonRow:
    row = ComparisonRow(name=name, total_time=total_time)
    row.items_per_second = items_per_second
    row.seconds_per_item = seconds_per_item
    row.relative_speed = relative_speed
    return row


def test_row_to_display_formats_floats():
    row = _make_row(total_time=2.5678, items_per_second=42.1, seconds_per_item=0.023752)
    display = row_to_display(row)
    assert display["total_time"] == "2.5678"
    assert display["items_per_second"] == "42.10"
    assert display["seconds_per_item"] == "0.023752"


def test_row_to_display_relative_speed_none():
    row = _make_row(relative_speed=None)
    display = row_to_display(row)
    assert display["relative_speed"] == "N/A"


def test_row_to_display_relative_speed_value():
    row = _make_row(relative_speed=1.75)
    display = row_to_display(row)
    assert display["relative_speed"] == "1.75x"


def test_format_table_contains_headers():
    rows = [_make_row(name="run_a"), _make_row(name="run_b", total_time=0.5)]
    table = format_table(rows)
    assert "Name" in table
    assert "Items Per Second" in table
    assert "Relative Speed" in table


def test_format_table_contains_row_names():
    rows = [_make_row(name="alpha"), _make_row(name="beta")]
    table = format_table(rows)
    assert "alpha" in table
    assert "beta" in table


def test_format_table_custom_columns():
    rows = [_make_row(name="only_name")]
    table = format_table(rows, columns=["name", "total_time"])
    assert "Name" in table
    assert "Total Time" in table
    assert "Relative Speed" not in table


def test_format_table_separator_line():
    rows = [_make_row()]
    table = format_table(rows)
    lines = table.splitlines()
    assert any(set(line.strip()) <= {"-", " "} for line in lines)


def test_print_table_outputs_to_stdout(capsys):
    rows = [_make_row(name="printed_row")]
    print_table(rows)
    captured = capsys.readouterr()
    assert "printed_row" in captured.out
    assert "Name" in captured.out
