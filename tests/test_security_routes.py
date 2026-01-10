import sys
import os
from fastapi.testclient import TestClient

# Add project root to path so we can import server
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import app

client = TestClient(app)

def test_shutdown_endpoint_removed():
    """Verify that the potentially dangerous /api/shutdown endpoint is not accessible."""
    response = client.post("/api/shutdown")
    assert response.status_code == 404, "Shutdown endpoint should not exist"
