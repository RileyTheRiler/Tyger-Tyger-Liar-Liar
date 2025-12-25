import sys
import os
import pytest

sys.path.append(os.path.abspath('src'))
sys.path.append(os.path.abspath('src/engine'))
sys.path.append(os.path.abspath('.'))

from liar_engine import LiarEngine
from mechanics import SkillSystem
from inventory_system import InventoryManager, Evidence

def test_liar_contradiction():
    # Setup
    skills = SkillSystem()
    inventory = InventoryManager()
    liar = LiarEngine(skills, inventory)
    
    # Add evidence that someone WAS there
    ev = Evidence("witness_01", "A witness saw a tall man.", "testimony")
    ev.tags.append("witness_seen")
    inventory.add_evidence(ev)
    
    # Mock text that says no one was there
    text = "The suspect says: 'I was alone. No one else was around that night.'"
    
    # Ensure Skepticism is high
    skills.get_skill("Skepticism").base_level = 10
    
    # Check contradictions
    tags = liar._get_player_evidence_tags()
    print(f"Evidence tags: {tags}")
    interrupts = liar.check_contradictions(text)
    print(f"Interrupts: {interrupts}")
    
    assert len(interrupts) > 0
    assert interrupts[0]["skill"] == "SKEPTICISM"
    assert "witness" in interrupts[0]["text"]
    print("Liar Engine test passed!")

if __name__ == "__main__":
    test_liar_contradiction()
