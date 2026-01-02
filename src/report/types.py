"""Data classes for report-style calculations."""

from collections import deque
from dataclasses import dataclass
from typing import Optional


@dataclass
class ReportCalcLine:
    """A line representing a report header or description."""
    line: deque
    comment: str
    latex: str


@dataclass
class ReportCalcCell:
    """
    A calc cell that supports headers, descriptions, explanations,
    and equations rendered as a single Markdown + MathJax block.
    """
    source: str
    calculated_results: dict
    lines: deque
    precision: Optional[int]
    scientific_notation: Optional[bool]
    latex_code: str
    markdown: Optional[str] = None


def test_for_report_line(source: str) -> bool:
    """Returns True if 'source' appears to be a header line."""
    return source.startswith("##")