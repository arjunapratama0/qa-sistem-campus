from fastapi.testclient import TestClient

from app.main import app


def test_security_headers_present_on_health():
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["cache-control"] == "no-store"
    assert response.headers.get("x-request-id")


def test_rate_limit_applies_to_login():
    client = TestClient(app, raise_server_exceptions=False)

    last_response = None
    for _ in range(12):
        last_response = client.post("/api/v1/auth/login", json={"email": "bad@example.com", "password": "bad"})

    assert last_response.status_code == 429
