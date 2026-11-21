"""Integration tests of the FastAPI app, with the Groq client replaced by a mock."""
import groq
import httpx
import pytest
from fastapi.testclient import TestClient

from app import MODEL, app, get_client

REQUEST = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")


@pytest.fixture
def fake_client(mocker):
    mock_choice = mocker.Mock()
    mock_choice.message.content = "Paris"
    mock_client = mocker.Mock()
    mock_client.chat.completions.create.return_value = mocker.Mock(choices=[mock_choice])
    app.dependency_overrides[get_client] = lambda: mock_client
    yield mock_client
    app.dependency_overrides.clear()


@pytest.fixture
def http():
    return TestClient(app)


def test_status(http):
    response = http.get("/status")
    assert response.status_code == 200
    assert response.json() == {"message": "OK"}


def test_chat_returns_llm_answer(http, fake_client):
    response = http.post("/chat", json={"prompt": "Capital of France?"})
    assert response.status_code == 200
    assert response.json() == {"response": "Paris"}
    kwargs = fake_client.chat.completions.create.call_args.kwargs
    assert kwargs["model"] == MODEL
    assert kwargs["messages"][-1] == {"role": "user", "content": "Capital of France?"}


def test_chat_rejects_invalid_body(http, fake_client):
    assert http.post("/chat", json={"wrong": "field"}).status_code == 422
    fake_client.chat.completions.create.assert_not_called()


@pytest.mark.parametrize("error, status, detail", [
    (groq.APIConnectionError(request=REQUEST), 500, "API Connection Error"),
    (groq.RateLimitError("slow down", response=httpx.Response(429, request=REQUEST), body=None),
     429, "Rate Limit Exceeded"),
    (groq.APIStatusError("unavailable", response=httpx.Response(503, request=REQUEST), body=None),
     503, "API Status Error"),
])
def test_chat_maps_groq_errors_to_http_errors(http, fake_client, error, status, detail):
    fake_client.chat.completions.create.side_effect = error
    response = http.post("/chat", json={"prompt": "Hello"})
    assert response.status_code == status
    assert response.json() == {"detail": detail}
