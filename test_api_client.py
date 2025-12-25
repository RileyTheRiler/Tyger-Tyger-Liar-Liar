import requests
import time
import subprocess
import sys

def test_game_server():
    print("Starting server process...")
    # Start server in background
    process = subprocess.Popen([sys.executable, "-m", "uvicorn", "server:app", "--port", "8000"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE)
    
    time.sleep(5) # Wait for startup
    
    try:
        url = "http://127.0.0.1:8000/api"
        
        # 1. Start Game
        print("\nTesting /api/start...")
        resp = requests.post(f"{url}/start")
        if resp.status_code == 200:
            data = resp.json()
            print(f"SUCCESS. Output len: {len(data['output'])}")
            print(f"State: {data['state']}")
        else:
            print(f"FAILED: {resp.status_code} {resp.text}")
            return
            
        # 2. Take Action (Examine)
        print("\nTesting /api/action (Look around)...")
        resp = requests.post(f"{url}/action", json={"input": "look"})
        if resp.status_code == 200:
            data = resp.json()
            print(f"SUCCESS. Output excerpt: {data['output'][:50]}...")
        else:
            print(f"FAILED: {resp.status_code} {resp.text}")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")
    finally:
        print("Killing server...")
        process.kill()

if __name__ == "__main__":
    test_game_server()
