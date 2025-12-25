"""
Trauma System - Psychological trauma modeling with Fortitude checks and narrative effects.

Handles psychological trauma from extreme events (torture, death, supernatural encounters).
Traumas apply persistent mental penalties and influence narrative perception.
"""

import json
import os
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class Trauma:
    """Represents a psychological trauma with mechanical and narrative effects."""
    id: str
    name: str
    type: str  # "flashbacks", "insomnia", "obsessive_patterning", "paranoia", "dissociation"
    description: str
    effects: Dict[str, int]  # Skill penalties {"Composure": -2, "Fortitude": -1}
    duration_hours: float  # Total duration
    duration_remaining: float  # Time left
    trigger_chance: float = 0.0  # 0.0-1.0 chance to trigger per scene
    narrative_effects: List[str] = field(default_factory=list)  # ["random_memory_inserts", "perception_distortion"]
    treatment: str = "rest_and_time"  # "rest_and_time", "therapy", "medication"
    severity: str = "moderate"  # "minor", "moderate", "severe"
    triggered_this_scene: bool = False
    
    def to_dict(self) -> dict:
        """Serialize trauma to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "effects": self.effects,
            "duration_hours": self.duration_hours,
            "duration_remaining": self.duration_remaining,
            "trigger_chance": self.trigger_chance,
            "narrative_effects": self.narrative_effects,
            "treatment": self.treatment,
            "severity": self.severity,
            "triggered_this_scene": self.triggered_this_scene
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Trauma':
        """Deserialize trauma from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            description=data["description"],
            effects=data["effects"],
            duration_hours=data["duration_hours"],
            duration_remaining=data["duration_remaining"],
            trigger_chance=data.get("trigger_chance", 0.0),
            narrative_effects=data.get("narrative_effects", []),
            treatment=data.get("treatment", "rest_and_time"),
            severity=data.get("severity", "moderate"),
            triggered_this_scene=data.get("triggered_this_scene", False)
        )


