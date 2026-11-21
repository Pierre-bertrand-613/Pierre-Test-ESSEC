# 03 - OOP exercises

Énoncé : https://gist.github.com/bdallard/b2f2c910e3a9b564a30c86991c97b4fc (slide 67)

| Fichier | Contenu |
|---|---|
| `operator_overloading.py` | `Complex` (`+`, `-`), `Person` (`>` sur l'âge), `Vector` (`*` = produit scalaire), `Circle` (les 6 comparaisons), `Point` (comparaison par distance à l'origine avec `@total_ordering`), `Matrix` (`*` = produit matriciel) |
| `inheritance.py` | `Vehicle`/`Car`/`Bicycle`, `Person`/`Student`/`Employee` (avec `super()`), `BankAccount`/`SavingsAccount` (`transfer`, `add_interest`, `check_balance`) |
| `test_oop.py` | Tests pytest |

```bash
python3 operator_overloading.py
python3 inheritance.py
python3 -m pytest
```

À retenir : quand `__eq__` reçoit un type qu'il ne gère pas, il renvoie `NotImplemented` (et non `False`), pour laisser Python essayer l'opération réfléchie de l'autre objet.
