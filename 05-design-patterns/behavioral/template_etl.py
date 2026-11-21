"""Template Method pattern - refactor of the data ETL pipelines.

Problems of the original code (answers to the questions):
1. Validation logic is repeated 3 times (only the required keys change).
2. Cleanup logic is repeated 3 times, identically.
3. Adding logging means editing every pipeline class.
4. Changing the workflow order means editing every run() method, and one may be forgotten.
5. About 2/3 of each class is duplicated (connect, validate, load, cleanup).
"""
import time
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from typing import List, Tuple


class DataPipeline(ABC):
    source_type = "source"
    required_keys: Tuple[str, ...] = ()
    delay = 0.5                       # simulated network / disk latency

    def __init__(self, source: str):
        self.source = source
        self.data: List[dict] = []

    # ----- Template method: the workflow is defined ONCE and can't be skipped -----
    def run(self) -> str:
        self.before_run()
        self.connect()
        self.data = self.extract()
        print(f"Extracted {len(self.data)} records")
        print(f"Transforming {self.source_type} data...")
        self.data = self.transform(self.data)
        print("Transformation complete")
        self.validate()
        self.load()
        self.cleanup()
        self.after_run()
        return f"{self.source_type} Pipeline finished"

    # ----- Steps every subclass MUST implement -----
    @abstractmethod
    def extract(self) -> List[dict]: ...

    @abstractmethod
    def transform(self, data: List[dict]) -> List[dict]: ...

    # ----- Common steps, implemented once -----
    def connect(self) -> None:
        print(f"Connecting to {self.source_type}: {self.source}")
        time.sleep(self.delay)
        print(f"{self.source_type} connection established")

    def validate(self) -> None:
        print("Validating data...")
        for record in self.data:
            if any(key not in record for key in self.required_keys):
                raise ValueError("Invalid record structure")
        print("Validation passed")

    def load(self) -> None:
        print("Loading data to destination...")
        time.sleep(self.delay)
        print(f"Loaded {len(self.data)} records successfully")

    def cleanup(self) -> None:
        print("Cleaning up resources...")
        self.data = []
        print("Cleanup complete")

    # ----- Hooks: optional, do nothing by default -----
    def before_run(self) -> None:
        pass

    def after_run(self) -> None:
        pass


class CSVPipeline(DataPipeline):
    source_type = "CSV"
    required_keys = ("id", "name")

    def extract(self) -> List[dict]:
        print("Extracting data from CSV...")
        return [{"id": 1, "name": "Alice", "age": "30"}, {"id": 2, "name": "Bob", "age": "25"}]

    def transform(self, data):
        return [{**r, "age": int(r["age"]), "name": r["name"].upper()} for r in data]


class APIPipeline(DataPipeline):
    source_type = "API"
    required_keys = ("user_id", "username")

    def extract(self) -> List[dict]:
        print("Extracting data from API...")
        return [{"user_id": 101, "username": "Charlie", "score": "85"},
                {"user_id": 102, "username": "Diana", "score": "92"}]

    def transform(self, data):
        result = []
        for r in data:
            score = int(r["score"])
            result.append({**r, "score": score, "username": r["username"].lower(),
                           "grade": "A" if score >= 90 else "B"})
        return result


class DatabasePipeline(DataPipeline):
    source_type = "Database"
    required_keys = ("product_id", "price")

    def extract(self) -> List[dict]:
        print("Extracting data from database...")
        return [{"product_id": 501, "product_name": "laptop", "price": 1200},
                {"product_id": 502, "product_name": "mouse", "price": 25}]

    def transform(self, data):
        return [{**r, "price": float(r["price"]), "product_name": r["product_name"].title(),
                 "tax": float(r["price"]) * 0.2} for r in data]


# Validation of the design: a new XML pipeline, nothing else changed
class XMLPipeline(DataPipeline):
    source_type = "XML"
    required_keys = ("order_id", "amount")
    SAMPLE = """<orders>
        <order><order_id>1001</order_id><customer>alice</customer><amount>59.90</amount></order>
        <order><order_id>1002</order_id><customer>bob</customer><amount>120.00</amount></order>
    </orders>"""

    def extract(self) -> List[dict]:
        print("Extracting data from XML...")
        root = ET.fromstring(self.SAMPLE)
        return [{child.tag: child.text for child in order} for order in root]

    def transform(self, data):
        return [{"order_id": int(r["order_id"]), "customer": r["customer"].capitalize(),
                 "amount": float(r["amount"])} for r in data]

    def after_run(self) -> None:          # uses a hook
        print("XML pipeline: archiving source file")


if __name__ == "__main__":
    for pipeline in (CSVPipeline("data/users.csv"),
                     APIPipeline("https://api.example.com/users"),
                     DatabasePipeline("postgresql://localhost/mydb"),
                     XMLPipeline("data/orders.xml")):
        print(f"RUNNING {pipeline.source_type.upper()} PIPELINE")
        print("=" * 70)
        print(f"\n{pipeline.run()}\n")
