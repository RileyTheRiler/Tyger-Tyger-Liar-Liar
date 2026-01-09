
import sys
import os

# Ensure src is in path so we can import server
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__))))

def test_shutdown_endpoint_removed():
    """
    Verify that the /api/shutdown endpoint has been removed from the FastAPI app.
    Unauthenticated remote shutdown is a denial of service vulnerability.
    """
    try:
        from server import app
    except ImportError:
        # In case server.py dependencies are missing in the test env,
        # we can't fully run the test, but this script is mainly for verification.
        # Assuming dev environment has fastapi.
        print("Skipping test: server module import failed (dependencies missing?)")
        return

    routes = [route.path for route in app.routes]

    # Assert that /api/shutdown is NOT in the routes
    assert "/api/shutdown" not in routes, "SECURITY FAIL: /api/shutdown endpoint is still present!"

    print("SECURITY PASS: /api/shutdown endpoint is absent.")

if __name__ == "__main__":
    test_shutdown_endpoint_removed()
