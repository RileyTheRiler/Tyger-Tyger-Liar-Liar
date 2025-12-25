import sys
import os
import json
from unittest.mock import MagicMock

# Add src to path
sys.path.append(os.path.abspath("src"))
sys.path.append(os.path.abspath("src/engine"))

from mechanics import SkillSystem
from flashback_system import FlashbackManager
from inventory_system import InventoryManager

def test_flashback_pov():
    print("\n--- Test: Flashback POV Shift ---")
    sys = SkillSystem()
    game_state = {"archetype": "DETECTIVE"}
    
    fm = FlashbackManager(sys, game_state)
    
    # Setup initial state
    sys.get_skill("Logic").base_level = 5
    # Valid names: Logic, Endurance
    sys.get_skill("Endurance").base_level = 2
    
    print(f"Original: Logic={sys.get_skill('Logic').base_level}, Endurance={sys.get_skill('Endurance').base_level}")
    
    # Enter POV
    pov_data = {
        "name": "Soldier",
        "skills": {"Logic": 2, "Endurance": 8},
        "archetype": "SOLDIER"
    }
    fm.enter_flashback(pov_data)
    
    curr_logic = sys.get_skill("Logic").base_level
    curr_endur = sys.get_skill("Endurance").base_level
    print(f"POV: Logic={curr_logic}, Endurance={curr_endur}")
    
    if curr_logic == 2 and curr_endur == 8 and game_state["archetype"] == "SOLDIER":
        print("POV stats applied correctly.")
    else:
        print("ERROR: POV stats mismatch.")

    # Exit POV
    fm.exit_flashback()
    
    restored_logic = sys.get_skill("Logic").base_level
    restored_endur = sys.get_skill("Endurance").base_level
    print(f"Restored: Logic={restored_logic}, Endurance={restored_endur}")

    if restored_logic == 5 and restored_endur == 2 and game_state["archetype"] == "DETECTIVE":
        print("Original stats restored correctly.")
    else:
        print("ERROR: Restoration failed.")

def test_documents():
    print("\n--- Test: Epistolary Documents ---")
    inv = InventoryManager()
    
    # Create temp doc file
    test_docs = [
        {"id": "doc1", "title": "Test Report", "text": "Confidential."}
    ]
    with open("temp_docs.json", "w") as f:
        json.dump(test_docs, f)
        
    inv.load_documents("temp_docs.json")
    
    if "doc1" in inv.document_database:
        print("Documents loaded into database.")
    else:
        print("ERROR: Database load failed.")
        
    # Unlock
    inv.add_document("doc1")
    if len(inv.documents) == 1 and inv.documents[0]["id"] == "doc1":
        print("Document unlocked successfully.")
    else:
        print("ERROR: Document unlock failed.")
        
    # Cleanup
    os.remove("temp_docs.json")

if __name__ == "__main__":
    test_flashback_pov()
    test_documents()
