
import unittest
from unittest.mock import MagicMock
import sys
import os

# Mock the 'game' module BEFORE importing server
# This prevents server.py from actually loading the heavy Game class and its broken dependencies
sys.modules['game'] = MagicMock()
sys.modules['game'].Game = MagicMock()

# Add root to path so we can import server
sys.path.append(os.getcwd())

try:
    from server import app
    from fastapi.testclient import TestClient
except ImportError:
    app = None

class TestServerSecurity(unittest.TestCase):
    def setUp(self):
        if app:
            self.client = TestClient(app)

    def test_shutdown_endpoint_removed(self):
        """
        Verify that the /api/shutdown endpoint (which was a vulnerability)
        is no longer present in the application.
        """
        if not app:
            self.skipTest("server.py could not be imported")

        # We try to hit the endpoint. It should return 404 (Not Found).
        # If it returns 200 or 405 (Method Not Allowed), it exists.
        response = self.client.post("/api/shutdown")
        self.assertEqual(response.status_code, 404, "Security Risk: /api/shutdown endpoint still exists!")

if __name__ == '__main__':
    unittest.main()
