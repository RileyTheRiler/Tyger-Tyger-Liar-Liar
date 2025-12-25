from enum import Enum
from dataclasses import dataclass, asdict
import time
import json
from typing import Any, Dict, Optional

class EventType(Enum):
    NARRATIVE_TEXT = "NARRATIVE_TEXT"
    STATE_UPDATE = "STATE_UPDATE"
    CLUE_ADDED = "CLUE_ADDED"
    OPTION_ADDED = "OPTION_ADDED"
    OPTION_REMOVED = "OPTION_REMOVED"
    MENTAL_EFFECT = "MENTAL_EFFECT"

class EventSource(Enum):
    SYSTEM = "system"
    NARRATOR = "narrator"
    HALLUCINATION = "hallucination"
    DEBUG = "debug"

@dataclass
class GameEvent:
    type: str
    payload: Dict[str, Any]
    source: str
    timestamp: float = 0.0

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @staticmethod
    def create(type: EventType, payload: Dict[str, Any], source: EventSource = EventSource.SYSTEM) -> 'GameEvent':
        return GameEvent(type=type.value, payload=payload, source=source.value)
