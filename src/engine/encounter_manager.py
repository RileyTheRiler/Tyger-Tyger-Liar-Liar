from typing import List, Dict, Any, Optional
from dice import DiceSystem, CheckResult

class EncounterManager:
    def __init__(self, game_state, dice_system: DiceSystem):
        self.state = game_state
        self.dice = dice_system
        self.current_encounter = None
        self.current_turn = 0
        self.encounter_state = {}
        self.is_active = False

    def start_encounter(self, encounter_data: dict):
        self.current_encounter = encounter_data
        self.current_turn = 0
        self.encounter_state = encounter_data.get("state_defaults", {}).copy()
        self.is_active = True
        return encounter_data.get("intro_text", {}).get("base", "")

    def get_current_options(self) -> List[dict]:
        if not self.is_active: return []
        
        options_list = self.current_encounter.get("options_by_turn", [])
        if self.current_turn < len(options_list):
            return options_list[self.current_turn]
        # If we run out of turns, maybe repeat last or return empty
        return []

    def resolve_turn(self, option_idx: int, manual_roll: int = None) -> dict:
        """Resolve a selected option and advance the encounter."""
        options = self.get_current_options()
        if not options or option_idx >= len(options):
            return {"error": "Invalid option"}
        
        option = options[option_idx]
        skill = option.get("skill")
        dc = option.get("dc", 9)
        
        # Get modifier from game state
        modifier = self.state.get_effective_skill(skill)
        
        # Resolve check
        roll_res = self.dice.resolve_check(skill, modifier, dc, manual_roll=manual_roll)
        
        # Apply outcomes
        outcomes = option.get("outcomes", {})
        outcome_data = {}
        
        if roll_res.result == CheckResult.CRITICAL_SUCCESS or roll_res.result == CheckResult.SUCCESS:
            outcome_data = outcomes.get("success", {})
        elif roll_res.result == CheckResult.PARTIAL_SUCCESS:
            outcome_data = outcomes.get("partial", {})
        else:
            outcome_data = outcomes.get("failure", {})
            
        # Apply outcome effects to encounter state
        effects = outcome_data.get("effects", {})
        for k, v in effects.items():
            if isinstance(v, (int, float)):
                self.encounter_state[k] = self.encounter_state.get(k, 0) + v
            else:
                self.encounter_state[k] = v
                
        # Handle environment rules (turn rules)
        turn_rules = self.current_encounter.get("turn_rules", {})
        env_msg = ""
        for k, v in turn_rules.items():
            # Example: "cold": -10
            if k in self.encounter_state and isinstance(v, (int, float)):
                self.encounter_state[k] += v
                if self.encounter_state[k] < 0: # Threshold logic
                    env_msg = f"The {k} is becoming critical!"

        # Advance turn
        self.current_turn += 1
        
        # Check exit conditions
        exit_msg, finished = self._check_exit()
        if finished:
            self.is_active = False

        return {
            "description": outcome_data.get("text", "You proceed."),
            "roll": self.dice.format_roll_result(roll_res),
            "env_msg": env_msg,
            "exit_msg": exit_msg,
            "finished": finished,
            "encounter_state": self.encounter_state
        }

    def _check_exit(self) -> (str, bool):
        exit_conds = self.current_encounter.get("exit_conditions", {})
        
        # Success exit
        success_cond = exit_conds.get("success", {})
        for k, v in success_cond.get("state_gte", {}).items():
            if self.encounter_state.get(k, 0) >= v:
                return success_cond.get("text", "Goal reached!"), True
                
        # Failure exit
        failure_cond = exit_conds.get("failure", {})
        for k, v in failure_cond.get("state_lte", {}).items():
            if self.encounter_state.get(k, 0) <= v:
                return failure_cond.get("text", "You failed."), True
        
        # Turn limit
        if self.current_turn >= len(self.current_encounter.get("options_by_turn", [])):
            return "Time has run out.", True
            
        return "", False
