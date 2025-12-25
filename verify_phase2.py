import os
import sys
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent
src_dir = root_dir / "src"
sys.path.append(str(src_dir))
sys.path.append(str(src_dir / "engine"))

from game_state import GameState

def verify_phase2():
    print("Verifying Phase 2: Game State + Rules Engine...")
    
    # 1. Initialization
    gs = GameState()
    print(f"Initial State: Day {gs.time['day']}, Block {gs.time['block']}, Population {gs.population_current}")
    
    # 2. Effect Handlers
    gs.apply_flag("met_stranger", True)
    gs.modify_trust("npc_stranger", 10)
    gs.advance_time(120) # 2 hours
    gs.modify_attention(15)
    gs.modify_population(-1)
    gs.add_condition("cold_exposure")
    gs.add_board_node({"id": "node_1", "type": "clue", "title": "Lost Key"})
    gs.add_board_edge("node_1", "theory_1", "supports")
    
    print("\nState after modifications:")
    print(f"Flag 'met_stranger': {gs.flags.get('met_stranger')}")
    print(f"Trust 'npc_stranger': {gs.trust.get('npc_stranger')}")
    print(f"Time: {gs.time['day']}d {gs.time['minutes']//60}:0{gs.time['minutes']%60 if gs.time['minutes']%60 < 10 else gs.time['minutes']%60} ({gs.time['block']})")
    print(f"Attention: {gs.attention_meter}")
    print(f"Population: {gs.population_current}")
    print(f"Conditions: {gs.conditions}")
    
    # 3. Skill Calculation
    gs.attributes["REASON"] = 4
    gs.skills["Logic"] = 2
    effective = gs.get_effective_skill("Logic")
    print(f"\nEffective Logic (Attr 4 + Rank 2): {effective}")
    
    if effective != 6:
        print("[FAILURE] Skill calculation is incorrect.")
        return
    
    # 4. Save / Load
    save_path = "test_save.json"
    gs.save(save_path)
    print(f"\nSaved to {save_path}")
    
    loaded_gs = GameState.load(save_path)
    print(f"Loaded State: Day {loaded_gs.time['day']}, Population {loaded_gs.population_current}")
    
    if (loaded_gs.flags.get("met_stranger") == True and 
        loaded_gs.population_current == 346 and 
        loaded_gs.time["minutes"] == 600):
        print("\n[SUCCESS] Phase 2: Game State persistence and logic verified.")
        os.remove(save_path)
    else:
        print("\n[FAILURE] Persistence check failed.")

if __name__ == "__main__":
    verify_phase2()
