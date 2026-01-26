
import requests
import time
import os
import subprocess
import signal
import sys
import shutil

def run_server():
    cmd = [sys.executable, "server.py"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process

def verify_security():
    print("Starting server for security verification...")
    server = run_server()
    time.sleep(5)

    base_url = "http://127.0.0.1:8001/api"

    # Clean up
    if os.path.exists("exports"):
        shutil.rmtree("exports")
    os.makedirs("exports")

    if os.path.exists("test_hack.txt"):
        os.remove("test_hack.txt")

    try:
        # Start
        requests.post(f"{base_url}/start")
        # Debug
        requests.post(f"{base_url}/action", json={"input": "debug"})
        # Save
        requests.post(f"{base_url}/action", json={"input": "save sec_test"})

        # Attack
        print("Attempting traversal attack...")
        target_file = "../test_hack.txt" # Should land in exports/test_hack.txt
        requests.post(f"{base_url}/action", json={"input": f"debugexport sec_test {target_file}"})

        # Verify
        safe_path = "exports/test_hack.txt"
        dangerous_path = "test_hack.txt" # In root (if ../ worked relative to cwd) OR ../test_hack.txt relative to root

        if os.path.exists(safe_path):
            print(f"PASS: File found in safe directory: {safe_path}")
        else:
            print(f"FAIL: File NOT found in safe directory: {safe_path}")

        if os.path.exists(dangerous_path):
             print(f"FAIL: File found in dangerous location: {dangerous_path}")
        elif os.path.exists("../test_hack.txt"):
             print(f"FAIL: File found in parent directory!")
        else:
             print("PASS: File NOT found in dangerous locations.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        server.send_signal(signal.SIGTERM)
        server.wait()

if __name__ == "__main__":
    verify_security()
