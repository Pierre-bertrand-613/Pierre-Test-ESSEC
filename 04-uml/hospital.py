"""Hospital Management System - implementation of the UML in hospital.md."""
import hashlib
import itertools
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import List, Optional


class ProblemStatus(Enum):
    PENDING = "pending"
    IN_REVIEW = "in-review"
    RESOLVED = "resolved"


class User(ABC):
    """Shared attributes of every member of the platform."""

    _ids = itertools.count(1)

    def __init__(self, name: str, password: str):
        self.id = next(User._ids)
        self.name = name
        self._password_hash = self._hash(password)
        self.logged_in = False

    @staticmethod
    def _hash(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self, password: str) -> bool:
        self.logged_in = self._hash(password) == self._password_hash
        return self.logged_in

    def logout(self) -> None:
        self.logged_in = False

    def __repr__(self) -> str:
        return f"{type(self).__name__}(id={self.id}, name={self.name!r})"


class HealthProblem:
    _ids = itertools.count(1)

    def __init__(self, patient: "Patient", description: str):
        self.id = next(HealthProblem._ids)
        self.patient = patient
        self.description = description
        self.status = ProblemStatus.PENDING
        self.created_at = datetime.now()
        self.doctor: Optional["Doctor"] = None
        self.prescription: Optional["Prescription"] = None  # composition

    def set_status(self, status: ProblemStatus) -> None:
        self.status = status


class Prescription:
    _ids = itertools.count(1)

    def __init__(self, doctor: "Doctor", problem: HealthProblem, content: str, fee: float,
                 previous: Optional["Prescription"] = None):
        self.id = next(Prescription._ids)
        self.doctor = doctor
        self.problem = problem
        self.content = content
        self.fee = fee
        self.previous = previous          # reference to the patient's past prescription
        self.created_at = datetime.now()
        self.delivered = False


# --- Payment strategy: polymorphism instead of if/elif on the payment type ---
class Payment(ABC):
    def __init__(self, amount: float):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self.amount = amount
        self.prescription: Optional[Prescription] = None
        self.paid_at: Optional[datetime] = None
        self.forwarded = False

    @abstractmethod
    def process(self) -> str:
        """Run the payment with this method; return a receipt line."""


class CheckPayment(Payment):
    def __init__(self, amount: float, check_number: str):
        super().__init__(amount)
        self.check_number = check_number

    def process(self) -> str:
        return f"Check #{self.check_number} of {self.amount}€ received"


class CashPayment(Payment):
    def process(self) -> str:
        return f"Cash payment of {self.amount}€ received"


class CreditCardPayment(Payment):
    def __init__(self, amount: float, card_number: str):
        super().__init__(amount)
        if len(card_number) != 16 or not card_number.isdigit():
            raise ValueError("Invalid card number")
        self.card_number = card_number

    def process(self) -> str:
        return f"Card ****{self.card_number[-4:]} charged {self.amount}€"


class Patient(User):
    def __init__(self, name: str, password: str):
        super().__init__(name, password)
        self.problems: List[HealthProblem] = []
        self.payments: List[Payment] = []

    def post_problem(self, description: str) -> HealthProblem:
        problem = HealthProblem(self, description)
        self.problems.append(problem)
        return problem

    def past_prescriptions(self) -> List[Prescription]:
        return [p.prescription for p in self.problems if p.prescription is not None]

    def pay(self, prescription: Prescription, payment: Payment) -> str:
        if not prescription.delivered:
            raise ValueError("Prescription has not been delivered yet")
        if payment.amount != prescription.fee:
            raise ValueError("Payment amount does not match the prescription fee")
        receipt = payment.process()
        payment.prescription = prescription
        payment.paid_at = datetime.now()
        self.payments.append(payment)
        prescription.problem.set_status(ProblemStatus.RESOLVED)
        return receipt


class Doctor(User):
    def __init__(self, name: str, password: str, speciality: str):
        super().__init__(name, password)
        self.speciality = speciality
        self.earnings = 0.0

    def write_prescription(self, problem: HealthProblem, content: str, fee: float) -> Prescription:
        if problem.doctor is not self:
            raise PermissionError("This problem is not assigned to this doctor")
        past = problem.patient.past_prescriptions()
        prescription = Prescription(self, problem, content, fee, previous=past[-1] if past else None)
        problem.prescription = prescription
        return prescription

    def receive_payment(self, amount: float) -> None:
        self.earnings += amount


class Organizer(User):
    """Coordinates patients and doctors, and acts as administrator."""

    def __init__(self, name: str, password: str):
        super().__init__(name, password)
        self.members: List[User] = []

    def register_member(self, kind: str, name: str, password: str, **extra) -> User:
        classes = {"patient": Patient, "doctor": Doctor}
        member = classes[kind](name, password, **extra)
        self.members.append(member)
        return member

    def assign_doctor(self, problem: HealthProblem, doctor: Doctor) -> None:
        problem.doctor = doctor
        problem.set_status(ProblemStatus.IN_REVIEW)

    def send_prescription(self, problem: HealthProblem) -> Prescription:
        if problem.prescription is None:
            raise ValueError("No prescription yet for this problem")
        problem.prescription.delivered = True
        return problem.prescription

    def forward_payment(self, payment: Payment) -> None:
        if payment.forwarded:
            raise ValueError("Payment already forwarded")   # data integrity
        if payment.prescription is None:
            raise ValueError("Payment has not been processed")
        payment.prescription.doctor.receive_payment(payment.amount)
        payment.forwarded = True


if __name__ == "__main__":
    organizer = Organizer("Admin", "admin")
    patient = organizer.register_member("patient", "Pierre", "secret")
    doctor = organizer.register_member("doctor", "Dr House", "vicodin", speciality="Diagnostic")

    problem = patient.post_problem("Headache for 3 days")
    organizer.assign_doctor(problem, doctor)
    doctor.write_prescription(problem, "Paracetamol 1g, 3x/day", fee=25.0)
    prescription = organizer.send_prescription(problem)
    payment = CreditCardPayment(25.0, "1234567812345678")
    print(patient.pay(prescription, payment))
    organizer.forward_payment(payment)
    print(problem.status, doctor.earnings)
