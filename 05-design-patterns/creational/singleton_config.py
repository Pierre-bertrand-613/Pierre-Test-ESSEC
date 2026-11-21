"""Singleton pattern - refactor of the configuration manager.

Problems of the original code:
- config.json is read from disk on every call (wasteful I/O)
- no shared state: each module has its own copy, changes are not synchronized
- hard to mock in tests: no single point to override
"""
import json
from pathlib import Path
from typing import Any, Optional

DEFAULT_CONFIG_PATH = Path(__file__).with_name("config.json")


class ConfigManager:
    _instance: Optional["ConfigManager"] = None

    def __init__(self, path: Path = DEFAULT_CONFIG_PATH):
        if ConfigManager._instance is not None:
            raise RuntimeError("Use ConfigManager.get_instance() instead")
        print(f"Loading config from {path.name}")   # shows the file is read only once
        with open(path, "r") as f:
            self._config = json.load(f)

    @classmethod
    def get_instance(cls) -> "ConfigManager":
        """Create the instance on first access, then always return the same one."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Only for tests: forget the instance so the next call reloads the file."""
        cls._instance = None

    def get(self, key: str, default: Any = None) -> Any:
        """Access nested values with a dotted key, e.g. get('database.host')."""
        value: Any = self._config
        for part in key.split("."):
            if not isinstance(value, dict) or part not in value:
                return default
            value = value[part]
        return value

    def set(self, key: str, value: Any) -> None:
        """Change a value: every module sees it, since they share the instance."""
        *parents, last = key.split(".")
        node = self._config
        for part in parents:
            node = node.setdefault(part, {})
        node[last] = value


# database.py
def connect_database():
    config = ConfigManager.get_instance()
    print(f"Connecting to database at {config.get('database.host')}:{config.get('database.port')}")


# email_service.py
def send_email(to: str, subject: str):
    config = ConfigManager.get_instance()
    print(f"Sending email from {config.get('email.sender')} via {config.get('email.smtp_host')}")


# payment_service.py
def process_payment(amount: float):
    config = ConfigManager.get_instance()
    print(f"Processing {amount}€ in {config.get('payment.environment')} mode")


# app.py
def start_application():
    config = ConfigManager.get_instance()
    print(f"Starting {config.get('app.name')} (debug={config.get('app.debug')})")


if __name__ == "__main__":
    start_application()      # the file is loaded here...
    connect_database()       # ...and never again
    send_email("user@test.com", "Welcome")
    process_payment(99.99)
    print(ConfigManager.get_instance() is ConfigManager.get_instance())  # True
