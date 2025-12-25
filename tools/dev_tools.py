import json
import os
import sys

# Minimal CLI editor for Tyger Tyger combat data

DATA_DIR = "data"
ENCOUNTERS_FILE = os.path.join(DATA_DIR, "encounters", "vertical_slice_encounters.json")
INJURIES_FILE = os.path.join(DATA_DIR, "injuries.json")

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

def main():
    ensure_dirs()
    while True:
        print("\n=== Tyger Tyger Developer Tools ===")
        print("1. Edit Encounters")
        print("2. Edit Injuries")
        print("3. Exit")
        choice = input("Select: ").strip()

        if choice == "1":
            edit_encounter()
        elif choice == "2":
            edit_injury()
        elif choice == "3":
            break

if __name__ == "__main__":
    main()
