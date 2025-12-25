"""
Test script for Corkboard Eureka patterns.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from board import Board
from inventory_system import InventoryManager, Evidence
from corkboard_minigame import CorkboardMinigame

def test_eureka():
    print("=" * 60)
    print("TESTING CORKBOARD EUREKA MECHANICS")
    print("=" * 60)
    
    board = Board()
    inventory = InventoryManager()
    minigame = CorkboardMinigame(board, inventory)
    
    # Add relevant evidence
    inventory.add_evidence(Evidence("aurora_footage", "A grainy video of the lights.", "digital"))
    inventory.add_evidence(Evidence("blood_sample", "Dark viscous fluid from the clearing.", "physical"))
    inventory.add_evidence(Evidence("population_log", "A list of residents.", "document"))
    inventory.add_evidence(Evidence("missing_report_01", "Report on Jensen's disappearance.", "document"))
    
    # Test 1: Link aurora and blood (Should unlock The Entity Is Hostile)
    print("\n[TEST 1] Linking 'aurora_footage' and 'blood_sample'...")
    result = minigame.link_evidence("aurora_footage", "blood_sample")
    print(f"  {result['message']}")
    print(f"  Eureka triggered: {result.get('eureka', False)}")
    
    theory = board.get_theory("the_entity_is_hostile")
    print(f"  Theory 'The Entity Is Hostile' status: {theory.status}")
    
    # Test 2: Link population and missing report (Should unlock Kaltvik Is A Prison)
    print("\n[TEST 2] Linking 'population_log' and 'missing_report_01'...")
    result = minigame.link_evidence("population_log", "missing_report_01")
    print(f"  {result['message']}")
    print(f"  Eureka triggered: {result.get('eureka', False)}")
    
    theory = board.get_theory("kaltvik_is_a_prison")
    print(f"  Theory 'Kaltvik Is A Prison' status: {theory.status}")
    
    # Test 3: Re-link same evidence (Should fail)
    print("\n[TEST 3] Re-linking same evidence...")
    result = minigame.link_evidence("aurora_footage", "blood_sample")
    print(f"  {result['message']}")
    
    # Test 4: Link unrelated evidence (No Eureka)
    print("\n[TEST 4] Linking unrelated evidence...")
    result = minigame.link_evidence("aurora_footage", "population_log")
    print(f"  {result['message']}")
    print(f"  Eureka triggered: {result.get('eureka', False)}")

    # Test 5: False Trail
    print("\n[TEST 5] Linking False Trail evidence...")
    inventory.add_evidence(Evidence("witness_statement_01", "A confusing account.", "testimony"))
    inventory.add_evidence(Evidence("unreliable_photo", "A blurry smudge.", "physical"))
    result = minigame.link_evidence("witness_statement_01", "unreliable_photo")
    print(f"  {result['message']}")
    print(f"  False Trail triggered: {result.get('false_trail', False)}")
    print(f"  Sanity drain: {result.get('sanity_drain', 0)}")

    print("\n" + "=" * 60)
    print("TESTS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_eureka()
