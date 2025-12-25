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
            return

        # Send shutdown
        print("Sending shutdown command...")
        try:
            requests.post(f"{url}/shutdown", timeout=1)
        except requests.exceptions.ReadTimeout:
            # This is expected if server dies immediately
            pass
        except Exception as e:
            print(f"Error sending shutdown: {e}")

        time.sleep(2)
        
        # Check if dead
        is_running = process.poll() is None
        if not is_running:
            print("Server terminated successfully.")
        else:
            print("Server is still running. Test FAILED.")
            process.kill()

    except Exception as e:
        print(f"Test Exception: {e}")
        if process.poll() is None:
            process.kill()

if __name__ == "__main__":
    test_cutoff()
