from collections import deque, ChainMap
from dataclasses import dataclass
import re
from typing import Union, Optional

from handcalcs import global_config
from handcalcs.handcalcs import CalcCell, ParameterCell, ConditionalLine

class ReportRenderer:
    def __init__(self, python_code_str: str, results: dict, line_args: dict):
        self.source = python_code_str
        self.results = results
        self.override_precision = line_args["precision"]
        self.override_scientific_notation = line_args["sci_not"]
        self.override_commands = line_args["override"]

    def render(self, config_options: dict = global_config._config):
        return latex_report(
            raw_python_source=self.source,
            calculated_results=self.results,
            override_commands=self.override_commands,
            config_options=config_options,
            cell_precision=self.override_precision,
            cell_notation=self.override_scientific_notation,
        )

from handcalcs.handcalcs import(
    
    test_for_blank_line,
    BlankLine,
    
    test_for_conditional_line,
    create_conditional_line,

    test_for_parameter_line,
    ParameterLine,
    split_parameter_line,

    test_for_numeric_line,
    expr_parser,
    NumericCalcLine,

    CalcLine,

    add_result_values_to_line,

    convert_cell,
    convert_line,
    format_cell,
    format_lines,
    )


def test_for_report_line(source: str) -> bool:
    """
    Returns True if 'source' appears to be an header line
    """
    return source.startswith("##")

@dataclass
class ReportCalcLine:
    line: deque
    comment: str
    latex: str

from handcalcs.handcalcs import add_result_values_to_line, dict_get

@add_result_values_to_line.register(ReportCalcLine)
def results_for_report(line_object, calculated_results):
    return line_object

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

def create_report_cell(
    raw_source: str,
    calculated_result: dict,
    cell_precision: Optional[int] = None,
    cell_notation: Optional[bool] = None,
) -> ReportCalcCell:
    """
    Returns an IntertextCalcCell.
    """
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

from handcalcs.handcalcs import(
    toggle_scientific_notation,
    round_and_render_line_objects_to_latex,
    convert_applicable_long_lines,
    )

@convert_cell.register(ReportCalcCell)
def convert_reportcalc_cell(cell: ReportCalcCell, **config_options) -> ReportCalcCell:
    outgoing = cell.lines
    calculated_results = cell.calculated_results
    incoming = deque([])
    for line in outgoing:
        incoming.append(convert_line(line, calculated_results, **config_options))
    cell.lines = incoming
    return cell

@convert_line.register(ReportCalcLine)
def convert_report(line, calculated_results, **config_options):
    return line

@round_and_render_line_objects_to_latex.register(ReportCalcLine)
def round_and_render_report(
    line, cell_precision: int, cell_notation: bool, **config_options
):
    return line

@convert_applicable_long_lines.register(ReportCalcLine)
def convert_report_to_long(line: ReportCalcLine):
    return line

@format_lines.register(ReportCalcLine)
def format_reportcalc_line(line: ReportCalcLine, **config_options) -> ReportCalcLine:
    raw = line.line.rstrip()

    # Strip markdown header markers
    text = raw.lstrip("#").strip()

    # Determine semantic level
    if re.match(r"^\d+\.\d+", text):
        # subheader (1.1)
        indent_em = 2
        size = r"\large "
        line_break = f"{config_options['line_break']}\n"
    elif re.match(r"^\d+\.", text):
        # header (1.)
        indent_em = 0
        size = r"\Large "
        line_break = f"{config_options['line_break']}\n"
    else:
        # description paragraph
        indent_em = 4
        size = r"\small "
        line_break = "\\\\"

    # Emit LaTeX
    line.latex = (
        rf"\hspace{{{indent_em}em}}\text{{\textbf{{{size}{text}}}}}{line_break}"
    )
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

    blocks = []
    pending_math = []

    def flush_math():
        if pending_math:
            blocks.append("$$\n" + f"\\begin{{aligned}}\n" + "\n".join(pending_math) + f"\\end{{aligned}}\n" + "$$")
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
            flush_math()

            text = line.line.lstrip("#").strip()
            if re.match(r"^\d+\.\d+", text):
                blocks.append(f"### {text}")
            elif re.match(r"^\d+\.", text):
                blocks.append(f"## {text}")
            else:
                blocks.append(text)

        else:
            pending_math.append(line.latex)

    flush_math()

    cell.markdown = "\n\n".join(blocks)
    cell.latex_code = ""  # unused
    return cell

