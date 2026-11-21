# 04 - UML exercises

Énoncé : https://gist.github.com/bdallard/2d2407c4de4c182afca6d3ec7235e9eb (slide 68)

Les diagrammes sont écrits en [Mermaid](https://mermaid.js.org/) : GitHub les affiche directement dans les fichiers `.md`.

| Exercice | Diagrammes | Code |
|---|---|---|
| Exo 1 - Hospital Management System | [`hospital.md`](hospital.md) : classes (tasks 1-3), séquence du scénario, 3 diagrammes de séquence système, réponses aux questions | [`hospital.py`](hospital.py) |
| Exo 2 - ABCD Records | [`abcd_records.md`](abcd_records.md) : cas d'utilisation (include/extend), classes, scénario Royal, 4 diagrammes de séquence | [`abcd_records.py`](abcd_records.py) |

```bash
python3 hospital.py
python3 abcd_records.py
python3 -m pytest
```
