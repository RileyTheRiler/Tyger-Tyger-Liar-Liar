
import sys
import os
import io
import contextlib

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))
sys.path.append(os.path.join(os.getcwd(), 'src/engine'))

from game import Game

def test_fail_forward_broken():
    """Test drifting towards 'Truth uncovered but psyche broken'"""
    print("\n--- Testing 'Broken Psyche' Ending Drift ---")
    game = Game()

    # Simulate low sanity (Broken)
    game.player_state['sanity'] = 10

    # Force counters
    game.player_state['ff_counters']['broken'] = 50
    game.player_state['ff_counters']['obscured'] = 0
    game.player_state['ff_counters']['annihilation'] = 0

    # Force limit
    game.player_state['investigation_count'] = 25

    # Run check
    triggered = game.check_fail_forward_ending()

    if triggered and game.scene_manager.current_scene_id == "ending_broken":
        print("✓ Successfully triggered 'ending_broken'")
    else:
        print(f"✗ Failed. Scene: {game.scene_manager.current_scene_id}")

def test_fail_forward_obscured():
    """Test drifting towards 'Psyche intact but truth obscured'"""
    print("\n--- Testing 'Obscured Truth' Ending Drift ---")
    game = Game()

    # Simulate high sanity (Obscured)
    game.player_state['sanity'] = 90

    # Force counters
    game.player_state['ff_counters']['broken'] = 0
    game.player_state['ff_counters']['obscured'] = 10 # Will be boosted by high sanity
    game.player_state['ff_counters']['annihilation'] = 0

    # Force limit
    game.player_state['investigation_count'] = 25

    triggered = game.check_fail_forward_ending()

    if triggered and game.scene_manager.current_scene_id == "ending_obscured":
        print("✓ Successfully triggered 'ending_obscured'")
    else:
        print(f"✗ Failed. Scene: {game.scene_manager.current_scene_id}")

def test_fail_forward_annihilation():
    """Test drifting towards 'Mutual Annihilation'"""
    print("\n--- Testing 'Mutual Annihilation' Ending Drift ---")
    game = Game()

    # Simulate high attention
    game.attention_system.attention_level = 80

    # Force counters
    game.player_state['ff_counters']['broken'] = 0
    game.player_state['ff_counters']['obscured'] = 0
    game.player_state['ff_counters']['annihilation'] = 50

    # Force limit
    game.player_state['investigation_count'] = 25

    triggered = game.check_fail_forward_ending()

    if triggered and game.scene_manager.current_scene_id == "ending_annihilation":
        print("✓ Successfully triggered 'ending_annihilation'")
    else:
        print(f"✗ Failed. Scene: {game.scene_manager.current_scene_id}")

def test_investigation_counter():
    """Test that investigation counter increments"""
    print("\n--- Testing Investigation Counter ---")
    game = Game()
    initial = game.player_state['investigation_count']

    # Mock search
    game.process_command("search", [])

    if game.player_state['investigation_count'] > initial:
        print(f"✓ Counter incremented: {initial} -> {game.player_state['investigation_count']}")
    else:
        print(f"✗ Counter failed to increment: {game.player_state['investigation_count']}")

if __name__ == "__main__":
    # Suppress game output during setup
    with contextlib.redirect_stdout(io.StringIO()):
        pass

    test_fail_forward_broken()
    test_fail_forward_obscured()
    test_fail_forward_annihilation()
    test_investigation_counter()