class TraumaSystem:
    """Manages psychological trauma application, tracking, and recovery."""
    
    # Trauma trigger events and their base DCs
    TRAUMA_TRIGGERS = {
        "witness_death": {"dc": 10, "trauma_type": "flashbacks"},
        "witness_torture": {"dc": 12, "trauma_type": "flashbacks"},
        "supernatural_encounter": {"dc": 14, "trauma_type": "paranoia"},
        "personal_torture": {"dc": 15, "trauma_type": "dissociation"},
        "betrayal": {"dc": 11, "trauma_type": "paranoia"},
        "entity_contact": {"dc": 16, "trauma_type": "obsessive_patterning"}
    }
    
    def __init__(self):
        self.trauma_database: Dict[str, dict] = {}
        self.active_traumas: List[Trauma] = []
        self.trauma_history: List[str] = []  # IDs of past traumas
        
    def load_trauma_database(self, filepath: str):
        """Load trauma templates from JSON file."""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.trauma_database = json.load(f)
                print(f"[TraumaSystem] Loaded {len(self.trauma_database)} trauma templates.")
            except Exception as e:
                print(f"[TraumaSystem] Error loading trauma database: {e}")
        else:
            print(f"[TraumaSystem] Trauma database not found: {filepath}")
    
    def check_trauma_trigger(self, trigger_event: str, skill_system, player_state: dict) -> Dict[str, Any]:
        """
        Check if a traumatic event causes trauma via Fortitude check.
        
        Args:
            trigger_event: Event identifier (e.g., "witness_death")
            skill_system: Reference to SkillSystem for checks
            player_state: Player state dict for sanity/reality modifiers
            
        Returns:
            Result dictionary with trauma application status
        """
        if trigger_event not in self.TRAUMA_TRIGGERS:
            return {"trauma_applied": False, "message": "Unknown trauma trigger."}
        
        trigger_data = self.TRAUMA_TRIGGERS[trigger_event]
        base_dc = trigger_data["dc"]
        
        # Modify DC based on existing traumas (each trauma makes you more vulnerable)
        dc = base_dc + len(self.active_traumas)
        
        # Modify DC based on sanity (lower sanity = harder to resist)
        sanity = player_state.get("sanity", 100.0)
        if sanity < 50:
            dc += 2
        if sanity < 25:
            dc += 2
        
        # Fortitude check
        result = skill_system.roll_check("Fortitude", dc)
        
        if result["success"]:
            return {
                "trauma_applied": False,
                "message": "You steel yourself against the horror. Your mind holds.",
                "roll_result": result
            }
        else:
            # Apply trauma
            trauma_type = trigger_data["trauma_type"]
            trauma = self.apply_trauma(trauma_type, trigger_event)
            
            return {
                "trauma_applied": True,
                "trauma": trauma,
                "message": f"The experience overwhelms you. You suffer: {trauma.name}",
                "roll_result": result
            }
    
    def apply_trauma(self, trauma_type: str, source: str = "unknown") -> Trauma:
        """
        Apply a trauma to the player.
        
        Args:
            trauma_type: Type identifier (e.g., "flashbacks", "paranoia")
            source: What caused the trauma
            
        Returns:
            The created Trauma object
        """
        # Try to load from database first
        if trauma_type in self.trauma_database:
            template = self.trauma_database[trauma_type]
            trauma = Trauma(
                id=f"{trauma_type}_{len(self.active_traumas)}",
                name=template["name"],
                type=trauma_type,
                description=template["description"],
                effects=template["effects"],
                duration_hours=template["duration_hours"],
                duration_remaining=template["duration_hours"],
                trigger_chance=template.get("trigger_chance", 0.0),
                narrative_effects=template.get("narrative_effects", []),
                treatment=template.get("treatment", "rest_and_time"),
                severity=template.get("severity", "moderate")
            )
        else:
            # Generate default trauma
            trauma = self._create_default_trauma(trauma_type, source)
        
        self.active_traumas.append(trauma)
        return trauma
    
    def _create_default_trauma(self, trauma_type: str, source: str) -> Trauma:
        """Create a default trauma when not in database."""
        defaults = {
            "flashbacks": {
                "name": "Flashbacks",
                "description": "Intrusive memories flood your mind at random moments.",
                "effects": {"Composure": -2, "Fortitude": -1},
                "duration": 168.0,  # 1 week
                "trigger_chance": 0.3
            },
            "insomnia": {
                "name": "Insomnia",
                "description": "Sleep eludes you. When it comes, nightmares follow.",
                "effects": {"Perception": -1, "Composure": -1, "Endurance": -1},
                "duration": 120.0,
                "trigger_chance": 0.2
            },
            "obsessive_patterning": {
                "name": "Obsessive Pattern Recognition",
                "description": "You see connections everywhere. Most aren't real.",
                "effects": {"Logic": -1, "Skepticism": -2},
                "duration": 96.0,
                "trigger_chance": 0.4
            },
            "paranoia": {
                "name": "Paranoia",
                "description": "Everyone is suspect. Everything is a threat.",
                "effects": {"Empathy": -2, "Authority": -1, "Composure": -1},
                "duration": 144.0,
                "trigger_chance": 0.25
            },
            "dissociation": {
                "name": "Dissociation",
                "description": "You feel disconnected from reality. Are you even here?",
                "effects": {"Perception": -2, "Composure": -2},
                "duration": 72.0,
                "trigger_chance": 0.35
            }
        }
        
        template = defaults.get(trauma_type, defaults["flashbacks"])
        
        return Trauma(
            id=f"{trauma_type}_{len(self.active_traumas)}",
            name=template["name"],
            type=trauma_type,
            description=template["description"],
            effects=template["effects"],
            duration_hours=template["duration"],
            duration_remaining=template["duration"],
            trigger_chance=template["trigger_chance"],
            narrative_effects=["perception_distortion"],
            severity="moderate"
        )
    
    def get_total_penalties(self) -> Dict[str, int]:
        """Calculate total skill penalties from all active traumas."""
        penalties: Dict[str, int] = {}
        
        for trauma in self.active_traumas:
            for skill, penalty in trauma.effects.items():
                penalties[skill] = penalties.get(skill, 0) + penalty
        
        return penalties
    
    def get_penalty_for_skill(self, skill_name: str) -> int:
        """Get total trauma penalty for a specific skill."""
        penalties = self.get_total_penalties()
        return penalties.get(skill_name, 0)
    
    def check_trauma_triggers(self, context: str = "") -> List[Dict[str, Any]]:
        """
        Check if any traumas trigger this scene.
        
        Returns:
            List of triggered trauma effects
        """
        triggered = []
        
        for trauma in self.active_traumas:
            if trauma.triggered_this_scene:
                continue
            
            if random.random() < trauma.trigger_chance:
                trauma.triggered_this_scene = True
                triggered.append({
                    "trauma": trauma,
                    "effect": self._get_trauma_trigger_effect(trauma, context)
                })
        
        return triggered
    
    def _get_trauma_trigger_effect(self, trauma: Trauma, context: str) -> str:
        """Generate narrative effect when trauma triggers."""
        effects = {
            "flashbacks": [
                "The memory hits you like a physical blow. You're back there, reliving it.",
                "Your vision blurs. For a moment, you're somewhere else entirely.",
                "The past crashes into the present. You can't tell which is real."
            ],
            "insomnia": [
                "Exhaustion weighs on you. How long since you truly slept?",
                "Your eyes burn. The world seems slightly unreal through the haze of fatigue.",
                "You blink hard, trying to focus. Everything feels distant, dreamlike."
            ],
            "obsessive_patterning": [
                "The connections are everywhere. You MUST find the pattern.",
                "Numbers, symbols, coincidences—they all mean something. They have to.",
                "Your mind races, linking disparate facts into a web only you can see."
            ],
            "paranoia": [
                "They're watching. You're sure of it. Who are they?",
                "Trust no one. Everyone has an agenda. Everyone lies.",
                "The hairs on your neck stand up. Danger. Everywhere."
            ],
            "dissociation": [
                "Are you really here? This doesn't feel real.",
                "You watch yourself from outside your body. A stranger wearing your face.",
                "The world is muffled, distant. You're floating through it like a ghost."
            ]
        }
        
        trauma_effects = effects.get(trauma.type, ["Your trauma surfaces."])
        return random.choice(trauma_effects)
    
    def reset_scene_triggers(self):
        """Reset trauma triggers for new scene."""
        for trauma in self.active_traumas:
            trauma.triggered_this_scene = False
    
    def advance_time(self, hours: float) -> List[str]:
        """
        Advance trauma duration timers.
        
        Returns:
            List of status messages
        """
        messages = []
        recovered = []
        
        for trauma in self.active_traumas:
            trauma.duration_remaining -= hours
            
            if trauma.duration_remaining <= 0:
                recovered.append(trauma)
                messages.append(f"[RECOVERY] Your '{trauma.name}' has faded with time.")
                self.trauma_history.append(trauma.id)
        
        # Remove recovered traumas
        for trauma in recovered:
            self.active_traumas.remove(trauma)
        
        return messages
    
    def get_narrative_effects(self) -> List[str]:
        """Get list of all active narrative effect types."""
        effects = []
        for trauma in self.active_traumas:
            effects.extend(trauma.narrative_effects)
        return list(set(effects))  # Remove duplicates
    
    def has_trauma_type(self, trauma_type: str) -> bool:
        """Check if player has a specific type of trauma."""
        return any(t.type == trauma_type for t in self.active_traumas)
    
    def get_trauma_status(self) -> str:
        """Get formatted string of all active traumas."""
        if not self.active_traumas:
            return "No active psychological traumas."
        
        status = "=== PSYCHOLOGICAL STATE ===\n"
        for i, trauma in enumerate(self.active_traumas, 1):
            time_str = f"{trauma.duration_remaining:.1f}h remaining"
            
            status += f"{i}. {trauma.name} [{trauma.severity.upper()}]\n"
            status += f"   {trauma.description}\n"
            status += f"   Effects: {', '.join(f'{k} {v}' for k, v in trauma.effects.items())}\n"
            status += f"   Duration: {time_str}\n"
            status += "\n"
        
        return status
    
    def apply_trauma_to_text(self, base_text: str, player_state: dict) -> str:
        """
        Modify text based on active traumas.
        
        Args:
            base_text: Original text
            player_state: Player state for additional context
            
        Returns:
            Modified text with trauma effects
        """
        modified_text = base_text
        
        for trauma in self.active_traumas:
            if "perception_distortion" in trauma.narrative_effects:
                if trauma.type == "paranoia" and random.random() < 0.3:
                    modified_text += "\n\n(Are they watching you? You feel eyes on your back.)"
                
                elif trauma.type == "dissociation" and random.random() < 0.2:
                    modified_text += "\n\n(This doesn't feel real. Nothing feels real anymore.)"
                
                elif trauma.type == "obsessive_patterning" and random.random() < 0.25:
                    modified_text += "\n\n(The patterns... you see them everywhere. They mean something.)"
        
        return modified_text
    
    def to_dict(self) -> dict:
        """Serialize trauma system state."""
        return {
            "active_traumas": [t.to_dict() for t in self.active_traumas],
            "trauma_history": self.trauma_history
        }
    
    def from_dict(self, data: dict):
        """Restore trauma system state."""
        self.active_traumas = [Trauma.from_dict(t) for t in data.get("active_traumas", [])]
        self.trauma_history = data.get("trauma_history", [])
