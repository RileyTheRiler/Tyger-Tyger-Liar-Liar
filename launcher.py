import subprocess
import time
import webbrowser
import os
import sys
import signal

def is_port_in_use(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def kill_process_tree(pid):
    # On Windows, taskkill is reliable for trees
    subprocess.call(['taskkill', '/F', '/T', '/PID', str(pid)], 
                   stdout=subprocess.DEVNULL, 
                   stderr=subprocess.DEVNULL)

def main():
    print("Initializing Tyger Tyger Liar Liar...")

    # 1. Start Backend
    print("Starting Mainframe (Backend)...")
    backend_cmd = [sys.executable, "-m", "uvicorn", "server:app", "--port", "8001"]
    backend_proc = subprocess.Popen(backend_cmd, cwd=os.getcwd())

    # Wait for backend to be ready
    retries = 20
    backend_ready = False
    while retries > 0:
        if is_port_in_use(8001):
            backend_ready = True
            break
        time.sleep(0.5)
        retries -= 1
    
    if not backend_ready:
        print("Error: Backend failed to start.")
        kill_process_tree(backend_proc.pid)
        sys.exit(1)

    print("Mainframe Online.")

    # 2. Start Frontend
    print("Booting Interface (Frontend)...")
    # Using npm run dev. Shell=True needed for npm on Windows sometimes, 
    # but direct call to npm.cmd is better if possible.
    # npm is usually a batch file on windows.
    frontend_cwd = os.path.join(os.getcwd(), 'frontend')
    frontend_cmd = ["npm.cmd", "run", "dev"] # npm.cmd for windows
    frontend_proc = subprocess.Popen(frontend_cmd, cwd=frontend_cwd, shell=True) # Shell true for finding npm in path easily

    # Wait a bit for frontend to likely be ready
    time.sleep(3)

    # 3. Open Browser
    print("Establishing Neural Link...")
    webbrowser.open("http://localhost:5173")

    print("\nSYSTEM READY. MONITORING PROCESSES...")
    print("Press Ctrl+C manually to force quit if needed.")

    request_shutdown = False

    try:
        while True:
            # Check if backend is alive
            if backend_proc.poll() is not None:
                print("Backend terminated.")
                request_shutdown = True
                break
            
            # Check if frontend is alive (if we care, but frontend is usually less critical to 'game state')
            if frontend_proc.poll() is not None:
                # If frontend dies, maybe we don't care as much, but let's just log it
                pass

            time.sleep(1)
    except KeyboardInterrupt:
        print("\nManual Interrupt Detected.")
        request_shutdown = True
    finally:
        print("Shutting down systems...")
        kill_process_tree(backend_proc.pid)
        kill_process_tree(frontend_proc.pid)
        print("Terminated.")

if __name__ == "__main__":
    main()
