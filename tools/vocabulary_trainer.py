
import sys
import os
import json

def load_scene(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_scene(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def vocabulary_trainer():
    print("--- Vocabulary Trainer ---")
    if len(sys.argv) < 2:
        print("Usage: python3 tools/vocabulary_trainer.py <scene_file>")
        return

    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    try:
        data = load_scene(filepath)
    except Exception as e:
        print(f"Error loading scene: {e}")
        return

    print(f"Loaded scene: {data.get('name', 'Unknown')}")

    # Check/Create synonyms dict
    if "synonyms" not in data:
        data["synonyms"] = {}

    while True:
        print("\nCurrent Synonyms:")
        for canonical, syns in data["synonyms"].items():
            print(f"  {canonical}: {', '.join(syns)}")

        print("\nCommands:")
        print("  add <canonical_object> <synonym>  - Add a synonym")
        print("  list                              - List objects in scene")
        print("  save                              - Save changes")
        print("  quit                              - Exit")

        try:
            cmd = input("> ").strip().split()
            if not cmd: continue

            op = cmd[0].lower()

            if op == "quit":
                break
            elif op == "save":
                save_scene(filepath, data)
                print(f"Saved to {filepath}")
            elif op == "list":
                objects = data.get("objects", {})
                print("Objects in scene:", ", ".join(objects.keys()))
            elif op == "add":
                if len(cmd) >= 3:
                    obj = cmd[1]
                    syn = " ".join(cmd[2:])
                    if obj not in data["synonyms"]:
                        data["synonyms"][obj] = []
                    if syn not in data["synonyms"][obj]:
                        data["synonyms"][obj].append(syn)
                        print(f"Added '{syn}' -> '{obj}'")
                    else:
                        print("Synonym already exists.")
                else:
                    print("Usage: add <canonical_object> <synonym>")
            else:
                print("Unknown command.")

        except (EOFError, KeyboardInterrupt):
            break

if __name__ == "__main__":
    vocabulary_trainer()
