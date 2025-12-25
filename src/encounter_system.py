"""
Encounter System - Turn-based tactical textual encounters.
Per Canon & Constraints: "Misses alter environment, building tension without dead ends."

Handles:
- Turn structure (player -> threat -> environment)
- Environment state tracking
- Threat AI behavior
- Skill checks with partial success
- Exit conditions and defeat states
"""

import json
import os
import copy
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum


class TurnPhase(Enum):
    PLAYER = "player"
    THREAT = "threat"
    ENVIRONMENT = "environment"
    NPC = "npc"


class ExitType(Enum):
    VICTORY = "victory"
    ESCAPE = "escape"
    DEFEAT = "defeat"
    DRAW = "draw"


class ThreatDistance(Enum):
    FAR = "far"
    MEDIUM = "medium"
    CLOSE = "close"
    ADJACENT = "adjacent"


class ThreatAwareness(Enum):
    UNAWARE = "unaware"
    ALERTED = "alerted"
    SEARCHING = "searching"
    HUNTING = "hunting"
    ENGAGED = "engaged"


@dataclass
class EncounterOption:
    """A player action available during an encounter."""
    id: str
    label: str
    description: str
    skill: str
    dc: int
    available_when: Dict[str, Any] = field(default_factory=dict)
    costs: Dict[str, Any] = field(default_factory=dict)
    outcomes: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_dict(data: dict) -> 'EncounterOption':
        return EncounterOption(
            id=data["id"],
            label=data["label"],
            description=data.get("description", ""),
            skill=data["skill"],
            dc=data["dc"],
            available_when=data.get("available_when", {}),
            costs=data.get("costs", {}),
            outcomes=data.get("outcomes", {})
        )


@dataclass
class EncounterState:
    """Current state of an active encounter."""
    turn: int = 0
    environment: Dict[str, Any] = field(default_factory=dict)
    player_resources: Dict[str, Any] = field(default_factory=dict)
    threat_state: Dict[str, Any] = field(default_factory=dict)
    npc_state: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    custom_flags: Dict[str, Any] = field(default_factory=dict)
    player_escaped: bool = False
    threat_defeated: bool = False
    active: bool = True
    last_action_text: str = ""

    def get_flat_state(self) -> Dict[str, Any]:
        """Get flattened state for condition checking."""
        flat = {
            "turn": self.turn,
            "player_escaped": self.player_escaped,
            "threat_defeated": self.threat_defeated,
            **self.environment,
            **self.player_resources,
            **{f"threat_{k}": v for k, v in self.threat_state.items()},
            **self.custom_flags
        }
        # Flatten NPC state
        for npc_id, npc_data in self.npc_state.items():
            for key, value in npc_data.items():
                flat[f"{npc_id}_{key}"] = value
        return flat


class Encounter:
    """Definition of an encounter from data."""

    def __init__(self, data: dict):
        self.id = data["id"]
        self.intro_text = data["intro_text"]
        self.initial_state = data.get("initial_state", {})
        self.turn_structure = data.get("turn_structure", {
            "order": ["player", "threat", "environment"],
            "max_turns": 20
        })

        self.options: List[EncounterOption] = [
            EncounterOption.from_dict(opt) for opt in data.get("options", [])
        ]

        self.threat_behavior = data.get("threat_behavior", [])
        self.environment_tick = data.get("environment_tick", {})
        self.exit_conditions = data.get("exit_conditions", [])
        self.defeat_condition = data.get("defeat_condition", {})

    def get_intro_text(self, lens: str = "neutral") -> str:
        """Get intro text for the given lens."""
        if isinstance(self.intro_text, dict):
            if lens in self.intro_text.get("lens", {}):
                return self.intro_text["lens"][lens]
            return self.intro_text.get("base", "")
        return str(self.intro_text)


