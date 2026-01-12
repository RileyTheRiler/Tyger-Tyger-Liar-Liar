from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_shutdown_endpoint_removed():
    """Verify that the /api/shutdown endpoint is no longer accessible."""
    response = client.post("/api/shutdown")
    assert response.status_code == 404, f"Expected 404 for shutdown, got {response.status_code}"
