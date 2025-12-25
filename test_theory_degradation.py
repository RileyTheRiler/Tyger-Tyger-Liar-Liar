"""
Test script for theory degradation mechanics.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from board import Board

def test_theory_degradation():
    print("=" * 60)
    print("TESTING THEORY DEGRADATION SYSTEM")
    print("=" * 60)
    
    board = Board()
    
    # Test 1: Internalize a theory
    print("\n[TEST 1] Internalizing 'I Want To Believe'...")
    board.discover_theory("i_want_to_believe")
    success = board.start_internalizing("i_want_to_believe")
    print(f"  Result: {'SUCCESS' if success else 'FAILED'}")
    
    # Complete internalization
    messages = board.on_time_passed(360)  # 6 hours
    for msg in messages:
        print(f"  {msg}")
    
    theory = board.get_theory("i_want_to_believe")
    print(f"  Status: {theory.status}")
    print(f"  Health: {theory.health}%")
    
    # Test 2: Check auto-locks
    print("\n[TEST 2] Checking auto-locks...")
    rational_theory = board.get_theory("there_is_a_rational_explanation")
    print(f"  'There's A Rational Explanation' status: {rational_theory.status}")
    print(f"  Expected: locked (auto-locked by 'I Want To Believe')")
    
    # Test 3: Add contradicting evidence
    print("\n[TEST 3] Adding contradicting evidence...")
    print(f"  Initial health: {theory.health}%")
    
    result = board.add_contradiction_to_theory("i_want_to_believe", "evidence_001")
    print(f"  {result['message']}")
    print(f"  New health: {theory.health}%")
    print(f"  Sanity damage: {result.get('sanity_damage', 0)}")
    
    # Test 4: Multiple contradictions to trigger collapse
    print("\n[TEST 4] Adding multiple contradictions to trigger collapse...")
    for i in range(2, 8):
        result = board.add_contradiction_to_theory("i_want_to_believe", f"evidence_{i:03d}")
        print(f"  Contradiction {i}: Health={theory.health}%, Message: {result['message']}")
        
        if result.get('theory_collapsed'):
            print(f"\n  ⚠ THEORY COLLAPSED!")
            print(f"  Total sanity damage: {result['sanity_damage']}")
            print(f"  Theory status: {theory.status}")
            break
    
    # Test 5: Theory health status
    print("\n[TEST 5] Getting theory health status...")
    status = board.get_theory_health_status("i_want_to_believe")
    print(f"  Health: {status['health']}%")
    print(f"  Status: {status['status']}")
    print(f"  Evidence count: {status['evidence_count']}")
    print(f"  Contradictions: {status['contradictions']}")
    
    # Test 6: New theories
    print("\n[TEST 6] Testing new theories...")
    new_theories = [
        "conspiracy_of_kindness",
        "the_entity_is_hostile",
        "the_entity_is_neutral",
        "kaltvik_is_a_prison",
        "kaltvik_is_a_sanctuary"
    ]
    
    for theory_id in new_theories:
        t = board.get_theory(theory_id)
        if t:
            print(f"  ✓ {t.name} (degradation: {t.degradation_rate}%)")
        else:
            print(f"  ✗ {theory_id} NOT FOUND")
    
    print("\n" + "=" * 60)
    print("TESTS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_theory_degradation()