class EncounterRunner:
    """
    Runs a single encounter, managing state and turn flow.
    """

    def __init__(self, encounter: Encounter, dice_system, skill_system,
                 condition_system=None, attention_system=None,
                 npc_system=None, player_state: dict = None):
        self.encounter = encounter
        self.dice_system = dice_system
        self.skill_system = skill_system
        self.condition_system = condition_system
        self.attention_system = attention_system
        self.npc_system = npc_system
        self.player_state = player_state or {}

        # Initialize state from encounter definition
        self.state = EncounterState()
        self._initialize_state()

        # Result tracking
        self.result: Optional[Dict[str, Any]] = None
        self.log: List[str] = []

    def _initialize_state(self):
        """Set up initial encounter state."""
        init = self.encounter.initial_state
        self.state.environment = copy.deepcopy(init.get("environment", {}))
        self.state.player_resources = copy.deepcopy(init.get("player_resources", {}))
        self.state.threat_state = copy.deepcopy(init.get("threat_state", {}))
        self.state.npc_state = copy.deepcopy(init.get("npc_state", {}))
        self.state.custom_flags = copy.deepcopy(init.get("custom_flags", {}))
        self.state.turn = 0
        self.state.active = True

    def get_intro(self, lens: str = "neutral") -> str:
        """Get the encounter introduction text."""
        return self.encounter.get_intro_text(lens)

    def get_available_options(self) -> List[EncounterOption]:
        """Get options currently available to the player."""
        available = []
        flat_state = self.state.get_flat_state()

        for option in self.encounter.options:
            if self._check_availability(option, flat_state):
                available.append(option)

        return available

    def _check_availability(self, option: EncounterOption, flat_state: dict) -> bool:
        """Check if an option is currently available."""
        conditions = option.available_when
        if not conditions:
            return True

        # Check state flags
        state_flags = conditions.get("state_flags", {})
        for flag, required_value in state_flags.items():
            actual = flat_state.get(flag)
            if isinstance(required_value, bool):
                if bool(actual) != required_value:
                    return False
            elif isinstance(required_value, int):
                # For numeric comparisons, check >= for minimums
                if actual is None or actual < required_value:
                    return False
            elif actual != required_value:
                return False

        # Check item requirement
        has_item = conditions.get("has_item")
        if has_item:
            special_items = flat_state.get("special_items", [])
            if has_item not in special_items:
                return False

        # Check turn requirements
        turn_gte = conditions.get("turn_gte")
        if turn_gte is not None and self.state.turn < turn_gte:
            return False

        turn_lte = conditions.get("turn_lte")
        if turn_lte is not None and self.state.turn > turn_lte:
            return False

        return True

    def _pay_costs(self, option: EncounterOption) -> Tuple[bool, str]:
        """Pay the costs for an option. Returns (success, message)."""
        costs = option.costs
        messages = []

        # Ammo cost
        ammo_cost = costs.get("ammo", 0)
        if ammo_cost > 0:
            current_ammo = self.state.player_resources.get("ammo", 0)
            if current_ammo < ammo_cost:
                return False, "Not enough ammunition."
            self.state.player_resources["ammo"] = current_ammo - ammo_cost
            messages.append(f"Spent {ammo_cost} ammo.")

        # Item cost
        item_cost = costs.get("item")
        if item_cost:
            special_items = self.state.player_resources.get("special_items", [])
            if item_cost not in special_items:
                return False, f"You don't have {item_cost}."
            special_items.remove(item_cost)
            messages.append(f"Used {item_cost}.")

        # Time cost (noted but handled elsewhere)
        time_cost = costs.get("time", 0)
        if time_cost > 0:
            messages.append(f"This takes {time_cost} minutes.")

        return True, " ".join(messages) if messages else ""

    def execute_option(self, option_id: str, manual_roll: int = None) -> Dict[str, Any]:
        """
        Execute a player option and resolve its outcome.

        Returns dict with:
            - success: bool
            - result_type: "success", "failure", "partial"
            - text: narrative text
            - roll_result: dice roll details
            - effects: list of effects applied
            - ends_encounter: bool
            - next_scene: optional scene to transition to
        """
        # Find the option
        option = None
        for opt in self.encounter.options:
            if opt.id == option_id:
                option = opt
                break

        if not option:
            return {"success": False, "text": "Invalid action.", "effects": []}

        # Check availability
        if option not in self.get_available_options():
            return {"success": False, "text": "That action is not available.", "effects": []}

        # Pay costs
        can_pay, cost_msg = self._pay_costs(option)
        if not can_pay:
            return {"success": False, "text": cost_msg, "effects": []}

        # Get skill modifier
        skill = self.skill_system.skills.get(option.skill)
        modifier = skill.effective_level if skill else 0

        # Apply condition penalties
        if self.condition_system:
            penalty = self.condition_system.get_skill_modifier(option.skill)
            modifier += penalty

        # Resolve the check
        roll_result = self.dice_system.resolve_check(
            skill_name=option.skill,
            modifier=modifier,
            dc=option.dc,
            manual_roll=manual_roll,
            allow_partial=True
        )

        # Determine outcome type
        from src.dice import CheckResult
        if roll_result.result in [CheckResult.CRITICAL_SUCCESS, CheckResult.SUCCESS]:
            outcome_key = "success"
        elif roll_result.result == CheckResult.PARTIAL_SUCCESS:
            outcome_key = "partial" if "partial" in option.outcomes else "success"
        else:
            outcome_key = "failure"

        outcome = option.outcomes.get(outcome_key, {})

        # Build result
        result = {
            "success": outcome_key != "failure",
            "result_type": outcome_key,
            "text": outcome.get("text", ""),
            "roll_result": roll_result,
            "effects": [],
            "ends_encounter": outcome.get("ends_encounter", False),
            "next_scene": outcome.get("next_scene")
        }

        # Add cost message if any
        if cost_msg:
            result["text"] = cost_msg + " " + result["text"]

        # Apply state changes
        state_changes = outcome.get("state_changes", {})
        self._apply_state_changes(state_changes)

        # Apply effects
        effects = outcome.get("effects", [])
        for effect in effects:
            effect_result = self._apply_effect(effect)
            result["effects"].append(effect_result)

        # Log the action
        self.log.append(f"Turn {self.state.turn}: {option.label} -> {outcome_key}")
        self.state.last_action_text = result["text"]

        # Check for encounter end
        if result["ends_encounter"]:
            self.state.active = False
            if outcome_key == "success" and "escape" in option.id.lower():
                self.state.player_escaped = True

        return result

    def _apply_state_changes(self, changes: Dict[str, Any]):
        """Apply state changes from an outcome."""
        for key, value in changes.items():
            # Handle special prefixed keys
            if key.startswith("threat_"):
                threat_key = key[7:]  # Remove "threat_" prefix
                if isinstance(value, int) and threat_key in self.state.threat_state:
                    # Numeric modification
                    self.state.threat_state[threat_key] += value
                else:
                    self.state.threat_state[threat_key] = value

            elif key.startswith("npc_"):
                # Parse npc_<id>_<field>
                parts = key[4:].rsplit("_", 1)
                if len(parts) == 2:
                    npc_id, npc_field = parts
                    if npc_id not in self.state.npc_state:
                        self.state.npc_state[npc_id] = {}
                    self.state.npc_state[npc_id][npc_field] = value

            elif key in self.state.environment:
                self.state.environment[key] = value

            elif key in self.state.player_resources:
                if isinstance(value, int):
                    self.state.player_resources[key] += value
                else:
                    self.state.player_resources[key] = value

            else:
                # Custom flag
                self.state.custom_flags[key] = value

    def _apply_effect(self, effect: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a single effect and return result."""
        effect_type = effect.get("type")
        result = {"type": effect_type, "applied": True}

        if effect_type == "add_condition":
            target = effect.get("target")
            if self.condition_system and target:
                self.condition_system.add_condition(target)
                result["condition"] = target

        elif effect_type == "modify_attention":
            value = effect.get("value", 0)
            if self.attention_system:
                self.attention_system.modify_attention(value)
                result["attention_change"] = value

        elif effect_type == "modify_sanity":
            value = effect.get("value", 0)
            if self.player_state:
                self.player_state["sanity"] = max(0, self.player_state.get("sanity", 100) + value)
                result["sanity_change"] = value

        elif effect_type == "modify_reality":
            value = effect.get("value", 0)
            if self.player_state:
                self.player_state["reality"] = max(0, self.player_state.get("reality", 100) + value)
                result["reality_change"] = value

        elif effect_type == "modify_trust":
            target = effect.get("target")
            value = effect.get("value", 0)
            if self.npc_system and target:
                self.npc_system.modify_trust(target, value)
                result["trust_target"] = target
                result["trust_change"] = value

        elif effect_type == "set_flag":
            target = effect.get("target")
            value = effect.get("value", True)
            if self.player_state and target:
                if "event_flags" not in self.player_state:
                    self.player_state["event_flags"] = set()
                flags = self.player_state["event_flags"]
                if isinstance(flags, set):
                    if value:
                        flags.add(target)
                    else:
                        flags.discard(target)
                result["flag"] = target

        elif effect_type == "skill_penalty":
            skill = effect.get("skill")
            value = effect.get("value", 0)
            if self.skill_system and skill:
                skill_obj = self.skill_system.skills.get(skill)
                if skill_obj:
                    skill_obj.set_modifier("encounter", value)
                result["skill"] = skill
                result["penalty"] = value

        return result

    def process_threat_turn(self) -> Optional[Dict[str, Any]]:
        """
        Process the threat's turn based on behavior rules.
        Returns action taken or None if no applicable behavior.
        """
        flat_state = self.state.get_flat_state()
        threat_state = self.state.threat_state

        for behavior in self.encounter.threat_behavior:
            condition = behavior.get("condition", {})

            # Check if condition matches
            matches = True
            for key, required in condition.items():
                if key == "state_flags":
                    for flag_key, flag_val in required.items():
                        if flat_state.get(flag_key) != flag_val:
                            matches = False
                            break
                elif key == "threat_health" and isinstance(required, int):
                    # Health threshold check
                    health = threat_state.get("health", 100)
                    if health > required:
                        matches = False
                else:
                    actual = threat_state.get(key)
                    if actual != required:
                        matches = False

            if not matches:
                continue

            # Execute this behavior
            action = behavior.get("action", {})
            result = {
                "text": action.get("text", "The threat acts."),
                "effects": []
            }

            # Apply state changes
            state_changes = action.get("state_changes", {})
            self._apply_state_changes(state_changes)

            # Apply player effects
            player_effects = action.get("player_effects", [])
            for effect in player_effects:
                effect_result = self._apply_effect(effect)
                result["effects"].append(effect_result)

            # Check for threat ending encounter
            if action.get("ends_encounter"):
                self.state.active = False
                result["ends_encounter"] = True
                result["next_scene"] = action.get("next_scene")

            self.log.append(f"Turn {self.state.turn} (Threat): {result['text'][:50]}...")
            return result

        return None

    def process_environment_turn(self) -> List[Dict[str, Any]]:
        """
        Process environmental effects for the current turn.
        Returns list of effects that occurred.
        """
        results = []
        tick = self.encounter.environment_tick

        # Cold exposure
        cold = tick.get("cold_exposure", {})
        if cold:
            condition = cold.get("condition", {})
            # Check condition (e.g., window_intact: false)
            matches = True
            for key, required in condition.items():
                actual = self.state.environment.get(key)
                if actual != required:
                    matches = False
                    break

            if matches:
                effect = cold.get("effect", {})
                result = {
                    "type": "cold_exposure",
                    "text": effect.get("text", "The cold intensifies."),
                    "effects": []
                }
                for eff in effect.get("effects", []):
                    effect_result = self._apply_effect(eff)
                    result["effects"].append(effect_result)
                results.append(result)

        # Visibility/scripted changes
        vis_changes = tick.get("visibility_changes", [])
        for change in vis_changes:
            if change.get("turn") == self.state.turn:
                effect = change.get("effect", {})
                result = {
                    "type": "visibility_change",
                    "text": effect.get("text", "The environment shifts."),
                    "effects": []
                }
                state_changes = effect.get("state_changes", {})
                self._apply_state_changes(state_changes)
                results.append(result)

        # Per-turn attention gain
        attention_gain = tick.get("attention_gain", 0)
        if attention_gain > 0 and self.attention_system:
            self.attention_system.modify_attention(attention_gain)
            results.append({
                "type": "attention_tick",
                "text": f"Tension builds. (+{attention_gain} Attention)",
                "effects": [{"type": "modify_attention", "value": attention_gain}]
            })

        return results

    def check_exit_conditions(self) -> Optional[Dict[str, Any]]:
        """
        Check if any exit condition is met.
        Returns exit result or None.
        """
        flat_state = self.state.get_flat_state()

        for exit_cond in self.encounter.exit_conditions:
            condition = exit_cond.get("condition", {})

            # Check each condition type
            matches = True

            # Turns survived
            turns_required = condition.get("turns_survived")
            if turns_required is not None and self.state.turn < turns_required:
                matches = False

            # Threat distance
            threat_dist = condition.get("threat_distance")
            if threat_dist is not None:
                actual = self.state.threat_state.get("distance")
                if actual != threat_dist:
                    matches = False

            # State flag check
            state_flag = condition.get("state_flag", {})
            for flag_key, flag_val in state_flag.items():
                if flat_state.get(flag_key) != flag_val:
                    matches = False
                    break

            # Player escaped
            if condition.get("player_escaped") and not self.state.player_escaped:
                matches = False

            # Threat defeated
            if condition.get("threat_defeated") and not self.state.threat_defeated:
                matches = False

            # Threat health check
            if "threat_health" in condition:
                required_health = condition["threat_health"]
                actual_health = self.state.threat_state.get("health", 100)
                if actual_health > required_health:
                    matches = False

            # NPC protected check
            npc_protected = condition.get("npc_protected")
            if npc_protected:
                npc_status = self.state.npc_state.get(npc_protected, {}).get("status")
                if npc_status in ["injured", "dead", "missing"]:
                    matches = False

            if matches:
                result = exit_cond.get("result", {})
                exit_result = {
                    "id": exit_cond.get("id"),
                    "type": ExitType(result.get("type", "draw")),
                    "text": result.get("text", "The encounter ends."),
                    "next_scene": result.get("next_scene"),
                    "effects": []
                }

                # Apply exit effects
                for effect in result.get("effects", []):
                    effect_result = self._apply_effect(effect)
                    exit_result["effects"].append(effect_result)

                self.result = exit_result
                self.state.active = False
                return exit_result

        return None

    def check_defeat_condition(self) -> Optional[Dict[str, Any]]:
        """
        Check if defeat condition is met.
        Returns defeat result or None.
        """
        defeat = self.encounter.defeat_condition
        if not defeat:
            return None

        condition = defeat.get("condition", {})
        flat_state = self.state.get_flat_state()

        # Check player health
        if "player_health" in condition:
            # We don't track player health directly; check via sanity
            player_health = self.player_state.get("sanity", 100)
            if player_health > condition["player_health"]:
                return None

        # Check state flags
        for key, required in condition.items():
            if key == "player_health":
                continue
            if flat_state.get(key) != required:
                return None

        # Defeat condition met
        result = defeat.get("result", {})
        defeat_result = {
            "type": ExitType.DEFEAT,
            "text": result.get("text", "You fall."),
            "next_scene": result.get("next_scene"),
            "game_over": result.get("game_over", False),
            "effects": []
        }

        for effect in result.get("effects", []):
            effect_result = self._apply_effect(effect)
            defeat_result["effects"].append(effect_result)

        self.result = defeat_result
        self.state.active = False
        return defeat_result

    def advance_turn(self) -> Dict[str, Any]:
        """
        Advance to the next turn and process threat + environment.
        Call this after the player acts.

        Returns summary of what happened.
        """
        self.state.turn += 1

        turn_result = {
            "turn": self.state.turn,
            "threat_action": None,
            "environment_effects": [],
            "exit_result": None,
            "defeat_result": None
        }

        # Check turn order
        order = self.encounter.turn_structure.get("order", ["player", "threat", "environment"])

        for phase in order:
            if phase == "player":
                continue  # Player already acted

            if phase == "threat":
                turn_result["threat_action"] = self.process_threat_turn()
                if not self.state.active:
                    break

            if phase == "environment":
                turn_result["environment_effects"] = self.process_environment_turn()

            if phase == "npc":
                # NPC behavior could be added here
                pass

        # Check exit conditions
        if self.state.active:
            turn_result["exit_result"] = self.check_exit_conditions()

        # Check defeat
        if self.state.active:
            turn_result["defeat_result"] = self.check_defeat_condition()

        # Check max turns
        max_turns = self.encounter.turn_structure.get("max_turns", 20)
        if self.state.active and self.state.turn >= max_turns:
            # Force end via survival
            for exit_cond in self.encounter.exit_conditions:
                if exit_cond.get("condition", {}).get("turns_survived") == max_turns:
                    turn_result["exit_result"] = {
                        "id": exit_cond.get("id"),
                        "type": ExitType.DRAW,
                        "text": exit_cond.get("result", {}).get("text", "You endure."),
                        "next_scene": exit_cond.get("result", {}).get("next_scene")
                    }
                    self.result = turn_result["exit_result"]
                    self.state.active = False
                    break

        return turn_result

    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of current encounter state for display."""
        return {
            "turn": self.state.turn,
            "active": self.state.active,
            "environment": self.state.environment,
            "threat": self.state.threat_state,
            "resources": self.state.player_resources,
            "last_action": self.state.last_action_text
        }

    def to_dict(self) -> dict:
        """Serialize encounter state for saving."""
        return {
            "encounter_id": self.encounter.id,
            "turn": self.state.turn,
            "environment": self.state.environment,
            "player_resources": self.state.player_resources,
            "threat_state": self.state.threat_state,
            "npc_state": self.state.npc_state,
            "custom_flags": self.state.custom_flags,
            "player_escaped": self.state.player_escaped,
            "threat_defeated": self.state.threat_defeated,
            "active": self.state.active,
            "log": self.log
        }


class EncounterSystem:
    """
    Manages encounter definitions and running encounters.
    """

    def __init__(self, encounters_dir: str = None):
        self.encounters: Dict[str, Encounter] = {}
        self.current_runner: Optional[EncounterRunner] = None

        if encounters_dir:
            self.load_encounters(encounters_dir)

    def load_encounters(self, encounters_dir: str):
        """Load encounter definitions from JSON files."""
        if not os.path.exists(encounters_dir):
            print(f"[ENCOUNTER] Directory not found: {encounters_dir}")
            return

        for filename in os.listdir(encounters_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(encounters_dir, filename), 'r') as f:
                        data = json.load(f)

                    # Handle single encounter or list
                    encounters = data if isinstance(data, list) else [data]
                    for enc_data in encounters:
                        enc = Encounter(enc_data)
                        self.encounters[enc.id] = enc
                        print(f"[ENCOUNTER] Loaded: {enc.id}")

                except Exception as e:
                    print(f"[ERROR] Loading encounter from {filename}: {e}")

    def get_encounter(self, encounter_id: str) -> Optional[Encounter]:
        """Get an encounter definition by ID."""
        return self.encounters.get(encounter_id)

    def start_encounter(self, encounter_id: str, dice_system, skill_system,
                        condition_system=None, attention_system=None,
                        npc_system=None, player_state: dict = None) -> Optional[EncounterRunner]:
        """
        Start an encounter and return the runner.
        """
        encounter = self.get_encounter(encounter_id)
        if not encounter:
            print(f"[ENCOUNTER] Unknown encounter: {encounter_id}")
            return None

        self.current_runner = EncounterRunner(
            encounter=encounter,
            dice_system=dice_system,
            skill_system=skill_system,
            condition_system=condition_system,
            attention_system=attention_system,
            npc_system=npc_system,
            player_state=player_state
        )

        print(f"[ENCOUNTER] Started: {encounter_id}")
        return self.current_runner

    def get_current_runner(self) -> Optional[EncounterRunner]:
        """Get the currently active encounter runner."""
        return self.current_runner

    def end_encounter(self) -> Optional[Dict[str, Any]]:
        """End the current encounter and return results."""
        if not self.current_runner:
            return None

        result = self.current_runner.result
        self.current_runner = None
        return result

    def is_in_encounter(self) -> bool:
        """Check if an encounter is currently active."""
        return self.current_runner is not None and self.current_runner.state.active


if __name__ == "__main__":
    # Test with example encounter from template
    from src.dice import DiceSystem

    # Create a minimal skill system mock
    class MockSkill:
        effective_level = 2

    class MockSkillSystem:
        skills = {"Firearms": MockSkill(), "Stealth": MockSkill(), "Athletics": MockSkill()}

    # Load template encounter
    template_path = "content_templates/encounter_template.json"
    if os.path.exists(template_path):
        with open(template_path, 'r') as f:
            data = json.load(f)

        encounter = Encounter(data)
        dice = DiceSystem()
        skills = MockSkillSystem()

        runner = EncounterRunner(encounter, dice, skills)

        print("=== ENCOUNTER TEST ===\n")
        print("Intro:", runner.get_intro())
        print("\nAvailable options:")
        for opt in runner.get_available_options():
            print(f"  - {opt.label}: {opt.description}")

        print("\nExecuting 'take cover' with roll=8...")
        result = runner.execute_option("option_hide", manual_roll=8)
        print(f"Result: {result['result_type']}")
        print(f"Text: {result['text']}")

        print("\nAdvancing turn...")
        turn_result = runner.advance_turn()
        if turn_result["threat_action"]:
            print(f"Threat: {turn_result['threat_action']['text']}")
        for env in turn_result["environment_effects"]:
            print(f"Environment: {env['text']}")

        print(f"\nState: {runner.get_state_summary()}")
    else:
        print("Template not found. Run from project root.")
