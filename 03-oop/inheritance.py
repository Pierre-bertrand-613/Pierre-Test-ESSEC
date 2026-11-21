"""OOP exercises - Inheritance.

Statement: https://gist.github.com/bdallard/b2f2c910e3a9b564a30c86991c97b4fc
"""


# Problem 1 - Vehicle / Car / Bicycle
class Vehicle:
    def drive(self) -> str:
        return "Driving a vehicle"


class Car(Vehicle):
    def drive(self) -> str:
        return "Driving a car"


class Bicycle(Vehicle):
    def drive(self) -> str:
        return "Riding a bicycle"


# Problem 2 - Person / Student / Employee
class Person:
    def __init__(self, name: str, age: int, address: str):
        self.name = name
        self.age = age
        self.address = address

    def introduce(self) -> str:
        return f"Hi, I'm {self.name}, I'm {self.age} and I live in {self.address}."


class Student(Person):
    def __init__(self, name: str, age: int, address: str, field_of_study: str):
        super().__init__(name, age, address)
        self.field_of_study = field_of_study

    def introduce(self) -> str:
        return f"{super().introduce()} I study {self.field_of_study}."


class Employee(Person):
    def __init__(self, name: str, age: int, address: str, company: str):
        super().__init__(name, age, address)
        self.company = company

    def introduce(self) -> str:
        return f"{super().introduce()} I work at {self.company}."


# Problem 3 - BankAccount / SavingsAccount
class BankAccount:
    def __init__(self, account_number: str, balance: float = 0.0):
        self.account_number = account_number
        self.balance = balance

    def deposit(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
        return self.balance

    def withdraw(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient balance")
        self.balance -= amount
        return self.balance

    def transfer(self, destination: "BankAccount", amount: float) -> bool:
        """Move money to another account. Return False if the balance is too low."""
        if amount <= 0 or amount > self.balance:
            return False
        self.withdraw(amount)
        destination.deposit(amount)
        return True


class SavingsAccount(BankAccount):
    def __init__(self, account_number: str, balance: float = 0.0, interest_rate: float = 0.02):
        super().__init__(account_number, balance)
        self.interest_rate = interest_rate

    def add_interest(self) -> float:
        interest = self.balance * self.interest_rate
        self.balance += interest
        return interest

    def check_balance(self) -> float:
        return self.balance


if __name__ == "__main__":
    for vehicle in (Vehicle(), Car(), Bicycle()):   # polymorphism
        print(vehicle.drive())

    people = [
        Person("Pierre", 21, "Paris"),
        Student("Alice", 20, "Lyon", "Computer Science"),
        Employee("Bob", 35, "Nice", "Airbus"),
    ]
    for person in people:
        print(person.introduce())

    checking = BankAccount("FR-001", 100)
    savings = SavingsAccount("FR-002", 1000, interest_rate=0.05)
    print(checking.transfer(savings, 50))    # True
    print(checking.transfer(savings, 500))   # False (insufficient balance)
    savings.add_interest()
    print(savings.check_balance())           # 1102.5
