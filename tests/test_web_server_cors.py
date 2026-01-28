
import sys
import os
import pytest
import importlib.util

def load_web_server():
    # Helper to load web/server.py as a module
    file_path = os.path.join(os.getcwd(), 'web', 'server.py')
    spec = importlib.util.spec_from_file_location("web_server", file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["web_server"] = module
    spec.loader.exec_module(module)
    return module

def test_cors_defaults():
    # Remove env var if exists
    if "CORS_ALLOWED_ORIGINS" in os.environ:
        del os.environ["CORS_ALLOWED_ORIGINS"]

    server = load_web_server()

    # Check default origins
    assert "http://localhost:5173" in server.allowed_origins
    assert "http://localhost:5000" in server.allowed_origins

    # Check socketio config
    # We access the configured cors_allowed_origins from the SocketIO instance
    # Note: Flask-SocketIO might process the list, but it stores it in server_options or similar
    # or passed to python-socketio.
    # checking the attribute on the instance itself if accessible

    # It seems flask_socketio.SocketIO stores options.
    # But checking the variable 'allowed_origins' in the module is sufficient to verify MY logic.
    assert server.allowed_origins == [
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:5000", "http://127.0.0.1:5000",
        "http://localhost:3000", "http://127.0.0.1:3000"
    ]

def test_cors_env_var():
    # Set env var
    os.environ["CORS_ALLOWED_ORIGINS"] = "http://example.com,http://foo.bar"

    server = load_web_server()

    assert server.allowed_origins == ["http://example.com", "http://foo.bar"]
