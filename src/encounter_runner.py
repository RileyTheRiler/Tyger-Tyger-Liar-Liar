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
        """Resolve the player's chosen action."""
        # This would use the DiceSystem for resolution
        # Simplified for now

        # Valid actions: ATTACK, HIDE, RUN, TALK, USE
        if action == "RUN":
            roll = self.skill_system.roll_check("Athletics", 10 + self.state.threat_level)
            if roll["success"]:
                 return {"message": "You scramble away into the darkness.", "end_encounter": True, "outcome": "escaped"}
            else:
                 return {"message": "You try to run, but the path twists back on itself."}

        if action == "HIDE":
            roll = self.skill_system.roll_check("Stealth", 10 + self.state.threat_level)
            if roll["success"]:
                self.state.threat_level = max(0, self.state.threat_level - 1)
                return {"message": "You stay low and quiet. The presence recedes slightly."}
            else:
                self.state.threat_level += 1
                return {"message": "You knock over something in the dark. It hears you."}

        return {"message": f"You try to {action}, but it has little effect."}

    def _resolve_entity_action(self) -> dict:
        """Determine what the entity does."""
        # Simple AI based on threat level
        if self.state.threat_level > 5:
            return {
                "message": "The entity LASHES OUT!",
                "damage_sanity": 10,
                "damage_reality": 5
            }
        elif self.state.threat_level > 2:
            return {
                "message": "The shadows deepen around you.",
                "damage_sanity": 5
            }
        else:
             return {
                "message": "It watches and waits.",
                "damage_sanity": 1
            }
