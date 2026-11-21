# 06 - Testing & mocking

Slide 93 + https://courses.dallard.tech/ci_cd/testing_python_intro/#mocking

- `groq_chat.py`: the `ask_groq()` function from the course
- `test_groq_chat.py`: unit tests with `mocker` (fake client, check the request we send, simulate the API being down, empty question)
- `app.py`: the FastAPI app from slide 93. I had to fix a few things: `import os` was missing, the mixtral model doesn't exist anymore on Groq, and I create the client with `Depends` so I can replace it in the tests
- `test_app.py`: tests of the API with `TestClient` (/status, /chat, and each Groq error -> 500 / 429 / 503)

```bash
python3 -m pytest   # no real API call, no key needed
```

Rule from the course: mock what you don't own (the API), test what you own (validation, error handling).
The API key goes in an environment variable (`GROQ_API_KEY`), never in the repo.
