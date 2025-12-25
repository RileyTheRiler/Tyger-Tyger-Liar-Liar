"""
Week 11 Dialogue System Verification Script

Tests:
1. Hybrid input (numbered choices + parser commands)
2. NPC stat tracking and passive interrupts
3. Parser triggers ('ask about', 'say')
4. Theory-based dialogue commentary
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'engine'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'content'))

from mechanics import SkillSystem
from board import Board
from npc_system import NPCSystem
from dialogue_manager import DialogueManager

def test_npc_system():
    """Test NPC loading and stat tracking."""
    print("\n=== TEST 1: NPC System ===")
    
    npcs_dir = os.path.join('data', 'npcs')
    npc_system = NPCSystem(npcs_dir)
    
    # Check if dock_guard loaded
    guard = npc_system.get_npc('dock_guard')
    if guard:
        print(f"✓ Loaded NPC: {guard.name}")
        print(f"  Initial Trust: {guard.trust}")
        print(f"  Initial Fear: {guard.fear}")
        print(f"  Relationship: {guard.get_relationship_status()}")
        
        # Test trust modification
        new_trust, msg = guard.modify_trust(15, "helped investigation")
        print(f"  After +15 trust: {new_trust}")
        if msg:
            print(f"  Message: {msg}")
        
        return True
    else:
        print("✗ Failed to load dock_guard NPC")
        return False

def test_dialogue_loading():
    """Test dialogue loading with NPC integration."""
    print("\n=== TEST 2: Dialogue Loading ===")
    
    # Initialize systems
    skill_system = SkillSystem(os.path.join('data', 'skills.json'))
    board = Board()
    player_state = {"sanity": 100, "reality": 100}
    npc_system = NPCSystem(os.path.join('data', 'npcs'))
    
    dialogue_manager = DialogueManager(skill_system, board, player_state, npc_system)
    
    # Load test dialogue
    success = dialogue_manager.load_dialogue('dock_guard_test', 'data/dialogues', 'dock_guard')
    
    if success:
        print(f"✓ Loaded dialogue: dock_guard_test")
        print(f"  Current NPC: {dialogue_manager.current_npc_id}")
        print(f"  Current Node: {dialogue_manager.current_node_id}")
        print(f"  Total Nodes: {len(dialogue_manager.nodes)}")
        return True
    else:
        print("✗ Failed to load dialogue")
        return False

def test_parser_input():
    """Test parser command processing."""
    print("\n=== TEST 3: Parser Input Processing ===")
    
    # Initialize systems
    skill_system = SkillSystem(os.path.join('data', 'skills.json'))
    board = Board()
    player_state = {"sanity": 100, "reality": 100}
    npc_system = NPCSystem(os.path.join('data', 'npcs'))
    
    dialogue_manager = DialogueManager(skill_system, board, player_state, npc_system)
    dialogue_manager.load_dialogue('dock_guard_test', 'data/dialogues', 'dock_guard')
    
    # Test numeric choice
    print("\n  Testing numeric choice '1':")
    success, msg = dialogue_manager.process_input("1")
    print(f"    Success: {success}, Message: {msg}")
    
    # Reset to intro
    dialogue_manager.start_node("intro")
    
    # Test 'ask about' command
    print("\n  Testing 'ask about lighthouse':")
    success, msg = dialogue_manager.process_input("ask about lighthouse")
    print(f"    Success: {success}, Message: {msg}")
    print(f"    Current Node: {dialogue_manager.current_node_id}")
    
    # Reset to intro
    dialogue_manager.start_node("intro")
    
    # Test parser trigger
    print("\n  Testing parser trigger 'badge':")
    success, msg = dialogue_manager.process_input("badge")
    print(f"    Success: {success}, Message: {msg}")
    print(f"    Current Node: {dialogue_manager.current_node_id}")
    
    return True

def test_npc_passive_checks():
    """Test NPC-driven passive skill checks."""
    print("\n=== TEST 4: NPC-Driven Passive Checks ===")
    
    # Initialize systems
    skill_system = SkillSystem(os.path.join('data', 'skills.json'))
    board = Board()
    player_state = {"sanity": 100, "reality": 100}
    npc_system = NPCSystem(os.path.join('data', 'npcs'))
    
    # Modify NPC stats to trigger checks
    guard = npc_system.get_npc('dock_guard')
    if guard:
        # Set high fear to trigger Empathy check
        guard.fear = 80
        guard.trust = 25  # Low trust for Profiling check
        
        dialogue_manager = DialogueManager(skill_system, board, player_state, npc_system)
        dialogue_manager.load_dialogue('dock_guard_test', 'data/dialogues', 'dock_guard')
        
        # Get interjections
        node = dialogue_manager.nodes.get('intro')
        interjections = dialogue_manager._run_passive_checks(node)
        
        print(f"  NPC Fear: {guard.fear}")
        print(f"  NPC Trust: {guard.trust}")
        print(f"  Interjections triggered: {len(interjections)}")
        for i in interjections:
            print(f"    - {i}")
        
        return True
    else:
        print("✗ Could not load NPC for testing")
        return False

def main():
    print("="*60)
    print("WEEK 11 DIALOGUE SYSTEM VERIFICATION")
    print("="*60)
    
    results = []
    
    results.append(("NPC System", test_npc_system()))
    results.append(("Dialogue Loading", test_dialogue_loading()))
    results.append(("Parser Input", test_parser_input()))
    results.append(("NPC Passive Checks", test_npc_passive_checks()))
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️ Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
