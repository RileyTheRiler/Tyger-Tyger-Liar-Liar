from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_shutdown_endpoint_removed():
    """Verify that the /api/shutdown endpoint has been removed for security."""
    response = client.post("/api/shutdown")
    assert response.status_code == 404
