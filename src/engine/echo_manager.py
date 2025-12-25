"""
Echo System - Persistent Sensory Scars.
A framework for narrative callbacks to past trauma, psychological failures, and critical choices.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
import random

@dataclass
class EchoMotif:
    id: str
    motif_type: str  # e.g., "smell", "sound", "visual", "thought"
    content: str     # e.g., "copper", "ticking", "a shadow", "they are lying"
    intensity: float  # 0.0 to 1.0
    lifetime: int     # Number of scene transitions before decay
    source: str      # What triggered this?

class EchoManager:
    """
    Tracks and manages sensory echoes that persistent in the narrative.
    """
    def __init__(self):
        self.active_echoes: Dict[str, EchoMotif] = {}
        self.motif_templates = {
            "smell": ["metallic", "copper", "burning hair", "ozone", "cloying floral"],
            "sound": ["ticking", "distant scratching", "whispering", "humming", "a heartbeat"],
            "visual": ["flickering", "blurring edges", "shifting shadows", "statues moving"],
            "thought": ["you've been here", "don't look back", "it's watching", "something is wrong"]
        }

    def add_echo(self, echo_id: str, motif_type: str, content: str, intensity: float = 0.5, lifetime: int = 5, source: str = "unknown"):
        """Add a manual echo."""
        self.active_echoes[echo_id] = EchoMotif(
            id=echo_id,
            motif_type=motif_type,
            content=content,
            intensity=intensity,
            lifetime=lifetime,
            source=source
        )

    def trigger_echo_from_failure(self, failure_id: str, intensity: float = 0.7):
        """Standardized echo generation from a psychological failure."""
        types = list(self.motif_templates.keys())
        m_type = random.choice(types)
        content = random.choice(self.motif_templates[m_type])
        
        echo_id = f"fail_{failure_id}_{random.randint(100,999)}"
        self.add_echo(echo_id, m_type, content, intensity=intensity, source=failure_id)
        return echo_id

    def advance_time(self, scene_transitions: int = 1):
        """Decay echoes over time."""
        to_remove = []
        for eid, echo in self.active_echoes.items():
            echo.lifetime -= scene_transitions
            if echo.lifetime <= 0:
                to_remove.append(eid)
        
        for eid in to_remove:
            del self.active_echoes[eid]

    def get_narrative_modifiers(self) -> List[Dict]:
        """Return active echoes for the TextComposer."""
        return [
            {"type": e.motif_type, "content": e.content, "intensity": e.intensity}
            for e in self.active_echoes.values()
        ]

    def to_dict(self) -> dict:
        return {
            "echoes": {eid: vars(e) for eid, e in self.active_echoes.items()}
        }

    def from_dict(self, data: dict):
        self.active_echoes = {
            eid: EchoMotif(**e_data)
            for eid, e_data in data.get("echoes", {}).items()
        }
