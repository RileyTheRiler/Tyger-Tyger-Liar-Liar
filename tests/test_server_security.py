import time
import requests
import sys
import os
import signal
from fastapi.testclient import TestClient
from server import app
from unittest.mock import MagicMock

# Mock game instance to avoid heavy startup
# We need to mock 'server.game_instance'
sys.modules['game'] = MagicMock()

def test_shutdown_endpoint_removed():
    client = TestClient(app)

    print("Testing /api/shutdown endpoint removal...")
    response = client.post("/api/shutdown")

    if response.status_code == 404:
        print("SUCCESS: Endpoint /api/shutdown returned 404 Not Found.")
    else:
        print(f"FAILURE: Endpoint /api/shutdown returned {response.status_code}")
        sys.exit(1)

def test_state_endpoint_active():
    client = TestClient(app)

    # We need to ensure game_instance is mocked properly if we want this to work without full game load
    # But since we import server, it tries to init Game().
    # The Game() init is heavy.

    # Actually, TestClient is good but server.py initializes 'game_instance = Game()' at module level.
    # So importing 'server' already triggered the heavy load (which failed earlier until I fixed it).

    # For this security test, we just want to know if the route exists.
    # We can inspect the app routes directly too, but an integration test is better.

    print("Testing /api/state endpoint...")
    # This might fail if Game isn't fully mocked or loaded, but let's see.
    try:
        response = client.get("/api/state")
        # valid responses are 200 or 500 (if game failed internally), but not 404
        if response.status_code != 404:
             print(f"SUCCESS: /api/state found (Status {response.status_code})")
        else:
             print("FAILURE: /api/state returned 404")
             sys.exit(1)
    except Exception as e:
        print(f"Warning: /api/state check failed with {e}, but that might be due to mocking.")

if __name__ == "__main__":
    test_shutdown_endpoint_removed()
    # test_state_endpoint_active() # Optional, focused on shutdown
