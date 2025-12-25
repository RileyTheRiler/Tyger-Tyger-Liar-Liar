import random
from typing import Dict, List, Optional, Any

class CombatManager:
    """
    Manages turn-based combat, chase scenes, and tense sequences.
    
    Attributes:
        skill_system: Reference to the mechanics.SkillSystem instance.
        player_state: Reference to the player's state dictionary (sanity, injuries, etc).
        enemies: List of dictionaries representing active threats.
        turn_order: List of participants sorted by initiative.
        active: Boolean indicating if a combat/chase sequence is currently running.
        round_counter: Integer tracking the current round.
        log: List of strings for combat log messages.
    """
    
    def __init__(self, skill_system, player_state):
        self.skill_system = skill_system
        self.player_state = player_state
        self.enemies: List[Dict] = []
        self.turn_order: List[Dict] = []
        self.active = False
        self.round_counter = 0
        self.log: List[str] = []
        
        # Initialize injuries if not present
        if "injuries" not in self.player_state:
            self.player_state["injuries"] = []

    def log_message(self, message: str):
        self.log.append(message)
        # Keep log size manageable
        if len(self.log) > 20:
            self.log.pop(0)

    def start_encounter(self, enemies: List[Dict], encounter_type: str = "combat"):
        """
        Starts a new encounter.
        
        Args:
            enemies: List of enemy dicts (e.g. {'name': 'Wolf', 'reflexes': 4, 'hp': 2})
            encounter_type: "combat" or "chase"
        """
        self.active = True
        self.round_counter = 1
        self.enemies = enemies
        self.log = []
        self.log_message(f"--- {encounter_type.upper()} STARTED ---")
        
        # Roll Initiative
        self._roll_initiative()
        
    def _roll_initiative(self):
        self.turn_order = []
        
        # Player Initiative
        # Using Reflexes for initiative
        reflex_check = self.skill_system.roll_check("Reflexes", 0) # DC 0 just to get total
        player_init = reflex_check["total"]
        self.turn_order.append({
            "name": "Player",
            "is_player": True,
            "initiative": player_init
        })
        
        # Enemy Initiative
        for enemy in self.enemies:
            # Simple 2d6 + 'reflexes' (or 0 if missing)
            roll = random.randint(1, 6) + random.randint(1, 6)
            bonus = enemy.get("reflexes", 0)
            total = roll + bonus
            self.turn_order.append({
                "name": enemy.get("name", "Unknown Threat"),
                "is_player": False,
                "initiative": total,
                "data": enemy
            })
            
        # Sort descending by initiative
        self.turn_order.sort(key=lambda x: x["initiative"], reverse=True)
        
        # Log order
        self.log_message("Initiative Order:")
        for participant in self.turn_order:
            self.log_message(f"  {participant['name']} ({participant['initiative']})")

    def end_encounter(self):
        self.active = False
        self.enemies = []
        self.turn_order = []
        self.log_message("--- ENCOUNTER ENDED ---")

    def get_player_turn_data(self):
        """Returns details if it's currently the player's turn to present UI choices."""
        if not self.active:
            return None
            
        # For simplicity in this text iteration, we assume strict turn order just rotates.
        # But to integrate with game loop, we just need to know if we are waiting for player input.
        # Let's assume the game loop calls `process_round` which iterates until player input is needed or round ends.
        pass

    def perform_action(self, action_type: str, target_name: str = None, description: str = "", manual_roll: int = None) -> str:
        """
        Executes a player action.
        
        Args:
            action_type: "attack", "move", "skill", "item", "flee"
            target_name: Name of the enemy targeted (if applicable)
            description: Optional context or skill name
            manual_roll: Optional forced dice roll for testing/determinism
        
        Returns:
            Result string
        """
        result_msg = f"Player uses {action_type}..."
        
        if action_type == "attack":
            # Determine skill (Firearms or Hand-to-Hand)
            # Defaulting to Hand-to-Hand for simplicity unless specified? 
            # Ideally the calling code specifies "Firearms" or "Hand-to-Hand Combat" as the action or param.
             # For now, let's assume 'description' holds the skill name or we default.
            skill = description if description in ["Firearms", "Hand-to-Hand Combat"] else "Hand-to-Hand Combat"
            
            target = self._get_enemy_by_name(target_name)
            if not target:
                return "Target not found."
            
            # Roll to hit
            # Base DC 8 + Enemy Reflexes/Defense?
            # Let's say default DC 10 + Enemy Modifier
            defense = target.get("reflexes", 0)
            dc = 8 + defense
            
            injury_penalties = self._get_total_injury_penalty(skill)
            
            # We can use combat_check helper
            outcome = self.combat_check(skill, dc, target["name"], "attack", manual_roll=manual_roll)
            
            if outcome["success"]:
                dmg = 1 # Discrete hits
                if outcome["difference"] >= 4: # Crit logic?
                    dmg = 2
                    self.log_message("CRITICAL HIT!")
                
                target["hp"] = target.get("hp", 3) - dmg
                result_msg = f"Hit {target['name']} for {dmg} damage!"
                
                if target["hp"] <= 0:
                    result_msg += f" {target['name']} is defeated!"
                    self.enemies.remove(target)
            else:
                result_msg = f"Missed {target['name']}."
        
        elif action_type == "flee":
            outcome = self.combat_check("Athletics", 10, "Escape", "move", manual_roll=manual_roll)
            if outcome["success"]:
                result_msg = "You managed to escape!"
                self.end_encounter()
                return result_msg
            else:
                result_msg = "Failed to escape!"
        
        elif action_type == "skill":
            # Arbitrary skill check in combat
            # description should be skill name?
            skill = description
            outcome = self.combat_check(skill, 10, "Environment", "skill", manual_roll=manual_roll)
            result_msg = f"Used {skill}: {'Success' if outcome['success'] else 'Failure'}."
            
        self.log_message(result_msg)
        
        # Check end condition
        if not self.enemies and self.active:
            self.log_message("All enemies defeated.")
            self.end_encounter()
            return "Victory!"

        # Enemy Turn (Simplified: immediate response)
        if self.active:
            self._process_enemy_turns()
            
        return result_msg

    def _process_enemy_turns(self):
        for enemy in self.enemies:
            if not self.active: break # Player might have fled
            
            # Enemy attacks player
            # DC 10 Reflex check for player to dodge? Or Attack roll vs Player DC?
            # Prompt says: "Player... actions... Enemy acts"
            # Let's make Enemy attack a roll against Player Reflexes (DC) or Player rolls Reflexes to dodge?
            # PbtA style: Player rolls to avoid. 
            # Traditional: Enemy rolls. 
            # Let's stick to prompt: "Modular turn system... Player and NPCs act"
            # Since user didn't specify Enemy mechanics deeply, let's have them roll simple attacks.
            
            # Enemy attack
            att = random.randint(1, 6) + random.randint(1, 6) + enemy.get("attack", 0)
            
            # Player Defense = 8 + Reflexes
            player_reflex = self.skill_system.get_skill("Reflexes")
            defense = 8 + (player_reflex.effective_level if player_reflex else 0)
            
            self.log_message(f"{enemy['name']} attacks!")
            if att >= defense:
                self.log_message(" -> HIT! Player takes damage.")
                self.apply_injury("blunt_force", "body", ["-1 Endurance"])
            else:
                self.log_message(" -> Miss!")
        
        self.round_counter += 1

    def combat_check(self, skill: str, dc: int, target: str, type: str = "attack", manual_roll: int = None) -> dict:
        """
        Executes a combat check.
        """
        # Calculate penalties
        penalties = self._get_total_injury_penalty(skill)
        
        # Need to temporarily apply injury-based penalty to the skill system? 
        # Or just subtract from total. mechanics.py `roll_check` doesn't take arbitrary mod param easily
        # except via `manual_roll` or we just subtract result.
        # BUT mechanics.py DOES return modifiers breakdown. 
        # Let's create a temporary modifier on the skill, roll, then remove it.
        
        sk_obj = self.skill_system.get_skill(skill)
        if sk_obj and penalties != 0:
            sk_obj.set_modifier("Injury", penalties)
            
        res = self.skill_system.roll_check(skill, dc, manual_roll=manual_roll)
        
        if sk_obj and penalties != 0:
            sk_obj.set_modifier("Injury", 0) # Clean up
            
        return {
            "success": res["success"],
            "total": res["total"],
            "difference": res["total"] - dc,
            "raw": res
        }

    def apply_injury(self, type: str, location: str, effects: List[str], persistent: bool = True):
        injury = {
            "type": type,
            "location": location,
            "effects": effects,
            "persistent": persistent,
            "healing_time_remaining": 72 * 60 # Default 72 hours in minutes
        }
        self.player_state["injuries"].append(injury)
        self.log_message(f"INJURY RECEIVED: {type} ({location})")

    def _get_enemy_by_name(self, name):
        for e in self.enemies:
            if e["name"].lower() == name.lower():
                return e
        return None

    def _get_total_injury_penalty(self, skill_name: str) -> int:
        total_penalty = 0
        # Parse injury strings like "-1 Reflexes" or "-2 All"
        for injury in self.player_state.get("injuries", []):
            for effect in injury["effects"]:
                parts = effect.split() 
                # e.g. ["-1", "Reflexes"] or ["-2", "Attributes"]
                if len(parts) >= 2:
                    try:
                        val = int(parts[0])
                        target = " ".join(parts[1:])
                        if target == skill_name or target == "All":
                            total_penalty += val
                    except ValueError:
                        pass
        return total_penalty
