import json
import os

def load_theories_data():
    """Load theory data from theories.json."""
    paths = [
        "data/theories.json",
        "../data/theories.json",
        "../../data/theories.json"
    ]
    
    for path in paths:
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
    
    # Fallback to empty dict if file not found
    print("[WARNING] theories.json not found, using empty theory database")
    return {}

THEORY_DATA = load_theories_data()
