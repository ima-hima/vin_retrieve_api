from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..database import Base
from ..main import app, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_create_vehicle():
    response = client.get("/lookup/1XP5DB9X7XD487964")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["vin"] == "1XP5DB9X7XD487964"
    assert not data["Cached Result?"]

    response = client.get("/lookup/1XP5DB9X7XD487964")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["vin"] == "1XP5DB9X7XD487964"
    assert data["Cached Result?"]
