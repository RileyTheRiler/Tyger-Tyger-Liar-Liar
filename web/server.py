
import os
import sys
import subprocess
import threading
import queue
import time
import secrets
from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit

# Define paths relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
TITLE_SCREEN_DIR = os.path.join(BASE_DIR, 'title_screen')

app = Flask(__name__, static_folder='title_screen')
# Sentinel: Replaced hardcoded secret with secure generation
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(32))

# Sentinel: Restricted CORS to localhost by default. Allow override via env for remote play.
allowed_origins = [origin.strip() for origin in os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')]
socketio = SocketIO(app, cors_allowed_origins=allowed_origins)

# Global process handle
game_process = None
input_queue = queue.Queue()

def read_output(process):
    """Reads output from the game process and emits it to the client."""
    for line in iter(process.stdout.readline, ''):
        if line:
            socketio.emit('game_output', {'data': line})
    process.stdout.close()

@app.route('/')
def index():
    return send_from_directory(TITLE_SCREEN_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(TITLE_SCREEN_DIR, path)

@socketio.on('connect')
def test_connect():
    print('Client connected')

@socketio.on('start_game')
def handle_start_game():
    global game_process

    if game_process and game_process.poll() is None:
        emit('game_output', {'data': "Game already running.\n"})
        return

    # Path to python executable
    python_exe = sys.executable
    game_script = os.path.join(ROOT_DIR, 'game.py')

    # Start the game process
    # We use -u for unbuffered output
    env = os.environ.copy()

    # Set PYTHONPATH to include src and root
    src_path = os.path.join(ROOT_DIR, 'src')
    env["PYTHONPATH"] = f"{ROOT_DIR}:{src_path}"

    try:
        game_process = subprocess.Popen(
            [python_exe, "-u", game_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1, # Line buffered
            cwd=ROOT_DIR, # Run game from root so it finds data/
            env=env
        )

        # Start output reading thread
        t = threading.Thread(target=read_output, args=(game_process,), daemon=True)
        t.start()

        emit('game_started', {'status': 'ok'})

    except Exception as e:
        emit('game_output', {'data': f"Error starting game: {str(e)}\n"})

@socketio.on('player_input')
def handle_input(data):
    global game_process
    if game_process and game_process.poll() is None:
        cmd = data.get('input', '')
        try:
            game_process.stdin.write(cmd + "\n")
            game_process.stdin.flush()
        except Exception as e:
            emit('game_output', {'data': f"Error sending input: {str(e)}\n"})
    else:
        emit('game_output', {'data': "Game not running.\n"})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    # Use eventlet if installed, otherwise standard
    port = int(os.environ.get("PORT", 5000))
    # Sentinel: Default to localhost for security. Use 0.0.0.0 only if strictly necessary.
    host = os.environ.get("HOST", "127.0.0.1")
    # Sentinel: Disable debug mode in production context.
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"

    socketio.run(app, host=host, port=port, debug=debug_mode)
