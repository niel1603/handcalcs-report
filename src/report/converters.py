"""Conversion functions for report cells and lines."""

from collections import deque

from handcalcs.handcalcs import (
    convert_cell,
    convert_line,
    add_result_values_to_line,
    convert_applicable_long_lines,
    round_and_render_line_objects_to_latex,
)

from report.types import (
    ReportCalcCell, ReportCalcLine,
    InputCalcCell, InputCalcLine)

def create_report_cell(
    raw_source: str,
    calculated_result: dict,
    cell_precision: int = None,
    cell_notation: bool = None,
) -> ReportCalcCell:
    """Create a ReportCalcCell from raw source code."""
    from handcalcs.handcalcs import strip_cell_code
    
    comment_tag_removed = strip_cell_code(raw_source)
    cell = ReportCalcCell(
        source=comment_tag_removed,
        calculated_results=calculated_result,
        precision=cell_precision,
        scientific_notation=cell_notation,
        lines=deque([]),
        latex_code="",
    )
    return cell

def create_input_cell(
    raw_source: str,
    calculated_result: dict,
    cell_precision: int = None,
    cell_notation: bool = None,
) -> InputCalcCell:
    """Create a InputCalcCell from raw source code."""
    from handcalcs.handcalcs import strip_cell_code
    
    comment_tag_removed = strip_cell_code(raw_source)
    cell = InputCalcCell(
        source=comment_tag_removed,
        calculated_results=calculated_result,
        precision=cell_precision,
        scientific_notation=cell_notation,
        lines=deque([]),
        latex_code="",
    )
    return cell

@add_result_values_to_line.register(ReportCalcLine)
def results_for_report(line_object, calculated_results):
    """Add results to a report line (no-op for report lines)."""
    return line_object

@add_result_values_to_line.register(InputCalcLine)
def results_for_input(line_object, calculated_results):
    """Add results to a input line (no-op for input lines)."""
    return line_object

@convert_cell.register(ReportCalcCell)
def convert_reportcalc_cell(cell: ReportCalcCell, **config_options) -> ReportCalcCell:
    """Convert all lines in a report cell."""
    outgoing = cell.lines
    calculated_results = cell.calculated_results
    incoming = deque([])
    
    for line in outgoing:
        incoming.append(convert_line(line, calculated_results, **config_options))
    
    cell.lines = incoming
    return cell

@convert_cell.register(InputCalcCell)
def convert_inputcalc_cell(cell: InputCalcCell, **config_options) -> InputCalcCell:
    """Convert all lines in a input cell."""
    outgoing = cell.lines
    calculated_results = cell.calculated_results
    incoming = deque([])
    
    for line in outgoing:
        incoming.append(convert_line(line, calculated_results, **config_options))
    
    cell.lines = incoming
    return cell

@convert_line.register(ReportCalcLine)
def convert_report(line, calculated_results, **config_options):
    """Convert a report line (no-op for report lines)."""
    return line

@convert_line.register(InputCalcLine)
def conver_input(line, calculated_results, **config_options):
    """Convert a input line (no-op for input lines)."""
    return line

@convert_applicable_long_lines.register(ReportCalcLine)
def convert_report_to_long(line: ReportCalcLine):
    """Convert long report lines (no-op for report lines)."""
    return line

@convert_applicable_long_lines.register(InputCalcLine)
def convert_input_to_long(line: InputCalcLine):
    """Convert long input lines (no-op for input lines)."""
    return line

@round_and_render_line_objects_to_latex.register(ReportCalcLine)
def round_and_render_report(
    line, cell_precision: int, cell_notation: bool, **config_options
):
    """Round and render report lines (no-op for report lines)."""
    return line

@round_and_render_line_objects_to_latex.register(InputCalcLine)
def round_and_render_input(
    line, cell_precision: int, cell_notation: bool, **config_options
):
    """Round and render input lines (no-op for input lines)."""
    return line