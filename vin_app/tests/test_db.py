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
    assert data["VIN"] == "1XP5DB9X7XD487964"
    assert not data["Cached Result?"]

    response = client.get("/lookup/1XP5DB9X7XD487964")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["VIN"] == "1XP5DB9X7XD487964"
    assert data["Cached Result?"]


def test_lookup_vin_not_in_cache():
    client.get("/remove/1M2AX09C88M003743")
    response = client.get("/lookup/1M2AX09C88M003743")
    assert response.status_code == 200
    assert response.json() == {
        "Body Class": "Truck",
        "Cached Result?": False,
        "Make": "MACK",
        "Model": "GU (Granite)",
        "Model Year": "2008",
        "VIN": "1M2AX09C88M003743",
    }


def test_vin_does_not_exist_at_dot():
    response = client.get("/lookup/1XP5DB9X7XD487945")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "1XP5DB9X7XD487945 1 - Check Digit (9th position) does not calculate properly"
    }


def test_remove_cached_vin():
    client.get("/lookup/1XP5DB9X7XD487964")
    response = client.get("/lookup/1XP5DB9X7XD487964")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["VIN"] == "1XP5DB9X7XD487964"
    assert data["Cached Result?"]
    response = client.get("/remove/1XP5DB9X7XD487964")
    assert response.status_code == 200
    assert response.json() == {"Success": True}
    # Now make sure it's actually removed. This should return false.
    response = client.get("/remove/1XP5DB9X7XD487964")
    assert response.status_code == 200
    assert response.json() == {"Success": False}


def test_fail_remove_not_cached_vin():
    response = client.get("/remove/1XP5DB9X7XD487964")
    assert response.status_code == 200
    assert not response.json()["Success"]
