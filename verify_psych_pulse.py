from game import Game

def verify_sync():
    print("Initializing Game Engine...")
    g = Game()
    
    # Mock some player state
    g.player_state["mental_load"] = 75
    g.player_state["fear_level"] = 85
    g.player_state["disorientation"] = True
    
    print("Fetching UI State...")
    state = g.get_ui_state()
    
    # Expected keys
    required = ['mental_load', 'fear_level', 'archetype', 'psych_flags']
    
    print("\n--- SYNC RESULTS ---")
    for key in required:
        val = state.get(key)
        print(f"{key:15}: {val}")
        
    success = all(k in state for k in required)
    
    if success:
        print("\n[SUCCESS] All psychological variables synchronized.")
        # Check specific values
        if state["mental_load"] == 75 and state["fear_level"] == 85:
            print("[SUCCESS] Data integrity verified.")
        else:
            print("[WARNING] Data mismatch in synced variables.")
    else:
        print("\n[FAILURE] Missing synchronization keys.")

if __name__ == "__main__":
    verify_sync()
