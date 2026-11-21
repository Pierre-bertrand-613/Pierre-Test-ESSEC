# 05 - Design patterns

Exercices du site du cours :
- [Creational patterns](https://courses.dallard.tech/sys_design/creational_pattern/)
- Structural patterns
- Behavioral patterns

Chaque fichier commence par la liste des problèmes du code « spaghetti » (step 1). Le code refactorisé suit, puis l'usage attendu dans `__main__`.

| Famille | Pattern | Exercice | Fichier |
|---|---|---|---|
| Créationnel | Factory | Payment system | [`creational/factory_payment.py`](creational/factory_payment.py) |
| Créationnel | Builder | HR Employee onboarding | [`creational/builder_employee.py`](creational/builder_employee.py) |
| Créationnel | Singleton | Configuration manager | [`creational/singleton_config.py`](creational/singleton_config.py) |
| Structurel | Adapter | XML → JSON reporting | [`structural/adapter_report.py`](structural/adapter_report.py) |
| Structurel | Decorator | Order pricing | [`structural/decorator_order.py`](structural/decorator_order.py) |
| Comportemental | Strategy | Multi-format reports | [`behavioral/strategy_report.py`](behavioral/strategy_report.py) |
| Comportemental | Template Method | ETL pipelines | [`behavioral/template_etl.py`](behavioral/template_etl.py) |

```bash
python3 creational/factory_payment.py      # etc.
python3 -m pytest                          # 13 tests
```

## Factory : système de paiement

**Problème :** une chaîne `if/elif` sur `payment_type`, qui viole Open/Closed. **Solution :** une classe par processeur, et une factory qui associe une chaîne à une classe grâce à un dictionnaire. `ApplePayProcessor` est ajouté avec `register()` sans modifier aucune classe existante.

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

## Builder : onboarding RH

**Problème :** un constructeur à 17 paramètres (telescoping constructor) et des booléens illisibles. **Solution :** des méthodes chaînables qui renvoient `self`, la validation regroupée dans `build()`, et des presets (`DeveloperBuilder`, `InternBuilder`).

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

## Singleton : gestionnaire de configuration

**Problème :** `config.json` est relu 4 fois, il n'y a pas d'état partagé et le code est difficile à mocker. **Solution :** `get_instance()` charge le fichier une seule fois. `get("database.host")` permet de lire les clés imbriquées, et `reset()` sert dans les tests.

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

## Adapter : rapports XML vers JSON

**Problème :** le générateur legacy (non modifiable) produit du XML, alors que le dashboard attend du JSON. **Solution :** `LegacyReportAdapter` implémente l'interface attendue et *enveloppe* le legacy (composition) pour convertir le XML en JSON.

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

## Decorator : calcul du prix d'une commande

**Problème :** 5 flags booléens dans une seule méthode, et un ordre des opérations implicite. **Solution :** chaque option est un décorateur qui enveloppe un `OrderComponent`. L'ordre d'empilement *est* l'ordre de calcul.

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

## Strategy : rapports multi-formats

**Problème :** deux chaînes `if/elif` (generate et save), on ne peut pas changer de format à l'exécution et le code est peu testable. **Solution :** une stratégie par format, et un contexte `ReportGenerator` avec `set_strategy()`. Le format HTML a été ajouté sans toucher au code existant, ce qui prouve que la conception est extensible.

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

## Template Method : pipelines ETL

**Problème :** connexion, validation, chargement et nettoyage sont copiés-collés dans 3 classes. **Solution :** `run()` (la *template method*) fixe le workflow une seule fois. Les sous-classes implémentent seulement `extract()` et `transform()`, et peuvent redéfinir les hooks `before_run()` et `after_run()`. Le pipeline XML valide la conception.

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
