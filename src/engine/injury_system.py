"""
Injury System - Narrative injury modeling with location-based penalties and treatment mechanics.

Handles physical injuries from combat, environmental hazards, and other sources.
Injuries apply persistent skill penalties, require treatment, and can escalate if neglected.
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class Injury:
    """Represents a physical injury with mechanical and narrative effects."""
    id: str
    name: str
    location: str  # "leg", "arm", "head", "torso", "general"
    severity: str  # "minor", "moderate", "severe", "critical"
    effects: Dict[str, int]  # Skill penalties {"Athletics": -2, "Stealth": -1}
    healing_time_hours: float  # Total time to heal
    healing_time_remaining: float  # Time left until healed
    treatment_required: bool = False
    treatment_skill: str = "Medicine"
    treatment_dc: int = 10
    equipment_needed: List[str] = field(default_factory=list)
    permanent_risk: float = 0.0  # 0.0-1.0 chance of permanent effect
    description: str = ""
    treated: bool = False
    worsening_threshold_hours: float = 48.0  # Hours before injury worsens if untreated
    time_since_injury: float = 0.0
    
    def to_dict(self) -> dict:
        """Serialize injury to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "severity": self.severity,
            "effects": self.effects,
            "healing_time_hours": self.healing_time_hours,
            "healing_time_remaining": self.healing_time_remaining,
            "treatment_required": self.treatment_required,
            "treatment_skill": self.treatment_skill,
            "treatment_dc": self.treatment_dc,
            "equipment_needed": self.equipment_needed,
            "permanent_risk": self.permanent_risk,
            "description": self.description,
            "treated": self.treated,
            "worsening_threshold_hours": self.worsening_threshold_hours,
            "time_since_injury": self.time_since_injury
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Injury':
        """Deserialize injury from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            location=data["location"],
            severity=data["severity"],
            effects=data["effects"],
            healing_time_hours=data["healing_time_hours"],
            healing_time_remaining=data["healing_time_remaining"],
            treatment_required=data.get("treatment_required", False),
            treatment_skill=data.get("treatment_skill", "Medicine"),
            treatment_dc=data.get("treatment_dc", 10),
            equipment_needed=data.get("equipment_needed", []),
            permanent_risk=data.get("permanent_risk", 0.0),
            description=data.get("description", ""),
            treated=data.get("treated", False),
            worsening_threshold_hours=data.get("worsening_threshold_hours", 48.0),
            time_since_injury=data.get("time_since_injury", 0.0)
        )


class InjurySystem:
    """Manages injury application, tracking, treatment, and healing."""
    
    # Default injury templates by location and severity
    INJURY_TEMPLATES = {
        "leg": {
            "minor": {"Athletics": -1, "Stealth": -1},
            "moderate": {"Athletics": -2, "Stealth": -1, "Reflexes": -1},
            "severe": {"Athletics": -3, "Stealth": -2, "Reflexes": -2},
            "critical": {"Athletics": -4, "Stealth": -3, "Reflexes": -2, "Endurance": -1}
        },
        "arm": {
            "minor": {"Hand-to-Hand Combat": -1, "Firearms": -1},
            "moderate": {"Hand-to-Hand Combat": -2, "Firearms": -2},
            "severe": {"Hand-to-Hand Combat": -3, "Firearms": -3, "Reflexes": -1},
            "critical": {"Hand-to-Hand Combat": -4, "Firearms": -4, "Reflexes": -2}
        },
        "head": {
            "minor": {"Perception": -1, "Logic": -1},
            "moderate": {"Perception": -2, "Logic": -1, "Composure": -1},
            "severe": {"Perception": -3, "Logic": -2, "Composure": -2},
            "critical": {"Perception": -4, "Logic": -3, "Composure": -3, "All": -1}
        },
        "torso": {
            "minor": {"Endurance": -1},
            "moderate": {"Endurance": -2, "Fortitude": -1},
            "severe": {"Endurance": -3, "Fortitude": -2, "Athletics": -1},
            "critical": {"Endurance": -4, "Fortitude": -3, "Athletics": -2, "All": -1}
        },
        "general": {
            "minor": {"All": -1},
            "moderate": {"All": -1, "Endurance": -1},
            "severe": {"All": -2, "Endurance": -2},
            "critical": {"All": -3, "Endurance": -3}
        }
    }
    
    # Healing times by severity (in hours)
    HEALING_TIMES = {
        "minor": 24.0,
        "moderate": 72.0,
        "severe": 168.0,  # 1 week
        "critical": 336.0  # 2 weeks
    }
    
    def __init__(self):
        self.injury_database: Dict[str, dict] = {}
        self.active_injuries: List[Injury] = []
        self.permanent_effects: List[Dict[str, Any]] = []
        self.systemic_collapse_threshold = 3  # Number of injuries before collapse risk
        
    def load_injury_database(self, filepath: str):
        """Load injury templates from JSON file."""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.injury_database = json.load(f)
                print(f"[InjurySystem] Loaded {len(self.injury_database)} injury templates.")
            except Exception as e:
                print(f"[InjurySystem] Error loading injury database: {e}")
        else:
            print(f"[InjurySystem] Injury database not found: {filepath}")
    
    def apply_injury(self, injury_type: str, location: str = None, severity: str = None, 
                     custom_effects: Dict[str, int] = None) -> Injury:
        """
        Apply an injury to the player.
        
        Args:
            injury_type: Type identifier (e.g., "gunshot_leg", "blunt_force")
            location: Body location if not in injury_type
            severity: Severity level if not in injury_type
            custom_effects: Override default effects
            
        Returns:
            The created Injury object
        """
        # Try to load from database first
        if injury_type in self.injury_database:
            template = self.injury_database[injury_type]
            injury = Injury(
                id=f"{injury_type}_{len(self.active_injuries)}",
                name=template["name"],
                location=template["location"],
                severity=template["severity"],
                effects=template["effects"],
                healing_time_hours=template["healing_time_hours"],
                healing_time_remaining=template["healing_time_hours"],
                treatment_required=template.get("treatment_required", False),
                treatment_skill=template.get("treatment_skill", "Medicine"),
                treatment_dc=template.get("treatment_dc", 10),
                equipment_needed=template.get("equipment_needed", []),
                permanent_risk=template.get("permanent_risk", 0.0),
                description=template.get("description", ""),
                worsening_threshold_hours=template.get("worsening_threshold_hours", 48.0)
            )
        else:
            # Generate from defaults
            if not location or not severity:
                raise ValueError("Must provide location and severity if injury_type not in database")
            
            effects = custom_effects or self.INJURY_TEMPLATES.get(location, {}).get(severity, {"All": -1})
            healing_time = self.HEALING_TIMES.get(severity, 24.0)
            
            injury = Injury(
                id=f"{location}_{severity}_{len(self.active_injuries)}",
                name=f"{severity.title()} {location.title()} Injury",
                location=location,
                severity=severity,
                effects=effects,
                healing_time_hours=healing_time,
                healing_time_remaining=healing_time,
                treatment_required=severity in ["severe", "critical"],
                treatment_dc=10 if severity == "severe" else 12,
                permanent_risk=0.1 if severity == "severe" else 0.3 if severity == "critical" else 0.0,
                description=f"A {severity} injury to your {location}."
            )
        
        self.active_injuries.append(injury)
        return injury
    
    def get_total_penalties(self) -> Dict[str, int]:
        """Calculate total skill penalties from all active injuries."""
        penalties: Dict[str, int] = {}
        
        for injury in self.active_injuries:
            for skill, penalty in injury.effects.items():
                if skill == "All":
                    # "All" penalty applies to every skill
                    continue
                penalties[skill] = penalties.get(skill, 0) + penalty
        
        # Handle "All" penalties separately
        all_penalty = sum(inj.effects.get("All", 0) for inj in self.active_injuries)
        
        return penalties, all_penalty
    
    def get_penalty_for_skill(self, skill_name: str) -> int:
        """Get total penalty for a specific skill."""
        penalties, all_penalty = self.get_total_penalties()
        return penalties.get(skill_name, 0) + all_penalty
    
    def advance_time(self, hours: float) -> List[str]:
        """
        Advance healing timers and check for injury worsening.
        
        Returns:
            List of status messages
        """
        messages = []
        healed = []
        
        for injury in self.active_injuries:
            injury.time_since_injury += hours
            
            # Check for worsening if untreated
            if injury.treatment_required and not injury.treated:
                if injury.time_since_injury >= injury.worsening_threshold_hours:
                    messages.append(self._worsen_injury(injury))
            
            # Healing progression (slower if untreated)
            if injury.treated or not injury.treatment_required:
                injury.healing_time_remaining -= hours
                
                if injury.healing_time_remaining <= 0:
                    healed.append(injury)
                    messages.append(f"[RECOVERY] Your '{injury.name}' has healed.")
            else:
                # Untreated injuries heal at 50% rate
                injury.healing_time_remaining -= hours * 0.5
        
        # Remove healed injuries
        for injury in healed:
            self.active_injuries.remove(injury)
        
        return messages
    
    def _worsen_injury(self, injury: Injury) -> str:
        """Worsen an untreated injury."""
        severity_progression = {
            "minor": "moderate",
            "moderate": "severe",
            "severe": "critical"
        }
        
        if injury.severity in severity_progression:
            old_severity = injury.severity
            injury.severity = severity_progression[old_severity]
            
            # Update effects to match new severity
            if injury.location in self.INJURY_TEMPLATES:
                injury.effects = self.INJURY_TEMPLATES[injury.location].get(
                    injury.severity, injury.effects
                )
            
            # Increase healing time
            injury.healing_time_hours *= 1.5
            injury.healing_time_remaining = injury.healing_time_hours
            
            # Reset worsening timer
            injury.time_since_injury = 0.0
            
            return f"[WARNING] Your '{injury.name}' has worsened to {injury.severity} due to lack of treatment!"
        
        return f"[WARNING] Your '{injury.name}' requires immediate treatment!"
    
    def treat_injury(self, injury_id: str, skill_system, inventory_system) -> Dict[str, Any]:
        """
        Attempt to treat an injury with a Medicine check.
        
        Returns:
            Result dictionary with success status and messages
        """
        injury = self._get_injury_by_id(injury_id)
        if not injury:
            return {"success": False, "message": "Injury not found."}
        
        if injury.treated:
            return {"success": False, "message": f"'{injury.name}' has already been treated."}
        
        # Check for required equipment
        for equipment in injury.equipment_needed:
            item = inventory_system.get_item_by_name(equipment)
            if not item:
                return {
                    "success": False, 
                    "message": f"Treatment requires: {', '.join(injury.equipment_needed)}"
                }
        
        # Perform Medicine check
        result = skill_system.roll_check(injury.treatment_skill, injury.treatment_dc)
        
        if result["success"]:
            injury.treated = True
            
            # Consume equipment if limited use
            for equipment in injury.equipment_needed:
                item = inventory_system.get_item_by_name(equipment)
                if item and item.limited_use:
                    item.use()
            
            # Reduce healing time by 25% for successful treatment
            injury.healing_time_remaining *= 0.75
            
            return {
                "success": True,
                "message": f"Successfully treated '{injury.name}'. Healing time reduced.",
                "roll_result": result
            }
        else:
            return {
                "success": False,
                "message": f"Failed to treat '{injury.name}'. The injury remains untreated.",
                "roll_result": result
            }
    
    def check_systemic_collapse(self, skill_system) -> Dict[str, Any]:
        """
        Check if player should suffer systemic collapse from injury overload.
        
        Returns:
            Result dictionary with collapse status and effects
        """
        if len(self.active_injuries) < self.systemic_collapse_threshold:
            return {"collapse": False}
        
        # Calculate DC based on number and severity of injuries
        severity_weights = {"minor": 1, "moderate": 2, "severe": 3, "critical": 4}
        injury_load = sum(severity_weights.get(inj.severity, 1) for inj in self.active_injuries)
        dc = 10 + injury_load
        
        # Fortitude check to resist collapse
        result = skill_system.roll_check("Fortitude", dc)
        
        if result["success"]:
            return {
                "collapse": False,
                "message": "You grit your teeth and push through the pain.",
                "roll_result": result
            }
        else:
            return {
                "collapse": True,
                "message": "Darkness takes you. Your body can't endure any more.",
                "time_lost_hours": 24,
                "roll_result": result
            }
    
    def apply_systemic_collapse(self) -> Dict[str, Any]:
        """
        Apply effects of systemic collapse.
        
        Returns:
            Collapse effects including time lost and location change
        """
        # Treat all injuries to "stabilized" state
        for injury in self.active_injuries:
            injury.treated = True
            injury.healing_time_remaining *= 0.5  # Hospital care speeds recovery
        
        return {
            "time_lost_hours": 24,
            "new_location": "hospital_recovery",
            "sanity_loss": 10,
            "message": "You wake up in a sterile room. The smell of antiseptic is overwhelming."
        }
    
    def _get_injury_by_id(self, injury_id: str) -> Optional[Injury]:
        """Get injury by ID."""
        for injury in self.active_injuries:
            if injury.id == injury_id:
                return injury
        return None
    
    def get_injury_status(self) -> str:
        """Get formatted string of all active injuries."""
        if not self.active_injuries:
            return "No active injuries."
        
        status = "=== ACTIVE INJURIES ===\n"
        for i, injury in enumerate(self.active_injuries, 1):
            treated_str = " [TREATED]" if injury.treated else " [UNTREATED]" if injury.treatment_required else ""
            time_str = f"{injury.healing_time_remaining:.1f}h remaining"
            
            status += f"{i}. {injury.name}{treated_str}\n"
            status += f"   Location: {injury.location.title()} | Severity: {injury.severity.title()}\n"
            status += f"   Effects: {', '.join(f'{k} {v}' for k, v in injury.effects.items())}\n"
            status += f"   Healing: {time_str}\n"
            if injury.description:
                status += f"   {injury.description}\n"
            status += "\n"
        
        return status
    
    def to_dict(self) -> dict:
        """Serialize injury system state."""
        return {
            "active_injuries": [inj.to_dict() for inj in self.active_injuries],
            "permanent_effects": self.permanent_effects,
            "systemic_collapse_threshold": self.systemic_collapse_threshold
        }
    
    def from_dict(self, data: dict):
        """Restore injury system state."""
        self.active_injuries = [Injury.from_dict(inj) for inj in data.get("active_injuries", [])]
        self.permanent_effects = data.get("permanent_effects", [])
        self.systemic_collapse_threshold = data.get("systemic_collapse_threshold", 3)
