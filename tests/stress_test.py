
import sys
import os
import random
import time

# Add src to path
sys.path.append(os.path.abspath("src"))
sys.path.append(os.path.abspath("."))

from game import Game
from engine.input_system import CommandParser

def stress_test():
    print("=== STARTING STRESS TEST ===")

    # Initialize Game
    game = Game()
    game.debug_mode = True

    # 1. High Attention + Low Sanity + Night
    print("\n[TEST] Setting Critical State (High Attention, Low Sanity, Night)")
    game.player_state["sanity"] = 5.0
    # Attention system might store state differently, checking directly
    game.attention_system.attention_level = 95.0

    # Manually advance time to night (Start is 8:00 AM)
    # 8 AM to 11 PM (23:00) is 15 hours = 900 minutes
    game.time_system.advance_time(900)

    # Verify state
    # Sanity might be drained by ambient effects during advance_time.
    # We check if it is low (<= 5.0) rather than exactly 5.0.
    assert game.player_state["sanity"] <= 5.0
    assert game.time_system.current_time.hour == 23

    # 2. Fuzz Parser
    print("\n[TEST] Fuzzing Parser")
    parser = CommandParser()
    fuzz_inputs = [
        "aksdjfhkasjdf",
        "look at the void",
        "examine darkness",
        "use item on self",
        "fight the moon",
        "run away very fast",
        "talk to myself",
        "inventory check",
        "go to sleep",
        "wait 1000",
        "scream",
        "pray",
        "destroy evidence"
    ]

    for inp in fuzz_inputs:
        print(f" > Input: '{inp}'")
        try:
            # We just want to ensure no crash
            game.step(inp)
        except Exception as e:
            print(f"CRASH on '{inp}': {e}")
            raise e

    # 3. Save/Load Corruption Test
    print("\n[TEST] Save/Load Integrity")
    game.save_game("stress_test_save")

    # Corrupt state slightly
    game.player_state["sanity"] = 50.0

    # Load back
    if game.load_game("stress_test_save"):
        if game.player_state["sanity"] == 5.0:
            print("PASS: Save state restored correctly.")
        else:
            print("FAIL: Sanity not restored correctly.")
    else:
        print("FAIL: Load failed.")

    print("\n=== STRESS TEST COMPLETE ===")

if __name__ == "__main__":
    stress_test()
