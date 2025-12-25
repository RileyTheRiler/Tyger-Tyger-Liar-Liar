import sys
import os
import json

sys.path.append(os.path.abspath("src"))
sys.path.append(os.path.abspath("."))

from game import Game

def verify_feedback():
    print("Verifying Feedback Tool...")

    game = Game()

    # Mock some state
    game.player_state["sanity"] = 55.5
    game.player_state["event_flags"].add("test_flag")

    print("Submitting feedback...")
    game.submit_feedback("Verification Test")

    if os.path.exists("feedback.log"):
        with open("feedback.log", "r") as f:
            content = f.read()
            print("Log content found.")

            if "Verification Test" in content:
                print("[OK] Comment found.")
            else:
                print("[FAIL] Comment missing.")

            if "STATE:" in content and "sanity" in content and "55.5" in content:
                print("[OK] State dump found.")
            else:
                print("[FAIL] State dump missing or incorrect.")

            if "test_flag" in content:
                print("[OK] Set serialization worked (test_flag found).")
            else:
                print("[FAIL] Set serialization failed.")
    else:
        print("[FAIL] feedback.log not created.")

if __name__ == "__main__":
    verify_feedback()
