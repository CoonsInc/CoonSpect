import pytest
from starlette.testclient import TestClient
from httpx import Response
from src.app.main import app
from src.app.api.schemas.status import Status
from src.tests.conftest import client

def test_health(client):
    response: Response = client.get("/")
    assert response.status_code == 200
    assert response.json() == Status.success().model_dump()
