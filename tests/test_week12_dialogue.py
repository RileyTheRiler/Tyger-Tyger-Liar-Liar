"""
Test Week 12: Dialogue Branching
Tests relationship gates, theory blocking, and emotional flag requirements.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.content.dialogue_manager import DialogueManager
from src.engine.npc_system import NPC, NPCSystem


class MockSkillSystem:
    """Mock skill system for testing."""
    def get_skill(self, name):
        class MockSkill:
            effective_level = 5
        return MockSkill()
    
    def roll_check(self, skill, dc, check_type="white", check_id=None):
        return {"success": True, "roll": 15}


class MockBoard:
    """Mock board for testing."""
    def __init__(self):
        self.active_theories = []
    
    def is_theory_active(self, theory_id):
        return theory_id in self.active_theories


def test_relationship_gates():
    """Test relationship gates blocking/allowing choices."""
    print("Testing relationship gates...")
    
    # Setup
    npc_data = {
        "id": "test_guard",
        "name": "Guard",
        "initial_trust": 25,
        "initial_rapport": 15,
        "initial_respect": 30
    }
    
    npc_system = NPCSystem()
    npc = npc_system.load_npc(npc_data)
    
    skill_system = MockSkillSystem()
    board = MockBoard()
    player_state = {}
    
    dialogue_manager = DialogueManager(skill_system, board, player_state, npc_system)
    dialogue_manager.current_npc_id = "test_guard"
    
    # Test choice with trust requirement (should fail)
    choice_high_trust = {
        "text": "Let's work together",
        "relationship_gate": {
            "trust_min": 50
        }
    }
    
    allowed, reason = dialogue_manager._check_requirements(choice_high_trust)
    assert not allowed, "Choice should be blocked by low trust"
    assert "Trust" in reason, f"Reason should mention trust: {reason}"
    print(f"  ✓ High trust requirement blocked: {reason}")
    
    # Test choice with low trust requirement (should pass)
    choice_low_trust = {
        "text": "Basic question",
        "relationship_gate": {
            "trust_min": 20
        }
    }
    
    allowed, reason = dialogue_manager._check_requirements(choice_low_trust)
    assert allowed, f"Choice should be allowed: {reason}"
    print("  ✓ Low trust requirement passed")
    
    # Test rapport gate
    choice_rapport = {
        "text": "Friendly chat",
        "relationship_gate": {
            "rapport_min": 20
        }
    }
    
    allowed, reason = dialogue_manager._check_requirements(choice_rapport)
    assert not allowed, "Choice should be blocked by low rapport"
    print(f"  ✓ Rapport gate working: {reason}")
    
    print("✓ Relationship gates test passed\n")


def test_theory_blocking():
    """Test theory blocking mechanism."""
    print("Testing theory blocking...")
    
    skill_system = MockSkillSystem()
    board = MockBoard()
    player_state = {}
    
    dialogue_manager = DialogueManager(skill_system, board, player_state)
    
    # Test without theory active (should pass)
    choice = {
        "text": "Cooperative approach",
        "theory_blocked": "Trust No One"
    }
    
    allowed, reason = dialogue_manager._check_requirements(choice)
    assert allowed, "Choice should be allowed when theory not active"
    print("  ✓ Choice allowed when blocking theory inactive")
    
    # Activate blocking theory
    board.active_theories.append("Trust No One")
    
    allowed, reason = dialogue_manager._check_requirements(choice)
    assert not allowed, "Choice should be blocked when theory is active"
    assert "Trust No One" in reason, f"Reason should mention theory: {reason}"
    print(f"  ✓ Choice blocked by active theory: {reason}")
    
    print("✓ Theory blocking test passed\n")


def test_emotional_flag_requirements():
    """Test emotional flag requirements."""
    print("Testing emotional flag requirements...")
    
    npc_data = {
        "id": "test_npc",
        "name": "Test NPC",
        "emotional_flags": ["brave", "loyal"]
    }
    
    npc_system = NPCSystem()
    npc = npc_system.load_npc(npc_data)
    
    skill_system = MockSkillSystem()
    board = MockBoard()
    player_state = {}
    
    dialogue_manager = DialogueManager(skill_system, board, player_state, npc_system)
    dialogue_manager.current_npc_id = "test_npc"
    
    # Test with present flag (should pass)
    choice_has_flag = {
        "text": "Appeal to loyalty",
        "emotional_flag_required": "loyal"
    }
    
    allowed, reason = dialogue_manager._check_requirements(choice_has_flag)
    assert allowed, f"Choice should be allowed with present flag: {reason}"
    print("  ✓ Choice allowed with present emotional flag")
    
    # Test with missing flag (should fail)
    choice_missing_flag = {
        "text": "Appeal to greed",
        "emotional_flag_required": "greedy"
    }
    
    allowed, reason = dialogue_manager._check_requirements(choice_missing_flag)
    assert not allowed, "Choice should be blocked without required flag"
    assert "greedy" in reason, f"Reason should mention missing flag: {reason}"
    print(f"  ✓ Choice blocked without required flag: {reason}")
    
    print("✓ Emotional flag requirements test passed\n")


if __name__ == "__main__":
    print("Running Week 12 Dialogue Branching Tests...")
    print("=" * 50)
    print()
    
    test_relationship_gates()
    test_theory_blocking()
    test_emotional_flag_requirements()
    
    print("=" * 50)
    print("All tests passed! ✓")
    print("=" * 50)
