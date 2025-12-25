"""
Population System - Tracks the town population (starts at 347).
Population decrements are permanent, visible, and consequential.
The number 347 has thematic significance.
"""

from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class PopulationEventType(Enum):
    DEATH = "death"
    DISAPPEARANCE = "disappearance"
    EVACUATION = "evacuation"
    ARRIVAL = "arrival"  # Rare - outsiders arriving


@dataclass
class PopulationEvent:
    """A recorded change in population."""
    event_type: PopulationEventType
    count: int
    description: str
    day: int
    npc_id: Optional[str] = None  # If event involves specific NPC
    location_id: Optional[str] = None
    is_correction: bool = False  # True if population was wrong and corrected


@dataclass
class PopulationThreshold:
    """A threshold that triggers effects when population drops below it."""
    population: int
    name: str
    description: str
    triggered: bool = False
    effects: Dict = field(default_factory=dict)


class PopulationSystem:
    """
    Tracks and manages the town population.
    Starting population: 347 (significant number per Canon & Constraints).
    """

    INITIAL_POPULATION = 347

    def __init__(self, initial_population: int = None):
        self.population = initial_population or self.INITIAL_POPULATION
        self.initial_population = self.population
        self.events: List[PopulationEvent] = []
        self.corrections: List[PopulationEvent] = []
        self.current_day = 1

        # Thresholds that trigger narrative/mechanical effects
        self.thresholds: List[PopulationThreshold] = [
            PopulationThreshold(
                population=340,
                name="First Week",
                description="The losses are noticeable now. Faces missing from the diner.",
                effects={"attention_base_increase": 5, "npc_tension_increase": 10}
            ),
            PopulationThreshold(
                population=320,
                name="Growing Concern",
                description="The town is holding its breath. Fear spreads.",
                effects={"attention_base_increase": 10, "storm_frequency_increase": 0.1}
            ),
            PopulationThreshold(
                population=300,
                name="Critical Mass",
                description="Everyone knows someone who's gone. The town is fracturing.",
                effects={"npc_availability_decrease": True, "trust_decay_rate": 0.5}
            ),
            PopulationThreshold(
                population=275,
                name="Exodus Pressure",
                description="Some want to leave. Others won't let them.",
                effects={"evacuation_dialogue_available": True}
            ),
            PopulationThreshold(
                population=250,
                name="Half Gone",
                description="More than a quarter of the town... gone. The silence is deafening.",
                effects={"attention_base_increase": 20, "entity_manifestation_chance": 0.15}
            ),
            PopulationThreshold(
                population=200,
                name="Skeleton Crew",
                description="The town feels empty. Only the determined—or trapped—remain.",
                effects={"reduced_services": True, "npc_paranoia_increase": 25}
            ),
            PopulationThreshold(
                population=100,
                name="Ghost Town",
                description="Kaltvik is dying. Perhaps it's already dead.",
                effects={"endgame_proximity": True}
            ),
            PopulationThreshold(
                population=47,
                name="The Remnant",
                description="47 souls. The number echoes. 347... 47...",
                effects={"resonance_revelation": True}
            )
        ]

        # Week 16: The 347 Rule - Population equilibrium mechanics
        self.target_population = 347  # Immutable target
        self.player_counted = False  # Set to True when player enters town
        self.hours_off_target = 0.0  # Tracks how long population != 347
        self.resonance_violation_threshold = 24  # Hours before Entity reacts
        self.last_subtraction_day = 0  # Track when last subtraction occurred

        # Listeners for population changes
        self._listeners: List[Callable[[PopulationEvent], None]] = []

    def add_listener(self, listener: Callable[[PopulationEvent], None]):
        """Add a listener for population change events."""
        self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[PopulationEvent], None]):
        """Remove a listener."""
        if listener in self._listeners:
            self._listeners.remove(listener)

    def _notify_listeners(self, event: PopulationEvent):
        """Notify all listeners of a population change."""
        for listener in self._listeners:
            try:
                listener(event)
            except Exception as e:
                print(f"[POPULATION] Listener error: {e}")

    def record_death(self, description: str, npc_id: str = None,
                     location_id: str = None, count: int = 1) -> PopulationEvent:
        """Record a death event and decrease population."""
        event = PopulationEvent(
            event_type=PopulationEventType.DEATH,
            count=count,
            description=description,
            day=self.current_day,
            npc_id=npc_id,
            location_id=location_id
        )

        self.population -= count
        self.events.append(event)
        self._check_thresholds()
        self._notify_listeners(event)

        print(f"[POPULATION] Death recorded: {description}")
        print(f"[POPULATION] Current: {self.population}/{self.initial_population}")

        return event

    def record_disappearance(self, description: str, npc_id: str = None,
                             location_id: str = None, count: int = 1) -> PopulationEvent:
        """Record a disappearance event. Missing presumed... something."""
        event = PopulationEvent(
            event_type=PopulationEventType.DISAPPEARANCE,
            count=count,
            description=description,
            day=self.current_day,
            npc_id=npc_id,
            location_id=location_id
        )

        self.population -= count
        self.events.append(event)
        self._check_thresholds()
        self._notify_listeners(event)

        print(f"[POPULATION] Disappearance recorded: {description}")
        print(f"[POPULATION] Current: {self.population}/{self.initial_population}")

        return event

    def record_evacuation(self, description: str, count: int = 1) -> PopulationEvent:
        """Record people leaving town (if allowed/possible)."""
        event = PopulationEvent(
            event_type=PopulationEventType.EVACUATION,
            count=count,
            description=description,
            day=self.current_day
        )

        self.population -= count
        self.events.append(event)
        self._check_thresholds()
        self._notify_listeners(event)

        print(f"[POPULATION] Evacuation recorded: {description}")
        print(f"[POPULATION] Current: {self.population}/{self.initial_population}")

        return event

    def record_correction(self, description: str, actual_population: int) -> PopulationEvent:
        """
        Record a population correction (discovering the count was wrong).
        This represents narrative reveals, not retroactive changes.
        """
        diff = actual_population - self.population

        event = PopulationEvent(
            event_type=PopulationEventType.DISAPPEARANCE if diff < 0 else PopulationEventType.ARRIVAL,
            count=abs(diff),
            description=description,
            day=self.current_day,
            is_correction=True
        )

        old_pop = self.population
        self.population = actual_population
        self.corrections.append(event)
        self._check_thresholds()
        self._notify_listeners(event)

        print(f"[POPULATION] Correction: {old_pop} -> {actual_population}")
        print(f"[POPULATION] {description}")

        return event

    def _check_thresholds(self) -> List[PopulationThreshold]:
        """Check and trigger any newly crossed thresholds."""
        triggered = []

        for threshold in self.thresholds:
            if not threshold.triggered and self.population <= threshold.population:
                threshold.triggered = True
                triggered.append(threshold)
                print(f"[POPULATION THRESHOLD] {threshold.name}: {threshold.description}")

        return triggered

    def get_triggered_thresholds(self) -> List[PopulationThreshold]:
        """Get all thresholds that have been triggered."""
        return [t for t in self.thresholds if t.triggered]

    def get_next_threshold(self) -> Optional[PopulationThreshold]:
        """Get the next threshold that will be triggered."""
        for threshold in self.thresholds:
            if not threshold.triggered:
                return threshold
        return None

    def get_population_status(self) -> dict:
        """Get current population status."""
        losses = self.initial_population - self.population
        loss_percent = (losses / self.initial_population) * 100

        return {
            "current": self.population,
            "initial": self.initial_population,
            "losses": losses,
            "loss_percent": round(loss_percent, 1),
            "deaths": len([e for e in self.events if e.event_type == PopulationEventType.DEATH]),
            "disappearances": len([e for e in self.events if e.event_type == PopulationEventType.DISAPPEARANCE]),
            "evacuations": len([e for e in self.events if e.event_type == PopulationEventType.EVACUATION]),
            "thresholds_triggered": len(self.get_triggered_thresholds()),
            "next_threshold": self.get_next_threshold().population if self.get_next_threshold() else None
        }

    def get_events_by_day(self, day: int) -> List[PopulationEvent]:
        """Get all population events for a specific day."""
        return [e for e in self.events if e.day == day]

    def get_events_by_type(self, event_type: PopulationEventType) -> List[PopulationEvent]:
        """Get all events of a specific type."""
        return [e for e in self.events if e.event_type == event_type]

    def get_events_for_npc(self, npc_id: str) -> List[PopulationEvent]:
        """Get all events involving a specific NPC."""
        return [e for e in self.events if e.npc_id == npc_id]

    def get_events_at_location(self, location_id: str) -> List[PopulationEvent]:
        """Get all events at a specific location."""
        return [e for e in self.events if e.location_id == location_id]

    # Week 16: The 347 Rule Methods
    
    def on_player_arrival(self, npc_system=None) -> Optional[PopulationEvent]:
        """
        Called when player enters Kaltvik for the first time.
        Triggers automatic subtraction to maintain 347 population.
        """
        if self.player_counted:
            return None  # Already handled
        
        self.player_counted = True
        
        # Player is the 348th person - someone must go
        if npc_system and self.population >= self.target_population:
            return self.enforce_347_rule(npc_system)
        
        return None
    
    def enforce_347_rule(self, npc_system) -> Optional[PopulationEvent]:
        """
        Enforces the 347 Rule by removing an NPC if population > 347.
        Returns the subtraction event.
        """
        if self.population <= self.target_population:
            return None
        
        # Get candidates for subtraction
        candidates = self.get_subtraction_candidates(npc_system)
        
        if not candidates:
            print("[347 RULE] No valid subtraction candidates found")
            return None
        
        # Select a candidate (weighted by importance - less important = more likely)
        import random
        weights = [1.0 / max(c.get("importance", 1), 1) for c in candidates]
        selected = random.choices(candidates, weights=weights, k=1)[0]
        
        # Record the disappearance
        description = selected.get("disappearance_text", 
                                  f"{selected['name']} has left town. No one saw them go.")
        
        event = self.record_disappearance(
            description=description,
            npc_id=selected["id"],
            count=1
        )
        
        # Mark NPC as unavailable in NPC system
        npc = npc_system.get_npc(selected["id"])
        if npc:
            npc.flags["alive"] = False
            npc.flags["subtracted_by_347"] = True
        
        self.last_subtraction_day = self.current_day
        
        return event
    
    def get_subtraction_candidates(self, npc_system) -> List[Dict]:
        """
        Returns list of NPCs that can be removed to maintain 347.
        Excludes critical NPCs and those already gone.
        """
        candidates = []
        
        for npc_id, npc in npc_system.npcs.items():
            # Skip if already dead/gone
            if not npc.flags.get("alive", True):
                continue
            
            # Skip if critical for endings
            if npc.critical_for:
                continue
            
            # Skip if player has high trust (>= 70)
            if npc.trust >= 70:
                continue
            
            candidates.append({
                "id": npc.id,
                "name": npc.name,
                "importance": len(npc.critical_for) + 1,  # Higher = more important
                "trust": npc.trust,
                "disappearance_text": f"{npc.name} is gone. Their house is empty."
            })
        
        return candidates
    
    def check_resonance_violation(self) -> Dict:
        """
        Checks if population has been off-target for too long.
        Returns dict with violation status and recommended actions.
        """
        is_off_target = self.population != self.target_population
        
        result = {
            "is_violation": False,
            "hours_off_target": self.hours_off_target,
            "threshold": self.resonance_violation_threshold,
            "actions": []
        }
        
        if is_off_target and self.hours_off_target >= self.resonance_violation_threshold:
            result["is_violation"] = True
            
            if self.population > self.target_population:
                result["actions"].append({
                    "type": "integration_spike",
                    "attention_gain": 20,
                    "description": "The aurora pulses. You feel a pressure in your skull."
                })
                result["actions"].append({
                    "type": "forced_subtraction",
                    "description": "Someone screams in the distance. Then silence."
                })
            else:  # Population < 347
                result["actions"].append({
                    "type": "entity_agitation",
                    "attention_gain": 15,
                    "description": "The lights are restless tonight. Searching."
                })
        
        return result


    def advance_day(self, new_day: int = None):
        """Advance to a new day."""
        if new_day:
            self.current_day = new_day
        else:
            self.current_day += 1

    def get_accumulated_effects(self) -> dict:
        """Get all accumulated effects from triggered thresholds."""
        effects = {}

        for threshold in self.get_triggered_thresholds():
            for key, value in threshold.effects.items():
                if isinstance(value, bool):
                    effects[key] = value
                elif isinstance(value, (int, float)):
                    effects[key] = effects.get(key, 0) + value
                else:
                    effects[key] = value

        return effects

    def to_dict(self) -> dict:
        """Serialize population state for saving."""
        return {
            "population": self.population,
            "initial_population": self.initial_population,
            "current_day": self.current_day,
            "events": [
                {
                    "event_type": e.event_type.value,
                    "count": e.count,
                    "description": e.description,
                    "day": e.day,
                    "npc_id": e.npc_id,
                    "location_id": e.location_id,
                    "is_correction": e.is_correction
                }
                for e in self.events
            ],
            "thresholds_triggered": [t.population for t in self.thresholds if t.triggered],
            # Week 16 fields
            "player_counted": self.player_counted,
            "hours_off_target": self.hours_off_target,
            "last_subtraction_day": self.last_subtraction_day
        }

    def restore_state(self, state: dict):
        """Restore population state from saved data."""
        self.population = state.get("population", self.INITIAL_POPULATION)
        self.initial_population = state.get("initial_population", self.INITIAL_POPULATION)
        self.current_day = state.get("current_day", 1)

        self.events.clear()
        for e_data in state.get("events", []):
            event = PopulationEvent(
                event_type=PopulationEventType(e_data["event_type"]),
                count=e_data["count"],
                description=e_data["description"],
                day=e_data["day"],
                npc_id=e_data.get("npc_id"),
                location_id=e_data.get("location_id"),
                is_correction=e_data.get("is_correction", False)
            )
            self.events.append(event)

        triggered_pops = state.get("thresholds_triggered", [])
        for threshold in self.thresholds:
            threshold.triggered = threshold.population in triggered_pops
        
        # Week 16 fields
        self.player_counted = state.get("player_counted", False)
        self.hours_off_target = state.get("hours_off_target", 0.0)
        self.last_subtraction_day = state.get("last_subtraction_day", 0)


