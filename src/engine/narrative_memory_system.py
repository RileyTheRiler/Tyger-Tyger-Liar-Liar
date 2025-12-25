"""
Narrative Memory System
Stores key narrative moments and allows them to be recalled with 'drift'
based on current psychological state and time passed.
"""

import time
import random
import copy
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from enum import Enum

# Import TextComposer definitions if needed, though we will inject the composer instance
# from engine.text_composer import Archetype

@dataclass
class NarrativeEvent:
    """A stored memory of a narrative event."""
    event_id: str
    text_data: Any  # Dict (scene structure) or Str
    importance: int  # 1-10
    timestamp: float  # Game time or real time? Let's use game time (total minutes)

    # Context at creation
    original_archetype: str
    original_sanity: float
    original_reality: float

    # Metadata
    tags: List[str] = field(default_factory=list)
    times_recalled: int = 0
    drift_level: float = 0.0  # Accumulates over time/recalls


class NarrativeMemorySystem:
    def __init__(self, text_composer=None, player_state=None, time_system=None):
        self.memories: Dict[str, NarrativeEvent] = {}
        self.text_composer = text_composer
        self.player_state = player_state
        self.time_system = time_system
        self.false_memory_injected = False  # Track if the mandatory false memory exists
        self.spontaneous_recall_triggered = False

    def log_event(self, event_id: str, text_data: Any, importance: int = 1, tags: List[str] = None):
        """
        Log a narrative event.
        text_data: The scene dictionary or string used to generate the text.
                   Storing the raw structure allows re-compositing with different lenses.
        """
        if not self.player_state or not self.time_system:
            return

        current_time = (self.time_system.current_time - self.time_system.start_time).total_seconds() / 60.0

        event = NarrativeEvent(
            event_id=event_id,
            text_data=copy.deepcopy(text_data), # Store copy to prevent mutation
            importance=importance,
            timestamp=current_time,
            original_archetype=self.player_state.get("archetype", "neutral"),
            original_sanity=self.player_state.get("sanity", 100.0),
            original_reality=self.player_state.get("reality", 100.0),
            tags=tags or []
        )

        self.memories[event_id] = event
        print(f"[MEMORY] Logged event: {event_id}")

    def recall_event(self, event_id: str) -> str:
        """
        Recall a memory, applying drift and current psychological filters.
        """
        if event_id not in self.memories:
            return "You try to remember, but there is nothing there."

        # Special case: The explicit false memory replaces the text entirely if active
        if event_id == "arrival_memory" and self.false_memory_injected:
             return "You arrived in town in a black sedan. You were driving. There was blood on the steering wheel."

        event = self.memories[event_id]
        event.times_recalled += 1

        # Calculate modifiers
        current_time = (self.time_system.current_time - self.time_system.start_time).total_seconds() / 60.0
        time_delta = current_time - event.timestamp

        current_archetype_str = self.player_state.get("archetype", "neutral")
        current_sanity = self.player_state.get("sanity", 100.0)
        current_reality = self.player_state.get("reality", 100.0)

        # Calculate Drift Factor
        # Drift increases with:
        # 1. Time passed
        # 2. Difference in Sanity/Reality from original
        # 3. Frequency of recall (re-consolidating memory changes it)

        sanity_diff = abs(current_sanity - event.original_sanity)
        reality_diff = abs(current_reality - event.original_reality)

        drift_increase = (time_delta / 1440.0) * 0.1  # 10% per day
        drift_increase += (sanity_diff / 100.0) * 0.2
        drift_increase += (reality_diff / 100.0) * 0.3
        drift_increase += 0.05  # Base recall distortion

        event.drift_level += drift_increase

        # Compose text using CURRENT filters
        recalled_text = ""

        # We need to map string archetype to Enum for TextComposer
        # Assuming TextComposer is available and has Archetype enum
        from engine.text_composer import Archetype

        arch_map = {
            "believer": Archetype.BELIEVER,
            "skeptic": Archetype.SKEPTIC,
            "haunted": Archetype.HAUNTED,
            "neutral": Archetype.NEUTRAL
        }
        target_archetype = arch_map.get(current_archetype_str, Archetype.NEUTRAL)

        # If we stored a dict, we can re-compose
        if isinstance(event.text_data, dict) and self.text_composer:
            # Re-run composition
            result = self.text_composer.compose(
                event.text_data,
                target_archetype,
                self.player_state
            )
            recalled_text = result.full_text
        else:
            # Simple string
            recalled_text = str(event.text_data)

        # Apply DRIFT EFFECTS
        recalled_text = self._apply_drift_effects(recalled_text, event.drift_level, current_reality)

        # Explicit Contradiction Check (The "False Memory" goal)
        if event_id == "false_memory_trigger" or self._should_trigger_false_memory(event):
            recalled_text = self._inject_false_memory(recalled_text)

        return recalled_text

    def check_spontaneous_recall(self, player_state: Dict) -> Optional[str]:
        """Check if a spontaneous false memory should surface."""
        if self.spontaneous_recall_triggered:
            return None

        sanity = player_state.get("sanity", 100)

        # Trigger if Sanity drops below 50 AND we have the seed memory
        if sanity < 50 and "arrival_memory" in self.memories:
            self.inject_explicit_false_memory() # Ensure it's corrupted
            text = self.recall_event("arrival_memory")
            self.spontaneous_recall_triggered = True
            return text

        return None

    def _apply_drift_effects(self, text: str, drift: float, current_reality: float) -> str:
        """Apply text distortions based on drift level."""
        if drift < 0.2 and current_reality > 80:
            return text  # Clear memory

        # Minor fuzziness
        if drift >= 0.2 or current_reality < 80:
            text = text.replace("definitely", "maybe")
            text = text.replace("saw", "think I saw")
            text = text.replace("clearly", "hazy")

        # Significant distortion
        if drift >= 0.5 or current_reality < 50:
            sentences = text.split(". ")
            if len(sentences) > 1:
                pass

            # Add doubt
            text += " ...or was it?"

        # Severe corruption
        if drift >= 0.8 or current_reality < 25:
            words = text.split()
            if words:
                # Randomly replace a word with "..."
                idx = random.randint(0, len(words)-1)
                words[idx] = "..."
                text = " ".join(words)

            text += "\n[MEMORY CORRUPTED]"

        return text

    def _should_trigger_false_memory(self, event: NarrativeEvent) -> bool:
        # Trigger on specific high drift or low reality conditions
        # for the explicit deliverable requirement
        if event.importance >= 8 and event.drift_level > 1.0:
            return True
        return False

    def _inject_false_memory(self, text: str) -> str:
        """Inject a specific contradiction."""
        contradictions = [
            "\n(Wait. That's not right. It was raining. It was pouring rain.)",
            "\n(No. You weren't alone. HE was there.)",
            "\n(You didn't find it. It found you.)"
        ]
        return text + random.choice(contradictions)

    def inject_explicit_false_memory(self):
        """Creates the required explicit false memory event."""
        if self.false_memory_injected:
            return

        # Ensure the base memory exists if it hasn't been logged yet
        if "arrival_memory" not in self.memories:
            self.log_event(
                event_id="arrival_memory",
                text_data={"base": "You arrived in town on the 4 PM bus. The driver was a quiet man with a scar on his cheek."},
                importance=10,
                tags=["core", "false_candidate"]
            )

        self.false_memory_injected = True
        print("[MEMORY] Explicit false memory activated: 'arrival_memory'")

    def to_dict(self) -> Dict:
        return {
            "memories": {k: asdict(v) for k, v in self.memories.items()},
            "false_memory_injected": self.false_memory_injected,
            "spontaneous_recall_triggered": self.spontaneous_recall_triggered
        }

    def load_state(self, data: Dict):
        if not data: return
        self.memories = {}
        for k, v in data.get("memories", {}).items():
            self.memories[k] = NarrativeEvent(**v)
        self.false_memory_injected = data.get("false_memory_injected", False)
        self.spontaneous_recall_triggered = data.get("spontaneous_recall_triggered", False)
