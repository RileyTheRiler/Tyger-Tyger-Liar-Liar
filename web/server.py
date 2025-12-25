from flask import Flask, render_template, request, Response, stream_with_context
import subprocess
import queue
import threading
import time
import os
import sys

# Add parent directory to path to find game.py if needed,
# but we will likely run it via subprocess calling 'python game.py'
# assuming we are running from root.

app = Flask(__name__)

# Global game process storage
game_process = None
output_queue = queue.Queue()
input_queue = queue.Queue()

def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line.decode('utf-8'))
    out.close()

def start_game_process():
    global game_process
    # Adjust path to game.py. Assuming server.py is in /web and game.py is in /
    # or if we run from root: python web/server.py

    # We will assume the CWD is the project root
    cmd = [sys.executable, "-u", "game.py"]

    # Check if game.py exists in CWD
    if not os.path.exists("game.py"):
        # Try looking up one level if we are in web/
        if os.path.exists("../game.py"):
            cmd = [sys.executable, "-u", "../game.py"]
            # Change CWD for the subprocess so it finds its data/ folder
            cwd = ".."
        else:
            print("Error: game.py not found.")
            return

    game_process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, # Merge stderr into stdout
        bufsize=0 # Unbuffered
    )

    t = threading.Thread(target=enqueue_output, args=(game_process.stdout, output_queue))
    t.daemon = True
    t.start()

@app.route('/')
def index():
    global game_process
    if game_process is None or game_process.poll() is not None:
        start_game_process()
    return render_template('index.html')

@app.route('/input', methods=['POST'])
def send_input():
    global game_process
    data = request.json
    user_input = data.get('input', '')

    if game_process and game_process.stdin:
        try:
            msg = f"{user_input}\n"
            game_process.stdin.write(msg.encode('utf-8'))
            game_process.stdin.flush()
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    return {"status": "no_process"}

@app.route('/stream')
def stream():
    def generate():
        while True:
            try:
                # Non-blocking get
                line = output_queue.get(timeout=0.1)
                # SSE format: "data: <content>\n\n"
                # We need to escape newlines for data payload if multiline, but line read is usually one line
                yield f"data: {line}\n\n"
            except queue.Empty:
                if game_process and game_process.poll() is not None:
                    yield "data: [Game Process Ended]\n\n"
                    break
                # Send heartbeat or just wait
                yield ": keepalive\n\n"
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    # Change working directory to project root if we are running inside web/
    if os.path.basename(os.getcwd()) == "web":
        os.chdir("..")

    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
