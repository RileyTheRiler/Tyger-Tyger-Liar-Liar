"""
Week 14: Board System Verification Script
Tests theory acquisition, internalization, and mechanics integration.
"""

import sys
import os
sys.path.append('src')
sys.path.append('src/engine')

from board import Board, Theory
from mechanics import SkillSystem
import json

def test_theory_data_loading():
    """Test that theories.json loads correctly."""
    print("="*60)
    print("TEST 1: Theory Data Loading")
    print("="*60)
    
    try:
        with open('data/theories.json', 'r') as f:
            theories_data = json.load(f)
        
        print(f"✓ Loaded {len(theories_data)} theories from data/theories.json")
        
        for theory_id, data in theories_data.items():
            print(f"  - {theory_id}: {data['name']} ({data['category']})")
        
        print("✓ Theory data loading: PASSED\n")
        return True
    except Exception as e:
        print(f"✗ Theory data loading: FAILED - {e}\n")
        return False

def test_theory_class_fields():
    """Test that Theory class has all Week 14 fields."""
    print("="*60)
    print("TEST 2: Theory Class Fields")
    print("="*60)
    
    try:
        with open('data/theories.json', 'r') as f:
            theories_data = json.load(f)
        
        # Create a theory instance
        theory_id = list(theories_data.keys())[0]
        theory_data = theories_data[theory_id]
        theory = Theory(theory_id, theory_data)
        
        # Check for Week 14 fields
        required_fields = [
            'requirements', 'unlocks', 'on_internalize_effects', 'lens_bias'
        ]
        
        for field in required_fields:
            if hasattr(theory, field):
                print(f"✓ Theory has '{field}' field")
            else:
                print(f"✗ Theory missing '{field}' field")
                return False
        
        print("✓ Theory class fields: PASSED\n")
        return True
    except Exception as e:
        print(f"✗ Theory class fields: FAILED - {e}\n")
        return False

def test_board_methods():
    """Test that Board has Week 14 methods."""
    print("="*60)
    print("TEST 3: Board Methods")
    print("="*60)
    
    try:
        # Mock theories data
        from theories import THEORY_DATA
        board = Board()
        
        # Check for Week 14 methods
        required_methods = [
            'can_discover_theory',
            'apply_internalize_effects',
            'get_active_theory_unlocks'
        ]
        
        for method in required_methods:
            if hasattr(board, method):
                print(f"✓ Board has '{method}' method")
            else:
                print(f"✗ Board missing '{method}' method")
                return False
        
        print("✓ Board methods: PASSED\n")
        return True
    except Exception as e:
        print(f"✗ Board methods: FAILED - {e}\n")
        return False

def test_theory_internalization():
    """Test theory internalization flow."""
    print("="*60)
    print("TEST 4: Theory Internalization")
    print("="*60)
    
    try:
        from theories import THEORY_DATA
        board = Board()
        
        # Find an available theory
        available_theory = None
        for tid, theory in board.theories.items():
            if theory.status == "available":
                available_theory = theory
                break
        
        if not available_theory:
            print("✗ No available theories found")
            return False
        
        print(f"Testing with theory: {available_theory.name}")
        
        # Start internalization
        success = board.start_internalizing(available_theory.id)
        if not success:
            print("✗ Failed to start internalization")
            return False
        
        print(f"✓ Started internalizing '{available_theory.name}'")
        print(f"  Status: {available_theory.status}")
        print(f"  Progress: {available_theory.internalization_progress_minutes}/{available_theory.internalize_time_hours * 60}min")
        
        # Simulate time passing
        messages = board.on_time_passed(available_theory.internalize_time_hours * 60)
        
        if available_theory.status == "active":
            print(f"✓ Theory became active after time passed")
            print(f"  Messages: {messages}")
        else:
            print(f"✗ Theory did not become active (status: {available_theory.status})")
            return False
        
        # Check modifiers
        modifiers = board.get_all_modifiers()
        print(f"✓ Active theory modifiers: {modifiers}")
        
        print("✓ Theory internalization: PASSED\n")
        return True
    except Exception as e:
        print(f"✗ Theory internalization: FAILED - {e}\n")
        import traceback
        traceback.print_exc()
        return False

def test_theory_conflicts():
    """Test theory conflict system."""
    print("="*60)
    print("TEST 5: Theory Conflicts")
    print("="*60)
    
    try:
        from theories import THEORY_DATA
        board = Board()
        
        # Find two conflicting theories
        theory1 = board.get_theory("trust_no_one")
        theory2 = board.get_theory("protect_innocent")
        
        if not theory1 or not theory2:
            print("✗ Test theories not found")
            return False
        
        # Internalize first theory
        board.start_internalizing("trust_no_one")
        board.on_time_passed(theory1.internalize_time_hours * 60)
        
        print(f"✓ Internalized '{theory1.name}'")
        
        # Try to internalize conflicting theory
        can_internalize, reason = board.can_internalize("protect_innocent")
        
        if not can_internalize:
            print(f"✓ Correctly blocked conflicting theory")
            print(f"  Reason: {reason}")
        else:
            print(f"✗ Failed to block conflicting theory")
            return False
        
        print("✓ Theory conflicts: PASSED\n")
        return True
    except Exception as e:
        print(f"✗ Theory conflicts: FAILED - {e}\n")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\\n" + "="*60)
    print("WEEK 14: BOARD SYSTEM VERIFICATION")
    print("="*60 + "\\n")
    
    tests = [
        test_theory_data_loading,
        test_theory_class_fields,
        test_board_methods,
        test_theory_internalization,
        test_theory_conflicts
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("="*60)
    print("SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\\n✓ ALL TESTS PASSED")
        return 0
    else:
        print(f"\\n✗ {total - passed} TEST(S) FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
