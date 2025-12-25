
import os
import sys
import subprocess
import threading
import queue
import time
from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit

app = Flask(__name__, static_folder='title_screen')
app.config['SECRET_KEY'] = 'tyger_tyger_secret'
socketio = SocketIO(app, cors_allowed_origins='*')

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
    return send_from_directory('title_screen', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('title_screen', path)

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
    game_script = os.path.join(os.path.dirname(__file__), 'game.py')

    # Start the game process
    # We use -u for unbuffered output
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.join(os.getcwd(), "src")

    try:
        game_process = subprocess.Popen(
            [python_exe, "-u", game_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1, # Line buffered
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
    # Optional: Kill game process on disconnect?
    # For now, keep it running or let it die if pipe breaks

if __name__ == '__main__':
    # Use eventlet if installed, otherwise standard
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)
