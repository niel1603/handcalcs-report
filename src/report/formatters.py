"""Formatting functions for report cells and lines."""

import re
from typing import Optional

from handcalcs.handcalcs import (
    format_cell,
    format_lines,
    toggle_scientific_notation,
    round_and_render_line_objects_to_latex,
    convert_applicable_long_lines,
    format_strings, itertools, BlankLine
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
    line_break = "\n"
    if "=" in line.latex:
        replaced = line.latex.replace("=", "&=")
        comment = format_strings(line.comment, comment=True)
        line.latex = f"{replaced} {comment_space} {comment}{line_break}"
    else:  # To handle sympy symbols displayed alone
        replaced = line.latex.replace(" ", comment_space)
        comment = format_strings(line.comment, comment=True)
        line.latex = f"{replaced} {comment_space} {comment}{line_break}"
    return line

@format_cell.register(InputCalcCell)
def format_input_cell(cell: InputCalcCell, **config_options) -> InputCalcCell:
    """Format a report cell as Markdown with embedded LaTeX math blocks."""
    precision = (
        config_options["display_precision"]
        if cell.precision is None
        else cell.precision
    )

    cell_notation = toggle_scientific_notation(
        config_options["use_scientific_notation"],
        cell.scientific_notation,
    )

    blocks = []
    pending_math = []

    def flush_math():
        """Flush accumulated math lines into a single aligned block."""
        if pending_math:
            blocks.append(
                  "$\n"
                + "\hspace{2em}"
                + "\\begin{aligned}\n"
                + "\n".join(pending_math)
                + "\\end{aligned}\n"
                + "$"
            )
            pending_math.clear()

    for line in cell.lines:
        # Process line through formatting pipeline
        line = round_and_render_line_objects_to_latex(
            line, precision, cell_notation, **config_options
        )
        line = convert_applicable_long_lines(line)
        line = format_lines(line, **config_options)

        if not line.latex:
            continue

        # Handle report lines differently from math lines
        if isinstance(line, ReportCalcLine):
            flush_math()
            text = line.line.lstrip("#").strip()
            
            if re.match(r"^\d+\.\d+", text):
                blocks.append(f"### {text}")
            elif re.match(r"^\d+\.", text):
                blocks.append(f"## {text}")
            else:
                blocks.append(text)
        else:
            # Accumulate math lines
            pending_math.append(line.latex)

    flush_math()

    cell.markdown = "\n\n".join(blocks)
    cell.latex_code = ""  # Unused in report mode
    return cell

@format_lines.register(ReportCalcLine)
def format_reportcalc_line(line: ReportCalcLine, **config_options) -> ReportCalcLine:
    """Format a report calculation line as LaTeX."""
    raw = line.line.rstrip()
    text = raw.lstrip("#").strip()

    # Determine semantic level based on numbering
    if re.match(r"^\d+\.\d+", text):
        # Subheader (e.g., "1.1")
        indent_em = 2
        size = r"\large "
        line_break = f"{config_options['line_break']}\n"
    elif re.match(r"^\d+\.", text):
        # Header (e.g., "1.")
        indent_em = 0
        size = r"\Large "
        line_break = f"{config_options['line_break']}\n"
    else:
        # Description paragraph
        indent_em = 4
        size = r"\small "
        line_break = "\\\\"

    # Generate LaTeX
    line.latex = (
        rf"\hspace{{{indent_em}em}}\text{{\textbf{{{size}{text}}}}}{line_break}"
    )
    return line


@format_cell.register(ReportCalcCell)
def format_reportcalc_cell(cell: ReportCalcCell, **config_options) -> ReportCalcCell:
    """Format a report cell as Markdown with embedded LaTeX math blocks."""
    precision = (
        config_options["display_precision"]
        if cell.precision is None
        else cell.precision
    )

    cell_notation = toggle_scientific_notation(
        config_options["use_scientific_notation"],
        cell.scientific_notation,
    )

    blocks = []
    pending_math = []

    def flush_math():
        """Flush accumulated math lines into a single aligned block."""
        if pending_math:
            blocks.append(
                "$$\n"
                + "\\begin{aligned}\n"
                + "\n".join(pending_math)
                + "\\end{aligned}\n"
                + "$$"
            )
            pending_math.clear()

    for line in cell.lines:
        # Process line through formatting pipeline
        line = round_and_render_line_objects_to_latex(
            line, precision, cell_notation, **config_options
        )
        line = convert_applicable_long_lines(line)
        line = format_lines(line, **config_options)

        if not line.latex:
            continue

        # Handle report lines differently from math lines
        if isinstance(line, ReportCalcLine):
            flush_math()
            text = line.line.lstrip("#").strip()
            
            if re.match(r"^\d+\.\d+", text):
                blocks.append(f"### {text}")
            elif re.match(r"^\d+\.", text):
                blocks.append(f"## {text}")
            else:
                blocks.append(text)
        else:
            # Accumulate math lines
            pending_math.append(line.latex)

    flush_math()

    cell.markdown = "\n\n".join(blocks)
    cell.latex_code = ""  # Unused in report mode
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
    cell = categorize_lines(cell)

    # Convert cell
    cell = convert_cell(cell, **config_options)

    # Format cell
    cell = format_cell(cell, **config_options)

    return cell.markdown