class PopulationDisplay:
    """UI helper for displaying population information."""

    @staticmethod
    def format_status(system: PopulationSystem) -> str:
        """Format population status for display."""
        status = system.get_population_status()

        lines = [
            f"KALTVIK POPULATION: {status['current']}/{status['initial']}",
            f"Losses: {status['losses']} ({status['loss_percent']}%)",
            ""
        ]

        if status['deaths'] > 0:
            lines.append(f"  Deaths: {status['deaths']}")
        if status['disappearances'] > 0:
            lines.append(f"  Missing: {status['disappearances']}")
        if status['evacuations'] > 0:
            lines.append(f"  Evacuated: {status['evacuations']}")

        next_threshold = status['next_threshold']
        if next_threshold:
            until_next = status['current'] - next_threshold
            lines.append(f"\n[{until_next} until next threshold]")

        return "\n".join(lines)

    @staticmethod
    def format_event(event: PopulationEvent) -> str:
        """Format a single event for display."""
        type_labels = {
            PopulationEventType.DEATH: "DEATH",
            PopulationEventType.DISAPPEARANCE: "MISSING",
            PopulationEventType.EVACUATION: "LEFT",
            PopulationEventType.ARRIVAL: "ARRIVED"
        }

        label = type_labels.get(event.event_type, "EVENT")
        correction = " [CORRECTION]" if event.is_correction else ""

        return f"Day {event.day} [{label}]{correction}: {event.description}"


if __name__ == "__main__":
    # Test population system
    system = PopulationSystem()

    print(PopulationDisplay.format_status(system))
    print("\n" + "=" * 40 + "\n")

    # Simulate events
    system.record_disappearance("The Miller family didn't show up for church.", count=3)
    system.record_death("Found frozen near the lake.", npc_id="npc_hunter_erikson")
    system.record_disappearance("Last seen heading into the forest.", count=2)

    print("\n" + "=" * 40 + "\n")
    print(PopulationDisplay.format_status(system))

    print("\nRecent events:")
    for event in system.events[-5:]:
        print(f"  {PopulationDisplay.format_event(event)}")

    print("\nAccumulated effects:")
    effects = system.get_accumulated_effects()
    for key, value in effects.items():
        print(f"  {key}: {value}")
