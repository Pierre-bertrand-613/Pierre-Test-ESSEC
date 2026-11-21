# 03 - OOP exercises

Exercise: https://gist.github.com/bdallard/b2f2c910e3a9b564a30c86991c97b4fc (slide 67)

- `operator_overloading.py`: Complex (+, -), Person (> on age), Vector (* = dot product), Circle (all comparisons), Point (compared by distance to origin), Matrix (* = matrix product)
- `inheritance.py`: Vehicle/Car/Bicycle, Person/Student/Employee, BankAccount/SavingsAccount
- `test_oop.py`: my tests

```bash
python3 operator_overloading.py
python3 inheritance.py
python3 -m pytest
```

Note to self: in `__eq__`, return `NotImplemented` (not `False`) when the other object is not the right type.
