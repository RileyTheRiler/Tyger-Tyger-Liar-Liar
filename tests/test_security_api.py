
import sys
import os
import signal
from unittest.mock import MagicMock

# Add src to path
sys.path.append(os.getcwd())

# MOCK the game module and Game class BEFORE importing server
# This prevents the broken engine code from being loaded/executed
sys.modules["game"] = MagicMock()
sys.modules["game"].Game = MagicMock()

# Now we can safely import app
from server import app
from fastapi.testclient import TestClient

def test_shutdown_endpoint_removed():
    client = TestClient(app)

    response = client.post("/api/shutdown")

    # Expect 404 because we removed it
    if response.status_code == 404:
        print("SUCCESS: /api/shutdown is gone (404)")
    elif response.status_code == 405:
         print("SUCCESS: /api/shutdown is gone (405 - Method Not Allowed)")
    else:
        print(f"FAILURE: /api/shutdown returned {response.status_code} {response.text}")
        sys.exit(1)

if __name__ == "__main__":
    test_shutdown_endpoint_removed()
