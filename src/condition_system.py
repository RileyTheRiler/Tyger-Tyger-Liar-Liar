"""
Condition System - Manages injuries and conditions with treatment options.
Conditions impose mechanical penalties and can worsen without treatment.
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class ConditionCategory(Enum):
    PHYSICAL = "physical"
    MENTAL = "mental"
    SUPERNATURAL = "supernatural"
    ENVIRONMENTAL = "environmental"


class ConditionSeverity(Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


@dataclass
class TreatmentOption:
    """A way to treat a condition."""
    id: str
    description: str
    requires_item: Optional[str] = None
    requires_skill: Optional[str] = None
    requires_skill_dc: int = 9
    requires_npc: Optional[str] = None
    time_cost_minutes: int = 30
    healing_reduction_hours: float = 0
    removes_immediately: bool = False
    side_effects: List[str] = field(default_factory=list)


@dataclass
class MechanicalPenalties:
    """Penalties applied while a condition is active."""
    skill_modifiers: Dict[str, int] = field(default_factory=dict)
    attribute_modifiers: Dict[str, int] = field(default_factory=dict)
    max_sanity_modifier: int = 0
    max_reality_modifier: int = 0
    movement_penalty: float = 1.0  # Multiplier on travel time
    attention_multiplier: float = 1.0  # Multiplier on attention gain


class Condition:
    """An injury or condition affecting the player."""

    def __init__(self, data: dict):
        self.id = data["id"]
        self.name = data["name"]
        self.description = data.get("description", {"base": ""})
        self.category = ConditionCategory(data.get("category", "physical"))
        self.severity = ConditionSeverity(data.get("severity", "minor"))

        # Parse mechanical penalties
        penalties_data = data.get("mechanical_penalties", {})
        self.penalties = MechanicalPenalties(
            skill_modifiers=penalties_data.get("skill_modifiers", {}),
            attribute_modifiers=penalties_data.get("attribute_modifiers", {}),
            max_sanity_modifier=penalties_data.get("max_sanity_modifier", 0),
            max_reality_modifier=penalties_data.get("max_reality_modifier", 0),
            movement_penalty=penalties_data.get("movement_penalty", 1.0),
            attention_multiplier=penalties_data.get("attention_multiplier", 1.0)
        )

        # Parse healing options
        healing_data = data.get("healing", {})
        self.natural_healing_hours = healing_data.get("natural_healing_hours", 0)

        self.treatment_options: List[TreatmentOption] = []
        for t in healing_data.get("treatment_options", []):
            self.treatment_options.append(TreatmentOption(
                id=t["id"],
                description=t["description"],
                requires_item=t.get("requires_item"),
                requires_skill=t.get("requires_skill", {}).get("skill"),
                requires_skill_dc=t.get("requires_skill", {}).get("dc", 9),
                requires_npc=t.get("requires_npc"),
                time_cost_minutes=t.get("time_cost_minutes", 30),
                healing_reduction_hours=t.get("healing_reduction_hours", 0),
                removes_immediately=t.get("removes_immediately", False),
                side_effects=t.get("side_effects", [])
            ))

        # Worsening mechanics
        worsens = healing_data.get("worsens_without_treatment", {})
        self.hours_until_worse = worsens.get("hours_until_worse", 0)
        self.becomes_condition = worsens.get("becomes_condition")

        # Stacking
        self.stacks = data.get("stacks", False)
        self.max_stacks = data.get("max_stacks", 1)

        self.visible_to_player = data.get("visible_to_player", True)

        # Narrative effects
        self.scene_inserts = data.get("narrative_effects", {}).get("scene_inserts", [])
        self.dialogue_modifiers = data.get("narrative_effects", {}).get("dialogue_modifiers", [])

    def get_description(self, lens: str = "neutral") -> str:
        """Get condition description for current lens."""
        if isinstance(self.description, dict):
            if lens in self.description.get("lens", {}):
                return self.description["lens"][lens]
            return self.description.get("base", "")
        return str(self.description)

    def get_severity_value(self) -> int:
        """Get numeric severity for comparisons."""
        severity_values = {
            ConditionSeverity.MINOR: 1,
            ConditionSeverity.MODERATE: 2,
            ConditionSeverity.SEVERE: 3,
            ConditionSeverity.CRITICAL: 4
        }
        return severity_values.get(self.severity, 1)


class ActiveCondition:
    """An instance of a condition affecting the player."""

    def __init__(self, condition: Condition, stacks: int = 1):
        self.condition = condition
        self.stacks = stacks
        self.time_remaining_minutes = condition.natural_healing_hours * 60
        self.time_without_treatment_minutes = 0
        self.treated = False

    def update_time(self, minutes: int) -> dict:
        """
        Update condition timers. Returns dict with events.
        """
        result = {
            "healed": False,
            "worsened": False,
            "becomes": None
        }

        if self.condition.natural_healing_hours > 0:
            self.time_remaining_minutes -= minutes
            if self.time_remaining_minutes <= 0:
                result["healed"] = True
                return result

        # Check for worsening
        if not self.treated and self.condition.hours_until_worse > 0:
            self.time_without_treatment_minutes += minutes
            hours_without = self.time_without_treatment_minutes / 60.0

            if hours_without >= self.condition.hours_until_worse:
                if self.condition.becomes_condition:
                    result["worsened"] = True
                    result["becomes"] = self.condition.becomes_condition

        return result

    def apply_treatment(self, treatment: TreatmentOption) -> dict:
        """
        Apply a treatment option.
        Returns dict with results including side effects.
        """
        result = {
            "success": True,
            "removed": False,
            "side_effects": []
        }

        self.treated = True
        self.time_without_treatment_minutes = 0

        if treatment.removes_immediately:
            result["removed"] = True
        elif treatment.healing_reduction_hours > 0:
            self.time_remaining_minutes -= treatment.healing_reduction_hours * 60

            if self.time_remaining_minutes <= 0:
                result["removed"] = True

        result["side_effects"] = treatment.side_effects

        return result

    def get_effective_penalties(self) -> MechanicalPenalties:
        """Get penalties multiplied by stacks if applicable."""
        base = self.condition.penalties

        if not self.condition.stacks or self.stacks == 1:
            return base

        # Stack skill modifiers
        stacked_skills = {k: v * self.stacks for k, v in base.skill_modifiers.items()}
        stacked_attrs = {k: v * self.stacks for k, v in base.attribute_modifiers.items()}

        return MechanicalPenalties(
            skill_modifiers=stacked_skills,
            attribute_modifiers=stacked_attrs,
            max_sanity_modifier=base.max_sanity_modifier * self.stacks,
            max_reality_modifier=base.max_reality_modifier * self.stacks,
            movement_penalty=base.movement_penalty ** self.stacks,
            attention_multiplier=base.attention_multiplier * self.stacks
        )

    def to_dict(self) -> dict:
        """Serialize for saving."""
        return {
            "condition_id": self.condition.id,
            "stacks": self.stacks,
            "time_remaining_minutes": self.time_remaining_minutes,
            "time_without_treatment_minutes": self.time_without_treatment_minutes,
            "treated": self.treated
        }


class ConditionSystem:
    """Manages all conditions and their effects on the player."""

    def __init__(self, conditions_dir: str = None):
        self.condition_definitions: Dict[str, Condition] = {}
        self.active_conditions: Dict[str, ActiveCondition] = {}

        if conditions_dir:
            self.load_conditions(conditions_dir)
        else:
            self._load_default_conditions()

    def _load_default_conditions(self):
        """Load built-in default conditions."""
        defaults = [
            {
                "id": "cond_hypothermia_mild",
                "name": "Mild Hypothermia",
                "description": {
                    "base": "Your core temperature is dropping. Shivers wrack your body.",
                    "lens": {
                        "believer": "The cold feels alive, hungry, reaching into your bones.",
                        "skeptic": "Classic Stage 1 hypothermia. You need warmth, now.",
                        "haunted": "The cold reminds you of something. Someone's touch."
                    }
                },
                "category": "environmental",
                "severity": "moderate",
                "mechanical_penalties": {
                    "skill_modifiers": {
                        "Athletics": -1,
                        "Firearms": -1,
                        "Hand-to-Hand Combat": -1,
                        "Reflexes": -1
                    },
                    "movement_penalty": 1.25
                },
                "healing": {
                    "natural_healing_hours": 2,
                    "treatment_options": [
                        {
                            "id": "warm_shelter",
                            "description": "Rest in a heated shelter",
                            "time_cost_minutes": 60,
                            "removes_immediately": True
                        },
                        {
                            "id": "hot_drink",
                            "description": "Drink something warm",
                            "requires_item": "item_hot_beverage",
                            "time_cost_minutes": 15,
                            "healing_reduction_hours": 1
                        }
                    ],
                    "worsens_without_treatment": {
                        "hours_until_worse": 3,
                        "becomes_condition": "cond_hypothermia_severe"
                    }
                }
            },
            {
                "id": "cond_hypothermia_severe",
                "name": "Severe Hypothermia",
                "description": {
                    "base": "Your movements are sluggish. Thinking is difficult. Everything is so cold.",
                    "lens": {
                        "believer": "The entity's touch. It's draining your life heat.",
                        "skeptic": "Stage 2-3 hypothermia. You're in serious danger.",
                        "haunted": "This is how it felt to drown. You remember now."
                    }
                },
                "category": "environmental",
                "severity": "severe",
                "mechanical_penalties": {
                    "skill_modifiers": {
                        "Athletics": -2,
                        "Firearms": -2,
                        "Hand-to-Hand Combat": -2,
                        "Reflexes": -2,
                        "Logic": -1,
                        "Research": -1
                    },
                    "max_sanity_modifier": -10,
                    "movement_penalty": 1.5
                },
                "healing": {
                    "natural_healing_hours": 0,
                    "treatment_options": [
                        {
                            "id": "medical_treatment",
                            "description": "Medical treatment required",
                            "requires_skill": {"skill": "Medicine", "dc": 11},
                            "time_cost_minutes": 120,
                            "removes_immediately": True
                        },
                        {
                            "id": "npc_doctor",
                            "description": "Seek help from the town doctor",
                            "requires_npc": "npc_doctor_hansen",
                            "time_cost_minutes": 90,
                            "removes_immediately": True
                        }
                    ],
                    "worsens_without_treatment": {
                        "hours_until_worse": 1,
                        "becomes_condition": "cond_hypothermia_lethal"
                    }
                }
            },
            {
                "id": "cond_sprained_ankle",
                "name": "Sprained Ankle",
                "description": {
                    "base": "Sharp pain lances through your ankle with every step.",
                    "lens": {
                        "believer": "Something tripped you. Something deliberate.",
                        "skeptic": "A minor injury, but it will slow you down.",
                        "haunted": "You've been here before. Running. Falling."
                    }
                },
                "category": "physical",
                "severity": "minor",
                "mechanical_penalties": {
                    "skill_modifiers": {
                        "Athletics": -2,
                        "Stealth": -1
                    },
                    "movement_penalty": 1.5
                },
                "healing": {
                    "natural_healing_hours": 24,
                    "treatment_options": [
                        {
                            "id": "bandage",
                            "description": "Wrap the ankle with bandages",
                            "requires_item": "item_bandages",
                            "time_cost_minutes": 10,
                            "healing_reduction_hours": 12
                        },
                        {
                            "id": "rest",
                            "description": "Rest and stay off it",
                            "time_cost_minutes": 240,
                            "healing_reduction_hours": 18
                        }
                    ]
                }
            },
            {
                "id": "cond_concussion",
                "name": "Concussion",
                "description": {
                    "base": "Your head pounds. Light and sound are unbearable.",
                    "lens": {
                        "believer": "The visions started after the blow. Are they visions?",
                        "skeptic": "Mild traumatic brain injury. You need rest.",
                        "haunted": "The ringing in your ears sounds like screaming."
                    }
                },
                "category": "physical",
                "severity": "moderate",
                "mechanical_penalties": {
                    "skill_modifiers": {
                        "Logic": -2,
                        "Research": -2,
                        "Perception": -2,
                        "Pattern Recognition": -1
                    },
                    "max_sanity_modifier": -5,
                    "attention_multiplier": 1.25
                },
                "healing": {
                    "natural_healing_hours": 48,
                    "treatment_options": [
                        {
                            "id": "rest_dark",
                            "description": "Rest in a dark, quiet room",
                            "time_cost_minutes": 360,
                            "healing_reduction_hours": 24
                        },
                        {
                            "id": "painkillers",
                            "description": "Take painkillers",
                            "requires_item": "item_painkillers",
                            "time_cost_minutes": 15,
                            "healing_reduction_hours": 6,
                            "side_effects": ["cond_drowsy"]
                        }
                    ]
                }
            },
            {
                "id": "cond_drowsy",
                "name": "Drowsy",
                "description": {"base": "Your eyelids are heavy. Focus is difficult."},
                "category": "physical",
                "severity": "minor",
                "mechanical_penalties": {
                    "skill_modifiers": {
                        "Perception": -1,
                        "Reflexes": -1
                    }
                },
                "healing": {"natural_healing_hours": 4}
            },
            {
                "id": "cond_frostbite_fingers",
                "name": "Frostbitten Fingers",
                "description": {
                    "base": "Your fingertips are white and numb. Fine motor control is compromised.",
                    "lens": {
                        "believer": "The cold has marked you. Claimed a piece.",
                        "skeptic": "Superficial frostbite. Treatable if caught in time.",
                        "haunted": "You've lost sensation before. The numbness is familiar."
                    }
                },
                "category": "environmental",
                "severity": "moderate",
                "mechanical_penalties": {
                    "skill_modifiers": {
                        "Firearms": -2,
                        "Technology": -1,
                        "Forensics": -1
                    }
                },
                "healing": {
                    "natural_healing_hours": 72,
                    "treatment_options": [
                        {
                            "id": "warm_water",
                            "description": "Soak in warm (not hot) water",
                            "time_cost_minutes": 45,
                            "healing_reduction_hours": 48
                        }
                    ],
                    "worsens_without_treatment": {
                        "hours_until_worse": 12,
                        "becomes_condition": "cond_frostbite_severe"
                    }
                }
            },
            {
                "id": "cond_paranoid",
                "name": "Paranoid",
                "description": {
                    "base": "Everyone is watching. Everyone is suspect.",
                    "lens": {
                        "believer": "Your senses are heightened. You can feel the entity's attention.",
                        "skeptic": "Stress-induced paranoia. You need to ground yourself.",
                        "haunted": "They're all looking at you the way they looked at you before."
                    }
                },
                "category": "mental",
                "severity": "minor",
                "mechanical_penalties": {
                    "skill_modifiers": {
                        "Charm": -2,
                        "Empathy": -1,
                        "Perception": 1  # Bonus!
                    },
                    "attention_multiplier": 1.2
                },
                "healing": {"natural_healing_hours": 8}
            },
            {
                "id": "cond_shaken",
                "name": "Shaken",
                "description": {"base": "Your hands won't stop trembling."},
                "category": "mental",
                "severity": "minor",
                "mechanical_penalties": {
                    "skill_modifiers": {
                        "Composure": -2,
                        "Firearms": -1
                    }
                },
                "healing": {"natural_healing_hours": 2}
            }
        ]

        for cond_data in defaults:
            self.condition_definitions[cond_data["id"]] = Condition(cond_data)

    def load_conditions(self, conditions_dir: str):
        """Load condition definitions from a directory."""
        if not os.path.exists(conditions_dir):
            self._load_default_conditions()
            return

        for filename in os.listdir(conditions_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(conditions_dir, filename), 'r') as f:
                        data = json.load(f)

                    conditions = data if isinstance(data, list) else [data]
                    for cond_data in conditions:
                        cond = Condition(cond_data)
                        self.condition_definitions[cond.id] = cond
                except Exception as e:
                    print(f"Error loading condition from {filename}: {e}")

    def get_condition_definition(self, condition_id: str) -> Optional[Condition]:
        """Get a condition definition by ID."""
        return self.condition_definitions.get(condition_id)

    def add_condition(self, condition_id: str) -> Optional[ActiveCondition]:
        """Add a condition to the player. Returns the active condition."""
        cond_def = self.get_condition_definition(condition_id)
        if not cond_def:
            print(f"[CONDITION] Unknown condition: {condition_id}")
            return None

        if condition_id in self.active_conditions:
            active = self.active_conditions[condition_id]
            if cond_def.stacks and active.stacks < cond_def.max_stacks:
                active.stacks += 1
                print(f"[CONDITION] {cond_def.name} stacks increased to {active.stacks}")
                return active
            else:
                print(f"[CONDITION] Already have {cond_def.name}")
                return active

        active = ActiveCondition(cond_def)
        self.active_conditions[condition_id] = active
        print(f"[CONDITION] Acquired: {cond_def.name}")
        return active

    def remove_condition(self, condition_id: str) -> bool:
        """Remove a condition from the player."""
        if condition_id in self.active_conditions:
            cond = self.active_conditions[condition_id]
            del self.active_conditions[condition_id]
            print(f"[CONDITION] Recovered from: {cond.condition.name}")
            return True
        return False

    def has_condition(self, condition_id: str) -> bool:
        """Check if player has a specific condition."""
        return condition_id in self.active_conditions

    def get_active_condition(self, condition_id: str) -> Optional[ActiveCondition]:
        """Get an active condition by ID."""
        return self.active_conditions.get(condition_id)

    def update_time(self, minutes: int) -> List[dict]:
        """
        Update all condition timers.
        Returns list of events (healed, worsened).
        """
        events = []
        to_remove = []
        to_add = []

        for cond_id, active in self.active_conditions.items():
            result = active.update_time(minutes)

            if result["healed"]:
                events.append({
                    "type": "healed",
                    "condition_id": cond_id,
                    "condition_name": active.condition.name
                })
                to_remove.append(cond_id)

            if result["worsened"]:
                events.append({
                    "type": "worsened",
                    "condition_id": cond_id,
                    "condition_name": active.condition.name,
                    "becomes": result["becomes"]
                })
                to_remove.append(cond_id)
                if result["becomes"]:
                    to_add.append(result["becomes"])

        for cond_id in to_remove:
            del self.active_conditions[cond_id]

        for cond_id in to_add:
            self.add_condition(cond_id)

        return events

    def get_available_treatments(self, condition_id: str, inventory: List[str] = None,
                                  available_npcs: List[str] = None) -> List[TreatmentOption]:
        """Get treatments available given current resources."""
        active = self.get_active_condition(condition_id)
        if not active:
            return []

        inventory = inventory or []
        npcs = available_npcs or []

        available = []
        for treatment in active.condition.treatment_options:
            can_use = True

            if treatment.requires_item and treatment.requires_item not in inventory:
                can_use = False
            if treatment.requires_npc and treatment.requires_npc not in npcs:
                can_use = False

            if can_use:
                available.append(treatment)

        return available

    def apply_treatment(self, condition_id: str, treatment_id: str) -> dict:
        """
        Apply a treatment to a condition.
        Returns dict with results.
        """
        active = self.get_active_condition(condition_id)
        if not active:
            return {"success": False, "error": "Condition not found"}

        treatment = None
        for t in active.condition.treatment_options:
            if t.id == treatment_id:
                treatment = t
                break

        if not treatment:
            return {"success": False, "error": "Treatment not found"}

        result = active.apply_treatment(treatment)

        if result["removed"]:
            self.remove_condition(condition_id)

        # Handle side effects
        for side_effect_id in result.get("side_effects", []):
            self.add_condition(side_effect_id)

        return result

    def get_total_penalties(self) -> MechanicalPenalties:
        """Get combined penalties from all active conditions."""
        combined = MechanicalPenalties()

        for active in self.active_conditions.values():
            penalties = active.get_effective_penalties()

            # Combine skill modifiers
            for skill, mod in penalties.skill_modifiers.items():
                combined.skill_modifiers[skill] = combined.skill_modifiers.get(skill, 0) + mod

            # Combine attribute modifiers
            for attr, mod in penalties.attribute_modifiers.items():
                combined.attribute_modifiers[attr] = combined.attribute_modifiers.get(attr, 0) + mod

            combined.max_sanity_modifier += penalties.max_sanity_modifier
            combined.max_reality_modifier += penalties.max_reality_modifier
            combined.movement_penalty *= penalties.movement_penalty
            combined.attention_multiplier *= penalties.attention_multiplier

        return combined

    def get_skill_modifier(self, skill_name: str) -> int:
        """Get total skill modifier from all conditions."""
        penalties = self.get_total_penalties()
        return penalties.skill_modifiers.get(skill_name, 0)

    def get_conditions_summary(self) -> List[dict]:
        """Get a summary of all active conditions."""
        summary = []
        for cond_id, active in self.active_conditions.items():
            cond = active.condition
            summary.append({
                "id": cond_id,
                "name": cond.name,
                "severity": cond.severity.value,
                "category": cond.category.value,
                "stacks": active.stacks,
                "time_remaining_hours": active.time_remaining_minutes / 60.0 if active.time_remaining_minutes > 0 else None,
                "treated": active.treated,
                "visible": cond.visible_to_player
            })
        return summary

    def to_dict(self) -> dict:
        """Serialize all active conditions for saving."""
        return {cond_id: active.to_dict() for cond_id, active in self.active_conditions.items()}

    def restore_state(self, state: dict):
        """Restore active conditions from saved data."""
        self.active_conditions.clear()

        for cond_id, active_data in state.items():
            cond_def = self.get_condition_definition(active_data["condition_id"])
            if cond_def:
                active = ActiveCondition(cond_def, active_data.get("stacks", 1))
                active.time_remaining_minutes = active_data.get("time_remaining_minutes", 0)
                active.time_without_treatment_minutes = active_data.get("time_without_treatment_minutes", 0)
                active.treated = active_data.get("treated", False)
                self.active_conditions[cond_id] = active


if __name__ == "__main__":
    # Test condition system
    system = ConditionSystem()

    print("Available conditions:")
    for cond_id in system.condition_definitions:
        cond = system.condition_definitions[cond_id]
        print(f"  - {cond.name} ({cond.severity.value})")

    print("\nAdding mild hypothermia...")
    system.add_condition("cond_hypothermia_mild")

    print("\nActive conditions:")
    for summary in system.get_conditions_summary():
        print(f"  - {summary['name']}: {summary['severity']}")

    print("\nTotal penalties:")
    penalties = system.get_total_penalties()
    print(f"  Skill mods: {penalties.skill_modifiers}")
    print(f"  Movement penalty: {penalties.movement_penalty}x")

    print("\nSimulating 4 hours without treatment...")
    events = system.update_time(240)
    for event in events:
        print(f"  Event: {event}")

    print("\nActive conditions after time:")
    for summary in system.get_conditions_summary():
        print(f"  - {summary['name']}: {summary['severity']}")
