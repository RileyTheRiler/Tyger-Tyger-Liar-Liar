import json
import random
import os
from utils.formatter import display_text
from engine.skill_check import roll_skill_check

# Load enemy templates
ENEMIES = {}
try:
    with open(os.path.join("data", "enemies.json"), "r") as f:
        ENEMIES = json.load(f)
except FileNotFoundError:
    print("Warning: data/enemies.json not found.")

def start_combat(state, enemy_id):
    """
    Initializes combat state against a specific enemy.
    """
    if enemy_id not in ENEMIES:
        display_text(f"Error: Enemy '{enemy_id}' not found.")
        return

    template = ENEMIES[enemy_id]
    state.combat_state = {
        "enemy_id": enemy_id,
        "name": template["name"],
        "hp": template["hp"],
        "max_hp": template["hp"],
        "turn": "player", # player always goes first for now
        "status": "engaging",
        "description": template.get("description", "A hostile presence.")
    }
    
    display_text(f"\n[COMBAT STARTED] You are facing: {template['name']}")
    display_text(template.get("description", ""))
    display_text(f"Status: {state.combat_state['status']}")

def resolve_turn(state, action, target=None):
    """
    Resolves the player's action in combat.
    Actions: 'fight', 'dodge', 'run', 'talk'
    """
    if not state.combat_state:
        return "No combat active."

    enemy_data = ENEMIES[state.combat_state["enemy_id"]]
    enemy_skills = enemy_data.get("skills", {})
    
    msg = ""

    # --- 1. FIGHT ---
    if action == "fight":
        # Attacking rolls Hand-to-Hand or Firearms vs Enemy Reflexes (DC 8 base + enemy reflex)
        weapon_skill = "Hand-to-Hand Combat" # default for now
        # TODO: Check inventory for weapons to switch skill
        
        enemy_reflex = enemy_skills.get("Reflexes", 1)
        dc = 8 + enemy_reflex
        
        skill_level = state.skills.get(weapon_skill, 0)
        result, roll = roll_skill_check(weapon_skill, skill_level, dc)
        
        display_text(f"\n[ATTACK] Rolling {weapon_skill} (Rank {skill_level}) vs DC {dc}...")
        
        if result == "success":
            damage = roll_damage("1d6") # Default player damage
            state.combat_state["hp"] -= damage
            display_text(f"SUCCESS! You hit for {damage} damage.")
            if state.combat_state["hp"] <= 0:
                end_combat(state, victory=True)
                return "victory"
        else:
            display_text("FAILURE! Your attack misses or glances off.")
            
    # --- 2. DODGE ---
    elif action == "dodge":
        # Defensive stance, gives bonus to next defense? 
        # For simple system: Dodge attempts to negate damage *if* attacked next?
        # Or maybe it's just a "Safe" turn where you don't attack but don't get hit?
        # Let's say Dodge rolls Reflexes vs Enemy Attack Skill. Success = Invulnerable this turn.
        
        dc = 10 # Base difficulty
        skill_level = state.skills.get("Reflexes", 0)
        result, roll = roll_skill_check("Reflexes", skill_level, dc)
        
        if result == "success":
            display_text("SUCCESS! You weave out of range, safe for a moment.")
            state.combat_state["dodging"] = True
        else:
            display_text("FAILURE! You stumble and remain exposed.")
            state.combat_state["dodging"] = False

    # --- 3. RUN ---
    elif action == "run":
        # Athletics vs Enemy Athletics or 12
        dc = 10 + enemy_skills.get("Athletics", 0)
        skill_level = state.skills.get("Athletics", 0)
        result, roll = roll_skill_check("Athletics", skill_level, dc)
        
        if result == "success":
            display_text("SUCCESS! You scramble away into the darkness.")
            end_combat(state, victory=False, escaped=True)
            return "escaped"
        else:
            display_text("FAILURE! You are cornered.")
    
    # --- 4. TALK ---
    elif action == "talk":
        # Authority or Empathy vs Enemy Volition/Empathy
        target_skill = "Authority" # could be Empathy
        dc = 12 # Hard check to talk down a fight
        skill_level = state.skills.get(target_skill, 0)
        
        result, roll = roll_skill_check(target_skill, skill_level, dc)
        
        if result == "success":
            display_text("SUCCESS! Your words give them pause.")
            state.combat_state["status"] = "hesitating"
            # Could lead to end combat?
        else:
            display_text("FAILURE! They are not listening.")

    else:
        display_text("Invalid combat action.")
        return "invalid"

    # End player turn actions
    return "continue"

def enemy_turn(state):
    """
    Resolves the enemy's action against the player.
    """
    if not state.combat_state:
        return

    # If player won or escaped, this shouldn't run, but check just in case
    
    enemy_data = ENEMIES.get(state.combat_state["enemy_id"], {})
    enemy_name = state.combat_state["name"]
    
    # Check if player is dodging
    if state.combat_state.get("dodging"):
        display_text(f"{enemy_name} strikes, but you are already moving. MISS.")
        state.combat_state["dodging"] = False # Reset dodge
        return

    display_text(f"\n{enemy_name} attacks!")
    
    # Enemy rolls 'Hand-to-Hand Combat' (or similar) vs Player Defense (DC 10 + Reflexes/2?)
    # Simplified: Enemy makes a flat roll or just fixed damage?
    # Let's simple: Enemy rolls Attack Skill vs Player Reflexes DC.
    
    att_skill = enemy_data.get("skills", {}).get("Hand-to-Hand Combat", 2)
    player_reflex = state.skills.get("Reflexes", 0)
    
    # Enemy Attack Roll (Simulated 2d6)
    attack_roll = roll_damage("2d6") + att_skill
    defense_dc = 8 + player_reflex
    
    display_text(f"Enemy Attack: {attack_roll} vs Your Defense: {defense_dc}")
    
    if attack_roll >= defense_dc:
        dmg_str = enemy_data.get("damage", "1d4")
        dmg = roll_damage(dmg_str)
        display_text(f"HIT! You take {dmg} damage.")
        
        # Apply damage / Injury
        # For now, we don't have HP, we have Injuries.
        # Maybe raw damage -> threshold -> Injury?
        # Or simple: "You get hurt."
        
        from engine.injury_system import apply_injury
        apply_injury(state, "general", "minor", {"General": -1})
        
    else:
        display_text(f"MISS! You deflect the blow.")

def roll_damage(die_str):
    """
    Parses '1d6', '2d4+1' etc and returns integer result.
    """
    try:
        if "+" in die_str:
            base, mod = die_str.split("+")
            mod = int(mod)
        else:
            base = die_str
            mod = 0
            
        count, sides = base.split("d")
        count = int(count)
        sides = int(sides)
        
        total = sum(random.randint(1, sides) for _ in range(count))
        return total + mod
    except:
        return 1

def end_combat(state, victory=False, escaped=False):
    if victory:
        display_text(f"\n[COMBAT END] {state.combat_state['name']} is defeated.")
    elif escaped:
        display_text(f"\n[COMBAT END] You escaped.")
    
    state.combat_state = None
