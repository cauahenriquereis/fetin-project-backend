import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from main import app
from dependencies import pegar_sessao, verify_token


@pytest.fixture
def mock_session():
    return MagicMock()


@pytest.fixture
def client(mock_session):
    app.dependency_overrides[pegar_sessao] = lambda: mock_session
    app.dependency_overrides[verify_token] = lambda: True 

    yield TestClient(app)

    app.dependency_overrides.clear()