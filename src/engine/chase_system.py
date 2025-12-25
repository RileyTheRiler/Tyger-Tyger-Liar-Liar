"""
Chase System - Chase and escape sequence mechanics with terrain navigation.

Handles pursuit sequences with alternating skill checks, environmental modifiers,
and dynamic obstacle navigation.
"""

import random
from typing import Dict, List, Optional, Any
import json
import os


class ChaseSystem:
    """Manages chase sequences with terrain, obstacles, and environmental effects."""
    
    def __init__(self):
        self.active_chase: Optional[Dict[str, Any]] = None
        self.chase_scenarios: Dict[str, dict] = {}
        
    def load_chase_scenarios(self, filepath: str):
        """Load chase scenario templates from JSON file."""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.chase_scenarios = json.load(f)
                print(f"[ChaseSystem] Loaded {len(self.chase_scenarios)} chase scenarios.")
            except Exception as e:
                print(f"[ChaseSystem] Error loading chase scenarios: {e}")
        else:
            print(f"[ChaseSystem] Chase scenarios not found: {filepath}")
    
    def start_chase(self, scenario_id: str, skill_system, player_state: dict) -> Dict[str, Any]:
        """
        Initialize a chase sequence.
        
        Args:
            scenario_id: Chase scenario identifier
            skill_system: Reference to SkillSystem
            player_state: Player state dict
            
        Returns:
            Chase initialization result
        """
        if scenario_id in self.chase_scenarios:
            scenario = self.chase_scenarios[scenario_id]
        else:
            # Create default chase
            scenario = self._create_default_chase(scenario_id)
        
        self.active_chase = {
            "scenario_id": scenario_id,
            "name": scenario["name"],
            "description": scenario["description"],
            "terrain": scenario["terrain"],
            "obstacles": scenario["obstacles"].copy(),
            "environmental_modifiers": scenario.get("environmental_modifiers", {}),
            "pursuer_speed": scenario.get("pursuer_speed", 3),
            "escape_threshold": scenario.get("escape_threshold", 5),
            "player_distance": 0,  # Positive = ahead, negative = caught
            "current_obstacle_index": 0,
            "round": 1,
            "log": []
        }
        
        self._log(f"--- CHASE STARTED: {scenario['name']} ---")
        self._log(scenario["description"])
        
        return {
            "started": True,
            "message": scenario["description"],
            "available_actions": self._get_available_actions()
        }
    
    def _create_default_chase(self, scenario_id: str) -> dict:
        """Create a default chase scenario."""
        return {
            "name": "Generic Pursuit",
            "description": "You run through unfamiliar terrain, pursued by an unknown threat.",
            "terrain": "urban",
            "obstacles": [
                {"type": "barrier", "skill": "Athletics", "dc": 10},
                {"type": "crowd", "skill": "Stealth", "dc": 9}
            ],
            "pursuer_speed": 3,
            "escape_threshold": 5
        }
    
    def perform_action(self, action: str, skill_system, player_state: dict, 
                       injury_system=None) -> Dict[str, Any]:
        """
        Execute a chase action.
        
        Args:
            action: Action type ("sprint", "vault", "hide", "draw_weapon", "surrender")
            skill_system: Reference to SkillSystem
            player_state: Player state dict
            injury_system: Optional InjurySystem for injury application
            
        Returns:
            Action result with chase status
        """
        if not self.active_chase:
            return {"error": "No active chase."}
        
        result = {"action": action, "messages": []}
        
        # Apply environmental modifiers
        env_mods = self._get_environmental_modifiers(player_state)
        
        if action == "sprint":
            result.update(self._action_sprint(skill_system, env_mods))
        
        elif action.startswith("vault") or action.startswith("jump") or action.startswith("climb"):
            result.update(self._action_navigate_obstacle(skill_system, env_mods, injury_system))
        
        elif action == "hide":
            result.update(self._action_hide(skill_system, env_mods))
        
        elif action == "draw_weapon" or action == "draw weapon":
            result.update(self._action_draw_weapon())
        
        elif action == "surrender":
            result.update(self._action_surrender())
        
        else:
            result["messages"].append("Invalid chase action.")
            return result
        
        # Pursuer movement
        if self.active_chase and not result.get("chase_ended"):
            self._pursuer_turn()
        
        # Check chase end conditions
        if self.active_chase:
            end_result = self._check_chase_end()
            if end_result:
                result.update(end_result)
        
        result["chase_state"] = self.get_chase_status()
        return result
    
    def _action_sprint(self, skill_system, env_mods: dict) -> dict:
        """Sprint action - Athletics check to gain distance."""
        dc = 8
        
        # Apply environmental modifiers
        athletics_mod = env_mods.get("Athletics", 0)
        
        result = skill_system.roll_check("Athletics", dc)
        
        if result["success"]:
            # Gain distance based on how well you rolled
            distance_gained = 1 + (result["total"] - dc) // 3
            self.active_chase["player_distance"] += distance_gained
            
            msg = f"You sprint ahead! (+{distance_gained} distance)"
            self._log(msg)
            
            return {"messages": [msg], "distance_gained": distance_gained, "roll_result": result}
        else:
            msg = "You stumble, losing momentum!"
            self._log(msg)
            return {"messages": [msg], "distance_gained": 0, "roll_result": result}
    
    def _action_navigate_obstacle(self, skill_system, env_mods: dict, injury_system) -> dict:
        """Navigate obstacle - skill check based on obstacle type."""
        obstacles = self.active_chase["obstacles"]
        idx = self.active_chase["current_obstacle_index"]
        
        if idx >= len(obstacles):
            return {"messages": ["No obstacles ahead. Use 'sprint' to gain distance."]}
        
        obstacle = obstacles[idx]
        skill = obstacle["skill"]
        dc = obstacle["dc"]
        
        # Apply environmental modifiers
        skill_mod = env_mods.get(skill, 0)
        
        result = skill_system.roll_check(skill, dc)
        
        if result["success"]:
            # Successfully navigate
            distance_gained = 2  # Obstacles give more distance if cleared
            self.active_chase["player_distance"] += distance_gained
            self.active_chase["current_obstacle_index"] += 1
            
            msg = f"You clear the {obstacle['type']}! (+{distance_gained} distance)"
            self._log(msg)
            
            return {"messages": [msg], "distance_gained": distance_gained, "roll_result": result}
        else:
            # Failed - take injury and lose distance
            self.active_chase["player_distance"] -= 1
            
            msg = f"You fail to clear the {obstacle['type']}!"
            self._log(msg)
            
            messages = [msg]
            
            # Apply injury if injury_system available
            if injury_system:
                injury = injury_system.apply_injury(
                    "blunt_force",
                    location="general",
                    severity="minor"
                )
                messages.append(f"You take a minor injury: {injury.name}")
            
            return {"messages": messages, "distance_gained": -1, "roll_result": result}
    
    def _action_hide(self, skill_system, env_mods: dict) -> dict:
        """Hide action - Stealth check to evade pursuer."""
        dc = 12  # Harder to hide while being chased
        
        # Terrain modifiers
        terrain = self.active_chase["terrain"]
        if terrain == "forest":
            dc -= 2
        elif terrain == "urban":
            dc -= 1
        
        result = skill_system.roll_check("Stealth", dc)
        
        if result["success"]:
            # Successful hide ends chase
            msg = "You slip into the shadows. Your pursuer loses you!"
            self._log(msg)
            
            return {
                "messages": [msg],
                "chase_ended": True,
                "outcome": "escaped_hidden",
                "roll_result": result
            }
        else:
            msg = "You try to hide, but they spot you immediately!"
            self._log(msg)
            self.active_chase["player_distance"] -= 1
            
            return {"messages": [msg], "roll_result": result}
    
    def _action_draw_weapon(self) -> dict:
        """Draw weapon - transitions to combat."""
        msg = "You draw your weapon and turn to face your pursuer!"
        self._log(msg)
        
        return {
            "messages": [msg],
            "chase_ended": True,
            "outcome": "transition_to_combat"
        }
    
    def _action_surrender(self) -> dict:
        """Surrender - ends chase with capture."""
        msg = "You stop running and raise your hands."
        self._log(msg)
        
        return {
            "messages": [msg],
            "chase_ended": True,
            "outcome": "surrendered"
        }
    
    def _pursuer_turn(self):
        """Pursuer movement each round."""
        speed = self.active_chase["pursuer_speed"]
        self.active_chase["player_distance"] -= speed
        
        self._log(f"Your pursuer closes in! (-{speed} distance)")
        self.active_chase["round"] += 1
    
    def _check_chase_end(self) -> Optional[dict]:
        """Check if chase has ended."""
        distance = self.active_chase["player_distance"]
        threshold = self.active_chase["escape_threshold"]
        
        if distance >= threshold:
            # Escaped!
            msg = "You've put enough distance between you and your pursuer. You're safe!"
            self._log(msg)
            self.end_chase()
            
            return {
                "chase_ended": True,
                "outcome": "escaped",
                "messages": [msg]
            }
        
        elif distance <= -2:
            # Caught!
            msg = "Your pursuer catches up to you!"
            self._log(msg)
            self.end_chase()
            
            return {
                "chase_ended": True,
                "outcome": "caught",
                "messages": [msg]
            }
        
        return None
    
    def _get_environmental_modifiers(self, player_state: dict) -> dict:
        """Calculate environmental modifiers for current conditions."""
        mods = {}
        
        env_effects = self.active_chase.get("environmental_modifiers", {})
        
        # Check weather conditions
        weather = player_state.get("current_weather", "clear")
        if weather in env_effects:
            mods.update(env_effects[weather])
        
        # Check time of day
        time_of_day = player_state.get("time_of_day", "day")
        if time_of_day in env_effects:
            for skill, mod in env_effects[time_of_day].items():
                mods[skill] = mods.get(skill, 0) + mod
        
        return mods
    
    def _get_available_actions(self) -> List[str]:
        """Get list of available chase actions."""
        actions = ["sprint", "hide", "draw_weapon", "surrender"]
        
        # Add obstacle-specific actions
        obstacles = self.active_chase["obstacles"]
        idx = self.active_chase["current_obstacle_index"]
        
        if idx < len(obstacles):
            obstacle = obstacles[idx]
            actions.insert(1, f"vault {obstacle['type']}")
        
        return actions
    
    def _log(self, message: str):
        """Add message to chase log."""
        if self.active_chase:
            self.active_chase["log"].append(message)
    
    def get_chase_status(self) -> dict:
        """Get current chase state for UI display."""
        if not self.active_chase:
            return {
                "active": False,
                "name": "",
                "round": 0,
                "distance": 0,
                "escape_threshold": 0,
                "available_actions": [],
                "log": []
            }
        
        return {
            "active": True,
            "name": self.active_chase["name"],
            "round": self.active_chase["round"],
            "distance": self.active_chase["player_distance"],
            "escape_threshold": self.active_chase["escape_threshold"],
            "available_actions": self._get_available_actions(),
            "log": self.active_chase["log"][-5:]  # Last 5 messages
        }
    
    def get_chase_log(self) -> str:
        """Get formatted chase log."""
        if not self.active_chase:
            return "No active chase."
        
        log = "\n".join(self.active_chase["log"])
        return f"=== CHASE LOG ===\n{log}\n"
    
    def end_chase(self):
        """End the current chase."""
        if self.active_chase:
            self._log("--- CHASE ENDED ---")
            self.active_chase = None
    
    def is_active(self) -> bool:
        """Check if a chase is currently active."""
        return self.active_chase is not None
