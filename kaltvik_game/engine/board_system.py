import json
import os

THEORY_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "theories.json")

def load_theory_data(theory_id):
    """
    Loads data for a specific theory from the JSON database.
    """
    try:
        with open(THEORY_DATA_PATH, "r") as f:
            data = json.load(f)
            return data.get(theory_id)
    except FileNotFoundError:
        print(f"Error: Theory data file not found at {THEORY_DATA_PATH}")
        return None

def internalize_theory(theory_id, state):
    """
    Attempts to start internalizing a theory.
    """
    if any(t["id"] == theory_id for t in state.board["active"]):
        return f"You are already internalizing '{theory_id}'."
    
    if theory_id in state.board["completed"]:
        return f"You have already internalized '{theory_id}'."

    if len(state.board["active"]) >= state.board["slots"]:
        return "No available slots on the board. Abandon a theory first."

    data = load_theory_data(theory_id)
    if not data:
        return f"Unknown theory: '{theory_id}'."

    state.board["active"].append({
        "id": theory_id,
        "remaining_time": data["time_to_internalize"]
    })
    return f"Started internalizing: {data['name']} ({data['time_to_internalize']} in-game hours remaining)"

def advance_theory_timers(state, hours):
    """
    Reduces remaining time for active theories and completes them if time hits 0.
    """
    still_active = []
    completed_this_turn = []

    for theory in state.board["active"]:
        theory["remaining_time"] -= hours
        if theory["remaining_time"] <= 0:
            completed_this_turn.append(theory["id"])
        else:
            still_active.append(theory)
    
    state.board["active"] = still_active

    for theory_id in completed_this_turn:
        complete_theory(theory_id, state)

def complete_theory(theory_id, state):
    """
    Applies the effects of a completed theory and moves it to the completed list.
    """
    data = load_theory_data(theory_id)
    if not data:
        return

    print(f"\n[INTERNALIZED] You have fully internalized: {data['name']}")
    
    effects = data.get("effects", {})
    if effects:
        effect_strings = []
        for skill, mod in effects.items():
            if skill in state.skills:
                state.skills[skill] += mod
                sign = "+" if mod >= 0 else ""
                effect_strings.append(f"{skill} {sign}{mod}")
        
        if effect_strings:
            print(f"Results: [{', '.join(effect_strings)}]")

    state.board["completed"].append(theory_id)

def abandon_theory(theory_id, state):
    """
    Removes a theory from the active board and moves it to rejected.
    """
    for i, theory in enumerate(state.board["active"]):
        if theory["id"] == theory_id:
            state.board["active"].pop(i)
            state.board["rejected"].append(theory_id)
            return f"Abandoned theory: {theory_id}"
    
    return f"Theory '{theory_id}' is not currently active."

def show_board(state):
    """
    Displays the current state of the board.
    """
    print("\n========= THE BOARD =========")
    print(f"Slots: {len(state.board['active'])} / {state.board['slots']}")
    
    print("\n[ACTIVE THEORIES]")
    if not state.board["active"]:
        print("  (None)")
    for theory in state.board["active"]:
        data = load_theory_data(theory["id"])
        name = data["name"] if data else theory["id"]
        print(f"  - {name}: {theory['remaining_time']} hours remaining")

    print("\n[COMPLETED THEORIES]")
    if not state.board["completed"]:
        print("  (None)")
    for tid in state.board["completed"]:
        data = load_theory_data(tid)
        name = data["name"] if data else tid
        print(f"  - {name}")
    
    print("=============================")
