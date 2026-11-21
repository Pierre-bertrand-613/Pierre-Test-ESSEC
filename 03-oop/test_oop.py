import pytest

from inheritance import Bicycle, BankAccount, Car, Employee, SavingsAccount, Student, Vehicle
from operator_overloading import Circle, Complex, Matrix, Person, Point, Vector


def test_complex_add_sub():
    assert Complex(1, 2) + Complex(3, 4) == Complex(4, 6)
    assert Complex(1, 2) - Complex(3, 4) == Complex(-2, -2)


def test_person_compared_by_age():
    assert Person("A", 30, "F") > Person("B", 20, "M")
    assert not Person("A", 20, "F") > Person("B", 30, "M")


def test_vector_dot_product():
    assert Vector(1, 2, 3) * Vector(4, 5, 6) == 32


def test_circle_comparisons():
    small, big = Circle(1), Circle(2)
    assert small < big and small <= big and big > small and big >= small
    assert small != big and Circle(1) == small


def test_point_compared_by_distance():
    assert Point(3, 4) == Point(-4, 3)
    assert Point(1, 1) < Point(3, 4)
    assert Point(3, 4) >= Point(0, 5)


def test_matrix_multiplication():
    assert Matrix([[1, 2], [3, 4]]) * Matrix([[5, 6], [7, 8]]) == Matrix([[19, 22], [43, 50]])
    with pytest.raises(ValueError):
        Matrix([[1, 2]]) * Matrix([[1, 2]])


def test_vehicles_override_drive():
    assert [v.drive() for v in (Vehicle(), Car(), Bicycle())] == [
        "Driving a vehicle", "Driving a car", "Riding a bicycle"]


def test_introduce_is_personalized():
    assert "Computer Science" in Student("A", 20, "Lyon", "Computer Science").introduce()
    assert "Airbus" in Employee("B", 35, "Nice", "Airbus").introduce()


def test_bank_transfer():
    src, dst = BankAccount("1", 100), BankAccount("2", 0)
    assert src.transfer(dst, 60) is True
    assert (src.balance, dst.balance) == (40, 60)
    assert src.transfer(dst, 100) is False
    assert (src.balance, dst.balance) == (40, 60)


def test_savings_interest():
    account = SavingsAccount("3", 1000, interest_rate=0.05)
    account.add_interest()
    assert account.check_balance() == pytest.approx(1050)
    assert isinstance(account, BankAccount)
