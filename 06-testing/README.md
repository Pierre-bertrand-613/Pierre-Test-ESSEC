# 06 - Testing & mocking

Slide 93 et https://courses.dallard.tech/ci_cd/testing_python_intro/#mocking

| Fichier | Contenu |
|---|---|
| `groq_chat.py` | `ask_groq()`, l'exemple du cours |
| `test_groq_chat.py` | Tests unitaires avec `mocker` : faux client, vérification de la requête envoyée, simulation d'une panne de l'API, question vide, `mocker.patch` |
| `app.py` | L'API FastAPI de la slide 93, corrigée (`import os` manquant, client injecté via `Depends`, modèle mixtral retiré par Groq) |
| `test_app.py` | Tests d'intégration avec `TestClient` + `app.dependency_overrides` : `/status`, `/chat`, body invalide (422), et chaque erreur Groq transformée en code HTTP (500 / 429 / 503) |

```bash
python3 -m pytest      # aucun appel réel à l'API, aucune clé nécessaire
```

> Règle du mocking : on mocke ce qu'on ne possède pas (l'API Groq) et on teste ce qu'on possède (validation, requête envoyée, gestion d'erreurs).
>
> La clé API se met dans une variable d'environnement (`export GROQ_API_KEY=...`) ou dans un fichier `.env` ignoré par Git, **jamais dans le repo public**.
