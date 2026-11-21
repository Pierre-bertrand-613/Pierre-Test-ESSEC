"""Adapter pattern - make the legacy XML report generator usable by the JSON dashboard.

Problems of the original code:
- incompatible interfaces: legacy returns XML, the dashboard expects JSON
- conversion repeated in every function (and it cheats by re-using the original dict)
- the legacy system can't be modified (external library)
- business logic mixed with format conversion (tight coupling)
"""
import json
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod


# Legacy reporting system (can't modify - external library)
class LegacyReportGenerator:
    def generate_report(self, data: dict) -> str:
        """Returns XML format - old system"""
        xml = "<report>\n"
        for key, value in data.items():
            xml += f" <{key}>{value}</{key}>\n"
        xml += "</report>"
        return xml


# New analytics dashboard expects JSON
class AnalyticsDashboard:
    def display(self, json_data: str):
        data = json.loads(json_data)
        print("=== Analytics Dashboard ===")
        for key, value in data.items():
            print(f" {key}: {value}")


class ReportGeneratorInterface(ABC):
    """The interface the client (dashboard code) expects."""

    @abstractmethod
    def generate(self, data: dict) -> str:
        """Return the report as a JSON string."""


class LegacyReportAdapter(ReportGeneratorInterface):
    """Wraps the legacy generator and converts its XML output to JSON."""

    def __init__(self, legacy: LegacyReportGenerator):
        self._legacy = legacy          # composition: the adaptee is wrapped, not inherited

    def generate(self, data: dict) -> str:
        xml_report = self._legacy.generate_report(data)
        return json.dumps(self._xml_to_dict(xml_report))

    @staticmethod
    def _xml_to_dict(xml_report: str) -> dict:
        root = ET.fromstring(xml_report)
        return {child.tag: LegacyReportAdapter._parse_value(child.text or "") for child in root}

    @staticmethod
    def _parse_value(text: str):
        """XML only has text: convert numbers back to int/float."""
        for cast in (int, float):
            try:
                return cast(text)
            except ValueError:
                pass
        return text


def show_report(generator: ReportGeneratorInterface, dashboard: AnalyticsDashboard, data: dict):
    # Business code only knows the interface, not the legacy system
    dashboard.display(generator.generate(data))


if __name__ == "__main__":
    report_generator = LegacyReportAdapter(LegacyReportGenerator())
    dashboard = AnalyticsDashboard()
    show_report(report_generator, dashboard, {"total_sales": 150000, "orders": 1234, "avg_order": 121.55})
    show_report(report_generator, dashboard, {"total_items": 5000, "low_stock": 45, "out_of_stock": 12})
