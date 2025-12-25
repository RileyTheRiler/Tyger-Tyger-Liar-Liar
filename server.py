from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
import signal

# Add src to path just in case, though game.py handles it
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from game import Game

app = FastAPI()

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Game Instance (Single Player for now)
game_instance = Game()

class ActionRequest(BaseModel):
    input: str

@app.post("/api/start")
def start_game():
    output = game_instance.start_game()
    return {
        "output": output,
        "state": game_instance.get_ui_state()
    }

@app.post("/api/action")
def take_action(request: ActionRequest):
    output = game_instance.step(request.input)
    return {
        "output": output,
        "state": game_instance.get_ui_state()
    }

@app.get("/api/state")
def get_state():
    return game_instance.get_ui_state()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

@app.post("/api/shutdown")
def shutdown_server():
    def kill_server():
        import time
        time.sleep(0.5)
        # On Windows, SIGTERM is brutal. sys.exit might be cleaner if running directly, 
        # but os.kill is sure to work for the external process.
        os.kill(os.getpid(), signal.SIGTERM)
    
    import threading
    threading.Thread(target=kill_server).start()
    return {"status": "shutting_down"}
