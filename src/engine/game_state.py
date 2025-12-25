import json
import os
from typing import Dict, List, Any, Optional

class GameState:
    # Skill -> Attribute Mapping from mechanics.py
    SKILL_MAP = {
        # REASON
        "Logic": "REASON", "Forensics": "REASON", "Research": "REASON", 
        "Skepticism": "REASON", "Medicine": "REASON", "Technology": "REASON", 
        "Occult Knowledge": "REASON",
        # INTUITION
        "Pattern Recognition": "INTUITION", "Paranormal Sensitivity": "INTUITION", 
        "Profiling": "INTUITION", "Instinct": "INTUITION", "Subconscious": "INTUITION", 
        "Manipulation": "INTUITION", "Perception": "INTUITION",
        # CONSTITUTION
        "Endurance": "CONSTITUTION", "Fortitude": "CONSTITUTION", "Firearms": "CONSTITUTION", 
        "Athletics": "CONSTITUTION", "Stealth": "CONSTITUTION", "Reflexes": "CONSTITUTION", 
        "Survival": "CONSTITUTION", "Hand-to-Hand Combat": "CONSTITUTION",
        # PRESENCE
        "Authority": "PRESENCE", "Charm": "PRESENCE", "Wits": "PRESENCE", 
        "Composure": "PRESENCE", "Empathy": "PRESENCE", "Interrogation": "PRESENCE", 
        "Deception": "PRESENCE"
    }

    def __init__(self):
        # Core Meters
        self.sanity = 100
        self.max_sanity = 100
        self.reality = 100
        self.max_reality = 100
        
        # Core Identity
        self.archetype = "neutral"  # believer, skeptic, haunted
        
        # Attributes
        self.attributes = {
            "REASON": 1,
            "INTUITION": 1,
            "CONSTITUTION": 1,
            "PRESENCE": 1
        }
        # Skills (Rank only, effective skill = rank + attribute)
        self.skills = {skill: 0 for skill in self.SKILL_MAP.keys()}
        
        # World & Flags
        self.flags = {}  # flag_id -> Any
        self.inventory = []  # List of item IDs
        
        # Time System
        self.time = {
            "day": 1,
            "block": "dawn",
            "minutes": 480
        }
        
        # Meters
        self.attention_meter = 0
        self.population_current = 347
        
        # NPC Trust
        self.trust = {}
        
        # Conditions
        self.conditions = [] 
        
        # Board Graph
        self.board_graph = {
            "nodes": [],
            "edges": []
        }
        
        # Navigation
        self.current_scene_id = "hello"
        self.visited_scenes = set()

    # --- Effect Handlers ---

    def apply_flag(self, flag_id: str, value: Any = True):
        self.flags[flag_id] = value

    def modify_trust(self, npc_id: str, delta: int):
        current = self.trust.get(npc_id, 0)
        self.trust[npc_id] = max(-100, min(100, current + delta))

    def advance_time(self, delta_minutes: int):
        self.time["minutes"] += delta_minutes
        if self.time["minutes"] >= 1440:
            self.time["day"] += self.time["minutes"] // 1440
            self.time["minutes"] %= 1440
        
        m = self.time["minutes"]
        if 0 <= m < 360: self.time["block"] = "night"
        elif 360 <= m < 480: self.time["block"] = "dawn"
        elif 480 <= m < 720: self.time["block"] = "morning"
        elif 720 <= m < 1080: self.time["block"] = "afternoon"
        elif 1080 <= m < 1260: self.time["block"] = "twilight"
        else: self.time["block"] = "night"

    def modify_attention(self, delta: int):
        self.attention_meter = max(0, min(100, self.attention_meter + delta))

    def modify_population(self, delta: int):
        self.population_current += delta

    def add_condition(self, condition_id: str):
        if condition_id not in self.conditions:
            self.conditions.append(condition_id)

    def remove_condition(self, condition_id: str):
        if condition_id in self.conditions:
            self.conditions.remove(condition_id)

    def add_board_node(self, node: dict):
        """Add or update a node in the board graph."""
        for existing in self.board_graph["nodes"]:
            if existing["id"] == node["id"]:
                existing.update(node)
                return
        self.board_graph["nodes"].append(node)

    def add_board_edge(self, from_id: str, to_id: str, edge_type: str):
        edge = {"from": from_id, "to": to_id, "type": edge_type}
        if edge not in self.board_graph["edges"]:
            self.board_graph["edges"].append(edge)

    def modify_sanity(self, delta: int):
        self.sanity = max(0, min(self.max_sanity, self.sanity + delta))

    def modify_reality(self, delta: int):
        self.reality = max(0, min(self.max_reality, self.reality + delta))

    # --- Skill Checks ---

    def get_effective_skill(self, skill_id: str) -> int:
        rank = self.skills.get(skill_id, 0)
        attr_name = self.SKILL_MAP.get(skill_id)
        attr_val = self.attributes.get(attr_name, 1) if attr_name else 0
        
        penalty = self._get_condition_penalties(skill_id)
        # Note: In DE, effective = attr + rank + modifiers. 
        # We'll treat our 'penalty' as a general modifier.
        return max(0, attr_val + rank + penalty)

    def _get_condition_penalties(self, skill_id: str) -> int:
        # This will be expanded in later phases with actual data
        return 0

    # --- Persistence ---

    def to_dict(self) -> dict:
        return {
            "sanity": self.sanity,
            "max_sanity": self.max_sanity,
            "reality": self.reality,
            "max_reality": self.max_reality,
            "archetype": self.archetype,
            "attributes": self.attributes,
            "skills": self.skills,
            "flags": self.flags,
            "inventory": self.inventory,
            "time": self.time,
            "attention_meter": self.attention_meter,
            "population_current": self.population_current,
            "trust": self.trust,
            "conditions": self.conditions,
            "board_graph": self.board_graph,
            "current_scene_id": self.current_scene_id,
            "visited_scenes": list(self.visited_scenes),
            "version_hash": "v1.0.0" 
        }

    @classmethod
    def from_dict(cls, data: dict):
        state = cls()
        state.sanity = data.get("sanity", 100)
        state.max_sanity = data.get("max_sanity", 100)
        state.reality = data.get("reality", 100)
        state.max_reality = data.get("max_reality", 100)
        state.archetype = data.get("archetype", "neutral")
        state.attributes = data.get("attributes", state.attributes)
        state.skills = data.get("skills", state.skills)
        state.flags = data.get("flags", {})
        state.inventory = data.get("inventory", [])
        state.time = data.get("time", state.time)
        state.attention_meter = data.get("attention_meter", 0)
        state.population_current = data.get("population_current", 347)
        state.trust = data.get("trust", {})
        state.conditions = data.get("conditions", [])
        state.board_graph = data.get("board_graph", state.board_graph)
        state.current_scene_id = data.get("current_scene_id", "hello")
        state.visited_scenes = set(data.get("visited_scenes", []))
        return state

    def save(self, filename: str):
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, filename: str):
        with open(filename, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
