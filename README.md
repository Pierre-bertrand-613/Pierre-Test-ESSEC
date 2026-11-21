# OOP & Design Patterns in Python - exercices

Exercices du cours *Object Oriented Programming & Design pattern in Python* (Benjamin Dallard, ESSEC - AIDAMS), ressources sur https://courses.dallard.tech/.

| # | Dossier | Exercice | Slide |
|---|---|---|---|
| 1 | [`01-git`](01-git) | Git mini exo : commandes, `install.sh`, questions de réflexion | 26 |
| 2 | [`02-bash`](02-bash) | Bash script exercise : `env_install.sh` (+ tous les bonus) | 13 |
| 3 | [`03-oop`](03-oop) | Surcharge d'opérateurs & héritage | 67 |
| 4 | [`04-uml`](04-uml) | UML : Hospital Management System & ABCD Records (diagrammes + code) | 68 |
| 5 | [`05-design-patterns`](05-design-patterns) | Factory, Builder, Singleton, Adapter, Decorator, Strategy, Template Method | 70-87 |
| 6 | [`06-testing`](06-testing) | Tests unitaires & d'intégration avec mocking (API Groq + FastAPI) | 88-93 |

## Lancer les tests

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 -m pytest
```

## Workflow Git

Chaque exercice a été développé sur sa propre branche (`feature-install`, `feature-bash-env`, `feature-oop`, `feature-uml`, `feature-design-patterns`, `feature-testing`). Chaque branche a ensuite été mergée dans `main` avec `git merge --no-ff` puis supprimée : `git log --graph` montre l'historique.
