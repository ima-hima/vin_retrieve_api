from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 404
    assert response.json() == {"detail": "Appropriate endpoints are lookup, remove, export."}


def test_lookup_fail_missing_vin():
    """No VIN is included in the url."""
    response = client.get("/lookup")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_lookup_vin_not_in_cache():
    response = client.get("/lookup/1M2AX09C88M003743")
    assert response.status_code == 200
    assert response.json() == {
        'Body Class': 'Truck',
        'Cached Result?': False,
        'Make': 'MACK',
        'Model': 'GU (Granite)',
        'Model Year': '2008',
        'VIN': '1M2AX09C88M003743'
    }


def test_vin_does_not_exist():
    response = client.get("/lookup/1XP5DB9X7XD487945")
    assert response.status_code == 404
    assert response.json() == {"detail": "1XP5DB9X7XD487945 1 - Check Digit (9th position) does not calculate properly"}


def test_lookup_fail_invalid_vin():
    """This is just one failure mode: VIN must be 17 digits."""
    response = client.get("/lookup/123456")
    assert response.status_code == 404
    assert response.json() == {"detail": "Invalid VIN. VIN must be 17 characters."}


def test_remove_fail_missing_vin():
    response = client.get("/remove")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_remove_fail_invalid_vin():
    """This VIN doesn't exist as far as dot.gov is concerned."""
    response = client.get("/remove/123456")
    assert response.status_code == 404
    assert response.json() == {"detail": "Invalid VIN. VIN must be 17 characters."}
