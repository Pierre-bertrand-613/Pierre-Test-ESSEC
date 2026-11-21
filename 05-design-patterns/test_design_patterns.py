import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).parent
for folder in ("creational", "structural", "behavioral"):
    sys.path.insert(0, str(HERE / folder))

from adapter_report import AnalyticsDashboard, LegacyReportAdapter, LegacyReportGenerator  # noqa: E402
from builder_employee import DeveloperBuilder, EmployeeBuilder, InternBuilder  # noqa: E402
from decorator_order import (BaseOrder, DiscountDecorator, ExpressShippingDecorator,  # noqa: E402
                             GiftWrapDecorator, InsuranceDecorator, PremiumMemberDecorator)
from factory_payment import (BankTransferProcessor, CreditCardProcessor, PaymentFactory,  # noqa: E402
                             PayPalProcessor)
from singleton_config import ConfigManager  # noqa: E402
from strategy_report import (CSVFormatStrategy, FormatStrategy, HTMLFormatStrategy,  # noqa: E402
                             JSONFormatStrategy, ReportGenerator)
from template_etl import CSVPipeline, DataPipeline, XMLPipeline  # noqa: E402


# --- Factory ---
@pytest.mark.parametrize("name, cls", [("credit_card", CreditCardProcessor),
                                       ("bank_transfer", BankTransferProcessor),
                                       ("paypal", PayPalProcessor)])
def test_factory_returns_right_processor(name, cls):
    assert isinstance(PaymentFactory().get_processor(name), cls)


def test_factory_fees_and_validation():
    factory = PaymentFactory()
    card = factory.get_processor("credit_card").process(100, {"card_number": "1" * 16, "cvv": "123"})
    assert card["success"] and card["fee"] == pytest.approx(2.9)
    assert factory.get_processor("paypal").process(100, {"email": "nope"})["success"] is False
    with pytest.raises(ValueError):
        factory.get_processor("bitcoin")


# --- Builder ---
def test_builder_fluent_and_presets():
    e = (EmployeeBuilder().with_name("J", "D").with_email("j@d.com")
         .with_job("Eng", "Dev", 1000).with_access(vpn=True).build())
    assert e.has_vpn_access and not e.has_admin_rights
    dev = DeveloperBuilder("J", "D", "j@d.com").build()
    assert dev.has_laptop and dev.has_admin_rights
    assert InternBuilder("J", "S", "j@s.com", "Mkt").build().contract_type == "internship"


def test_builder_validation():
    with pytest.raises(ValueError):
        EmployeeBuilder().with_name("J", "D").with_email("invalid").with_job("E", "D", 1).build()


# --- Singleton ---
def test_singleton_same_instance_and_nested_get():
    ConfigManager.reset()
    a, b = ConfigManager.get_instance(), ConfigManager.get_instance()
    assert a is b
    assert a.get("database.port") == 5432 and a.get("missing.key", "x") == "x"
    a.set("app.debug", False)
    assert b.get("app.debug") is False         # shared state
    ConfigManager.reset()


# --- Adapter ---
def test_adapter_converts_xml_to_json(capsys):
    data = {"total_sales": 150000, "avg_order": 121.55}
    json_report = LegacyReportAdapter(LegacyReportGenerator()).generate(data)
    assert json.loads(json_report) == data
    AnalyticsDashboard().display(json_report)
    assert "total_sales: 150000" in capsys.readouterr().out


# --- Decorator ---
def test_decorators_match_original_computation():
    order = PremiumMemberDecorator(DiscountDecorator(GiftWrapDecorator(ExpressShippingDecorator(
        InsuranceDecorator(BaseOrder(100)))), percent=15))
    # original code: (100 + 15 + 5 + 5) * 0.85 * 0.90
    assert order.get_cost() == pytest.approx(125 * 0.85 * 0.9)
    assert "Gift wrap" in order.get_description()
    assert BaseOrder(100).get_cost() == 100


# --- Strategy ---
DATA = [{"name": "Q1", "value": 1}, {"name": "Q2", "value": 2}]


def test_strategy_switch_at_runtime(tmp_path):
    generator = ReportGenerator(DATA, CSVFormatStrategy())
    assert generator.generate_report() == "name,value\nQ1,1\nQ2,2\n"
    generator.set_strategy(JSONFormatStrategy())
    assert json.loads(generator.generate_report()) == DATA
    generator.set_strategy(HTMLFormatStrategy())
    assert "<td>Q1</td>" in generator.generate_report()
    assert generator.save_report(str(tmp_path / "r")).endswith(".html")


def test_new_strategy_without_touching_existing_code():
    class MarkdownFormatStrategy(FormatStrategy):
        extension = "md"

        def format(self, data):
            return "\n".join(f"- {d['name']}: {d['value']}" for d in data)

    assert ReportGenerator(DATA, MarkdownFormatStrategy()).generate_report() == "- Q1: 1\n- Q2: 2"


# --- Template Method ---
@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(DataPipeline, "delay", 0)


def test_template_runs_all_steps(capsys):
    assert XMLPipeline("orders.xml").run() == "XML Pipeline finished"
    out = capsys.readouterr().out
    assert out.index("Connecting") < out.index("Validation passed") < out.index("Cleanup complete")
    assert "archiving" in out          # hook was called


def test_template_validation_fails_on_bad_records():
    class BrokenPipeline(CSVPipeline):
        def transform(self, data):
            return [{"age": 1}]

    with pytest.raises(ValueError):
        BrokenPipeline("x.csv").run()