def categorize_lines(
    cell: Union[CalcCell, ParameterCell],
) -> Union[CalcCell, ParameterCell]:
    """
    Return 'cell' with the line data contained in cell_object.source categorized
    into one of four types:
    * CalcLine
    * ParameterLine
    * ConditionalLine

    categorize_lines(calc_cell) is considered the default behaviour for the
    singledispatch categorize_lines function.
    """
    incoming = cell.source.rstrip().split("\n")
    outgoing = deque([])
    calculated_results = cell.calculated_results
    cell_override = ""
    for line in incoming:
        cell_override = "report"
        categorized = categorize_line(line, calculated_results, cell_override)
        categorized_w_result_appended = add_result_values_to_line(
            categorized, calculated_results
        )
        outgoing.append(categorized_w_result_appended)
    cell.lines = outgoing
    return cell

def categorize_line(
    line: str, calculated_results: dict, cell_override: str = ""
) -> Union[CalcLine, ParameterLine, ConditionalLine]:
    """
    Return 'line' as either a CalcLine, ParameterLine, or ConditionalLine if 'line'
    fits the appropriate criteria. Raise ValueError, otherwise.

    'override' is a str used to short-cut the tests in categorize_line(). e.g.
    if the cell that the lines belong to is a ParameterCell,
    we do not need to run the test_for_parameter_line() function on the line
    because, in a ParameterCell, all lines will default to a ParameterLine
    because of the cell it's in and how that cell is supposed to behave.

    'override' is passed from the categorize_lines() function because that
    function has the information of the cell type and can pass along any
    desired behavior to categorize_line().
    """

    if test_for_blank_line(line):
        return BlankLine(line, "", "")

    if test_for_report_line(line):
        return ReportCalcLine(line, "", "")

    if line.startswith("#"):
        return BlankLine(line, "", "")

    if line.endswith("ignore"):
        return BlankLine(line, "", "")

    try:
        line, comment = line.split("#", 1)
    except ValueError:
        comment = ""

    # Override behaviour
    categorized_line = None
    if cell_override == "report":
        if test_for_report_line(line):
            categorized_line = ReportCalcLine(line, comment, "")

        elif test_for_conditional_line(line):
            categorized_line = create_conditional_line(
                line, calculated_results, cell_override, comment
            )

        elif test_for_parameter_line(line):
            categorized_line = ParameterLine(
                split_parameter_line(line, calculated_results), comment, ""
            )

        elif test_for_numeric_line(
            deque(list(expr_parser(line))[1:])
        ):
            categorized_line = NumericCalcLine(expr_parser(line), comment, "")

        elif "=" in line:
            categorized_line = CalcLine(expr_parser(line), comment, "")

        else:
            categorized_line = ReportCalcLine(line, comment, "")

        return categorized_line
    
    elif True:
        pass  # Future override conditions to match new cell types can be put here

    # Standard behaviour
    if line == "\n" or line == "":
        categorized_line = BlankLine(line, "", "")

    elif test_for_parameter_line(line):
        categorized_line = ParameterLine(
            split_parameter_line(line, calculated_results), comment, ""
        )

    elif test_for_conditional_line(line):
        categorized_line = create_conditional_line(
            line, calculated_results, cell_override, comment
        )

    elif test_for_numeric_line(
        deque(list(expr_parser(line))[1:])  # Leave off the declared variable
    ):
        categorized_line = NumericCalcLine(expr_parser(line), comment, "")

    elif "=" in line:
        categorized_line = CalcLine(expr_parser(line), comment, "")  # code_reader

    elif len(expr_parser(line)) == 1:
        categorized_line = ParameterLine(
            split_parameter_line(line, calculated_results), comment, ""
        )

    else:
        # TODO: Raise this error in a test
        raise ValueError(
            f"Line: {line} is not recognized for rendering.\n"
            "Lines must either:\n"
            "\t * Be the name of a previously assigned single variable\n"
            "\t * Be an arithmetic variable assignment (i.e. calculation that uses '=' in the line)\n"
            "\t * Be a conditional arithmetic assignment (i.e. uses 'if', 'elif', or 'else', each on a single line)"
        )
    return categorized_line

def latex_report(
    raw_python_source: str,
    calculated_results: dict,
    override_commands: str,
    config_options: dict,
    cell_precision: Optional[int] = None,
    cell_notation: Optional[bool] = None,
) -> str:
    """
    Report-oriented wrapper around `latex()`.

    Produces Markdown + LaTeX suitable for technical reports.
    """

    source = raw_python_source

    # create_report_cell
    cell = create_report_cell(
        raw_source=source,
        calculated_result=calculated_results,
        cell_precision=cell_precision,
        cell_notation=cell_notation,
    )

    # categorize_lines
    cell = categorize_lines(cell)

    # convert_cell
    cell = convert_cell(
        cell,
        **config_options,
    )

    # format_cell
    cell = format_cell(
        cell,
        **config_options,
        # dec_sep
    )
    return cell.markdown
