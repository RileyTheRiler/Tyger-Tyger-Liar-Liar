
from fastapi.testclient import TestClient
import sys
import os

# Ensure we can import server
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mocking Game to avoid loading the entire engine which might require assets/paths
import unittest.mock
with unittest.mock.patch('server.Game') as MockGame:
    from server import app

client = TestClient(app)

def test_shutdown_endpoint_removed():
    response = client.post("/api/shutdown")
    assert response.status_code == 404, "Shutdown endpoint should be removed (404)"
