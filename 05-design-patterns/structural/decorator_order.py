"""Decorator pattern - refactor of the order pricing system.

Problems of the original code:
- boolean flag explosion: each new option = a new parameter
- one method does everything -> violates Single Responsibility
- new option = modify existing code -> violates Open/Closed
- option logic can't be reused, and the order of operations is unclear
"""
from abc import ABC, abstractmethod


class OrderComponent(ABC):
    @abstractmethod
    def get_cost(self) -> float: ...

    @abstractmethod
    def get_description(self) -> str: ...


class BaseOrder(OrderComponent):
    def __init__(self, base_price: float):
        self.base_price = base_price

    def get_cost(self) -> float:
        return self.base_price

    def get_description(self) -> str:
        return f"Base price: {self.base_price:.2f}€"


class OrderDecorator(OrderComponent):
    """Wraps another component and delegates to it by default."""

    def __init__(self, order: OrderComponent):
        self._order = order

    def get_cost(self) -> float:
        return self._order.get_cost()

    def get_description(self) -> str:
        return self._order.get_description()


class ExpressShippingDecorator(OrderDecorator):
    COST = 15.00

    def get_cost(self) -> float:
        return self._order.get_cost() + self.COST

    def get_description(self) -> str:
        return f"{self._order.get_description()}\nExpress shipping: +{self.COST:.2f}€"


class InsuranceDecorator(OrderDecorator):
    """5% of the cost of the wrapped order (wrap it first to insure only the base price)."""

    RATE = 0.05

    def _insurance(self) -> float:
        return self._order.get_cost() * self.RATE

    def get_cost(self) -> float:
        return self._order.get_cost() + self._insurance()

    def get_description(self) -> str:
        return f"{self._order.get_description()}\nInsurance (5%): +{self._insurance():.2f}€"


class GiftWrapDecorator(OrderDecorator):
    COST = 5.00

    def get_cost(self) -> float:
        return self._order.get_cost() + self.COST

    def get_description(self) -> str:
        return f"{self._order.get_description()}\nGift wrap: +{self.COST:.2f}€"


class DiscountDecorator(OrderDecorator):
    def __init__(self, order: OrderComponent, percent: float):
        super().__init__(order)
        if not 0 < percent <= 100:
            raise ValueError("percent must be in ]0, 100]")
        self.percent = percent

    def _discount(self) -> float:
        return self._order.get_cost() * self.percent / 100

    def get_cost(self) -> float:
        return self._order.get_cost() - self._discount()

    def get_description(self) -> str:
        return f"{self._order.get_description()}\nDiscount ({self.percent:g}%): -{self._discount():.2f}€"


class PremiumMemberDecorator(DiscountDecorator):
    """A premium member gets a fixed 10% discount: reuse DiscountDecorator."""

    def __init__(self, order: OrderComponent):
        super().__init__(order, percent=10)

    def get_description(self) -> str:
        return f"{self._order.get_description()}\nPremium member (10%): -{self._discount():.2f}€"


if __name__ == "__main__":
    simple = BaseOrder(100.00)
    print(simple.get_description())
    print(f"TOTAL: {simple.get_cost():.2f}€\n---")

    # The order of the decorators is the order of operations: it is explicit now
    # Insurance wraps the base order first, so it is 5% of the base price like in the original code
    order = BaseOrder(100.00)
    order = InsuranceDecorator(order)
    order = ExpressShippingDecorator(order)
    order = GiftWrapDecorator(order)
    order = DiscountDecorator(order, percent=15)
    order = PremiumMemberDecorator(order)
    print(order.get_description())
    print(f"TOTAL: {order.get_cost():.2f}€")
