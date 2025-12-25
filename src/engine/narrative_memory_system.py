"""
Narrative Memory System
Stores key narrative moments and allows them to be recalled with 'drift'.
The drift changes based on current stress (sanity) and archetype, and can introduce contradictions.
"""

from dataclasses import dataclass, field
import random
import copy
from typing import Dict, List, Optional, Any
from text_composer import TextComposer, Archetype

@dataclass
class NarrativeMoment:
    id: str
    original_text_data: dict  # The raw text data (base, lens, etc.)
    importance: int           # 1-10
    timestamp: str            # Game time string when stored
    context_tags: List[str] = field(default_factory=list)

class NarrativeMemorySystem:
    def __init__(self, text_composer: TextComposer):
        self.memories: Dict[str, NarrativeMoment] = {}
        self.text_composer = text_composer

    def store_moment(self, event_id: str, text_data: dict, importance: int, timestamp: str, tags: List[str] = None):
        """
        Store a narrative moment in the memory log.
        """
        if event_id in self.memories:
            # Don't overwrite existing memories of the same event unless intentional?
            # For now, let's keep the first impression as the "truth" (or original experience)
            return

        # Ensure we store the structured data, not just string
        if isinstance(text_data, str):
            text_data = {"base": text_data}

        self.memories[event_id] = NarrativeMoment(
            id=event_id,
            original_text_data=copy.deepcopy(text_data),
            importance=importance,
            timestamp=timestamp,
            context_tags=tags or []
        )
        print(f"[Memory Stored: {event_id}]")

    def recall_memory(self, event_id: str, player_state: dict) -> str:
        """
        Recall a past memory.
        Applies current archetype filter (re-interpretation) and stress-based drift (contradictions).
        """
        memory = self.memories.get(event_id)
        if not memory:
            return "You search your mind, but find nothing."

        # 1. Re-compose using CURRENT archetype/stats
        # This effectively "re-writes" the memory through the current lens.
        current_archetype = self.text_composer.calculate_dominant_lens(player_state)

        composed = self.text_composer.compose(
            memory.original_text_data,
            current_archetype,
            player_state
        )

        text = composed.full_text

        # 2. Apply Drift (Time + Stress)
        sanity = player_state.get("sanity", 100)
        # 0 sanity = 1.0 stress, 100 sanity = 0.0 stress
        stress_factor = max(0.0, (100.0 - sanity) / 100.0)

        drifted_text = self._apply_drift(text, stress_factor, memory, current_archetype)

        return drifted_text

    def _apply_drift(self, text: str, stress: float, memory: NarrativeMoment, archetype: Archetype) -> str:
        """
        Apply text distortions and contradictions based on stress and specific event triggers.
        """

        # === EXPLICIT CONTRADICTION (Deliverable Requirement) ===
        # If this is the 'arrival' event, force a contradiction
        if memory.id == "arrival" or "arrival" in memory.context_tags:
            text = self._apply_arrival_contradiction(text, stress)

        # === GENERAL DRIFT ===

        # Low Stress: Minor doubts
        if stress < 0.3:
            if random.random() < 0.2:
                text += "\n\n(At least, that's how you remember it.)"

        # Medium Stress: Emotional coloring
        elif stress < 0.6:
            text = self._inject_emotion(text, stress)

        # High Stress: Active falsification
        else:
            text = self._scramble_details(text)
            text += f"\n\n[MEMORY CORRUPTED: {int(stress * 100)}% DETACHMENT]"

        return text

    def _apply_arrival_contradiction(self, text: str, stress: float) -> str:
        """
        The specific contradiction for the arrival scene.
        Changes weather/time details to be incorrect.
        """
        # Original likely mentions rain/bus/night.
        # We flip it.

        contradictions = [
            ("rain", "scorching sun"),
            ("raining", "bone dry"),
            ("night", "blinding noon"),
            ("dark", "bright"),
            ("bus", "train"),
            ("driver", "conductor")
        ]

        drifted = text
        changed = False

        for old, new in contradictions:
            if old in drifted.lower():
                # Case insensitive replacement for demo
                import re
                drifted = re.sub(re.escape(old), new.upper(), drifted, flags=re.IGNORECASE)
                changed = True

        if changed:
            drifted += "\n\n(Wait. That's wrong. It wasn't like that. Why do you remember it like that?)"
        else:
            # Fallback if text didn't match keywords
            drifted += "\n\n(The memory feels slippery. You remember arriving by train, not bus. But there are no tracks in Tyger Tyger.)"

        return drifted

    def _inject_emotion(self, text: str, stress: float) -> str:
        emotions = [
            "You felt cold then.",
            "The smell of ozone was overpowering.",
            "You were afraid.",
            "It seemed funny at the time."
        ]
        return text + f"\n\n[{random.choice(emotions)}]"

    def _scramble_details(self, text: str) -> str:
        words = text.split()
        if len(words) > 10:
            # Shuffle a few words
            for _ in range(3):
                i, j = random.randint(0, len(words)-1), random.randint(0, len(words)-1)
                words[i], words[j] = words[j], words[i]
        return " ".join(words)

    def to_dict(self):
        """Export for save system."""
        return {
            "memories": {
                mid: {
                    "id": m.id,
                    "original_text_data": m.original_text_data,
                    "importance": m.importance,
                    "timestamp": m.timestamp,
                    "context_tags": m.context_tags
                }
                for mid, m in self.memories.items()
            }
        }

    def load_state(self, data: dict):
        """Load from save system."""
        memories_data = data.get("memories", {})
        self.memories = {}
        for mid, m_data in memories_data.items():
            self.memories[mid] = NarrativeMoment(
                id=m_data["id"],
                original_text_data=m_data["original_text_data"],
                importance=m_data["importance"],
                timestamp=m_data["timestamp"],
                context_tags=m_data.get("context_tags", [])
            )
