"""OOP exercises - Operator overloading.

Statement: https://gist.github.com/bdallard/b2f2c910e3a9b564a30c86991c97b4fc
"""
import math
from functools import total_ordering
from typing import List


# Problem 1 - Complex numbers with + and -
class Complex:
    def __init__(self, real: float, imag: float):
        self.real = real
        self.imag = imag

    def __add__(self, other: "Complex") -> "Complex":
        return Complex(self.real + other.real, self.imag + other.imag)

    def __sub__(self, other: "Complex") -> "Complex":
        return Complex(self.real - other.real, self.imag - other.imag)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Complex):
            return NotImplemented
        return self.real == other.real and self.imag == other.imag

    def __repr__(self) -> str:
        sign = "+" if self.imag >= 0 else "-"
        return f"{self.real} {sign} {abs(self.imag)}i"


# Problem 2 - Compare persons by age with >
class Person:
    def __init__(self, name: str, age: int, gender: str):
        self.name = name
        self.age = age
        self.gender = gender

    def __gt__(self, other: "Person") -> bool:
        return self.age > other.age

    def __repr__(self) -> str:
        return f"Person({self.name!r}, {self.age})"


# Problem 4 - Dot product with *
class Vector:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def __mul__(self, other: "Vector") -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def __repr__(self) -> str:
        return f"Vector({self.x}, {self.y}, {self.z})"


# Problem 5 - All comparison operators on a Circle, based on the radius
class Circle:
    def __init__(self, radius: float):
        self.radius = radius

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Circle):
            return NotImplemented
        return self.radius == other.radius

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Circle):
            return NotImplemented
        return self.radius != other.radius

    def __lt__(self, other: "Circle") -> bool:
        return self.radius < other.radius

    def __le__(self, other: "Circle") -> bool:
        return self.radius <= other.radius

    def __gt__(self, other: "Circle") -> bool:
        return self.radius > other.radius

    def __ge__(self, other: "Circle") -> bool:
        return self.radius >= other.radius

    def __repr__(self) -> str:
        return f"Circle({self.radius})"


# Problem 6 - 2D points compared by their distance to the origin.
# @total_ordering builds <=, > and >= from __eq__ and __lt__.
@total_ordering
class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def distance_from_origin(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return self.distance_from_origin() == other.distance_from_origin()

    def __lt__(self, other: "Point") -> bool:
        return self.distance_from_origin() < other.distance_from_origin()

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"


# Problem 7 - Matrix multiplication with *
class Matrix:
    def __init__(self, rows: List[List[float]]):
        if not rows or any(len(row) != len(rows[0]) for row in rows):
            raise ValueError("All rows must have the same, non-zero length")
        self.rows = rows

    @property
    def shape(self):
        return len(self.rows), len(self.rows[0])

    def __mul__(self, other: "Matrix") -> "Matrix":
        n, m = self.shape
        m2, p = other.shape
        if m != m2:
            raise ValueError(f"Cannot multiply {self.shape} by {other.shape}")
        result = [
            [sum(self.rows[i][k] * other.rows[k][j] for k in range(m)) for j in range(p)]
            for i in range(n)
        ]
        return Matrix(result)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Matrix):
            return NotImplemented
        return self.rows == other.rows

    def __repr__(self) -> str:
        return f"Matrix({self.rows})"


if __name__ == "__main__":
    print(Complex(1, 2) + Complex(3, -5))   # 4 - 3i
    print(Complex(1, 2) - Complex(3, -5))   # -2 + 7i

    alice, bob = Person("Alice", 30, "F"), Person("Bob", 25, "M")
    print(alice > bob)                      # True

    print(Vector(1, 2, 3) * Vector(4, 5, 6))  # 32

    print(Circle(2) < Circle(3), Circle(2) == Circle(2), Circle(5) >= Circle(1))

    print(Point(3, 4) > Point(1, 1), Point(3, 4) == Point(4, 3))  # True True

    print(Matrix([[1, 2], [3, 4]]) * Matrix([[5, 6], [7, 8]]))  # [[19, 22], [43, 50]]
