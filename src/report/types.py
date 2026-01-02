"""Data classes for report-style calculations."""

from collections import deque
from dataclasses import dataclass
from typing import Optional

from handcalcs.handcalcs import expr_parser, test_for_unary
import pyparsing as pp

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


@dataclass
class InputCalcLine:
    """A line representing a input header or description."""
    line: deque
    comment: str
    latex: str


@dataclass
class InputCalcCell:
    source: str
    calculated_results: dict
    lines: deque
    precision: Optional[int]
    scientific_notation: Optional[bool]
    # cols: int
    latex_code: str

def test_for_input_line(line: str) -> bool:
    """
    Returns True if `line` appears to be a line to simply declare a
    parameter (e.g. "a = 34") instead of an actual calculation.
    """
    # Fast Tests
    if not line.strip():  # Blank lines
        return False
    elif len(line.strip().split()) == 1:  # Outputing variable names
        return True
    elif "=" not in line or "if " in line or ":" in line:  # conditional lines
        return False

    # Exploratory Tests
    _, right_side = line.split("=", 1)
    right_side = right_side.replace(" ", "")

    if (right_side.find("(") == 0) and (
        right_side.find(")") == len(right_side) - 1
    ):  # Blocked by parentheses
        return True

    try:
        right_side_deque = expr_parser(right_side)
    except pp.ParseException:
        right_side_deque = deque([right_side])

    if len(right_side_deque) == 1:
        return True
    elif test_for_unary(right_side_deque):
        return True
    else:
        return False
    
def split_input_line(line: str, calculated_results: dict) -> deque:
    """
    Return 'line' as a deque that represents the line as:
        deque([<parameter>, "&=", <value>])
    """
    param = line.replace(" ", "").split("=", 1)[0]
    param_line = deque([param, "=", calculated_results[param]])
    return param_line