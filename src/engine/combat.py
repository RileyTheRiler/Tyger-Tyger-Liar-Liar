import random
import json
import os
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
    
    def __init__(self, skill_system, player_state, injury_system=None, trauma_system=None, inventory_system=None):
        self.skill_system = skill_system
        self.player_state = player_state
        self.injury_system = injury_system
        self.trauma_system = trauma_system
        self.inventory_system = inventory_system
        self.enemies: List[Dict] = []
        self.turn_order: List[Dict] = []
        self.active = False
        self.round_counter = 0
        self.log: List[str] = []
        self.encounter_templates: Dict[str, dict] = {}
        
        # Initialize injuries if not present
        if "injuries" not in self.player_state:
            self.player_state["injuries"] = []

    def load_encounter_templates(self, filepath: str):
        """Load encounter templates from JSON file."""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.encounter_templates = json.load(f)
                print(f"[CombatManager] Loaded {len(self.encounter_templates)} encounter templates.")
            except Exception as e:
                print(f"[CombatManager] Error loading encounters: {e}")
    
    def log_message(self, message: str):
        self.log.append(message)
        # Keep log size manageable
        if len(self.log) > 20:
            self.log.pop(0)

    def start_encounter(self, encounter_id: str = None, enemies: List[Dict] = None, encounter_type: str = "combat"):
        """
        Starts a new encounter.
        
        Args:
            encounter_id: Template ID to load from encounter_templates
            enemies: List of enemy dicts (if not using template)
            encounter_type: "combat" or "chase"
        """
        if encounter_id and encounter_id in self.encounter_templates:
            template = self.encounter_templates[encounter_id]
            self.enemies = [template.copy()]
        elif enemies:
            self.enemies = enemies
        else:
            raise ValueError("Must provide either encounter_id or enemies list")
        
        self.active = True
        self.round_counter = 1
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

    def perform_action(self, action_type: str, target_name: str = None, description: str = "") -> Dict[str, Any]:
        """
        Executes a player action.
        
        Args:
            action_type: "attack", "dodge", "talk", "flee"
            target_name: Name of the enemy targeted (if applicable)
            description: Additional context (skill name, dialogue, etc.)
        
        Returns:
            Result dictionary with messages and effects
        """
        result = {"action": action_type, "messages": [], "effects": {}}
        
        if action_type == "attack" or action_type == "fight":
            # Determine weapon skill from equipped items
            skill = self._get_combat_skill()
            
            target = self._get_enemy_by_name(target_name)
            if not target:
                result["messages"].append("Target not found.")
                return result
            
            # Roll to hit
            defense = target.get("reflexes", 0)
            dc = 8 + defense
            
            outcome = self.combat_check(skill, dc, target["name"], "attack")
            
            if outcome["success"]:
                dmg = 1
                if outcome["difference"] >= 4:
                    dmg = 2
                    self.log_message("CRITICAL HIT!")
                
                target["hp"] = target.get("hp", 3) - dmg
                msg = f"Hit {target['name']} for {dmg} damage!"
                self.log_message(msg)
                result["messages"].append(msg)
                
                if target["hp"] <= 0:
                    defeat_msg = f"{target['name']} is defeated!"
                    self.log_message(defeat_msg)
                    result["messages"].append(defeat_msg)
                    self.enemies.remove(target)
            else:
                msg = f"Missed {target['name']}."
                self.log_message(msg)
                result["messages"].append(msg)
        
        elif action_type == "dodge":
            # Dodge gives defensive bonus for next enemy attack
            dc = 10
            outcome = self.combat_check("Reflexes", dc, "Dodge", "defense")
            
            if outcome["success"]:
                self.player_state["combat_dodging"] = True
                msg = "You weave and bob, ready to evade the next attack."
                self.log_message(msg)
                result["messages"].append(msg)
            else:
                msg = "You stumble and remain exposed."
                self.log_message(msg)
                result["messages"].append(msg)
        
        elif action_type == "talk" or action_type == "intimidate" or action_type == "reason":
            # Attempt to de-escalate with Authority or Empathy
            target = self._get_enemy_by_name(target_name) if target_name else self.enemies[0] if self.enemies else None
            if not target:
                result["messages"].append("No one to talk to.")
                return result
            
            # Check if enemy has dialogue options
            if not target.get("dialogue_options"):
                msg = f"{target['name']} is beyond reason."
                self.log_message(msg)
                result["messages"].append(msg)
            else:
                skill = "Authority" if action_type == "intimidate" else "Empathy"
                dc = 12  # Hard check to de-escalate combat
                
                outcome = self.combat_check(skill, dc, target["name"], "social")
                
                if outcome["success"]:
                    msg = f"Your words give {target['name']} pause. The tension eases."
                    self.log_message(msg)
                    result["messages"].append(msg)
                    result["effects"]["de_escalated"] = True
                    # Could end combat or make enemy non-hostile
                    self.end_encounter()
                    return result
                else:
                    msg = f"{target['name']} is not listening."
                    self.log_message(msg)
                    result["messages"].append(msg)
        
        elif action_type == "flee" or action_type == "run":
            dc = 10 + (self.enemies[0].get("skills", {}).get("Athletics", 0) if self.enemies else 0)
            outcome = self.combat_check("Athletics", dc, "Escape", "move")
            
            if outcome["success"]:
                msg = "You scramble away into the darkness!"
                self.log_message(msg)
                result["messages"].append(msg)
                result["effects"]["escaped"] = True
                self.end_encounter()
                return result
            else:
                msg = "You try to run, but they cut you off!"
                self.log_message(msg)
                result["messages"].append(msg)
        
        # Check end condition
        if not self.enemies and self.active:
            self.log_message("All enemies defeated.")
            result["messages"].append("Victory!")
            result["effects"]["victory"] = True
            self.end_encounter()
            return result

        # Enemy Turn (Simplified: immediate response)
        if self.active and not result.get("effects", {}).get("escaped"):
            enemy_results = self._process_enemy_turns()
            result["messages"].extend(enemy_results)
            
        return result

    def _process_enemy_turns(self) -> List[str]:
        """Process all enemy turns and return messages."""
        messages = []
        
        for enemy in self.enemies:
            if not self.active:
                break
            
            # Check if player is dodging
            if self.player_state.get("combat_dodging", False):
                msg = f"{enemy['name']} strikes, but you're already moving. MISS!"
                self.log_message(msg)
                messages.append(msg)
                self.player_state["combat_dodging"] = False
                continue
            
            # Enemy attack roll
            att = random.randint(1, 6) + random.randint(1, 6) + enemy.get("attack", 0)
            
            # Player Defense = 8 + Reflexes
            player_reflex = self.skill_system.get_skill("Reflexes")
            defense = 8 + (player_reflex.effective_level if player_reflex else 0)
            
            attack_msg = f"{enemy['name']} attacks! (Roll: {att} vs Defense: {defense})"
            self.log_message(attack_msg)
            messages.append(attack_msg)
            
            if att >= defense:
                hit_msg = "HIT! You take damage."
                self.log_message(hit_msg)
                messages.append(hit_msg)
                
                # Apply injury via injury_system if available
                if self.injury_system:
                    injury = self.injury_system.apply_injury(
                        "blunt_force_head" if random.random() < 0.2 else "bruised_ribs",
                        severity="minor"
                    )
                    injury_msg = f"Injury sustained: {injury.name}"
                    messages.append(injury_msg)
                else:
                    # Fallback to old system
                    self.apply_injury("blunt_force", "body", ["-1 Endurance"])
            else:
                miss_msg = "MISS! You deflect the blow."
                self.log_message(miss_msg)
                messages.append(miss_msg)
        
        self.round_counter += 1
        return messages

    def combat_check(self, skill: str, dc: int, target: str, type: str = "attack") -> dict:
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
            
        res = self.skill_system.roll_check(skill, dc)
        
        if sk_obj and penalties != 0:
            sk_obj.set_modifier("Injury", 0) # Clean up
            
        return {
            "success": res["success"],
            "total": res["total"],
            "difference": res["total"] - dc,
            "raw": res
        }

    def apply_injury(self, type: str, location: str, effects: List[str], persistent: bool = True):
        """Legacy injury application (kept for backwards compatibility)."""
        injury = {
            "type": type,
            "location": location,
            "effects": effects,
            "persistent": persistent,
            "healing_time": 72
        }
        self.player_state["injuries"].append(injury)
        self.log_message(f"INJURY RECEIVED: {type} ({location})")
    
    def _get_combat_skill(self) -> str:
        """Determine which combat skill to use based on equipped weapons."""
        if not self.inventory_system:
            return "Hand-to-Hand Combat"
        
        # Check for equipped firearms
        for item in self.inventory_system.carried_items:
            if item.equipped and item.type == "weapon":
                weapon_type = item.effects.get("weapon_type", "melee")
                if weapon_type == "firearm":
                    return "Firearms"
                elif weapon_type == "melee":
                    return "Hand-to-Hand Combat"
        
        return "Hand-to-Hand Combat"

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
