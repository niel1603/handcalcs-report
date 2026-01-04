"""Line categorization logic for report cells."""

from collections import deque
from typing import Union

from handcalcs.handcalcs import (
    CalcCell,
    ParameterCell,
    LongCalcLine,
    ParameterLine,
    ConditionalLine,
    BlankLine,
    test_for_blank_line,
    test_for_conditional_line,
    create_conditional_line,
    test_for_parameter_line,
    split_parameter_line,
    test_for_numeric_line,
    expr_parser,
    NumericCalcLine,
    add_result_values_to_line,
)

from report.types import (
    ReportCalcLine, test_for_report_line,
    InputCalcLine, test_for_input_line, split_input_line,
    )


def categorize_lines(
    cell: Union[CalcCell, ParameterCell], cell_override: str = ""
) -> Union[CalcCell, ParameterCell]:
    """
    Categorize each line in the cell into one of four types:
    * LongCalcLine
    * ParameterLine
    * ConditionalLine
    * ReportCalcLine
    """
    incoming = cell.source.rstrip().split("\n")
    outgoing = deque([])
    calculated_results = cell.calculated_results
    
    for line in incoming:
        categorized = categorize_line(line, calculated_results, cell_override)
        categorized_w_result = add_result_values_to_line(
            categorized, calculated_results
        )
        outgoing.append(categorized_w_result)
    
    cell.lines = outgoing
    return cell


def categorize_line(
    line: str, calculated_results: dict, cell_override: str = ""
) -> Union[LongCalcLine, ParameterLine, ConditionalLine, ReportCalcLine]:
    """
    Categorize a single line based on its content.
    
    The 'cell_override' parameter allows cell-level behavior to override
    default line categorization logic.
    """
    # Handle blank lines and comments
    if test_for_blank_line(line):
        return BlankLine(line, "", "")

    if test_for_report_line(line):
        return ReportCalcLine(line, "", "")

    if line.startswith("#"):
        return BlankLine(line, "", "")

    if line.endswith("ignore"):
        return BlankLine(line, "", "")

    # Split off inline comments
    try:
        line, comment = line.split("#", 1)
    except ValueError:
        comment = ""

    # Report cell override behavior
    if cell_override == "input":
        return _categorize_input_line(line, calculated_results, comment)
    if cell_override == "report":
        return _categorize_report_line(line, calculated_results, comment)
    
    # Standard behavior (for future extension)
    return _categorize_standard_line(line, calculated_results, comment)


def _categorize_input_line(
    line: str, calculated_results: dict, comment: str
) -> Union[ConditionalLine, InputCalcLine]:
    """Categorize a line within a report cell."""
    if test_for_conditional_line(line):
        return create_conditional_line(
            line, calculated_results, "input", comment
        )
    return InputCalcLine(
        split_parameter_line(line, calculated_results), comment, "")

def _categorize_report_line(
    line: str, calculated_results: dict, comment: str
) -> Union[LongCalcLine, ParameterLine, ConditionalLine, ReportCalcLine]:
    """Categorize a line within a report cell."""
    if test_for_parameter_line(line):  # A parameter can exist in a long cell, too
        categorized_line = ParameterLine(
            split_parameter_line(line, calculated_results), comment, ""
        )
    elif test_for_conditional_line(
        line
    ):  # A conditional line can exist in a long cell, too
        categorized_line = create_conditional_line(
            line, calculated_results, "report", comment
        )
    elif test_for_numeric_line(
        deque(
            list(expr_parser(line))[1:]
        )  # Leave off the declared variable, e.g. _x_ = ...
    ):
        categorized_line = NumericCalcLine(expr_parser(line), comment, "")

    else:
        categorized_line = LongCalcLine(
            expr_parser(line), comment, ""
        )  # code_reader
    return categorized_line

def _categorize_standard_line(
    line: str, calculated_results: dict, comment: str
) -> Union[LongCalcLine, ParameterLine, ConditionalLine]:
    """Categorize a line using standard behavior."""
    if line == "\n" or line == "":
        return BlankLine(line, "", "")

    if test_for_parameter_line(line):
        return ParameterLine(
            split_parameter_line(line, calculated_results), comment, ""
        )

    if test_for_conditional_line(line):
        return create_conditional_line(
            line, calculated_results, "", comment
        )

    if test_for_numeric_line(deque(list(expr_parser(line))[1:])):
        return NumericCalcLine(expr_parser(line), comment, "")

    if "=" in line:
        return LongCalcLine(expr_parser(line), comment, "")

    if len(expr_parser(line)) == 1:
        return ParameterLine(
            split_parameter_line(line, calculated_results), comment, ""
        )

    raise ValueError(
        f"Line: {line} is not recognized for rendering.\n"
        "Lines must either:\n"
        "\t * Be the name of a previously assigned single variable\n"
        "\t * Be an arithmetic variable assignment (i.e. calculation that uses '=' in the line)\n"
        "\t * Be a conditional arithmetic assignment (i.e. uses 'if', 'elif', or 'else', each on a single line)"
    )