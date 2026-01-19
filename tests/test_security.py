import sys
import os
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

# Mock the game module to avoid loading the full engine
# This must be done BEFORE importing server
sys.modules['game'] = MagicMock()
# Setup the mock Game class and instance
mock_game_class = MagicMock()
sys.modules['game'].Game = mock_game_class
mock_game_instance = mock_game_class.return_value

# Configure the mock instance methods
mock_game_instance.start_game.return_value = "Mock Output"
mock_game_instance.get_ui_state.return_value = {"mock": "state"}
mock_game_instance.step.return_value = "Mock Action Output"

# Add current directory to path to find server.py
sys.path.append(os.getcwd())

from server import app

client = TestClient(app)

def test_shutdown_endpoint_removed():
    """
    Verify that the /api/shutdown endpoint has been removed.
    It should return 404 Not Found.
    """
    response = client.post("/api/shutdown")
    assert response.status_code == 404

def test_start_endpoint_exists():
    """
    Verify that other endpoints still work (sanity check).
    """
    response = client.post("/api/start")
    assert response.status_code == 200
    assert response.json() == {"output": "Mock Output", "state": {"mock": "state"}}

def test_action_endpoint_exists():
    """
    Verify /api/action works.
    """
    response = client.post("/api/action", json={"input": "test"})
    assert response.status_code == 200
    assert response.json() == {"output": "Mock Action Output", "state": {"mock": "state"}}
