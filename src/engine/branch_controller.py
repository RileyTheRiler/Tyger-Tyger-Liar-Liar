"""
Branch Controller - Centralized condition evaluation engine for dynamic scene branching.

Evaluates complex conditions based on:
- Board state (theories internalized, disproven)
- Skill thresholds (passive and active)
- Attention level ranges
- NPC relationship flags
- Parser memory (player input history)
- Time and weather conditions
- Item/evidence possession
"""

import re
import json
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict


class BranchController:
    """Evaluates scene conditions and filters choices based on game state."""
    
    def __init__(self):
        self.condition_cache = {}
        self.cache_enabled = False # Disable caching as state changes frequently
        self.debug_mode = False
        self.last_evaluation_log = []
        
    def evaluate_condition(self, condition: Dict[str, Any], game_state: Dict[str, Any]) -> bool:
        """
        Evaluate a single condition dictionary against current game state.
        
        Args:
            condition: Condition dictionary with various checks
            game_state: Current game state including board, skills, player_state, etc.
            
        Returns:
            True if condition is met, False otherwise
        """
        if not condition:
            return True  # Empty condition = always true
            
        # Check cache
        cache_key = None
        if self.cache_enabled:
            cache_key = self._get_cache_key(condition, game_state)
            if cache_key in self.condition_cache:
                return self.condition_cache[cache_key]
        
        self.last_evaluation_log = []
        result = self._evaluate_condition_recursive(condition, game_state)
        
        # Cache result
        if self.cache_enabled and cache_key:
            self.condition_cache[cache_key] = result
            
        return result
    
    def _evaluate_condition_recursive(self, condition: Dict[str, Any], game_state: Dict[str, Any]) -> bool:
        """Recursive condition evaluation with AND/OR logic support."""
        
        # Handle logical operators
        if "AND" in condition:
            results = [self._evaluate_condition_recursive(c, game_state) for c in condition["AND"]]
            result = all(results)
            self._log(f"AND condition: {results} -> {result}")
            return result
            
        if "OR" in condition:
            results = [self._evaluate_condition_recursive(c, game_state) for c in condition["OR"]]
            result = any(results)
            self._log(f"OR condition: {results} -> {result}")
            return result
            
        if "NOT" in condition:
            result = not self._evaluate_condition_recursive(condition["NOT"], game_state)
            self._log(f"NOT condition -> {result}")
            return result
        
        # Evaluate individual condition types
        checks = []
        
        # Board state checks
        if "required_theories" in condition:
            checks.append(self._check_required_theories(condition["required_theories"], game_state))
            
        if "disproven_theories" in condition:
            checks.append(self._check_disproven_theories(condition["disproven_theories"], game_state))
            
        if "active_theories_min" in condition:
            checks.append(self._check_active_theories_count(condition["active_theories_min"], game_state, "min"))
            
        if "active_theories_max" in condition:
            checks.append(self._check_active_theories_count(condition["active_theories_max"], game_state, "max"))
        
        # Skill checks
        if "skill_thresholds" in condition:
            checks.append(self._check_skill_thresholds(condition["skill_thresholds"], game_state))
            
        if "skill_gte" in condition:
            checks.append(self._check_skill_thresholds(condition["skill_gte"], game_state))
            
        if "skill_lte" in condition:
            checks.append(self._check_skill_thresholds(condition["skill_lte"], game_state, operator="lte"))
        
        # Attention checks
        if "attention_range" in condition:
            checks.append(self._check_attention_range(condition["attention_range"], game_state))
            
        if "attention_above" in condition:
            checks.append(self._check_attention_threshold(condition["attention_above"], game_state, "above"))
            
        if "attention_below" in condition:
            checks.append(self._check_attention_threshold(condition["attention_below"], game_state, "below"))
        
        # NPC checks
        if "npc_flags" in condition:
            checks.append(self._check_npc_flags(condition["npc_flags"], game_state))
            
        if "npc_relationship" in condition:
            checks.append(self._check_npc_relationship(condition["npc_relationship"], game_state))
        
        # Parser memory checks
        if "parser_memory" in condition:
            checks.append(self._check_parser_memory(condition["parser_memory"], game_state))
            
        if "parser_keywords" in condition:
            checks.append(self._check_parser_keywords(condition["parser_keywords"], game_state))
        
        # Time/weather checks
        if "time_range" in condition:
            checks.append(self._check_time_range(condition["time_range"], game_state))
            
        if "weather" in condition:
            checks.append(self._check_weather(condition["weather"], game_state))
        
        # Player state checks
        if "sanity_range" in condition:
            checks.append(self._check_stat_range("sanity", condition["sanity_range"], game_state))
            
        if "reality_range" in condition:
            checks.append(self._check_stat_range("reality", condition["reality_range"], game_state))
        
        # Flag checks
        if "player_flags" in condition:
            checks.append(self._check_player_flags(condition["player_flags"], game_state))
            
        if "location_flags" in condition:
            checks.append(self._check_location_flags(condition["location_flags"], game_state))
        
        # Inventory checks
        if "has_item" in condition:
            checks.append(self._check_has_item(condition["has_item"], game_state))
            
        if "has_evidence" in condition:
            checks.append(self._check_has_evidence(condition["has_evidence"], game_state))
        
        # All checks must pass (implicit AND)
        return all(checks) if checks else True
    
    # ===== Board State Checks =====
    
    def _check_required_theories(self, theories: List[str], game_state: Dict[str, Any]) -> bool:
        """Check if all required theories are internalized."""
        board = game_state.get("board")
        if not board:
            self._log(f"Required theories check FAILED: No board in game_state")
            return False
            
        for theory_id in theories:
            theory = board.get_theory(theory_id)
            if not theory or theory.status != "active":
                self._log(f"Required theory '{theory_id}' not active")
                return False
                
        self._log(f"Required theories check PASSED: {theories}")
        return True
    
    def _check_disproven_theories(self, theories: List[str], game_state: Dict[str, Any]) -> bool:
        """Check if specified theories are disproven."""
        board = game_state.get("board")
        if not board:
            return False
            
        for theory_id in theories:
            theory = board.get_theory(theory_id)
            if not theory or theory.status != "disproven":
                self._log(f"Theory '{theory_id}' not disproven")
                return False
                
        self._log(f"Disproven theories check PASSED: {theories}")
        return True
    
    def _check_active_theories_count(self, count: int, game_state: Dict[str, Any], mode: str) -> bool:
        """Check if active theory count meets threshold."""
        board = game_state.get("board")
        if not board:
            return False
            
        active_count = board.get_active_or_internalizing_count()
        
        if mode == "min":
            result = active_count >= count
            self._log(f"Active theories >= {count}: {active_count} -> {result}")
        else:  # max
            result = active_count <= count
            self._log(f"Active theories <= {count}: {active_count} -> {result}")
            
        return result
    
    # ===== Skill Checks =====
    
    def _check_skill_thresholds(self, thresholds: Dict[str, int], game_state: Dict[str, Any], operator: str = "gte") -> bool:
        """Check if skills meet thresholds."""
        skill_system = game_state.get("skill_system")
        if not skill_system:
            self._log("Skill threshold check FAILED: No skill_system")
            return False
            
        for skill_name, threshold in thresholds.items():
            skill = skill_system.get_skill(skill_name)
            if not skill:
                self._log(f"Skill '{skill_name}' not found")
                return False
                
            current_value = skill.get_total()
            
            if operator == "gte":
                if current_value < threshold:
                    self._log(f"Skill '{skill_name}' {current_value} < {threshold}")
                    return False
            elif operator == "lte":
                if current_value > threshold:
                    self._log(f"Skill '{skill_name}' {current_value} > {threshold}")
                    return False
                    
        self._log(f"Skill thresholds check PASSED: {thresholds}")
        return True
    
    # ===== Attention Checks =====
    
    def _check_attention_range(self, range_dict: Dict[str, float], game_state: Dict[str, Any]) -> bool:
        """Check if attention is within range."""
        attention_system = game_state.get("attention_system")
        if not attention_system:
            # Try to get from player_state
            attention = game_state.get("attention", 0)
        else:
            attention = attention_system.attention_level
            
        min_val = range_dict.get("min", 0)
        max_val = range_dict.get("max", 100)
        
        result = min_val <= attention <= max_val
        self._log(f"Attention range [{min_val}, {max_val}]: {attention} -> {result}")
        return result
    
    def _check_attention_threshold(self, threshold: float, game_state: Dict[str, Any], mode: str) -> bool:
        """Check if attention is above/below threshold."""
        attention_system = game_state.get("attention_system")
        if not attention_system:
            attention = game_state.get("attention", 0)
        else:
            attention = attention_system.attention_level
            
        if mode == "above":
            result = attention > threshold
        else:  # below
            result = attention < threshold
            
        self._log(f"Attention {mode} {threshold}: {attention} -> {result}")
        return result
    
    # ===== NPC Checks =====
    
    def _check_npc_flags(self, flags: Dict[str, Any], game_state: Dict[str, Any]) -> bool:
        """Check NPC flags (e.g., integrated, suspicious)."""
        npc_system = game_state.get("npc_system")
        if not npc_system:
            self._log("NPC flags check FAILED: No npc_system")
            return False
            
        for npc_id, expected_flags in flags.items():
            npc = npc_system.get_npc(npc_id)
            if not npc:
                self._log(f"NPC '{npc_id}' not found")
                return False
                
            for flag, expected_value in expected_flags.items():
                actual_value = npc.tags.get(flag) if hasattr(npc, 'tags') else None
                if actual_value != expected_value:
                    self._log(f"NPC '{npc_id}' flag '{flag}': {actual_value} != {expected_value}")
                    return False
                    
        self._log(f"NPC flags check PASSED")
        return True
    
    def _check_npc_relationship(self, relationships: Dict[str, Dict[str, Any]], game_state: Dict[str, Any]) -> bool:
        """Check NPC relationship stats (trust, fear, etc.)."""
        npc_system = game_state.get("npc_system")
        if not npc_system:
            return False
            
        for npc_id, stats in relationships.items():
            npc = npc_system.get_npc(npc_id)
            if not npc:
                return False
                
            for stat_name, threshold in stats.items():
                if not hasattr(npc, stat_name):
                    return False
                    
                actual = getattr(npc, stat_name)
                if isinstance(threshold, dict):
                    # Range check
                    min_val = threshold.get("min", float('-inf'))
                    max_val = threshold.get("max", float('inf'))
                    if not (min_val <= actual <= max_val):
                        return False
                else:
                    # Exact or >= check
                    if actual < threshold:
                        return False
                        
        self._log(f"NPC relationship check PASSED")
        return True
    
    # ===== Parser Memory Checks =====
    
    def _check_parser_memory(self, concepts: List[str], game_state: Dict[str, Any]) -> bool:
        """Check if concepts have been discovered via parser."""
        parser_memory = game_state.get("parser_memory")
        if not parser_memory:
            self._log("Parser memory check FAILED: No parser_memory")
            return False
            
        discovered = parser_memory.get_discovered_concepts()
        
        for concept in concepts:
            if concept not in discovered:
                self._log(f"Concept '{concept}' not discovered")
                return False
                
        self._log(f"Parser memory check PASSED: {concepts}")
        return True
    
    def _check_parser_keywords(self, keywords: List[str], game_state: Dict[str, Any]) -> bool:
        """Check if keywords have been mentioned."""
        parser_memory = game_state.get("parser_memory")
        if not parser_memory:
            return False
            
        for keyword in keywords:
            if not parser_memory.has_mentioned(keyword):
                self._log(f"Keyword '{keyword}' not mentioned")
                return False
                
        self._log(f"Parser keywords check PASSED: {keywords}")
        return True
    
    # ===== Time/Weather Checks =====
    
    def _check_time_range(self, time_range: List[str], game_state: Dict[str, Any]) -> bool:
        """Check if current time is within range."""
        time_system = game_state.get("time_system")
        if not time_system:
            current_time = game_state.get("time")
        else:
            current_time = time_system.current_time
            
        if not current_time:
            return False
            
        start_str, end_str = time_range
        start_h = int(start_str.split(":")[0])
        end_h = int(end_str.split(":")[0])
        current_h = current_time.hour
        
        if start_h <= end_h:
            result = start_h <= current_h < end_h
        else:  # Overnight
            result = current_h >= start_h or current_h < end_h
            
        self._log(f"Time range [{start_str}, {end_str}]: {current_h}:00 -> {result}")
        return result
    
    def _check_weather(self, allowed_weather: List[str], game_state: Dict[str, Any]) -> bool:
        """Check if current weather is in allowed list."""
        time_system = game_state.get("time_system")
        if not time_system:
            return True  # No weather system = always pass
            
        current_weather = time_system.weather
        result = current_weather in allowed_weather
        self._log(f"Weather check {allowed_weather}: {current_weather} -> {result}")
        return result
    
    # ===== Player State Checks =====
    
    def _check_stat_range(self, stat_name: str, range_dict: Dict[str, float], game_state: Dict[str, Any]) -> bool:
        """Check if player stat is within range."""
        player_state = game_state.get("player_state", {})
        stat_value = player_state.get(stat_name, game_state.get(stat_name, 100))
        
        min_val = range_dict.get("min", 0)
        max_val = range_dict.get("max", 100)
        
        result = min_val <= stat_value <= max_val
        self._log(f"{stat_name.capitalize()} range [{min_val}, {max_val}]: {stat_value} -> {result}")
        return result
    
    def _check_player_flags(self, flags: Dict[str, bool], game_state: Dict[str, Any]) -> bool:
        """Check player event flags."""
        player_flags = game_state.get("player_flags", set())
        player_state = game_state.get("player_state", {})
        event_flags = player_state.get("event_flags", set())
        
        # Combine both sources
        all_flags = player_flags | event_flags
        
        for flag, expected in flags.items():
            has_flag = flag in all_flags
            if has_flag != expected:
                self._log(f"Player flag '{flag}': {has_flag} != {expected}")
                return False
                
        self._log(f"Player flags check PASSED")
        return True
    
    def _check_location_flags(self, flags: Dict[str, Any], game_state: Dict[str, Any]) -> bool:
        """Check location-specific flags."""
        current_location = game_state.get("current_location")
        location_states = game_state.get("location_states", {})
        
        if not current_location:
            return False
            
        loc_state = location_states.get(current_location, {})
        
        for flag, expected in flags.items():
            actual = loc_state.get(flag)
            if actual != expected:
                self._log(f"Location flag '{flag}': {actual} != {expected}")
                return False
                
        self._log(f"Location flags check PASSED")
        return True
    
    # ===== Inventory Checks =====
    
    def _check_has_item(self, item_ids: List[str], game_state: Dict[str, Any]) -> bool:
        """Check if player has specific items."""
        inventory_system = game_state.get("inventory_system")
        if not inventory_system:
            return False
            
        for item_id in item_ids:
            if not inventory_system.has_item(item_id):
                self._log(f"Item '{item_id}' not in inventory")
                return False
                
        self._log(f"Has item check PASSED: {item_ids}")
        return True
    
    def _check_has_evidence(self, evidence_ids: List[str], game_state: Dict[str, Any]) -> bool:
        """Check if player has specific evidence."""
        inventory_system = game_state.get("inventory_system")
        if not inventory_system:
            return False
            
        for evidence_id in evidence_ids:
            if not inventory_system.has_evidence(evidence_id):
                self._log(f"Evidence '{evidence_id}' not collected")
                return False
                
        self._log(f"Has evidence check PASSED: {evidence_ids}")
        return True
    
    # ===== Choice Filtering =====
    
    def filter_choices(self, choices: List[Dict[str, Any]], game_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter choices based on their conditions.
        
        Args:
            choices: List of choice dictionaries
            game_state: Current game state
            
        Returns:
            Filtered list of available choices
        """
        available = []
        
        for choice in choices:
            condition = choice.get("condition") or choice.get("requires")
            
            if not condition:
                # No condition = always available
                available.append(choice)
            elif self.evaluate_condition(condition, game_state):
                available.append(choice)
            elif self.debug_mode:
                # In debug mode, show blocked choices
                choice_copy = choice.copy()
                choice_copy["_blocked"] = True
                available.append(choice_copy)
                
        return available
    
    def get_next_scene(self, current_scene: Dict[str, Any], choice: Dict[str, Any], game_state: Dict[str, Any]) -> Optional[str]:
        """
        Determine the next scene ID based on choice and conditions.
        
        Args:
            current_scene: Current scene data
            choice: Selected choice
            game_state: Current game state
            
        Returns:
            Next scene ID or None
        """
        # Simple case: direct next_scene
        if "next_scene" in choice:
            return choice["next_scene"]
        
        # Conditional branching
        if "branches" in choice:
            for branch in choice["branches"]:
                if self.evaluate_condition(branch.get("condition", {}), game_state):
                    return branch.get("next_scene")
            
            # Fallback
            return choice.get("default_scene")
        
        return None
    
    # ===== Utility Methods =====
    
    def _get_cache_key(self, condition: Dict[str, Any], game_state: Dict[str, Any]) -> str:
        """Generate cache key for condition."""
        # Simple hash of condition + relevant game state
        return json.dumps(condition, sort_keys=True)
    
    def _log(self, message: str):
        """Log evaluation step."""
        if self.debug_mode:
            self.last_evaluation_log.append(message)
    
    def clear_cache(self):
        """Clear condition cache."""
        self.condition_cache.clear()
    
    def get_evaluation_log(self) -> List[str]:
        """Get log of last evaluation."""
        return self.last_evaluation_log.copy()
    
    def validate_scene_graph(self, scenes: Dict[str, Dict[str, Any]]) -> List[str]:
        """
        Validate scene graph for common issues.
        
        Returns:
            List of warning/error messages
        """
        issues = []
        
        for scene_id, scene in scenes.items():
            # Check for unreachable scenes
            choices = scene.get("choices", [])
            
            for choice in choices:
                next_scene = choice.get("next_scene")
                if next_scene and next_scene not in scenes:
                    issues.append(f"Scene '{scene_id}' references missing scene '{next_scene}'")
            
            # Check for impossible conditions
            condition = scene.get("conditions", {})
            if "required_theories" in condition and "disproven_theories" in condition:
                overlap = set(condition["required_theories"]) & set(condition["disproven_theories"])
                if overlap:
                    issues.append(f"Scene '{scene_id}' has contradictory theory requirements: {overlap}")
        
        return issues
