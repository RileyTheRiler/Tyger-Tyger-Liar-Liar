"""
Test Week 12: Relationship Tracking System
Tests NPC rapport, respect, tags, emotional_flags, and serialization.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine.npc_system import NPC, NPCSystem


def test_npc_initialization():
    """Test NPC initialization with Week 12 fields."""
    npc_data = {
        "id": "test_npc",
        "name": "Test NPC",
        "initial_trust": 40,
        "initial_fear": 10,
        "initial_rapport": 35,
        "initial_respect": 45,
        "tags": ["met_at_dock", "knows_secret"],
        "emotional_flags": ["distrusts_law", "protective"],
        "last_seen": "chapter_1"
    }
    
    npc = NPC(npc_data)
    
    assert npc.trust == 40, f"Expected trust 40, got {npc.trust}"
    assert npc.fear == 10, f"Expected fear 10, got {npc.fear}"
    assert npc.rapport == 35, f"Expected rapport 35, got {npc.rapport}"
    assert npc.respect == 45, f"Expected respect 45, got {npc.respect}"
    assert npc.tags == ["met_at_dock", "knows_secret"], f"Tags mismatch: {npc.tags}"
    assert npc.emotional_flags == ["distrusts_law", "protective"], f"Emotional flags mismatch: {npc.emotional_flags}"
    assert npc.last_seen == "chapter_1", f"Last seen mismatch: {npc.last_seen}"
    
    print("✓ NPC initialization test passed")


def test_relationship_modification():
    """Test modifying rapport and respect."""
    npc_data = {
        "id": "test_npc",
        "name": "Test NPC",
        "initial_rapport": 50,
        "initial_respect": 50
    }
    
    npc = NPC(npc_data)
    
    # Test rapport modification
    new_rapport = npc.modify_rapport(15, "helped with task")
    assert new_rapport == 65, f"Expected rapport 65, got {new_rapport}"
    
    # Test respect modification
    new_respect = npc.modify_respect(-10, "failed promise")
    assert new_respect == 40, f"Expected respect 40, got {new_respect}"
    
    # Test bounds (should cap at 100)
    npc.modify_rapport(50)
    assert npc.rapport == 100, f"Rapport should cap at 100, got {npc.rapport}"
    
    # Test lower bound (should floor at 0)
    npc.modify_respect(-50)
    assert npc.respect == 0, f"Respect should floor at 0, got {npc.respect}"
    
    print("✓ Relationship modification test passed")


def test_get_relationship_data():
    """Test get_relationship_data method."""
    npc_data = {
        "id": "test_npc",
        "name": "Test NPC",
        "initial_trust": 60,
        "initial_fear": 20,
        "initial_rapport": 55,
        "initial_respect": 70,
        "tags": ["ally"],
        "emotional_flags": ["brave"],
        "last_seen": "chapter_2"
    }
    
    npc = NPC(npc_data)
    rel_data = npc.get_relationship_data()
    
    assert rel_data["trust"] == 60
    assert rel_data["fear"] == 20
    assert rel_data["rapport"] == 55
    assert rel_data["respect"] == 70
    assert rel_data["tags"] == ["ally"]
    assert rel_data["emotional_flags"] == ["brave"]
    assert rel_data["last_seen"] == "chapter_2"
    assert "status" in rel_data
    
    print("✓ Get relationship data test passed")


def test_serialization():
    """Test NPC serialization and restoration."""
    npc_data = {
        "id": "test_npc",
        "name": "Test NPC",
        "initial_trust": 45,
        "initial_rapport": 38,
        "initial_respect": 52,
        "tags": ["important"],
        "emotional_flags": ["nervous"],
        "last_seen": "chapter_3"
    }
    
    npc = NPC(npc_data)
    npc.modify_rapport(10)
    npc.modify_respect(-5)
    npc.tags.append("helped_player")
    
    # Serialize
    state = npc.to_dict()
    
    assert state["rapport"] == 48, f"Serialized rapport mismatch: {state['rapport']}"
    assert state["respect"] == 47, f"Serialized respect mismatch: {state['respect']}"
    assert "helped_player" in state["tags"]
    assert state["emotional_flags"] == ["nervous"]
    assert state["last_seen"] == "chapter_3"
    
    # Create new NPC and restore
    npc2 = NPC(npc_data)
    NPC.restore_state(npc2, state)
    
    assert npc2.rapport == 48, f"Restored rapport mismatch: {npc2.rapport}"
    assert npc2.respect == 47, f"Restored respect mismatch: {npc2.respect}"
    assert "helped_player" in npc2.tags
    assert npc2.last_seen == "chapter_3"
    
    print("✓ Serialization test passed")


if __name__ == "__main__":
    print("Running Week 12 Relationship Tracking Tests...")
    print()
    
    test_npc_initialization()
    test_relationship_modification()
    test_get_relationship_data()
    test_serialization()
    
    print()
    print("=" * 50)
    print("All tests passed! ✓")
    print("=" * 50)
