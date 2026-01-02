"""Main renderer class for report-style calculations."""

from typing import Optional
from handcalcs import global_config
from report.formatters import latex_report

class ReportRenderer:
    """Renders Python calculations as formatted reports."""
    
    def __init__(self, python_code_str: str, results: dict, line_args: dict):
        self.source = python_code_str
        self.results = results
        self.override_precision = line_args["precision"]
        self.override_scientific_notation = line_args["sci_not"]
        self.override_commands = line_args["override"]

    def render(self, config_options: dict = global_config._config) -> str:
        """Render the calculation as a formatted report."""
        return latex_report(
            raw_python_source=self.source,
            calculated_results=self.results,
            override_commands=self.override_commands,
            config_options=config_options,
            cell_precision=self.override_precision,
            cell_notation=self.override_scientific_notation,
        )