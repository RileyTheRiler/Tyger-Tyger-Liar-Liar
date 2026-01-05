import subprocess
import time
import requests
import sys
import os

def test_endpoint_security():
    print("Starting server...")
    # Start server in background
    process = subprocess.Popen([sys.executable, "-m", "uvicorn", "server:app", "--port", "8002"],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL,
                               cwd=os.getcwd())

    time.sleep(5)

    url = "http://localhost:8002/api"

    try:
        # Check if alive
        print("Checking status...")
        try:
            requests.get(f"{url}/state", timeout=2)
            print("Server is UP.")
        except:
            print("Server failed to start.")
            process.kill()
            return

        # Check for shutdown endpoint (should NOT exist)
        print("Checking for /api/shutdown endpoint...")
        response = requests.post(f"{url}/shutdown", timeout=2)

        if response.status_code == 404:
            print("SUCCESS: Shutdown endpoint is gone (404 Not Found).")
        elif response.status_code == 405:
            print("SUCCESS: Shutdown endpoint is disabled (405 Method Not Allowed).")
        else:
            print(f"FAILURE: Shutdown endpoint returned {response.status_code}. It should be 404.")
            process.kill()
            sys.exit(1)

        # Check for other potential sensitive endpoints
        print("Checking for other sensitive endpoints...")
        sensitive_endpoints = ["/admin", "/config", "/debug"]
        for endpoint in sensitive_endpoints:
            resp = requests.get(f"http://localhost:8002{endpoint}", timeout=1)
            if resp.status_code == 200:
                print(f"WARNING: Endpoint {endpoint} is accessible (200 OK).")
            else:
                print(f"OK: Endpoint {endpoint} is not accessible ({resp.status_code}).")

        print("Security verification complete.")
        process.kill()

    except Exception as e:
        print(f"Test Exception: {e}")
        if process.poll() is None:
            process.kill()
        sys.exit(1)

if __name__ == "__main__":
    test_endpoint_security()
