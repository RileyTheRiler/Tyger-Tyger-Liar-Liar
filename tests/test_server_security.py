import subprocess
import time
import requests
import sys
import os

def test_cutoff():
    print("Starting server...")
    # Start server in background
    # Ensure we use a different port if needed, but 8001 is the one we implemented
    process = subprocess.Popen([sys.executable, "-m", "uvicorn", "server:app", "--port", "8001"], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL,
                               cwd=os.getcwd())
    
    time.sleep(5)
    
    url = "http://localhost:8001/api"
    
    try:
        # Check if alive
        print("Checking status...")
        try:
            requests.get(f"{url}/state", timeout=2)
            print("Server is UP.")
        except:
            print("Server failed to start.")
            process.kill()
            sys.exit(1)

        # Send shutdown - EXPECTING FAILURE (404)
        print("Sending shutdown command (expecting 404)...")
        try:
            response = requests.post(f"{url}/shutdown", timeout=1)
            if response.status_code == 404:
                print("Got 404 Not Found as expected.")
            else:
                print(f"Unexpected status code: {response.status_code}")
                process.kill()
                sys.exit(1)
        except requests.exceptions.ReadTimeout:
             print("Request timed out - server might have died!")

        except Exception as e:
            print(f"Error sending shutdown: {e}")

        time.sleep(2)
        
        # Check if dead
        is_running = process.poll() is None
        if is_running:
            print("Server is still running. Test PASSED.")
            process.kill()
        else:
            print("Server terminated. Test FAILED.")
            sys.exit(1)

    except Exception as e:
        print(f"Test Exception: {e}")
        if process.poll() is None:
            process.kill()
        sys.exit(1)

if __name__ == "__main__":
    test_cutoff()
