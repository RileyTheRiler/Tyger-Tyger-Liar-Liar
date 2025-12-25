import json
import os
import sys

# Minimal CLI editor for Tyger Tyger combat data

DATA_DIR = "data"
ENCOUNTERS_FILE = os.path.join(DATA_DIR, "encounters", "vertical_slice_encounters.json")
INJURIES_FILE = os.path.join(DATA_DIR, "injuries.json")

# Ensure src is in path for imports
sys.path.append(os.path.join(os.getcwd(), 'src'))
from engine.combat import CombatManager
from engine.mechanics import SkillSystem
from engine.injury_system import InjurySystem
from engine.trauma_system import TraumaSystem

def ensure_dirs():
    if not os.path.exists(os.path.join(DATA_DIR, "encounters")):
        os.makedirs(os.path.join(DATA_DIR, "encounters"))

def load_json(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved to {filepath}")

def edit_encounter():
    data = load_json(ENCOUNTERS_FILE)
    print("\n--- Encounter Editor ---")
    print("Existing IDs:", list(data.keys()))
    eid = input("Enter Encounter ID to edit/create: ").strip()

    encounter = data.get(eid, {
        "name": "New Encounter",
        "hp": 10,
        "reflexes": 1,
        "attack": 1,
        "logic": 1,
        "endurance": 1,
        "psychology": "neutral",
        "traits": [],
        "dialogue_options": False
    })

    print(f"Editing {eid} (Press Enter to keep current value)")

    for key in ["name", "hp", "reflexes", "attack", "logic", "endurance", "psychology"]:
        val = input(f"{key} [{encounter.get(key)}]: ").strip()
        if val:
            if key in ["hp", "reflexes", "attack", "logic", "endurance"]:
                encounter[key] = int(val)
            else:
                encounter[key] = val

    data[eid] = encounter
    save_json(ENCOUNTERS_FILE, data)

def edit_injury():
    data = load_json(INJURIES_FILE)
    print("\n--- Injury Editor ---")
    print("Existing IDs:", list(data.keys()))
    iid = input("Enter Injury ID to edit/create (e.g. 'gunshot_leg'): ").strip()

    injury = data.get(iid, {
        "name": "New Injury",
        "location": "leg",
        "severity": "minor",
        "effects": {"Athletics": -1},
        "healing_time_hours": 24.0,
        "description": "A painful wound."
    })

    print(f"Editing {iid} (Press Enter to keep current value)")

    name = input(f"name [{injury['name']}]: ").strip()
    if name: injury['name'] = name

    loc = input(f"location [{injury['location']}]: ").strip()
    if loc: injury['location'] = loc

    sev = input(f"severity [{injury['severity']}]: ").strip()
    if sev: injury['severity'] = sev

    print(f"Current effects: {injury['effects']}")
    eff_in = input("Enter effects (key:val,key:val) or Enter to skip: ").strip()
    if eff_in:
        new_eff = {}
        for pair in eff_in.split(","):
            k, v = pair.split(":")
            new_eff[k.strip()] = int(v.strip())
        injury['effects'] = new_eff

    desc = input(f"description [{injury['description']}]: ").strip()
    if desc: injury['description'] = desc

    data[iid] = injury
    save_json(INJURIES_FILE, data)

def simulate_combat():
    print("\n--- Combat Simulation ---")
    print("This will run a mock combat using the current systems.")

    skill_sys = SkillSystem()
    player_state = {"sanity": 100, "injuries": []}
    injury_sys = InjurySystem()
    trauma_sys = TraumaSystem()

    combat = CombatManager(skill_sys, player_state, injury_sys, trauma_sys)

    # Load default enemy or create one
    enemy = {
        "name": "Simulation Dummy",
        "hp": 5,
        "reflexes": 0,
        "attack": 1,
        "traits": []
    }

    print("Initializing encounter...")
    combat.start_encounter(enemies=[enemy], encounter_type="simulation")

    while combat.active:
        print(f"\nRound {combat.round_counter}")
        print("1. Attack")
        print("2. Dodge")
        print("3. Intimidate")
        print("4. End Simulation")

        choice = input("Choose action: ").strip()
        result = {}

        if choice == "1":
            result = combat.perform_action("attack", "Simulation Dummy")
        elif choice == "2":
            result = combat.perform_action("dodge")
        elif choice == "3":
            result = combat.perform_action("intimidate", "Simulation Dummy")
        elif choice == "4":
            combat.end_encounter()
            break
        else:
            print("Invalid.")
            continue

        # Print Log for this turn
        if result:
            print(f"\n[ACTION RESULT]: {result.get('messages')}")

        print("\n--- COMBAT LOG (Last 5) ---")
        for msg in combat.log[-5:]:
            print(f" > {msg}")

        if not combat.active:
            print("\nCombat Ended.")
            if "injuries" in player_state and player_state["injuries"]:
                 print("Injuries sustained:")
                 for inj in injury_sys.active_injuries:
                     print(f" - {inj.name} ({inj.severity})")

def main():
    ensure_dirs()
    while True:
        print("\n=== Tyger Tyger Developer Tools ===")
        print("1. Edit Encounters")
        print("2. Edit Injuries")
        print("3. Simulate Combat (Debug Log)")
        print("4. Exit")
        choice = input("Select: ").strip()

        if choice == "1":
            edit_encounter()
        elif choice == "2":
            edit_injury()
        elif choice == "3":
            simulate_combat()
        elif choice == "4":
            break

if __name__ == "__main__":
    main()
