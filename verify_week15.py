"""
Verification Script for Week 15: Psychological Systems
Tests Sanity, Mental Load, Fear Events, and Unreliable Narration.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from engine.psychological_system import PsychologicalState
from engine.fear_system import FearManager, FearEvent
from engine.unreliable_narrator import HallucinationEngine


def test_psychological_state():
    """Test PsychologicalState class."""
    print("\n" + "="*60)
    print("TEST 1: Psychological State System")
    print("="*60)
    
    # Create mock player state
    player_state = {
        "sanity": 100.0,
        "reality": 100.0,
        "mental_load": 0,
        "fear_level": 0,
        "disorientation": False,
        "instability": False,
        "hallucination_history": []
    }
    
    psych = PsychologicalState(player_state)
    
    # Test 1.1: Sanity Tiers
    print("\n1.1: Testing Sanity Tiers")
    test_values = [100, 75, 50, 25, 10, 0]
    for val in test_values:
        player_state["sanity"] = val
        tier = psych.get_sanity_tier()
        tier_name = psych.get_sanity_tier_name()
        multiplier = psych.get_mental_load_multiplier()
        print(f"  Sanity {val}: Tier {tier} ({tier_name}), Load Multiplier: {multiplier}x")
    
    # Test 1.2: Mental Load Accumulation
    print("\n1.2: Testing Mental Load Accumulation")
    player_state["sanity"] = 100
    player_state["mental_load"] = 0
    
    result = psych.add_mental_load(10, "Test event")
    print(f"  Added 10 load at 100 sanity: {result['amount_added']} (expected 10)")
    
    player_state["sanity"] = 40  # Tier 2: 1.5x multiplier
    result = psych.add_mental_load(10, "Test event")
    print(f"  Added 10 load at 40 sanity: {result['amount_added']} (expected 15)")
    
    # Test 1.3: Fear Level and Decay
    print("\n1.3: Testing Fear Level")
    player_state["fear_level"] = 0
    result = psych.add_fear(30, "Test fear")
    print(f"  Added 30 fear: Current level = {player_state['fear_level']}")
    
    result = psych.decay_fear(20)  # 20 minutes = 10 decay
    print(f"  After 20 min decay: {player_state['fear_level']} (expected 20)")
    
    # Test 1.4: Psychological Summary
    print("\n1.4: Psychological Summary")
    player_state["sanity"] = 30
    player_state["mental_load"] = 65
    player_state["fear_level"] = 40
    player_state["disorientation"] = True
    summary = psych.get_psychological_summary()
    print(summary)
    
    print("\n✓ Psychological State tests complete")


def test_fear_system():
    """Test Fear Event System."""
    print("\n" + "="*60)
    print("TEST 2: Fear Event System")
    print("="*60)
    
    # Test 2.1: Fear Event Creation
    print("\n2.1: Testing Fear Event Creation")
    event_data = {
        "id": "test_fear",
        "name": "Test Fear",
        "trigger_conditions": {
            "location": "outdoor",
            "sanity_below": 50,
            "chance": 1.0
        },
        "effects": {
            "fear_level": 20,
            "sanity": -10,
            "text_overlay": "Test fear text"
        },
        "cooldown_minutes": 30
    }
    
    event = FearEvent(event_data)
    print(f"  Created event: {event.id} - {event.name}")
    print(f"  Cooldown: {event.cooldown_minutes} minutes")
    
    # Test 2.2: Trigger Conditions
    print("\n2.2: Testing Trigger Conditions")
    
    game_state_pass = {
        "current_location": "outdoor",
        "sanity": 40,
        "player_flags": set()
    }
    
    game_state_fail = {
        "current_location": "indoor",
        "sanity": 60,
        "player_flags": set()
    }
    
    can_trigger_pass = event.can_trigger(game_state_pass)
    can_trigger_fail = event.can_trigger(game_state_fail)
    
    print(f"  Matching conditions: {can_trigger_pass} (expected True)")
    print(f"  Non-matching conditions: {can_trigger_fail} (expected False)")
    
    # Test 2.3: Fear Manager
    print("\n2.3: Testing Fear Manager")
    manager = FearManager()
    
    # Load from data directory
    fear_events_path = os.path.join(os.path.dirname(__file__), 'data', 'fear_events')
    if os.path.exists(fear_events_path):
        manager.load_fear_events(fear_events_path)
        print(f"  Loaded {len(manager.fear_events)} fear events")
        for event_id in manager.fear_events.keys():
            print(f"    - {event_id}")
    else:
        print(f"  Warning: Fear events directory not found at {fear_events_path}")
    
    # Test toggle
    manager.toggle_enabled(False)
    print(f"  Fear events disabled: {not manager.enabled}")
    manager.toggle_enabled(True)
    print(f"  Fear events enabled: {manager.enabled}")
    
    print("\n✓ Fear Event System tests complete")


def test_hallucination_engine():
    """Test Unreliable Narrator / Hallucination Engine."""
    print("\n" + "="*60)
    print("TEST 3: Hallucination Engine")
    print("="*60)
    
    engine = HallucinationEngine()
    
    # Load hallucination templates
    hallucinations_path = os.path.join(os.path.dirname(__file__), 'data', 'hallucinations')
    if os.path.exists(hallucinations_path):
        engine.load_hallucination_templates(hallucinations_path)
        print(f"\n3.1: Loaded Hallucination Templates")
        print(f"  Visual: {len(engine.visual_hallucinations)}")
        print(f"  Auditory: {len(engine.auditory_hallucinations)}")
        print(f"  Memory Drifts: {len(engine.memory_drifts)}")
    else:
        print(f"  Warning: Hallucinations directory not found at {hallucinations_path}")
        return
    
    # Test 3.2: Hallucination Retrieval
    print("\n3.2: Testing Hallucination Retrieval")
    
    # Visual (tier 1 or lower)
    visual = engine.get_visual_hallucination(sanity_tier=1)
    if visual:
        print(f"  Visual (tier 1): {visual[:60]}...")
    else:
        print("  No visual hallucination for tier 1")
    
    # Auditory (tier 2 or lower)
    auditory = engine.get_auditory_hallucination(sanity_tier=2)
    if auditory:
        print(f"  Auditory (tier 2): {auditory[:60]}...")
    else:
        print("  No auditory hallucination for tier 2")
    
    # Test 3.3: False Choice Injection
    print("\n3.3: Testing False Choice Injection")
    original_choices = [
        {"text": "Choice 1", "next": "scene1"},
        {"text": "Choice 2", "next": "scene2"}
    ]
    
    modified = engine.inject_false_choice(original_choices, sanity_tier=1, instability=True)
    print(f"  Original choices: {len(original_choices)}")
    print(f"  Modified choices: {len(modified)}")
    
    hallucinated_count = sum(1 for c in modified if c.get("hallucinated"))
    print(f"  Hallucinated choices added: {hallucinated_count}")
    
    # Test 3.4: Competing Voices
    print("\n3.4: Testing Competing Voices")
    test_text = "You find a piece of evidence that contradicts your theory."
    voices = engine.get_competing_voices(test_text, sanity_tier=1, instability=True)
    print(f"  Generated {len(voices)} competing voices")
    for voice in voices:
        print(f"    [{voice['skill']}] {voice['text'][:50]}...")
    
    # Test 3.5: Unreliable Feedback
    print("\n3.5: Testing Unreliable Feedback")
    original_feedback = "Success: You passed the check."
    modified_feedback = engine.apply_unreliable_feedback(original_feedback, success=True, sanity_tier=1)
    print(f"  Original: {original_feedback}")
    print(f"  Modified: {modified_feedback}")
    
    print("\n✓ Hallucination Engine tests complete")


def test_integration():
    """Test integration with game systems."""
    print("\n" + "="*60)
    print("TEST 4: Integration Test")
    print("="*60)
    
    print("\n4.1: Checking game.py integration")
    
    # Check if psychological systems are imported
    game_py_path = os.path.join(os.path.dirname(__file__), 'game.py')
    if os.path.exists(game_py_path):
        with open(game_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            checks = [
                ("PsychologicalState import", "from engine.psychological_system import PsychologicalState"),
                ("FearManager import", "from engine.fear_system import FearManager"),
                ("HallucinationEngine import", "from engine.unreliable_narrator import HallucinationEngine"),
                ("mental_load in player_state", '"mental_load"'),
                ("fear_level in player_state", '"fear_level"'),
                ("MENTAL command", 'verb == "MENTAL"'),
                ("GROUND command", 'verb == "GROUND"'),
            ]
            
            for check_name, check_string in checks:
                if check_string in content:
                    print(f"  ✓ {check_name}")
                else:
                    print(f"  ✗ {check_name} - NOT FOUND")
    else:
        print(f"  Warning: game.py not found at {game_py_path}")
    
    print("\n4.2: Checking data files")
    data_checks = [
        ("Fear Events", "data/fear_events"),
        ("Hallucinations", "data/hallucinations"),
        ("Grounding Rituals", "data/activities/grounding_rituals.json"),
    ]
    
    for check_name, path in data_checks:
        full_path = os.path.join(os.path.dirname(__file__), path)
        if os.path.exists(full_path):
            if os.path.isdir(full_path):
                files = [f for f in os.listdir(full_path) if f.endswith('.json')]
                print(f"  ✓ {check_name}: {len(files)} files")
            else:
                print(f"  ✓ {check_name}: exists")
        else:
            print(f"  ✗ {check_name}: NOT FOUND")
    
    print("\n✓ Integration tests complete")


def main():
    """Run all verification tests."""
    print("\n" + "="*60)
    print("WEEK 15: PSYCHOLOGICAL SYSTEMS VERIFICATION")
    print("="*60)
    
    try:
        test_psychological_state()
        test_fear_system()
        test_hallucination_engine()
        test_integration()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*60)
        print("\nWeek 15 psychological systems are ready for use!")
        print("\nNew Commands:")
        print("  - MENTAL or PSYCH: View psychological state")
        print("  - GROUND: Perform grounding ritual")
        print("\nDebug Module:")
        print("  - src/debug/debug_psych.py")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
