from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from backend.core.config import Settings
from backend.main import create_app


@pytest.fixture
def app():
    # Isolated stores and deterministic CORS regardless of the developer environment.
    return create_app(Settings(cors_origins=("http://localhost:5173",)))


@pytest.fixture
def client(app):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def png_bytes():
    buffer = BytesIO()
    Image.new("RGB", (8, 8), "white").save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.fixture
def body(client, png_bytes):
    response = client.post("/api/tryon/analyze", data={"height_cm": "170"},
                           files={"image": ("demo.png", png_bytes, "image/png")})
    assert response.status_code == 200
    return response.json()["data"]
