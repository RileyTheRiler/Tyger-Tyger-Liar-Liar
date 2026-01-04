
import sys
import os
import unittest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

# Mock the Game class and its dependencies before importing server
# This prevents the actual game engine from starting up
sys.modules['game'] = MagicMock()
sys.modules['game'].Game = MagicMock()
sys.modules['src.game'] = sys.modules['game']

sys.path.append(os.getcwd())

try:
    from server import app
except ImportError as e:
    print(f"Failed to import server: {e}")
    sys.exit(1)

class TestServerSecurity(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_shutdown_endpoint_removed(self):
        """
        Verify that the /api/shutdown endpoint has been removed.
        """
        response = self.client.post("/api/shutdown")

        if response.status_code == 404:
            print("\n[SECURE] /api/shutdown is gone (404).")
        elif response.status_code == 405:
            print("\n[SECURE] /api/shutdown method not allowed (405).")
        else:
            print(f"\n[VULNERABLE] /api/shutdown returned {response.status_code}")

        # We expect 404 because we are going to remove the route completely
        self.assertEqual(response.status_code, 404, "Security fix: /api/shutdown should be removed (404 Not Found).")

if __name__ == '__main__':
    unittest.main()
