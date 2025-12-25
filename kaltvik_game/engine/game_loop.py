from engine.scene_manager import load_scene
from utils.formatter import display_text, highlight_objects
from engine.input_handler import get_player_input
from engine.character_sheet import show_character_sheet
from engine.skill_check import roll_skill_check
from engine.board_system import show_board, internalize_theory, advance_theory_timers, abandon_theory
from engine.combat_system import resolve_turn, enemy_turn, start_combat
from engine.injury_system import heal_injury
import sys

def run_game_loop(state):
    """
    Main runtime loop for the game.
    """
    while True:
        try:
            scene = load_scene(state.current_scene)
            
            # Highlight interactive objects in the scene text
            objects = scene.get("objects", {})
            highlighted_text = highlight_objects(scene["text"], objects)
            display_text(highlighted_text)
            
            if not scene.get("options"):
                print("The story ends here.")
                break

            for i, opt in enumerate(scene["options"]):
                print(f"{i+1}. {opt['label']}")

            action_type, payload = get_player_input(scene, objects)

            # --- COMBAT FLOW ---
            if state.combat_state:
                # If we are in combat, intercept invalid or non-combat movements?
                # For now, we allow checking inventory/stats, but movement might need blocking.
                if action_type == "movement": # If we had movement
                   print("You cannot leave while in combat! (Use 'run')")
                   continue
                
                # Combat actions
                if action_type == "combat_action":
                    verb = payload
                    # Player Turn
                    outcome = resolve_turn(state, verb)
                    
                    if outcome == "victory" or outcome == "escaped":
                        # Combat ended, loop will refresh and handle clean state
                        input("\nPress Enter to continue...")
                        continue
                        
                    # Enemy Turn (if still fighting)
                    enemy_turn(state)
                    # Check for death/collapse automatically happens inside injury logic/combat logic?
                    # If we collapsed, state.current_scene is already updated to hospital.
                    input("\nPress Enter to continue...")
                    continue
                
                # Allow other actions like 'medicate' or 'check' but warn?
                if action_type not in ["combat_action", "roll", "check", "injuries", "action", "medicate"]:
                    print("You are in combat! Options: fight, dodge, run, talk.")

            # --- NORMAL FLOW ---

            if action_type == "choice":
                state.current_scene = scene["options"][payload]["next"]

            elif action_type == "examine":
                target = payload
                print(f"\n{objects[target]}")
                
                check = scene.get("check")
                if check:
                    skill_name = check["skill"]
                    dc = check["dc"]
                    skill_level = state.skills.get(skill_name, 0)
                    
                    result, roll = roll_skill_check(
                        skill_name, 
                        skill_level, 
                        dc, 
                        check.get("white_id"), 
                        check.get("is_red", False), 
                        state
                    )
                    
                    print(f"\n[CHECK: {skill_name}] Roll: {roll} + {skill_level} vs DC {dc}")
                    
                    if result == "success":
                        print(f"RESULT: SUCCESS")
                        display_text(check["success_text"])
                    elif result == "fail":
                        print(f"RESULT: FAILURE")
                        display_text(check["fail_text"])
                    elif result == "locked":
                        print("You’ve already tried this and failed (locked).")

                input("\nPress Enter to continue...")

            elif action_type == "character":
                show_character_sheet(state)
                input("\nPress Enter to continue...")

            elif action_type == "theories":
                show_board(state)
                input("\nPress Enter to continue...")

            elif action_type == "internalize":
                msg = internalize_theory(payload, state)
                print(f"\n{msg}")
                input("\nPress Enter to continue...")
            
            elif action_type == "abandon":
                msg = abandon_theory(payload, state)
                print(f"\n{msg}")
                input("\nPress Enter to continue...")

            elif action_type == "advance":
                hours = payload
                print(f"\nAdvancing time by {hours} hours...")
                advance_theory_timers(state, hours)
                input("\nPress Enter to continue...")

            elif action_type == "roll":
                skill_name, dc = payload
                skill_level = state.skills.get(skill_name, 0)
                result, roll = roll_skill_check(skill_name, skill_level, dc)
                print(f"\n[MANUAL ROLL: {skill_name}] Roll: {roll} + {skill_level} vs DC {dc}")
                print(f"RESULT: {result.upper()}")
                input("\nPress Enter to continue...")

            elif action_type == "check":
                skill_name = payload
                val = state.skills.get(skill_name, "Unknown")
                print(f"\n[DEBUG] {skill_name} level: {val}")
                input("\nPress Enter to continue...")

            elif action_type == "combat_action":
                if not state.combat_state:
                    print("There is no one to fight here.")
                input("\nPress Enter to continue...")

            elif action_type == "injuries":
                print("\n[PHYSICAL STATUS]")
                if not state.injuries:
                    print("You are healthy.")
                else:
                    for inj in state.injuries:
                        print(f"- {inj['severity'].upper()} {inj['location']} injury ({inj['effect']})")
                input("\nPress Enter to continue...")
            
            elif action_type == "medicate":
                # Check for medkit item? For prototype, just heal first injury.
                heal_injury(state)
                input("\nPress Enter to continue...")

            elif action_type == "rest":
                print("\nYou rest for a while...")
                if state.combat_state:
                    print("It's too dangerous to rest now!")
                else:
                    advance_theory_timers(state, 8)
                    # Heals
                    heal_injury(state)
                input("\nPress Enter to continue...")

            elif action_type == "action":
                verb, target = payload
                print(f"\nYou try to {verb} {target}, but nothing happens yet.")
                input("\nPress Enter to continue...")

            elif action_type == "invalid":
                continue


        
        except FileNotFoundError:
            print(f"Error: Scene file '{state.current_scene}.json' not found.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            import traceback
            traceback.print_exc()
            break
