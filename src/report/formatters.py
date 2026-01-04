"""Formatting functions for report cells and lines."""

import re
from typing import Optional

from handcalcs.handcalcs import (
    format_cell,
    format_lines,
    toggle_scientific_notation,
    round_and_render_line_objects_to_latex,
    convert_applicable_long_lines,
    format_strings, itertools, BlankLine, deque
)

from report.types import (
    InputCalcCell, InputCalcLine,
    ReportCalcCell, ReportCalcLine,
    )
from report.categorizer import categorize_lines
from report.converters import create_report_cell, create_input_cell, convert_cell

@format_lines.register(InputCalcLine)
def format_input_line(line: InputCalcLine, **config_options) -> InputCalcLine:
    comment_space = "\\;"

    if isinstance(line.line, deque):
        latex = " ".join(str(x) for x in line.line)
    else:
        latex = str(line.line)
    if "=" in latex:
        latex = latex.replace("=", "&=", 1)

    comment = format_strings(line.comment, comment=True) if line.comment else ""

    line.latex = f"{latex} {comment_space} {comment}".rstrip()
    return line

@format_cell.register(InputCalcCell)
def format_input_cell(cell: InputCalcCell, **config_options) -> InputCalcCell:
    precision = (
        config_options["display_precision"]
        if cell.precision is None
        else cell.precision
    )
    cell_notation = toggle_scientific_notation(
        config_options["use_scientific_notation"],
        cell.scientific_notation,
    )

    blocks: list[str] = []

    def flush_math(single_math_line: str):
        blocks.append(
              "$$\n"
              "\\hspace{2em}"
            + "\\begin{aligned}\n"
            + single_math_line
            + "\n\\end{aligned}\n"
            + "$$"
        )

    for line in cell.lines:
        line = round_and_render_line_objects_to_latex(
            line, precision, cell_notation, **config_options
        )
        line = format_lines(line, **config_options)

        if not line.latex:
            continue

        if isinstance(line, ReportCalcLine):
            blocks.append(line.latex)
        else:
            flush_math(line.latex)

    cell.markdown = "\n\n".join(blocks)
    return cell

@format_lines.register(ReportCalcLine)
def format_reportcalc_line(line: ReportCalcLine, **config_options) -> ReportCalcLine:
    """Format a report calculation line as Markdown."""
    text = line.line.lstrip("#").strip()
    if re.match(r"^\d+\.\d+", text):
        line.latex = f"### {text}"
    elif re.match(r"^\d+\.", text):
        line.latex = f"## {text}"
    else:
        line.latex = text
    return line

@format_cell.register(ReportCalcCell)
def format_reportcalc_cell(cell: ReportCalcCell, **config_options) -> ReportCalcCell:
    precision = (
        config_options["display_precision"]
        if cell.precision is None
        else cell.precision
    )
    cell_notation = toggle_scientific_notation(
        config_options["use_scientific_notation"],
        cell.scientific_notation,
    )

    blocks: list[str] = []
    pending_math: list[str] = []

    def flush_math():
        if not pending_math:
            return
        blocks.append(
              "$$\n"
              "\\hspace{2em}"
            + "\\begin{aligned}\n"
            + "\n".join(pending_math)
            + "\\end{aligned}\n"
            + "$$"
        )
        pending_math.clear()

    for line in cell.lines:
        line = round_and_render_line_objects_to_latex(
            line, precision, cell_notation, **config_options
        )
        line = convert_applicable_long_lines(line)
        line = format_lines(line, **config_options)

        if not line.latex:
            continue

        if isinstance(line, ReportCalcLine):
            # Text always breaks math
            flush_math()
            blocks.append(line.latex)
            continue

        flush_math()
        pending_math.append(line.latex)

    flush_math()
    cell.markdown = "\n\n".join(blocks)
    return cell


def latex_report(
    raw_python_source: str,
    calculated_results: dict,
    override_commands: str,
    config_options: dict,
    cell_precision: Optional[int] = None,
    cell_notation: Optional[bool] = None,
) -> str:
    """
    Generate a formatted report from Python calculations.
    
    Produces Markdown + LaTeX suitable for technical reports.
    """
    # Create cell
    if override_commands == "report":
        cell = create_report_cell(
            raw_source=raw_python_source,
            calculated_result=calculated_results,
            cell_precision=cell_precision,
            cell_notation=cell_notation,
        )
    if override_commands == "input":
        cell = create_input_cell(
            raw_source=raw_python_source,
            calculated_result=calculated_results,
            cell_precision=cell_precision,
            cell_notation=cell_notation,
        )
    # Categorize lines
    cell = categorize_lines(cell, override_commands)

    # Convert cell
    cell = convert_cell(cell, **config_options)

    # Format cell
    cell = format_cell(cell, **config_options)

    return cell.markdown