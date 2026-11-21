"""Factory pattern - refactor of the payment system.

Problems of the original code:
- one function with an if/elif per payment type -> violates Open/Closed
- validation, fees and processing mixed together -> violates Single Responsibility
- impossible to test one payment method alone
"""
from abc import ABC, abstractmethod
from typing import Dict, Type


class PaymentProcessor(ABC):
    """Interface every payment processor must follow."""

    method = ""
    error_message = "Invalid payment details"

    @abstractmethod
    def validate(self, details: dict) -> bool: ...

    @abstractmethod
    def compute_fee(self, amount: float) -> float: ...

    def process(self, amount: float, details: dict) -> dict:
        if not self.validate(details):
            return {"success": False, "error": self.error_message}
        fee = self.compute_fee(amount)
        return {"success": True, "method": self.method, "amount": amount + fee, "fee": fee}


class CreditCardProcessor(PaymentProcessor):
    method = "credit_card"
    error_message = "Invalid card number or CVV"

    def validate(self, details: dict) -> bool:
        card_number = details.get("card_number") or ""
        cvv = details.get("cvv") or ""
        return len(card_number) == 16 and len(cvv) == 3

    def compute_fee(self, amount: float) -> float:
        return amount * 0.029          # 2.9%


class BankTransferProcessor(PaymentProcessor):
    method = "bank_transfer"
    error_message = "Invalid IBAN"

    def validate(self, details: dict) -> bool:
        return len(details.get("iban") or "") >= 15

    def compute_fee(self, amount: float) -> float:
        return 1.50                    # flat fee


class PayPalProcessor(PaymentProcessor):
    method = "paypal"
    error_message = "Invalid PayPal email"

    def validate(self, details: dict) -> bool:
        return "@" in (details.get("email") or "")

    def compute_fee(self, amount: float) -> float:
        return amount * 0.034 + 0.30   # 3.4% + 0.30€


class PaymentFactory:
    """Maps a string to a processor class: no if/elif chain."""

    _processors: Dict[str, Type[PaymentProcessor]] = {
        "credit_card": CreditCardProcessor,
        "bank_transfer": BankTransferProcessor,
        "paypal": PayPalProcessor,
    }

    @classmethod
    def register(cls, name: str, processor: Type[PaymentProcessor]) -> None:
        """Add a new payment method without modifying the factory code."""
        cls._processors[name] = processor

    def get_processor(self, payment_type: str) -> PaymentProcessor:
        try:
            return self._processors[payment_type]()
        except KeyError:
            raise ValueError(f"Unknown payment type: {payment_type}") from None


# Extension example: Apple Pay added without touching any existing class
class ApplePayProcessor(PaymentProcessor):
    method = "apple_pay"
    error_message = "Missing Apple Pay token"

    def validate(self, details: dict) -> bool:
        return bool(details.get("token"))

    def compute_fee(self, amount: float) -> float:
        return amount * 0.015


PaymentFactory.register("apple_pay", ApplePayProcessor)


if __name__ == "__main__":
    factory = PaymentFactory()
    processor = factory.get_processor("credit_card")
    print(processor.process(100.0, {"card_number": "1234567890123456", "cvv": "123"}))
    print(factory.get_processor("bank_transfer").process(100.0, {"iban": "FR7630006000011234567890189"}))
    print(factory.get_processor("paypal").process(100.0, {"email": "bad-email"}))
    print(factory.get_processor("apple_pay").process(100.0, {"token": "tok_123"}))
