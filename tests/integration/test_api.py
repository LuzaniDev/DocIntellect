import pytest
from httpx import AsyncClient, ASGITransport

from app.api.main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_root_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_upload_invalid_file_type(client):
    response = await client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.txt", b"conteudo", "text/plain")},
    )
    assert response.status_code == 400
