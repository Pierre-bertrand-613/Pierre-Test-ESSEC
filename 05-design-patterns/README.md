# 05 - Design patterns

Exercises from the course website:
- [Creational patterns](https://courses.dallard.tech/sys_design/creational_pattern/)
- Structural patterns
- Behavioral patterns

For each one I wrote the problems of the spaghetti code at the top of the file, then the refactored code, and the expected usage in `__main__`.

| Type | Pattern | Exercise | File |
|---|---|---|---|
| Creational | Factory | Payment system | [`creational/factory_payment.py`](creational/factory_payment.py) |
| Creational | Builder | HR employee onboarding | [`creational/builder_employee.py`](creational/builder_employee.py) |
| Creational | Singleton | Config manager | [`creational/singleton_config.py`](creational/singleton_config.py) |
| Structural | Adapter | XML -> JSON reports | [`structural/adapter_report.py`](structural/adapter_report.py) |
| Structural | Decorator | Order pricing | [`structural/decorator_order.py`](structural/decorator_order.py) |
| Behavioral | Strategy | Report formats | [`behavioral/strategy_report.py`](behavioral/strategy_report.py) |
| Behavioral | Template Method | ETL pipelines | [`behavioral/template_etl.py`](behavioral/template_etl.py) |

```bash
python3 creational/factory_payment.py
python3 -m pytest
```

## Factory - payment system

Problem: a big if/elif on `payment_type`, so adding a payment method means modifying the function (breaks Open/Closed). Solution: one class per processor and a factory with a dict that maps the string to the class. I added Apple Pay with `register()` without changing the other classes.

```mermaid
classDiagram
    class PaymentProcessor {
        <<abstract>>
        +validate(details) bool*
        +compute_fee(amount) float*
        +process(amount, details) dict
    }
    class CreditCardProcessor
    class BankTransferProcessor
    class PayPalProcessor
    class ApplePayProcessor
    class PaymentFactory {
        -_processors: dict~str, type~
        +register(name, cls)$
        +get_processor(payment_type) PaymentProcessor
    }
    PaymentProcessor <|-- CreditCardProcessor
    PaymentProcessor <|-- BankTransferProcessor
    PaymentProcessor <|-- PayPalProcessor
    PaymentProcessor <|-- ApplePayProcessor
    PaymentFactory ..> PaymentProcessor : creates
```

## Builder - HR onboarding

Problem: a function with 17 parameters and a lot of True/False that you can't read. Solution: chainable methods that return `self`, all the validation in `build()`, and presets (`DeveloperBuilder`, `InternBuilder`).

```mermaid
classDiagram
    class Employee {
        <<dataclass>>
        +first_name: str
        +last_name: str
        +email: str
        +department: str
        +position: str
        +salary: float
        +has_laptop: bool
        +has_vpn_access: bool
        +has_admin_rights: bool
        +contract_type: str
    }
    class EmployeeBuilder {
        -_data: dict
        +with_name(first, last) EmployeeBuilder
        +with_email(email) EmployeeBuilder
        +with_job(dept, position, salary) EmployeeBuilder
        +with_equipment(laptop, parking) EmployeeBuilder
        +with_access(vpn, admin) EmployeeBuilder
        +build() Employee
    }
    class DeveloperBuilder
    class InternBuilder
    EmployeeBuilder <|-- DeveloperBuilder
    EmployeeBuilder <|-- InternBuilder
    EmployeeBuilder ..> Employee : builds
```

## Singleton - config manager

Problem: config.json is read 4 times and every module has its own copy. Solution: `get_instance()` loads the file only once, `get("database.host")` reads nested keys, and `reset()` is for the tests.

```mermaid
classDiagram
    class ConfigManager {
        -_instance: ConfigManager$
        -_config: dict
        +get_instance() ConfigManager$
        +reset()$
        +get(key, default) Any
        +set(key, value)
    }
    ConfigManager --> ConfigManager : _instance
```

## Adapter - XML to JSON reports

Problem: the legacy generator (that we can't modify) returns XML but the dashboard wants JSON. Solution: `LegacyReportAdapter` implements the interface the dashboard expects, wraps the legacy object and converts XML to JSON.

```mermaid
classDiagram
    class ReportGeneratorInterface {
        <<interface>>
        +generate(data) str
    }
    class LegacyReportAdapter {
        -_legacy: LegacyReportGenerator
        +generate(data) str
    }
    class LegacyReportGenerator {
        +generate_report(data) str
    }
    class AnalyticsDashboard {
        +display(json_data)
    }
    ReportGeneratorInterface <|.. LegacyReportAdapter
    LegacyReportAdapter o--> LegacyReportGenerator : adapts
    AnalyticsDashboard ..> ReportGeneratorInterface : uses JSON from
```

## Decorator - order pricing

Problem: 5 boolean flags in one method and the order of the operations is not clear. Solution: each option is a decorator that wraps an `OrderComponent`, and the order you wrap them is the order of the calculation.

```mermaid
classDiagram
    class OrderComponent {
        <<interface>>
        +get_cost() float
        +get_description() str
    }
    class BaseOrder {
        -base_price: float
    }
    class OrderDecorator {
        <<abstract>>
        #_order: OrderComponent
    }
    class ExpressShippingDecorator
    class InsuranceDecorator
    class GiftWrapDecorator
    class DiscountDecorator {
        -percent: float
    }
    class PremiumMemberDecorator
    OrderComponent <|.. BaseOrder
    OrderComponent <|.. OrderDecorator
    OrderDecorator o--> OrderComponent : wraps
    OrderDecorator <|-- ExpressShippingDecorator
    OrderDecorator <|-- InsuranceDecorator
    OrderDecorator <|-- GiftWrapDecorator
    OrderDecorator <|-- DiscountDecorator
    DiscountDecorator <|-- PremiumMemberDecorator
```

## Strategy - report formats

Problem: two if/elif chains (generate and save), you can't switch format at runtime and it's hard to test. Solution: one strategy class per format and a `ReportGenerator` with `set_strategy()`. I added HTML at the end without touching the other classes.

```mermaid
classDiagram
    class FormatStrategy {
        <<interface>>
        +extension: str
        +format(data) str
    }
    class PDFFormatStrategy
    class ExcelFormatStrategy
    class CSVFormatStrategy
    class JSONFormatStrategy
    class HTMLFormatStrategy
    class ReportGenerator {
        -data: list
        -_strategy: FormatStrategy
        +set_strategy(strategy)
        +generate_report() str
        +save_report(filename) str
    }
    FormatStrategy <|.. PDFFormatStrategy
    FormatStrategy <|.. ExcelFormatStrategy
    FormatStrategy <|.. CSVFormatStrategy
    FormatStrategy <|.. JSONFormatStrategy
    FormatStrategy <|.. HTMLFormatStrategy
    ReportGenerator o--> "1" FormatStrategy
```

## Template Method - ETL pipelines

Problem: connect, validate, load and cleanup are copy-pasted in the 3 classes. Solution: `run()` is the template method that defines the steps once, subclasses only write `extract()` and `transform()` and can override the hooks `before_run()` / `after_run()`. I added the XML pipeline to check it works.

```mermaid
classDiagram
    class DataPipeline {
        <<abstract>>
        +source_type: str
        +required_keys: tuple
        +run() str
        +extract() list*
        +transform(data) list*
        +connect()
        +validate()
        +load()
        +cleanup()
        +before_run()
        +after_run()
    }
    class CSVPipeline
    class APIPipeline
    class DatabasePipeline
    class XMLPipeline {
        +after_run()
    }
    DataPipeline <|-- CSVPipeline
    DataPipeline <|-- APIPipeline
    DataPipeline <|-- DatabasePipeline
    DataPipeline <|-- XMLPipeline
```
