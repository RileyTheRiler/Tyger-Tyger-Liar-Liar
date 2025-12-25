import random
import json
import os
import copy
from typing import Dict, List, Optional, Any
from enum import Enum

class ActionType(Enum):
    STANDARD = "standard"
    TACTICAL = "tactical"
    ENVIRONMENTAL = "environmental"
    MENTAL = "mental"

class CombatManager:
    """
    Manages turn-based combat, chase scenes, and tense sequences.
    
    Attributes:
        skill_system: Reference to the mechanics.SkillSystem instance.
        player_state: Reference to the player's state dictionary.
        injury_system: Reference to InjurySystem.
        trauma_system: Reference to TraumaSystem.
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
        self.last_action_result: Optional[Dict] = None  # For skill chaining
        self.environment_features: Dict[str, Any] = {} # Lights, cover, hazards
        
        # Initialize injuries if not present (legacy support)
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
        if len(self.log) > 50:
            self.log.pop(0)

    def start_encounter(self, encounter_id: str = None, enemies: List[Dict] = None,
                       encounter_type: str = "combat", environment: Dict = None):
        """
        Starts a new encounter.
        
        Args:
            encounter_id: Template ID to load from encounter_templates
            enemies: List of enemy dicts (if not using template)
            encounter_type: "combat" or "chase"
            environment: Dict defining environment features (e.g. {"lighting": "dark", "cover": ["table"]})
        """
        if encounter_id and encounter_id in self.encounter_templates:
            template = self.encounter_templates[encounter_id]
            # Deep copy to avoid modifying template
            self.enemies = [copy.deepcopy(template)] if isinstance(template, dict) else copy.deepcopy(template)
        elif enemies:
            self.enemies = copy.deepcopy(enemies)
        else:
            raise ValueError("Must provide either encounter_id or enemies list")
        
        self.active = True
        self.round_counter = 1
        self.log = []
        self.environment_features = environment or {}
        self.last_action_result = None

        self.log_message(f"--- {encounter_type.upper()} STARTED ---")
        if self.environment_features:
            desc = ", ".join(f"{k}: {v}" for k, v in self.environment_features.items())
            self.log_message(f"Environment: {desc}")
        
        # Roll Initiative
        self._roll_initiative()
        
    def _roll_initiative(self):
        self.turn_order = []
        
        # Player Initiative - Reflexes check
        reflex_check = self.skill_system.roll_check("Reflexes", 0)
        player_init = reflex_check["total"]
        self.turn_order.append({
            "name": "Player",
            "is_player": True,
            "initiative": player_init
        })
        
        # Enemy Initiative
        for enemy in self.enemies:
            roll = random.randint(1, 6) + random.randint(1, 6)
            bonus = enemy.get("reflexes", 0)
            total = roll + bonus
            # Enemies with 'ambusher' trait get bonus
            if "ambusher" in enemy.get("traits", []):
                total += 2

            self.turn_order.append({
                "name": enemy.get("name", "Unknown Threat"),
                "is_player": False,
                "initiative": total,
                "data": enemy
            })
            
        self.turn_order.sort(key=lambda x: x["initiative"], reverse=True)
        
        self.log_message("Initiative Order:")
        for participant in self.turn_order:
            self.log_message(f"  {participant['name']} ({participant['initiative']})")

    def end_encounter(self):
        self.active = False
        self.enemies = []
        self.turn_order = []
        self.log_message("--- ENCOUNTER ENDED ---")

    def perform_action(self, action_type: str, target_name: str = None, description: str = "") -> Dict[str, Any]:
        """
        Executes a player action.
        Dispatches to specific handlers based on action category.
        """
        if not self.active:
            return {"success": False, "messages": ["No active encounter."]}

        # Normalize action string
        action_clean = action_type.lower()
        
        # Detect Action Category
        category = ActionType.STANDARD
        if action_clean in ["feint", "disarm", "shove", "flank", "trip"]:
            category = ActionType.TACTICAL
        elif action_clean in ["intimidate", "threaten", "plead", "distract", "reason", "talk"]:
            category = ActionType.MENTAL
        elif action_clean in ["interact", "use", "ignite", "collapse"]:
            category = ActionType.ENVIRONMENTAL

        # Dispatch
        if category == ActionType.STANDARD:
            result = self._handle_standard_action(action_clean, target_name)
        elif category == ActionType.TACTICAL:
            result = self._handle_tactical_action(action_clean, target_name)
        elif category == ActionType.MENTAL:
            result = self._handle_mental_action(action_clean, target_name)
        elif category == ActionType.ENVIRONMENTAL:
            result = self._handle_environmental_action(action_clean, target_name, description)
        else:
            result = {"success": False, "messages": [f"Unknown action: {action_type}"]}

        # Update Skill Chaining State
        if result.get("success"):
            self.last_action_result = {
                "action": action_clean,
                "skill": result.get("skill_used"),
                "margin": result.get("margin", 0)
            }
        else:
            self.last_action_result = None

        # Check Win Condition
        if not self.enemies and self.active:
            self.log_message("All enemies defeated.")
            result["messages"].append("Victory!")
            result["effects"] = result.get("effects", {})
            result["effects"]["victory"] = True
            self.end_encounter()
            return result
        
        # Process Enemy Turns (if player didn't escape/win)
        if self.active and not result.get("effects", {}).get("escaped") and not result.get("effects", {}).get("de_escalated"):
            enemy_results = self._process_enemy_turns()
            result["messages"].extend(enemy_results)

        return result

    def _handle_standard_action(self, action: str, target_name: str) -> Dict[str, Any]:
        result = {"action": action, "messages": [], "effects": {}, "success": False}
        
        target = self._get_enemy_by_name(target_name)
        if (action == "attack" or action == "fight") and not target:
             result["messages"].append("Target not found.")
             return result

        if action in ["attack", "fight"]:
            skill = self._get_combat_skill()
            
            # Chain Bonus?
            bonus = 0
            if self.last_action_result and self.last_action_result["action"] in ["feint", "distract"]:
                if self.last_action_result["margin"] >= 2:
                    bonus = 2
                    result["messages"].append("Capitalizing on their hesitation!")
            
            defense = target.get("reflexes", 0)
            dc = 8 + defense
            
            outcome = self.combat_check(skill, dc, target["name"], "attack", bonus=bonus)
            
            if outcome["success"]:
                result["success"] = True
                result["skill_used"] = skill
                result["margin"] = outcome["difference"]

                dmg = 1
                # Check weapon damage
                weapon_dmg = 0
                if self.inventory_system:
                    for item in self.inventory_system.carried_items:
                        if item.equipped and item.type == "weapon":
                             weapon_dmg = item.effects.get("damage_bonus", 0)

                total_dmg = dmg + weapon_dmg
                if outcome["difference"] >= 4:
                    total_dmg += 1
                    self.log_message("CRITICAL HIT!")
                
                target["hp"] = target.get("hp", 3) - total_dmg
                msg = f"Hit {target['name']} for {total_dmg} damage!"
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

        elif action == "dodge":
            dc = 10
            outcome = self.combat_check("Reflexes", dc, "Dodge", "defense")
            if outcome["success"]:
                result["success"] = True
                self.player_state["combat_dodging"] = True
                msg = "You weave and bob, ready to evade the next attack."
                self.log_message(msg)
                result["messages"].append(msg)
            else:
                msg = "You stumble and remain exposed."
                self.log_message(msg)
                result["messages"].append(msg)

        elif action in ["flee", "run"]:
            dc = 10 + (self.enemies[0].get("skills", {}).get("Athletics", 0) if self.enemies else 0)
            outcome = self.combat_check("Athletics", dc, "Escape", "move")
            if outcome["success"]:
                result["success"] = True
                msg = "You scramble away into the darkness!"
                self.log_message(msg)
                result["messages"].append(msg)
                result["effects"]["escaped"] = True
                self.end_encounter()
            else:
                msg = "You try to run, but they cut you off!"
                self.log_message(msg)
                result["messages"].append(msg)

        return result

    def _handle_tactical_action(self, action: str, target_name: str) -> Dict[str, Any]:
        result = {"action": action, "messages": [], "effects": {}, "success": False}
        target = self._get_enemy_by_name(target_name)
        
        if not target:
            result["messages"].append("No target specified.")
            return result

        if action == "feint":
            # Deception vs Logic/Instinct
            dc = 10 + target.get("logic", 0)
            outcome = self.combat_check("Deception", dc, target["name"], "tactical")

            if outcome["success"]:
                result["success"] = True
                result["skill_used"] = "Deception"
                result["margin"] = outcome["difference"]
                msg = f"You feint left, exposing {target['name']}'s guard."
                self.log_message(msg)
                result["messages"].append(msg)
                # Next attack gets bonus handled in _handle_standard_action via last_action_result
            else:
                msg = f"{target['name']} sees through your ploy."
                self.log_message(msg)
                result["messages"].append(msg)

        elif action == "shove":
            # Hand-to-Hand vs Constitution/Strength (simulated by Endurance)
            dc = 8 + target.get("endurance", 0)
            outcome = self.combat_check("Hand-to-Hand Combat", dc, target["name"], "tactical")

            if outcome["success"]:
                result["success"] = True
                result["skill_used"] = "Hand-to-Hand Combat"
                msg = f"You shove {target['name']} back, buying space."
                self.log_message(msg)
                result["messages"].append(msg)
                target["stunned"] = True # Simple status effect
            else:
                msg = f"You fail to move {target['name']}."
                self.log_message(msg)
                result["messages"].append(msg)

        return result

    def _handle_mental_action(self, action: str, target_name: str) -> Dict[str, Any]:
        result = {"action": action, "messages": [], "effects": {}, "success": False}
        target = self._get_enemy_by_name(target_name)

        if not target:
            target = self.enemies[0] if self.enemies else None

        if not target:
            result["messages"].append("No one to target.")
            return result

        skill = "Authority" # Default
        if action == "intimidate" or action == "threaten":
            skill = "Authority"
        elif action == "plead" or action == "reason":
            skill = "Empathy"
        elif action == "distract":
            skill = "Wits"

        dc = 12 # Default hard
        if target.get("psychology", "") == "weak_willed":
            dc = 8
        elif target.get("psychology", "") == "fanatic":
            dc = 15

        outcome = self.combat_check(skill, dc, target["name"], "mental")

        if outcome["success"]:
            result["success"] = True
            result["skill_used"] = skill
            result["margin"] = outcome["difference"]

            if action == "distract":
                msg = f"You successfully distract {target['name']}!"
                self.log_message(msg)
                result["messages"].append(msg)
            else:
                msg = f"Your words land. {target['name']} hesitates."
                self.log_message(msg)
                result["messages"].append(msg)
                result["effects"]["de_escalated"] = True
                if outcome["difference"] > 3:
                     # Complete morale break
                     msg = f"{target['name']} backs down completely."
                     self.log_message(msg)
                     result["messages"].append(msg)
                     self.enemies.remove(target) # Effectively defeated
        else:
            msg = f"{target['name']} ignores you."
            self.log_message(msg)
            result["messages"].append(msg)
            
        return result

    def _handle_environmental_action(self, action: str, target_name: str, description: str) -> Dict[str, Any]:
        result = {"action": action, "messages": [], "effects": {}, "success": False}

        # This requires contextual objects in environment_features
        # For now, we simulate generic interaction

        if action == "turn off lights" or (action == "interact" and "light" in description):
            if self.environment_features.get("lighting") == "dim":
                 self.environment_features["lighting"] = "dark"
                 msg = "You smash the light. Darkness floods the room."
                 self.log_message(msg)
                 result["messages"].append(msg)
                 result["success"] = True
                 # Effect: +2 Stealth, -2 Firearms
        else:
             # Generic improvisation
             skill = "Logic"
             dc = 10
             outcome = self.combat_check(skill, dc, "Environment", "environmental")
             if outcome["success"]:
                 result["success"] = True
                 msg = f"You use the environment to your advantage ({description or 'improvise'})."
                 self.log_message(msg)
                 result["messages"].append(msg)
             else:
                 msg = "You can't find an advantage here."
                 self.log_message(msg)
                 result["messages"].append(msg)

        return result

    def _process_enemy_turns(self) -> List[str]:
        """Process all enemy turns and return messages, handling player reactions."""
        messages = []
        
        for enemy in self.enemies:
            if not self.active:
                break
            
            # Skip if stunned
            if enemy.get("stunned"):
                msg = f"{enemy['name']} shakes off the stun."
                self.log_message(msg)
                messages.append(msg)
                enemy["stunned"] = False
                continue

            # 1. Determine Attack
            att_roll = random.randint(1, 6) + random.randint(1, 6) + enemy.get("attack", 0)
            
            # 2. Player Reaction Opportunity (Passive)
            # Check reflexes/instinct to auto-defend or interrupt
            reaction_success = False
            reaction_msg = ""
            
            player_reflex = self.skill_system.get_skill("Reflexes")
            reflex_val = player_reflex.effective_level if player_reflex else 0

            # If player explicitly dodged, they get bonus, but here we check for PASSIVE interrupt
            # e.g. "Instinct" warns you of a feint, or "Reflexes" allows a parry
            
            if att_roll > 10: # Strong attack coming
                # Check Instinct
                instinct_check = self.skill_system.roll_check("Instinct", 10, "reaction")
                if instinct_check["success"]:
                    reaction_msg = "Your instinct screams 'MOVE'!"
                    # Grant bonus to defense
                    reflex_val += 2

            # 3. Calculate Defense
            # Base 8 + Reflexes
            defense = 8 + reflex_val
            if self.player_state.get("combat_dodging"):
                defense += 2
                self.player_state["combat_dodging"] = False # Consumed

            # Environment modifiers
            if self.environment_features.get("lighting") == "dark":
                # Harder to hit
                att_roll -= 2

            attack_msg = f"{enemy['name']} attacks! (Roll: {att_roll} vs Defense: {defense})"
            if reaction_msg:
                messages.append(reaction_msg)
            self.log_message(attack_msg)
            messages.append(attack_msg)
            
            if att_roll >= defense:
                # HIT
                hit_msg = "HIT! You take damage."
                self.log_message(hit_msg)
                messages.append(hit_msg)
                
                # Apply Injury
                self._apply_damage(enemy)

            else:
                miss_msg = "MISS! You evade the blow."
                self.log_message(miss_msg)
                messages.append(miss_msg)
        
        self.round_counter += 1
        return messages

    def _apply_damage(self, enemy_source: Dict):
        """Calculates and applies injury."""
        # Determine injury based on enemy type or random
        severity = "minor"
        location = random.choice(["arm", "leg", "torso", "head"])

        # Bosses or high rolls deal more damage
        if enemy_source.get("damage_tier") == "high":
            severity = "moderate"

        if self.injury_system:
            injury = self.injury_system.apply_injury(
                f"{enemy_source.get('attack_type', 'blunt')}_{location}",
                location=location,
                severity=severity
            )
            self.log_message(f"INJURY: {injury.name}")

            # Check for Trauma Trigger (Pain/Violence)
            if self.trauma_system and severity in ["moderate", "severe"]:
                 self.trauma_system.check_trauma_trigger("personal_torture", self.skill_system, self.player_state)

        else:
            # Fallback
            self.player_state["injuries"].append({"type": "generic", "severity": severity})

    def combat_check(self, skill: str, dc: int, target: str, type: str = "attack", bonus: int = 0) -> dict:
        """
        Executes a combat check.
        """
        penalties = self._get_total_injury_penalty(skill)
        
        sk_obj = self.skill_system.get_skill(skill)
        if sk_obj:
            if penalties != 0:
                sk_obj.set_modifier("Injury", penalties)
            if bonus != 0:
                sk_obj.set_modifier("CombatBonus", bonus)
            
        res = self.skill_system.roll_check(skill, dc, check_id=f"combat_{self.round_counter}_{random.randint(0,100)}")
        
        if sk_obj:
            if penalties != 0:
                sk_obj.set_modifier("Injury", 0)
            if bonus != 0:
                sk_obj.set_modifier("CombatBonus", 0)
            
        return {
            "success": res["success"],
            "total": res["total"],
            "difference": res["total"] - dc,
            "raw": res
        }

    def _get_combat_skill(self) -> str:
        """Determine which combat skill to use based on equipped weapons."""
        if not self.inventory_system:
            return "Hand-to-Hand Combat"
        
        try:
            for item in self.inventory_system.carried_items:
                if item.equipped and item.type == "weapon":
                    weapon_type = item.effects.get("weapon_type", "melee")
                    if weapon_type == "firearm":
                        return "Firearms"
                    elif weapon_type == "melee":
                        return "Hand-to-Hand Combat"
        except AttributeError:
             # Safety fallback if inventory_system is mocked or incomplete
             return "Hand-to-Hand Combat"
        
        return "Hand-to-Hand Combat"

    def _get_enemy_by_name(self, name):
        if not name:
             return self.enemies[0] if self.enemies else None

        name_lower = name.lower()
        # Exact match first
        for e in self.enemies:
            if e["name"].lower() == name_lower:
                return e

        # Then startswith
        for e in self.enemies:
            if e["name"].lower().startswith(name_lower):
                return e

        # Then fuzzy 'in' (fallback)
        for e in self.enemies:
            if name_lower in e["name"].lower():
                return e
        return None

    def _get_total_injury_penalty(self, skill_name: str) -> int:
        if self.injury_system:
            return self.injury_system.get_penalty_for_skill(skill_name)

        total_penalty = 0
        for injury in self.player_state.get("injuries", []):
            if isinstance(injury, dict) and "effects" in injury:
                # Legacy parsing
                pass
        return total_penalty
