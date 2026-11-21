"""ABCD Records - implementation of the UML in abcd_records.md."""
import itertools
from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional, Union


# --- Customers -------------------------------------------------------------
class NonMember:
    def __init__(self, name: str, address: str):
        self.name = name
        self.address = address


class MembershipApplication:
    def __init__(self, applicant: NonMember):
        self.applicant = applicant
        self.sent_at = date.today()


class Member(ABC):
    _ids = itertools.count(1)

    def __init__(self, name: str, address: str):
        self.member_id = next(Member._ids)
        self.name = name
        self.address = address

    @abstractmethod
    def discount_rate(self) -> float: ...

    @abstractmethod
    def can_order_unavailable(self) -> bool: ...

    def place_order(self) -> "Order":
        return Order(self)


class RoyalMember(Member):
    def discount_rate(self) -> float:
        return 0.10

    def can_order_unavailable(self) -> bool:
        return True


class RegularMember(Member):
    def discount_rate(self) -> float:
        return 0.0

    def can_order_unavailable(self) -> bool:
        return False


# --- Items -----------------------------------------------------------------
class Item(ABC):
    def __init__(self, code: str, title: str, artist: str, price: float, stock: int):
        self.code = code
        self.title = title
        self.artist = artist
        self.price = price
        self.stock = stock

    def is_available(self, quantity: int) -> bool:
        return self.stock >= quantity


class CD(Item):
    def __init__(self, code, title, artist, price, stock, tracks: int = 12):
        super().__init__(code, title, artist, price, stock)
        self.tracks = tracks


class Tape(Item):
    def __init__(self, code, title, artist, price, stock, duration_min: int = 60):
        super().__init__(code, title, artist, price, stock)
        self.duration_min = duration_min


# --- Orders ----------------------------------------------------------------
class OrderLine:
    def __init__(self, item: Item, quantity: int, backordered: bool = False):
        self.item = item
        self.quantity = quantity
        self.backordered = backordered

    def line_total(self) -> float:
        return self.item.price * self.quantity


class Order:
    _ids = itertools.count(1)

    def __init__(self, member: Member):
        self.order_id = next(Order._ids)
        self.member = member
        self.date = date.today()
        self.lines: List[OrderLine] = []   # composition: lines live and die with the order
        self.status = "new"

    def add_line(self, item: Item, quantity: int, backordered: bool = False) -> None:
        self.lines.append(OrderLine(item, quantity, backordered))

    def subtotal(self) -> float:
        return sum(line.line_total() for line in self.lines)

    def total(self) -> float:
        return round(self.subtotal() * (1 - self.member.discount_rate()), 2)


class Invoice:
    def __init__(self, order: Order):
        self.order = order
        self.amount = order.total()
        self.paid = False

    def print(self) -> str:
        return f"INVOICE order #{self.order.order_id} - {self.order.member.name}: {self.amount}€"


class ShippingList:
    def __init__(self, order: Order):
        # Only items that are in stock can be shipped now
        self.lines = [line for line in order.lines if not line.backordered]

    def print(self) -> str:
        return "SHIPPING: " + ", ".join(f"{l.quantity}x {l.item.title}" for l in self.lines)


# --- Payments --------------------------------------------------------------
class Payment(ABC):
    def __init__(self, amount: float):
        self.amount = amount
        self.date = date.today()

    @abstractmethod
    def process(self) -> str: ...


class Cash(Payment):
    def process(self) -> str:
        return f"Cash {self.amount}€"


class Check(Payment):
    def __init__(self, amount: float, check_number: str, bank: str):
        super().__init__(amount)
        self.check_number = check_number
        self.bank = bank

    def process(self) -> str:
        return f"Check #{self.check_number} ({self.bank}) {self.amount}€"


class BankDraft(Payment):
    def __init__(self, amount: float, draft_number: str):
        super().__init__(amount)
        self.draft_number = draft_number

    def process(self) -> str:
        return f"Bank draft #{self.draft_number} {self.amount}€"


# --- Staff -----------------------------------------------------------------
class DailyRecordsFile:
    def __init__(self):
        self.date = date.today()
        self.orders: List[Order] = []

    def save(self, order: Order) -> None:
        self.orders.append(order)


class OrderProcessingClerk:
    def __init__(self, records: DailyRecordsFile):
        self.records = records

    def verify_membership(self, customer: Union[Member, NonMember]) -> Optional[MembershipApplication]:
        """Return None for members, a membership application for non-members."""
        if isinstance(customer, Member):
            return None
        return MembershipApplication(customer)

    def process_order(self, member: Member, wanted: List[tuple]):
        """wanted = [(item, quantity), ...]. Returns (order, invoice, shipping_list)."""
        order = member.place_order()
        for item, quantity in wanted:
            if item.is_available(quantity):
                item.stock -= quantity
                order.add_line(item, quantity)
            elif member.can_order_unavailable():
                order.add_line(item, quantity, backordered=True)   # Royal privilege
            # Regular members simply cannot order unavailable items
        if not order.lines:
            raise ValueError("Nothing could be ordered")
        order.status = "processed"
        self.records.save(order)
        return order, Invoice(order), ShippingList(order)


class CollectionDeptClerk:
    def collect_payment(self, invoice: Invoice, payment: Payment) -> str:
        if payment.amount < invoice.amount:
            raise ValueError("Insufficient payment")
        invoice.paid = True
        invoice.order.status = "paid"
        return payment.process()


if __name__ == "__main__":
    # Scenario: Royal member orders 2 CDs (one unavailable) and pays by check
    records = DailyRecordsFile()
    clerk = OrderProcessingClerk(records)
    collector = CollectionDeptClerk()

    royal = RoyalMember("Pierre", "Paris")
    cd_a = CD("CD-001", "Discovery", "Daft Punk", 15.0, stock=3)
    cd_b = CD("CD-002", "Random Access Memories", "Daft Punk", 20.0, stock=0)

    assert clerk.verify_membership(royal) is None
    order, invoice, shipping = clerk.process_order(royal, [(cd_a, 1), (cd_b, 1)])
    print(invoice.print())        # (15 + 20) * 0.9 = 31.5€
    print(shipping.print())       # only Discovery is shipped now
    print(collector.collect_payment(invoice, Check(invoice.amount, "0042", "BNP")))

    visitor = NonMember("Alice", "Lyon")
    print(type(clerk.verify_membership(visitor)).__name__)  # MembershipApplication
