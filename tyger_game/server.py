import sys
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tyger_game.engine.scene_manager import SceneManager
from tyger_game.engine.parser import CommandParser
from tyger_game.engine.character import Character
from tyger_game.engine.dialogue import DialogueManager
from tyger_game.ui import interface

app = FastAPI()

# Enable CORS for frontend
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ActionRequest(BaseModel):
    input: str

class GameResponse(BaseModel):
    text: str
    color: Optional[str] = None
    state: Optional[dict] = None

# Game State
class GameSession:
    def __init__(self):
        self.output_buffer = []
        
        # Initialize Engine Components
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.scene_manager = SceneManager(base_path)
        self.scene_manager.data_path = os.path.join(base_path, "data")
        
        self.character = Character()
        self.dialogue_manager = DialogueManager()
        self.parser = CommandParser(self.scene_manager, self.character, self.dialogue_manager)
        
        # Override Interface
        interface.set_output_handler(self.capture_output)

    def capture_output(self, text, color=None):
        self.output_buffer.append({"text": text, "color": color})

    def get_and_clear_output(self):
        # Join text for simple display, or return list of objects
        # To simplify api.js integration which likely expects a string or simple object
        # let's join them with newlines
        full_text = "\n".join([item["text"] for item in self.output_buffer])
        self.output_buffer = []
        return full_text

# Global Session (Single player per server instance for prototype)
session = None

@app.post("/api/start")
def start_game():
    global session
    session = GameSession()
    
    # Load initial scene
    try:
        session.scene_manager.load_scene("intro_arrival")
        session.parser._handle_look_scene()
        return {"text": session.get_and_clear_output()}
    except Exception as e:
        return {"text": f"Error starting game: {str(e)}"}

@app.post("/api/action")
def take_action(request: ActionRequest):
    global session
    if not session:
        return {"text": "Game not started. Please refresh or click Start."}
    
    # Process command
    result = session.parser.parse(request.input)
    
    response_text = session.get_and_clear_output()
    
    if result == "quit":
        return {"text": response_text + "\n[GAME ENDED]"}
        
    return {"text": response_text}

@app.post("/api/shutdown")
def shutdown():
    os._exit(0)

if __name__ == "__main__":
    # Sentinel: Bind to localhost to prevent network exposure
    uvicorn.run(app, host="127.0.0.1", port=8001)
