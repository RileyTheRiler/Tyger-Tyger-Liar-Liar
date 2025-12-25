"""
Encounter Runner - Turn-based interaction engine for Entity encounters.
"""

import random
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

@dataclass
class EncounterState:
    threat_level: int
    player_initiative: bool
    environment_status: Dict[str, str]
    turn_count: int
    history: List[str]

class EncounterRunner:
    def __init__(self, player_state: dict, skill_system, dice_system):
        self.player_state = player_state
        self.skill_system = skill_system
        self.dice_system = dice_system
        self.active_encounter = None
        self.state: Optional[EncounterState] = None

    def load_encounter(self, encounter_data: dict):
        """Initialize a new encounter."""
        self.active_encounter = encounter_data
        self.state = EncounterState(
            threat_level=encounter_data.get("initial_threat", 1),
            player_initiative=self._check_initiative(encounter_data),
            environment_status={},
            turn_count=0,
            history=[]
        )
        print(f"\n*** ENCOUNTER STARTED: {encounter_data['name']} ***")
        print(f"{encounter_data['description']}")

    def _check_initiative(self, data: dict) -> bool:
        """Determine starting initiative."""
        base_init = data.get("initiative_score", 10)
        # Roll reflex/instinct
        skill_total = self.skill_system.get_skill_total("Reflexes")
        roll = random.randint(1, 10) + skill_total
        return roll >= base_init

    def process_turn(self, action: str, target: str = None) -> dict:
        """Process a single turn in the encounter."""
        if not self.active_encounter:
            return {"status": "error", "message": "No active encounter"}

        self.state.turn_count += 1
        response = {"status": "continue", "messages": []}

        # 1. Player Action
        result = self._resolve_player_action(action, target)
        response["messages"].append(result["message"])

        if result.get("end_encounter"):
            response["status"] = "ended"
            response["result"] = result["outcome"]
            return response

        # 2. Entity Reaction (if not defeated/escaped)
        entity_action = self._resolve_entity_action()
        response["messages"].append(entity_action["message"])

        if entity_action.get("damage_sanity"):
            self.player_state["sanity"] -= entity_action["damage_sanity"]
            response["messages"].append(f"[SANITY -{entity_action['damage_sanity']}]")

        if entity_action.get("damage_reality"):
            self.player_state["reality"] -= entity_action["damage_reality"]
            response["messages"].append(f"[REALITY -{entity_action['damage_reality']}]")

        # Check Failure States
        if self.player_state["sanity"] <= 0 or self.player_state["reality"] <= 0:
            response["status"] = "ended"
            response["result"] = "collapse"
            response["messages"].append("You cannot withstand the encounter any longer.")

        return response

    def _resolve_player_action(self, action: str, target: str) -> dict:
        """Resolve the player's chosen action using data definition."""
        actions_def = self.active_encounter.get("actions", {})

        if action not in actions_def:
             # Fallback for undefined actions
             return {"message": f"You try to {action}, but it seems ineffective here."}

        act_def = actions_def[action]
        skill = act_def.get("skill", "Composure")
        base_dc = act_def.get("difficulty", 10)

        # Roll using DiceSystem indirectly via SkillSystem wrapper
        # The DiceSystem is passed in but SkillSystem handles checks usually.
        # But we want to use the unified DiceSystem ideally.
        # Let's assume SkillSystem.roll_check uses DiceSystem internally or mimics it.
        # Current SkillSystem.roll_check returns dict with 'success' and 'total'.

        result = self.skill_system.roll_check(skill, base_dc)

        if result["success"]:
            eff = act_def.get("success_effect", {})
            msg = eff.get("message", "Success.")

            # Apply effects
            if "threat_damage" in eff:
                self.state.threat_level = max(0, self.state.threat_level - eff["threat_damage"])
            if "threat_reduction" in eff:
                 self.state.threat_level = max(0, self.state.threat_level - eff["threat_reduction"])

            if eff.get("escape"):
                return {"message": msg, "end_encounter": True, "outcome": "escaped"}

            # Check if threat eliminated (for ATTACK)
            if self.state.threat_level <= 0 and action == "ATTACK":
                 return {"message": msg + " The entity dissolves.", "end_encounter": True, "outcome": "victory"}

            return {"message": msg}
        else:
            eff = act_def.get("fail_effect", {})
            msg = eff.get("message", "Failure.")

            if "threat_increase" in eff:
                self.state.threat_level += eff["threat_increase"]

            # Damage handled here or in entity reaction?
            # Let's apply immediate fail damage
            if "sanity_damage" in eff:
                self.player_state["sanity"] -= eff["sanity_damage"]
                msg += f" [SANITY -{eff['sanity_damage']}]"

            return {"message": msg}

    def _resolve_entity_action(self) -> dict:
        """Determine what the entity does."""
        moves = self.active_encounter.get("entity_moves", [])

        # Find move with highest threshold <= current threat
        selected_move = None
        for move in sorted(moves, key=lambda x: x["threshold"], reverse=True):
            if self.state.threat_level >= move["threshold"]:
                selected_move = move
                break

        if not selected_move:
             return {"message": "The entity watches."}

        effects = selected_move.get("effects", {})
        return {
            "message": selected_move.get("message", "The entity acts."),
            "damage_sanity": abs(effects.get("sanity", 0)), # Ensure positive value for damage
            "damage_reality": abs(effects.get("reality", 0))
        }
