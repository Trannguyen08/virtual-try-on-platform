from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from backend.core.config import Settings
from backend.main import create_app
from backend.db.models import Base
from backend.db.session import make_engine


@pytest.fixture
def isolated_main_database(tmp_path, monkeypatch):
    """Each test gets a fresh metadata database; production uses PostgreSQL."""
    url = f"sqlite+pysqlite:///{(tmp_path / 'main.sqlite3').as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    engine = make_engine(url)
    Base.metadata.create_all(engine)
    engine.dispose()


@pytest.fixture
def app(isolated_main_database):
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
