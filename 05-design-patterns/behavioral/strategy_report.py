"""Strategy pattern - refactor of the multi-format report generator.

Problems of the original code (answers to the questions):
1. Adding XML/Markdown means editing two if/elif chains (generate AND save).
2. It violates the Open/Closed Principle.
3. Hard to test: every format lives in the same method, you can't test one alone.
4. Formats can't be changed at runtime except by passing strings around.
5. Duplication: the format name is checked twice, and the file extension logic is repeated.
"""
import json
from abc import ABC, abstractmethod
from html import escape
from typing import List, Optional


class FormatStrategy(ABC):
    """Contract for all report formats."""

    extension = ""

    @abstractmethod
    def format(self, data: List[dict]) -> str: ...


class PDFFormatStrategy(FormatStrategy):
    extension = "pdf"

    def format(self, data: List[dict]) -> str:
        report = "PDF REPORT\n" + "=" * 50 + "\n"
        for item in data:
            report += f"| {item['name']:20} | {item['value']:10} |\n"
        return report + "=" * 50 + "\nEnd of PDF Report"


class ExcelFormatStrategy(FormatStrategy):
    extension = "xlsx"

    def format(self, data: List[dict]) -> str:
        report = "EXCEL REPORT\n" + "-" * 50 + "\nName\tValue\n"
        for item in data:
            report += f"{item['name']}\t{item['value']}\n"
        return report + "-" * 50 + "\n"


class CSVFormatStrategy(FormatStrategy):
    extension = "csv"

    def format(self, data: List[dict]) -> str:
        return "name,value\n" + "".join(f"{item['name']},{item['value']}\n" for item in data)


class JSONFormatStrategy(FormatStrategy):
    extension = "json"

    def format(self, data: List[dict]) -> str:
        return json.dumps(data, indent=2)


# Final test of the exercise: HTML added WITHOUT modifying any existing class
class HTMLFormatStrategy(FormatStrategy):
    extension = "html"

    def format(self, data: List[dict]) -> str:
        rows = "\n".join(
            f"  <tr><td>{escape(str(item['name']))}</td><td>{item['value']}</td></tr>" for item in data
        )
        return f"<table>\n  <tr><th>Name</th><th>Value</th></tr>\n{rows}\n</table>"


class ReportGenerator:
    """Context: holds the data and delegates formatting to the current strategy."""

    def __init__(self, data: List[dict], strategy: Optional[FormatStrategy] = None):
        self.data = data
        self._strategy = strategy

    def set_strategy(self, strategy: FormatStrategy) -> None:
        self._strategy = strategy

    def generate_report(self) -> str:
        if self._strategy is None:
            raise ValueError("No format strategy set")
        return self._strategy.format(self.data)

    def save_report(self, filename: str) -> str:
        path = f"{filename}.{self._strategy.extension}"
        with open(path, "w") as f:
            f.write(self.generate_report())
        return path


if __name__ == "__main__":
    data = [
        {"name": "Sales Q1", "value": 15000},
        {"name": "Sales Q2", "value": 18000},
        {"name": "Sales Q3", "value": 22000},
        {"name": "Sales Q4", "value": 25000},
    ]
    generator = ReportGenerator(data)
    for title, strategy in [("PDF", PDFFormatStrategy()), ("CSV", CSVFormatStrategy()),
                            ("JSON", JSONFormatStrategy()), ("HTML (NEW!)", HTMLFormatStrategy())]:
        print(f"=== {title} FORMAT ===")
        generator.set_strategy(strategy)       # switch format at runtime
        print(generator.generate_report())
        print("\n" + "=" * 60 + "\n")

    generator.set_strategy(CSVFormatStrategy())
    print("Saved:", generator.save_report("sales_report"))
