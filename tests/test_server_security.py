import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Mock the game module before importing server, as game.py is heavy/complex
# We need to mock it effectively so 'from game import Game' works
game_mock = MagicMock()
sys.modules['game'] = game_mock

# Mock uvicorn
sys.modules['uvicorn'] = MagicMock()

# Add root to path so we can import server
sys.path.insert(0, os.getcwd())

try:
    from fastapi.testclient import TestClient
    HAS_TESTCLIENT = True
except ImportError:
    HAS_TESTCLIENT = False

class TestServerSecurity(unittest.TestCase):
    def setUp(self):
        # Force reload server module to ensure we test the current state
        if 'server' in sys.modules:
            import importlib
            import server
            importlib.reload(server)
        else:
            import server
        self.server = server

    def test_shutdown_endpoint_removed(self):
        """
        Verifies that the shutdown endpoint NO LONGER exists.
        """
        routes = [route.path for route in self.server.app.routes]
        self.assertNotIn("/api/shutdown", routes, "Shutdown endpoint should be removed")

if __name__ == '__main__':
    unittest.main()
