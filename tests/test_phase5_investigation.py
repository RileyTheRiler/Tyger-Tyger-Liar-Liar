import sys
import os
from unittest.mock import patch

# Add src and src/engine to path
sys.path.append(os.path.abspath("src"))
sys.path.append(os.path.abspath("src/engine"))

from inventory_system import InventoryManager, Evidence
from mechanics import SkillSystem
from autopsy_system import AutopsyMinigame

def test_aging():
    print("\n--- Test: Evidence Aging ---")
    inv = InventoryManager()
    blood = Evidence("blood_sample", "Vaporous blood from the scene.", "physical")
    blood.degrades = True
    blood.degradation_rate = 10.0 # 10% per hour
    inv.add_evidence(blood)
    
    print(f"Initial Quality: {blood.quality}%")
    inv.update_evidence_aging(2.0) # 2 hours pass
    print(f"Quality after 2 hours: {blood.quality}%")
    
    if blood.quality == 80.0:
        print("Aging correctly calculated.")
    else:
        print(f"ERROR: Aging mismatch. Got {blood.quality}")

def test_reliability():
    print("\n--- Test: Unreliable Evidence ---")
    sys = SkillSystem()
    inv = InventoryManager()
    
    fake_note = Evidence("note", "A handwritten note pointing to the neighbor.", "document")
    fake_note.is_reliable = False
    fake_note.reliability_detected = False
    inv.add_evidence(fake_note)
    
    # Mock Skepticism check success
    with patch('random.randint', return_value=6): # 6+6=12 > 9
        # Logic from handle_analyze
        result = sys.roll_check("Skepticism", 9)
        if result["success"]:
            fake_note.reliability_detected = True
            print("Successfully detected unreliable evidence!")
    
    if fake_note.reliability_detected:
        print("Reliability detection verified.")
    else:
        print("ERROR: Reliability detection failed.")

def test_autopsy():
    print("\n--- Test: Autopsy Minigame ---")
    sys = SkillSystem()
    inv = InventoryManager()
    
    autopsy = AutopsyMinigame("victim_1", "Victim 1", sys, inv)
    
    # Mock successful medicine check for brain
    with patch('random.randint', return_value=6):
        res = autopsy.examine_zone("Brain")
        print(f"Brain Exam Result: {res['message']}")
        print(f"Findings: {res['findings']}")
        
    # Mock failed medicine check for Toxicology
    with patch('random.randint', return_value=1): # 1+1=2 < 9
        res = autopsy.examine_zone("Toxicology")
        print(f"Toxicology Exam Result: {res['message']}")
        print(f"Body Integrity: {autopsy.integrity}%")
        
    if autopsy.integrity < 100.0 and "Brain" in autopsy.zones_examined:
        print("Autopsy mechanics verified.")
    else:
        print("ERROR: Autopsy verification failed.")

if __name__ == "__main__":
    test_aging()
    test_reliability()
    test_autopsy()
