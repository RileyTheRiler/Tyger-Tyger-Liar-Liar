import sys
import os
import io
import json
from unittest.mock import MagicMock, patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tyger_game.engine.character import Character
from tyger_game.engine.dialogue import DialogueManager
from tyger_game.engine.alignment_system import AlignmentSystem
from tyger_game.utils.constants import ALIGNMENTS

def verify_dialogue_filtering():
    print("\n--- Testing Dialogue Alignment Filters ---")
    
    # Load Test Data
    with open("tyger_game/data/dialogues/epistemic_test.json", "r") as f:
        node_data = json.load(f)

    # Setup Character
    char = Character("TestSubject")
    dm = DialogueManager()
    
    # 1. Test Filter (Neutral Character)
    # Character is not "Fundamentalist", so the 3rd option should be HIDDEN.
    # We need to capture stdout to verify what is printed.
    
    # We patch input to just quit immediately (or select invalid) to break loop if needed, 
    # but actually _run_node loops. We should patch `get_input` to return '1' (which is valid)
    # and then patch `_run_node` to break loop after one choice? 
    # Or simpler: we can inspect the `choices` list variable inside `_run_node` if we refactor,
    # but since we can't easily, we'll spy on `print`.
    
    print("Scenario 1: Neutral Character")
    with patch('builtins.print') as mock_print:
        with patch('tyger_game.engine.dialogue.get_input', side_effect=['1']):
             dm.start_dialogue(node_data, char)
        
        # Check printed options
        # We expect "1. [Skeptic] It's just a drone..."
        # We expect "2. [Believer] This is it..."
        # We DO NOT expect "3. Only a true believer..."
        
        output = [call.args[0] for call in mock_print.call_args_list if call.args]
        found_fundamentalist = any("Only a true believer" in s for s in output)
        if found_fundamentalist:
            print("FAILURE: Fundamentalist option was shown to Neutral character.")
        else:
            print("SUCCESS: Fundamentalist option correctly hidden.")

    # 2. Test Unlock (Fundamentalist Character)
    print("\nScenario 2: Fundamentalist Character")
    char.alignment_scores["believer"] = 10
    char.alignment_scores["order"] = 10
    char.active_alignment = ALIGNMENTS["FUNDAMENTALIST"]
    
    with patch('builtins.print') as mock_print:
        with patch('tyger_game.engine.dialogue.get_input', side_effect=['3']): # Select the locked one
             dm.start_dialogue(node_data, char)
        
        output = [call.args[0] for call in mock_print.call_args_list if call.args]
        found_fundamentalist = any("Only a true believer" in s for s in output)
        if found_fundamentalist:
            print("SUCCESS: Fundamentalist option correctly unlocked.")
        else:
            print("FAILURE: Fundamentalist option was HIDDEN for Fundamentalist character.")

    # 3. Test Alignment Effect
    # Selecting Option 1 (Skeptic) should increment Skeptic score
    print("\nScenario 3: Alignment Effect Application")
    char_effect = Character("EffectTest")
    with patch('builtins.print') as mock_print:
        with patch('tyger_game.engine.dialogue.get_input', side_effect=['1']):
            dm.start_dialogue(node_data, char_effect)
            
    if char_effect.alignment_scores["skeptic"] == 1:
        print("SUCCESS: Skeptic score incremented.")
    else:
        print(f"FAILURE: Skeptic score is {char_effect.alignment_scores['skeptic']}, expected 1.")

if __name__ == "__main__":
    verify_dialogue_filtering()
