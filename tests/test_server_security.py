
import unittest
from fastapi.testclient import TestClient
from server import app
import sys
from unittest.mock import MagicMock

# Mock game module to avoid loading the whole game engine
sys.modules['game'] = MagicMock()

class TestServerSecurity(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_shutdown_endpoint_removed(self):
        """
        CRITICAL: The /api/shutdown endpoint must NOT exist.
        It allows unauthenticated remote shutdown of the server.
        """
        response = self.client.post("/api/shutdown")
        # Should return 404 Not Found
        self.assertEqual(response.status_code, 404, "Security Risk: /api/shutdown endpoint is exposed!")

if __name__ == '__main__':
    unittest.main()
