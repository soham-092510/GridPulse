import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_rate_limiter_active():
    """Verify that slowapi rate limiting is attached and working."""
    assert hasattr(app.state, "limiter")
    client = TestClient(app)
    response = client.get("/api/forecasts/multi-horizon")
    assert response.status_code == 200
    assert "horizon_15m" in response.json()
