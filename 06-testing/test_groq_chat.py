"""Unit tests with mocks: no API key, no network, no tokens burnt.

Mocking rule: mock what you don't own (the Groq API), test what you own
(validation, the request we send, error handling).
"""
import pytest

from groq_chat import MODEL, ask_groq


def test_ask_groq(make_fake_client):
    assert ask_groq("What is 2+2?", client=make_fake_client()) == "4"


def test_ask_groq_calls_api_correctly(make_fake_client):
    client = make_fake_client()
    ask_groq("What is 2+2?", client=client)
    client.chat.completions.create.assert_called_once_with(
        model=MODEL,
        messages=[{"role": "user", "content": "What is 2+2?"}],
        max_tokens=1024,
    )


def test_ask_groq_raises_error_when_api_fails(mocker):
    client = mocker.Mock()
    client.chat.completions.create.side_effect = Exception("API down")
    with pytest.raises(Exception, match="API down"):
        ask_groq("Hello", client=client)


@pytest.mark.parametrize("question", ["", "   ", "\n"])
def test_empty_question_never_calls_the_api(make_fake_client, question):
    client = make_fake_client()
    with pytest.raises(ValueError):
        ask_groq(question, client=client)
    client.chat.completions.create.assert_not_called()


def test_default_client_is_created_when_none_given(mocker, make_fake_client):
    fake = make_fake_client("hi")
    groq_class = mocker.patch("groq_chat.Groq", return_value=fake)   # patch where it is used
    assert ask_groq("Hello") == "hi"
    groq_class.assert_called_once_with()
