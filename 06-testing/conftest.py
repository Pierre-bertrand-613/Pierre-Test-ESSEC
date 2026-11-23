"""Fixtures shared by the tests of this folder (the course asks for a conftest.py)."""
import pytest


@pytest.fixture
def make_fake_client(mocker):
    """Return a function that builds a fake Groq client answering `answer`."""
    def _make(answer: str = "4"):
        mock_choice = mocker.Mock()
        mock_choice.message.content = answer
        mock_client = mocker.Mock()
        mock_client.chat.completions.create.return_value = mocker.Mock(choices=[mock_choice])
        return mock_client
    return _make
